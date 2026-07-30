---
kind: incident
date: 2026-07-01
topic: golive-day1-5-bugs
title: >-
  2026-07-01 — Go-live day-1: 5 bugs, none caught by rehearsal
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-01 — Go-live day-1: 5 bugs, none caught by rehearsal

**What happened:** SpaceX bot failed to place any live orders on go-live morning; 5
distinct bugs had to be fixed in sequence before it worked. User feedback: "these are
basic errors that rehearsal should have caught — not acceptable."

1. **`python` not on PATH on Linux** — `run_bot.sh` called `python` instead of `python3`
   (script written/tested on Windows, never run in Linux production before go-live).
2. **`PlannedOrder` rejected extra fields from DollarBill's plan JSON** — DollarBill's v2
   plan format added `est_value`/`weight_pct`/`timing`; `load_plan()` didn't filter to
   known dataclass fields before construction → `TypeError`.
3. **Auto-OTP silently skipped when `credentials_file: null`** — guard written for
   "not a DNSE account" also matched a legitimate DNSE account using the default
   credentials file, so it ran with no trading token → 1300+ `PLACE_FAIL`.
4. **`TZ` not set → `session_phase()` returned PRE during market hours** — `run_bot.sh`
   didn't source `wc_env.sh`; server ran UTC, `session_phase()` hardcodes ICT hours, so
   the bot connected and loaded the plan but placed zero orders.
5. **`nohup ... &` inside a single Bash tool call didn't survive across tool calls** —
   when Mike manually restarted the bot mid-incident (not via cron/systemd), the sandbox
   reaped the process group ~5 min after that tool call "finished," silently killing 9
   in-flight orders with no monitoring. Fixed by using `setsid` (verified via
   `ps -o pid,ppid,pgid,sid` showing PGID=SID=PID) instead of `nohup`.

**Fix:** All 5 patched same day; full detail and the resulting rehearsal checklist in
[[feedback-golive-day1-bugs]] (memory).

**Lesson:** A rehearsal that doesn't run in the actual production environment (Linux
cron, real plan JSON from the actual upstream producer, real credentials shape, real TZ)
doesn't actually rehearse the failure modes that matter — every one of these 5 bugs was
an environment/integration gap, not a logic bug that a dev-machine test would have caught.
