---
kind: incident
date: 2026-07-06
topic: t2-shares-not-sellable-until-afternoon
title: >-
  2026-07-06 (later same day) — Executor didn't know T+2-purchased shares aren't sellable until the afternoon session
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-06 (later same day) — Executor didn't know T+2-purchased shares aren't sellable until the afternoon session

**What happened:** User asked whether Mike understood that shares bought Thursday 07-02 (T)
would only become sellable "this afternoon" (T+2 = 07-06, afternoon session) — flagging that
plan-building needs to respect this settlement rule. Checking the live journal confirmed it in
real time: `bot_execute.py` had been retrying the exact 11 tickers from the 07-02 batch every
~20 seconds since 09:12 ICT, hitting `HTTP 400: Trade quantity not enough` **~2000 times** over
more than an hour, while the 12 tickers from the 07-01 batch (already past T+2) sold normally.
No capital or correctness impact — every attempt was correctly rejected by the broker — but a
real inefficiency (wasted API calls, log noise, latent rate-limit risk) that the execution layer
had no way to anticipate.

**Root cause:** `DNSEBroker.get_positions()` already returns both `total` (all held shares) and
`sellable` (shares actually available to sell, i.e. past T+2 settlement) per the `BrokerBase`
contract — but `Executor._place_slices`/`_atc_sweep` never called `get_positions()` or consulted
`sellable` at all. They computed a desired sell qty from the plan and blindly called
`place_order()`, letting the broker's own rejection be the only signal that shares weren't
settled yet.

**Fix:** `Executor.step()` now fetches `get_positions()` once per cycle (only when the plan has
at least one SELL order, to avoid the extra API call on buy-only days) and passes it into
`_place_slices`/`_atc_sweep`. Both now cap the sell qty to the ticker's `sellable` amount, or
skip the ticker entirely (logging a new `WAIT_T2_SETTLEMENT` journal event) when sellable is
below 1 lot — instead of attempting and waiting for an HTTP 400. If `get_positions()` itself
fails, the code degrades gracefully to the old behavior (attempt anyway) rather than blocking —
this is a retry-noise optimization, not a correctness guard, so a transient API failure shouldn't
stop legitimate sells. Commit: see `t2_settlement_selfcheck.py` (7 new regression checks) and the
updated `ghost_order_selfcheck.py` (its `step()`-spy lambdas needed a signature update for the
new `positions` parameter — caught by running the full existing suite before committing, no
regressions found). Also committed, separately, the `trading_bot/plan.py` id/ref_price
normalization shim that had been hotfixed directly on disk during the morning's plan-swap
incident (see the entry above) but was still uncommitted.

**Deployment note:** the live `bot_execute.py` process (running continuously since this
morning's 09:12 ICT restart) will only pick up this fix at its next natural restart — the
existing 11:30 ICT lunch-stop (`pkill`) followed by the 13:00 ICT resume cron — not via a manual
restart during the fix itself, to avoid touching a running production process mid-session.

**Lesson:** a broker API that already distinguishes "held" from "actually actionable" (here:
`total` vs `sellable`) is a signal the execution layer should consult *before* acting, not just a
field to shrug off until the broker's rejection teaches the same lesson the expensive way. Same
class of gap as the id/ref_price schema mismatch earlier today: a plan (or an execution loop)
built without checking the concrete rules of the system it operates in will "work" on the happy
path and silently misbehave (crash, or here, spin uselessly) the first time reality diverges from
the implicit assumption.
