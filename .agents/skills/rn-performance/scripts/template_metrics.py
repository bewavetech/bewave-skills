#!/usr/bin/env python3
"""Create a metrics JSON skeleton compatible with compare_metrics.py."""
import argparse
import json
import sys


REQUIRED_CONTEXT = [
    'platform', 'device', 'os', 'build_mode', 'scenario', 'engine',
    'architecture', 'refresh_hz', 'dataset', 'network', 'cache',
    'start_type', 'instrumentation',
]


def parse_metric(value):
    parts = value.split(':')
    if len(parts) != 3:
        raise argparse.ArgumentTypeError('metric must be name:unit:direction')
    name, unit, direction = (part.strip() for part in parts)
    if not name or not unit:
        raise argparse.ArgumentTypeError('metric name and unit must be nonempty')
    if direction not in ('lower', 'higher'):
        raise argparse.ArgumentTypeError('metric direction must be lower or higher')
    return name, {'unit': unit, 'direction': direction, 'samples': []}


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact', required=True, help='Measured build, commit, or artifact identifier')
    parser.add_argument('--trace', default='replace-with-local-trace-path')
    parser.add_argument(
        '--metric',
        action='append',
        type=parse_metric,
        required=True,
        help='Metric in name:unit:direction form, for example tti_ms:ms:lower',
    )
    for key in REQUIRED_CONTEXT:
        required = key in {'platform', 'device', 'os', 'scenario', 'engine', 'architecture'}
        parser.add_argument(f'--{key.replace("_", "-")}', required=required)
    parser.set_defaults(
        build_mode='release',
        refresh_hz='60',
        dataset='replace-with-fixture-and-volume',
        network='replace-with-network-policy',
        cache='replace-with-reset-policy',
        start_type='not-applicable',
        instrumentation='replace-with-tool-version-and-markers',
    )
    return parser


def coerce_refresh_hz(value):
    try:
        hz = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError('refresh_hz must be numeric') from exc
    if hz <= 0:
        raise argparse.ArgumentTypeError('refresh_hz must be positive')
    return int(hz) if hz.is_integer() else hz


def main():
    parser = build_parser()
    args = parser.parse_args()
    context = {}
    for key in REQUIRED_CONTEXT:
        value = getattr(args, key)
        context[key] = coerce_refresh_hz(value) if key == 'refresh_hz' else value
    metrics = {}
    for name, metric in args.metric:
        if name in metrics:
            parser.error(f'duplicate metric: {name}')
        metrics[name] = metric
    record = {
        'run': {'artifact': args.artifact, 'trace': args.trace},
        'context': context,
        'metrics': metrics,
    }
    json.dump(record, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write('\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
