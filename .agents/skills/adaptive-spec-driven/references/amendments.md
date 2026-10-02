# Spec Amendments

**Goal:** when implementation reveals that the approved spec is wrong, incomplete, infeasible or riskier than assessed, change the spec **explicitly**, with a trail and the right approval, instead of letting code and spec drift apart.

An amendment is the only way an approved spec changes. Code comments like `// deviates from spec` are not a substitute: they hide the decision in the code, and the next reader of the spec never sees it.

## When to raise one

Stop the current task and raise an amendment when you discover that:

- An AC cannot be implemented as written (a technical constraint, an API limit, a conflicting AC).
- An AC is ambiguous or lacks a precise outcome (a **spec-precision gap**). Often found while writing its test.
- The real behavior needs a case the spec did not foresee (a new failure mode, an edge case users will hit).
- The work is bigger than or different from the scope.
- A risk factor was missed or underrated (a hidden external call, a shared table, a race).
- A verifier or UAT finding shows the spec itself was wrong, not the code.

Do not raise an amendment for an implementation detail the spec never fixed (internal naming, file layout, algorithm choice). That belongs in the plan's Design.

## Types and approval

| Type | Meaning | Approval needed before continuing |
| --- | --- | --- |
| `clarification` | Same intent, sharper wording or a precise outcome added; no behavior a user would notice changes | LOW/MEDIUM: none, inform in the next summary. HIGH/CRITICAL: inform now; continue unless the user objects |
| `behavior-change` | Observable behavior differs from what was approved | LOW/MEDIUM: inform and continue if it is the only sensible option; otherwise ask. HIGH/CRITICAL: explicit approval |
| `scope-change` | Adds or removes a capability | Always explicit approval. Default: defer to a new feature |
| `risk-change` | A factor rating changes | Re-run `risk.py`. If the level rises: inform, apply the new profile, backfill. If it rises to CRITICAL: explicit approval of the new plan |

When unsure between two types, treat it as the stricter one.

## Procedure

1. **Pause the task.** Keep the work in progress uncommitted or on a WIP commit that is clearly marked as such. Do not mark the task done.
2. **Write the amendment** in `spec.md` → `## Amendments`:

   ```markdown
   ### A-02 — Exhausted coupons return 409, not 422
   - **Type**: behavior-change
   - **Discovered in**: T2
   - **Change**: CPN-04 now expects HTTP 409 `COUPON_EXHAUSTED`.
   - **Reason**: the public API returns 409 for every quota conflict (`docs/api-errors.md:31`); 422 would break client error handling.
   - **Affected**: CPN-04 (modified)
   - **Risk impact**: none
   - **Status**: proposed
   ```

3. **Update the ACs in place.** Edit the affected AC text and tag it, as in `**CPN-04** *(A-02)* — …`. New ACs get new IDs; removed ACs are struck through with the tag, as in `~~**CPN-05** — …~~ *(removed by A-03)*`, never deleted. The spec always reads as the current truth, and the amendment explains how it got there.
4. **Get the approval** the table requires. Then set `Status: approved` or `rejected`. If rejected, revert the AC edits and find another way to meet the original AC, or escalate.
5. **Propagate to the plan.** Adjust affected tasks: `Covers`, tests, `Touches`, waves. Add tasks for new ACs and mark dropped ones `[-] dropped (A-NN)`. Re-run `validate_plan.py`.
6. **Re-classify** if `Risk impact` is not `none`. Apply the higher profile to remaining work and backfill completed tasks that now lack required tests or verification.
7. **Resume the task.** Its tests now follow the amended AC.

Already-completed tasks affected by the amendment get a follow-up fix task rather than an edit to history.

## What the verifier checks

Every approved amendment must show up in three places: the amended AC text, the code, and a test whose assertion matches the amended outcome. A `proposed` amendment at verification time blocks PASS (`validate_state.py` enforces this).

## Lessons

An approved `behavior-change` or `risk-change` amendment is a lesson signal (`spec_amendment`). The question to distill: what could Discover or Specify have checked to catch this earlier? Record it after verification ([lessons.md](lessons.md)).
