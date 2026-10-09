# Bewave Skills

Agent skills for Claude Code, Codex, and other agents supported by the [`skills`](https://www.npmjs.com/package/skills) CLI.

| Skill | What it does |
| --- | --- |
| [`rn-performance`](.agents/skills/rn-performance/SKILL.md) | Audits, diagnoses, and fixes React Native and Expo performance (startup/TTI, dropped frames, re-renders, lists, memory, animations, bundle size) using profiling evidence and before/after measurements. Based on an adaptation of Callstack's *Ultimate Guide to React Native Optimization 2026* (not an official Callstack skill). |
| [`adaptive-spec-driven`](.agents/skills/adaptive-spec-driven/SKILL.md) | Spec-driven development that scales rigor to risk. Classifies each change as LOW, MEDIUM, HIGH, or CRITICAL, then sizes the spec, plan, tests, and verification to match, taking a feature from discovery to verified, committed code. |

## Installation

Requires Node.js. No need to clone this repository.

```bash
# All projects (Claude Code)
npx skills add bewavetech/bewave-skills --skill rn-performance --agent claude-code --global --yes
npx skills add bewavetech/bewave-skills --skill adaptive-spec-driven --agent claude-code --global --yes
```

- **One project only:** drop `--global` and run from the project root (the skill can then be committed with the repo).
- **Other agents:** change `--agent`, e.g. `--agent codex`.
- **Update:** run the same command again.

Restart the agent, then type `/` (Claude Code) or `$` (Codex) to confirm the skill is listed.

## Usage

The agent loads a skill automatically when the request matches it. You can also call it explicitly: `/skill-name <request>` in Claude Code, `$skill-name <request>` in Codex.

### rn-performance

Run it from the root of a React Native or Expo app. It works in three modes, picked from your wording:

| Mode | What it does | Changes code? |
| --- | --- | --- |
| **audit** (default) | Prioritized findings (`PERF-001`, ...) from source, config, and traces | No |
| **fix** | Implements one finding, then runs the available checks | Yes |
| **verify** | Compares baseline vs. candidate measurements | No |

```text
/rn-performance audit why the product list stutters when scrolling on Android
/rn-performance fix PERF-001 and verify the same interaction
/rn-performance compare baseline.json and candidate.json
```

Give it the symptom, platform/device, build mode, and any traces you have. Without a device or trace it still runs static analysis, but won't claim gains as proven. Metrics helpers (`scripts/`, Python 3) are documented in the skill.

### adaptive-spec-driven

Run it from the root of any project.

```text
/adaptive-spec-driven init                     # optional: writes .specs/PROJECT.md and ARCHITECTURE.md
/adaptive-spec-driven add CSV export to the reports page
/adaptive-spec-driven status                   # read-only progress and next step
/adaptive-spec-driven pause | resume
```

For each change it runs discover → specify → plan → execute → verify. LOW-risk work stays inline in the chat; higher risk produces `spec.md`, `plan.md`, and `validation.md` under `.specs/features/<feature>/` and asks for approval before building. Approval covers local edits and commits only; push, deploy, and other irreversible actions always need explicit confirmation.
