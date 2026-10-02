# Testing

**Goal:** tests that prove the spec and catch regressions. Not tests that restate the code. Tests are part of every task, their origin says why each one exists, and their depth follows risk.

## Test origins

Every planned test carries exactly one origin. The origin determines what the test may assert.

| Origin | Why it exists | Anchors to | What it asserts |
| --- | --- | --- | --- |
| `SPEC` | Proves an acceptance criterion | An AC ID (`CPN-03`) | The precise outcome the spec defines |
| `REGRESSION` | Protects existing behavior the change could break, or reproduces a bug before fixing it | The behavior or bug (issue, AC of an older feature) | The previously correct behavior |
| `CONTRACT` | Locks an agreement at a boundary: API schema, event payload, DB schema, third-party request/response | The contract (endpoint, event, schema) | Shape, required fields, status codes, compatibility |
| `INVARIANT` | Proves a property holds for all inputs and interleavings | An invariant ID (`INV-01`) | The property, ideally via property-based or randomized testing |
| `CHARACTERIZATION` | Pins current behavior of untested code before changing it | The legacy unit | What the code does today, including quirks |

Rules:

- **SPEC tests derive from the spec, never from the code.** Write or plan them from the AC before reading the implementation, and assert the spec-defined value. If the spec gives no precise outcome, that is a **spec-precision gap**: raise a clarification amendment instead of writing a vague assertion.
- **CHARACTERIZATION is the only origin allowed to mirror the implementation.** Label it clearly. If a later task intentionally changes that behavior, update the characterization test in the same commit and cite the AC or amendment that justifies the change.
- **Bug fixes start with a failing REGRESSION test** that reproduces the bug, then the fix makes it pass.
- **No unanchored tests.** Every test maps to an AC, an invariant, a contract, a protected behavior or a characterized unit. Speculative "what if" tests and tests of framework or library behavior are scope creep.

## Depth by risk

Task risk (or feature risk when the task inherits) sets the depth.

| Level | Required |
| --- | --- |
| LOW | Existing suite stays green. Add one REGRESSION or CHARACTERIZATION test where observable behavior changes. Pure copy or style changes need no new test. |
| MEDIUM | One SPEC test per AC at the cheapest layer that observes the behavior. REGRESSION for touched behavior that already had users. |
| HIGH | MEDIUM, plus a test for every failure and edge AC, CONTRACT tests at every boundary the change creates or modifies, and integration-level coverage for persistence and external calls (with fakes or sandboxes, not mocks of your own code). |
| CRITICAL | HIGH, plus an INVARIANT test per invariant (property-based where the stack supports it), failure-injection tests for each failure mode in the plan (timeout, duplicate delivery, crash mid-write), and concurrency tests where races are possible. |

**Layer choice.** Test each behavior at the lowest layer where it is observable, and once. A rule computed in the domain gets a unit test. The route that exposes it gets a test for wiring and status codes, not a second copy of every domain case. The existing suite's depth is a floor; the spec is the ceiling.

## Adequacy review (per task, before commit)

Scaled to risk. LOW does the first item only.

1. **Covered.** Every AC in the task's `Covers` maps to at least one assertion. You must be able to cite `file:line` plus the assertion expression. No citation means not covered.
2. **Precise.** Each SPEC assertion targets the spec-defined value (the exact status, field value, message or state), not merely that something was returned.
3. **Non-shallow.** Reject assertion-free tests, tautologies, "did not throw" as the only check (unless not throwing is the spec), and mock-call counts where the spec demands a resulting state. For every field the spec names in a returned object, event or record, assert that field's value. The litmus test: would this assertion still pass under a plausible wrong implementation? If yes, strengthen it.
4. **Necessary.** Every new test maps back to an anchor. Remove the ones that do not.
5. **Conventions.** Location, naming and framework follow the project's guidelines or existing tests.

Record the result as one line in the commit body or the task status when it is noteworthy. HIGH and CRITICAL put the full evidence table in `validation.md`. Do not keep a second copy per task.

## Test integrity (never violated)

- Never weaken an assertion to make it pass.
- Never delete, skip, `.only`, `xit` or otherwise disable a test to get green.
- A test that is genuinely wrong per the spec is fixed openly: say so, cite the AC, and change it in its own visible step. If the spec itself was wrong, that is an amendment.
- The test count per affected suite never silently drops. A drop needs a stated reason.

## Discrimination (mutation) testing

Coverage shows that code ran. Discrimination shows the tests would notice if it were wrong. Inject a behavior-level fault and confirm a test fails ("the mutant is killed").

| Level | Depth | Who |
| --- | --- | --- |
| LOW | None | — |
| MEDIUM | 1–3 targeted mutations on the new decision logic, when the task adds non-trivial branching | Author, during the fresh-eyes pass |
| HIGH | 3–5 mutations across the riskiest new code: conditions, returned values, required side effects | Independent verifier |
| CRITICAL | Language mutation tooling scoped to the diff (Stryker, mutmut, cargo-mutants, PIT, …) when available; otherwise at least 5 manual mutations covering every branch of invariant-bearing code. Zero survivors. | Independent verifier |

Good mutations: flip a condition (`>` → `>=`), return a wrong but plausible value, drop a required side effect (the event emit, the audit write), skip an idempotency check, swap the order of two writes.

### Isolation is mandatory

Mutations never touch the real working tree.

1. Record `git status --porcelain` of the real tree as a baseline.
2. Create a scratch: `git worktree add <tmp> HEAD` (preferred) or copy the affected files to a temp directory.
3. Mutate and run the relevant tests **in the scratch**.
4. Remove the scratch (`git worktree remove --force <tmp>`).
5. Confirm the real tree's porcelain matches the baseline. If not, stop and restore it; the run is invalid.

**Never use `git stash` for this.** On a clean tree it records nothing, and popping it does not undo a mutation applied afterwards.

A surviving mutant means a missing or weak assertion. It becomes a fix task (strengthen the test) and, after verification, a lesson.
