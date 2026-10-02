# <Feature name> — Spec

**Status**: Draft | Approved | Amended
**Date**: <YYYY-MM-DD>

<!-- WHY + WHAT only. HOW lives in plan.md. Delete sections your risk level does not require (see references/specify.md). -->

## Problem

<2–4 sentences: who is affected, what hurts today, why now. For a bug: observed vs. expected behavior.>

## Scope

### In scope

- <capability>

### Out of scope

| Item | Reason |
| --- | --- |
| <excluded thing> | <why> |

## Risk Assessment

| Factor | Rating | Evidence |
| --- | --- | --- |
| ambiguity | none | <one line> |
| criticality | none | <one line> |
| blast_radius | none | <e.g. 14 call sites of applyDiscount()> |
| novelty | none | <one line> |
| irreversibility | none | <one line> |
| integrations | none | <one line> |
| state | none | <one line> |
| auth | none | <one line> |
| concurrency | none | <one line> |
| migrations | none | <one line> |
| security | none | <one line> |
| data_integrity | none | <one line> |

**Declared level**: <LOW | MEDIUM | HIGH | CRITICAL>
**Override**: <only when declared < computed: why the triggering factor does not carry its usual weight here>

## Acceptance Criteria

<!-- One behavior per AC, a precise outcome, a stable ID. Use EARS where it removes ambiguity (failures, states, concurrency); plain sentences, Given/When/Then or example tables where they are clearer. -->

### P1 — <story or slice title>

- **<AREA>-01** — WHEN <trigger> THEN the system SHALL <precise outcome>
- **<AREA>-02** — <plain declarative rule with a concrete value>

### P2 — <story or slice title>

- **<AREA>-03** — Given <setup>, When <action>, Then <precise outcome>

## Failure & Edge Behavior

- **<AREA>-04** — IF <failure or invalid input> THEN the system SHALL <precise handling>
- **<AREA>-05** — WHILE <state> the system SHALL <behavior>

<!-- HIGH/CRITICAL: implicit-requirement dimensions not covered above, each with a reason. -->
Other dimensions: <dimension> N/A because <reason>; <dimension> N/A because <reason>

## Invariants

<!-- Required at CRITICAL. Properties that hold for every input and interleaving. -->

- **INV-01** — <property, e.g. a coupon is redeemed at most max_uses times across all concurrent checkouts>

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed |
| --- | --- | --- | --- |
| <ambiguity> | <what we will do> | <why> | <yes / no> |

**Open questions**: none

## Amendments

<!-- Added only after approval, when implementation reveals the spec must change. See references/amendments.md. -->

### A-01 — <short title>

- **Type**: clarification | behavior-change | scope-change | risk-change
- **Discovered in**: <T-id or verification>
- **Change**: <what the spec now says>
- **Reason**: <evidence>
- **Affected**: <AC IDs (modified | added | removed)>
- **Risk impact**: none | <factor change and new level>
- **Status**: proposed | approved | rejected
