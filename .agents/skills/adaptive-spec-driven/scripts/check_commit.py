#!/usr/bin/env python3
"""
check_commit.py - Conventional Commits 1.0.0 check for logical-unit commits.

Reads the message from a file path (as git passes to a commit-msg hook),
--message, or stdin. Can be wired as a plain git hook:

    ln -sf <skill-dir>/scripts/check_commit.py .git/hooks/commit-msg

  ERROR  header is not 'type(scope)!: description'
  ERROR  unknown type
  ERROR  description empty, capitalized, or ending with a period
  ERROR  '!' without a 'BREAKING CHANGE:' footer
  ERROR  header and body not separated by a blank line
  WARN   header longer than 72 characters
  WARN   WIP-style message ('wip', 'fixup', 'misc changes')

Usage:
  python3 <skill-dir>/scripts/check_commit.py --message "feat(coupons): reject expired coupons"
  python3 <skill-dir>/scripts/check_commit.py .git/COMMIT_EDITMSG

Exit codes: 0 pass, 1 violation, 2 usage error.
"""

import argparse
import re
import sys

TYPES = ["feat", "fix", "refactor", "perf", "test", "docs", "build", "ci", "chore", "style", "revert"]
HEADER_RE = re.compile(r"^(?P<type>[a-z]+)(?:\((?P<scope>[^()\s][^()]*)\))?(?P<bang>!)?: (?P<desc>.+)$")
WIP_RE = re.compile(r"^(wip|fixup!|squash!|misc|changes|updates?|stuff)\b", re.IGNORECASE)


def check(message):
    errors, warnings = [], []
    lines = [ln.rstrip() for ln in message.splitlines() if not ln.lstrip().startswith("#")]
    while lines and not lines[0].strip():
        lines.pop(0)
    if not lines:
        return ["empty commit message"], warnings

    header = lines[0]
    if header.startswith("Merge ") or header.startswith('Revert "'):
        return errors, warnings  # git-generated
    if len(header) > 72:
        warnings.append(f"header is {len(header)} chars (> 72)")
    m = HEADER_RE.match(header)
    if not m:
        errors.append(f"header must be 'type(scope): description', got: {header!r}")
        return errors, warnings
    if m.group("type") not in TYPES:
        errors.append(f"type '{m.group('type')}' is not one of: {', '.join(TYPES)}")
    desc = m.group("desc").strip()
    if not desc:
        errors.append("description is empty")
    else:
        if desc[0].isupper() and not re.match(r"^[A-Z0-9_]{2,}\b", desc):
            errors.append("description should start lowercase (imperative mood: 'add', not 'Added')")
        if desc.endswith("."):
            errors.append("description should not end with a period")
        if WIP_RE.match(desc):
            warnings.append("description reads like WIP; a commit should be a finished logical unit")
    if len(lines) > 1 and lines[1].strip():
        errors.append("separate the header from the body with a blank line")
    body = "\n".join(lines[1:])
    if m.group("bang") and not re.search(r"^BREAKING[ -]CHANGE:", body, re.MULTILINE):
        errors.append("'!' marks a breaking change but there is no 'BREAKING CHANGE:' footer")
    return errors, warnings


def main(argv=None):
    p = argparse.ArgumentParser(prog="check_commit.py", description="Validate a Conventional Commits message.")
    p.add_argument("msgfile", nargs="?", help="commit message file")
    p.add_argument("--message", help="commit message text")
    args = p.parse_args(argv)
    if args.message is not None:
        msg = args.message
    elif args.msgfile:
        with open(args.msgfile, encoding="utf-8") as f:
            msg = f.read()
    elif not sys.stdin.isatty():
        msg = sys.stdin.read()
    else:
        print("check_commit: pass a message file, --message, or stdin", file=sys.stderr)
        return 2

    errors, warnings = check(msg)
    for w in warnings:
        print(f"  WARN  {w}")
    for e in errors:
        print(f"  ERROR {e}")
    if errors:
        print("check_commit: FAIL (https://www.conventionalcommits.org/en/v1.0.0/)")
        return 1
    print("check_commit: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
