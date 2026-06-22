#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime

ROOT = Path.home() / ".claude" / "projects"


def parse_time(ts):
    if not ts:
        return None

    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


for file in ROOT.rglob("*.jsonl"):

    start_time = None
    end_time = None
    title = None

    try:
        with open(file, encoding="utf-8") as f:

            for line in f:
                try:
                    obj = json.loads(line)
                except Exception:
                    continue

                ts = parse_time(obj.get("timestamp"))

                if ts:
                    if start_time is None:
                        start_time = ts
                    end_time = ts

                if title is None:
                    text = str(obj)

                    if len(text) > 20:
                        title = text[:80].replace("\n", " ")

        if start_time:
            duration = end_time - start_time

            print(
                f"{start_time:%Y-%m-%d %H:%M:%S} | "
                f"{str(duration).split('.')[0]:>10} | "
                f"{file.stem} | "
                f"{title or ''}"
            )

    except Exception as e:
        print(f"ERROR {file}: {e}")
