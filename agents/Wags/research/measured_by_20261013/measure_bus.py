#!/usr/bin/env python3
"""Chạy luật bin/finding_measured_by.py lên finding THẬT của bus (chỉ đọc).

    python3 agents/Wags/research/measured_by_20261013/measure_bus.py \
        --bus /home/trido/thanhdt/WorkingClaude/mike/bus --since 2026-09-29 --until 2026-10-13 [--sample 24]
"""
import argparse, collections, glob, json, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "bin"))
import finding_measured_by as fmb  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--bus", required=True)
ap.add_argument("--since", required=True)
ap.add_argument("--until", required=True)
ap.add_argument("--sample", type=int, default=0)
ap.add_argument("--topics", nargs="*", default=[])
a = ap.parse_args()

rows = []
for f in sorted(glob.glob(os.path.join(a.bus, "inbox", "*.jsonl"))):
    for l in open(f, encoding="utf-8", errors="replace"):
        try:
            e = json.loads(l)
        except ValueError:
            continue
        if a.since <= e.get("ts", "")[:10] <= a.until:
            rows.append(e)
rows.sort(key=lambda e: (e["ts"], e.get("event_id", "")))
fnd = [e for e in rows if e.get("event_type") == "finding"]
warn = [e for e in fnd if fmb.verdict(e)]
print("events_all=%d findings=%d dict_payload=%d would_warn=%d (%.1f%%) has_measured_by=%d" % (
    len(rows), len(fnd), sum(isinstance(e["payload"], dict) for e in fnd), len(warn),
    100.0 * len(warn) / max(1, len(fnd)),
    sum(isinstance(e["payload"], dict) and fmb.has_measured_by(e["payload"]) for e in fnd)))
print("non_finding_flagged=%d (phải = 0)" % sum(bool(fmb.verdict(e)) for e in rows if e.get("event_type") != "finding"))
print("would_warn theo agent:", collections.Counter(e["agent_id"] for e in warn).most_common())
print("would_warn KHÔNG trace_id (script/cron):", sum(not e.get("trace_id") for e in warn),
      collections.Counter(re.sub(r"\d{4}-\d{2}-\d{2}", "D", e["topic"]) for e in warn if not e.get("trace_id")).most_common(6))
print("finding KHÔNG bị cảnh báo:", [(e["agent_id"], e["topic"][:60]) for e in fnd if not fmb.verdict(e)])
for t in a.topics:
    for e in rows:
        if e["topic"] == t:
            print("CA %s | %s | type=%s | warn=%s" % (e["ts"], t, e["event_type"], fmb.verdict(e)))
if a.sample:
    random.seed(20261013)
    for i, e in enumerate(random.sample(warn, a.sample)):
        print("\n[%d] %s %s | %s | trace=%s | %s" % (i, e["ts"][:16], e["agent_id"], e["topic"][:70],
              bool(e.get("trace_id")), fmb.number_tokens(e["payload"], 12)))
        print("    " + json.dumps(e["payload"], ensure_ascii=False)[:260])
