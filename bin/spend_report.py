#!/usr/bin/env python3
"""spend_report.py [--days N] [--csv-append PATH]

Cost-optimization #5 (2026-07-17) — repeatable ops-vs-research spend measurement.

REVISED same day (model-drift incident): the original version only counted JOBS and
dispatch-log bytes per agent-category — and that metric actively hid the real problem.
Real measurement 2026-07-17: job count fell 688 -> 168 (-76%) over 3 weeks while total
wall-clock compute ROSE 12.2h -> 30.4h (+150%), because the fraction of dispatches using
the most expensive model (fable) went from 0% (no --model flag existed 3 weeks ago) to
~58% this week — mostly from Mike manually choosing fable for routine audit/fix work
that the team's own model ladder (MIKE.md §Model routing) says belongs at Opus at most.
A job-count trend alone would have shown this as "ops spend is DOWN" — completely
missing the actual cost driver. Model-mix % and total duration are now the primary
signals; job count and log-bytes are kept as secondary context.

Measures three things over the trailing N days (default 7), from bus/jobs/*.json:
  1. Job count + total duration (ended_at - started_at) per agent-category (research /
     production / ops-coordination / other) — duration is the better spend proxy;
     log-bytes is kept too but is weaker (doesn't reflect model price tier).
  2. Model mix (sonnet/opus/fable/default) per category, as a percentage — the metric
     that actually caught the 2026-07-17 incident.
  3. Git commits in the same window, bucketed by conventional-commit prefix.

Known gap: native subagent calls (Agent(subagent_type=...) for data-ops, risk-auditor,
legal-vn, fleet-scout, quant-skeptic, bq-analyst) are NOT tracked here — they don't
create bus/jobs records, only headless dispatch.sh calls do.

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


# Nhan model cua CLAUDE. Provider khac (opencode/codex/antigravity) KHONG dung nhan nay —
# xem _model_key(). Truoc 2026-08-03 moi model la khong nam trong list nay bi gan thanh
# "default", nen job opencode se bi dem lan vao claude: viec chia tai sang provider re tro
# thanh VO HINH, va ty le model-mix cua claude (chi so da bat duoc drift fable 07-17) bi loang.
MODELS = ["sonnet", "opus", "fable", "default"]
# Provider != claude duoc gom theo TEN PROVIDER, khong theo ten model, vi ten model cua ho
# (vd "opencode/deepseek-v4-flash-free") khong so sanh duoc voi tier cua claude.
PROVIDER_KEYS = ["opencode", "codex", "antigravity"]


def _model_key(rec):
    """Nhan de gom 1 job: model cua claude, hoac ten provider neu chay CLI khac."""
    provider = rec.get("provider") or "claude"
    if provider != "claude":
        return provider if provider in PROVIDER_KEYS else "other-provider"
    model = rec.get("model") or "default"
    return model if model in MODELS else "default"


def _scan_jobs(since_ts):
    buckets = {}  # category -> {"jobs", "log_bytes", "duration_s", "agents": {}, "models": {}}
    agent_effort = {}  # agent -> {effort_level: count} — drift watch, xem canh bao o main()
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
        b = buckets.setdefault(
            cat, {"jobs": 0, "log_bytes": 0, "duration_s": 0, "agents": {}, "models": {}}
        )
        b["jobs"] += 1
        b["agents"][agent] = b["agents"].get(agent, 0) + 1
        mk = _model_key(rec)
        b["models"][mk] = b["models"].get(mk, 0) + 1
        effort = rec.get("effort") or "medium"
        ae = agent_effort.setdefault(agent, {})
        ae[effort] = ae.get(effort, 0) + 1
        logfile = rec.get("logfile")
        if logfile and os.path.isfile(logfile):
            b["log_bytes"] += os.path.getsize(logfile)
        # status=orphaned: ended_at la thoi diem `jobs.sh reap` QUET DEP record (co the
        # nhieu ngay sau deadline that), KHONG phai thoi diem job that su ngung chay —
        # pid da duoc xac nhan CHET truoc do (mike_json.py cmd_job_reap). Dung nguyen
        # ended_at o day tung thoi phong compute_h len ~140h/tuan gia tao quanh
        # 2026-07-22 (mot dot mass-reap don le). Deadline la can tren hop ly hon cho
        # "job co the da chay that su lau nhat".
        end_ref = rec.get("ended_at")
        if rec.get("status") == "orphaned" and rec.get("deadline"):
            end_ref = rec.get("deadline")
        try:
            dur = int(end_ref) - started
        except (TypeError, ValueError):
            dur = 0
        if dur > 0:
            b["duration_s"] += dur
    return buckets, agent_effort


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

    job_buckets, agent_effort = _scan_jobs(since_ts)
    commit_counts, commit_total = _scan_commits(days)

    empty = {"jobs": 0, "log_bytes": 0, "duration_s": 0, "agents": {}, "models": {}}

    print(f"Spend report — trailing {days} days")
    print()
    print("Headless dispatch jobs by category (bus/jobs/, native Agent() calls NOT counted):")
    total_jobs = 0
    total_bytes = 0
    total_dur = 0
    total_models = {m: 0 for m in MODELS + PROVIDER_KEYS}
    for cat in ["research", "production", "ops-coordination", "other"]:
        b = job_buckets.get(cat, empty)
        total_jobs += b["jobs"]
        total_bytes += b["log_bytes"]
        total_dur += b["duration_s"]
        agents_str = ", ".join(f"{a}={n}" for a, n in sorted(b["agents"].items()))
        print(
            f"  {cat:18s} jobs={b['jobs']:4d}  compute_h={b['duration_s']/3600:5.1f}  "
            f"log_kb={b['log_bytes']//1024:6d}  ({agents_str})"
        )
        model_str = ", ".join(
            f"{m}={100*n/b['jobs']:.0f}%" for m, n in sorted(b["models"].items()) if b["jobs"]
        )
        if model_str:
            print(f"    model mix: {model_str}")
        for m, n in b["models"].items():
            total_models[m] = total_models.get(m, 0) + n
    print(
        f"  {'TOTAL':18s} jobs={total_jobs:4d}  compute_h={total_dur/3600:5.1f}  "
        f"log_kb={total_bytes//1024:6d}"
    )
    if total_jobs:
        overall_mix = ", ".join(
            f"{m}={100*n/total_jobs:.0f}%" for m, n in sorted(total_models.items()) if n
        )
        print(f"    overall model mix: {overall_mix}")
        claude_jobs = sum(total_models.get(m, 0) for m in MODELS)
        offload = sum(total_models.get(p, 0) for p in PROVIDER_KEYS)
        if offload:
            print(f"    offload: {offload}/{total_jobs} job ({100*offload/total_jobs:.0f}%) "
                  f"chay tren provider KHAC claude — phan nay khong tieu quota claude")
        # Mau so = job CLAUDE, khong phai tong. Neu chia mau bang total_jobs thi cang chuyen
        # tai sang opencode, fable% cang tut gia tao => canh bao tu tat, dung luc can nhat.
        fable_pct = 100 * total_models.get("fable", 0) / claude_jobs if claude_jobs else 0
        if fable_pct >= 30:
            print(
                f"    ⚠ fable = {fable_pct:.0f}% of CLAUDE dispatches — ladder policy "
                f"(MIKE.md §Model routing) says fable should be rare, reserved for "
                f"genuinely exceptional complexity, not routine audit/fix work."
            )
    print()
    # Effort-tier drift watch (2026-08-10) — same mechanism as the fable_pct check above,
    # applied to the effort axis: MIKE.md §Model routing says --effort default should be
    # medium, high only for genuinely complex tasks. Nothing watched this before; audit
    # 2026-08-10 found Taylor at 95% high with zero monitoring, the exact drift shape the
    # 2026-07-17 fable incident already taught us to catch early.
    EFFORT_WARN_PCT = 70
    EFFORT_WARN_MIN_JOBS = 10
    print("Effort-tier mix by agent (drift watch):")
    for agent in sorted(agent_effort, key=lambda a: -sum(agent_effort[a].values())):
        efforts = agent_effort[agent]
        n = sum(efforts.values())
        mix_str = ", ".join(
            f"{e}={100*c/n:.0f}%" for e, c in sorted(efforts.items(), key=lambda kv: -kv[1])
        )
        print(f"  {agent:12s} n={n:4d}  {mix_str}")
        high_pct = 100 * efforts.get("high", 0) / n if n else 0
        if n >= EFFORT_WARN_MIN_JOBS and high_pct >= EFFORT_WARN_PCT:
            print(
                f"    ⚠ effort=high = {high_pct:.0f}% of {agent}'s dispatches (n={n}) — "
                f"MIKE.md §Model routing says default should be medium, high only for "
                f"genuinely complex tasks."
            )
    print()
    print(f"Commits by type ({commit_total} total):")
    for p in COMMIT_PREFIXES + ["other"]:
        print(f"  {p:10s} {commit_counts.get(p, 0)}")

    if csv_path:
        csv_path = os.path.join(ROOT, csv_path) if not os.path.isabs(csv_path) else csv_path
        is_new = not os.path.isfile(csv_path)
        research = job_buckets.get("research", empty)
        production = job_buckets.get("production", empty)
        ops = job_buckets.get("ops-coordination", empty)
        other = job_buckets.get("other", empty)
        with open(csv_path, "a", encoding="utf-8") as f:
            if is_new:
                f.write(
                    "date,days,research_jobs,research_kb,research_h,production_jobs,production_kb,"
                    "production_h,ops_jobs,ops_kb,ops_h,other_jobs,other_kb,other_h,"
                    "sonnet_jobs,opus_jobs,fable_jobs,default_jobs,"
                    "feat,fix,docs,chore,refactor,test,other_commits\n"
                )
            f.write(
                f"{time.strftime('%Y-%m-%d', time.gmtime())},{days},"
                f"{research['jobs']},{research['log_bytes']//1024},{research['duration_s']/3600:.1f},"
                f"{production['jobs']},{production['log_bytes']//1024},{production['duration_s']/3600:.1f},"
                f"{ops['jobs']},{ops['log_bytes']//1024},{ops['duration_s']/3600:.1f},"
                f"{other['jobs']},{other['log_bytes']//1024},{other['duration_s']/3600:.1f},"
                f"{total_models.get('sonnet',0)},{total_models.get('opus',0)},"
                f"{total_models.get('fable',0)},{total_models.get('default',0)},"
                f"{commit_counts.get('feat',0)},{commit_counts.get('fix',0)},"
                f"{commit_counts.get('docs',0)},{commit_counts.get('chore',0)},"
                f"{commit_counts.get('refactor',0)},{commit_counts.get('test',0)},"
                f"{commit_counts.get('other',0)}\n"
            )
        print(f"\nAppended row to {csv_path}")


if __name__ == "__main__":
    main()
