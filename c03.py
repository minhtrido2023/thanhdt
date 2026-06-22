#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime

CLAUDE_DIR = Path.home() / ".claude" / "projects"

def parse_timestamp(ts):
    if not ts:
        return None

try:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))
except Exception:
    return None

sessions = []

for file in CLAUDE_DIR.rglob("*.jsonl"):

start_time = None
end_time = None
title = None

try:
    with open(file, "r", encoding="utf-8") as f:

        for line in f:
            line = line.strip()

            if not line:
                continue

            try:
                obj = json.loads(line)
            except Exception:
                continue

            # session title
            if (
                title is None
                and obj.get("type") == "ai-title"
            ):
                title = obj.get("aiTitle")

            # timestamps
            ts = parse_timestamp(obj.get("timestamp"))

            if ts:
                if start_time is None:
                    start_time = ts

                end_time = ts

    if start_time:

        duration = end_time - start_time

        sessions.append(
            {
                "session_id": file.stem,
                "title": title or "(untitled)",
                "start": start_time,
                "end": end_time,
                "duration": duration,
            }
        )

except Exception as e:
    print(f"ERROR {file}: {e}")

sessions.sort(
key=lambda x: x["start"],
reverse=True
)

print(
f"{'START':16} "
f"{'END':16} "
f"{'HOURS':>8} "
f"{'SESSION ID':36} "
f"TITLE"
)

print("-" * 140)

for s in sessions:

hours = round(
    s["duration"].total_seconds() / 3600,
    2
)

print(
    f"{s['start'].strftime('%Y-%m-%d %H:%M'):16} "
    f"{s['end'].strftime('%Y-%m-%d %H:%M'):16} "
    f"{hours:8.2f} "
    f"{s['session_id'][:36]:36} "
    f"{s['title']}"
)
