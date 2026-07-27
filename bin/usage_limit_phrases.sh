#!/usr/bin/env bash
# usage_limit_phrases.sh — SINGLE source of truth for "does this log text look like an
# ACCOUNT usage-limit failure (vs a real task failure)". Sourced by BOTH:
#   - bin/dispatch.sh  (_looks_like_usage_limit → schedule auto-resume instead of failing)
#   - bin/daily_retro.sh (draft-fail triage → calm status instead of alarm question)
# Keep the phrase list HERE ONLY so the two detectors can never drift apart over time
# (arch-review coord-2026-07-27 round2).
#
# Covers the real Claude CLI wordings observed in the wild:
#   - "You've hit your weekly limit · resets Jul 26, 5pm"  ← WEEKLY cap. Note it has NO
#      "usage/session limit" and "resets 5pm"/"resets Jul 26" has NO "at" — this exact
#      phrasing evaded the old dispatch.sh list and broke auto-resume for EVERY agent that
#      hit the weekly cap (root cause, 2026-07-24 & 07-25 daily-retro draft failures).
#   - "usage limit reached · resets at 6am"                 ← 5-hour rolling window cap.
#   - API 429 / rate_limit_error / quota exceeded.
#
# IMPORTANT — why a pct-fallback (usage_watch.py) cannot replace this list for the weekly
# cap: usage_watch.py only estimates the rolling 5-HOUR window. The WEEKLY ceiling is a
# DIFFERENT limit, so the 5h pct can read low (e.g. 3%) while the account is blocked
# weekly. The phrase list is the only reliable signal for a weekly exhaustion.
USAGE_LIMIT_PHRASE_RE='weekly limit|usage limit|session limit|rate.?limit|resets? ([0-9]|at)|quota exceeded|limit reached|rate_limit_error|"status":[[:space:]]*429'
