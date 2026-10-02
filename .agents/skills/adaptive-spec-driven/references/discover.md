# Discover

**Goal:** understand the request, the code it touches and how far a mistake could spread, then classify risk. Discover is short for LOW work (a minute of reading) and thorough for CRITICAL work. It always runs.

## Process

### 1. Load memory

- If `.specs/PROJECT.md` exists, read it for the stack, real quality commands and conventions; do not rediscover what it already states, but trust the code where they disagree. If `ARCHITECTURE.md` exists, read only the sections for the affected area. Missing project files never block Discover ([init.md](init.md)).
- If `.specs/STATE.md` exists, read `## Decisions`. Active `AD-NNN` entries constrain this work.
- If the request continues earlier work, follow Resume in [memory.md](memory.md) instead.
- For anything that may land at MEDIUM or above, load confirmed lessons for the area:
  `python3 <skill-dir>/scripts/lessons.py list --status confirmed [--scope <area>] [--query <term>]`.
  Load only `confirmed`. If no store exists, skip silently.

### 2. Restate the request

One or two sentences: what changes for whom, and what done looks like. If the request is a bug, state the observed and the expected behavior. Ask only if the request cannot be restated without a guess about intent; otherwise continue and log the assumption.

### 3. Map the affected surface

Read before asking. Use the strongest available search tool (see [research.md](research.md)) to find:

- **Entry points**: routes, screens, commands, jobs or events where the behavior starts.
- **Call graph**: who calls the code you will change. Count call sites of every function, type, schema or event you might modify. This count is the blast-radius evidence.
- **Contracts**: public APIs, event payloads, DB schemas, SDK surfaces and config keys others depend on.
- **State**: tables, caches, queues and files read or written.
- **External systems**: network calls, webhooks, third-party SDKs.
- **Tests**: existing tests for this area, their layer, framework and location pattern, and how they are run.
- **Commands**: the project's real build, lint, typecheck and test commands, taken from manifests, task runners and CI config. Never invent them.
- **Conventions**: AGENTS.md, CONTRIBUTING, testing guidelines, coverage thresholds.

Keep it proportional. LOW: the file and its direct callers. CRITICAL: the full path from entry point to persistence, plus every consumer of each contract you will touch.

### 4. Rate the factors and classify

Rate each factor from [risk.md](risk.md) with one line of evidence, then compute:

```bash
python3 <skill-dir>/scripts/risk.py --set auth=medium state=medium blast_radius=low
```

### 5. Announce the track

One line, then move on. Do not ask for permission to apply the profile.

```
Risk: HIGH — migrations=medium, concurrency=medium (2 job workers update the same rows)
→ full spec, plan approval, independent verification.
```

For LOW, continue directly with the inline spec and plan ([SKILL.md](../SKILL.md), LOW track). For MEDIUM and above, continue to [specify.md](specify.md). The factor table and its evidence go into the spec's Risk Assessment section; do not write them anywhere else.

## Discover outputs

| Level | Output |
| --- | --- |
| LOW | Chat only: restatement, risk line, inline ACs and steps |
| MEDIUM+ | Risk line in chat; the factor table becomes the first content of `spec.md` |

## Escalation signals during Discover

Stop and raise the level, or open Discuss, if you find:

- The "simple fix" lives in code shared by many features.
- Behavior depends on undocumented data shapes or production-only configuration.
- There are no tests around the area and the change alters behavior. Characterization tests become mandatory before changing it ([testing.md](testing.md)).
- The request conflicts with an active `AD-NNN` decision. Either conform, or record a superseding decision during Plan.
