# Verify

**Goal:** evidence, not belief, that the implementation does what the spec says and that the tests would notice if it stopped. Verification always runs after the last task. Its depth is set by risk (table in [SKILL.md](../SKILL.md)), never by asking the user. HIGH and CRITICAL also read [verify-high.md](verify-high.md).

Template: [assets/templates/validation.md](../assets/templates/validation.md).

## LOW: self-check

Full gate green (cite it), diff re-read against the stated ACs, nothing outside scope. Report: `Verified: gate green @ <sha>; AC 1–2 observed via <test or manual check>.`

## MEDIUM: fresh-eyes pass

Reset your frame. Re-read `spec.md` first, then the diff (`git diff <base>..HEAD`). Do **not** re-read the plan (only its Verification Commands). Build the AC evidence table from what the diff and tests actually contain, run the due mutations (1–3, unless Execute already did), and report table and verdict in chat. Write `validation.md` only if the user wants a persisted record or the feature will be revisited. MEDIUM uses steps 2, 3, 5 and 10.

## Verification steps

1. **Completion.** Every task in `plan.md` is `[x]` or `[-] dropped (A-NN)`; no amendment is `proposed`.
2. **Gate.** Run the `full` gate, or cite the green full gate at the current `HEAD` SHA. Record passed/failed/skipped; every skip needs a reason. Compare test counts with the baseline from the start of Execute.
3. **AC evidence (evidence-or-zero).** For every AC, including failure and edge ACs (`validate_state.py` requires the literal ✅ plus a `file:line` in each row):

   | AC | Spec-defined outcome | Evidence (`file:line` — assertion) | Origin | Result |
   | --- | --- | --- | --- | --- |
   | CPN-03 | 422 `COUPON_EXPIRED` | `src/checkout/apply-coupon.test.ts:48` — `expect(res.body.code).toBe('COUPON_EXPIRED')` | SPEC | ✅ |

   - No `file:line` means not covered. Search the tests before declaring something missing, and show the search.
   - The assertion must target the spec's outcome and each field the AC names ([testing.md](testing.md#adequacy-review-per-task-before-commit)). A vague assertion against a precise AC is a gap. A vague AC is a **spec-precision gap** (⚠️) and becomes a clarification amendment.
4. **Amendments reconciled.** Each approved `A-NN` shows in the AC text, the code and a test.
5. **Discrimination.** Run the tier's mutations in an isolated scratch ([testing.md](testing.md#isolation-is-mandatory)). Record location, mutation, killed or survived.
6. **Change review.** One pass over the whole diff: scope matches In scope; no drive-by changes; matches project patterns; no secrets, debug leftovers or disabled tests; tests are necessary and anchored; no overengineering (single-use abstractions, speculative options, unrequested layers or dependencies).
7. **UAT** (when due): [verify-high.md](verify-high.md#uat).
8. **Report.** Write `validation.md` (HIGH+), then run `python3 <skill-dir>/scripts/validate_state.py <feature>`. Non-zero means the feature is not done.
9. **Distill lessons** from every signal ([lessons.md](lessons.md)).
10. **Architecture update.** On PASS, if `plan.md` records `ARCHITECTURE_UPDATE_REQUIRED`, update the affected sections of `ARCHITECTURE.md` to match what was built (not planned), and `PROJECT.md` if the stack or external systems changed. Section-scoped edits, committed as `docs(architecture): …`. No marker, no edit.

## Verdict and the fix loop

**PASS** requires: gate green, every AC ✅ with evidence, no surviving mutant, no open blocker or major UAT issue, and at CRITICAL proven invariants and approved sign-off.

On **FAIL**, the verifier returns a ranked gap list. The orchestrator turns gaps into fix tasks in `plan.md` (`### F1 — …`, same fields as tasks, `Covers` = the failing AC; its tests may be any origin, e.g. a stronger assertion that kills a surviving mutant), runs them through the normal task cycle and re-verifies. The verifier never fixes code. Diagnose the root cause before writing a fix task. Cap the loop at **three** fix → re-verify rounds (and diagnosis at three attempts per issue), then escalate to the user with what remains and why.

## Chat summary

Lead with the verdict:

```
## Validation: coupon-expiry — PASS ✅  (risk HIGH, independent verifier)
ACs: 9/9 with evidence · Gate: full @ 4e1c2aa, 212 passed · Sensor: 4/4 killed
Report: .specs/features/coupon-expiry/validation.md
```

On FAIL, add the ranked gaps: `1. CPN-07 — no assertion on the retry count`. After PASS, say what is ready locally (branch, commits) and what still needs the user's go-ahead (push, PR, deploy).
