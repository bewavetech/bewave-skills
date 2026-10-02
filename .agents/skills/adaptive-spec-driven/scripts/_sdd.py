"""
_sdd.py - shared helpers for the adaptive-spec-driven validation scripts.

Pure standard library. Imported by the sibling scripts (Python puts the
script's own directory on sys.path, so `import _sdd` works when they are
invoked as `python3 <skill-dir>/scripts/<name>.py`). Not meant to be run.

Parsing is deliberately heuristic markdown inspection keyed on the exact
headings and field labels used by the templates in assets/templates/.
"""

import os
import re
import sys

LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

FACTORS = [
    "ambiguity",
    "criticality",
    "blast_radius",
    "novelty",
    "irreversibility",
    "integrations",
    "state",
    "auth",
    "concurrency",
    "migrations",
    "security",
    "data_integrity",
]
RATINGS = ["none", "low", "medium", "high"]

# Factors whose `high` rating alone makes a change CRITICAL.
CRITICAL_ON_HIGH = {"irreversibility", "auth", "security", "data_integrity"}
# Factors whose `medium` rating alone makes a change HIGH.
HIGH_ON_MEDIUM = CRITICAL_ON_HIGH | {"migrations", "concurrency"}

TEST_ORIGINS = ["SPEC", "REGRESSION", "CONTRACT", "INVARIANT", "CHARACTERIZATION"]

PROFILES = {
    "LOW": [
        "Artifacts: inline spec + plan in chat; no .specs files",
        "Discuss: skip | Research: only if unfamiliar | Approvals: none",
        "Tests: keep suite green; REGRESSION/CHARACTERIZATION where behavior changes",
        "Discrimination: none",
        "Verification: author self-check (gate green + diff re-read)",
    ],
    "MEDIUM": [
        "Artifacts: spec.md + plan.md (lite); validation.md optional",
        "Discuss: only user-facing ambiguity | Research: when unfamiliar",
        "Approvals: one checkpoint (spec + plan together)",
        "Tests: SPEC per AC at the cheapest observing layer + REGRESSION",
        "Discrimination: 1-3 targeted mutations on new decision logic (author)",
        "Verification: author fresh-eyes pass (spec -> diff), evidence table in chat",
    ],
    "HIGH": [
        "Artifacts: full spec.md, plan.md, validation.md; context.md if discussed",
        "Discuss: gray areas + implicit dimensions | Research: mandatory for new libs/integrations",
        "Approvals: spec, then plan",
        "Design: components, data, errors, 2-3 alternatives, risks",
        "Tests: + failure/edge ACs, CONTRACT at boundaries, integration for state/external calls",
        "Discrimination: 3-5 mutations by the verifier",
        "Verification: independent verifier (fresh context); UAT if user-facing",
    ],
    "CRITICAL": [
        "Artifacts: all of HIGH + invariants (spec) + failure modes and rollback (plan)",
        "Discuss: always (invariants, failure behavior, rollback) | Research: mandatory, version-pinned",
        "Approvals: spec, plan, and each irreversible step at the moment it runs",
        "Tests: + INVARIANT (property-based where possible), failure injection, concurrency",
        "Discrimination: mutation tooling or >=5 manual, all invariant branches, zero survivors",
        "Verification: independent verifier + adversarial review + human sign-off; UAT required if user-facing",
    ],
}

ID_RE = re.compile(r"\b([A-Z][A-Z0-9]*-\d+)\b")
EVIDENCE_RE = re.compile(r"[\w./@-]+\.[A-Za-z0-9]+:\d+")
PLACEHOLDER_RE = re.compile(r"<[^<>\n]+>")
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
CODE_SPAN_RE = re.compile(r"`[^`\n]*`")


def level_index(level):
    return LEVELS.index(level) if level in LEVELS else -1


def compute_level(ratings):
    """Return (level, reasons) from a {factor: rating} mapping."""
    r = {f: (ratings.get(f) or "none").lower() for f in FACTORS}
    highs = [f for f, v in r.items() if v == "high"]
    meds = [f for f, v in r.items() if v == "medium"]
    lows = [f for f, v in r.items() if v == "low"]

    crit_hits = [f for f in highs if f in CRITICAL_ON_HIGH]
    if crit_hits:
        return "CRITICAL", [f"{f}=high" for f in crit_hits]
    if len(highs) >= 3:
        return "CRITICAL", [f"3+ factors high ({', '.join(highs)})"]
    if highs:
        return "HIGH", [f"{f}=high" for f in highs]
    sensitive = [f for f in meds if f in HIGH_ON_MEDIUM]
    if sensitive:
        return "HIGH", [f"{f}=medium" for f in sensitive]
    if len(meds) >= 3:
        return "HIGH", [f"3+ factors medium ({', '.join(meds)})"]
    if meds:
        return "MEDIUM", [f"{f}=medium" for f in meds]
    if len(lows) >= 3:
        return "MEDIUM", [f"3+ factors low ({', '.join(lows)})"]
    return "LOW", ["no factor above low" if lows else "no factor applies"]


# ----------------------------------------------------------------- markdown

def read_clean(path):
    """Read a markdown file with HTML comments removed (line count preserved)."""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    return COMMENT_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def has_placeholder(text):
    """True for template markers: <...> outside code spans, or a code span that is wholly <...>."""
    if PLACEHOLDER_RE.search(CODE_SPAN_RE.sub("", text)):
        return True
    return any(re.match(r"^<[^<>]+>$", span[1:-1].strip()) for span in CODE_SPAN_RE.findall(text))


def heading_level(line):
    m = re.match(r"^(#{1,6})\s+\S", line)
    return len(m.group(1)) if m else 0


def find_section(lines, name, level=2):
    """Return (start, end) indices of the body of `#{level} name`, or None.

    The body ends at the next heading of the same or a higher level.
    Matching is case-insensitive and ignores trailing text after the name.
    """
    pat = re.compile(r"^#{%d}\s+%s\b" % (level, re.escape(name)), re.IGNORECASE)
    for i, ln in enumerate(lines):
        if pat.match(ln.strip()):
            end = len(lines)
            for j in range(i + 1, len(lines)):
                hl = heading_level(lines[j])
                if hl and hl <= level:
                    end = j
                    break
            return (i + 1, end)
    return None


def section_lines(lines, name, level=2):
    b = find_section(lines, name, level)
    return [] if b is None else lines[b[0]:b[1]]


def table_rows(body_lines):
    """Return data rows (list of cell lists) of the first markdown table in body."""
    rows = []
    started = False
    for ln in body_lines:
        s = ln.strip()
        if s.startswith("|"):
            started = True
            if re.match(r"^\|?[\s:|-]+\|?$", s) and "-" in s:
                continue
            rows.append([c.strip() for c in s.strip("|").split("|")])
        elif started:
            break
    return rows[1:] if rows else []  # drop header


def field(lines, label):
    """Value of a `**Label**: value` line anywhere in lines, or None."""
    pat = re.compile(r"^\s*(?:[-*]\s+)?\*\*%s\*\*\s*:\s*(.*)$" % re.escape(label), re.IGNORECASE)
    for ln in lines:
        m = pat.match(ln)
        if m:
            return m.group(1).strip()
    return None


# ----------------------------------------------------------------- features

def resolve_feature_dir(target, root):
    """Resolve a feature dir from a path, a feature name, a file inside it, or auto-detect."""
    base = os.path.join(root, ".specs", "features")
    if target:
        if os.path.isfile(target):
            return os.path.dirname(os.path.abspath(target))
        if os.path.isdir(target):
            return os.path.abspath(target)
        cand = os.path.join(base, target)
        if os.path.isdir(cand):
            return cand
        die(f"feature not found: {target} (looked in {base})")
    feats = list_features(root)
    if len(feats) == 1:
        return os.path.join(base, feats[0])
    if not feats:
        die(f"no features under {base}; pass a feature path or name")
    die("multiple features found; pass one explicitly:\n  " + "\n  ".join(feats))


def list_features(root):
    base = os.path.join(root, ".specs", "features")
    if not os.path.isdir(base):
        return []
    return sorted(d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d)))


def die(msg, code=2):
    print(msg, file=sys.stderr)
    raise SystemExit(code)


# ----------------------------------------------------------------- spec

AC_LINE_RE = re.compile(r"^\s*[-*]\s+(?P<strike>~~)?\s*\*{0,2}(?P<id>[A-Z][A-Z0-9]*-\d+)\*{0,2}(?P<rest>.*)$")
AC_SECTIONS = ["Acceptance Criteria", "Failure & Edge Behavior"]


def _parse_criteria(lines, start, end, section):
    items = []
    for i in range(start, end):
        m = AC_LINE_RE.match(lines[i])
        if not m:
            continue
        rest = m.group("rest")
        tags = re.findall(r"\(\s*(?:removed by\s+)?(A-\d+)\s*\)", rest)
        text = re.sub(r"^\s*(\*\([^)]*\)\*\s*)*", "", rest)
        text = re.sub(r"^\s*[—–:-]+\s*", "", text).strip()
        removed = bool(m.group("strike")) or "removed by" in rest.lower()
        items.append({
            "id": m.group("id"),
            "text": text.strip("~ ").strip(),
            "line": i + 1,
            "section": section,
            "removed": removed,
            "amendments": tags,
        })
    return items


def parse_spec(path):
    text = read_clean(path)
    lines = text.splitlines()
    spec = {"path": path, "lines": lines}

    ra = section_lines(lines, "Risk Assessment")
    ratings, evidence, unknown = {}, {}, []
    for row in table_rows(ra):
        if len(row) < 2:
            continue
        key = row[0].strip("` *").lower()
        if key in FACTORS:
            ratings[key] = row[1].strip("` *").lower()
            evidence[key] = row[2] if len(row) > 2 else ""
        elif key:
            unknown.append(key)
    spec["ratings"] = ratings
    spec["evidence"] = evidence
    spec["unknown_factors"] = unknown

    declared = field(lines, "Declared level")
    spec["declared_raw"] = declared
    spec["declared"] = None
    if declared:
        m = re.search(r"\b(LOW|MEDIUM|HIGH|CRITICAL)\b", declared.upper())
        if m and not has_placeholder(declared):
            spec["declared"] = m.group(1)
    spec["override"] = field(lines, "Override")

    criteria = []
    for name in AC_SECTIONS:
        b = find_section(lines, name)
        if b:
            criteria += _parse_criteria(lines, b[0], b[1], name)
    spec["criteria"] = criteria

    b = find_section(lines, "Invariants")
    spec["invariants"] = _parse_criteria(lines, b[0], b[1], "Invariants") if b else []

    amendments = []
    b = find_section(lines, "Amendments")
    if b:
        cur = None
        for i in range(b[0], b[1]):
            m = re.match(r"^###\s+(A-\d+)\b", lines[i].strip())
            if m:
                cur = {"id": m.group(1), "line": i + 1, "body": []}
                amendments.append(cur)
            elif cur is not None:
                cur["body"].append(lines[i])
        for a in amendments:
            a["type"] = (field(a["body"], "Type") or "").lower()
            a["status"] = (field(a["body"], "Status") or "").lower()
    spec["amendments"] = amendments

    spec["sections"] = {
        name: find_section(lines, name) is not None
        for name in ["Problem", "Scope", "Risk Assessment", "Acceptance Criteria",
                     "Failure & Edge Behavior", "Invariants", "Assumptions & Open Questions", "Amendments"]
    }
    return spec


def active_criteria(spec):
    return [c for c in spec["criteria"] if not c["removed"]]


def spec_level(spec):
    """Effective feature level: declared, or computed when the declaration is missing."""
    if spec.get("declared"):
        return spec["declared"]
    return compute_level(spec.get("ratings", {}))[0]


# ----------------------------------------------------------------- plan

TASK_HEAD_RE = re.compile(r"^###\s+(?P<id>[TF]\d+)\s*[—–:-]\s*(?P<title>.+)$")
FIELD_RE = re.compile(r"^\s*[-*]\s+\*\*(?P<label>[^*]+)\*\*\s*:\s*(?P<value>.*)$")
STATUS_RE = re.compile(r"^\[(?P<mark>[ x~\-])\]\s*(?P<rest>.*)$", re.IGNORECASE)


def parse_plan(path):
    text = read_clean(path)
    lines = text.splitlines()
    plan = {"path": path, "lines": lines}
    plan["risk_raw"] = field(lines, "Risk")

    tasks = []
    b = find_section(lines, "Tasks")
    if b:
        cur = None
        in_tests = False
        for i in range(b[0], b[1]):
            ln = lines[i]
            m = TASK_HEAD_RE.match(ln.strip())
            if m:
                cur = {"id": m.group("id"), "title": m.group("title").strip(), "line": i + 1,
                       "fields": {}, "tests": [], "raw": []}
                tasks.append(cur)
                in_tests = False
                continue
            if cur is None:
                continue
            cur["raw"].append(ln)
            fm = FIELD_RE.match(ln)
            if fm and (len(ln) - len(ln.lstrip())) < 2:
                label = fm.group("label").strip().lower()
                cur["fields"][label] = fm.group("value").strip()
                in_tests = label == "tests"
                continue
            if in_tests:
                tm = re.match(r"^\s{2,}[-*]\s+(.*)$", ln)
                if tm:
                    cur["tests"].append({"text": tm.group(1).strip(), "line": i + 1})
                elif ln.strip():
                    in_tests = False
    plan["tasks"] = tasks

    waves = []
    for ln in section_lines(lines, "Execution Waves"):
        m = re.match(r"^\s*[-*]\s+\*{0,2}Wave\s+(\d+)\*{0,2}\s*:\s*(.*)$", ln, re.IGNORECASE)
        if not m:
            continue
        groups = []
        for grp in re.split(r"∥|\|\||,", m.group(2)):
            chain = re.findall(r"\b([TF]\d+)\b", grp)
            if chain:
                groups.append(chain)
        waves.append({"n": int(m.group(1)), "groups": groups})
    plan["waves"] = waves

    gates = {}
    for row in table_rows(section_lines(lines, "Verification Commands")):
        if row and row[0]:
            gates[row[0].strip("` *").lower()] = row[1] if len(row) > 1 else ""
    plan["gates"] = gates

    plan["deferred_text"] = "\n".join(section_lines(lines, "Deferred"))
    plan["sections"] = {
        name: find_section(lines, name) is not None
        for name in ["Approach", "Design", "Alternatives Considered", "Failure Modes",
                     "Risks & Mitigations", "Rollback", "Test Strategy", "Verification Commands",
                     "Tasks", "Execution Waves", "Deferred"]
    }
    return plan


def task_status(task):
    """Return one of pending, progress, done, dropped, invalid."""
    raw = task["fields"].get("status", "")
    m = STATUS_RE.match(raw)
    if not m:
        return "invalid"
    return {" ": "pending", "~": "progress", "x": "done", "X": "done", "-": "dropped"}[m.group("mark")]


def task_level(task, feature_level):
    raw = (task["fields"].get("risk") or "inherit").strip()
    m = re.match(r"^(LOW|MEDIUM|HIGH|CRITICAL)\b", raw.upper())
    return m.group(1) if m else feature_level


def ids_in(text):
    return ID_RE.findall(text or "")


# ----------------------------------------------------------------- output

class Report:
    def __init__(self, name):
        self.name = name
        self.errors = []
        self.warnings = []
        self.notes = []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def note(self, msg):
        self.notes.append(msg)

    def finish(self, target, strict=False):
        for n in self.notes:
            print(f"  INFO  {n}")
        for w in self.warnings:
            print(f"  WARN  {w}")
        for e in self.errors:
            print(f"  ERROR {e}")
        print(f"\n{self.name}: {len(self.errors)} error(s), {len(self.warnings)} warning(s) in {target}")
        return 1 if (self.errors or (strict and self.warnings)) else 0
