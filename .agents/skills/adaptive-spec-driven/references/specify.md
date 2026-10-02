# Specify

**Goal:** capture WHY the change exists and WHAT must be true when it is done, as acceptance criteria a test can prove. The spec says nothing about HOW; that belongs to `plan.md`.

Template: [assets/templates/spec.md](../assets/templates/spec.md).

## Depth by risk

| Section | LOW | MEDIUM | HIGH | CRITICAL |
| --- | --- | --- | --- | --- |
| Problem | inline | required | required | required |
| Scope (in / out) | inline | required | required | required |
| Risk Assessment | inline line | required | required | required |
| Acceptance Criteria with IDs | 1–3 inline | required | required | required |
| Failure & Edge Behavior | — | when present | required | required |
| Assumptions & Open Questions | — | when any exist | required, closed | required, closed |
| Invariants | — | — | when any exist | required |
| Amendments | — | when raised | when raised | when raised |

`validate_spec.py` enforces the required sections for the declared level.

## Process

### 1. Clarify

Be a thinking partner, not an interviewer. Let the user describe the change, then make the abstract concrete: "walk me through it", "what does the user see when it fails?". Challenge vague words. "Fast" means a number. "Users" means which role.

Resolve facts from the code and docs yourself. Ask only for decisions the user owns: scope, priorities, product behavior, trade-offs. Ask at most two independent questions per turn, and one at a time when answers depend on each other.

If several user-visible behaviors could reasonably go different ways, or an implicit-requirement dimension below is present and undecided, open [discuss.md](discuss.md).

### 2. Sweep implicit requirements

These are the requirements people forget. Sweep them in proportion to risk.

| Dimension | Ask |
| --- | --- |
| Input validation and bounds | Limits, formats, empty, huge, malformed |
| Failure and partial failure | Timeouts, partial writes, rollback, user-visible error |
| Idempotency and retries | Duplicate submits, replayed events, dedup keys |
| Auth boundaries and rate limits | Who may do this, to which resources, how often |
| Concurrency and ordering | Two actors at once, out-of-order delivery |
| State transitions | Allowed transitions, guards, terminal states |
| Data lifecycle | Retention, expiry, deletion, archival |
| External-dependency failure | Fallbacks, circuit breaking, degraded mode |
| Observability | What must be logged, measured or alerted |

- **MEDIUM:** cover the dimensions obviously present; one line `Other dimensions: N/A for this scope`.
- **HIGH / CRITICAL:** every dimension resolves to an AC, an invariant, an assumption, or `N/A because <reason>`. The reason is mandatory; it stops invented requirements.

Bound the sweep to this feature. It clarifies existing behavior; it never adds capabilities.

### 3. Write acceptance criteria

Each AC has a stable ID (`<AREA>-NN`, such as `CPN-03`), states **one** observable behavior and names a **precise outcome**: a status code, a value, a message, a state, a bound.

**Choose the format that removes ambiguity.** EARS is a tool, not a uniform.

| Format | Use when | Example |
| --- | --- | --- |
| EARS event (`WHEN … THEN the system SHALL …`) | A trigger produces a response | WHEN a coupon past its expiry date is applied THEN the system SHALL reject it with `COUPON_EXPIRED` |
| EARS unwanted (`IF … THEN … SHALL …`) | Errors, invalid input, timeouts | IF the payment provider times out after 10 s THEN the system SHALL mark the order `PAYMENT_PENDING` |
| EARS state (`WHILE … SHALL …`) | Behavior that holds during a state | WHILE an import is running the system SHALL reject a second import for the same account |
| EARS optional (`WHERE … SHALL …`) | Flagged or optional capability | WHERE the `bulk_export` flag is enabled the system SHALL show the Export all button |
| Given / When / Then | Multi-step scenario with setup | Given a cart with 2 items, When one is removed, Then the total equals the remaining item's price |
| Example table | Several inputs map to outputs | `quantity → discount: 1→0%, 10→5%, 100→12%` |
| Plain declarative | Static facts and simple display rules | The receipt shows the coupon code and the discounted amount |

**Prefer EARS for failure handling, state-dependent behavior and concurrency at HIGH and CRITICAL.** Those are the places where informal prose hides two readings. For simple display or data rules, a plain sentence with a concrete value is clearer than forced EARS.

Rules for every format:

- One behavior per AC. "…and also…" means two ACs.
- Concrete values, never "quickly", "gracefully", "properly", "user-friendly", "as expected". `validate_spec.py` flags these words.
- If you cannot imagine the assertion, the AC is not ready.

Group ACs by user story or priority when it helps (`### P1 — Apply coupon at checkout`). P1 must be a demo-able vertical slice. Priorities are optional for LOW and MEDIUM.

### 4. Invariants (CRITICAL; HIGH when they exist)

Invariants are properties that hold for **every** input and interleaving, not one scenario: "an account balance never goes negative", "a payment is captured at most once per order", "sum of ledger entries per transaction equals zero". Give each an ID (`INV-01`). Each becomes an `INVARIANT` test, property-based where the stack supports it ([testing.md](testing.md)).

### 5. Closure gate

Before presenting the spec:

1. **Unambiguous and precise.** Every AC has one reading and a defined outcome. Otherwise split it, resolve it, or log an assumption.
2. **Open questions closed.** Every unresolved decision is either answered or recorded as an assumption with a chosen default and a rationale. HIGH and CRITICAL require the line `Open questions: none`.
3. **Declined gray areas logged.** Anything the user chose not to discuss becomes an assumption, never a silent gap.
4. **Risk recorded.** The factor table is filled with evidence; the declared level is at or above the computed level, or has an `Override:` line.

Then run:

```bash
python3 <skill-dir>/scripts/validate_spec.py <feature>
```

Fix every ERROR. Read every WARN and fix it or consciously accept it.

### 6. Approval

- **MEDIUM:** do not stop yet. Present the spec together with the plan for one approval.
- **HIGH / CRITICAL:** present the spec now. Lead with the risk line, the ACs and the assumptions the user should check. Planning starts after approval.

After approval, the spec changes only through [amendments.md](amendments.md).
