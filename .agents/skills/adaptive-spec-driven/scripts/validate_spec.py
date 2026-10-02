#!/usr/bin/env python3
"""
validate_spec.py - risk-aware closure gate for a feature spec.md.

Run before presenting a spec for approval. Checks structure only; judging
whether an AC captures the right behavior stays with the agent and the user.

  ERROR  section required by the declared risk level is missing
  ERROR  declared level missing, or lower than computed without an Override
  ERROR  a factor is unrated or has an invalid rating (MEDIUM+)
  ERROR  no acceptance criteria, duplicate IDs, or unfilled template rows
  ERROR  CRITICAL spec without invariants
  ERROR  assumption row without chosen default or rationale
  ERROR  HIGH+ spec whose open questions are not closed
  ERROR  malformed amendment, or an AC tag pointing to a missing amendment
  WARN   vague wording in a criterion (ERROR at CRITICAL)
  WARN   a criterion that bundles several SHALLs
  WARN   rated factor with no evidence; proposed amendments still open

Usage:
  python3 <skill-dir>/scripts/validate_spec.py [feature|path] [--root DIR] [--strict]

Exit codes: 0 pass, 1 errors (or warnings under --strict), 2 usage error.
"""

import argparse
import os
import re
import sys

import _sdd

REQUIRED = {
    "LOW": ["Problem", "Acceptance Criteria"],
    "MEDIUM": ["Problem", "Scope", "Risk Assessment", "Acceptance Criteria"],
    "HIGH": ["Problem", "Scope", "Risk Assessment", "Acceptance Criteria",
             "Failure & Edge Behavior", "Assumptions & Open Questions"],
    "CRITICAL": ["Problem", "Scope", "Risk Assessment", "Acceptance Criteria",
                 "Failure & Edge Behavior", "Assumptions & Open Questions", "Invariants"],
}

VAGUE = [
    "fast", "quickly", "slow", "gracefully", "properly", "appropriate", "appropriately",
    "user-friendly", "intuitive", "seamless", "seamlessly", "robust", "efficient",
    "efficiently", "easy", "easily", "simple", "as expected", "correctly", "reasonable",
    "etc", "and/or", "should work", "nice", "better", "optimal", "adequate",
]
VAGUE_RE = re.compile(r"(?<![\w-])(" + "|".join(re.escape(w) for w in VAGUE) + r")(?![\w-])", re.IGNORECASE)

AMEND_TYPES = {"clarification", "behavior-change", "scope-change", "risk-change"}
AMEND_STATUS = {"proposed", "approved", "rejected"}


def check(spec, rep):
    lines = spec["lines"]
    computed, reasons = _sdd.compute_level(spec["ratings"])
    declared = spec["declared"]
    level = declared or computed

    if not declared:
        rep.error("missing or invalid '**Declared level**: LOW|MEDIUM|HIGH|CRITICAL' in Risk Assessment")
    rep.note(f"computed level: {computed} ({'; '.join(reasons)}); declared: {declared or '-'}")

    for name in REQUIRED[level]:
        if not spec["sections"].get(name):
            rep.error(f"missing section required at {level}: ## {name}")

    # Factors.
    if _sdd.level_index(level) >= 1 or spec["ratings"]:
        for f in _sdd.FACTORS:
            v = spec["ratings"].get(f)
            if v is None:
                (rep.error if _sdd.level_index(level) >= 1 else rep.warn)(f"risk factor not rated: {f}")
            elif v not in _sdd.RATINGS:
                rep.error(f"risk factor {f} has invalid rating '{v}' (use {', '.join(_sdd.RATINGS)})")
            elif v != "none":
                ev = spec["evidence"].get(f, "")
                if not ev or _sdd.has_placeholder(ev):
                    rep.warn(f"risk factor {f}={v} has no evidence")
        for k in spec["unknown_factors"]:
            if k not in ("factor",):
                rep.warn(f"unknown risk factor row '{k}' (ignored)")

    # Declared vs computed.
    if declared and _sdd.level_index(declared) < _sdd.level_index(computed):
        ov = spec["override"] or ""
        if not ov or _sdd.has_placeholder(ov) or ov.strip("-— ") == "":
            rep.error(f"declared {declared} is below computed {computed} without an '**Override**:' justification")
        elif len(ov) < 25:
            rep.warn(f"override justification is very short: '{ov}'")

    # Criteria.
    crit = spec["criteria"]
    active = _sdd.active_criteria(spec)
    if not active:
        rep.error("no acceptance criteria with IDs (expected lines like '- **AREA-01** — ...')")
    seen = {}
    for c in crit + spec["invariants"]:
        if c["id"] in seen:
            rep.error(f"L{c['line']}: duplicate ID {c['id']} (first at L{seen[c['id']]})")
        seen.setdefault(c["id"], c["line"])
    for c in active:
        t = c["text"]
        if _sdd.has_placeholder(t):
            rep.error(f"L{c['line']}: template placeholder left in {c['id']}: {t[:60]}")
            continue
        if len(t) < 12:
            rep.warn(f"L{c['line']}: {c['id']} is too short to be testable: '{t}'")
        hits = sorted(set(h.lower() for h in VAGUE_RE.findall(_sdd.CODE_SPAN_RE.sub("", t))))
        if hits:
            msg = f"L{c['line']}: {c['id']} uses vague wording ({', '.join(hits)}); state a concrete outcome"
            (rep.error if level == "CRITICAL" else rep.warn)(msg)
        if len(re.findall(r"\bshall\b", t, re.IGNORECASE)) > 1:
            rep.warn(f"L{c['line']}: {c['id']} has several SHALLs; split into one behavior per AC")
    for c in spec["invariants"]:
        if not c["id"].startswith("INV-"):
            rep.warn(f"L{c['line']}: invariant ID {c['id']} should use the INV-NN form")
        if _sdd.has_placeholder(c["text"]):
            rep.error(f"L{c['line']}: template placeholder left in {c['id']}")

    if _sdd.level_index(level) >= 2 and spec["sections"].get("Failure & Edge Behavior"):
        if not [c for c in active if c["section"] == "Failure & Edge Behavior"]:
            rep.warn("Failure & Edge Behavior has no ID'd criteria; confirm every failure path is N/A with a reason")
    if level == "CRITICAL" and not [i for i in spec["invariants"] if not i["removed"]]:
        rep.error("CRITICAL spec has no invariants (expected '- **INV-01** — ...')")

    # Assumptions.
    body = _sdd.section_lines(lines, "Assumptions & Open Questions")
    if body:
        for row in _sdd.table_rows(body):
            if len(row) < 3:
                continue
            what, chosen, why = row[0], row[1], row[2]
            if _sdd.has_placeholder(what) and _sdd.has_placeholder(chosen):
                rep.warn("Assumptions table still has the template row")
                continue
            if not chosen or _sdd.has_placeholder(chosen):
                rep.error(f"assumption '{what[:40]}' has no chosen default")
            if not why or _sdd.has_placeholder(why):
                rep.error(f"assumption '{what[:40]}' has no rationale")
        oq = _sdd.field(body, "Open questions")
        closed = oq is not None and re.match(r"^\s*none\b", oq, re.IGNORECASE)
        if not closed:
            msg = "open questions are not closed (expected '**Open questions**: none')"
            (rep.error if _sdd.level_index(level) >= 2 else rep.warn)(msg)

    # Amendments.
    amend_ids = set()
    for a in spec["amendments"]:
        if a["id"] in amend_ids:
            rep.error(f"L{a['line']}: duplicate amendment {a['id']}")
        amend_ids.add(a["id"])
        if _sdd.has_placeholder(" ".join(a["body"])):
            rep.error(f"L{a['line']}: amendment {a['id']} still has template placeholders")
            continue
        if a["type"] not in AMEND_TYPES:
            rep.error(f"L{a['line']}: amendment {a['id']} type must be one of {', '.join(sorted(AMEND_TYPES))}")
        if a["status"] not in AMEND_STATUS:
            rep.error(f"L{a['line']}: amendment {a['id']} status must be one of {', '.join(sorted(AMEND_STATUS))}")
        elif a["status"] == "proposed":
            rep.warn(f"amendment {a['id']} is still proposed; resolve before continuing the affected task")
    for c in crit:
        for tag in c["amendments"]:
            if tag not in amend_ids:
                rep.error(f"L{c['line']}: {c['id']} references {tag}, which is not in ## Amendments")


def main(argv=None):
    p = argparse.ArgumentParser(prog="validate_spec.py", description="Risk-aware closure gate for spec.md.")
    p.add_argument("target", nargs="?", default=None, help="feature name, feature dir, or spec.md path")
    p.add_argument("--root", default=".", help="project root containing .specs/")
    p.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = p.parse_args(argv)

    fdir = _sdd.resolve_feature_dir(args.target, os.path.abspath(args.root))
    path = args.target if args.target and os.path.isfile(args.target) else os.path.join(fdir, "spec.md")
    if not os.path.isfile(path):
        _sdd.die(f"validate_spec: no spec.md at {path}")

    rep = _sdd.Report("validate_spec")
    check(_sdd.parse_spec(path), rep)
    return rep.finish(path, args.strict)


if __name__ == "__main__":
    sys.exit(main())
