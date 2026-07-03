#!/usr/bin/env python3
"""staleness_watch.py [--oneline]

Watch-the-watcher check for pipelines that self-report freshness in a JSON artifact but only
alert when they successfully RUN (e.g. macro_healthcheck.py sends Telegram on DEGRADED/FAILED,
but says nothing if the pipeline never runs at all — cron misfire, an earlier step in
daily_refresh_v34b_linux.sh crashing before reaching the healthcheck step, host down at the
scheduled time). Root cause of the 2026-06-30 "DT5G stuck 11 days" incident: nothing EXTERNAL
to that pipeline was checking whether its output artifact was still being refreshed.

This script is deliberately independent of the pipeline it watches (different cron entry,
different codepath) — it just reads each artifact's own self-reported top-level "ts" field
(assumed Asia/Ho_Chi_Minh wall-clock, naive — matches how these scripts write it; see
macro_healthcheck.py's `datetime.now()` under TZ=Asia/Ho_Chi_Minh via wc_env.sh) and flags
anything older than its configured max age.

  staleness_watch.py            → human summary, one line per watched artifact
  staleness_watch.py --oneline  → "KEY AGE_H MAX_H FLAG" per artifact, for watchdog.sh
                                   FLAG: 0=fresh 1=stale 2=unknown(missing/unparseable)

Add new artifacts to WATCH below as more pipelines earn a real incident. Never raises; a
missing/unparseable file reports flag=2 (worse than stale, not silently treated as fresh).
"""
import sys
import json
import datetime
from zoneinfo import ZoneInfo

ICT = ZoneInfo("Asia/Ho_Chi_Minh")

# (key, path, max_age_hours). max_age_hours is generous enough to survive a normal weekend gap
# (Fri 23:15 ICT run -> next check Mon) without false-firing every Monday morning.
WATCH = [
    ("macro_health", "/home/trido/thanhdt/WorkingClaude/data/macro_health.json", 60),
]


def age_hours(path):
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        ts = datetime.datetime.fromisoformat(d["ts"]).replace(tzinfo=ICT)
        now = datetime.datetime.now(ICT)
        return round((now - ts).total_seconds() / 3600, 1)
    except Exception:
        return -1.0


def main():
    oneline = "--oneline" in sys.argv
    any_bad = False
    for key, path, max_h in WATCH:
        age = age_hours(path)
        # flag: 0=fresh 1=stale (file readable but too old) 2=unknown (missing/unparseable —
        # worse than stale, since a vanished/broken artifact could mean the pipeline was
        # never even reached, not just delayed)
        if age < 0:
            flag, status = 2, "UNKNOWN"
        elif age >= max_h:
            flag, status = 1, "STALE"
        else:
            flag, status = 0, "fresh"
        any_bad = any_bad or flag != 0
        if oneline:
            print(f"{key} {age} {max_h} {flag}")
        else:
            print(f"{key}: age={age}h max={max_h}h [{status}] ({path})")
    sys.exit(1 if any_bad else 0)


if __name__ == "__main__":
    main()
