---
name: adaptive-spec-driven
description: Risk-adaptive spec-driven development, from discovery to verified, committed code. Classifies each change LOW/MEDIUM/HIGH/CRITICAL and scales spec, plan, tests, mutation checks and independent verification to match. Produces spec.md, plan.md and, when risk calls for it, validation.md. Also covers project init, status, discuss, research, amendments, sub-agents, lessons, pause/resume, and Python gates. Use to init a project, check status, or specify, plan, implement, verify, amend, pause or resume a feature or bug fix.
license: CC-BY-4.0
metadata:
  version: 1.3.0
  derived-from: tlc-spec-driven 3.3.0 by Felipe Rodrigues (github.com/felipfr), CC-BY-4.0
---

# Adaptive Spec Driven

**Risk determines rigor.** Every change runs the full engineering loop at the depth its risk warrants. A copy tweak and a payment migration differ in how much of each phase runs, not in which phases exist.

```
PROJECT  INIT → PROJECT.md · ARCHITECTURE.md · STATE.md (optional; features work without it)
FEATURE  DISCOVER → SPECIFY → PLAN → EXECUTE → VERIFY
SESSION  STATUS (read-only) · PAUSE · RESUME
         cross-cutting: DISCUSS · RESEARCH · MEMORY · LESSONS · AMENDMENTS · SUB-AGENTS
```

## Operating contract

These rules hold even if no reference file is opened.

1. **Classify before you build.** Discover ends with a risk level ([risk.md](references/risk.md)). Re-classify whenever new evidence appears; never silently keep a stale level.
2. **Specs are the source of truth for behavior.** `SPEC` tests assert the outcome the spec defines, never what the code happens to do. When reality contradicts the spec, raise a **Spec Amendment** ([amendments.md](references/amendments.md)); never diverge silently.
3. **The gate decides done.** A task is done when its tests exist, its gate command exits 0 and the plan records it. Never weaken, skip or delete a test to get green; a genuinely wrong test needs a spec amendment or the user's agreement.
4. **Verification scales with risk and is never skipped.** Never ask the user whether to verify.
5. **Blast radius.** Approving a spec or plan authorizes local edits and local commits only. `git push`, deploys, shared or production data changes, external side effects and anything irreversible need an explicit go-ahead for that action ([execute.md](references/execute.md#blast-radius)).
6. **The agent owns tool choice** ([research.md](references/research.md)). Ask the user only for credentials, paid or side-effecting services, or product decisions.
7. **Lean code, good practices, no overengineering.** Write the smallest change that satisfies the ACs, in the project's own style and idioms ([execute.md](references/execute.md#3-implement)). Add no feature, abstraction, option or error handling the ACs do not need. Good practices (clear names, small cohesive functions, validation at boundaries, no duplication of existing code) apply to what you write, not to a rewrite of what exists.
8. **One fact, one home.** Reference it; never copy it.
9. **The skill never changes itself.** Project work never edits `<skill-dir>`.

**Loading.** `references/`, `assets/` and `scripts/` resolve relative to the directory containing this file (`<skill-dir>`). Open only the reference for the phase you are in, and within it only the sections that apply to the current risk level. LOW work opens no reference beyond Discover's. Project data lives in the project's `.specs/`.

## Risk levels and rigor profile

Rate the twelve factors in [risk.md](references/risk.md), then run `python3 <skill-dir>/scripts/risk.py`. The highest triggered rule wins. Raising a level is free; lowering below the computed level needs a written justification.

| Level | Typical shape |
| --- | --- |
| **LOW** | Local, reversible, well understood: copy, styling, safe config, isolated obvious bug fix |
| **MEDIUM** | New behavior in a bounded area, conventional persistence, read-only integration, some ambiguity |
| **HIGH** | Migrations, concurrency, side-effecting integrations, auth checks, new patterns, shared contracts |
| **CRITICAL** | Money, auth core, security boundaries, irreversible data, system of record, or several HIGH factors |

| Activity | LOW | MEDIUM | HIGH | CRITICAL |
| --- | --- | --- | --- | --- |
| Artifacts | Inline spec and plan in chat, no files | `spec.md` + `plan.md` (lite) | Full `spec.md`, `plan.md`, `validation.md`; `context.md` if discussed | All, plus invariants and rollback |
| Discuss | Skip | Only for user-facing ambiguity | Gray areas, implicit dimensions | Always: invariants and failure behavior |
| Research | If unfamiliar | If unfamiliar | Mandatory for new libraries or integrations | Mandatory, version-pinned |
| Design depth | None | Approach paragraph | Components, data, errors, alternatives | Plus failure modes and rollback |
| Approvals | None (the request is the approval) | One checkpoint: spec + plan | Spec, then plan | Spec, plan, then each irreversible step |
| Tests | Regression or characterization where behavior changes | SPEC per AC + regression | + edge/failure paths, CONTRACT at boundaries | + INVARIANT, failure injection |
| Discrimination | None | 1–3 targeted mutations on new logic | 3–5 mutations by the verifier | Mutation tooling or ≥5 manual; zero survivors |
| Verification | Author self-check | Author fresh-eyes pass | Independent verifier | Independent verifier + adversarial review + human sign-off |
| UAT | No | Optional | If user-facing | Required if user-facing |
| Lessons | Record on signal | Load + record | Load + record | Load + record |

Risk may also be set **per task** (`Risk:` field). Task risk sets that task's test and discrimination depth; feature risk sets artifacts, approvals and final verification.

**LOW track (no files).** State the change, its 1–3 ACs and the steps in a short chat block. Add or extend a regression or characterization test where observable behavior changes. Run the gate, re-read the diff, commit. If the inline plan passes ~5 steps, uncovers a new risk factor or touches shared contracts, stop and re-classify.

## Artifacts and ownership

Create files lazily: a skipped phase leaves no file, and an empty file falsely implies the phase ran.

| Fact | Lives only in |
| --- | --- |
| Stack, structure, conventions, quality commands | `.specs/PROJECT.md` |
| Test stack, layout, naming, layers, fixtures, doubles, standards | `.specs/TESTING.md` |
| Architecture: services, modules, data flow, persistence, auth, integrations | `ARCHITECTURE.md` (project root) |
| Risk level and factor ratings; requirements, ACs, invariants, scope; amendments | `.specs/features/<f>/spec.md` |
| Discussion decisions (only when Discuss ran) | `.specs/features/<f>/context.md` |
| Design, feature-local decisions, tasks, task status and SHAs, gate commands | `.specs/features/<f>/plan.md` |
| Verification evidence and verdict (MEDIUM optional, HIGH/CRITICAL required) | `.specs/features/<f>/validation.md` |
| Project decisions (`AD-NNN`) and the Handoff snapshot | `.specs/STATE.md` |
| Lessons (script-owned, never hand-edit) | `.specs/lessons.json` (readable view on demand: `lessons.py render`) |

`spec.md` has no requirement-status column. Coverage lives in `plan.md`, evidence in `validation.md`. When an approved design materially changes the documented architecture, `plan.md` records `ARCHITECTURE_UPDATE_REQUIRED` and Verify updates `ARCHITECTURE.md` on PASS ([plan.md](references/plan.md), [verify.md](references/verify.md)).

## Workflow and triggers

| Request | Phase | Reference | Template |
| --- | --- | --- | --- |
| "Init", "bootstrap project" | Init | [init.md](references/init.md) | [PROJECT.md](assets/templates/PROJECT.md), [ARCHITECTURE.md](assets/templates/ARCHITECTURE.md) |
| "Status", "where are we", "what's next" | Status (read-only; never edits or commits) | [status.md](references/status.md) | — |
| New feature, change, "build X", "fix Y"; "what risk is this" | Discover | [discover.md](references/discover.md), [risk.md](references/risk.md) | — |
| "Specify", "write requirements" | Specify | [specify.md](references/specify.md) | [spec.md](assets/templates/spec.md) |
| "Discuss", "how should this work" | ↳ Discuss | [discuss.md](references/discuss.md) | [context.md](assets/templates/context.md) |
| Unfamiliar API, library or pattern | ↳ Research | [research.md](references/research.md) | — |
| "Design", "plan", "break into tasks" | Plan | [plan.md](references/plan.md), [testing.md](references/testing.md) | [plan.md](assets/templates/plan.md) |
| "Implement", "execute", "continue T3" | Execute | [execute.md](references/execute.md) | — |
| "Verify", "validate", "UAT" | Verify | [verify.md](references/verify.md); HIGH+: [verify-high.md](references/verify-high.md) | [validation.md](assets/templates/validation.md) |
| "The spec is wrong", "we found that…" | Amendments | [amendments.md](references/amendments.md) | — |
| "Record decision", "pause", "resume" | Memory | [memory.md](references/memory.md) | [STATE.md](assets/templates/STATE.md) |
| "What have we learned", "record lesson" | Lessons | [lessons.md](references/lessons.md) | — |
| Parallel waves, verifier, worktrees | Sub-agents | [sub-agents.md](references/sub-agents.md) | — |

MEDIUM presents spec and plan together for one approval. HIGH and CRITICAL approve the spec before planning and the plan before executing.

## Deterministic gates

Run from the project root as `python3 <skill-dir>/scripts/<name>.py` (add `--root` if needed). A non-zero exit means stop and fix. Without code execution, apply the same checks by reading the artifact and say so.

| When | Script |
| --- | --- |
| End of Init | `validate_project.py` |
| Status | `status.py [feature]` (read-only) |
| End of Discover | `risk.py` |
| Before presenting a spec | `validate_spec.py <feature>` |
| Before presenting a plan | `validate_plan.py <feature>` |
| Each commit | `check_commit.py --message "…"` |
| Before declaring done | `validate_state.py <feature>` |
| After verification | `lessons.py add …` |

## Knowledge and evidence

Facts you look up; decisions you ask. Resolve what the codebase, docs or tools can answer through the chain in [research.md](references/research.md). Never invent an API, command, file, metric or test result. Stated uncertainty beats a confident fabrication that propagates into the plan.

## Output behavior

- With no human available (headless or automated runs), treat approval checkpoints as granted, answer product questions with the most reasonable default recorded as an assumption, and say so in the summary. Blast-radius rule 5 still holds.
- Respond in the user's language. Follow the project's AGENTS.md / CLAUDE.md and preserve uncommitted work.
- Do the work instead of narrating the process. Open with a one-line triage (`Risk: HIGH — migration + concurrency → full spec, plan approval, independent verification`), then produce the artifact. Do not announce phases.
- **Writing voice** for specs, plans, commits, reports and chat: verdict first, decisions stated definitively, hedging only real uncertainty (and what would resolve it), short sentences, plain verbs. In Portuguese, avoid long chains of subordinate clauses.
- Keep context lean: only the active feature's artifacts. Start from `PROJECT.md`, `STATE.md`, `TESTING.md` and the relevant `ARCHITECTURE.md` sections, then load only what a task needs. Keep `spec.md` under ~4k tokens and `plan.md` under ~8k; past that, split the feature.
