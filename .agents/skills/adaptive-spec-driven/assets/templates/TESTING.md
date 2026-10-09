# Testing

<!--
Project-specific test rules: HOW this project tests. Written by `init` from the repository (code > config > docs); never invented.
Generic rules (test origins, depth by risk, integrity) live in the skill's testing.md and are not repeated here.
Commands live in PROJECT.md → Quality. Delete sections that do not apply.
-->

## Stack

| Layer | Runner / library | Config |
| --- | --- | --- |
| <unit / integration / e2e / contract> | <name + version> | `<config path>` |

## Layout and Naming

- <Where tests live (colocated or mirrored tree) and the file naming pattern, e.g. `*.test.ts` next to the source>
- <Test naming style, e.g. `describe('<unit>') / it('<behavior>')`>

## Layers

| Layer | Use for | Example |
| --- | --- | --- |
| <unit> | <what is tested at this layer here> | `<path to a representative test>` |

## Fixtures and Test Doubles

- <Factories, builders, seed data, shared helpers and where they live>
- <What may be faked or mocked (external HTTP, clock, queue) and what must never be (own modules, DB in integration tests)>

## Standards

- <Coverage threshold or CI requirement, with source>
- <Required patterns: async handling, time/randomness control, test isolation, snapshot policy>
- <Forbidden: `.only`, skipped tests without ticket, network in unit tests, ...>

## Known Gaps

<!-- Untested or flaky areas that affect planning. Delete if none. -->

- <Area> has no tests; changes there need CHARACTERIZATION first.
