# Research and Tool Selection

**Goal:** replace assumptions with verified facts before they reach the plan, and pick the right tools without handing that choice to the user.

## Knowledge verification chain

Follow it in order. Do not skip ahead to a later step while an earlier one is available.

```
1. Codebase        existing code, conventions, installed versions, types in node_modules / site-packages / vendor
2. Project docs    README, docs/, ADRs, AGENTS.md, .specs/STATE.md decisions
3. Library docs    Context7 MCP or the vendor's docs for the installed version
4. Web             official sources first, then reputable community sources
5. Uncertain       say "I could not verify X; my best reading is Y" and treat it as a risk
```

- Version matters. Read the lockfile or installed package before trusting any doc, and query docs for that version.
- Never invent an API, flag, config key, command or behavior. A fabricated fact propagates through plan, tasks and tests.
- Unverified facts that the plan depends on go into the plan's Risks section with a mitigation, such as a spike task or a contract test.

## When research is mandatory

| Level | Research |
| --- | --- |
| LOW | Only if something is unfamiliar |
| MEDIUM | Unfamiliar library, API or pattern |
| HIGH | Any new dependency, external integration, or a pattern not yet used in this codebase |
| CRITICAL | All of the above, pinned to exact versions, plus the failure semantics of every external system (timeouts, retries, idempotency guarantees, error codes) |

Record findings briefly in the plan's Design section, with a source link or `file:line`. Do not produce a separate research document unless the user asks.

## Concern flagging

While reading code for research, flag what threatens this change: fragile code, tech debt, security gaps, performance hazards (N+1, unbounded loops), untested paths the feature depends on. Each concern goes into the plan's Risks & Mitigations with a mitigation.

## Tool selection: the agent decides

Tool choice is engineering judgment and it is the agent's job. Do not ask "which MCP should I use?".

1. **Inventory once per session.** Note the available MCP servers, skills, CLIs (`rg`, `ast-grep`, language servers, test runners) and whether sub-agents and worktrees are available.
2. **Pick per need**, preferring the most precise tool available:

   | Need | Prefer → fall back |
   | --- | --- |
   | Structural code search | `ast-grep` / LSP references → `rg` → `grep` |
   | Text search | `rg` → `grep` |
   | Library or API docs | Context7 or the vendor docs MCP → official web docs |
   | Current events, changelogs | Web search |
   | UI behavior, visual checks | Browser automation MCP (Playwright, Chrome) → manual UAT |
   | Data shape questions | Read-only DB / warehouse MCP, if configured → schema files |
   | Specialized domains | A matching installed skill (performance, security, framework-specific) |

3. **Mention the choice only when it matters** to the outcome, for example "verified against Stripe API 2024-06 via Context7".
4. **Ask the user only when** a tool needs credentials they must supply, costs money, has external side effects (sending messages, writing to shared systems), or is disallowed by project policy.

Tools are not recorded per task in `plan.md`. If a task depends on a specific tool, such as a migration CLI or a contract-testing harness, mention it in the task's Change line.

## Code search scope

Exclude generated and vendored trees (`node_modules`, `vendor`, `dist`, `build`, `.git`) unless tracing an implicated dependency. Use focused reads; do not load whole directories into context.
