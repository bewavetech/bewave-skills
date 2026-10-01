#!/usr/bin/env python3
"""Compare real recorded samples; refuse incompatible experiment contexts."""
import argparse
import json
import math
import statistics
import sys
from pathlib import Path

REQUIRED_CONTEXT = {
    'platform', 'device', 'os', 'build_mode', 'scenario', 'engine',
    'architecture', 'refresh_hz', 'dataset', 'network', 'cache',
    'start_type', 'instrumentation',
}


def load_record(path):
    try:
        record = json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise ValueError(f'{path}: cannot read JSON: {exc}') from exc
    if not isinstance(record, dict):
        raise ValueError(f'{path}: root must be an object')
    context, metrics, run = (record.get(k) for k in ('context', 'metrics', 'run'))
    if not isinstance(run, dict) or not isinstance(run.get('artifact'), str) or not run['artifact'].strip():
        raise ValueError(f'{path}: run.artifact must identify the measured build')
    if not isinstance(context, dict) or not REQUIRED_CONTEXT.issubset(context):
        raise ValueError(f'{path}: context must contain {sorted(REQUIRED_CONTEXT)}')
    for key, value in context.items():
        if value is None or isinstance(value, bool) or not isinstance(value, (str, int, float)):
            raise ValueError(f'{path}: context.{key} must be a scalar string/number')
        if isinstance(value, str) and not value.strip():
            raise ValueError(f'{path}: context.{key} must not be empty')
        if isinstance(value, (int, float)) and not math.isfinite(value):
            raise ValueError(f'{path}: context.{key} must be finite')
    hz = context['refresh_hz']
    if not isinstance(hz, (int, float)) or hz <= 0:
        raise ValueError(f'{path}: refresh_hz must be a positive number')
    if not isinstance(metrics, dict) or not metrics:
        raise ValueError(f'{path}: metrics must be a nonempty object')
    for name, metric in metrics.items():
        if not isinstance(metric, dict) or metric.get('direction') not in ('lower', 'higher'):
            raise ValueError(f'{path}: {name} requires direction lower or higher')
        unit = metric.get('unit')
        if not isinstance(unit, str) or not unit.strip():
            raise ValueError(f'{path}: {name} requires a nonempty unit')
        samples = metric.get('samples')
        if not isinstance(samples, list) or not samples:
            raise ValueError(f'{path}: {name} requires nonempty real samples')
        if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or x < 0 for x in samples):
            raise ValueError(f'{path}: {name} samples must be finite nonnegative numbers')
    return record


def summarize(samples):
    ordered = sorted(samples)
    return {
        'n': len(ordered),
        'median': statistics.median(ordered),
        'p95': ordered[math.ceil(.95 * len(ordered)) - 1],
        'min': ordered[0], 'max': ordered[-1],
    }


def improvement(before, after, direction):
    if before == 0:
        return None  # Percentage relative to zero is undefined.
    sign = 1 if direction == 'lower' else -1
    return sign * (before - after) / before * 100


def compare_records(baseline, candidate):
    if baseline['context'] != candidate['context']:
        keys = sorted(set(baseline['context']) | set(candidate['context']))
        differing = [k for k in keys if baseline['context'].get(k) != candidate['context'].get(k)]
        raise ValueError('Incompatible measurement context: ' + ', '.join(differing))
    if set(baseline['metrics']) != set(candidate['metrics']):
        raise ValueError('Both records must contain the same metric names')
    rows, warnings = [], []
    for name in sorted(baseline['metrics']):
        a, b = baseline['metrics'][name], candidate['metrics'][name]
        if (a['unit'], a['direction']) != (b['unit'], b['direction']):
            raise ValueError(f'{name}: unit/direction differs')
        before, after = summarize(a['samples']), summarize(b['samples'])
        if min(before['n'], after['n']) < 20:
            warnings.append(f'{name}: fewer than 20 samples; tail estimate may be unstable. A single artifact-size sample may be appropriate.')
        rows.append({
            'metric': name, 'unit': a['unit'], 'direction': a['direction'],
            'baseline': before, 'candidate': after,
            'median_delta': after['median'] - before['median'],
            'median_improvement_pct': improvement(before['median'], after['median'], a['direction']),
            'p95_delta': after['p95'] - before['p95'],
            'p95_improvement_pct': improvement(before['p95'], after['p95'], a['direction']),
        })
    return {
        'baseline_artifact': baseline['run']['artifact'],
        'candidate_artifact': candidate['run']['artifact'],
        'context': baseline['context'], 'metrics': rows,
        'warnings': warnings,
        'interpretation': 'Positive improvement percentage favors the candidate. Descriptive only; no statistical significance, causality or automatic acceptance is established. For higher-is-better metrics such as FPS, p95 is an upper tail, not the worst-performance tail.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('baseline')
    parser.add_argument('candidate')
    args = parser.parse_args()
    try:
        result = compare_records(load_record(args.baseline), load_record(args.candidate))
    except ValueError as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
