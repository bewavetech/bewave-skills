# Discuss Gray Areas

**Goal:** capture how the user envisions the parts of the feature that could reasonably go several ways, so the agent does not guess. Discuss runs inside Specify. It clarifies HOW the scoped feature behaves; it never decides WHETHER to add capabilities.

## When it runs

| Level | Trigger |
| --- | --- |
| LOW | Never. If a LOW change has a real gray area, it is not LOW. |
| MEDIUM | User-facing behavior has two or more plausible designs and the user has not expressed a preference |
| HIGH | Any gray area above, or any implicit-requirement dimension present and undecided |
| CRITICAL | Always, at least to confirm invariants, failure behavior and rollback expectations |

The user can always invoke it explicitly ("discuss", "how should this work?").

## Process

### 1. Find feature-specific gray areas

Pick 3–4 concrete decisions for **this** feature, never generic categories.

| The feature is something users… | Typical gray areas |
| --- | --- |
| SEE | Layout, density, empty and loading states, what is shown on error |
| CALL (API) | Response shape, error format, pagination, versioning, rate limits |
| RUN (CLI, job) | Output format, flags, verbosity, exit codes, re-run behavior |
| READ (docs, emails) | Structure, tone, depth |
| STORE or MOVE (backend, state) | Partial failure, idempotency, retries, ordering, retention |

### 2. Present and choose pace

Present the feature boundary and the gray areas. Ask once how they want to go, recommending **Guided**:

| Pace | Cadence |
| --- | --- |
| Quick | Propose a default plus a one-line rationale per area; the user accepts or overrides |
| Guided (default) | Assume where safe and invite correction; at most 2 independent questions per turn; dependent questions one at a time |
| Detailed | One decision per turn in dependency order |

Honor switches mid-way ("just decide", "slow down") without re-asking settled points.

### 3. Deep-dive

- Options are concrete ("table with inline edit" vs. "cards with a detail drawer"), never "option A".
- Lead with your recommendation and one line of reasoning drawn from the codebase.
- Offer "you decide"; record it as agent discretion.
- Never ask what the code answers. Never ask about internal architecture; that is Plan's job.
- Scope creep ("should we also add comments?") goes to Deferred Ideas: "That's a separate feature, noted. Back to X."

### 4. Record

Write `context.md` from [assets/templates/context.md](../assets/templates/context.md) when the discussion produced decisions worth keeping beyond this session. That is usually HIGH and CRITICAL. For MEDIUM, fold short decisions straight into the spec as ACs or assumptions and skip `context.md`.

Every decision that changes observable behavior must also appear in `spec.md` as an AC or an assumption. `context.md` holds the reasoning, references and deferred ideas, not a second copy of requirements.

Declined or undiscussed areas become assumptions in the spec with a chosen default and a rationale.
