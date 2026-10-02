# Architecture

<!--
Documents the architecture that EXISTS, not the one the agent wishes existed.
Evidence order: code > configuration > documentation > inference. Cite paths.
Delete every section that does not apply. Never pad a section to satisfy the template.
New project with no code yet: replace the body with `## Current Architecture` + `## Planned Architecture`
(see references/init.md), listing only technologies the user explicitly chose.
-->

## Overview

<Two to four sentences: the architectural shape of the system.>

## System Context

<Users, the applications they use, and the external systems this one talks to.>

## Applications / Services

| Name | Path | Responsibility | Runtime |
| --- | --- | --- | --- |
| <app / service / package> | `<path>` | <what it owns> | <platform> |

## High-Level Architecture

<!-- Mermaid only when it saves words. -->

## Modules

| Module | Path | Responsibility | Depends on |
| --- | --- | --- | --- |
| <module> | `<path>` | <what it owns> | <modules> |

## Data Flow

<How a typical request or user action moves through the system, with paths.>

## Data / Persistence

<Databases, schemas and migrations, storage, caches, and the access patterns in use.>

## Authentication & Authorization

<Mechanism, where it is enforced, session/token handling.>

## External Integrations

| System | Purpose | Integrated in | Direction |
| --- | --- | --- | --- |
| <system> | <why> | `<path>` | outbound / inbound / both |

## Cross-Cutting Concerns

- **Logging / observability**: <tooling and where it is wired>
- **Error handling**: <pattern>
- **Configuration**: <env files, config modules, feature flags>

## Testing Architecture

<Test layers, frameworks, locations and how they run.>

## Deployment

<!-- Only what can be discovered reliably (CI/CD files, IaC, platform config). -->

## Architectural Conventions

- <Pattern actually used, with an example path>

## Known Constraints

- <Architectural limitation>

## Documentation Drift

<!-- Delete if none. -->

- <Doc> says <X>; the code does <Y> (`<path>`).

## Open Architectural Questions

<!-- Only questions that are genuinely open. Delete if none. -->
