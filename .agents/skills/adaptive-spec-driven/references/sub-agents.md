# Sub-Agents and Parallel Execution

Sub-agents serve two purposes: **throughput** (parallel workers on independent tasks, parallel explorers during Discover/Research) and **independence** (a verifier that does not share the author's mental model). Use them when the harness provides them and they pay off. Everything in this skill still works without them, with sequential execution and context-reset verification.

**Consent.** Some harnesses or users require approval before spawning agents. If so, ask once per feature with a concrete proposal ("Wave 2 has 3 independent tasks; I'll run them as 3 parallel workers in separate worktrees, then integrate. OK?"). Otherwise decide yourself and mention it in one line.

## Roles

| Role | When | Gets | Returns | May modify |
| --- | --- | --- | --- | --- |
| **Explorer** | Discover or Research on a large surface: map callers in several packages, read several integrations | A precise question and the search scope | Conclusions with `file:line`, not file dumps | Nothing |
| **Worker** | Executing tasks of one wave, or a sequential batch | Its task definitions, the relevant spec ACs, the plan's Design excerpt, Verification Commands, [execute.md](execute.md) and [testing.md](testing.md) | Compact summary (below) | Only its `Touches`, in its own worktree or branch |
| **Verifier** | HIGH and CRITICAL after the last task | `spec.md`, diff range, test files in scope, Verification Commands, [verify.md](verify.md) | Verdict + ranked gaps; writes `validation.md` | Only `validation.md`; mutations in a scratch |
| **Adversarial reviewer** | CRITICAL, alongside the verifier | `spec.md` (invariants, failure behavior), diff, plan's Failure modes and Rollback | Findings ranked by severity | Nothing |

Workers never spawn further agents. The orchestrator (the main agent) owns `plan.md` status, integration, the full gate and all communication with the user.

## Parallel waves

Only tasks in the same wave that meet the parallel-safety conditions in [plan.md](plan.md#4-order-work-into-waves) run concurrently.

1. **Prepare.** For each parallel task, create an isolated worktree from the current integrated `HEAD`: `git worktree add ../<repo>-T3 -b sdd/<feature>/T3`.
2. **Dispatch.** One worker per task (or per small group of tightly related tasks). Each runs the full task cycle in its worktree: tests, implementation, quick gate, commit(s).
3. **Collect.** Each worker returns:

   ```
   T3 — done | blocked
   Commits: 9a1f0c2 feat(coupons): reject exhausted coupons
   Gate: quick — 38 passed, 0 failed
   Touches (actual): src/coupons/validate.ts, src/coupons/validate.test.ts
   Amendments raised: none | A-04 (proposed, see below)
   Notes: <one line, only if it matters>
   ```

   No raw logs. If the actual touches differ from the planned ones, say so.
4. **Integrate.** The orchestrator merges or cherry-picks the worker branches in task-ID order, resolves trivial conflicts, and marks each task `[x] done (<sha>)` in `plan.md`. A non-trivial conflict means the parallel-safety judgment was wrong: stop, re-run the conflicting task sequentially on the integrated tree, and record a lesson if it recurs.
5. **Gate.** Run the `full` gate on the integrated result before the next wave.
6. **Clean up.** Remove worktrees and temporary branches.

**Failures.** A blocked worker does not stop its siblings, but the next wave does not start until every task in the current wave is done or explicitly re-planned. An amendment raised by a worker is decided by the orchestrator before integrating that worker's commits.

**Without worktrees or sub-agents**, execute the wave's tasks sequentially. Correctness never depends on parallelism.

## Sequential batching for long plans

For plans with many sequential tasks (more than ~8), a worker can take a batch of consecutive tasks to keep the orchestrator's context lean. Cut batches only at wave boundaries. Each batch reports the same compact summary per task.

## Verifier

**Author ≠ verifier.** The value of the verifier comes from not inheriting the author's assumptions. Its payload is deliberately narrow: spec, diff, tests, commands, checklist. It does not receive the plan's reasoning, the chat history or the author's adequacy notes.

The verifier:

1. Follows [verify.md](verify.md) steps 1–6 (and 7 when UAT is due, coordinated through the orchestrator, since only the orchestrator talks to the user).
2. Runs mutations only in an isolated scratch and confirms the real tree's porcelain is unchanged afterwards.
3. Writes `validation.md` and returns the compact verdict with ranked gaps.
4. Never fixes code or tests. Gaps go back to the orchestrator as fix tasks.

The fix → re-verify loop is capped at three rounds; each round dispatches a fresh verifier.

## Model tier (only if the harness lets you choose per agent)

Spend reasoning where ambiguity and consequence are high.

| Work | Tier |
| --- | --- |
| Plan design at HIGH/CRITICAL, workers on core-domain or ambiguous tasks | High-reasoning |
| Verifier, adversarial reviewer | Mid-to-high; never the cheapest. A weak verifier defeats the point |
| Workers on mechanical tasks (wiring, config, CRUD on a settled pattern), explorers | Faster / cheaper |

When unsure, size up. This is advisory; no gate depends on it.
