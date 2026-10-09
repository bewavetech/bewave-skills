#!/usr/bin/env python3
"""
validate_plan.py - risk-aware structural gate for a feature plan.md.

Run before presenting a plan for approval (and again after amendments).
Reads the sibling spec.md for IDs and the risk level.

  ERROR  section required by the risk level is missing
  ERROR  task missing a required field, or holding template placeholders
  ERROR  Covers references an unknown or removed AC
  ERROR  an active AC is covered by no task and not listed in Deferred
  ERROR  a test line without a valid origin (SPEC|REGRESSION|CONTRACT|INVARIANT|CHARACTERIZATION)
  ERROR  a SPEC / INVARIANT test that cites no existing AC / invariant
  ERROR  a covered AC with no SPEC test in its task (task risk MEDIUM+)
  ERROR  an invariant with no INVARIANT test (CRITICAL)
  ERROR  Tests: none at task risk HIGH+, or without a reason
  ERROR  unknown or cyclic dependencies; waves that contradict dependencies
  ERROR  a task missing from the waves, or listed twice
  ERROR  a gate level not defined in Verification Commands
  ERROR  task risk lowered below the feature level without a reason
  WARN   overlapping Touches between parallel tasks in the same wave
  WARN   file-shaped task titles, tasks covering many ACs, no CONTRACT test where boundaries are risky

Usage:
  python3 <skill-dir>/scripts/validate_plan.py [feature|path] [--root DIR] [--strict]

Exit codes: 0 pass, 1 errors (or warnings under --strict), 2 usage error.
"""

import argparse
import os
import re
import sys

import _sdd

REQUIRED = {
    "LOW": ["Tasks"],
    "MEDIUM": ["Approach", "Verification Commands", "Tasks", "Execution Waves"],
    "HIGH": ["Approach", "Design", "Alternatives Considered", "Risks & Mitigations",
             "Test Strategy", "Verification Commands", "Tasks", "Execution Waves"],
    "CRITICAL": ["Approach", "Design", "Alternatives Considered", "Failure Modes",
                 "Risks & Mitigations", "Rollback", "Test Strategy", "Verification Commands",
                 "Tasks", "Execution Waves"],
}
TASK_FIELDS = ["covers", "depends on", "touches", "change", "tests", "done when", "gate", "status"]
FILE_SHAPED_RE = re.compile(
    r"^(?i:create|add|implement|write|build|update)\s+(?i:the\s+)?(`[^`]+`|[\w./-]+\.(ts|tsx|js|py|go|rb|java|kt|swift|rs|sql)\b|[A-Z][a-z]+[A-Z]\w*)",
)
TESTS_ONLY_RE = re.compile(r"^(write|add)\s+(unit\s+|e2e\s+|integration\s+)?tests?\b", re.IGNORECASE)


def touches(task):
    return [t.strip().rstrip("/") for t in re.findall(r"`([^`]+)`", task["fields"].get("touches", ""))]


def overlap(a, b):
    for x in a:
        for y in b:
            xs, ys = x.rstrip("*").rstrip("/"), y.rstrip("*").rstrip("/")
            if xs == ys or xs.startswith(ys + "/") or ys.startswith(xs + "/"):
                return f"{x} ~ {y}"
    return None


def find_cycle(deps):
    state = {}

    def visit(n, stack):
        state[n] = 1
        for d in deps.get(n, []):
            if d not in deps:
                continue
            if state.get(d) == 1:
                return stack + [n, d]
            if state.get(d) is None:
                c = visit(d, stack + [n])
                if c:
                    return c
        state[n] = 2
        return None

    for n in deps:
        if state.get(n) is None:
            c = visit(n, [])
            if c:
                return c
    return None


def check(spec, plan, rep):
    level = _sdd.spec_level(spec)
    li = _sdd.level_index(level)
    rep.note(f"feature risk: {level}")

    pr = plan["risk_raw"] or ""
    m = re.search(r"\b(LOW|MEDIUM|HIGH|CRITICAL)\b", pr.upper())
    if m and m.group(1) != level:
        rep.warn(f"plan header says Risk {m.group(1)} but spec declares {level}; the spec is the source of truth")

    for name in REQUIRED[level]:
        if not plan["sections"].get(name):
            rep.error(f"missing section required at {level}: ## {name}")

    tasks = plan["tasks"]
    if not tasks:
        rep.error("no tasks found (expected '### T1 — <behavior>')")
        return
    by_id = {}
    for t in tasks:
        if t["id"] in by_id:
            rep.error(f"L{t['line']}: duplicate task {t['id']}")
        by_id[t["id"]] = t

    ac_ids = {c["id"] for c in _sdd.active_criteria(spec)}
    removed_ids = {c["id"] for c in spec["criteria"] if c["removed"]}
    inv_ids = {i["id"] for i in spec["invariants"] if not i["removed"]}
    gates = plan["gates"]
    for g, cmd in gates.items():
        if not cmd or _sdd.has_placeholder(cmd):
            rep.error(f"Verification Commands: gate '{g}' has no real command")

    covered = set()
    invariant_tested = set()
    contract_seen = False
    deps = {}

    for t in tasks:
        tid, f = t["id"], t["fields"]
        where = f"L{t['line']} {tid}"
        status = _sdd.task_status(t)
        for name in TASK_FIELDS:
            if name not in f:
                rep.error(f"{where}: missing field **{name.title()}**")
        if _sdd.has_placeholder(t["title"]) or _sdd.has_placeholder("\n".join(t["raw"])):
            rep.error(f"{where}: template placeholders left in the task")
        if status == "invalid":
            rep.error(f"{where}: Status must start with [ ], [~], [x] or [-]")
        elif status == "dropped" and not re.search(r"\bA-\d+\b", f.get("status", "")):
            rep.warn(f"{where}: dropped without the amendment that dropped it")

        # Risk.
        raw_risk = (f.get("risk") or "inherit").strip()
        tl = _sdd.task_level(t, level)
        if raw_risk.lower() != "inherit" and not re.match(r"^(LOW|MEDIUM|HIGH|CRITICAL)\b", raw_risk.upper()):
            rep.error(f"{where}: Risk must be 'inherit' or a level with a reason")
        if _sdd.level_index(tl) < li and not re.search(r"[—–-]\s*\w.{2,}", raw_risk):
            rep.error(f"{where}: task risk {tl} is below the feature level {level} without a reason")

        # Gate.
        gate = (f.get("gate") or "").strip("` ").lower()
        if gates and gate and gate not in gates:
            rep.error(f"{where}: gate '{gate}' is not defined in Verification Commands")

        # Covers.
        cov_raw = f.get("covers", "")
        cov = [i for i in _sdd.ids_in(cov_raw) if not re.match(r"^[TF]\d+$", i)]
        enabler = "enabler" in cov_raw.lower()
        if not cov and not enabler and status != "dropped":
            rep.error(f"{where}: Covers lists no AC (use 'enabler for T<n>' for preparatory tasks)")
        if len(cov) > 6:
            rep.warn(f"{where}: covers {len(cov)} ACs; consider splitting by behavior")
        for i in cov:
            if i in removed_ids:
                rep.error(f"{where}: covers {i}, which an amendment removed")
            elif i not in ac_ids and i not in inv_ids:
                rep.error(f"{where}: covers {i}, which is not in spec.md")
        if status != "dropped":
            covered.update(cov)

        # Dependencies.
        dep_raw = f.get("depends on", "")
        dlist = re.findall(r"\b([TF]\d+)\b", dep_raw)
        if dep_raw and not dlist and not re.match(r"^\s*(none|-|—)\s*$", dep_raw, re.IGNORECASE):
            rep.warn(f"{where}: Depends on '{dep_raw}' names no task; use 'none'")
        for d in dlist:
            if d not in by_id:
                rep.error(f"{where}: depends on unknown task {d}")
        deps[tid] = dlist

        # Tests.
        tests_inline = f.get("tests", "")
        tests = t["tests"]
        if not tests:
            if re.match(r"^\s*none\b", tests_inline, re.IGNORECASE):
                if _sdd.level_index(tl) >= 2:
                    rep.error(f"{where}: 'Tests: none' is not allowed at task risk {tl}")
                elif not re.search(r"none\s*[—–:-]\s*\w.{2,}", tests_inline, re.IGNORECASE):
                    rep.error(f"{where}: 'Tests: none' needs a reason ('none — copy change only')")
            elif status != "dropped":
                rep.error(f"{where}: no test lines under **Tests**")
        spec_tested = set()
        for tl_ in tests:
            txt = tl_["text"]
            om = re.match(r"^(\w+)\b", txt)
            origin = om.group(1).upper() if om else ""
            if origin not in _sdd.TEST_ORIGINS:
                rep.error(f"L{tl_['line']} {tid}: test has no valid origin ({'|'.join(_sdd.TEST_ORIGINS)}): {txt[:50]}")
                continue
            refs = _sdd.ids_in(txt)
            if origin == "SPEC":
                anchors = [r for r in refs if r in ac_ids]
                if not anchors:
                    rep.error(f"L{tl_['line']} {tid}: SPEC test cites no existing AC ID")
                for r in anchors:
                    if r not in cov:
                        rep.warn(f"L{tl_['line']} {tid}: SPEC test for {r}, which the task does not list in Covers")
                spec_tested.update(anchors)
            elif origin == "INVARIANT":
                anchors = [r for r in refs if r in inv_ids]
                if not anchors:
                    rep.error(f"L{tl_['line']} {tid}: INVARIANT test cites no existing invariant ID")
                invariant_tested.update(anchors)
            elif origin == "CONTRACT":
                contract_seen = True
        fix_task = tid.upper().startswith("F") and bool(tests)
        if status != "dropped" and not fix_task:
            for i in cov:
                if i in ac_ids and i not in spec_tested:
                    msg = f"{where}: covers {i} but has no SPEC test citing it"
                    (rep.error if _sdd.level_index(tl) >= 1 else rep.warn)(msg)

        # Granularity smells.
        title = t["title"]
        if TESTS_ONLY_RE.match(title):
            rep.warn(f"{where}: tests-only task; tests belong inside the behavioral task they prove")
        elif FILE_SHAPED_RE.match(title):
            rep.warn(f"{where}: title looks file-shaped ('{title[:40]}'); name the behavior that becomes true")

    # Coverage of the spec.
    deferred = set(_sdd.ids_in(plan["deferred_text"]))
    for i in sorted(ac_ids - covered):
        if i in deferred:
            rep.note(f"{i} deferred (listed in ## Deferred)")
        else:
            rep.error(f"{i} is covered by no task and not listed in ## Deferred")
    for i in sorted(inv_ids - invariant_tested):
        msg = f"invariant {i} has no INVARIANT test"
        (rep.error if level == "CRITICAL" else rep.warn)(msg)
    boundary = any(spec["ratings"].get(k) in ("medium", "high") for k in ("integrations", "blast_radius"))
    if li >= 2 and boundary and not contract_seen:
        rep.warn("integrations/blast_radius rated medium+ but no CONTRACT test is planned")

    # Cycles.
    cyc = find_cycle(deps)
    if cyc:
        rep.error("dependency cycle: " + " -> ".join(cyc))

    # Waves.
    if plan["waves"]:
        position = {}
        for w in plan["waves"]:
            for gi, chain in enumerate(w["groups"]):
                for ci, tid in enumerate(chain):
                    if tid not in by_id:
                        rep.error(f"Wave {w['n']}: unknown task {tid}")
                    elif tid in position:
                        rep.error(f"Wave {w['n']}: {tid} already listed in wave {position[tid][0]}")
                    else:
                        position[tid] = (w["n"], gi, ci)
        for tid, t in by_id.items():
            if tid not in position and _sdd.task_status(t) != "dropped":
                rep.error(f"{tid} is not assigned to any wave")
        for tid, dl in deps.items():
            if tid not in position:
                continue
            wn, gi, ci = position[tid]
            for d in dl:
                if d not in position:
                    continue
                dw, dg, dc = position[d]
                if dw > wn:
                    rep.error(f"{tid} (wave {wn}) depends on {d} in a later wave ({dw})")
                elif dw == wn and (dg != gi or dc > ci):
                    rep.error(f"{tid} and its dependency {d} run in parallel in wave {wn}; chain them ({d} → {tid}) or move {tid} later")
        for w in plan["waves"]:
            groups = w["groups"]
            for a in range(len(groups)):
                for b in range(a + 1, len(groups)):
                    for x in groups[a]:
                        for y in groups[b]:
                            if x in by_id and y in by_id:
                                o = overlap(touches(by_id[x]), touches(by_id[y]))
                                if o:
                                    rep.warn(f"Wave {w['n']}: parallel tasks {x} and {y} overlap ({o})")
    elif li >= 1:
        rep.error("no waves found (expected '- **Wave 1**: T1')")


def main(argv=None):
    p = argparse.ArgumentParser(prog="validate_plan.py", description="Risk-aware structural gate for plan.md.")
    p.add_argument("target", nargs="?", default=None, help="feature name, feature dir, or plan.md path")
    p.add_argument("--root", default=".", help="project root containing .specs/")
    p.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = p.parse_args(argv)

    fdir = _sdd.resolve_feature_dir(args.target, os.path.abspath(args.root))
    plan_path = args.target if args.target and os.path.isfile(args.target) else os.path.join(fdir, "plan.md")
    spec_path = os.path.join(fdir, "spec.md")
    for pth in (plan_path, spec_path):
        if not os.path.isfile(pth):
            _sdd.die(f"validate_plan: missing {pth}")

    rep = _sdd.Report("validate_plan")
    check(_sdd.parse_spec(spec_path), _sdd.parse_plan(plan_path), rep)
    return rep.finish(plan_path, args.strict)


if __name__ == "__main__":
    sys.exit(main())
