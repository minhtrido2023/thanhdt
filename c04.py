#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime

ROOT = Path.home() / ".claude" / "projects"


def parse_ts(ts):
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def extract_title(obj):
    """
    Try multiple known Claude Code formats
    """
    if not isinstance(obj, dict):
        return None

    # format 1: ai-title (older/newer variants)
    if obj.get("type") == "ai-title":
        return obj.get("aiTitle")

    # format 2: last prompt (sometimes contains useful name)
    if obj.get("type") == "last-prompt":
        msg = obj.get("message") or obj
        if isinstance(msg, dict):
            content = msg.get("content")
            if isinstance(content, str):
                return content[:80]

    # format 3: fallback - first meaningful text
    msg = obj.get("message")
    if isinstance(msg, dict):
        content = msg.get("content")
        if isinstance(content, str) and len(content) > 10:
            return content[:80]

    return None


sessions = []

for file in ROOT.rglob("*.jsonl"):
    start = None
    end = None
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

                ts = parse_ts(obj.get("timestamp"))

                if ts:
                    if start is None:
                        start = ts
                    end = ts

                if title is None:
                    title = extract_title(obj)

        if start and end:
            sessions.append({
                "id": file.stem,
                "start": start,
                "end": end,
                "duration": end - start,
                "title": title or "(untitled)"
            })

    except Exception:
        continue


sessions.sort(key=lambda x: x["start"], reverse=True)


print(
    f"{'START':16} {'END':16} {'DURATION':12} {'SESSION ID':36} TITLE"
)
print("-" * 140)

for s in sessions:
    duration = str(s["duration"]).split(".")[0]

    print(
        f"{s['start']:%Y-%m-%d %H:%M} "
        f"{s['end']:%Y-%m-%d %H:%M} "
        f"{duration:12} "
        f"{s['id'][:36]:36} "
        f"{s['title']}"
    )
