# <Feature name> — Validation

**Verdict**: PASS | FAIL
**Risk**: <level> (from spec)
**Verifier**: independent sub-agent | author, context-reset (no independent agent available) | author fresh-eyes
**Diff range**: `<base>..<head>`
**Date**: <YYYY-MM-DD>

## Gate

- **Command**: full gate (plan.md → Verification Commands)
- **Result**: <N> passed, <N> failed, <N> skipped @ `<sha>`
- **Test count**: <before> → <after>
- **Skips**: none | <test — reason>

## Acceptance Criteria Evidence

| AC | Spec-defined outcome | Evidence (`file:line` — assertion) | Origin | Result |
| --- | --- | --- | --- | --- |
| <AREA>-01 | <precise outcome> | `<path>:<line>` — `<assertion expression>` | SPEC | ✅ |
| <AREA>-02 | <precise outcome> | — (searched `<pattern>` in `<dir>`, no match) | — | ❌ gap |
| <AREA>-03 | not precise in spec | — | — | ⚠️ spec-precision gap |

## Invariants

<!-- CRITICAL. -->

| Invariant | Evidence (`file:line`) | Breaking mutation attempted | Result |
| --- | --- | --- | --- |
| INV-01 | `<path>:<line>` — `<property assertion>` | <mutation> | ✅ held / killed |

## Discrimination

| # | Location | Mutation | Killed |
| --- | --- | --- | --- |
| 1 | `<path>:<line>` | `<a > b>` → `<a >= b>` | ✅ |
| 2 | `<path>:<line>` | removed `<side effect>` | ❌ survived → F1 |

**Result**: <N> injected · <N> killed · <N> survived
**Isolation**: scratch worktree; real-tree porcelain matched baseline

## Amendments Reconciled

| Amendment | AC text | Code | Test |
| --- | --- | --- | --- |
| A-01 | ✅ | ✅ | `<path>:<line>` |

## Adversarial Review

<!-- CRITICAL. Findings ranked by severity, or "No findings". -->

## UAT

| # | Check | Result | Notes |
| --- | --- | --- | --- |
| 1 | <check> | ✅ pass | — |

## Change Review

- Scope matches spec In scope: ✅
- No drive-by changes, debug leftovers, secrets or disabled tests: ✅
- Tests anchored and necessary: ✅

## Gaps & Fix Tasks

1. <gap> — <AC> — <evidence or "no evidence"> → F<n> in plan.md

## Sign-off

<!-- CRITICAL only. -->

**Human sign-off**: pending | approved by <name> on <YYYY-MM-DD>
