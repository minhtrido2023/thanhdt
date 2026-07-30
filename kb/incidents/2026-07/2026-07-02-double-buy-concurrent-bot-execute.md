---
kind: incident
date: 2026-07-02
topic: double-buy-concurrent-bot-execute
title: >-
  2026-07-02 — Double-buy: 2 concurrent bot_execute.py processes fill the same plan 2x
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-02 — Double-buy: 2 concurrent bot_execute.py processes fill the same plan 2x

**What happened:** SpaceX live account bought all 11 planned tickers at exactly 2x
quantity (~456M → ~912M VND), pushing gross exposure to 140.8% NAV and breaching the
10% single-name cap on 4 bank tickers (BID 19.8%, CTG 19.3%, VPB 15.6%, MBB 15.0%).

**Root cause:** `bot_heartbeat.sh`'s autoheal fired at 09:00:01 ICT (before the scheduled
09:05 cron), launching a second `bot_execute.py` for SpaceX while the first was already
running. Neither process knew about the other — separate memory, separate participation
quota, cash-check against a broker balance that didn't reflect the other's concurrent
spend — so both independently filled the entire plan. At the time, no lock existed
between two `bot_execute.py` invocations for the same (account, date).

**Fix:** `_acquire_account_lock()` added to `bot_execute.py` — exclusive `fcntl.flock` on
`data/execution_logs/exec_{label}_{plan_date}.lock`, held for the whole process lifetime.
A second process for the same account+date fails to acquire it and skips that account
instead of running a duplicate session. Commit `503aa2f` (WorkingClaude repo).
Self-check: `concurrent_lock_selfcheck.py`.

**Residual gap found by quant-skeptic (2026-07-02T05:29 VERIFY):** flock blocks
*concurrent* double-runs, but not a *sequential* one — if a process is killed right after
`broker.place_order()` succeeds but before `_save_state()` persists it, the order exists
at the broker but state.json doesn't know it; a later run (even holding the lock
correctly) would re-place it. **Closed same day**: `Executor._ghost_tickers()` in
`executor.py` cross-checks the broker's live order book against state on every cycle and
fail-safe-pauses (not auto-adopts) any plan ticker with an untracked order, plus
`_save_state()` now runs immediately after each placement instead of once per cycle.
Self-check: `ghost_order_selfcheck.py` (8/8, incl. a poll-failure fail-safe test added
after quant-skeptic's second review found the guard failed OPEN on a `poll_orders()`
exception).

**Resolution:** Trim plan approved by user, executed 2026-07-06 (sell the doubled half of
each position back to 1x). T+2 settlement meant no forced-sale risk before then.
`data/BOT_STOP` correctly stayed clear (bug fixed, no loss spiral).

**Lesson:** A single preventive control (flock) closes the *known* failure mode but not
every failure mode in that class — an independent reviewer re-attacking the same
incident with a different angle (sequential vs concurrent) found a second real gap the
same day. Real-money order-placement code gets a second, independent defense even after
the first fix is confirmed; see [[risk-reward-calculated-not-avoidance]] for how the
fleet reasons about downside vs. paralysis.
