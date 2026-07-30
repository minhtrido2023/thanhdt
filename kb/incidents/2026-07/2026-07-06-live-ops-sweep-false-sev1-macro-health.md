---
kind: incident
date: 2026-07-06
topic: live-ops-sweep-false-sev1-macro-health
title: >-
  2026-07-06 — Live ops sweep for the day (user asked "is anything still wrong"), found a third, unrelated bug: false SEV1 in the DT5G macro health-check itself
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-06 — Live ops sweep for the day (user asked "is anything still wrong"), found a third, unrelated bug: false SEV1 in the DT5G macro health-check itself

**Context:** after fixing the two pricing bugs above, user asked for a full sweep of
today's operations and what lessons to draw. Live-checked BOT_STOP, circuit breakers,
today's journal, tomorrow's plan timing, the EOD report cron, and `data/macro_health.json`
— found the macro pipeline reporting **`"status": "FAILED", "sev": "SEV1",
"recommended_state_source": "DT4_only"`** as of 15:30 ICT today (written by
`papertrade_daily.sh`'s own health-check call, not the nightly refresh).

**What was confirmed real vs. false, by checking ground truth directly (not trusting the
health-check's own output):**
1. `local_v34b_state_csv` source: pointed at `data/vnindex_5state_tam_quan_v3_4b_full_history.csv`
   — a file frozen since 2026-06-30 that `daily_refresh_v34b_linux.sh`'s build step never
   writes to (it saves to WORKDIR root, per that script's own comment). This check had been
   comparing against a dead file for over a week and only crossed the 3-trading-day alert
   threshold today by coincidence of elapsed time, not because anything got worse today.
   **Fixed**: switched the check to query BQ `tav2_bq.vnindex_5state_tam_quan_v34b_clean`
   directly (confirmed via direct `bq query` this returns 2026-07-03, correctly fresh) — this
   is also the *actual* primary source `macro_state_live.py` reads since a 2026-06-02 change
   (local CSV there is an emergency-fallback-only path, not the normal input). Commit
   `eb9a3fa` (WorkingClaude repo).
2. `bq_ticker_vnindex` source: reported `as_of=2026-06-25` (7 trading days stale). Verified
   with a direct `bq query` — the true answer is **2026-07-06** (today, fresh). Re-ran the
   exact same `bq()` helper the health-check uses (`simulate_holistic_nav.bq`) manually and
   it also returned the correct 2026-07-06 — so the wrong reading did not reproduce on
   retry. Most likely explanation (NOT fully confirmed — flagged rather than guessed as
   fact): the BQ local-cache layer `simulate_holistic_nav.bq()` wraps behaves differently
   across cron environments (the Friday-night nightly-refresh log showed explicit
   "`BQ_LOCAL_CACHE init failed ... falling back to real BQ`" messages; `papertrade_daily.sh`
   runs in a different environment and may have hit a stale-but-"verified" cache instead of
   a clean fallback). **Left open** — did not guess-fix a shared cache layer without
   understanding it, per the lesson from the two pricing bugs earlier the same day.

**Practical impact today: none.** `market_stress.flag` was `false` at the time (VIX/SPX both
in range) — even with DT5G active, no macro cap would have fired, so the fail-safe
degradation to DT4-only did not change any live trading decision today. The gap that
matters is forward-looking: if genuine market stress had coincided with this false SEV1,
the system would have been silently running without the extra defensive cap that DT5G is
specifically insurance against.

**Lesson:** this is the health-check that exists *specifically* to catch "silent staleness
that the system doesn't know it has" (its own docstring's stated purpose) — and it had
exactly that failure mode itself, for over a week, undetected, because nothing regression-
tests the checker's own file paths against the pipeline's actual write targets. A monitor
is also code that can silently drift from what it's monitoring.
