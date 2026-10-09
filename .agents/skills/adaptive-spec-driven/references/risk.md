# Risk Classification

**Goal:** decide how much rigor a change deserves, with evidence, before writing the spec. The level is the single input that sizes every later phase.

## The twelve factors

Rate each factor `none`, `low`, `medium` or `high` for **this change**, not for the system in general. Base each rating on something you found during Discover and write that evidence down. A rating without evidence is a guess.

| Key | Factor | low | medium | high |
| --- | --- | --- | --- | --- |
| `ambiguity` | Ambiguity | One reasonable reading; minor defaults | Several user-visible behaviors undecided | Problem or success criteria unclear; stakeholders may disagree |
| `criticality` | Business criticality | Internal or rarely used path | Commonly used feature; degraded UX on failure | Revenue, onboarding, core flow, SLA or compliance path |
| `blast_radius` | Blast radius | One module, few callers | Shared component or several call sites; one public surface | Platform-wide utility, public API or event contract, many consumers |
| `novelty` | Architectural novelty | Follows an existing pattern exactly | Adapts a pattern or adds a dependency | New pattern, framework, service boundary or paradigm in this codebase |
| `irreversibility` | Irreversibility | Revert the commit and redeploy | Revert needs data cleanup or a coordinated rollout | Cannot be undone: deletes or transforms data, sends messages, publishes contracts |
| `integrations` | External integrations | Read-only, tolerant of failure | Writes to or depends on an external system with retries | Side-effecting calls where duplicates or loss matter (payments, emails, webhooks) |
| `state` | Persistence / state | Reads existing data | New fields or records in a conventional way | State machines, caches with invalidation, multi-store consistency |
| `auth` | Authentication / authorization | Displays role-based UI only | Adds or changes a permission check on a bounded resource | Changes login, sessions, tokens, tenancy or the authorization model |
| `concurrency` | Concurrency | Single-user, sequential | Parallel requests on the same records, background jobs | Ordering guarantees, locks, distributed coordination, race-prone counters |
| `migrations` | Migrations | Additive, backward-compatible schema change | Backfill, column rename with dual-write, index on a large table | Destructive or long-running migration on production data |
| `security` | Security | No untrusted input reaches the change | Untrusted input parsed or rendered; secrets referenced | Crypto, secret handling, injection surfaces, PII exposure, sandbox boundaries |
| `data_integrity` | Financial / data integrity | Derived or cosmetic data | Business records that can be corrected by hand | Money, balances, ledgers, inventory, medical/legal records, system of record |

`none` means the factor does not apply. Prefer `none` over `low` when the change truly does not touch the dimension. Display-only formatting of money or data (nothing computed, stored or sent) is `low` for `data_integrity`, not `medium`. Unrated factors count as `none`, so list only the ones that apply.

## Computing the level

The rules are deterministic so two agents classify the same change identically. `python3 <skill-dir>/scripts/risk.py` applies them.

```
CRITICAL  if any of {irreversibility, auth, security, data_integrity} is high
          or 3+ factors are high
HIGH      if any factor is high
          or any of {irreversibility, auth, security, data_integrity, migrations, concurrency} is medium
          or 3+ factors are medium
MEDIUM    if any factor is medium
LOW       otherwise (any number of low factors)
```

Usage:

```bash
python3 <skill-dir>/scripts/risk.py --set migrations=medium state=medium blast_radius=low
python3 <skill-dir>/scripts/risk.py --spec .specs/features/<feature>/spec.md   # reads the Risk Assessment table
python3 <skill-dir>/scripts/risk.py --profile HIGH                              # prints the rigor profile only
```

## Declared vs. computed

The spec records both. **Raising** the declared level above the computed one needs no justification: the user or the agent may simply want more assurance. **Lowering** it needs an `Override:` line explaining why the triggering factor does not carry its usual weight here (for example, "migration is additive on an empty table created in this same feature"). `validate_spec.py` fails a lowered level without an override line, and warns when the override is shorter than a real sentence. At LOW there is no spec, so state the override in the one-line triage in chat.

When in doubt between two levels, choose the higher one. The cost of extra rigor is minutes; the cost of under-verification on a critical path is an incident.

## Task-level risk

A task inherits the feature level unless its `Risk` field says otherwise. Set task risk when rigor should concentrate:

- A HIGH feature's task that only renames a label → `Risk: LOW — copy only, no behavior change`.
- A MEDIUM feature's task that runs a backfill → `Risk: HIGH — backfill on production table`.

Task risk sizes that task's test depth and discrimination ([testing.md](testing.md)). Feature risk still sizes artifacts, approvals and final verification. A task may raise the feature level: if any task is HIGH or CRITICAL, re-run `risk.py` and amend the feature level if the computed result changes.

## Re-classification

Risk is re-evaluated, not set once. Re-run the classification when:

- Discover or Research finds a factor you did not rate (a hidden external call, a shared table).
- A Spec Amendment of type `risk-change` is raised ([amendments.md](amendments.md)).
- A task's actual diff touches surfaces outside its `Touches` line.
- The verifier finds a failure mode the spec did not anticipate.

When the level rises mid-flight, apply the new profile to all remaining work, and **backfill** what completed work now lacks: missing test origins, discrimination, the verification tier. Do not re-do work that already meets the new bar. When the level falls, keep the artifacts already written; do not delete them to match.

The rigor profile per level is the table in [SKILL.md](../SKILL.md).
