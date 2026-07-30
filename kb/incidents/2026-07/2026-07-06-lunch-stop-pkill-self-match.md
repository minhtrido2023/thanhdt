---
kind: incident
date: 2026-07-06
topic: lunch-stop-pkill-self-match
title: >-
  2026-07-06 (evening) — Lunch-stop `pkill` self-matched its own cron-invoking shell
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-06 (evening) — Lunch-stop `pkill` self-matched its own cron-invoking shell

**What happened:** User asked why the bot appeared to keep running through the 11:30–13:00 ICT
lunch break today when a dedicated cron line (`pkill -f "bot_execute.py --account SpaceX"`,
11:30 ICT) exists specifically to stop it, and pointedly asked whether this was a regression from
code Mike wrote that day without tests/review. Checked history first: `exec_SpaceX_2026-07-01_
journal.csv` (go-live day, before Mike touched any code) shows the **identical** pattern —
continuous activity to 11:29, a clean gap, resume exactly at 13:00 — so this is not a regression
introduced that day; it predates all of that day's changes.

**Root cause (confirmed by direct experiment, not inferred):** cron invokes each line via
`/bin/sh -c '<the exact crontab line>'`. The line's own text — `pkill -f "bot_execute.py
--account SpaceX" >> lunch_stop.log 2>&1` — becomes that wrapper shell's own `/proc/<pid>/cmdline`,
which therefore *contains the search pattern being passed to pkill*. `pkill -f` only excludes its
own PID, not its parent, so it also matches (and signals) its own invoking shell. Verified with a
live `sh -c '...' -- pkill -f "..."` experiment: `pgrep -f "bot_execute.py --account SpaceX"`
matched the wrapper shell's own PID. This makes the command's effect on the real target
unreliable/order-dependent rather than a clean, deterministic kill — a classic `pgrep`/`pkill`
self-match pitfall (the same class of bug the `ps aux | grep [x]xx` bracket trick exists for).

**Why it never caused a real problem:** `trading_bot/executor.py`'s `run_session()` loop calls
`session_phase(now)` every cycle; during the lunch window `vn_market.session_phase()` returns
`"CLOSED"`, which the loop already treats as a safe no-op (`_place_slices`/`_atc_sweep` don't run,
nothing gets journaled) — so the bot idles correctly through lunch on its own regardless of
whether the pkill actually reached it. The lunch-stop cron was, in effect, redundant defense-in-
depth that had silently never worked as a *kill*, not a live risk.

**Fix:** changed the crontab pattern to `pkill -f "[b]ot_execute.py --account SpaceX"` — the
standard bracket trick. `[b]` is a one-character regex class matching literal `b`, so it still
matches the real target's argv (`python3 bot_execute.py --account SpaceX ...`), but the *pattern
text itself* no longer appears verbatim as `bot_execute.py` in the invoking shell's own cmdline
(it appears as `[b]ot_execute.py`), so pkill no longer matches its own parent. Re-verified with
the same live experiment after the fix: target still matches, self-match gone. No selfcheck script
exists for this (unlike the T+2 fix from earlier the same day, which has
`t2_settlement_selfcheck.py`) — this is a one-line cron pattern, judged not to need one; deemed
low enough risk (config-only, doesn't touch order-placement logic, already double-verified with
live `pgrep`/`pkill` experiments against both a real-pattern dummy process and the actual new
crontab line) not to require a separate agent audit — offered to the user, declined as
unnecessary for a fix of this size.

**Lesson:** (1) always check history before assuming a same-day code change caused an observed
anomaly — the go-live-day journal comparison took two minutes and immediately ruled out
regression, redirecting the investigation to the actual (much older) root cause. (2) A "does
nothing today" bug can still be a real bug worth fixing even when a separate safety net already
covers the correctness gap — `pkill` not reliably killing its target is still wrong, independent
of whether `session_phase()` happens to make that harmless right now.
