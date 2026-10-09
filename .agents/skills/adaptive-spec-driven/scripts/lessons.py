#!/usr/bin/env python3
"""
lessons.py - deterministic bookkeeping for the adaptive-spec-driven lessons layer.

The agent supplies judgment (which failure, the general rule, its grounding).
This script owns the mechanics: IDs, recurrence across distinct features,
candidate -> confirmed promotion, pruning and quarantine. Markdown rendering is on demand.

  .specs/lessons.json   canonical store (machine-owned, never hand-edit)

Commands:
  add       record a grounded lesson from a verification signal
  list      print lessons (default: confirmed) for loading at Discover/Plan
  penalize  mark a confirmed lesson as failed-when-applied (2x -> quarantined)
  prune     drop stale, uncorroborated candidates (also automatic)
  status    print counts
  init      create an empty store
  render    print the store as Markdown (--write saves .specs/LESSONS.md)
  selftest  run normalization regressions

Run with cwd at the project root, or pass --root.
Adapted from tlc-spec-driven's lessons.py (Felipe Rodrigues, CC-BY-4.0).
Exit codes: 0 ok, 1 selftest failure, 2 usage / grounding error.
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import unicodedata

STORE = os.path.join(".specs", "lessons.json")
RENDER = os.path.join(".specs", "LESSONS.md")

SIGNALS = {
    "ac_gap": "Acceptance criterion failed or had no evidence",
    "surviving_mutant": "A discrimination mutant survived (weak test)",
    "spec_precision_gap": "The spec did not define a precise outcome",
    "spec_amendment": "An approved behavior-change or risk-change amendment",
    "gate_fail": "The full gate failed at verification",
    "uat_issue": "A major or blocker UAT issue",
    "escaped_defect": "A defect found after the feature passed verification",
}
DEFAULTS = {"promote_threshold": 2, "window_days": 60, "quarantine_threshold": 2}


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_date(s):
    try:
        return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
    except (TypeError, ValueError):
        return dt.datetime.now(dt.timezone.utc)


def norm(text):
    """Dedup key: casefold, strip diacritics, keep alphanumerics of any script."""
    t = unicodedata.normalize("NFD", text.casefold())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = "".join(c if (c.isalnum() or c.isspace()) else " " for c in t)
    return re.sub(r"\s+", " ", t).strip()


def load(root):
    path = os.path.join(root, STORE)
    if not os.path.exists(path):
        return dict(DEFAULTS, schema=1, next_id=1, lessons=[])
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for k, v in DEFAULTS.items():
        data.setdefault(k, v)
    data.setdefault("next_id", 1)
    data.setdefault("lessons", [])
    return data


def save(root, data):
    os.makedirs(os.path.join(root, ".specs"), exist_ok=True)
    with open(os.path.join(root, STORE), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def prune(data):
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=data["window_days"])
    kept, dropped = [], []
    for l in data["lessons"]:
        stale = l["status"] == "candidate" and parse_date(l.get("last_seen")) < cutoff
        (dropped if stale else kept).append(l)
    data["lessons"] = kept
    return [l["id"] for l in dropped]


def render(data):
    out = [
        "# LESSONS",
        "",
        "> Rendered by `scripts/lessons.py render`. Do not edit; canonical state: `.specs/lessons.json`.",
        f"> promote after {data['promote_threshold']} distinct features · candidates expire after "
        f"{data['window_days']} days · quarantine after {data['quarantine_threshold']} penalties",
        "",
    ]
    groups = [
        ("confirmed", "Confirmed: load at Discover and Plan"),
        ("candidate", "Candidates: tracked, not trusted yet"),
        ("quarantined", "Quarantined: failed when applied, ignore"),
    ]
    for status, title in groups:
        items = sorted((l for l in data["lessons"] if l["status"] == status), key=lambda l: l["id"])
        out += [f"## {title}", ""]
        if not items:
            out += ["_none_", ""]
        for l in items:
            scope = f" · scope `{l['scope']}`" if l.get("scope") else ""
            out.append(f"### {l['id']}: {l['text']}")
            out.append(f"- signal `{l['signal']}` · seen in {l['recurrence']} feature(s){scope} · penalties {l.get('harmful', 0)}")
            out.append(f"- features: {', '.join(l['features'])}")
            ev = l.get("evidence", [])
            if ev:
                out.append(f"- evidence: {ev[-1]}" + (f" (+{len(ev) - 1} more)" if len(ev) > 1 else ""))
            out.append("")
    return "\n".join(out).rstrip() + "\n"


def cmd_add(root, a):
    feature, source, text = a.feature.strip(), a.source.strip(), a.text.strip()
    if not feature:
        return fail("--feature is required")
    if not source:
        return fail("--source is required (file:line, AC id, mutation id or amendment id). "
                    "A lesson without grounding in a verification signal is an opinion; refused.")
    if len(text) < 12:
        return fail("--text is too short; state the general rule in one sentence")
    data = load(root)
    prune(data)
    key = f"{a.signal}::{norm(text)}"
    ev = f"{feature}: {source}"
    hit = next((l for l in data["lessons"] if l["key"] == key), None)
    if hit:
        if feature not in hit["features"]:
            hit["features"].append(feature)
        hit["recurrence"] = len(hit["features"])
        hit["last_seen"] = now()
        if ev not in hit["evidence"]:
            hit["evidence"].append(ev)
        promoted = hit["status"] == "candidate" and hit["recurrence"] >= data["promote_threshold"]
        if promoted:
            hit["status"] = "confirmed"
        save(root, data)
        print(f"UPDATED {hit['id']} (recurrence={hit['recurrence']}, status={hit['status']})"
              + (" - promoted to confirmed" if promoted else ""))
        return 0
    lid = f"L-{data['next_id']:03d}"
    data["next_id"] += 1
    data["lessons"].append({
        "id": lid, "key": key, "text": text, "signal": a.signal, "scope": a.scope.strip(),
        "status": "candidate", "features": [feature], "recurrence": 1, "harmful": 0,
        "evidence": [ev], "created": now(), "last_seen": now(),
    })
    save(root, data)
    print(f"ADDED {lid} (candidate)")
    return 0


def cmd_list(root, a):
    data = load(root)
    if prune(data):
        save(root, data)
    q, scope = a.query.lower().strip(), a.scope.lower().strip()
    rows = [l for l in data["lessons"]
            if (a.status == "all" or l["status"] == a.status)
            and (not q or q in l["text"].lower())
            and (not scope or scope in l.get("scope", "").lower())]
    if not rows:
        print(f"(no {a.status} lessons)")
    for l in sorted(rows, key=lambda l: l["id"]):
        sc = f" [{l['scope']}]" if l.get("scope") else ""
        print(f"{l['id']} ({l['status']}, x{l['recurrence']}){sc}: {l['text']}")
    return 0


def cmd_penalize(root, a):
    data = load(root)
    hit = next((l for l in data["lessons"] if l["id"].lower() == a.id.lower()), None)
    if not hit:
        return fail(f"no lesson {a.id}")
    hit["harmful"] = hit.get("harmful", 0) + 1
    hit["last_seen"] = now()
    if hit["harmful"] >= data["quarantine_threshold"]:
        hit["status"] = "quarantined"
    save(root, data)
    print(f"PENALIZED {hit['id']} (penalties={hit['harmful']}, status={hit['status']})")
    return 0


def cmd_prune(root, a):
    data = load(root)
    dropped = prune(data)
    save(root, data)
    print(f"pruned {len(dropped)} stale candidate(s)" + (f": {', '.join(dropped)}" if dropped else ""))
    return 0


def cmd_status(root, a):
    data = load(root)
    c = {s: sum(1 for l in data["lessons"] if l["status"] == s) for s in ("confirmed", "candidate", "quarantined")}
    print(f"lessons: {len(data['lessons'])} | confirmed={c['confirmed']} candidate={c['candidate']} quarantined={c['quarantined']}")
    return 0


def cmd_init(root, a):
    save(root, load(root))
    print(f"initialized {os.path.join(root, STORE)}")
    return 0


def cmd_render(root, a):
    text = render(load(root))
    if a.write:
        with open(os.path.join(root, RENDER), "w", encoding="utf-8") as f:
            f.write(text)
        print(f"wrote {os.path.join(root, RENDER)}")
    else:
        print(text, end="")
    return 0


def cmd_selftest(root, a):
    checks = [
        (norm("Não use datas locais") == norm("Nao use datas locais") == "nao use datas locais", "pt diacritics"),
        (norm("café") == "cafe", "accent strip"),
        (norm("日本語の文です") != "" and norm("日本語の文です") != norm("別の日本語文"), "non-latin text kept distinct"),
        (norm("Assert the exact status!") == norm("assert the exact   status"), "punctuation and spacing"),
    ]
    bad = [name for ok, name in checks if not ok]
    for name in bad:
        print(f"FAIL: {name}", file=sys.stderr)
    print("selftest: ok" if not bad else "selftest: failed")
    return 1 if bad else 0


def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    return 2


def main(argv=None):
    p = argparse.ArgumentParser(prog="lessons.py", description="Lessons bookkeeping for adaptive-spec-driven.")
    p.add_argument("--root", default=".", help="project root containing .specs/")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("add")
    s.add_argument("--feature", required=True)
    s.add_argument("--signal", required=True, choices=sorted(SIGNALS))
    s.add_argument("--source", required=True)
    s.add_argument("--text", required=True)
    s.add_argument("--scope", default="")
    s.set_defaults(fn=cmd_add)

    s = sub.add_parser("list")
    s.add_argument("--status", default="confirmed", choices=["confirmed", "candidate", "quarantined", "all"])
    s.add_argument("--query", default="")
    s.add_argument("--scope", default="")
    s.set_defaults(fn=cmd_list)

    s = sub.add_parser("penalize")
    s.add_argument("--id", required=True)
    s.set_defaults(fn=cmd_penalize)

    s = sub.add_parser("render")
    s.add_argument("--write", action="store_true", help="save to .specs/LESSONS.md instead of printing")
    s.set_defaults(fn=cmd_render)

    for name, fn in (("prune", cmd_prune), ("status", cmd_status), ("init", cmd_init), ("selftest", cmd_selftest)):
        sub.add_parser(name).set_defaults(fn=fn)

    a = p.parse_args(argv)
    return a.fn(os.path.abspath(a.root), a)


if __name__ == "__main__":
    sys.exit(main())
