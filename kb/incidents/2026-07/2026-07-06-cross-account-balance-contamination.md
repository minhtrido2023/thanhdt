---
kind: incident
date: 2026-07-06
topic: cross-account-balance-contamination
title: >-
  2026-07-06 — Cross-account balance contamination: EOD report posted a WRONG NAV to Discord
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-06 — Cross-account balance contamination: EOD report posted a WRONG NAV to Discord

**What happened:** User asked to manually regenerate today's (missed) EOD report for
SpaceX. `eod_trading_report.sh --account SpaceX` ran successfully and posted **NAV
688,509,567 VND** to Discord — wrong by ~294M VND. Real NAV (verified minutes later via a
fresh API call): **982,867,365 VND**.

**Root cause:** `trading_bot/brokers.py`'s `DNSEBroker._raw_log` path is
`dnse_raw_{date}.jsonl` — keyed by DATE ONLY, shared across every DNSE account that trades
that day. `_log_raw()` never wrote which account a record belonged to, and `"balances"`
records in particular carry no account identifier in their payload either (unlike
`"orders"`/`"place_order"` records, which do have `accountNo`). This was invisible for the
five weeks SpaceX was the only live DNSE account. The moment ZaloPay went live the SAME
DAY (2026-07-06) and both accounts called `balances()`, their records interleaved in the
one shared file. `daily_nav_snapshot.py`'s `latest_balance()` blindly took "the last
`balances` record in the file" — which by pure timing happened to be ZaloPay's (cash≈4.9M,
debt=0), not SpaceX's (cash=709M, debt=410M) — producing a materially wrong NAV that looked
completely plausible (a real, freshly-fetched balance, just for the wrong account) and sailed
through with no warning.

**Fix (root cause, not a patch):**
1. `trading_bot/brokers.py::_log_raw()` now writes `account_no`/`account_label` at the TOP
   LEVEL of every logged record (all kinds, not just balances) — additive, no existing
   consumer's fields changed.
2. `daily_nav_snapshot.py::latest_balance()` now takes `account_no` and filters to it;
   raises loudly if records exist but none match the requested account (fail-safe, not a
   silent wrong-account fallback). `main()` auto-resolves `account_no` from
   `trading_bot_accounts.json` by label if `--account-no` isn't passed explicitly, so no
   caller (cron or manual) needs to remember to pass it.
3. Getting the CORRECT number for today required a fresh, properly-tagged balance call
   (old records predate the fix and carry no tag) — dispatched a scoped, evidence-file
   read-only check, independently re-verified the resulting NAV myself, then re-ran
   `daily_nav_snapshot.py` and confirmed `nav_history_SpaceX.csv`'s 07-06 row corrected.
4. Posted a correction — Discord thread post failed (`HTTP 500`, bridge-side, unrelated to
   content — retried twice, both failed) so the correction went out via Telegram
   (`notify.sh`) instead, plus a bus `decision` event so it's captured even if the Discord
   bridge issue is still down next session.

**Lesson — same shape as the marketPrice/BQ-staleness pair from earlier the same day, one
layer deeper:** a number can be "freshly fetched from the real API" and STILL be wrong, if
the plumbing carrying it mixes up WHICH entity it's for. Multi-tenancy bugs (one shared
resource silently serving the wrong tenant) don't show up until the second tenant exists —
exactly the moment this session added ZaloPay. Any shared-by-date (not shared-by-account)
file/cache/log introduced when there was only one live account is now a latent risk the
moment a second one exists; worth an explicit grep for `_{date}.jsonl`-style shared-file
patterns across the codebase as a follow-up, not just this one call site.

**Not yet done:** no automated regression test proving `latest_balance()` correctly picks
the right account when 2 are interleaved in one file — the fix was verified manually
against tonight's real contaminated file. Should get a synthetic-fixture selfcheck (2 fake
accounts' balances interleaved, assert each account's query returns only its own) before
this is considered fully closed, following the `ghost_order_selfcheck.py` pattern in
`kb/coding_guidelines.md` §7.
