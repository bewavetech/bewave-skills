# Verify: HIGH and CRITICAL

Extends [verify.md](verify.md). Run all its steps, plus what follows.

## HIGH: independent verifier

Dispatch a fresh sub-agent with **only** `spec.md`, the diff range, the test files in scope, the plan's Verification Commands and [verify.md](verify.md) as its checklist ([sub-agents.md](sub-agents.md#verifier)). It gets neither the author's reasoning nor the chat history. It runs read-only on the real tree; mutations (3–5) happen in a scratch.

Without sub-agent support, do the same pass yourself after an explicit context reset (spec → diff → tests only) and record `Verifier: author, context-reset (no independent agent available)`. `validate_state.py` accepts this with a warning at HIGH and rejects it at CRITICAL unless the human sign-off explicitly accepts it.

## CRITICAL: on top of HIGH

- **Invariants.** Every `INV-NN` has an INVARIANT test cited with `file:line`, and the verifier attempted at least one mutation that breaks each. Use mutation tooling, or ≥5 manual mutations; zero survivors.
- **Adversarial review.** A second fresh pass (separate sub-agent when available) that tries to break the change: authorization bypass, injection, replay and duplicate delivery, race windows, partial failure, rollback viability, data exposure in logs. Findings go into Gaps.
- **Rollback check.** The plan's rollback is still valid for what was built.
- **Human sign-off.** The verdict is not final until a person records approval in `validation.md`. Present the summary and ask; until then the Sign-off line reads `pending`.

## UAT

Walk the user through one observable check at a time:

```
Check 3 — Expired coupon
Do: apply SUMMER23 (expired 2023-09-01) to any cart
Expect: inline error "This coupon has expired"; total unchanged
→ What do you see?
```

"Yes / works / next" is a pass, "skip" is a skip, anything else is an issue recorded verbatim. Infer severity yourself: crash or error → blocker; wrong or missing → major; slow or odd → minor; visual → cosmetic; unclear → major. When a verifier sub-agent is used, UAT is coordinated through the orchestrator, since only the orchestrator talks to the user.
