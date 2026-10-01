# React Native Performance Skill

An independent skill based on an adaptation of Callstack's **The Ultimate Guide to React Native Optimization 2026**. This is not an official Callstack skill.

## Usage

The skill lives in `.agents/skills/rn-performance/`, with `SKILL.md`, topic references, report templates, and a metrics comparison script. Agents that support skills can load this directory; automatic discovery varies by tool.

Example requests:

- "Use rn-performance in audit mode to analyze this React Native app without changing the code."
- "Use rn-performance in fix mode to fix PERF-001 and verify the same interaction."
- "Use rn-performance in verify mode to compare the before and after results."

`audit`, `fix`, and `verify` are modes described in the request, not registered CLI commands.

## Process

Reproduce → measure → form a hypothesis → fix → verify behavior → measure again.

The skill distinguishes between issues confirmed at runtime, evidence found in the code, and hypotheses. Without a device or trace, it does not present performance gains as proven.

## Comparing real measurements

Copy the schema from `.agents/skills/rn-performance/assets/metrics-example.json` into two files and fill in the context and collected samples. The empty lists in the template are intentional: they need real data.

```bash
python3 .agents/skills/rn-performance/scripts/compare_metrics.py baseline.json candidate.json
```

Requires Python 3, with no additional dependencies. It rejects incompatible contexts and invalid data. It computes the median, nearest-rank p95, range, and descriptive change; it does not prove statistical significance or causality.

## References and limits

The map of all performance chapters is in `references/sources.md`, inside the skill, with PDF page numbers and official references for version-sensitive rules. The original PDF is not included. The skill does not provide access to devices, profilers, or app repositories.
