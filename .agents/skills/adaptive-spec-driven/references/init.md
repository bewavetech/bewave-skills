# Init

**Goal:** prepare a project for Adaptive Spec Driven by writing down what the project is (`.specs/PROJECT.md`), how it is built (`ARCHITECTURE.md`), and an empty work state (`.specs/STATE.md`). Init is project-level; it never starts a feature.

Triggered by "init", "init project", "initialize project", "setup adaptive spec", "bootstrap project", "start project", "initialize adaptive spec".

**Facts are discovered. Decisions are asked.** Never ask what the repository can answer.

**Init is idempotent.** Running it twice never destroys content. Existing files are read, compared and, when they drifted, an update is proposed. They are never overwritten silently.

| File | Owns | Template |
| --- | --- | --- |
| `.specs/PROJECT.md` | What the project is: overview, goals, stack, structure, conventions, quality commands, external systems, constraints | [PROJECT.md](../assets/templates/PROJECT.md) |
| `ARCHITECTURE.md` (project root) | How the system is built: services, modules, data flow, persistence, auth, integrations, cross-cutting concerns | [ARCHITECTURE.md](../assets/templates/ARCHITECTURE.md) |
| `.specs/STATE.md` | Where the work is: decisions and handoff | [STATE.md](../assets/templates/STATE.md) |

`PROJECT.md` links to `ARCHITECTURE.md` and never repeats its detail. Neither of them holds in-flight work.

## 1. Detect the mode

Inspect the repository before anything else.

| Mode | Signal |
| --- | --- |
| **Existing project** | Source files, a package manifest or a build config exist |
| **New / empty project** | Nothing beyond scaffolding: empty dir, README stub, license, `.gitignore`, an untouched generator template |
| **Re-init** | `.specs/PROJECT.md`, `.specs/STATE.md` or `ARCHITECTURE.md` already exists (combine with one of the above) |

## 2. Existing project: discover

```
Inspect repository → stack → structure → architecture → conventions
→ build/test/lint/typecheck → integrations → existing docs → write metadata
```

Read what exists, proportionally. Use explorer sub-agents for large monorepos ([sub-agents.md](sub-agents.md)). Exclude generated and vendored trees.

| Area | Where to look |
| --- | --- |
| Stack and versions | Manifests and lockfiles (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `Gemfile`, `pom.xml`, `build.gradle`, `Podfile`, `app.json`/`app.config.*`) |
| Structure | Top-level and source directories; workspace config (`pnpm-workspace.yaml`, `turbo.json`, `nx.json`, `lerna.json`, Cargo/Go workspaces) |
| Architecture | Entry points, routing/navigation, state management, API layer, module boundaries, DI, layering |
| Quality commands | Scripts in manifests, `Makefile`, task runners, CI workflows. Copy the real commands; never invent them |
| Test setup | Test config files, test directories, layers in use |
| Lint / format | ESLint, Prettier, Biome, Ruff, golangci, EditorConfig |
| CI/CD and deployment | `.github/workflows`, GitLab CI, EAS, Fastlane, Dockerfiles, IaC |
| Environment | `.env.example`, config modules. Never read or copy secret values |
| Data | Schemas, ORM models, migrations, storage and cache clients |
| Auth | Auth providers, middleware, guards, token/session handling |
| Integrations | SDK clients, HTTP clients, webhooks, queues |
| Documentation | `README`, `docs/`, ADRs, `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING`, existing `ARCHITECTURE.md`, existing `.specs/` |

### Evidence order

```
CODE > CONFIGURATION > DOCUMENTATION > INFERENCE
```

- Document the architecture that exists, not the one you would prefer.
- When documentation contradicts the code, the code wins. Record the conflict under `## Documentation Drift` (for example: "README describes Redux; the app uses Zustand (`src/store/`)"). Do not change the project to match the docs.
- Inference is allowed only when labeled ("inferred from …"). What cannot be determined is `Unknown`, or omitted if it does not matter.
- Delete template sections that do not apply. An empty section with filler is worse than no section.

## 3. New / empty project: ask the minimum

Ask in **one** compact message, only what you cannot discover and what a first feature needs:

- the product or problem, and its primary users;
- the main capabilities;
- the stack, if already decided;
- hard constraints (platform, compliance, deadlines, budget);
- deployment or platform expectations.

Do not run a questionnaire. Decisions that can wait until a feature needs them wait. No speculative architecture: an undecided technology is not written down.

In `ARCHITECTURE.md`, separate what exists from what is planned, and list only explicit choices:

```markdown
## Current Architecture

Project not implemented yet.

## Planned Architecture

- React Native application (decided by user)
- REST API (decided by user)
- PostgreSQL (decided by user)
```

Never present planned architecture as current. When code later implements it, move it to the regular sections.

## 4. Write the files

For each file, in this order: `ARCHITECTURE.md`, `.specs/PROJECT.md`, `.specs/STATE.md`.

| File state | Action |
| --- | --- |
| Missing | Create it from the template, filled with discovered facts |
| Present | Read it and use it as a context source. Do **not** overwrite. Compare it with the repository (step 5) |

`ARCHITECTURE.md` may also exist under another name (`docs/architecture.md`, ADRs). If so, do not create a duplicate root file: reference the existing document from `PROJECT.md` → References and say so in the summary.

**`STATE.md`** keeps its two-section format ([memory.md](memory.md)). A fresh one gets an empty `## Decisions` and this Handoff:

```markdown
## Handoff
- **Feature**: none
- **Next step**: start a feature
- **Blockers**: none
- **Updated**: <YYYY-MM-DD>
```

If `STATE.md` exists, leave it untouched. Section-scoped writes only, as always.

**Lessons.** Initialize the store with the existing script; it keeps any lessons already recorded:

```bash
python3 <skill-dir>/scripts/lessons.py init
```

**Project decisions.** Do not invent `AD-NNN` entries during init. Record one only if the user made a project-level decision during the new-project questions and it meets the criteria in [memory.md](memory.md).

## 5. Re-init: detect drift, propose, never destroy

When a file already exists, compare it with what discovery found:

- stack or version changes, new or removed apps/packages/modules;
- quality commands that no longer exist or changed;
- new external systems, databases or auth mechanisms;
- documentation drift not yet recorded;
- planned architecture that has since been implemented.

Report material drift as a short list and propose the specific section edits. Apply them only after the user agrees. Never rewrite hand-written decisions or prose; edit the affected section only. No drift → say "up to date" and change nothing.

## 6. Validate

```bash
python3 <skill-dir>/scripts/validate_project.py
```

It checks structure only: the three files exist, `PROJECT.md` has its core sections and links to the architecture document, `STATE.md` has both headers, no template placeholders remain. It does not judge the architecture. Fix every ERROR.

## 7. Report

Compact. The documents carry the detail; do not paste the analysis into chat.

```
Adaptive Spec Driven initialized.

Project
✓ Existing React Native project (Expo SDK 52, TypeScript)
✓ Jest · ESLint · tsc

Existing
✓ ARCHITECTURE.md (read; no drift)

Created
✓ .specs/PROJECT.md
✓ .specs/STATE.md
✓ .specs/lessons.json, .specs/LESSONS.md

Drift
! README describes Redux; code uses Zustand (recorded in PROJECT.md)

Ready to start a feature.
```

## Using the project files later

Init writes them; the rest of the workflow reads them incrementally:

- **Discover** reads `PROJECT.md` (stack, quality commands, conventions) and the `ARCHITECTURE.md` sections for the affected area. Do not load both in full for every task.
- **Plan** flags `ARCHITECTURE_UPDATE_REQUIRED` when the approved design materially changes the documented architecture ([plan.md](plan.md)).
- **Verify** applies that update when the feature passes ([verify.md](verify.md)).
- Missing project files never block feature work. Proceed with Discover; suggest `init` once if the project would benefit.
