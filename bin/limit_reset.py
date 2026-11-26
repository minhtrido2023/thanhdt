#!/usr/bin/env python3
"""Parse "resets <time> (<tz>)" from a Claude CLI usage-limit message -> epoch.
Shared by dispatch.sh (headless jobs) and session_limit_resume.py (Discord sessions)."""
import re, sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

MONTHS = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
          "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
pat = re.compile(
    r"resets?\s+(?:at\s+)?(?:(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+(\d{1,2}),?\s+)?"
    r"(?:(\d{1,2}):(\d{2})\s*(am|pm)?|(\d{1,2})\s*(am|pm))"
    r"(?:\s*\(([^)]+)\))?",
    re.IGNORECASE,
)
def reset_epoch(text, now=None):
    """now: tz-aware datetime, only for tests."""
    best = 0
    for m in pat.finditer(text):
        mon_s, day_s, h1, m1, ap1, h2, ap2, tz_raw = m.groups()
        hh = int(h1 if h1 is not None else h2)
        mm = int(m1) if m1 is not None else 0
        ap = (ap1 or ap2 or "").lower()
        if ap == "pm" and hh < 12:
            hh += 12
        elif ap == "am" and hh == 12:
            hh = 0
        if hh > 23 or mm > 59:
            continue
        tz_name = (tz_raw or "Asia/Ho_Chi_Minh").strip()
        try:
            tz = ZoneInfo(tz_name)
        except Exception:
            tz = ZoneInfo("Asia/Ho_Chi_Minh")
        now_dt = now.astimezone(tz) if now else datetime.now(tz)
        if mon_s and day_s:
            mon = MONTHS[mon_s.lower()]
            day = int(day_s)
            try:
                cand = now_dt.replace(month=mon, day=day, hour=hh, minute=mm, second=0, microsecond=0)
                if cand <= now_dt - timedelta(days=30):
                    cand = cand.replace(year=now_dt.year + 1)
            except ValueError:
                continue
        else:
            cand = now_dt.replace(hour=hh, minute=mm, second=0, microsecond=0)
            if cand <= now_dt:
                cand += timedelta(days=1)
        delta = (cand - now_dt).total_seconds()
        if 0 < delta <= 8 * 86400:
            best = max(best, int(cand.timestamp()))
    return best or None


if __name__ == "__main__":
    text = ""
    for p in sys.argv[1:3]:
        if not p:
            continue
        try:
            with open(p, encoding="utf-8", errors="replace") as f:
                text += "\n" + f.read()[-4000:]
        except Exception:
            pass
    e = reset_epoch(text)
    if e:
        print(e)
