#!/usr/bin/env python3
"""usage_watch.py [--oneline]

Estimate how close the ACCOUNT is to its rolling 5-hour usage limit — the shared ceiling the
whole fleet (and every other session on this login) draws from. There is no public API for the
exact %, so this is a CALIBRATED estimate: it sums assistant OUTPUT tokens across ALL sessions
in ~/.claude/projects over the last 5h (output tokens are the dominant cost), and scales by a
calibration point you read off the Claude app's /usage panel.

Calibrate: when the app shows P%, run this, note the token total T, and set
USAGE_TOKENS_AT_100 = T / (P/100). Seeded from 2026-06-22: ~1.15M output ≈ 22% → ~5.2M = 100%.
Re-set it (env or the constant) whenever you read a fresh app value — it self-improves.

  usage_watch.py            → human summary (exit 1 if ≥ WARN%)
  usage_watch.py --oneline  → "PCT TOKENS TURNS RESET_HHMM" for fleet_health / watchdog

Env: USAGE_TOKENS_AT_100 (default 5200000), USAGE_WARN_PCT (default 80), USAGE_WINDOW_H (5).
Never raises; always prints something. The % is an ESTIMATE — treat ≥WARN as "ease off", not gospel.
"""
import sys, os, json, glob, time, datetime

PROJ = os.path.expanduser("~/.claude/projects")
WINDOW_H = float(os.environ.get("USAGE_WINDOW_H", "5"))
AT_100 = float(os.environ.get("USAGE_TOKENS_AT_100", "5200000"))
WARN = float(os.environ.get("USAGE_WARN_PCT", "80"))


def collect(now):
    cutoff = now - WINDOW_H * 3600
    out = 0
    turns = 0
    earliest = None
    for f in glob.glob(os.path.join(PROJ, "**", "*.jsonl"), recursive=True):
        try:
            if os.path.getmtime(f) < cutoff:
                continue
            lines = open(f, encoding="utf-8").read().splitlines()
        except Exception:
            continue
        for line in lines:
            if '"usage"' not in line:
                continue
            try:
                e = json.loads(line)
            except Exception:
                continue
            m = e.get("message")
            if not (isinstance(m, dict) and m.get("role") == "assistant"
                    and isinstance(m.get("usage"), dict)):
                continue
            ts = e.get("timestamp")
            if ts:
                try:
                    tt = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
                    if tt < cutoff:
                        continue
                    earliest = tt if earliest is None else min(earliest, tt)
                except Exception:
                    pass
            out += m["usage"].get("output_tokens", 0) or 0
            turns += 1
    return out, turns, earliest


def main():
    oneline = "--oneline" in sys.argv[1:]
    now = time.time()
    out, turns, earliest = collect(now)
    pct = 100.0 * out / AT_100 if AT_100 else 0.0
    # The rolling window frees up as the earliest counted turn ages past WINDOW_H; a practical
    # "reset" estimate = when that earliest turn exits the window (when the bulk frees, varies).
    reset = "?"
    if earliest:
        rt = datetime.datetime.utcfromtimestamp(earliest + WINDOW_H * 3600)
        reset = rt.strftime("%H:%MZ")

    if oneline:
        print("%.0f %d %d %s" % (pct, out, turns, reset))
        return

    bar = min(int(pct / 5), 20)
    print("ACCOUNT 5-hour usage (estimate)  —  %s" % datetime.datetime.utcnow().strftime("%FT%TZ"))
    print("  [%-20s] ~%.0f%%   (%d output tok / ~%.1fM at 100%%, %d turns in %.0fh)"
          % ("#" * bar, pct, out, AT_100 / 1e6, turns, WINDOW_H))
    print("  oldest counted turn frees ~%s (rolling window)" % reset)
    if pct >= WARN:
        print("  ⚠ at/over %.0f%% — ease off heavy Opus work or pause until the window rolls." % WARN)
    print("  NOTE: estimate only (no public usage API). Re-calibrate USAGE_TOKENS_AT_100 from the app's /usage.")
    sys.exit(1 if pct >= WARN else 0)


if __name__ == "__main__":
    main()
