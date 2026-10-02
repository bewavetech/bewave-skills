#!/usr/bin/env python3
"""
risk.py - deterministic risk classification for adaptive-spec-driven.

Applies the rules in references/risk.md to twelve factor ratings and prints
the resulting level, the rules that fired, and the rigor profile to apply.

Usage:
  python3 <skill-dir>/scripts/risk.py --set migrations=medium state=low ...
  python3 <skill-dir>/scripts/risk.py --spec .specs/features/<feature>/spec.md
  python3 <skill-dir>/scripts/risk.py --profile HIGH
  python3 <skill-dir>/scripts/risk.py --factors          # list factor keys
  add --json for machine-readable output.

Ratings: none | low | medium | high. Unlisted factors count as none.
Exit codes: 0 ok, 2 usage error.
"""

import argparse
import json
import os
import sys

import _sdd


def main(argv=None):
    p = argparse.ArgumentParser(prog="risk.py", description="Compute the risk level and rigor profile.")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--set", nargs="+", metavar="FACTOR=RATING", help="factor ratings")
    src.add_argument("--spec", help="read ratings from a spec.md Risk Assessment table")
    src.add_argument("--profile", choices=_sdd.LEVELS, help="print the rigor profile for a level")
    src.add_argument("--factors", action="store_true", help="list factor keys and ratings")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    if args.factors:
        print("factors: " + ", ".join(_sdd.FACTORS))
        print("ratings: " + ", ".join(_sdd.RATINGS))
        return 0

    if args.profile:
        level, reasons, ratings = args.profile, ["requested"], {}
    else:
        if args.set:
            ratings = {}
            for item in args.set:
                if "=" not in item:
                    _sdd.die(f"risk.py: expected FACTOR=RATING, got '{item}'")
                k, v = (s.strip().lower() for s in item.split("=", 1))
                if k not in _sdd.FACTORS:
                    _sdd.die(f"risk.py: unknown factor '{k}'. Known: {', '.join(_sdd.FACTORS)}")
                if v not in _sdd.RATINGS:
                    _sdd.die(f"risk.py: rating for {k} must be one of {', '.join(_sdd.RATINGS)}")
                ratings[k] = v
        else:
            if not os.path.isfile(args.spec):
                _sdd.die(f"risk.py: spec not found: {args.spec}")
            spec = _sdd.parse_spec(args.spec)
            ratings = spec["ratings"]
            bad = {k: v for k, v in ratings.items() if v not in _sdd.RATINGS}
            if bad:
                _sdd.die(f"risk.py: invalid ratings in spec: {bad}")
        level, reasons = _sdd.compute_level(ratings)

    if args.json:
        print(json.dumps({"level": level, "reasons": reasons, "ratings": ratings,
                          "profile": _sdd.PROFILES[level]}, indent=2))
        return 0

    print(f"Risk: {level}  ({'; '.join(reasons)})")
    rated = {k: v for k, v in ratings.items() if v != "none"}
    if rated:
        print("Rated: " + ", ".join(f"{k}={v}" for k, v in rated.items()))
    print("\nRigor profile:")
    for line in _sdd.PROFILES[level]:
        print(f"  - {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
