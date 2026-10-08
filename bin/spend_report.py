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

Per-job telemetry (2026-10-08): dispatch.sh truyen `--session-id` cho claude roi goi
bin/job_telemetry.py (KHONG goi file nay — spend_report o tier T2, khong nam tren duong T0) => record co num_turns/total_cost_usd/input_tokens/cache_read_tokens/
cache_creation_tokens/output_tokens/session_id. Bao cao dung no cho muc "Top chuoi ton nhat".
Job truoc 2026-10-08 va provider khac claude khong co field => khong vao bang do (dem rieng).
"""
import glob
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dispatch_loop_hint as H  # noqa: E402  — MOT dinh nghia chuoi (giong dispatch_round_cap)
import job_telemetry as JT  # noqa: E402

_ICT = ZoneInfo("Asia/Ho_Chi_Minh")


def _ict_today():
    """Ngày ICT — §16. time.gmtime() cũ cho ngày UTC: mọi lần chạy sau 17:00 ICT
    sẽ dán nhãn NGÀY HÔM TRƯỚC vào dòng CSV."""
    return datetime.now(_ICT).strftime("%Y-%m-%d")

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

RETRY_WARN_MIN_JOBS = 10
RETRY_WARN_PCT = 10

TOP_CHAINS = 15
TELEMETRY_INT_FIELDS = JT.INT_FIELDS
_to_int = JT.to_int
_to_float = JT.to_cost
# Prompt tu sinh khi chay tiep / bao ket qua 1 job khac => noi vao chuoi cua job do (N1).
_LINK_RE = re.compile(
    r"^\[(?:(RESUME sau (?:usage-limit|max-turns)|FALLBACK provider)[^\]]*job gốc=|AUTO-CALLBACK(?:-FAIL)? job=)([\w-]+)"
    r"|TIẾP TỤC (?:job|JOB) ([\w-]+)"
)


def _link_target(prompt_summary):
    m = _LINK_RE.search(prompt_summary or "")
    return (m.group(2) or m.group(3)) if m else None


def _resume_cause(ps):
    """Nguyen nhan cua 1 job CHAY TIEP job khac, hoac None. Gom ca 'TIẾP TỤC job X' (Mike go tay,
    cung dieu kien voi resume_jobs) — vi vay tong causes_resume >= resume_jobs: resume_jobs (dinh
    nghia cu, dung chung routing_retrospective.py) khong dem [RESUME sau max-turns / [FALLBACK."""
    if ps.startswith("[RESUME sau usage-limit"):
        return "usage_limited"
    if ps.startswith("[RESUME sau max-turns"):
        return "max_turns"
    if ps.startswith("[FALLBACK provider"):
        return "fallback_provider"
    if "TIẾP TỤC job" in ps or "TIẾP TỤC JOB" in ps:
        return "tiep_tuc_timeout" if "timeout" in ps.lower() else "tiep_tuc_khac"
    return None


def _parse_args(argv):
    days = 7
    csv_path = None
    root = ROOT
    i = 0
    while i < len(argv):
        if argv[i] == "--days":
            days = int(argv[i + 1])
            i += 2
        elif argv[i] == "--csv-append":
            csv_path = argv[i + 1]
            i += 2
        elif argv[i] == "--root":
            root = argv[i + 1]
            i += 2
        else:
            i += 1
    return days, csv_path, root


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
    retry_stats = {
        "attempt_counts": {},
        "retried_jobs": 0,
        "extra_attempts": 0,
        "resume_jobs": 0,
        "by_status": {},
        "causes_inloop": {},   # retry trong cung job (field retry_causes, tu 2026-10-08)
        "causes_resume": {},   # job MOI do auto-resume/fallback sinh ra
        "tele_missing": 0,
    }
    tele_jobs = []  # record co telemetry token (dispatch.sh tu 2026-10-08)
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
        status = rec.get("status") or "unknown"
        attempt = str(rec.get("attempt") or "1")
        retry_stats["attempt_counts"][attempt] = retry_stats["attempt_counts"].get(attempt, 0) + 1
        if attempt.isdigit() and int(attempt) > 1:
            retry_stats["retried_jobs"] += 1
            retry_stats["extra_attempts"] += int(attempt) - 1
            retry_stats["by_status"][status] = retry_stats["by_status"].get(status, 0) + 1
            causes = [c for c in str(rec.get("retry_causes") or "").split(",") if c]
            # attempt>1 ma khong co retry_causes = record truoc 2026-10-08: status/exit_code da
            # bi lan cuoi ghi de, khong suy lai duoc nguyen nhan => dem rieng, khong doan.
            for c in causes or ["khong_ro"] * (int(attempt) - 1):
                ci = retry_stats["causes_inloop"]
                ci[c] = ci.get(c, 0) + 1
        prompt_summary = rec.get("prompt_summary") or ""
        if (
            "TIẾP TỤC job" in prompt_summary
            or "TIẾP TỤC JOB" in prompt_summary
            or prompt_summary.startswith("[RESUME sau usage-limit")
        ):
            retry_stats["resume_jobs"] += 1
        cause = _resume_cause(prompt_summary)
        if cause:
            cr = retry_stats["causes_resume"]
            cr[cause] = cr.get(cause, 0) + 1
        if any(k in rec for k in TELEMETRY_INT_FIELDS):
            tele_jobs.append(rec)
        elif rec.get("session_id"):
            retry_stats["tele_missing"] += 1   # co --session-id nhung khong doc duoc transcript
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
    retry_stats["tele_jobs"] = tele_jobs
    return buckets, agent_effort, retry_stats


def _rec_tokens(rec):
    """Token chuoi cua 1 job — CUNG dinh nghia dispatch_round_cap (H.branch_tokens tren
    prompt_summary + chain_tokens)."""
    ps = rec.get("prompt_summary") or ""
    return H.branch_tokens(ps + " " + " ".join(str(rec.get("chain_tokens") or "").split(",")))


def _top_chains(tele_jobs, all_by_id, top=TOP_CHAINS):
    """Gom job thanh chuoi bang UNION-FIND theo TUNG token (2 job chung 1 token bat ky => cung
    chuoi; vd job A mang token worktree X, job B mang ca token nhanh Y lan X => A, B cung chuoi)
    + noi job resume/fallback/auto-callback/TIEP TUC vao job goc. Nhan chuoi = token xuat hien o
    nhieu job nhat; chuoi khong co token => 40 ky tu dau prompt.
    LUU Y: gop BAC CAU (A~B qua X, B~C qua Y => A~C) — rong hon dispatch_round_cap (dem vong theo
    tung token rieng). Job cron dinh ky khong co token thi gop theo 40 ky tu dau prompt, nen cac
    lan chay cung 1 cron se hien thanh 1 "chuoi". Telemetry chi doc transcript phien chinh, KHONG
    doc transcript subagent rieng (Agent()) => chi phi subagent khong nam trong so nay."""
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    labels = {}
    for i, rec in enumerate(tele_jobs):
        node = "job:" + str(rec.get("job_id") or f"#{i}")
        find(node)
        cur, toks, depth = rec, [], 0
        while True:
            toks += _rec_tokens(cur)
            tgt = _link_target(cur.get("prompt_summary") or "")
            if not tgt or depth >= 5:
                break
            union(node, "job:" + tgt)
            depth += 1
            cur = all_by_id.get(tgt)
            if not cur:
                labels.setdefault(node, []).append("resume:" + tgt)
                break
        for t in dict.fromkeys(toks):
            union(node, "tok:" + t)
            labels.setdefault(node, []).append(t)
        if not toks and node not in labels:
            ps = (rec.get("prompt_summary") or "")[:40].replace("\n", " ")
            union(node, "ps:" + ps)
            labels[node] = [ps]
    chains = {}
    for i, rec in enumerate(tele_jobs):
        node = "job:" + str(rec.get("job_id") or f"#{i}")
        c = chains.setdefault(find(node), {"jobs": 0, "tokens": 0, "cost": 0.0, "turns": 0,
                                            "agents": set(), "labels": {}, "no_cost": 0,
                                            "cache_read": 0})
        c["jobs"] += 1
        c["tokens"] += sum(_to_int(rec.get(k)) for k in TELEMETRY_INT_FIELDS if k != "num_turns")
        cost = _to_float(rec.get("total_cost_usd"))
        c["cost"] += cost or 0.0
        c["no_cost"] += cost is None
        c["turns"] += _to_int(rec.get("num_turns"))
        c["cache_read"] += _to_int(rec.get("cache_read_tokens"))
        c["agents"].add(rec.get("to", "?"))
        for lb in labels.get(node, []):
            c["labels"][lb] = c["labels"].get(lb, 0) + 1
    out = []
    for c in chains.values():
        lbs = c.pop("labels")
        key = max(lbs, key=lambda k: (lbs[k], k)) if lbs else "?"
        out.append((key, c))
    ranked = sorted(out, key=lambda kv: (-kv[1]["cost"], -kv[1]["tokens"]))
    return ranked[:top], len(chains)


def _jobs_by_id():
    out = {}
    for path in glob.glob(os.path.join(ROOT, "bus", "jobs", "*.json")):
        try:
            with open(path, encoding="utf-8") as f:
                rec = json.load(f)
        except Exception:
            continue
        if isinstance(rec, dict):
            out[rec.get("job_id") or os.path.basename(path)[:-5]] = rec
    return out


def _timestamp_to_epoch(value):
    if not value:
        return None
    text = value.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()


def _cache_project_dirs(since_ts):
    """Claude project dirs for fleet agents, including worktree copies if present."""
    proj_root = os.path.join(os.path.expanduser("~"), ".claude", "projects")
    if not os.path.isdir(proj_root):
        return
    agents = set(AGENT_CATEGORY) | {"Mike"}
    for name in os.listdir(proj_root):
        if not (
            name.startswith("-home-trido-thanhdt-WorkingClaude-mike-agents-")
            or name.startswith("-home-trido-mike-lite-")
        ):
            continue
        if "-agents-" in name:
            suffix = name.rsplit("-agents-", 1)[-1]
        else:
            suffix = name.rsplit("-", 1)[-1]
        if suffix not in agents:
            continue
        for tf in glob.glob(os.path.join(proj_root, name, "*.jsonl")):
            if os.path.getmtime(tf) >= since_ts - 86400:
                yield tf


def _scan_cache_usage(since_ts):
    """Read Claude transcript usage in the window and dedupe repeated usage lines."""
    totals = {"input_tokens": 0, "cache_read_tokens": 0, "cache_creation_tokens": 0, "messages": 0}
    seen = set()
    for tf in _cache_project_dirs(since_ts):
        try:
            with open(tf, encoding="utf-8") as f:
                for line in f:
                    if '"usage"' not in line:
                        continue
                    try:
                        event = json.loads(line)
                    except Exception:
                        continue
                    msg = event.get("message")
                    if not isinstance(msg, dict):
                        continue
                    usage = msg.get("usage")
                    if not isinstance(usage, dict):
                        continue
                    uid = msg.get("id") or event.get("requestId") or event.get("uuid")
                    if not uid or uid in seen:
                        continue
                    ts = _timestamp_to_epoch(event.get("timestamp"))
                    if ts is None or ts < since_ts:
                        continue
                    seen.add(uid)
                    totals["input_tokens"] += int(usage.get("input_tokens") or 0)
                    totals["cache_read_tokens"] += int(usage.get("cache_read_input_tokens") or 0)
                    totals["cache_creation_tokens"] += int(usage.get("cache_creation_input_tokens") or 0)
                    totals["messages"] += 1
        except Exception:
            continue
    prompt_tokens = (
        totals["input_tokens"] + totals["cache_read_tokens"] + totals["cache_creation_tokens"]
    )
    totals["prompt_tokens"] = prompt_tokens
    totals["hit_pct"] = 100 * totals["cache_read_tokens"] / prompt_tokens if prompt_tokens else None
    return totals


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
    days, csv_path, root = _parse_args(sys.argv[1:])
    global ROOT
    ROOT = os.path.abspath(root)
    since_ts = int(time.time()) - days * 86400

    job_buckets, agent_effort, retry_stats = _scan_jobs(since_ts)
    cache_usage = _scan_cache_usage(since_ts)
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
    # Retry / duplicate compute watch (2026-08-16) — attempt>1 records in bus/jobs/ are
    # the only stable signal that a task already consumed one run and then consumed more.
    print("Retry / duplicate compute watch:")
    attempt_str = ", ".join(
        f"attempt {k}={v}" for k, v in sorted(retry_stats["attempt_counts"].items())
    )
    print(f"  attempts: {attempt_str}")
    if retry_stats["retried_jobs"]:
        retry_pct = 100 * retry_stats["extra_attempts"] / total_jobs if total_jobs else 0
        print(
            f"  retried_jobs={retry_stats['retried_jobs']}  "
            f"extra_attempts={retry_stats['extra_attempts']}  "
            f"({retry_pct:.0f}% of jobs)"
        )
        status_str = ", ".join(
            f"{k}={v}" for k, v in sorted(retry_stats["by_status"].items())
        )
        if status_str:
            print(f"  retry status: {status_str}")
        if retry_stats["resume_jobs"]:
            print(f"  explicit resume/re-dispatch prompts: {retry_stats['resume_jobs']}")
        if (
            total_jobs >= RETRY_WARN_MIN_JOBS
            and retry_pct >= RETRY_WARN_PCT
        ):
            print(
                f"    ⚠ duplicate compute = {retry_pct:.0f}% of jobs — xem xét nguyên "
                f"nhân retry/timeout trước khi tăng throughput."
            )
    else:
        print("  no attempt>1 jobs in window")
    ci, cr = retry_stats["causes_inloop"], retry_stats["causes_resume"]
    if ci or cr:
        order = ["timeout", "usage_limited", "max_turns", "fallback_provider", "tiep_tuc_timeout",
                 "tiep_tuc_khac", "khac", "khong_ro"]
        fmt = lambda d: ", ".join(f"{k}={d[k]}" for k in order + sorted(set(d) - set(order)) if d.get(k))
        print("  retry theo nguyên nhân:")
        if ci:
            print(f"    trong cùng job (attempt>1): {fmt(ci)}")
        if cr:
            print(f"    job auto-resume/fallback mới: {fmt(cr)}")
        if ci.get("khong_ro"):
            print("    (khong_ro = record trước 2026-10-08, chưa có field retry_causes)")
    print()
    tele_jobs = retry_stats["tele_jobs"]
    print(f"Top chuỗi tốn nhất (telemetry theo job; {len(tele_jobs)}/{total_jobs} job có field):")
    # Mục mới: lỗi ở đây KHÔNG được làm mất phần còn lại (CSV row ngày hôm đó) — fail-open có báo.
    try:
        if tele_jobs:
            ranked, n_chains = _top_chains(tele_jobs, _jobs_by_id())
            tot_cost = sum(_to_float(r.get("total_cost_usd")) or 0.0 for r in tele_jobs)
            print(f"  {n_chains} chuỗi, tổng cost=${tot_cost:,.2f}; xếp theo cost rồi token "
                  f"(token = input+cache_read+cache_creation+output; cr% = phần cache_read, rẻ ~10× input; "
                  f"'*N' = N job thiếu cost ⇒ cost là CẬN DƯỚI)")
            for key, c in ranked:
                cr = 100.0 * c["cache_read"] / c["tokens"] if c["tokens"] else 0.0
                nk = f"*{c['no_cost']}" if c["no_cost"] else ""
                print(f"  ${c['cost']:8.2f}{nk:<4} tok={c['tokens']/1e6:8.2f}M cr%={cr:3.0f}  turns={c['turns']:5d}  "
                      f"jobs={c['jobs']:3d}  [{','.join(sorted(c['agents']))}] {key}")
            no_cost = sum(1 for r in tele_jobs if _to_float(r.get("total_cost_usd")) is None)
            if no_cost:
                print(f"  ({no_cost} job không có cost — phiên bị kill trước khi CLI ghi cost-state; "
                      f"chỉ token được cộng)")
        else:
            print("  chưa có job nào mang telemetry (dispatch.sh ghi từ 2026-10-08; provider khác claude không có)")
    except Exception as e:  # noqa: BLE001
        print(f"  LỖI khi dựng 'Top chuỗi tốn nhất' (bỏ qua mục này, phần còn lại vẫn chạy): {type(e).__name__}: {e}")
    if retry_stats["tele_missing"]:
        print(f"  ({retry_stats['tele_missing']} job có session_id nhưng KHÔNG có token — transcript thiếu/không đọc được)")
    print()
    print("Cache usage (Claude transcripts in agent project dirs):")
    if cache_usage["prompt_tokens"]:
        print(
            f"  prompt_tokens={cache_usage['prompt_tokens']:,}  "
            f"input={cache_usage['input_tokens']:,}  "
            f"cache_read={cache_usage['cache_read_tokens']:,}  "
            f"cache_creation={cache_usage['cache_creation_tokens']:,}"
        )
        print(
            f"  cache hit = {cache_usage['hit_pct']:.0f}% of prompt tokens "
            f"({cache_usage['messages']} assistant messages)"
        )
    else:
        print("  no transcript usage found in window")
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
                    "feat,fix,docs,chore,refactor,test,other_commits,"
                    "retried_jobs,extra_attempts,resume_jobs,cache_hit_pct\n"
                )
            f.write(
                f"{_ict_today()},{days},"
                f"{research['jobs']},{research['log_bytes']//1024},{research['duration_s']/3600:.1f},"
                f"{production['jobs']},{production['log_bytes']//1024},{production['duration_s']/3600:.1f},"
                f"{ops['jobs']},{ops['log_bytes']//1024},{ops['duration_s']/3600:.1f},"
                f"{other['jobs']},{other['log_bytes']//1024},{other['duration_s']/3600:.1f},"
                f"{total_models.get('sonnet',0)},{total_models.get('opus',0)},"
                f"{total_models.get('fable',0)},{total_models.get('default',0)},"
                f"{commit_counts.get('feat',0)},{commit_counts.get('fix',0)},"
                f"{commit_counts.get('docs',0)},{commit_counts.get('chore',0)},"
                f"{commit_counts.get('refactor',0)},{commit_counts.get('test',0)},"
                # 4 cột cuối do spend_report_weekly.py tính (retry/cache); writer nightly
                # này KHÔNG đo chúng — ghi RỖNG để giữ đúng số cột của header, thay vì
                # cắt ngắn dòng (csv.DictReader trả None => consumer int()/float() nổ).
                f"{commit_counts.get('other',0)},,,,\n"
            )
        print(f"\nAppended row to {csv_path}")


if __name__ == "__main__":
    sys.exit(main())
