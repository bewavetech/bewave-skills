# Evolve

**Goal:** let the user change this skill, or have it point out where it could improve, without the methodology ever changing itself.

> The skill may identify how it could improve, but only the user decides when the methodology itself changes.

Triggered by "evolve", "evolve skill", "improve skill", "update adaptive spec", "change workflow". `evolve: <change>` is an explicit change; bare `evolve` is a self-assessment.

**Scope.** Evolve edits files under `<skill-dir>` (this `SKILL.md`, `references/`, `assets/`, `scripts/`, `EVOLUTION.md`). It never edits the consumer project, and project work never edits the skill. If a feature is in flight, finish or pause it first; evolve is not a side effect of building something.

## The safety loop

```
Analyze → Propose → User approval → Modify → Validate
```

- **Never modify the skill without approval of that specific proposal.** Approval of a spec, plan or earlier proposal does not carry over. A request to evolve is a request to analyze and propose, not to edit.
- **Analyze and Propose are read-only.** No edits, no `EVOLUTION.md` writes, no commits.
- **Approval is per proposal.** The user may approve some, reject some, or edit them. Apply exactly what was approved.

Every proposal is shown before approval in this shape:

```
E-1  Skip validation.md for MEDIUM unless a gate failed
Problem:          <what goes wrong today, in one or two sentences>
Evidence:         <concrete sources: features, amendments, overrides, lessons, user statements>
Proposed change:  <the rule as it would read after the change>
Files affected:   SKILL.md (rigor table), references/verify.md, scripts/validate_state.py
Expected impact:  <what gets cheaper, safer or clearer; what gets weaker>
```

Flag a proposal **⚠ CORE** when it is destructive, large, or touches a central principle: the operating contract, risk levels or their computation, "the gate decides done", verification never skipped, blast-radius rules, removing a phase, a script or a gate, or loosening any CRITICAL requirement. A CORE proposal states what protection is lost and needs its own explicit approval; it is never bundled with others.

## Mode 1: explicit change (`evolve: <change>`)

1. **Analyze.** Read `SKILL.md` and every file the change touches. Search the skill for the rule's other homes (`grep -rn` across `<skill-dir>`): rigor table, track descriptions, references, templates, script checks and their docstrings. A rule enforced by a script and documented in prose changes in both places.
2. **Assess.** List conflicts with other rules, the operating contract and the ownership table, and what a weaker rule could let through. If the change contradicts a principle, say so and flag it ⚠ CORE. If the request is ambiguous ("fewer approvals"), propose the narrowest reading and name the alternatives.
3. **Propose** in the shape above. Usually one proposal; split it when parts can be accepted independently.
4. **Wait for approval.**
5. **Modify** only what was approved. Keep the surrounding voice and structure; this is an edit, not a rewrite.
6. **Validate** (below).

Example: `evolve: don't generate validation.md for LOW features`. LOW already creates no files, so the analysis reports that the rule exists (SKILL.md → rigor table and LOW track) and proposes nothing. Saying "no change needed" is a valid outcome.

## Mode 2: self-assessment (`evolve`)

Gather evidence, classify it, and propose only what survives.

### Evidence sources

Read from the current project and the skill. Load summaries, not every artifact in full.

| Source | Signals a workflow problem when |
| --- | --- |
| `.specs/LESSONS.md` / `lessons.py list` | Confirmed lessons cluster on one phase (e.g. many `spec_precision_gap` → Specify guidance is weak); a lesson is quarantined because the rule it relied on did not help |
| `spec.md` → Risk Assessment `Override:` lines across features | The same factor is overridden downward for the same reason repeatedly → `risk.md` overweights it |
| `spec.md` → Amendments | The same amendment type recurs across features (e.g. risk changes found at Execute → Discover misses a factor) |
| `validation.md` and lessons with `escaped_defect` | Defects escaped at a risk level whose profile should have caught them |
| `plan.md` | Sections routinely left empty or `N/A`; tasks routinely split or merged at Execute |
| `STATE.md` → Decisions / Handoff | Decisions that override skill defaults; repeated resume drift of the same kind |
| Git history of `.specs/` | Artifacts created and deleted, or approvals followed by immediate rewrites |
| The current conversation | The user overrode a skill rule, skipped a step, or said a step was pointless |
| `<skill-dir>` itself | Broken links, a rule stated differently in two files, a script check with no documented rule (or the reverse), a trigger with no destination |
| `<skill-dir>/EVOLUTION.md` | Open candidates that now have more evidence, or that were contradicted |

If there is no `.specs/` and no conversation history, only the structural review applies. Say so.

### Classify before proposing

Not every problem is the skill's problem. Walk each finding down this ladder and stop at the first level that explains it:

```
implementation problem         a bug, a bad test, a wrong call by the agent → fix the code; record a lesson if it is a signal
↓
project-specific problem       this codebase, team or domain → PROJECT.md, STATE.md decision, or a project lesson
↓
recurring workflow problem     same friction across ≥2 distinct features, or a structural defect in the skill
↓
candidate skill improvement    a concrete rule change that would have prevented the recurrences
```

Only the last level becomes a proposal. The agent not following an existing rule is an implementation problem, not a missing rule.

### Evidence threshold

- **Propose** when the problem recurs in ≥2 distinct features, the user explicitly stated it, or it is a structural defect in the skill (broken link, contradicting rules, script/prose mismatch).
- **Record as a candidate** in `EVOLUTION.md` (with the user's approval) when there is one solid occurrence and a plausible pattern.
- **Drop** everything else. Do not pad the list.

### Report

```
Adaptive Spec Driven — Evolve

Reviewed: 4 features, 7 lessons (3 confirmed), 5 amendments, skill structure
Classified: 6 findings → 3 implementation, 1 project-specific, 2 workflow

Proposals
E-1  …   (full shape)
E-2  ⚠ CORE  …

Candidates (single occurrence, not proposed)
- …

Not skill problems
- provider-reviews: flaky date test → implementation; lesson L-004 already covers it
```

No proposals is a valid result: "No skill change is warranted by the current evidence."

## Validate

After modifying, before reporting done:

1. **References resolve.** Every relative link in the touched files, and in `SKILL.md`, points to an existing file and anchor.
2. **One rule, one statement.** `grep -rn` the changed rule across `<skill-dir>`; no file still states the old version. The rigor table, track descriptions, references, templates and script checks agree.
3. **Scripts still run.** For each touched script: `python3 -m py_compile <script>`; `python3 scripts/lessons.py selftest` if `lessons.py` changed. When a check changed, run the script against a sample or the current `.specs/` and confirm it now accepts and rejects what the new rule says.
4. **Triggers and tables.** New or renamed phases appear in the `SKILL.md` diagram, workflow table and Triggers; the frontmatter `description` still describes the skill.
5. **Version.** Bump `metadata.version` in `SKILL.md`: patch for wording, minor for a new or changed rule, major for a CORE change.
6. **Bookkeeping.** If the change came from an `EVOLUTION.md` entry, mark it `applied` with the version.

Report the diff summary and the validation results. Committing follows the usual blast-radius rule: local commit with a Conventional Commit message (`docs(skill): …`, `feat(skill): …`) only if the user's workflow commits; never push.

## EVOLUTION.md

`<skill-dir>/EVOLUTION.md` belongs to the skill, not to any project. It holds candidate improvements to the methodology.

| File | About | Example |
| --- | --- | --- |
| `.specs/LESSONS.md` | This project's code | "Compare expiry timestamps in UTC" |
| `<skill-dir>/EVOLUTION.md` | The skill's workflow | "MEDIUM features rarely need a separate Discuss step" |

Project lessons never go to `EVOLUTION.md`, and opinions about the method never go to `lessons.json`.

Create it only when there is a real candidate to record and the user agreed to record it. Never create it empty or as a placeholder. If `<skill-dir>` is not writable (installed read-only or shared), show the entry in chat instead.

Entry format:

```markdown
## EV-001 · Discuss is rarely useful at MEDIUM
- **Status**: candidate | proposed | applied (v1.3.0) | rejected
- **Seen**: 2026-09-14 · project: profiza · features: provider-reviews, search-filters
- **Problem**: Discuss ran for two MEDIUM features and resolved nothing the spec had not.
- **Evidence**: provider-reviews/context.md, search-filters/context.md — every decision duplicated an AC
- **Idea**: Skip Discuss at MEDIUM unless the spec has open assumptions.
```

Append new evidence to an existing entry instead of duplicating it. A candidate becomes a proposal when it meets the evidence threshold; evolve presents it through the safety loop like any other. Rejected entries stay, with the reason, so the same idea is not re-proposed without new evidence.
