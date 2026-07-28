#!/usr/bin/env python3
"""staleness_watch.py [--oneline]

Watch-the-watcher check for pipelines that self-report freshness in a JSON artifact but only
alert when they successfully RUN (e.g. macro_healthcheck.py sends Telegram on DEGRADED/FAILED,
but says nothing if the pipeline never runs at all — cron misfire, an earlier step in
daily_refresh_v34b_linux.sh crashing before reaching the healthcheck step, host down at the
scheduled time). Root cause of the 2026-06-30 "DT5G stuck 11 days" incident: nothing EXTERNAL
to that pipeline was checking whether its output artifact was still being refreshed.

This script is deliberately independent of the pipeline it watches (different cron entry,
different codepath) — it reads each artifact's own self-reported top-level "ts" field
(assumed Asia/Ho_Chi_Minh wall-clock, naive — matches how these scripts write it; see
macro_healthcheck.py's `datetime.now()` under TZ=Asia/Ho_Chi_Minh via wc_env.sh) and flags
anything older than its configured max age. An entry with path=None is instead measured by its
own probe below (kb_ingest_lag compares two timestamps rather than aging one file).

  staleness_watch.py            → human summary, one line per watched artifact
  staleness_watch.py --oneline  → "KEY AGE_H MAX_H FLAG" per artifact, for watchdog.sh
                                   FLAG: 0=fresh 1=stale 2=unknown(missing/unparseable)

Add new artifacts to WATCH below as more pipelines earn a real incident. Never raises; a
missing/unparseable file reports flag=2 (worse than stale, not silently treated as fresh).
"""
import sys
import os
import re
import json
import glob
import datetime
from zoneinfo import ZoneInfo

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
MIKE = "/home/trido/thanhdt/WorkingClaude/mike"

# (key, path, max_age_hours). max_age_hours is generous enough to survive a normal weekend gap
# (Fri 23:15 ICT run -> next check Mon) without false-firing every Monday morning.
# path=None means the key has its own probe below instead of a self-reported "ts" artifact.
WATCH = [
    ("macro_health", "/home/trido/thanhdt/WorkingClaude/data/macro_health.json", 60),
    # KB ingestion: bus/inbox -> kb/events_buffer.md. Earned its slot on 2026-07-28, when a
    # stale consolidate.sh cursor first stranded ingestion fleet-wide for 21h and then silently
    # leapfrogged a CONFIRMED verification event. Neither failure was visible to any existing
    # check: consolidate.sh kept exiting 0 ("no new events") and only whispered into a logfile.
    # So measure the OUTCOME — how far the KB trails the bus — and any future cause (cursor
    # bug, cron misfire, lock starvation, crash) surfaces the same way. 3h ≫ the hourly :07
    # cron, so one missed run is not an alert.
    ("kb_ingest_lag", None, 3),
]


def kb_ingest_lag_hours():
    """Hours between the newest event on the bus and the newest event that reached the KB.
    Both sides are UTC Zulu (bus "ts" fields; the "- [<ts>]" lines consolidate.sh writes), so
    unlike the ICT artifacts above this needs no timezone handling.

    Heartbeats are excluded from the BUS side because kb_nightly.sh Phase 1a strips them from
    the KB side — counting them here but not there lets the gap grow on its own through any
    heartbeat-only stretch and raises a STALE that ingestion never caused."""
    newest_bus = ""
    for fp in glob.glob(os.path.join(MIKE, "bus/inbox/*.jsonl")):
        try:
            with open(fp, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        ev = json.loads(line)
                    except Exception:
                        continue          # unparseable line can't date the bus
                    if ev.get("event_type") == "heartbeat":
                        continue          # compare like with like (see docstring)
                    ts = ev.get("ts", "")
                    if ts > newest_bus:
                        newest_bus = ts
        except Exception:
            continue
    if not newest_bus:
        return 0.0                        # empty bus: nothing to ingest, not a fault
    newest_kb = ""
    try:
        with open(os.path.join(MIKE, "kb/events_buffer.md"), encoding="utf-8") as f:
            for line in f:
                # "/heartbeat" is skipped on this side too, so the comparison is symmetric
                # both before and after Phase 1a first strips them from the buffer.
                m = re.match(r"^- \[(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)\] \S+?/(\S+)", line)
                if m and m.group(2) != "heartbeat" and m.group(1) > newest_kb:
                    newest_kb = m.group(1)
    except Exception:
        return -1.0                       # buffer unreadable -> UNKNOWN, louder than STALE
    if not newest_kb:
        return -1.0
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    try:
        gap = (datetime.datetime.strptime(newest_bus, fmt)
               - datetime.datetime.strptime(newest_kb, fmt))
    except Exception:
        return -1.0
    return round(max(0.0, gap.total_seconds() / 3600), 1)


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
        age = kb_ingest_lag_hours() if path is None else age_hours(path)
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
            src = path or "bus/inbox → kb/events_buffer.md"
            print(f"{key}: age={age}h max={max_h}h [{status}] ({src})")
    sys.exit(1 if any_bad else 0)


if __name__ == "__main__":
    main()
