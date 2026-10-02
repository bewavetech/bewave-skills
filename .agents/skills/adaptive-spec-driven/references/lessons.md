# Lessons

**Goal:** turn real verification failures into project-local guidance that changes future behavior, without the file rotting into a log nobody trusts.

**Division of labor.** The agent supplies judgment: which failure happened, how to phrase the general rule, what grounds it. `scripts/lessons.py` owns the bookkeeping: IDs, recurrence across distinct features, promotion, pruning, quarantine and rendering. Hand-kept bookkeeping is what rots, so do not do it by hand.

| File | Owner | Purpose |
| --- | --- | --- |
| `.specs/lessons.json` | script | Canonical store. Never hand-edit. |
| `.specs/LESSONS.md` | script (rendered) | Readable playbook. Read it; never edit it. |

Statuses: `candidate` (seen once, tracked but not trusted), `confirmed` (recurred in ≥2 distinct features; this is what gets loaded), `quarantined` (failed when applied; ignored).

## Write: after verification, on signal only

No signal, no lesson. A clean PASS records nothing, and that is correct.

| Signal | `--signal` |
| --- | --- |
| An AC failed or had no evidence | `ac_gap` |
| A mutant survived | `surviving_mutant` |
| A spec-precision gap was found | `spec_precision_gap` |
| An approved behavior-change or risk-change amendment | `spec_amendment` |
| The full gate failed at verification | `gate_fail` |
| A UAT issue of major or blocker severity | `uat_issue` |
| A defect found later in a feature that had passed verification | `escaped_defect` |

```bash
python3 <skill-dir>/scripts/lessons.py add \
  --feature coupon-expiry \
  --signal surviving_mutant \
  --source "src/coupons/validate.ts:41 (mutation 3)" \
  --text "Assert the exact error code for each rejection path, not only the HTTP status" \
  --scope coupons
```

`--source` is mandatory: the script refuses ungrounded lessons.

**Phrasing.** Write the general rule, not the incident ("Compare expiry timestamps in UTC", not "the test on line 88 was wrong"). Be terse and canonical: deduplication is exact after normalization, so the same lesson must read the same way to recur and promote. One lesson per signal. Capture **project** lessons about this codebase, never opinions about the method itself; those belong to Evolve ([evolve.md](evolve.md#evolutionmd)).

**Self-check.** If verification produced a signal and you recorded nothing, say so in chat and why.

**Demotion.** If a confirmed lesson was loaded for this feature and the same failure happened anyway, run `lessons.py penalize --id L-NNN`. Two penalties quarantine it.

`escaped_defect` is the strongest signal the system gets: verification passed and reality disagreed. When a bug traces to a feature built with this skill, record it once the fix is verified, and ask what the risk classification or test depth missed.

## Read: Discover and Plan, MEDIUM and above

```bash
python3 <skill-dir>/scripts/lessons.py list --status confirmed
python3 <skill-dir>/scripts/lessons.py list --status confirmed --scope coupons
python3 <skill-dir>/scripts/lessons.py list --status confirmed --query idempotency
```

Apply what comes back as guidance while specifying and planning. A lesson about risk ("background jobs on the orders table are always concurrency=medium") should directly inform factor ratings. Never load candidates or quarantined lessons as guidance.

## Other commands

`lessons.py status` (counts), `lessons.py prune` (drop stale uncorroborated candidates; also runs automatically), `lessons.py init`, `lessons.py selftest`.

## Without code execution

Maintain `.specs/LESSONS.md` by hand with the same rules (grounded only, promote after two distinct features). Say once that bookkeeping is best-effort in this mode.

## Disable

Delete `.specs/lessons.json` and `.specs/LESSONS.md` and skip the read and write steps. Nothing else depends on them.
