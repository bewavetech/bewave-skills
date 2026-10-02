#!/usr/bin/env python3
"""
validate_state.py - risk-aware completion gate for a feature.

Run as the closing step of Verify. A feature is done only when the evidence
required by its risk level exists. A missing, hollow, placeholder or FAIL
report cannot slip through.

All levels:
  ERROR  a task still pending / in progress, or an amendment still proposed
MEDIUM:
  ERROR  validation.md present but not PASS, or PASS without file:line evidence
HIGH (adds):
  ERROR  no validation.md, no PASS, no file:line evidence
  ERROR  an active AC missing from the evidence table, or not marked ✅
  ERROR  surviving mutants
  WARN   fewer than 3 mutations; verifier is the author (context-reset)
CRITICAL (adds):
  ERROR  an invariant without ✅ evidence
  ERROR  fewer than 5 mutations (unless mutation tooling is cited)
  ERROR  verifier is the author without an approved sign-off
  ERROR  human sign-off not recorded as approved

Usage:
  python3 <skill-dir>/scripts/validate_state.py [feature] [--root DIR]
  Without a feature: checks the only feature, or every feature whose plan is complete.

Exit codes: 0 done, 1 not done, 2 usage error.
"""

import argparse
import os
import re
import sys

import _sdd


def verdict(lines):
    v = _sdd.field(lines, "Verdict") or ""
    has_pass, has_fail = bool(re.search(r"\bPASS\b", v)), bool(re.search(r"\bFAIL\b", v))
    if has_pass and has_fail:
        return "unfilled"
    return "pass" if has_pass else "fail" if has_fail else None


def evidence_rows(lines, section):
    """Map ID -> row text for rows of the first table in a section."""
    out = {}
    for row in _sdd.table_rows(_sdd.section_lines(lines, section)):
        if row:
            ids = _sdd.ids_in(row[0])
            if ids:
                out[ids[0]] = " | ".join(row)
    return out


def ok_row(row):
    return "✅" in row and "❌" not in row and "⚠️" not in row and bool(_sdd.EVIDENCE_RE.search(row))


def check_feature(fdir, rep, label):
    spec_path, plan_path = os.path.join(fdir, "spec.md"), os.path.join(fdir, "plan.md")
    val_path = os.path.join(fdir, "validation.md")
    if not os.path.isfile(spec_path):
        rep.note(f"{label}: no spec.md; treated as LOW inline work, nothing to gate")
        return
    spec = _sdd.parse_spec(spec_path)
    level = _sdd.spec_level(spec)
    li = _sdd.level_index(level)
    rep.note(f"{label}: risk {level}")

    # Plan completion.
    if not os.path.isfile(plan_path):
        if li >= 1:
            rep.error(f"{label}: no plan.md for a {level} feature")
    else:
        plan = _sdd.parse_plan(plan_path)
        if not plan["tasks"]:
            rep.error(f"{label}: plan.md has no tasks")
        for t in plan["tasks"]:
            st = _sdd.task_status(t)
            if st in ("pending", "progress", "invalid"):
                rep.error(f"{label}: {t['id']} is not done (status: {t['fields'].get('status', '?')})")

    for a in spec["amendments"]:
        if a["status"] == "proposed":
            rep.error(f"{label}: amendment {a['id']} is still proposed")

    if li <= 0:
        return
    if not os.path.isfile(val_path):
        if li >= 2:
            rep.error(f"{label}: no validation.md; {level} requires a written verification report")
        else:
            rep.note(f"{label}: MEDIUM without validation.md; verification evidence must be in the chat summary")
        return

    lines = _sdd.read_clean(val_path).splitlines()
    text = "\n".join(lines)
    v = verdict(lines)
    if v is None:
        rep.error(f"{label}: validation.md has no '**Verdict**: PASS|FAIL'")
    elif v == "unfilled":
        rep.error(f"{label}: validation.md verdict is still the template 'PASS | FAIL'")
    elif v == "fail":
        rep.error(f"{label}: verdict is FAIL; route gaps to fix tasks and re-verify")
    if not _sdd.EVIDENCE_RE.search(text):
        rep.error(f"{label}: validation.md cites no file:line evidence (evidence-or-zero)")
    if li < 2:
        return

    # HIGH and CRITICAL: per-AC evidence.
    rows = evidence_rows(lines, "Acceptance Criteria Evidence")
    for c in _sdd.active_criteria(spec):
        row = rows.get(c["id"])
        if row is None:
            rep.error(f"{label}: {c['id']} is missing from Acceptance Criteria Evidence")
        elif not ok_row(row):
            rep.error(f"{label}: {c['id']} is not ✅ with file:line evidence")

    # Discrimination.
    res = _sdd.field(_sdd.section_lines(lines, "Discrimination"), "Result") or ""
    nums = dict((k, int(n)) for n, k in re.findall(r"(\d+)\s+(injected|killed|survived)", res))
    tooling = bool(re.search(r"stryker|mutmut|cargo-mutants|pit\b|pitest|mutation tool", text, re.IGNORECASE))
    if not nums:
        rep.error(f"{label}: Discrimination result missing ('N injected · N killed · N survived')")
    else:
        if nums.get("survived", 0) > 0:
            rep.error(f"{label}: {nums['survived']} mutant(s) survived; strengthen the tests")
        inj = nums.get("injected", 0)
        if level == "CRITICAL" and inj < 5 and not tooling:
            rep.error(f"{label}: CRITICAL needs >=5 mutations or mutation tooling (got {inj})")
        elif level == "HIGH" and inj < 3:
            rep.warn(f"{label}: HIGH expects 3-5 mutations (got {inj})")

    verifier = (_sdd.field(lines, "Verifier") or "").lower()
    signoff = (_sdd.field(lines, "Human sign-off") or "").lower()
    signed = signoff.startswith("approved")
    if "|" in verifier or not verifier:
        rep.error(f"{label}: Verifier line not filled")
    elif "independent" not in verifier:
        if level == "CRITICAL" and not signed:
            rep.error(f"{label}: CRITICAL verification by the author needs an approved human sign-off")
        else:
            rep.warn(f"{label}: verification was not independent ({verifier})")

    if level != "CRITICAL":
        return
    inv_rows = evidence_rows(lines, "Invariants")
    for i in spec["invariants"]:
        if i["removed"]:
            continue
        row = inv_rows.get(i["id"])
        if row is None or not ok_row(row):
            rep.error(f"{label}: invariant {i['id']} lacks ✅ evidence in ## Invariants")
    if not signed:
        rep.error(f"{label}: awaiting human sign-off ('**Human sign-off**: approved by <name> on <date>')")


def main(argv=None):
    p = argparse.ArgumentParser(prog="validate_state.py", description="Risk-aware completion gate.")
    p.add_argument("feature", nargs="?", default=None, help="feature name or dir")
    p.add_argument("--root", default=".", help="project root containing .specs/")
    args = p.parse_args(argv)
    root = os.path.abspath(args.root)
    rep = _sdd.Report("validate_state")

    if args.feature:
        fdir = _sdd.resolve_feature_dir(args.feature, root)
        targets = [(fdir, os.path.basename(fdir.rstrip("/")))]
    else:
        feats = _sdd.list_features(root)
        base = os.path.join(root, ".specs", "features")
        if len(feats) == 1:
            targets = [(os.path.join(base, feats[0]), feats[0])]
        else:
            targets = []
            for f in feats:
                pp = os.path.join(base, f, "plan.md")
                if os.path.isfile(pp):
                    tasks = _sdd.parse_plan(pp)["tasks"]
                    if tasks and all(_sdd.task_status(t) in ("done", "dropped") for t in tasks):
                        targets.append((os.path.join(base, f), f))
            if not targets:
                print("validate_state: no completed feature to gate.")
                return 0

    for fdir, label in targets:
        check_feature(fdir, rep, label)
    return rep.finish(", ".join(l for _, l in targets))


if __name__ == "__main__":
    sys.exit(main())
