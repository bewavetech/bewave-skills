# <Feature name> — Plan

**Spec**: [spec.md](spec.md)
**Risk**: <level> (from spec)
**Status**: Draft | Approved | In progress | Done

<!-- HOW + WORK. Delete sections your risk level does not require (see references/plan.md). -->

## Approach

<One paragraph: the shape of the solution and what it reuses. Cite AD-NNN decisions it conforms to.>

## Design

### Reuse

| Existing | Location | Use |
| --- | --- | --- |
| <component or pattern> | `<path>` | <extend / call / mirror> |

### Components and interfaces

- **<Component>** (`<path>`): <purpose>. `<signature>`. Depends on <x>.

### Data

<Fields, constraints, indexes, migration shape. Delete if no data changes.>

### Error handling

| Failure (AC) | Handling | Caller / user sees |
| --- | --- | --- |
| <AREA>-04 | <how> | <what> |

### Decisions

| Decision | Choice | Rationale |
| --- | --- | --- |
| <non-obvious decision> | <choice> | <why> |

## Alternatives Considered

<!-- HIGH/CRITICAL. Recommendation first. -->

| Option | Trade-offs | Verdict |
| --- | --- | --- |
| <recommended> | <+/-> | Chosen |
| <alternative> | <+/-> | Rejected: <why> |

## Failure Modes

<!-- CRITICAL. One row per external call, write path and concurrent path. -->

| Path | Timeout | Duplicate | Partial success | Crash mid-way | Covered by |
| --- | --- | --- | --- | --- | --- |
| <path> | <behavior> | <behavior> | <behavior> | <behavior> | <AC / INV IDs> |

## Risks & Mitigations

| Risk | Location | Impact | Mitigation |
| --- | --- | --- | --- |
| <fragile code, unverified fact, perf hazard> | `<file:line>` | <impact> | <mitigation or task> |

## Rollback

<!-- Required at CRITICAL or when any step is irreversible. -->

- **Point of no return**: <step>
- **Undo / compensate**: <how>
- **Rehearsal**: <how and where it was or will be tested>

## Test Strategy

| Layer | Test type | Origins used | Location pattern |
| --- | --- | --- | --- |
| <domain> | unit | SPEC, INVARIANT | `<glob>` |
| <API> | integration | SPEC, CONTRACT | `<glob>` |

## Verification Commands

| Gate | Command | When |
| --- | --- | --- |
| quick | `<affected tests + typecheck>` | after each task |
| full | `<all tests + lint + typecheck + build>` | after each wave, before verify |

## Tasks

### T1 — <observable behavior that becomes true>

- **Covers**: <AREA>-01, <AREA>-02
- **Depends on**: none
- **Risk**: inherit
- **Touches**: `<path>`, `<path>`
- **Change**: <what changes, in behavior terms>
- **Tests**:
  - SPEC <AREA>-01 · unit — <input> → <precise expected outcome>
  - SPEC <AREA>-02 · integration — <input> → <precise expected outcome>
  - REGRESSION · unit — <existing behavior that must not change>
- **Done when**: tests above pass; quick gate green
- **Gate**: quick
- **Status**: [ ] pending

### T2 — <observable behavior>

- **Covers**: <AREA>-03, <AREA>-04
- **Depends on**: T1
- **Risk**: inherit
- **Touches**: `<path>`
- **Change**: <what changes>
- **Tests**:
  - SPEC <AREA>-03 · unit — <input> → <outcome>
  - SPEC <AREA>-04 · unit — <failure input> → <precise error>
- **Done when**: tests above pass; quick gate green
- **Gate**: quick
- **Status**: [ ] pending

## Execution Waves

- **Wave 1**: T1
- **Wave 2**: T2

## Deferred

| Item | Reason | Where it goes |
| --- | --- | --- |
| <idea or bug found> | <why not now> | <new feature / issue / never> |
