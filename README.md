# React Native Performance Skill

An independent skill based on an adaptation of Callstack's **The Ultimate Guide to React Native Optimization 2026**. This is not an official Callstack skill.

It helps a coding agent audit, diagnose, and fix React Native and Expo performance problems using profiling evidence and repeatable before/after measurements: slow startup or TTI, dropped frames, input lag, excessive re-renders, large lists, memory leaks, expensive animations, native module threading, and bundle size.

## Contents

```
.agents/skills/rn-performance/
├── SKILL.md                    # Main instructions loaded by the agent
├── references/                 # Topic guides (rendering, lists, memory, startup, ...)
│   ├── profiling-tools.md      # Profiler selection and capture playbooks
│   └── sources.md              # Chapter map, PDF pages, official references
├── assets/
│   ├── report-template.md      # Structure of the audit/fix report
│   └── metrics-example.json    # Schema for recorded measurements
├── scripts/
│   ├── compare_metrics.py      # Baseline vs. candidate comparison
│   └── template_metrics.py     # Generate baseline/candidate JSON skeletons
└── agents/
    └── openai.yaml             # Display metadata for Codex
```

## Installation

Install the skill directly from GitHub with the [`skills`](https://www.npmjs.com/package/skills) CLI. You need Node.js (for `npx`); you don't have to clone this repository.

### Claude Code (all projects)

```bash
npx skills add bewavetech/skill-rn-performance --skill rn-performance --agent claude-code --global --yes
```

| Flag | Meaning |
| --- | --- |
| `--skill rn-performance` | Installs this skill from the repository. |
| `--agent claude-code` | Installs it for Claude Code. |
| `--global` | Installs it for your user, so it's available in every project. |
| `--yes` | Skips the confirmation prompts. |

### Claude Code (one project only)

Run this from the root of the React Native app without `--global`. The skill is installed inside the project, so you can commit it and share it with your team.

```bash
npx skills add bewavetech/skill-rn-performance --skill rn-performance --agent claude-code --yes
```

### Other agents

Change the `--agent` value to install for another supported agent, for example Codex:

```bash
npx skills add bewavetech/skill-rn-performance --skill rn-performance --agent codex --global --yes
```

### Updating

To get the latest version, run the same install command again.

### Checking the installation

Restart the agent or open a new session, then:

- **Claude Code:** type `/` and look for `rn-performance`, or ask "Which skills do you have available?"
- **Codex:** type `$` and look for `rn-performance`, or ask the same question.

### Requirements

- Node.js, to run `npx skills add`.
- An agent with skill support (Claude Code, Codex, or another agent supported by the `skills` CLI).
- Python 3 only if you want to use the metrics helper scripts. No extra packages are needed.
- For runtime evidence: a device or emulator, and the profiling tools relevant to the problem (React Native DevTools, Hermes profiler, Android Studio / Perfetto, Xcode Instruments, Expo Atlas, bundle analyzers, etc.). Without them, the skill still works, but only for static analysis.

## Usage

Open the agent at the root of your React Native or Expo app and describe the problem. The agent loads the skill automatically when the request is about React Native performance. You can also invoke it explicitly:

- **Claude Code:** `/rn-performance <your request>`
- **Codex:** `$rn-performance <your request>`
- **Any agent:** mention "use rn-performance" in the request.

### Modes

The skill works in three modes. They are chosen from the wording of your request; they are not CLI commands.

| Mode | What it does | Changes code? |
| --- | --- | --- |
| **audit** | Inspects the project, configuration, and any traces you provide, then returns a prioritized report of findings (`PERF-001`, `PERF-002`, ...). | No |
| **fix** | Implements a specific finding, or the highest-priority evidenced one, one hypothesis at a time, then runs the available checks. | Yes, within the scope you authorize |
| **verify** | Compares before/after measurements and functional checks against the recorded baseline. Does not add new optimizations. | No |

If you ask for a general performance review without authorizing changes, the skill defaults to **audit**.

### A typical workflow

1. **Audit.** Ask for an audit of the whole app or a specific flow:

   > Use rn-performance in audit mode to analyze this React Native app, without changing the code.

   > Use rn-performance to audit why the product list stutters when scrolling on Android.

   The agent detects the installed versions (React Native, Expo, Hermes, New Architecture, React Compiler, Reanimated, navigation, lists, state management), picks the relevant areas, and writes a report following `assets/report-template.md`.

2. **Measure a baseline.** Record the affected scenario on a real device or emulator, ideally in a release or profiling build, and save the samples in a JSON file (see [Comparing real measurements](#comparing-real-measurements)).

3. **Fix.** Ask for a specific finding:

   > Use rn-performance in fix mode to fix PERF-001 and verify the same interaction.

4. **Verify.** Repeat the same scenario under the same conditions and compare:

   > Use rn-performance in verify mode to compare baseline.json and candidate.json.

### Writing good requests

The more context you give, the less the agent has to guess. Useful details:

- **Symptom and flow:** "typing in the search field lags", "cold start takes 4 s until the home screen is usable".
- **Platform and device:** Android/iOS, model, OS version, refresh rate.
- **Build mode:** debug, release, or profiling build.
- **Data volume:** for example, "a list of about 2,000 items".
- **Evidence you already have:** paths to traces, profiler exports, screenshots, or measurements.
- **Scope:** what the agent may change (for example, "only files in `src/features/search`", "do not add dependencies").

### How to read the results

Each finding is labeled with how strong its evidence is:

- **runtime-confirmed:** reproduced, and backed by a trace or measurement tied to the code path.
- **source-supported:** the code shows a clear mechanism, but its runtime impact hasn't been measured.
- **hypothesis:** plausible, but needs more evidence.

After a fix, the outcome is reported as **verified improvement**, **no demonstrated improvement**, **regression**, or **runtime impact unverified**. Without a device or trace, the skill does not present performance gains as proven.

## Process

Reproduce → measure → form a hypothesis → fix → verify behavior → measure again.

## Comparing real measurements

Copy the schema from `.agents/skills/rn-performance/assets/metrics-example.json` into two files (for example `baseline.json` and `candidate.json`) and fill them in:

- `run`: the build or commit and the path to the trace.
- `context`: platform, device, OS, build mode, scenario, engine, architecture, refresh rate, dataset, network, cache, start type, and instrumentation. **Both files must have the same context**, otherwise the comparison is rejected.
- `metrics`: one entry per metric, with its unit, its direction (`lower` or `higher` is better), and the collected `samples`.

The empty lists in the template are intentional: they need real data. For example:

```json
"metrics": {
  "tti_ms": {"unit": "ms", "direction": "lower", "samples": [1840, 1795, 1902, 1860, 1821]}
}
```

Then run:

```bash
python3 ~/.claude/skills/rn-performance/scripts/compare_metrics.py baseline.json candidate.json
```

You can generate an empty record with all required context fields:

```bash
python3 ~/.claude/skills/rn-performance/scripts/template_metrics.py \
  --platform android \
  --device "Pixel 8" \
  --os "Android 15" \
  --scenario "cold-launch-to-searchable-home" \
  --engine "Hermes" \
  --architecture "new-architecture" \
  --artifact "build-or-commit" \
  --metric tti_ms:ms:lower > baseline.json
```

This path is for the global Claude Code install. For a project install or another agent, point to the matching file inside the `scripts/` folder where the skill was installed. You can also just ask the agent to generate the template or run the comparison for you.

The script rejects incompatible contexts and invalid data. It computes the median, nearest-rank p95, range, and descriptive change; it does not prove statistical significance or causality. Collect several samples per side and keep slow runs instead of discarding them.

## References and limits

The map of all performance chapters is in `references/sources.md`, inside the skill, with PDF page numbers and official references for version-sensitive rules. The original PDF is not included. The skill does not provide access to devices, profilers, or app repositories.
