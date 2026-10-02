# Plan

**Goal:** decide HOW to build the approved spec and break it into WORK: behavioral tasks with their tests, dependencies, parallel waves and gates. `plan.md` replaces the separate design and task documents. The design explains the tasks, and the tasks implement the design.

Template: [assets/templates/plan.md](../assets/templates/plan.md).

## Depth by risk

| Section | MEDIUM | HIGH | CRITICAL |
| --- | --- | --- | --- |
| Approach | required (one paragraph) | required | required |
| Design (components, data, errors) | only if non-obvious | required | required |
| Alternatives considered | — | required (2–3, with a recommendation) | required |
| Failure modes | — | in Risks | required section |
| Risks & Mitigations | when any exist | required | required |
| Rollback | when any step is irreversible | when any step is irreversible | required |
| Test Strategy | one line | required | required |
| Verification Commands | required | required | required |
| Tasks + Execution Waves | required | required | required |
| Deferred | when any exist | when any exist | when any exist |

LOW has no `plan.md`; its plan is an inline list of steps in chat.

## Process

### 1. Load context

Read `spec.md`, and `context.md` if it exists. Re-read `STATE.md` → Decisions; conform to every active `AD-NNN` or supersede it explicitly (see [memory.md](memory.md)). Load confirmed lessons for the area (MEDIUM+).

### 2. Design

- **Approach:** the shape of the solution in plain words, and what it reuses.
- **Reuse first.** Name the existing components, utilities and patterns being extended, with paths. A new abstraction needs a reason the existing ones do not fit.
- **Components and interfaces** (HIGH+): purpose, location, signatures, dependencies. Interfaces before internals.
- **Data model** (when data changes): fields, constraints, indexes, migration shape (additive → backfill → switch → cleanup).
- **Error handling:** one row per failure the spec names, with what the user or caller sees.
- **Alternatives** (HIGH+): 2–3 approaches that deliver the same scope, trade-offs, and a recommendation stated first. At HIGH and CRITICAL, confirm the chosen approach with the user before detailing tasks if it is not obvious.
- **Failure modes** (CRITICAL): for each external call, write and concurrent path, what happens on timeout, duplicate, partial success and crash mid-way, and which invariant or AC covers it.
- **Rollback** (any irreversible step): how to undo or compensate, how it was or will be rehearsed, and the point of no return.
- **Decisions:** feature-local decisions go in the Design section. Project-level ones (hard to reverse, surprising without context, a real trade-off) are also appended to `STATE.md` as `AD-NNN`.

Use mermaid diagrams when they save words. Skip them when they do not.

### 3. Define tasks

**A task is one cohesive behavioral change**: after it lands, something observable is true that was not true before, and the task's own tests prove it. A task is not a file, a function or a component.

| File-shaped (avoid) | Behavior-shaped (prefer) |
| --- | --- |
| T1 Create `CouponRepository` · T2 Create `CouponService` · T3 Add route · T4 Write tests | T1 Apply a valid coupon at checkout and show the discounted total (CPN-01, CPN-02) |
| T5 Add `expiresAt` column · T6 Add validation | T2 Reject expired and exhausted coupons with specific errors (CPN-03, CPN-04) |

A behavioral task usually cuts vertically through layers (schema → domain → API → UI) as far as needed to make its behavior observable.

**Sizing heuristics:**

- One sentence describes the change without "and" between unrelated behaviors.
- Reviewable in one sitting. A diff well beyond ~400 changed lines, excluding generated code, should usually split by behavior.
- Covers 1–4 related ACs. Zero ACs is allowed only for **enablers**: a preparatory refactor or migration whose `Covers` is `enabler for T<n>` and whose tests are `CHARACTERIZATION` or `REGRESSION`.
- Has exactly one done-claim the gate can check.

**Every task carries its own tests.** There are no "write tests" tasks. Each test line names its origin (`SPEC`, `REGRESSION`, `CONTRACT`, `INVARIANT`, `CHARACTERIZATION`), the AC or invariant it anchors to when applicable, its layer, and the precise outcome it asserts. Depth follows the task's risk ([testing.md](testing.md)).

**Task fields** (exact labels; the validator reads them):

```markdown
### T2 — Reject expired and exhausted coupons
- **Covers**: CPN-03, CPN-04
- **Depends on**: T1
- **Risk**: inherit
- **Touches**: `src/coupons/validate.ts`, `src/checkout/apply-coupon.ts`, `src/checkout/apply-coupon.test.ts`
- **Change**: validation runs before discount calculation; expired → `COUPON_EXPIRED`, exhausted → `COUPON_EXHAUSTED`, both HTTP 422.
- **Tests**:
  - SPEC CPN-03 · unit — coupon with `expiresAt` in the past → `COUPON_EXPIRED`
  - SPEC CPN-04 · integration — 101st redemption of a 100-use coupon → 422 `COUPON_EXHAUSTED`
  - REGRESSION · unit — valid coupons still apply (existing suite `apply-coupon.test.ts`)
- **Done when**: tests above pass; quick gate green
- **Gate**: quick
- **Status**: [ ] pending
```

- `Risk`: `inherit`, or a level plus reason (`HIGH — backfill on orders table`).
- `Touches`: the expected surface. It is what parallel safety is judged on, not a fence: if the real diff must go elsewhere, update the line and re-check the wave.
- `Status`: `[ ] pending`, `[~] in progress`, `[x] done (<sha>)`, or `[-] dropped (A-NN)`.

### 4. Order work into waves

Build the dependency graph from `Depends on`, then group tasks into **waves**. Every task in a wave depends only on earlier waves.

```markdown
## Execution Waves
- **Wave 1**: T1
- **Wave 2**: T2 ∥ T3
- **Wave 3**: T4
```

Tasks in the same wave **may run in parallel** only if all of these hold:

- Their `Touches` sets are disjoint, including shared config, lockfiles, generated code, migration sequences and snapshot files.
- They do not both change the same schema, contract or global state.
- Each can pass its gate without the other.

If any condition fails, list them in sequence (`T2 → T3`) inside the wave, or move one to the next wave. `validate_plan.py` warns on overlapping `Touches` within a wave. Parallel execution mechanics: [sub-agents.md](sub-agents.md).

### 5. Verification commands

Define each gate once, from the project's real commands found during Discover. Tasks only name the level.

| Gate | Typical content | When |
| --- | --- | --- |
| `quick` | Tests affected by the task (path- or tag-filtered) + typecheck of touched packages | After each task |
| `full` | Whole test suite + lint + typecheck + build | After each wave, and once before Verify |
| extra (optional) | e2e, contract or mutation tooling | Named where a task or Verify needs it |

**Consolidate.** If lint, typecheck and tests are one script in the project (`npm run check`, `make ci`), use it. Do not list three commands that CI already runs as one. Do not rerun the full gate during Verify if `HEAD` has not changed since the last green full gate; cite the SHA instead.

If the project has no tests at all, ask once which test types and runner to adopt, or propose one that matches the stack. This is the one tooling question that is the user's call, because it adds a dependency.

### 6. Validate and present

```bash
python3 <skill-dir>/scripts/validate_plan.py <feature>
```

It checks that every AC and invariant is covered by a task, that each test has a valid origin, that SPEC and INVARIANT tests anchor to real IDs, that dependencies exist and are acyclic, that waves respect dependencies, and that sections required by risk are present. Fix every ERROR before presenting.

Present:

- **MEDIUM:** spec and plan together, one approval.
- **HIGH / CRITICAL:** the plan, after the spec was approved. Lead with the approach, the task list (titles + ACs) and the waves. Mention the top risks and, at CRITICAL, the rollback and the irreversible steps that will need their own go-ahead.

Approval of the plan authorizes local implementation and local commits. Nothing remote ([SKILL.md](../SKILL.md), contract rule 5).

## Anti-patterns

| Anti-pattern | Why it fails |
| --- | --- |
| A task per file or layer | Nothing observable is true until the last one; tests become a separate afterthought |
| A "write tests" task at the end | Tests written after the fact mirror the implementation |
| A task with no test and no reason | Its done-claim is unverifiable |
| Copying AC text into tasks | Two homes for one fact; reference the ID instead |
| Asking the user which tools to use | The agent owns tool choice |
| Waves with overlapping `Touches` | Parallel workers conflict and the merge silently breaks one of them |
