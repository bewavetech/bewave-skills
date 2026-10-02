# Status

**Goal:** answer "where are we and what should happen next?" in a few lines, from evidence.

Triggered by "status", "project status", "feature status", "adaptive spec status", "where are we", "what's next".

**Status is read-only.** It never edits files, implements, updates task statuses, commits, creates specs or runs tasks. It reports drift; it does not fix it. Persistent reconciliation belongs to Resume ([memory.md](memory.md#resume)).

**Evidence wins over stale state.** `STATE.md` → Handoff is a hypothesis. `plan.md` statuses and git are evidence.

## 1. Gather

```bash
python3 <skill-dir>/scripts/status.py
```

The script is read-only. It reads `PROJECT.md` (project name), `STATE.md` → Handoff, the active feature's `spec.md`, `plan.md` and `validation.md`, and git (branch, `git status --porcelain`, recent commits). It prints phase progress, the current and next task, and any drift it can detect deterministically. Pass a feature name to look at a specific feature.

Without code execution, read the same sources yourself in this order and stop as soon as the picture is complete:

1. `.specs/PROJECT.md` → title / Overview (project name only).
2. `.specs/STATE.md` → Handoff (feature, risk, where, next step, blockers, branch).
3. Active feature: the Handoff feature; otherwise the only feature whose plan has unfinished tasks.
4. That feature's `spec.md` (declared risk, amendments), `plan.md` (task statuses, waves), `validation.md` (verdict).
5. Git: `git branch --show-current`, `git status --porcelain`, `git log --oneline -10`.

Load only these. Do not read source code or other features.

## 2. Derive

| Phase | Done when |
| --- | --- |
| Discover | `spec.md` exists with a Risk Assessment |
| Spec | `spec.md` exists; no amendment `proposed` |
| Plan | `plan.md` has tasks |
| Execute | `done + dropped` / total tasks; current = first `[~]`, next = first `[ ]` in wave order |
| Verify | `validation.md` verdict PASS (HIGH/CRITICAL), or all tasks done and verification reported (MEDIUM/LOW) |

LOW work has no files. If the Handoff names a feature with no folder, report the Handoff's **Next step** as-is.

## 3. Reconcile (report only)

| Evidence | Drift |
| --- | --- |
| Handoff names task T3 as in progress; `plan.md` marks it `[x]` | Handoff is stale; resume from the next open task |
| A commit mentions `T3` but `plan.md` still shows it open | Plan status is stale |
| Handoff branch ≠ current branch | Wrong branch, or Handoff is stale |
| Handoff says "Uncommitted: none" but the tree is dirty (or the reverse) | Unrecorded work |
| Handoff names a feature whose folder does not exist | Handoff is stale |
| Several features have open tasks and the Handoff names none | Ambiguous active feature; list them |
| Amendment `proposed` | Blocked on approval |

Name the evidence for each drift. Do not edit `STATE.md` or `plan.md`; suggest `resume` to persist the reconciliation.

## 4. Report

Short and operational. Keep these fields when they apply; omit the ones that do not.

```
Adaptive Spec Driven — Status

Project: Profiza
Active feature: provider-reviews · Risk MEDIUM

Progress
✓ Discover  ✓ Spec  ✓ Plan  ◉ Execute 3/5  ○ Verify

Current: T4 — Integrate reviews into provider profile
Next:    T5 — Add review summary to search results
Blockers: none

Git: feature/provider-reviews · 2 modified files

Suggested next action: continue T4.
```

No active feature:

```
Adaptive Spec Driven — Status

Project: Profiza
Active feature: none
Repository: clean
Open work: none

Suggested next action: start a new feature.
```

Drift:

```
State drift detected.

STATE.md: T3 is in progress.
plan.md / git: T3 is done (a1b2c3d); T4 is the next open task.

Suggested next action: resume from T4.
```

Not initialized (no `.specs/`): say so and suggest `init`, or starting a feature directly.
