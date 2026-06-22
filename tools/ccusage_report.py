#!/usr/bin/env python3
"""Claude Code usage report — equivalent API cost (not actual billing on Max plan).

NOTE: Numbers show what usage would cost at pay-per-token API rates. On Claude
Max plan you pay a flat monthly subscription, so these figures are a usage-volume
indicator, not your actual bill.

Usage:
    python3 tools/ccusage_report.py              # session list, last 7 days
    python3 tools/ccusage_report.py --pivot      # daily pivot table, last 7 days
    python3 tools/ccusage_report.py --days 30    # custom window
    python3 tools/ccusage_report.py --all        # all time
    python3 tools/ccusage_report.py --min-cost 1 # hide sessions below $1
"""
import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Pricing table (USD per million tokens) ──────────────────────────────────
PRICING = {
    "claude-opus-4": {"input": 15.00, "output": 75.00, "cache_write": 18.75, "cache_read": 1.50},
    "claude-sonnet-4": {"input": 3.00, "output": 15.00, "cache_write": 3.75, "cache_read": 0.30},
    "claude-haiku-4": {"input": 0.80, "output": 4.00, "cache_write": 1.00, "cache_read": 0.08},
    "claude-fable-5": {"input": 3.00, "output": 15.00, "cache_write": 3.75, "cache_read": 0.30},
}

def _price_per_tok(model: str) -> dict:
    for prefix, p in PRICING.items():
        if model.startswith(prefix):
            return p
    return PRICING["claude-sonnet-4"]

def _cost_usd(usage: dict, model: str) -> float:
    p = _price_per_tok(model)
    M = 1_000_000
    return (
        usage.get("input_tokens", 0)                  * p["input"]       / M
        + usage.get("output_tokens", 0)               * p["output"]      / M
        + usage.get("cache_creation_input_tokens", 0) * p["cache_write"] / M
        + usage.get("cache_read_input_tokens", 0)     * p["cache_read"]  / M
    )

# ── Project dir → display label ──────────────────────────────────────────────
BASE_PREFIX = "-home-trido-"
_STRIP = ("thanhdt-WorkingClaude-mike-agents-", "thanhdt-WorkingClaude-mike-",
          "thanhdt-WorkingClaude-", "thanhdt-")

def _project_label(dir_name: str) -> str:
    s = dir_name[len(BASE_PREFIX):] if dir_name.startswith(BASE_PREFIX) else dir_name
    for pfx in _STRIP:
        if s.startswith(pfx):
            return s[len(pfx):]
    return s or dir_name

# ── Parse one session file ────────────────────────────────────────────────────
def _parse_session(path: Path) -> dict | None:
    timestamps, title = [], None
    model_usage: dict = defaultdict(lambda: defaultdict(int))
    daily_cost: dict = defaultdict(float)   # "YYYY-MM-DD" -> cost

    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for raw in f:
                try:
                    r = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                ts = r.get("timestamp")
                if ts:
                    timestamps.append(ts)
                rtype = r.get("type")
                if rtype == "ai-title" and title is None:
                    title = r.get("aiTitle", "")
                if rtype == "assistant":
                    msg = r.get("message", {})
                    model = msg.get("model") or "unknown"
                    usage = msg.get("usage") or {}
                    mu = model_usage[model]
                    for k in ("input_tokens", "output_tokens",
                              "cache_creation_input_tokens", "cache_read_input_tokens"):
                        mu[k] += usage.get(k, 0)
                    if ts:
                        day = ts[:10]
                        daily_cost[day] += _cost_usd(usage, model)
    except OSError:
        return None

    if not timestamps:
        return None

    ts_first, ts_last = min(timestamps), max(timestamps)
    try:
        t0 = datetime.fromisoformat(ts_first.replace("Z", "+00:00"))
        t1 = datetime.fromisoformat(ts_last.replace("Z", "+00:00"))
    except ValueError:
        return None

    total_cost = sum(_cost_usd(dict(mu), m) for m, mu in model_usage.items())
    total_input = sum(mu.get("input_tokens", 0) for mu in model_usage.values())
    total_output = sum(mu.get("output_tokens", 0) for mu in model_usage.values())
    real = {m: mu for m, mu in model_usage.items() if not m.startswith("<")}
    primary_model = max(real, key=lambda m: real[m].get("output_tokens", 0)) if real else "?"

    return {
        "session_id": path.stem,
        "title": title or "(untitled)",
        "first": t0,
        "last": t1,
        "duration_s": (t1 - t0).total_seconds(),
        "cost": total_cost,
        "input_tok": total_input,
        "output_tok": total_output,
        "model": primary_model,
        "daily_cost": dict(daily_cost),
    }

# ── Scan all projects ─────────────────────────────────────────────────────────
def gather_sessions(projects_root: Path, cutoff: datetime | None) -> list[dict]:
    sessions = []
    for proj_dir in sorted(projects_root.iterdir()):
        if not proj_dir.is_dir():
            continue
        label = _project_label(proj_dir.name)
        for jl in proj_dir.glob("*.jsonl"):
            s = _parse_session(jl)
            if s is None:
                continue
            if cutoff and s["last"] < cutoff:
                continue
            s["project"] = label
            sessions.append(s)
    return sessions

# ── Formatting helpers ────────────────────────────────────────────────────────
def _fmt_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{int(seconds)}s"
    m = int(seconds // 60)
    h, m = m // 60, m % 60
    return f"{h}h {m:02d}m" if h else f"{m}m"

def _fmt_tok(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.0f}K"
    return str(n)

def _truncate(s: str, n: int) -> str:
    return s if len(s) <= n else s[:n - 1] + "…"

def _fmt_cost(v: float) -> str:
    return f"${v:.2f}" if v >= 0.005 else ("·" if v == 0 else "<$0.01")

# ── Session list view ─────────────────────────────────────────────────────────
def print_session_list(sessions: list[dict], period: str) -> None:
    total_cost = sum(s["cost"] for s in sessions)
    W_PROJ, W_TITLE, W_DUR, W_IN, W_OUT, W_MODEL, W_COST = 22, 42, 9, 7, 7, 20, 10
    header = (f"{'Project':<{W_PROJ}} {'Session':<{W_TITLE}} {'Duration':>{W_DUR}} "
              f"{'Input':>{W_IN}} {'Output':>{W_OUT}} {'Model':<{W_MODEL}} {'Cost*':>{W_COST}}")
    sep = "─" * len(header)
    print(f"\nClaude Usage — {period} | {len(sessions)} sessions | equiv. API cost ${total_cost:.2f}*")
    print("* Equivalent API rate cost. Max plan users pay flat subscription, not per-token.")
    print(sep)
    print(header)
    print(sep)
    for s in sessions:
        proj  = _truncate(s["project"], W_PROJ)
        title = _truncate(s["title"], W_TITLE)
        dur   = _fmt_duration(s["duration_s"])
        inp   = _fmt_tok(s["input_tok"])
        out   = _fmt_tok(s["output_tok"])
        model = _truncate(s["model"], W_MODEL)
        cost  = "$" + f"{s['cost']:.2f}"
        date  = s["first"].strftime("%m-%d")
        print(f"{proj:<{W_PROJ}} {title:<{W_TITLE}} {dur:>{W_DUR}} "
              f"{inp:>{W_IN}} {out:>{W_OUT}} {model:<{W_MODEL}} "
              f"{cost:>{W_COST}}  {date}")
    print(sep)
    print(f"{'TOTAL':<{W_PROJ+1+W_TITLE}} {'':>{W_DUR}} {'':>{W_IN}} {'':>{W_OUT}} "
          f"{'':>{W_MODEL}} {f'${total_cost:.2f}':>{W_COST}}")
    print()

# ── Daily pivot view ──────────────────────────────────────────────────────────
def print_pivot(sessions: list[dict], days: int, now: datetime) -> None:
    # build day columns: today and N-1 prior days
    cols = [(now - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days - 1, -1, -1)]
    col_labels = [(now - timedelta(days=i)).strftime("%m/%d") for i in range(days - 1, -1, -1)]

    # build rows: (label, {day: cost}, total)
    rows = []
    for s in sessions:
        label = f"{s['project']} / {_truncate(s['title'], 36)}"
        daily = s["daily_cost"]
        row_total = sum(daily.get(d, 0) for d in cols)
        if row_total < 0.005:
            continue
        rows.append((label, daily, row_total))
    rows.sort(key=lambda r: r[2], reverse=True)

    if not rows:
        print("No sessions with non-zero daily cost in this window.")
        return

    # column widths
    W_NAME = 52
    W_DAY = 8
    total_cost = sum(r[2] for r in rows)

    header_days = "  ".join(f"{lbl:>{W_DAY}}" for lbl in col_labels)
    header = f"{'Session':<{W_NAME}}  {header_days}  {'Total':>{W_DAY}}"
    sep = "─" * len(header)

    print(f"\nClaude Usage — daily pivot (last {days} days) | equiv. API cost ${total_cost:.2f}*")
    print("* Max plan users pay flat subscription. These are equivalent API-rate costs.")
    print(sep)
    print(header)
    print(sep)

    for label, daily, row_total in rows:
        day_vals = "  ".join(f"{_fmt_cost(daily.get(d,0)):>{W_DAY}}" for d in cols)
        print(f"{_truncate(label, W_NAME):<{W_NAME}}  {day_vals}  {_fmt_cost(row_total):>{W_DAY}}")

    print(sep)
    # daily totals footer
    day_totals = "  ".join(
        f"{_fmt_cost(sum(r[1].get(d,0) for r in rows)):>{W_DAY}}" for d in cols
    )
    grand = _fmt_cost(total_cost)
    print(f"{'TOTAL':<{W_NAME}}  {day_totals}  {grand:>{W_DAY}}")
    print()

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=7, help="lookback window in days (default 7)")
    ap.add_argument("--all", dest="all_time", action="store_true", help="show all sessions")
    ap.add_argument("--pivot", action="store_true", help="show daily cost pivot table")
    ap.add_argument("--projects-dir", type=Path, default=Path.home() / ".claude/projects")
    ap.add_argument("--min-cost", type=float, default=0.0, help="hide sessions below this USD total")
    args = ap.parse_args()

    now = datetime.now(tz=timezone.utc)
    cutoff = None if args.all_time else now - timedelta(days=args.days)

    sessions = gather_sessions(args.projects_dir, cutoff)
    sessions = [s for s in sessions if s["cost"] >= args.min_cost]
    sessions.sort(key=lambda s: s["cost"], reverse=True)

    if not sessions:
        print("No sessions found for the given window.")
        return

    period = "all time" if args.all_time else f"last {args.days} days"

    if args.pivot:
        print_pivot(sessions, args.days if not args.all_time else 7, now)
    else:
        print_session_list(sessions, period)

if __name__ == "__main__":
    main()
