#!/usr/bin/env python3
"""
status.py - read-only snapshot of where the work is and what comes next.

Never writes anything: no file edits, no git index refresh (git runs with
--no-optional-locks). Drift between STATE.md -> Handoff and the evidence
(plan.md, git) is reported, never fixed; resume owns reconciliation.

Reads:
  .specs/PROJECT.md      project name (first heading)
  .specs/STATE.md        ## Handoff
  .specs/features/<f>/   spec.md (risk, amendments), plan.md (tasks, waves),
                         validation.md (verdict)
  git                    branch, porcelain status, recent commits

Active feature: the argument, else the Handoff feature, else the only open
feature (spec without plan, or plan with unfinished tasks).

Usage:
  python3 <skill-dir>/scripts/status.py [feature] [--root DIR]

Exit codes: 0 ok, 2 usage error.
"""

import argparse
import os
import re
import subprocess
import sys

import _sdd

NONE_RE = re.compile(r"^\s*(none|n/a|-|—)?\s*$", re.IGNORECASE)


def git(root, *args):
    try:
        r = subprocess.run(["git", "--no-optional-locks", *args], cwd=root,
                           capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout if r.returncode == 0 else None


def project_name(root):
    path = os.path.join(root, ".specs", "PROJECT.md")
    if os.path.isfile(path):
        for ln in _sdd.read_clean(path).splitlines():
            m = re.match(r"^#\s+(.+)$", ln.strip())
            if m:
                name = re.sub(r"^project\s*[:—–-]?\s*", "", m.group(1).strip(), flags=re.IGNORECASE)
                if name and not _sdd.has_placeholder(name):
                    return name
                break
    return os.path.basename(root)


def handoff(root):
    path = os.path.join(root, ".specs", "STATE.md")
    if not os.path.isfile(path):
        return None
    body = _sdd.section_lines(_sdd.read_clean(path).splitlines(), "Handoff")
    keys = ["Feature", "Risk", "Where", "In progress", "Next step", "Open amendments",
            "Blockers", "Uncommitted", "Branch", "Updated"]
    h = {k: _sdd.field(body, k) for k in keys}
    feat = h["Feature"] or ""
    m = re.match(r"^\s*`?([\w.-]+)`?", feat)
    h["feature_name"] = None if (NONE_RE.match(feat) or not m or m.group(1).lower() == "none") else m.group(1)
    return h


def is_none(value):
    return value is None or bool(NONE_RE.match(value))


def feature_info(fdir):
    info = {"name": os.path.basename(fdir.rstrip("/")), "dir": fdir, "spec": None, "plan": None,
            "verdict": None, "level": None}
    sp, pp, vp = (os.path.join(fdir, n) for n in ("spec.md", "plan.md", "validation.md"))
    if os.path.isfile(sp):
        info["spec"] = _sdd.parse_spec(sp)
        info["level"] = _sdd.spec_level(info["spec"])
    if os.path.isfile(pp):
        info["plan"] = _sdd.parse_plan(pp)
    if os.path.isfile(vp):
        v = _sdd.field(_sdd.read_clean(vp).splitlines(), "Verdict") or ""
        has_pass, has_fail = bool(re.search(r"\bPASS\b", v)), bool(re.search(r"\bFAIL\b", v))
        info["verdict"] = "PASS" if has_pass and not has_fail else "FAIL" if has_fail and not has_pass else None
    return info


def ordered_tasks(plan):
    """Tasks in wave order, then any task not listed in a wave, in file order."""
    by_id = {t["id"]: t for t in plan["tasks"]}
    seen, out = set(), []
    for w in sorted(plan["waves"], key=lambda w: w["n"]):
        for group in w["groups"]:
            for tid in group:
                if tid in by_id and tid not in seen:
                    seen.add(tid)
                    out.append(by_id[tid])
    return out + [t for t in plan["tasks"] if t["id"] not in seen]


def is_open(info):
    if info["plan"] is None:
        return info["spec"] is not None
    tasks = info["plan"]["tasks"]
    if not tasks or any(_sdd.task_status(t) in ("pending", "progress", "invalid") for t in tasks):
        return True
    return _sdd.level_index(info["level"]) >= 2 and info["verdict"] != "PASS"


def main(argv=None):
    p = argparse.ArgumentParser(prog="status.py", description="Read-only Adaptive Spec Driven status.")
    p.add_argument("feature", nargs="?", default=None, help="feature name or dir")
    p.add_argument("--root", default=".", help="project root containing .specs/")
    args = p.parse_args(argv)
    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        _sdd.die(f"not a directory: {root}")

    out, drift, notes = [], [], []
    initialized = os.path.isdir(os.path.join(root, ".specs"))
    h = handoff(root)
    feats = _sdd.list_features(root)
    base = os.path.join(root, ".specs", "features")

    # Git evidence.
    branch = (git(root, "branch", "--show-current") or "").strip() or None
    porcelain = git(root, "status", "--porcelain")
    dirty = [l for l in (porcelain or "").splitlines() if l.strip()]
    log = git(root, "log", "--oneline", "-20") or ""
    commits = [l.split(" ", 1) for l in log.splitlines() if " " in l]

    # Active feature.
    active, ambiguous = None, []
    if args.feature:
        active = feature_info(_sdd.resolve_feature_dir(args.feature, root))
    elif h and h["feature_name"]:
        fdir = os.path.join(base, h["feature_name"])
        if os.path.isdir(fdir):
            active = feature_info(fdir)
        else:
            notes.append(f"Handoff feature '{h['feature_name']}' has no folder (LOW inline work, or stale Handoff)")
    if active is None and not args.feature:
        open_feats = [i for i in (feature_info(os.path.join(base, f)) for f in feats) if is_open(i)]
        if len(open_feats) == 1:
            active = open_feats[0]
            if h and h["feature_name"] is None and h["Feature"] is not None:
                drift.append(f"STATE.md Handoff says no active feature, but {active['name']} has open work")
        elif len(open_feats) > 1:
            ambiguous = [i["name"] for i in open_feats]

    out.append("Adaptive Spec Driven — Status")
    out.append("")
    out.append(f"Project: {project_name(root)}")
    if not initialized:
        out.append("Initialized: no (.specs/ missing)")

    current = nxt = None
    if active:
        level = active["level"] or (h and h.get("Risk")) or "unknown"
        out.append(f"Active feature: {active['name']} · Risk {level}")
        spec, plan = active["spec"], active["plan"]
        tasks = ordered_tasks(plan) if plan else []
        done = [t for t in tasks if _sdd.task_status(t) in ("done", "dropped")]
        current = next((t for t in tasks if _sdd.task_status(t) == "progress"), None)
        nxt = next((t for t in tasks if _sdd.task_status(t) in ("pending", "invalid") and t is not current), None)
        proposed = [a["id"] for a in (spec["amendments"] if spec else []) if a["status"] == "proposed"]
        all_done = bool(tasks) and len(done) == len(tasks)

        def mark(ok, active_now):
            return "✓" if ok else "◉" if active_now else "○"

        disc = spec is not None and spec["sections"].get("Risk Assessment")
        spec_ok = spec is not None and not proposed
        plan_ok = bool(tasks)
        if _sdd.level_index(active["level"]) >= 2:
            verify_ok = active["verdict"] == "PASS"
        else:
            verify_ok = all_done and active["verdict"] != "FAIL"
        exec_label = f"Execute {len(done)}/{len(tasks)}" if tasks else "Execute"
        verify_label = "Verify" + (" (FAIL)" if active["verdict"] == "FAIL" else "")
        stages = [
            (disc, not disc, "Discover"),
            (spec_ok, disc and not spec_ok, "Spec"),
            (plan_ok, spec_ok and not plan_ok, "Plan"),
            (all_done, plan_ok and not all_done, exec_label),
            (verify_ok, all_done and not verify_ok, verify_label),
        ]
        out.append("")
        out.append("Progress")
        out.append("  ".join(f"{mark(ok, now)} {label}" for ok, now, label in stages))
        out.append("")
        if current:
            out.append(f"Current: {current['id']} — {current['title']}")
        if nxt:
            out.append(f"Next:    {nxt['id']} — {nxt['title']}")
        if proposed:
            out.append(f"Open amendments: {', '.join(proposed)} (proposed)")

        # Drift: Handoff vs plan.md vs git.
        if h and h["feature_name"] == active["name"]:
            where = " ".join(filter(None, [h.get("Where"), h.get("In progress")]))
            m = re.search(r"\b([TF]\d+)\b[^;,.]*\bin progress\b", where, re.IGNORECASE)
            claimed = m.group(1) if m else (current is None and (re.findall(r"\b[TF]\d+\b", where) or [None])[0])
            by_id = {t["id"]: t for t in tasks}
            if claimed and claimed in by_id and _sdd.task_status(by_id[claimed]) in ("done", "dropped"):
                follow = f"{nxt['id']} is the next open task" if nxt else "no open task remains"
                drift.append(f"STATE.md: {claimed} is in progress. plan.md: {claimed} is "
                             f"{by_id[claimed]['fields'].get('status', '?')}; {follow}")
            hb = (h.get("Branch") or "").strip("` ")
            if hb and branch and not is_none(hb) and hb != branch:
                drift.append(f"STATE.md branch is {hb}; current branch is {branch}")
            if porcelain is not None:
                unc = h.get("Uncommitted")
                if is_none(unc) and dirty and unc is not None:
                    drift.append(f"STATE.md says nothing uncommitted; git has {len(dirty)} changed path(s)")
                elif unc is not None and not is_none(unc) and not dirty:
                    drift.append("STATE.md lists uncommitted files; the working tree is clean")
        for t in tasks:
            if _sdd.task_status(t) in ("pending", "progress"):
                hits = [sha for sha, msg in commits if re.search(r"\b%s\b" % re.escape(t["id"]), msg)]
                if hits:
                    drift.append(f"commit {hits[0]} mentions {t['id']}, which plan.md still shows as "
                                 f"{t['fields'].get('status', '?')}")
    elif ambiguous:
        out.append(f"Active feature: ambiguous — open work in {', '.join(ambiguous)}")
    else:
        out.append("Active feature: none")

    blockers = h.get("Blockers") if h else None
    out.append(f"Blockers: {blockers if blockers and not is_none(blockers) else 'none'}")
    if h and h.get("Next step") and not is_none(h["Next step"]):
        out.append(f"Handoff next step: {h['Next step']}")
    if branch is None and porcelain is None:
        out.append("Git: unavailable")
    else:
        state = "clean" if not dirty else f"{len(dirty)} changed path(s)"
        out.append(f"Git: {branch or '(detached)'} · {state}")
        if commits:
            out.append(f"Last commit: {commits[0][0]} {commits[0][1]}")

    for n in notes:
        out.append(f"Note: {n}")
    if drift:
        out.append("")
        out.append("State drift detected (evidence wins; status does not fix it — run resume):")
        out += [f"  - {d}" for d in drift]

    # Suggested next action.
    if not initialized:
        action = "run init, or start a feature"
    elif ambiguous:
        action = "pick the feature to continue, then resume"
    elif not active:
        action = "start a new feature" if not dirty else "review the uncommitted changes, then start a feature"
    elif active["spec"] and [a for a in active["spec"]["amendments"] if a["status"] == "proposed"]:
        action = "decide the proposed amendment(s)"
    elif drift:
        action = "resume to reconcile" + (f", then continue from {(current or nxt)['id']}" if (current or nxt) else "")
    elif current:
        action = f"continue {current['id']}"
    elif nxt:
        action = f"start {nxt['id']}"
    elif active["plan"] is None:
        action = "write the plan" if active["spec"] else "specify the feature"
    elif active["verdict"] == "FAIL":
        action = "turn the verification gaps into fix tasks"
    elif _sdd.level_index(active["level"]) >= 2 and active["verdict"] != "PASS":
        action = "run verification"
    else:
        action = "feature complete; start the next one (push/PR need your go-ahead)"
    out.append("")
    out.append(f"Suggested next action: {action}.")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
