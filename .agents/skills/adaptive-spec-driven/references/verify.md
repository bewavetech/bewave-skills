# Verify

**Goal:** evidence, not belief, that the implementation does what the spec says, and that the tests would notice if it stopped. Verification always runs after the last task. Its depth is set by the feature's risk level, never by asking the user.

Template: [assets/templates/validation.md](../assets/templates/validation.md).

## Tiers

| Level | Who verifies | Output | Discrimination | UAT | Sign-off |
| --- | --- | --- | --- | --- | --- |
| LOW | Author self-check | Two lines in chat | — | — | — |
| MEDIUM | Author fresh-eyes pass | Evidence table in chat; `validation.md` optional | 1–3 mutations if new logic was not already sensor-checked during Execute | Optional, for complex UI | — |
| HIGH | Independent verifier (fresh context) | `validation.md` | 3–5 mutations | If user-facing | — |
| CRITICAL | Independent verifier + adversarial reviewer | `validation.md` incl. invariants | Tooling or ≥5, zero survivors | Required if user-facing | Human sign-off recorded |

### LOW: self-check

Full gate green (cite it), diff re-read against the stated ACs, nothing outside scope. Report: `Verified: gate green @ <sha>; AC 1–2 observed via <test or manual check>.`

### MEDIUM: fresh-eyes pass

Deliberately reset your frame. Re-read `spec.md` first, then the diff (`git diff <base>..HEAD`). Do **not** re-read the plan. Build the AC evidence table (below) from what the diff and tests actually contain. Run the mutations if due. Report the table and verdict in chat. Write `validation.md` only if the user wants a persisted record or the feature will be revisited.

### HIGH: independent verifier

Dispatch a fresh sub-agent with **only** `spec.md`, the diff range, the test files in scope, the plan's Verification Commands, and this file as its checklist ([sub-agents.md](sub-agents.md#verifier)). It does not get the author's reasoning or chat history. It runs read-only on the real tree; mutations happen in a scratch.

Without sub-agent support, perform the same pass yourself after an explicit context reset (spec → diff → tests only), and record `Verifier: author, context-reset (no independent agent available)`. `validate_state.py` accepts this with a warning at HIGH and rejects it at CRITICAL unless the human sign-off explicitly accepts it.

### CRITICAL: independent verifier + adversarial review + sign-off

On top of HIGH:

- **Invariants:** every `INV-NN` has an INVARIANT test cited with `file:line`, and the verifier attempted at least one mutation that breaks each invariant.
- **Adversarial review:** a second fresh pass (a separate sub-agent when available) that tries to break the change rather than confirm it. It covers authorization bypass, injection, replay and duplicate delivery, race windows, partial failure, rollback viability and data exposure in logs. Findings go into Gaps.
- **Rollback check:** the plan's rollback is still valid for what was actually built.
- **Human sign-off:** the verdict cannot be final until a person records approval in `validation.md`. Present the summary and ask for it; until then the Sign-off line reads `pending`.

## Verification steps (HIGH and CRITICAL; MEDIUM uses 2, 3, 5 and 10)

1. **Completion.** Every task in `plan.md` is `[x]` or `[-] dropped (A-NN)`; no amendment is `proposed`.
2. **Gate.** Run the `full` gate, or cite the green full gate at the current `HEAD` SHA if it already ran there. Record passed/failed/skipped. Any skip needs a reason. Compare test counts with the baseline from the start of Execute.
3. **AC evidence (evidence-or-zero).** For every AC and failure/edge AC in `spec.md`:

   | AC | Spec-defined outcome | Evidence (`file:line` — assertion) | Origin | Result |
   | --- | --- | --- | --- | --- |
   | CPN-03 | 422 `COUPON_EXPIRED` | `src/checkout/apply-coupon.test.ts:48` — `expect(res.body.code).toBe('COUPON_EXPIRED')` | SPEC | ✅ |

   - No `file:line` means not covered. Search the tests before declaring something missing, and show the search.
   - The assertion must target the spec's outcome. A vague assertion against a precise AC is a gap. A vague AC is a **spec-precision gap** (⚠️), which becomes a clarification amendment.
   - Payload rule: for each field the AC names, the assertion checks that field's value. A call happening is not the field being right.
4. **Amendments reconciled.** Each approved `A-NN` is reflected in the ACs, the code and a test.
5. **Discrimination.** Run the tier's mutations in an isolated scratch ([testing.md](testing.md#isolation-is-mandatory)). Record each one: location, mutation, killed or survived.
6. **Change review.** One pass over the whole diff: scope matches the spec's In scope; no drive-by changes; matches project patterns; no secrets, debug leftovers or disabled tests; tests are necessary and anchored.
7. **UAT** (when due): walk the user through one observable check at a time:

   ```
   Check 3 — Expired coupon
   Do: apply SUMMER23 (expired 2023-09-01) to any cart
   Expect: inline error "This coupon has expired"; total unchanged
   → What do you see?
   ```

   "Yes / works / next" is a pass, "skip" is a skip, anything else is an issue, recorded verbatim. Infer severity yourself: crash or error → blocker; wrong or missing → major; slow or odd → minor; visual → cosmetic; unclear → major.
8. **Report.** Write `validation.md` (HIGH+), then run:

   ```bash
   python3 <skill-dir>/scripts/validate_state.py <feature>
   ```

   A non-zero exit means the feature is not done.
9. **Distill lessons** from every signal ([lessons.md](lessons.md)).
10. **Architecture update.** On PASS, if `plan.md` records `ARCHITECTURE_UPDATE_REQUIRED`, update the affected sections of `ARCHITECTURE.md` to match what was actually built (not what was planned), and `PROJECT.md` if the stack or external systems changed. Section-scoped edits; commit them as `docs(architecture): …`. No marker, no edit.

## Verdict and the fix loop

**PASS** requires: gate green, every AC ✅ with evidence, no surviving mutant, no open blocker or major UAT issue, invariants proven (CRITICAL), and sign-off approved (CRITICAL).

On **FAIL**, the verifier returns a ranked gap list. The orchestrator turns gaps into fix tasks in `plan.md` (`### F1 — …`, same fields as tasks, `Covers` = the failing AC), executes them through the normal task cycle, and re-verifies. The verifier never fixes code itself. Cap the loop at **three** fix → re-verify rounds, then escalate to the user with what remains and why.

For any issue, diagnose the root cause before writing a fix task. Cap diagnosis at three attempts per issue before asking for human help.

## Chat summary

Lead with the verdict:

```
## Validation: coupon-expiry — PASS ✅  (risk HIGH, independent verifier)
ACs: 9/9 with evidence · Gate: full @ 4e1c2aa, 212 passed · Sensor: 4/4 killed
Report: .specs/features/coupon-expiry/validation.md
```

On FAIL, add the ranked gaps: `1. CPN-07 — no assertion on the retry count — apply-coupon.test.ts has no case for 2nd attempt`.

After PASS, tell the user what is ready locally (branch, commits) and what still needs their go-ahead (push, PR, deploy).
