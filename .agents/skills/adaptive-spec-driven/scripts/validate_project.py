#!/usr/bin/env python3
"""
validate_project.py - structural gate for the project-level files written by init.

Run as the last step of init (and after approved re-init edits). Checks
structure only; it never judges whether the architecture is right.

  ERROR  .specs/PROJECT.md, .specs/STATE.md or the architecture document missing
  ERROR  PROJECT.md without ## Overview or ## References
  ERROR  PROJECT.md does not link to the architecture document
  ERROR  STATE.md without ## Decisions or ## Handoff
  ERROR  template placeholders (<...>) left in PROJECT.md or ARCHITECTURE.md
  WARN   PROJECT.md without ## Stack or ## Quality
  WARN   a relative link in PROJECT.md that does not resolve
  WARN   ARCHITECTURE.md has Planned Architecture but no Current Architecture
  WARN   lessons store not initialized

The architecture document is ARCHITECTURE.md at the project root, or another
existing document that PROJECT.md links to with "architecture" in its path.

Usage:
  python3 <skill-dir>/scripts/validate_project.py [--root DIR] [--strict]

Exit codes: 0 pass, 1 errors (or warnings under --strict), 2 usage error.
"""

import argparse
import os
import re
import sys

import _sdd

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
FENCE_RE = re.compile(r"^(```|~~~).*?^\1", re.DOTALL | re.MULTILINE)
HTML_TAGS = {"br", "details", "summary", "img", "sub", "sup", "a", "kbd", "p", "div", "span", "b", "i", "hr"}


def placeholders(path):
    """(line, text) of template markers outside comments, fences and plain HTML tags."""
    text = _sdd.read_clean(path)
    text = FENCE_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    out = []
    for i, ln in enumerate(text.splitlines(), 1):
        bare = _sdd.CODE_SPAN_RE.sub("", ln)
        for m in _sdd.PLACEHOLDER_RE.finditer(bare):
            tag = re.match(r"^</?\s*([a-zA-Z]+)\b[^<>]*/?>$", m.group(0))
            if tag and tag.group(1).lower() in HTML_TAGS:
                continue
            out.append((i, m.group(0)))
        for span in _sdd.CODE_SPAN_RE.findall(ln):
            if re.match(r"^<[^<>]+>$", span[1:-1].strip()):
                out.append((i, span))
    return out


def local_links(lines):
    links = []
    for ln in lines:
        for target in LINK_RE.findall(ln):
            if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE) or target.startswith("#"):
                continue
            links.append(target.split("#", 1)[0])
    return [l for l in links if l]


def main(argv=None):
    p = argparse.ArgumentParser(prog="validate_project.py", description="Structural gate for init outputs.")
    p.add_argument("--root", default=".", help="project root containing .specs/")
    p.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = p.parse_args(argv)
    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        _sdd.die(f"not a directory: {root}")
    rep = _sdd.Report("validate_project")
    specs = os.path.join(root, ".specs")
    project = os.path.join(specs, "PROJECT.md")
    state = os.path.join(specs, "STATE.md")
    arch = os.path.join(root, "ARCHITECTURE.md")

    arch_doc = arch if os.path.isfile(arch) else None

    if not os.path.isfile(project):
        rep.error(".specs/PROJECT.md is missing; run init")
    else:
        lines = _sdd.read_clean(project).splitlines()
        for name in ("Overview", "References"):
            if _sdd.find_section(lines, name) is None:
                rep.error(f"PROJECT.md has no ## {name}")
        for name in ("Stack", "Quality"):
            if _sdd.find_section(lines, name) is None:
                rep.warn(f"PROJECT.md has no ## {name}")
        links = local_links(lines)
        linked_arch = False
        for target in links:
            resolved = os.path.normpath(os.path.join(specs, target))
            if not os.path.exists(resolved):
                rep.warn(f"PROJECT.md links to {target}, which does not exist")
                continue
            if "architecture" in target.lower():
                linked_arch = True
                arch_doc = arch_doc or resolved
        if not linked_arch:
            rep.error("PROJECT.md does not link to the architecture document (e.g. [ARCHITECTURE.md](../ARCHITECTURE.md))")
        for ln, ph in placeholders(project):
            rep.error(f"PROJECT.md:{ln} template placeholder {ph}")

    if arch_doc is None:
        rep.error("ARCHITECTURE.md is missing at the project root; run init")
    else:
        if arch_doc != arch:
            rep.note(f"architecture document: {os.path.relpath(arch_doc, root)}")
        alines = _sdd.read_clean(arch_doc).splitlines()
        if _sdd.find_section(alines, "Planned Architecture") and not _sdd.find_section(alines, "Current Architecture"):
            rep.warn("ARCHITECTURE.md has ## Planned Architecture without ## Current Architecture")
        if arch_doc == arch:
            for ln, ph in placeholders(arch):
                rep.error(f"ARCHITECTURE.md:{ln} template placeholder {ph}")

    if not os.path.isfile(state):
        rep.error(".specs/STATE.md is missing; run init")
    else:
        slines = _sdd.read_clean(state).splitlines()
        for name in ("Decisions", "Handoff"):
            if _sdd.find_section(slines, name) is None:
                rep.error(f"STATE.md has no ## {name}")

    if not os.path.isfile(os.path.join(specs, "lessons.json")):
        rep.warn("lessons store not initialized; run lessons.py init")

    return rep.finish(root, strict=args.strict)


if __name__ == "__main__":
    sys.exit(main())
