---
name: adaptive-spec-driven
description: Risk-adaptive spec-driven development that takes a feature from discovery to verified, committed code. Classifies each change as LOW, MEDIUM, HIGH or CRITICAL from ambiguity, criticality, blast radius, novelty, irreversibility, integrations, state, auth, concurrency, migrations, security and financial/data-integrity impact, then scales the spec, plan, tests, mutation checks and independent verification to that level. Artifacts are spec.md (why + what), plan.md (how + work), and validation.md when risk calls for it. Covers project init (PROJECT.md + ARCHITECTURE.md from the real codebase), a read-only status view, gray-area discussion, research, behavioral tasks with built-in tests, parallel waves, logical commits, spec amendments, sub-agents, STATE.md memory, a lessons layer, pause/resume, deterministic Python gates and blast-radius protection. Includes user-controlled self-improvement (evolve): proposes evidence-backed changes to the skill itself and applies them only after approval. Use to initialize a project, check status, or specify, plan, implement, verify, amend, pause or resume a feature or bug fix, or to evolve the workflow. Not for standalone architecture design work outside init.
license: CC-BY-4.0
metadata:
  version: 1.2.0
  derived-from: tlc-spec-driven 3.3.0 by Felipe Rodrigues (github.com/felipfr), CC-BY-4.0
---

# Adaptive Spec Driven

**Risk determines rigor.** Run the full engineering loop for every change, at the depth its risk warrants. A copy tweak and a payment migration go through the same phases. They differ in how much of each phase runs.

```
PROJECT     INIT → project ready (PROJECT.md · ARCHITECTURE.md · STATE.md)
FEATURE     DISCOVER → SPECIFY → PLAN → EXECUTE → VERIFY
SESSION     STATUS (read-only) · PAUSE · RESUME
SKILL       EVOLVE (analyze → propose → user approval → modify → validate)
        cross-cutting: DISCUSS · RESEARCH · MEMORY · LESSONS
                       SPEC AMENDMENTS · SUB-AGENTS
```

Init is project-level and optional: features work without it. Status, pause and resume act on work state. Evolve acts on the skill itself, never on the project.

## Operating contract

These rules hold even if no reference file is opened.

1. **Classify before you build.** Discover ends with a risk level ([risk.md](references/risk.md)). The level selects the rigor profile below. Re-classify whenever new evidence appears; never silently keep a stale level.
2. **Specs are the source of truth for behavior.** Tests with origin `SPEC` assert the outcome the spec defines, never what the code happens to do. When reality contradicts the spec, raise a **Spec Amendment** ([amendments.md](references/amendments.md)) and do not silently diverge.
3. **The gate decides done.** A task is done when its tests exist, its gate command exits 0 and the plan records it. Self-assessment never substitutes for the runner. Never weaken, skip or delete a test to get green; a test that is genuinely wrong needs a spec amendment or the user's agreement.
4. **Verification scales with risk and is never skipped.** LOW gets a self-check. CRITICAL gets an independent verifier, adversarial review and human sign-off. Never ask the user whether to verify; the risk level already answered that.
5. **Blast radius.** Approval of a spec or plan authorizes local edits and local commits only. `git push`, force-push, deploys, shared or production data changes, and anything irreversible or externally visible need an explicit go-ahead for that specific action.
6. **The agent owns tool choice.** Pick the MCPs, skills, CLIs and search tools yourself ([research.md](references/research.md)). Ask the user only for credentials, paid or side-effecting services, or genuine product decisions.
7. **One fact, one home.** Each piece of state lives in exactly one artifact (see the ownership table below). Reference it; never copy it.
8. **The skill never changes itself.** It may propose improvements to its own workflow, but edits to `<skill-dir>` happen only through Evolve, after the user approves that specific proposal ([evolve.md](references/evolve.md)).

**Loading this skill's files.** `references/`, `assets/` and `scripts/` resolve relative to the directory containing this `SKILL.md` (`<skill-dir>`), never the project root. Read a reference completely before acting on it. Project data lives in the project's `.specs/`.

## Risk levels and rigor profile

Rate the twelve factors in [risk.md](references/risk.md), then compute the level with `python3 <skill-dir>/scripts/risk.py`. The highest triggered rule wins. You may raise a level freely; lowering below the computed level needs a written justification.

| Level | Typical shape |
| --- | --- |
| **LOW** | Local, reversible, well-understood: copy, styling, config with no runtime risk, isolated bug with an obvious fix |
| **MEDIUM** | New behavior in a bounded area, conventional persistence, a read-only integration, some ambiguity |
| **HIGH** | Migrations, concurrency, side-effecting integrations, auth checks, new architectural patterns, shared contracts with many callers |
| **CRITICAL** | Money, authentication core, security boundaries, irreversible data changes, system-of-record integrity, or several HIGH factors at once |

| Activity | LOW | MEDIUM | HIGH | CRITICAL |
| --- | --- | --- | --- | --- |
| Artifacts | Inline spec and plan in chat | `spec.md` + `plan.md` (lite) | Full `spec.md`, `plan.md`, `validation.md`; `context.md` if discussed | All, plus invariants and rollback |
| Discuss | Skip | Only for user-facing ambiguity | Gray areas and implicit dimensions | Always confirm invariants and failure behavior |
| Research | When unfamiliar | When unfamiliar | Mandatory for new libraries or integrations | Mandatory and version-pinned |
| Design depth | None | Approach paragraph | Components, data, errors, alternatives | Plus failure modes and rollback |
| Approvals | None (the request is the approval) | One checkpoint: spec + plan together | Spec, then plan | Spec, plan, then each irreversible step |
| Tests | Regression or characterization where behavior changes | SPEC per AC + regression | + edge/failure paths, CONTRACT at boundaries | + INVARIANT (property-based where available), failure injection |
| Discrimination | None | 1–3 targeted mutations on new logic | 3–5 mutations by the verifier | Mutation tooling or ≥5 manual, all invariant branches, zero survivors |
| Verification | Author self-check | Author fresh-eyes pass | Independent verifier | Independent verifier + adversarial review + human sign-off |
| UAT | No | Optional | If user-facing | Required if user-facing |
| Lessons | Record on signal | Load + record | Load + record | Load + record |

Risk may also be set **per task**. A CRITICAL feature can contain a LOW task (a label change); a MEDIUM feature can contain one HIGH task (the migration). Task-level risk sets that task's test and discrimination depth. Feature-level risk sets artifacts, approvals and final verification.

## Artifacts and ownership

```
ARCHITECTURE.md       # How the system is built (project root; written by init)
.specs/
├── PROJECT.md        # What the project is: stack, structure, conventions, quality commands
├── STATE.md          # Project decisions (AD-NNN) + Handoff snapshot
├── LESSONS.md        # Rendered lessons playbook (script-owned, do not hand-edit)
├── lessons.json      # Canonical lessons store (script-owned)
└── features/<feature>/
    ├── spec.md        # WHY + WHAT: problem, scope, risk, ACs, invariants, amendments
    ├── context.md     # Discussion decisions — only when Discuss ran
    ├── plan.md        # HOW + WORK: approach, design, tasks with tests, waves, gates
    └── validation.md  # Verification evidence — MEDIUM optional, HIGH/CRITICAL required
```

Create files lazily. A skipped phase leaves no file; an empty file falsely implies the phase ran. LOW work normally creates no files at all.

| Fact | Lives only in | Others do |
| --- | --- | --- |
| Stack, structure, conventions, quality commands | `.specs/PROJECT.md` | Discover reads it; `plan.md` gates use the real commands |
| Architecture: services, modules, data flow, persistence, auth, integrations | `ARCHITECTURE.md` | `PROJECT.md` links to it; `plan.md` flags `ARCHITECTURE_UPDATE_REQUIRED` |
| Risk level and factor ratings | `spec.md` → Risk Assessment | `plan.md` and `validation.md` cite the level |
| Requirements, ACs, invariants, scope | `spec.md` | `plan.md` references IDs in `Covers` |
| Spec changes after approval | `spec.md` → Amendments | Tasks reference `A-NN` |
| Design and feature-local decisions | `plan.md` → Design | — |
| Task status and commit SHAs | `plan.md` → Tasks | Handoff points to the task ID |
| Gate commands | `plan.md` → Verification Commands | Tasks name the gate level only |
| Verification evidence and verdict | `validation.md` (or the chat summary below HIGH) | `plan.md` does not repeat it |
| Project-wide decisions | `STATE.md` → Decisions | `plan.md` cites `AD-NNN` |
| In-flight session state | `STATE.md` → Handoff | — |
| Candidate improvements to the skill itself | `<skill-dir>/EVOLUTION.md` (only when one exists) | Never in `.specs/` |

There is no requirement-status column in `spec.md`. Coverage lives in `plan.md`, evidence in `validation.md`.

## Workflow

| Phase | Purpose | Reference | Template |
| --- | --- | --- | --- |
| Init (project) | Discover the project, write `PROJECT.md`, `ARCHITECTURE.md`, `STATE.md`; idempotent | [init.md](references/init.md) | [PROJECT.md](assets/templates/PROJECT.md), [ARCHITECTURE.md](assets/templates/ARCHITECTURE.md) |
| Discover | Understand the request and the code, assess blast radius, classify risk | [discover.md](references/discover.md), [risk.md](references/risk.md) | — |
| Specify | Problem, scope, testable ACs, assumptions | [specify.md](references/specify.md) | [spec.md](assets/templates/spec.md) |
| ↳ Discuss | Resolve gray areas with the user | [discuss.md](references/discuss.md) | [context.md](assets/templates/context.md) |
| ↳ Research | Verify unfamiliar APIs and patterns; pick tools | [research.md](references/research.md) | — |
| Plan | Design plus behavioral tasks with embedded tests and waves | [plan.md](references/plan.md), [testing.md](references/testing.md) | [plan.md](assets/templates/plan.md) |
| Execute | Implement task by task, gate, commit logical units | [execute.md](references/execute.md) | — |
| Verify | Risk-scaled evidence that the spec is met | [verify.md](references/verify.md) | [validation.md](assets/templates/validation.md) |
| Evolve (skill) | Propose and, after approval, apply changes to this skill | [evolve.md](references/evolve.md) | — |

**LOW track (no files).** State the change, its 1–3 ACs and the steps in a short chat block. Add or extend a regression or characterization test where observable behavior changes. Run the gate, re-read the diff, commit. If the inline plan grows past ~5 steps, uncovers a new risk factor, or touches shared contracts, stop and re-classify; LOW was wrong.

**MEDIUM track.** Write a lite `spec.md` and `plan.md` and present them together for one approval. Execute, then run the fresh-eyes verification and report the evidence table in chat.

**HIGH and CRITICAL tracks.** Follow every phase. Approve the spec before planning and the plan before executing. CRITICAL also approves each irreversible step at the moment it runs.

**Status.** Read-only: project, active feature, risk, phase progress, current and next task, blockers, git, drift and the suggested next action. It never edits, commits or fixes stale state ([status.md](references/status.md)).

**Resume.** Read `.specs/STATE.md`, reconcile the Handoff against git and `plan.md`, persist the reconciliation, and propose the next step before editing ([memory.md](references/memory.md)).

**Evolve.** Change the skill itself. `evolve: <change>` analyzes an explicit request; bare `evolve` reviews lessons, overrides, amendments, recurring friction and the skill's own consistency, and proposes only evidence-backed improvements. Every proposal shows Problem, Evidence, Proposed change, Files affected and Expected impact; changes to core principles are flagged. Nothing is edited before approval; after editing, links, rules and scripts are re-validated. Candidates without enough evidence may go to `<skill-dir>/EVOLUTION.md`, which is about the skill, unlike `.specs/LESSONS.md`, which is about the project ([evolve.md](references/evolve.md)).

**Architecture drift.** When an approved design materially changes the documented architecture (new service, database, layer, external system, auth or data-flow change, module boundary move), `plan.md` records `ARCHITECTURE_UPDATE_REQUIRED` and Verify updates `ARCHITECTURE.md` when the feature passes. Trivial changes do not touch it.

## Spec amendments

Implementation teaches things the spec did not know. When a task reveals that an AC is wrong, infeasible, incomplete or riskier than assessed, stop that task and classify the discovery: **clarification**, **behavior change**, **scope change** or **risk change**. Record it as `A-NN` in `spec.md`, update the affected ACs in place with an `(A-NN)` tag, and get approval proportional to risk before continuing. Scope changes become deferred items or new features, never silent additions. Full procedure: [amendments.md](references/amendments.md).

## Sub-agents and parallelism

Tasks in the same **wave** have no dependencies on each other and touch disjoint surfaces, so they may run in parallel: workers in isolated worktrees, integrated by the orchestrator, followed by the full gate. The **Verifier** is always a fresh context (author ≠ verifier) at HIGH and CRITICAL. Use sub-agents when they pay off and the harness allows them. If the harness or the user requires consent before spawning agents, ask once per feature. Without sub-agents, run waves sequentially and do verification as an explicit context-reset pass. Details: [sub-agents.md](references/sub-agents.md).

## Deterministic gates

Scripts enforce structure so it does not depend on memory. Run them from the project root as `python3 <skill-dir>/scripts/<name>.py` (pass `--root` if needed). A non-zero exit means stop and fix. Without a code-execution tool, apply the same checks by reading the artifact and say so.

| When | Script | Checks |
| --- | --- | --- |
| End of Init | `validate_project.py` | `PROJECT.md`, `STATE.md` and the architecture doc exist; core sections; `PROJECT.md` links the architecture doc; no placeholders |
| Status | `status.py [feature]` | Read-only: phase progress, current/next task, git state, Handoff drift |
| End of Discover | `risk.py` | Computes the level from factor ratings and prints the rigor profile |
| Before presenting a spec | `validate_spec.py <feature>` | Risk sections per level, declared vs. computed risk, AC IDs and testability smells, assumptions closed, amendments well-formed |
| Before presenting a plan | `validate_plan.py <feature>` | Every AC covered, test origins valid, SPEC tests anchored, invariants tested, dependencies acyclic, waves consistent, required sections per risk |
| Each commit | `check_commit.py --message "…"` | Conventional Commits |
| Before declaring done | `validate_state.py <feature>` | All tasks done, no open amendments, verification evidence meets the risk level |
| After verification | `lessons.py add …` | Grounded lesson bookkeeping |

## Memory and lessons

`STATE.md` holds project-level decisions (`AD-NNN`, recorded sparingly) and a Handoff snapshot overwritten at each pause. Writes are section-scoped, never whole-file ([memory.md](references/memory.md)). Lessons turn grounded verification failures into project-local guidance. Load confirmed lessons at Discover and Plan for MEDIUM and above. Record one lesson per real signal after verification ([lessons.md](references/lessons.md)).

## Knowledge and evidence

Facts you look up; decisions you ask. Resolve anything the codebase, docs or tools can answer through the chain in [research.md](references/research.md): codebase → project docs → library docs (Context7 or equivalent) → web → explicitly flagged uncertainty. Never invent an API, command, file, metric or test result. Uncertainty stated plainly beats a confident fabrication that propagates into the plan.

## Output behavior

- Respond in the user's language. Follow the project's AGENTS.md / CLAUDE.md and preserve uncommitted work.
- Do the work instead of narrating the process. Open with a one-line triage (`Risk: HIGH — migration + concurrency → full spec, plan approval, independent verification`), then produce the artifact.
- Write artifacts in a plain, decided voice: verdict first, definitive decisions, no filler ([execute.md](references/execute.md#writing-voice)).
- Keep loaded context lean: the active feature's artifacts, never several features' specs at once. At the start of a feature, `PROJECT.md`, `STATE.md` and the relevant `ARCHITECTURE.md` sections are the initial context; after that, load only the parts a task needs. Keep `spec.md` under ~4k tokens and `plan.md` under ~8k; past that, split the feature.

## Triggers

| Request | Start at |
| --- | --- |
| "Init", "initialize project", "setup adaptive spec", "bootstrap project", "start project" | Init |
| "Status", "project / feature status", "where are we", "what's next" | Status (read-only) |
| New feature, change, "build X", "fix Y" | Discover |
| "Specify", "write requirements" | Specify |
| "Discuss", "how should this work" | Discuss |
| "Design", "plan", "break into tasks" | Plan |
| "Implement", "execute", "continue T3" | Execute |
| "Verify", "validate", "UAT", "walk me through it" | Verify |
| "The spec is wrong", "we found that…" | Amendments |
| "Record decision", "pause", "resume" | Memory |
| "What have we learned", "record lesson" | Lessons |
| "What risk is this", "how rigorous should we be" | Risk |
| "Evolve", "evolve skill", "improve skill", "update adaptive spec", "change workflow" | Evolve (proposes only; edits after approval) |
