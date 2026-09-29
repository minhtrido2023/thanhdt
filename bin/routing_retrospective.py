#!/usr/bin/env python3
"""routing_retrospective.py [--days N]

Weekly routing quality retrospective for Mike's dispatch decisions.
Produces actionable routing signals — meant to be read by Mike in the Friday
KB editorial review (kb_nightly.sh step 5e) and fed back into MIKE.md routing
rules when drift is confirmed.

Signals computed (per-agent, trailing N days from bus/jobs/):
  1. Success rate  (status=done vs failed/timeout/cancelled)
  2. Short-duration high-effort rate (effort=high AND duration<60s → over-spec'd)
  3. Re-dispatch rate  (attempt>1 on same job)
  4. Fast-fail rate  (done but duration<30s — possible trivial task mis-routed to heavy agent)

Outputs:
  - Summary table per agent
  - Flagged anomalies with concrete threshold breach
  - Specific routing rule candidates (what to consider changing)

Limitations:
  - Native Agent() calls not tracked (only headless dispatch.sh jobs visible)
  - "Wrong routing" is proxied by retries + failures; direct correctness not observable
  - N is small (~30-70 jobs/week); interpret as signal, not statistics
"""

import glob
import json
import os
import sys
import time
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Thresholds
FAIL_RATE_WARN = 0.20       # >20% failure rate = routing suspect
HIGH_SHORT_WARN = 0.25      # >25% of high-effort jobs complete in <60s = over-spec'd
RETRY_RATE_WARN = 0.15      # >15% retry rate = routing/prompt suspect
MIN_JOBS_FOR_SIGNAL = 5     # suppress warnings for agents with <5 jobs (too noisy)
SHORT_DUR_SECS = 60         # duration threshold for "effort=high but fast" flag
FAST_FAIL_SECS = 30         # duration threshold for "done but suspiciously fast"


def _parse_args(argv):
    days = 7
    i = 0
    while i < len(argv):
        if argv[i] == "--days":
            days = int(argv[i + 1])
            i += 2
        else:
            i += 1
    return days


def _scan(since_ts):
    """Scan bus/jobs/*.json and compute per-agent routing signals."""
    agents = {}  # agent_id -> dict of counters

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

        agent = rec.get("to") or "unknown"
        status = rec.get("status") or "unknown"
        effort = rec.get("effort") or "medium"
        attempt = str(rec.get("attempt") or "1")
        model = rec.get("model") or "default"

        ended = rec.get("ended_at")
        if status == "orphaned" and rec.get("deadline"):
            ended = rec.get("deadline")
        try:
            dur = int(ended) - started
        except (TypeError, ValueError):
            dur = None

        a = agents.setdefault(agent, {
            "total": 0,
            "done": 0,
            "failed": 0,      # includes timeout, cancelled, orphaned
            "retried": 0,     # attempt > 1
            "high_total": 0,
            "high_short": 0,  # effort=high AND duration<SHORT_DUR_SECS
            "fast_done": 0,   # done AND duration<FAST_FAIL_SECS
            "models": {},
            "efforts": {},
            "dur_sum": 0,
            "dur_count": 0,
        })
        a["total"] += 1
        a["models"][model] = a["models"].get(model, 0) + 1
        a["efforts"][effort] = a["efforts"].get(effort, 0) + 1

        terminal_ok = {"done"}
        terminal_bad = {"failed", "timeout", "cancelled", "orphaned"}
        if status in terminal_ok:
            a["done"] += 1
        elif status in terminal_bad:
            a["failed"] += 1

        # Count retries, but exclude auto-resume jobs (usage-limit/max-turns resumes
        # show attempt>1 but are infrastructure events, not routing failures).
        prompt_summary = rec.get("prompt_summary") or ""
        is_auto_resume = (
            "TIẾP TỤC job" in prompt_summary
            or "TIẾP TỤC JOB" in prompt_summary
            or prompt_summary.startswith("[RESUME sau usage-limit")
        )
        if attempt.isdigit() and int(attempt) > 1 and not is_auto_resume:
            a["retried"] += 1

        if dur is not None and dur > 0:
            a["dur_sum"] += dur
            a["dur_count"] += 1
            if effort == "high":
                a["high_total"] += 1
                if dur < SHORT_DUR_SECS:
                    a["high_short"] += 1
            if status == "done" and dur < FAST_FAIL_SECS:
                a["fast_done"] += 1

    return agents


def _pct(num, denom):
    if not denom:
        return 0.0
    return 100.0 * num / denom


def _dur_str(secs):
    if secs < 60:
        return f"{secs:.0f}s"
    return f"{secs/60:.1f}m"


def main():
    days = _parse_args(sys.argv[1:])
    since_ts = time.time() - days * 86400
    agents = _scan(since_ts)

    since_dt = datetime.fromtimestamp(since_ts, tz=timezone.utc).strftime("%Y-%m-%d")
    print(f"Routing Retrospective — trailing {days} days (since {since_dt})")
    print(f"Source: bus/jobs/*.json  |  Native Agent() calls NOT included\n")

    if not agents:
        print("No jobs found in window.")
        return

    # Sort by total jobs descending
    sorted_agents = sorted(agents.items(), key=lambda kv: kv[1]["total"], reverse=True)

    # ── Summary table ──
    print(f"{'Agent':<14} {'Jobs':>5} {'Done%':>6} {'Fail%':>6} {'Retry%':>7} {'EffortH%':>9} {'AvgDur':>7}  Models")
    print("-" * 80)
    for agent, a in sorted_agents:
        total = a["total"]
        done_pct = _pct(a["done"], total)
        fail_pct = _pct(a["failed"], total)
        retry_pct = _pct(a["retried"], total)
        high_pct = _pct(a["efforts"].get("high", 0), total)
        avg_dur = a["dur_sum"] / a["dur_count"] if a["dur_count"] else 0
        model_str = "/".join(
            f"{m}={n}" for m, n in sorted(a["models"].items(), key=lambda x: -x[1])
        )
        print(f"{agent:<14} {total:>5} {done_pct:>5.0f}% {fail_pct:>5.0f}% {retry_pct:>6.0f}% {high_pct:>8.0f}%  {_dur_str(avg_dur):>6}  {model_str}")

    # ── Flagged anomalies ──
    flags = []
    for agent, a in sorted_agents:
        total = a["total"]
        if total < MIN_JOBS_FOR_SIGNAL:
            continue

        done_terminal = a["done"] + a["failed"]
        fail_rate = a["failed"] / done_terminal if done_terminal else 0
        retry_rate = a["retried"] / total
        high_short_rate = a["high_short"] / a["high_total"] if a["high_total"] >= 3 else 0
        high_pct = a["efforts"].get("high", 0) / total

        if fail_rate > FAIL_RATE_WARN:
            flags.append((
                "FAIL-RATE", agent,
                f"{_pct(a['failed'], done_terminal):.0f}% failure ({a['failed']}/{done_terminal} terminal jobs) "
                f"— investigate: wrong agent? prompt too vague? task type not suited?"
            ))

        if retry_rate > RETRY_RATE_WARN:
            flags.append((
                "RETRY-RATE", agent,
                f"{_pct(a['retried'], total):.0f}% retried ({a['retried']}/{total} jobs) "
                f"— prompt quality or task scope mismatch?"
            ))

        if high_short_rate > HIGH_SHORT_WARN and a["high_total"] >= 3:
            flags.append((
                "OVERSPEC", agent,
                f"{_pct(a['high_short'], a['high_total']):.0f}% of effort=high jobs finished <{SHORT_DUR_SECS}s "
                f"({a['high_short']}/{a['high_total']}) — these are likely mechanical tasks; "
                f"consider effort=medium as default for this agent"
            ))

        # Warning if high% is extreme AND fails are also high (synergy signal)
        if high_pct > 0.7 and fail_rate > 0.1 and total >= 10:
            flags.append((
                "HIGH+FAIL", agent,
                f"effort=high {_pct(a['efforts'].get('high',0), total):.0f}% AND fail {_pct(a['failed'], done_terminal):.0f}% — "
                f"over-specifying effort does not improve success rate here"
            ))

    print()
    if flags:
        print("── Flagged anomalies ──")
        for flag_type, agent, msg in flags:
            print(f"  [{flag_type}] {agent}: {msg}")
    else:
        print("── No anomalies flagged (all agents within thresholds) ──")

    # ── Routing rule candidates ──
    print()
    print("── Routing rule update candidates ──")
    candidates = []
    for agent, a in sorted_agents:
        total = a["total"]
        if total < MIN_JOBS_FOR_SIGNAL:
            continue
        high_pct = a["efforts"].get("high", 0) / total
        medium_pct = a["efforts"].get("medium", 0) / total
        high_short_rate = a["high_short"] / a["high_total"] if a["high_total"] >= 3 else 0

        if high_short_rate > HIGH_SHORT_WARN and a["high_total"] >= 3:
            candidates.append(
                f"  {agent}: lower default effort medium→high threshold. "
                f"{_pct(a['high_short'], a['high_total']):.0f}% high-effort jobs done <{SHORT_DUR_SECS}s — most were mechanical."
            )
        if high_pct < 0.05 and total >= 10:
            candidates.append(
                f"  {agent}: effort=high used only {_pct(a['efforts'].get('high',0), total):.0f}% — "
                f"routing is conservative; OK if task mix is genuinely mechanical."
            )

    if candidates:
        for c in candidates:
            print(c)
    else:
        print("  None — routing appears calibrated for this window.")

    print()
    print(f"Note: {sum(a['total'] for a in agents.values())} total jobs scanned. "
          f"Agents with <{MIN_JOBS_FOR_SIGNAL} jobs suppressed from anomaly detection.")
    print("Action: If anomalies confirmed across ≥2 consecutive weeks → propose specific")
    print("        MIKE.md routing rule edit to user; single-week anomaly = note only.")


if __name__ == "__main__":
    main()
