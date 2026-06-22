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

                if title is None and obj.get("type") == "ai-title":
                    title = obj.get("aiTitle")

                ts = parse_timestamp(obj.get("timestamp"))

                if ts:
                    if start_time is None:
                        start_time = ts

                    end_time = ts

        if start_time:
            duration = end_time - start_time

            sessions.append({
                "session_id": file.stem,
                "title": title or "(untitled)",
                "start": start_time,
                "end": end_time,
                "hours": duration.total_seconds() / 3600.0,
            })

    except Exception:
        pass

sessions.sort(key=lambda x: x["start"], reverse=True)

print(
    f"{'START':16} {'END':16} {'HOURS':>8} {'SESSION ID':36} TITLE"
)
print("-" * 140)

for s in sessions:
    print(
        f"{s['start'].strftime('%Y-%m-%d %H:%M'):16} "
        f"{s['end'].strftime('%Y-%m-%d %H:%M'):16} "
        f"{s['hours']:8.2f} "
        f"{s['session_id'][:36]:36} "
        f"{s['title']}"
    )
