---
kind: incident
date: 2026-07-06
topic: eod-report-missing-nav-sell-only-day
title: >-
  2026-07-06 (late afternoon) — Today's EOD report never posted + NAV computation broke on the first SELL-only day
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-06 (late afternoon) — Today's EOD report never posted + NAV computation broke on the first SELL-only day

**What happened:** User asked Mike to check the day's operations again. `eod_trading_report.sh`'s
15:00 ICT cron run crashed silently (`KeyError: 'id'`) before ever printing the order-fill
summary — today's fully-successful 710.5M VND trim (23/23 orders, exactly matching plan) never
reached Discord. Investigating the crash then surfaced two more bugs in `verify_account_snapshot.py`
and `daily_nav_snapshot.py`, all sharing one theme: **every script involved was written and only
ever tested against buy-only days; today was the first SELL-only day, and each one broke on an
assumption that only holds for buys.**

**Bug 1 — `eod_trading_report.sh` parsed the plan JSON directly instead of through `load_plan()`.**
Same root cause class as the morning's `trading_bot/plan.py` fix: today's plan uses the v2+ schema
(`priority`/`mtm_price_ref`, no `id`/`ref_price`), and this script's inline Python built
`orders_by_id = {o['id']: o for o in plan.get('orders', [])}` straight from the raw file, never
benefiting from `load_plan()`'s normalization shim that `bot_execute.py` already uses. Fixed by
routing through `trading_bot.plan.load_plan()` instead of hand-rolling a second, now-inconsistent
copy of the same parsing logic — the actual lesson: normalization belongs in exactly one place,
and any script reading `trade_plans/*.json` directly should go through that one place, not around it.

**Bug 2 — `verify_account_snapshot.py` summed fill quantity regardless of buy/sell side.**
Every prior use of this script was buy-only (2026-07-01/02/03), so `agg[sym][0] += fq` was never
wrong until today's trim (all sells) made it add when it should subtract — BID appeared to hold
7300 shares when the real post-trim holding was 1900. Fixed: sells subtract from a `net_qty`,
weighted-average cost basis is computed from buy-side fills only (correct accounting — selling
part of a position doesn't change the average cost of what remains).

**Bug 3 — the same script's journal-side aggregation double-counted partial fills.** A child
order that fills in multiple slices gets a `FILL` journal row *each time*, but the `qty` logged is
the **cumulative** filled-so-far for that child (`Executor._sync_fills`: `c["filled"] = min(...)`
then journals `c["filled"]`), not an incremental delta. Summing every row for the same `child_oid`
(HDB: rows of 600, then cumulative 2100) over-counted to 2700. Fixed: keep only the latest-by-
timestamp row per `child_oid` before aggregating — the exact same pattern `true_fills_from_dnse_raw`
already used for real broker order records, just missing on the journal side.

**Bug 4 — `daily_nav_snapshot.py` doesn't know DNSE settles sell proceeds asymmetrically from buys.**
A T+2 *payable* (from a buy) already shows as negative `totalCash` immediately — confirmed by the
2026-07-02 double-buy incident. A T+2 *receivable* (from a sell) does **not** show up anywhere in
`totalCash` until it actually settles — confirmed empirically today: post-trim balance is
byte-identical to pre-trim except the 710.7M in stock is simply gone, no offsetting cash appeared.
Naively adding the full pending-sell value back produced an equally wrong number the other way
(+42%, 1.4B) once it became clear that the account's pre-existing margin debt (409.86M, from the
07-02 double-buy) dropped to exactly 0 the SAME day — strongly suggesting DNSE nets sell proceeds
against outstanding margin debt immediately (standard margin-account mechanic), with only the
excess beyond debt payoff (~300.8M here) actually pending T+2 cash settlement. Implemented as an
explicit, clearly-labeled **estimate** (`nav_is_estimate` flag + full breakdown persisted) rather
than asserted as fact — this netting behavior is inferred from the observed numbers matching,
not confirmed via DNSE documentation. Flagged to re-verify against the real settled balance on
T+2 (2026-07-08).

**CORRECTION (same evening, ~1h later): Bug 4's "margin netting" theory was WRONG.** User sent a
real DNSE app screenshot at 16:02 ICT showing `totalDebt` **still 409,863,737** — unchanged, not
paid off — with Tài sản ròng (net worth) = Tiền + Cổ phiếu − Nợ = 709,276,086 + 683,590,000 −
409,863,737 = 983,002,349, matching the simple textbook formula exactly. Re-checked live via
Mafee (independently verified by reading the raw evidence file, not just the summary): a fresh
`balances()` call at 16:12 ICT now correctly returned `totalDebt=409,863,737` and
`totalCash=709,276,086` — i.e., the EARLIER 14:42 ICT read (which showed `totalDebt=0`) was
simply **stale** — the broker's balance figures hadn't finished an end-of-day reconciliation
batch yet when queried mid-afternoon, not because the debt had actually been netted against sell
proceeds. The entire "debt payoff" inference in Bug 4 above was explaining a data-freshness
artifact as if it were real broker mechanics — a second-order version of the same mistake this
whole incident thread is about (trusting a plausible-sounding number without tracing it back
far enough). Fixed: removed the netting-estimate logic entirely, reverted to the simple
`stock_mtm + totalCash − totalDebt` formula (exactly what the user asked for — "kiểm tra số liệu
từ api dnse không nên đoán mò"), using whatever is the LATEST balance snapshot. Added a cheap
staleness heuristic instead (warn if today had meaningful sell activity but cash didn't move
commensurately) so a similarly-stale read gets flagged rather than quietly trusted. Also lost
and had to manually restore 2 days of `nav_history_SpaceX.csv` rows in the process — a narrower
`csv.DictWriter` fieldnames list raised `ValueError` partway through `writerows()` on a row
carrying now-removed estimate-fields, truncating the file to just its header; fixed with
`extrasaction="ignore"` plus explicit per-row key filtering.

**Why none of this reached the user wrong (revised):** the fail-safe design caught bugs 1-3
before publishing a number, but **bug 4's wrong estimate DID reach Discord** (via the EOD report
re-run) before the user caught it with a real screenshot — the `nav_is_estimate` flag correctly
labeled it as uncertain, but a labeled-uncertain wrong number is still a wrong number reaching
someone. The actual save here was the user's own verification habit (checking against the real
app), not the system's fail-safe design. Update to the lesson: a self-reported "estimate" label
is not the same protection as the earlier bugs' hard fail (exit 1, nothing published) — when
genuinely uncertain, the stronger move is to not publish a number at all (or wait for a fresher
read) rather than publish a caveated guess.

**Lesson:** a script that has only ever been exercised by one direction of real-world data (all
buys, so far) has an untested code path (sells) sitting dormant — "it's been running fine" is not
evidence it's correct for a case it has never actually seen. Every script in the daily-report
pipeline needs an explicit test with SELL fills, partial-fill sequences, and T+2-in-flight state
before being trusted the way the buy-side path now is (see `t2_settlement_selfcheck.py` for the
executor-level equivalent already built this same day for a related bug).
