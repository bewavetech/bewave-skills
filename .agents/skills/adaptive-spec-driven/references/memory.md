# Memory, Pause and Resume

**File:** `.specs/STATE.md`, two sections with different lifecycles. Template: [assets/templates/STATE.md](../assets/templates/STATE.md).

`STATE.md` holds only what lives nowhere else: project-wide decisions and in-flight session state. Task status lives in `plan.md`, requirements in `spec.md`, evidence in `validation.md`. Never copy those into `STATE.md`.

## `## Decisions`: append-only

Project-level decisions that future features must follow or explicitly supersede. Record one only when **all three** hold:

1. **Hard to reverse.** Changing course later has a real cost.
2. **Surprising without context.** A future reader would ask "why this way?".
3. **A real trade-off.** There were genuine alternatives.

Typical: architectural shape, integration patterns, technology choices with lock-in, ownership boundaries, deliberate deviations from the obvious path. Feature-local decisions stay in the plan's Design section.

```markdown
### AD-004
- **Decision**: Coupon redemption counts are enforced with a DB unique constraint on (coupon_id, order_id), not in application code.
- **Reason**: Two checkout workers can redeem concurrently; only the database serializes reliably.
- **Trade-off**: Constraint violations surface as DB errors that the service must map to COUPON_EXHAUSTED.
- **Scope**: Any feature that limits per-entity usage (coupons, referrals, trials).
- **Source**: coupon-expiry plan.md
- **Date**: 2026-10-02
- **Status**: active
```

To supersede, append a new entry and set the old one's status to `superseded by AD-NNN`. Never delete or renumber entries. Numbers are sequential and permanent.

Read Decisions at Discover and Plan. Conform, or supersede explicitly. Silently ignoring an active decision is not allowed.

## `## Handoff`: overwritten at each pause

A small snapshot (~300 tokens) of what git and `plan.md` cannot tell the next session.

```markdown
## Handoff
- **Feature**: coupon-expiry (`.specs/features/coupon-expiry/`)
- **Risk**: HIGH
- **Where**: Wave 2 / T3 in progress; T1, T2 done (see plan.md)
- **In progress**: `src/coupons/validate.ts:88`, exhaustion check written, test failing on timezone handling
- **Next step**: make `isExpired` compare in UTC, then run the quick gate
- **Open amendments**: A-02 proposed, waiting on user
- **Blockers**: none
- **Uncommitted**: `src/coupons/validate.ts`, `src/coupons/validate.test.ts`
- **Branch**: feat/coupon-expiry
- **Updated**: 2026-10-02
```

For LOW work with no `plan.md`, put the remaining inline steps under **Next step**.

## Section-scoped writes (critical)

Replace or append only between a section's `##` header and the next `##` header or end of file. Never rewrite the whole file. A whole-file write during a pause silently destroys the decision log, and a decision append that touches the Handoff corrupts in-flight state. If the file does not exist, create it with both headers.

## Pause

Triggered by "pause", "stop for today", "end session", or a session that is clearly ending mid-feature.

1. Finish or safely park the current step. Do not leave a half-applied edit you cannot describe.
2. Make sure `plan.md` statuses are current (`[~]` for the task in progress).
3. Replace the Handoff section.
4. Ask whether to make a WIP commit of uncommitted work. Do not decide that alone, since a WIP commit affects the user's history.
5. Tell the user, in one line, where things stand and what comes next.

## Resume

Triggered by "resume", "continue", "where were we", or a new session on a feature with an active Handoff.

Resume is the counterpart of [status.md](status.md): status only reports drift; resume fixes it in `plan.md` and the Handoff. A request that only asks where things stand ("status", "where are we", "what's next") is Status, and changes nothing.

1. Read `STATE.md` (Decisions, then Handoff) and the feature's `plan.md`.
2. **Treat the Handoff as a hypothesis.** Reconcile it against evidence:
   - current branch vs. the Handoff branch
   - `git status --porcelain`
   - recent commits (`git log --oneline <base>..HEAD`)
   - task statuses in `plan.md`
3. Resolve conflicts with evidence:
   - A task committed with a green gate but still open in `plan.md` → mark it done (citing the SHA); do not redo it.
   - Uncommitted work matching the in-progress task → keep it, re-run its gate, continue the cycle.
   - Uncommitted changes you cannot map to any task → stop and ask. Never discard them.
   - Stale or missing Handoff → rebuild the next step from git plus `plan.md`.
4. Check open amendments and blockers.
5. Propose the next step in one or two lines and continue once confirmed, or immediately if the user said "continue".
