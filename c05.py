#!/usr/bin/env python3

import json
import subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path.home() / ".claude" / "projects"


# ---------- parse timestamp ----------
def ts(x):
    if not x:
        return None
    try:
        return datetime.fromisoformat(x.replace("Z", "+00:00"))
    except:
        return None


# ---------- extract title ----------
def get_title(obj):
    if obj.get("type") == "ai-title":
        return obj.get("aiTitle")

    if obj.get("type") == "last-prompt":
        msg = obj.get("message") or {}
        if isinstance(msg, dict):
            c = msg.get("content")
            if isinstance(c, str):
                return c[:80]

    return None


# ---------- build local session map ----------
sessions = {}

for f in ROOT.rglob("*.jsonl"):
    start = None
    end = None
    title = None

    try:
        for line in open(f, encoding="utf-8"):
            try:
                obj = json.loads(line)
            except:
                continue

            t = ts(obj.get("timestamp"))

            if t:
                if start is None:
                    start = t
                end = t

            if title is None:
                title = get_title(obj)

        if start and end:
            sessions[f.stem] = {
                "start": start,
                "end": end,
                "duration": end - start,
                "title": title or "(untitled)",
            }

    except:
        continue

# = ccusage ====
def get_ccusage():
    try:
        out = subprocess.check_output(
            ["npx", "ccusage@latest", "session", "--json"],
            text=True
        )
        return json.loads(out)
    except:
        return []


cc = get_ccusage()
cc_map = {}

# 🔥 FIX: handle multiple possible formats
if isinstance(cc, dict):
    cc = cc.get("sessions") or cc.get("data") or []

for s in cc:

    # nếu là string → skip an toàn
    if isinstance(s, str):
        continue

    if not isinstance(s, dict):
        continue

    sid = (
        s.get("session")
        or s.get("sessionId")
        or s.get("id")
    )

    if sid:
        cc_map[sid] = s

# ---------- merge ----------
def match_cc(session_start, session_end, cc_sessions):

    best = None
    best_score = 0

    for s in cc_sessions:

        if not isinstance(s, dict):
            continue

        cs = s.get("startTime") or s.get("start") or None
        ce = s.get("endTime") or s.get("end") or None

        cs = ts(cs)
        ce = ts(ce)

        if not cs or not ce:
            continue

        # overlap scoring
        overlap = min(session_end, ce) - max(session_start, cs)
        overlap_seconds = overlap.total_seconds()

        if overlap_seconds > best_score:
            best_score = overlap_seconds
            best = s

    return best or {}



cc = get_ccusage()

rows = []

for s in sessions:
    c = match_cc(s["start"], s["end"], cc)

    rows.append({
        "id": sid,
        "start": s["start"],
        "end": s["end"],
        "duration": s["duration"],
        "input": c.get("inputTokens", 0),
        "output": c.get("outputTokens", 0),
        "cost": c.get("cost", 0),
        "model": c.get("model", "-"),
        "title": s["title"],
    })



rows.sort(key=lambda x: x["start"], reverse=True)


# ---------- print ----------
print(
    f"| {'Session':36} | {'Start':16} | {'End':16} | {'Duration':12} | {'Input':10} | {'Output':10} | {'Cost':8} | {'Model':10} | Title |"
)

print("-" * 140)

for r in rows:

    print(
        f"| {r['id'][:36]:36} "
        f"| {r['start']:%Y-%m-%d %H:%M} "
        f"| {r['end']:%Y-%m-%d %H:%M} "
        f"| {str(r['duration']).split('.')[0]:12} "
        f"| {str(r['input']):10} "
        f"| {str(r['output']):10} "
        f"| {r['cost']:8} "
        f"| {r['model'][:10]:10} "
        f"| {r['title']} |"
    )
