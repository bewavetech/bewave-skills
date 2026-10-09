# Project: <name>

<!--
Stable project context: WHAT this project is. Written by `init`; refreshed only when a drift proposal is approved.
In-flight work belongs in STATE.md. Architecture detail belongs in ARCHITECTURE.md; link to it, do not copy it.
Existing projects: facts come from code > configuration > documentation > inference. Never invent.
Delete sections that do not apply. Write `Unknown` only where the gap matters.
-->

## Overview

<One or two sentences: what the product or system does and for whom.>

## Goals

- <Known objective>

## Stack

| Area | Technology | Source |
| --- | --- | --- |
| <language / framework / runtime / database> | <name + version> | `<manifest or config path>` or "decided by user" |

## Repository Structure

| Path | Contents |
| --- | --- |
| `<path>` | <what lives there> |

## Engineering Conventions

- <Convention observed in the code or stated in AGENTS.md / CLAUDE.md / CONTRIBUTING, with its source>

## Quality

| Check | Command | Source |
| --- | --- | --- |
| Tests | `<command>` | `<package.json / Makefile / CI file>` |
| Lint | `<command>` | `<source>` |
| Typecheck | `<command>` | `<source>` |
| Build | `<command>` | `<source>` |

## External Systems

- **<System>**: <what it is used for> (`<where it is integrated>`)

## Constraints

- <Platform, compliance, performance, budget or compatibility constraint>

## Documentation Drift

<!-- Only when documentation contradicts the code. Code wins; record, do not fix. Delete if none. -->

- <Doc> says <X>; the code does <Y> (`<path>`).

## References

- [ARCHITECTURE.md](../ARCHITECTURE.md): architecture, modules, data flow
- [TESTING.md](TESTING.md): test stack, layout, layers, fixtures, standards
- [STATE.md](STATE.md): project decisions (AD-NNN) and current handoff
- <Other important project docs>
