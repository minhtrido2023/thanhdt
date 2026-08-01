#!/usr/bin/env python3
"""cron_health_check.py — deterministic audit of EVERY crontab entry: does it have a log
target at all, when did it last actually write, and does that recent output contain a
crash signature? Built 2026-08-01 (user mandate) after finding kb_nightly.sh's Friday/
Saturday dispatch had been silently failing for 2 weeks, and daily_retro.sh for 2 nights
straight — both invisible because "the cron fired" was mistaken for "the job worked".

This is the standing mechanism the user asked for: "cái gì đã lên lịch chạy phải có một
nơi để review lại". Wired into weekly_ops_audit.sh (replaces the ad-hoc log-grep
instruction in item 1) and runnable standalone any time: `python3 bin/cron_health_check.py`.

Not a full cron-semantics parser — good enough for triage, not a scheduler simulator:
  - Classifies each entry into a rough cadence bucket (frequent/daily/weekly/monthly) from
    its 5 schedule fields, to pick a "how stale is too stale" threshold.
  - Jobs with a literal `>> logfile 2>&1` redirect: check that file's mtime + tail for
    crash signatures.
  - Jobs whose log path embeds `$(date ...)` (e.g. run_bot_SpaceX_$(date +%Y-%m-%d).log):
    glob for the pattern instead of a literal path.
  - Jobs with NO explicit log redirect: flagged separately (NO_LOG) — cron's default
    behavior (mail via local MTA) silently discards output if no MTA is configured, which
    is exactly the "silently running, silently failing" shape the user is worried about.
"""
import glob
import os
import re
import subprocess
import sys
import time

ROOT = "/home/trido/thanhdt/WorkingClaude/mike"
NOW = time.time()

ERROR_PATTERNS = [
    r"Traceback \(most recent call last\)",
    r": line \d+: .+: (No such file or directory|Permission denied|command not found|unbound variable)",
    r"syntax error",
    r"ERROR: unknown argument",
    r"Errno \d+",
    r"CRITICAL",
    r"FATAL",
    r"Exception:",
    r"^\s*Error:",
]
ERROR_RE = re.compile("|".join(ERROR_PATTERNS), re.MULTILINE)

# Known-benign lines that match the crude patterns above but are NOT real failures —
# add here instead of loosening the real patterns (keeps signal tight).
BENIGN_SUBSTR = [
    "PASS] A1 consolidate.sh runs without error",  # selfcheck harness deliberately triggers this
    "PASS] C1 consolidate.sh runs without error",
]


def parse_crontab():
    out = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
    jobs = []
    for line in out.splitlines():
        line = line.rstrip()
        if not line or line.startswith("#") or "=" in line.split()[0:1][0] and not line[0].isdigit() and line[0] not in "*@":
            continue
        if line.startswith("PATH="):
            continue
        comment = ""
        if "#" in line:
            code, comment = line.split("#", 1)
        else:
            code = line
        code = code.strip()
        m = re.match(r"^(@\w+|\S+\s+\S+\s+\S+\s+\S+\s+\S+)\s+(.*)$", code)
        if not m:
            continue
        schedule, cmd = m.group(1), m.group(2).strip()
        if not cmd:
            continue
        jobs.append({"schedule": schedule, "cmd": cmd, "comment": comment.strip()})
    return jobs


def cadence_bucket(schedule):
    if schedule.startswith("@reboot"):
        return "reboot", None
    parts = schedule.split()
    if len(parts) != 5:
        return "unknown", 3 * 86400
    minute, hour, dom, month, dow = parts
    if minute.startswith("*/") or hour == "*":
        return "frequent", 2 * 3600
    if dom != "*" or month != "*":
        return "monthly", 33 * 86400
    if dow != "*":
        return "weekly", 8 * 86400
    return "daily", 3 * 86400  # 3d buffer covers Fri->Mon weekday-only jobs


def extract_log_target(cmd):
    # Path can contain a `$(...)` command substitution with embedded spaces (e.g.
    # run_bot_SpaceX_$(date +\%Y-\%m-\%d).log) — one shell "word" despite the spaces.
    m = re.search(r">>\s*((?:\$\([^)]*\)|\S)+)\s+2>&1", cmd)
    if not m:
        return None
    return m.group(1)


def resolve_log_paths(path):
    if "$(date" in path or "%Y" in path:
        # dynamic filename (e.g. run_bot_SpaceX_$(date +%Y-%m-%d).log) -> glob the stem
        stem = re.split(r"\$\(", path)[0]
        pattern = stem + "*"
        matches = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
        return matches[:1]
    return [path] if os.path.exists(path) else []


DATE_RE = re.compile(r"(20\d\d-\d\d-\d\d)")
RECENT_DAYS = 10  # a hit whose nearest surrounding datestamp is older than this = historical noise


def scan_errors(path, since_ts):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception as e:
        return [f"(không đọc được log: {e})"]
    # only look at the tail — bound cost on multi-MB logs
    tail = content[-200_000:]
    lines = tail.splitlines()
    cutoff = time.strftime("%Y-%m-%d", time.gmtime(NOW - RECENT_DAYS * 86400))
    last_date = None
    hits = []
    for line in lines:
        dm = DATE_RE.search(line)
        if dm:
            last_date = dm.group(1)
        if ERROR_RE.search(line) and not any(b in line for b in BENIGN_SUBSTR):
            # skip if we have a nearby datestamp and it's older than the recency window —
            # avoids resurfacing e.g. a 15-day-old transient timeout that self-retried OK
            if last_date is not None and last_date < cutoff:
                continue
            hits.append(line.strip()[:200])
    # dedup, keep last 5
    seen = []
    for h in reversed(hits):
        if h not in seen:
            seen.append(h)
        if len(seen) >= 5:
            break
    return list(reversed(seen))


def main():
    jobs = parse_crontab()
    rows = []
    for j in jobs:
        bucket, max_age = cadence_bucket(j["schedule"])
        if bucket == "reboot":
            continue
        log_target = extract_log_target(j["cmd"])
        script_m = re.search(r"(/\S+\.(?:sh|py))", j["cmd"])
        script = script_m.group(1) if script_m else j["cmd"][:60]
        if log_target is None:
            rows.append({
                "script": script, "schedule": j["schedule"], "bucket": bucket,
                "status": "NO_LOG_REDIRECT",
                "detail": "Không có `>> logfile 2>&1` — output đi vào cron mail mặc định "
                          "(im lặng mất nếu không có MTA cấu hình), không thể verify freshness/lỗi.",
            })
            continue
        paths = resolve_log_paths(log_target)
        if not paths:
            rows.append({
                "script": script, "schedule": j["schedule"], "bucket": bucket,
                "status": "LOG_MISSING",
                "detail": f"Log target khai báo ({log_target}) nhưng không tìm thấy file nào khớp.",
            })
            continue
        p = paths[0]
        age_s = NOW - os.path.getmtime(p)
        age_days = age_s / 86400
        errs = scan_errors(p, NOW - 7 * 86400)
        if age_s > max_age:
            rows.append({
                "script": script, "schedule": j["schedule"], "bucket": bucket,
                "status": "STALE",
                "detail": f"Log {os.path.basename(p)} không đổi {age_days:.1f} ngày (ngưỡng {bucket}={max_age/86400:.1f}d).",
            })
        elif errs:
            rows.append({
                "script": script, "schedule": j["schedule"], "bucket": bucket,
                "status": "ERRORS_FOUND",
                "detail": f"{len(errs)} dòng lỗi gần nhất trong {os.path.basename(p)}: " + " | ".join(errs),
            })
        else:
            rows.append({
                "script": script, "schedule": j["schedule"], "bucket": bucket,
                "status": "OK",
                "detail": f"{os.path.basename(p)} tươi ({age_days:.1f}d), 0 dấu hiệu lỗi trong tail.",
            })

    bad = [r for r in rows if r["status"] != "OK"]
    print(f"cron_health_check — {len(rows)} job có log target, {len(bad)} cần chú ý\n")
    for status in ("ERRORS_FOUND", "STALE", "LOG_MISSING", "NO_LOG_REDIRECT"):
        grp = [r for r in rows if r["status"] == status]
        if not grp:
            continue
        print(f"=== {status} ({len(grp)}) ===")
        for r in grp:
            print(f"  [{r['schedule']}] {r['script']}")
            print(f"    {r['detail']}")
        print()
    ok = [r for r in rows if r["status"] == "OK"]
    print(f"=== OK ({len(ok)}) ===")
    for r in ok:
        print(f"  [{r['schedule']}] {r['script']} — {r['detail']}")

    if "--bus" in sys.argv:
        sys.path.insert(0, ROOT)
        summary = {"total": len(rows), "ok": len(ok), "bad": len(bad),
                   "by_status": {s: len([r for r in rows if r["status"] == s])
                                 for s in ("ERRORS_FOUND", "STALE", "LOG_MISSING", "NO_LOG_REDIRECT")}}
        import json
        subprocess.run([os.path.join(ROOT, "bin", "append_event.sh"), "Mike", "finding",
                         "cron-health-check", json.dumps(summary, ensure_ascii=False)])

    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
