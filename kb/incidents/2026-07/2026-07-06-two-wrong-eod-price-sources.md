---
kind: incident
date: 2026-07-06
topic: two-wrong-eod-price-sources
title: >-
  2026-07-06 — Two wrong "end-of-day market price" sources, same day, both caught by user
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-06 — Two wrong "end-of-day market price" sources, same day, both caught by user

**What happened:** After the margin-netting correction (entry above), user asked for a
holdings table with end-of-day market price. Mike built it from DNSE's `positions()`
API `marketPrice` field, total 692,430,000 VND. User: *"giá thị trường cuối ngày của bạn
sai rồi, không đúng với giá khớp cuối ngày ở tất cả các cổ phiếu"* (your EOD price is
wrong for ALL stocks, doesn't match the true closing matched price). Second real bug
surfaced in the same investigation: the **already-posted** official NAV for the day
(`daily_nav_snapshot.py`, mtm_stock=688,380,000, part of the standing `verify_account_
snapshot.py` pipeline) was ALSO wrong, for an unrelated reason.

**Root causes (two separate bugs, same symptom class):**
1. **`positions().marketPrice` is not the ATC closing price.** Verified by calling
   `close_price(symbol, boardId=G1)` and `latest_trade(symbol, boardId=G1)` for all 15
   held tickers — the two independent DNSE endpoints agree with each other on every
   ticker (100% match) but disagree with `marketPrice` on every ticker (VCB: marketPrice
   62,300 vs true ATC 61,200; VHM: 157,700 vs 154,100; etc. — `marketPrice` runs ahead
   of the real close on 13/15 names). `marketPrice` is some other reference/intraday
   mark, not the ATC-session matched price; boardId=G1 with a nonzero `closePrice`/
   `matchPrice` is the correct field. Recomputing the table with the correct field gave
   **683,590,000 VND total — exact match to the user's own DNSE app screenshot.**
2. **`verify_account_snapshot.py`'s BQ-based MTM is structurally stale for same-day
   reports.** `bq_close_prices()` queries `MAX(t.time) <= asof`; `tav2_bq.ticker` only
   syncs nightly at 23:45 ICT (`sync_bq_cache_daily.sh`), so when `eod_trading_report.sh`
   runs at 15:00 ICT the SAME day, BQ has no row for today yet and silently falls back to
   the last available date (07-03, the prior Friday — 07-04/05 was a weekend). This is
   not a crash or a warning, just a quiet stale read, exactly the failure shape flagged
   in `kb/coding_guidelines.md` §6.

**Fix:** `verify_account_snapshot.py` now calls a new `dnse_close_prices()` (boardId=G1,
same two endpoints verified above) and uses it to OVERRIDE the BQ price per-ticker
whenever `--asof` is today's real date; BQ remains authoritative for past dates (already
correct once the nightly sync has run). Every position now carries `mtm_price_source`
(`"dnse_atc_g1"` or `"bq_close"`) for audit, and a warning fires listing any ticker that
had to fall back to BQ same-day (DNSE API failure case). Re-ran `daily_nav_snapshot.py
--account SpaceX --date 2026-07-06` after the fix: NAV corrected from 987,792,349 to
**983,002,349** (stock value 688,380,000 → 683,590,000) — now exactly matching the
user's screenshot end-to-end, and `data/execution_logs/nav_history_SpaceX.csv` updated
in place.

**Lesson:** Same lesson as the margin-netting entry, a third time in one day — a field
or a data source that *looks* authoritative (a broker API field named `marketPrice`; a
BigQuery table that's the system's normal source of truth) can be wrong for a reason
that's only visible once you cross-check against ground truth (the user's own screenshot)
and an independent second API call. Two bugs of the identical "stale/wrong price"
symptom, different root causes, both real, both would have kept silently misreporting
NAV by a few million VND every same-day report until caught.
