#!/usr/bin/env python3
"""spend_report.py [--days N] [--csv-append PATH]

Cost-optimization #5 (2026-07-17) — repeatable ops-vs-research spend measurement.
The 4 changes made earlier today (context tiering, risk-tiered arch-review, batched
research dispatch, model-config smoke-test) were justified by a one-off manual count
(dispatch job counts by agent, commit-type breakdown) done by hand in this session.
This script turns that same measurement into something that can be re-run any time
to check whether the optimizations are actually holding, instead of trusting memory.

Measures two things over the trailing N days (default 7):
  1. Headless dispatch jobs (bus/jobs/*.json) grouped into research / production /
     ops-coordination / other, with total dispatch-log bytes per bucket as a rough
     proxy for token spend (no real per-job token count is logged anywhere).
  2. Git commits in the same window, bucketed by conventional-commit prefix
     (feat/fix/docs/chore/refactor/other) — a proxy for how much work was new
     capability vs. maintenance/fixes.

Known gap: native subagent calls (Agent(subagent_type=...) for data-ops, risk-auditor,
legal-vn, fleet-scout, quant-skeptic, bq-analyst) are NOT tracked here — they don't
create bus/jobs records, only headless dispatch.sh calls do. This undercounts total
spend but the headless dispatch path is where the 4 fixes today actually applied, so
it's the right thing to trend.

  spend_report.py                              -> human report, trailing 7 days
  spend_report.py --days 14                    -> trailing 14 days
  spend_report.py --csv-append state/spend_history.csv   -> also append one row
"""
import glob
import json
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AGENT_CATEGORY = {
    "Taylor": "research",
    "DollarBill": "production",
    "Mafee": "production",
    "Wags": "ops-coordination",
    "Winston": "ops-coordination",
    "Spyros": "ops-coordination",
    "Wendy": "ops-coordination",
}

COMMIT_PREFIXES = ["feat", "fix", "docs", "chore", "refactor", "test"]


def _parse_args(argv):
    days = 7
    csv_path = None
    i = 0
    while i < len(argv):
        if argv[i] == "--days":
            days = int(argv[i + 1])
            i += 2
        elif argv[i] == "--csv-append":
            csv_path = argv[i + 1]
            i += 2
        else:
            i += 1
    return days, csv_path


def _scan_jobs(since_ts):
    buckets = {}  # category -> {"jobs": int, "log_bytes": int, "agents": {}}
    for path in glob.glob(os.path.join(ROOT, "bus", "jobs", "*.json")):
        try:
            with open(path, encoding="utf-8") as f:
                rec = json.load(f)
        except Exception:
            continue
        started = rec.get("started_at")
        try:
            started = int(started)
        except (TypeError, ValueError):
            continue
        if started < since_ts:
            continue
        agent = rec.get("to", "?")
        cat = AGENT_CATEGORY.get(agent, "other")
        b = buckets.setdefault(cat, {"jobs": 0, "log_bytes": 0, "agents": {}})
        b["jobs"] += 1
        b["agents"][agent] = b["agents"].get(agent, 0) + 1
        logfile = rec.get("logfile")
        if logfile and os.path.isfile(logfile):
            b["log_bytes"] += os.path.getsize(logfile)
    return buckets


def _scan_commits(days):
    try:
        out = subprocess.run(
            ["git", "log", f"--since={days} days ago", "--pretty=%s"],
            cwd=ROOT, capture_output=True, text=True, timeout=10, check=True,
        ).stdout
    except Exception:
        return {}, 0
    counts = {p: 0 for p in COMMIT_PREFIXES}
    counts["other"] = 0
    total = 0
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        total += 1
        m = re.match(r"^(\w+)(\(.+\))?:", line)
        prefix = m.group(1).lower() if m else None
        if prefix in counts:
            counts[prefix] += 1
        else:
            counts["other"] += 1
    return counts, total


def main():
    days, csv_path = _parse_args(sys.argv[1:])
    since_ts = int(time.time()) - days * 86400

    job_buckets = _scan_jobs(since_ts)
    commit_counts, commit_total = _scan_commits(days)

    print(f"Spend report — trailing {days} days")
    print()
    print("Headless dispatch jobs by category (bus/jobs/, native Agent() calls NOT counted):")
    total_jobs = 0
    total_bytes = 0
    for cat in ["research", "production", "ops-coordination", "other"]:
        b = job_buckets.get(cat, {"jobs": 0, "log_bytes": 0, "agents": {}})
        total_jobs += b["jobs"]
        total_bytes += b["log_bytes"]
        agents_str = ", ".join(f"{a}={n}" for a, n in sorted(b["agents"].items()))
        print(f"  {cat:18s} jobs={b['jobs']:4d}  log_kb={b['log_bytes']//1024:6d}  ({agents_str})")
    print(f"  {'TOTAL':18s} jobs={total_jobs:4d}  log_kb={total_bytes//1024:6d}")
    print()
    print(f"Commits by type ({commit_total} total):")
    for p in COMMIT_PREFIXES + ["other"]:
        print(f"  {p:10s} {commit_counts.get(p, 0)}")

    if csv_path:
        csv_path = os.path.join(ROOT, csv_path) if not os.path.isabs(csv_path) else csv_path
        is_new = not os.path.isfile(csv_path)
        research = job_buckets.get("research", {"jobs": 0, "log_bytes": 0})
        production = job_buckets.get("production", {"jobs": 0, "log_bytes": 0})
        ops = job_buckets.get("ops-coordination", {"jobs": 0, "log_bytes": 0})
        other = job_buckets.get("other", {"jobs": 0, "log_bytes": 0})
        with open(csv_path, "a", encoding="utf-8") as f:
            if is_new:
                f.write(
                    "date,days,research_jobs,research_kb,production_jobs,production_kb,"
                    "ops_jobs,ops_kb,other_jobs,other_kb,feat,fix,docs,chore,refactor,test,other_commits\n"
                )
            f.write(
                f"{time.strftime('%Y-%m-%d', time.gmtime())},{days},"
                f"{research['jobs']},{research['log_bytes']//1024},"
                f"{production['jobs']},{production['log_bytes']//1024},"
                f"{ops['jobs']},{ops['log_bytes']//1024},"
                f"{other['jobs']},{other['log_bytes']//1024},"
                f"{commit_counts.get('feat',0)},{commit_counts.get('fix',0)},"
                f"{commit_counts.get('docs',0)},{commit_counts.get('chore',0)},"
                f"{commit_counts.get('refactor',0)},{commit_counts.get('test',0)},"
                f"{commit_counts.get('other',0)}\n"
            )
        print(f"\nAppended row to {csv_path}")


if __name__ == "__main__":
    main()
