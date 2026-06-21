---
name: V11 transparent sim bugs fixed (NNC refund + ETF FIFO)
description: 2026-05-18 fix log for two transparent-sim bugs (NNC abandoned-refund silent / ETF entry_date hallucinated). All 8 verification gates now pass.
type: project
originSessionId: 6c923c95-596e-4b63-88f9-e716caa135c6
---
# V11 transparent sim — 2 bugs fixed (2026-05-18)

## Bug 1: NNC silent abandoned-refund

**Root cause** (`simulate_holistic_nav.py` line ~731 pre-fix): when an entry's
multi-day fill could not reach `min_fill_pct` (30%) within `max_fill_days` (5),
the partial fill was refunded via `cash += [REDACTED]_shares * px * sell_cost_factor`
with **no event_log entry**. Result: NNC had 4 buy rows in
`v11_transparent_transactions.csv` but no matching sell.

**Fix**: log the refund as a SELL action with `reason='ABANDONED_REFUND'` and
the SAME holding_id as the buys, so `analyze_portfolio.py` groups them together
under one position. Also audited and added event_log captures for the other
silent cash flow sites (partial profit-takes, legacy T-close exits, EVICT) for
defense in depth even though V11 doesn't currently exercise those paths.

**Verification**: post-fix, NNC has 5 rows under holding_id `NNC_20250610_6` —
4 ENTRY_FILL + 1 ABANDONED_REFUND. DHA also got refunded the same way (also
appears now). Total round-trip: bought 957.9M, refunded 952.5M → ~5M cost from
the partial fill churn (entry+exit fees on 30k shares).

## Bug 2: ETF entry_dates hallucinated

**Root cause** (`sim_v11_transparent.py` pre-fix): ETF "open positions" was
emitted as a single row per book with hard-coded `entry_date=common[0]` (sim
inception) and `days_held=340` (entire period). Not real — ETF goes through
many rebalance buy+sells with different dates.

**Fix**: full FIFO per-lot accounting in `simulate_holistic_nav.py`:
- New `etf_lots` list of `{entry_date, shares, cost_basis, holding_id}`
- Replaced `cash_etf` scalar daily compounding with `_etf_mark(today)` helper
  that computes MTM from `sum(lot.shares * today_px)`
- Each rebalance buy creates a NEW lot with today's date + unique holding_id
- Each rebalance sell consumes lots oldest-first (FIFO); one tx row per lot
  consumed, tagged with that lot's holding_id
- At end of period, `nav_df.attrs["etf_lots_final"]` exposes remaining lots
  with their REAL `entry_date` and `days_held = (last_day - entry_date).days`

**Verification post-fix**: 4 open positions in `v11_transparent_open_positions.new.csv`:
- PAN BAL entry=2026-04-10 days=22 (real position)
- E1VFVN30 BAL entry=2026-04-09 days=36 cost=21.38B (real ETF lot)
- E1VFVN30 BAL entry=2026-04-24 days=21 cost=0.59B (real ETF lot)
- E1VFVN30 VN30 entry=2026-04-09 days=36 cost=21.86B (real ETF lot)

Each lot's entry_date matches its actual buy row in
`v11_transparent_transactions.csv` (`holding_id` cross-references).

## All 8 verification gates PASS

1. Day 0 NAV = exactly 50,000,000,000 (diff 0.00)
2. Every BUY ticker in transactions has activity (50 unique)
3. Every closed position has both buy AND sell rows (0 orphans across 77 closed)
4. Open positions entry_date = actual buy date (0 mismatches across 4 lots)
5. Cash flow from transactions reconstructs end cash exactly (diff 0.00 VND)
6. Per-book columns sum to NAV (max diff 0.000015 VND across 233 rows)
7. End cash residual = 0 (no orphan ETF appreciation)
8. Final NAV = end cash + end ETF + open stock mark (diff -0.00 VND)

## Bug 3 (extra): D1 RE_BACKLOG_BUY tier was missing from sim (2026-05-18 fix)

User verification caught that `sim_v11_transparent.py` was importing raw
`SIGNAL_V10` SQL directly, which does **not** emit the `RE_BACKLOG_BUY` tier —
that override lives in Python wrapper code in `recommend_holistic.py:243-255`
(deployed 2026-05-16). Sim was therefore not applying "người mua trả tiền
trước" (advance customer payments YoY > 0.5) signal for ICB 8633 (RE/KCN).

**Fix**: ported the D1 wrapper to `sim_v11_transparent.py` step 2b. Runs a small
BQ query for ICB-8633-only universe pulling AdvCust YoY + fa_tier + np/rev_yoy
+ state5, applies condition (adv_yoy>0.5 AND fa C/D AND ta>=120 AND state 3-5
AND (np_yoy>0 OR rev_yoy>0)) → overrides play_type to RE_BACKLOG_BUY.
Added RE_BACKLOG_BUY to `BUY_TIERS_V11`, `TIER_BAL`, and
`sector_cap_exempt_tiers={RE_BACKLOG_BUY}` so it slots beyond Fin/RE cap=4
(matching prod).

**Impact on 11mo sim**: 135 signal rows / 9 tickers reclassified. 3 actually
entered (KBC, VHM, VIC). KBC stopped out at -22.95% via TIME (Jan→Mar 2026),
but VHM (+8.06%) and VIC (+6.38%) still open. Net NAV change: **65.50B → 65.62B
(+0.12B / +0.25pp CAGR)**. Cohort win-rate worse but exempt-slot mechanics
preserve other winners → small net positive. Matches direction of D1's
production validation (memory: ba_v11_production_proposal).

## Bug 4 (extra): slot12 deployment + 10% fixed sizing (2026-05-18)

Production (`recommend_holistic.py:575-584`) deployed slot12 on 2026-05-16:
`max_positions=12` with `Per-slot size = NAV/10 = 10% per position`. Extra 2
slots let RE_BACKLOG_BUY enter beyond 10 without shrinking existing positions.

Sim previously used `max_positions=10` with default 1/N sizing. Fixed:
- Added `MAX_POS_V11 = 12` constant
- Added `TIER_WEIGHTS_V11 = {tier: 0.10 for tier in TIER_BAL}` (fixed 10% NAV
  per position regardless of max_positions; over-allocation naturally capped
  by `cash * 0.95` fallback in simulator)
- Passed both to BAL + VN30 `simulate()` calls

**Impact (11mo 50B sim, on top of D1)**:
- Without slot12: 65.62B / CAGR 33.91% / DD -11.97% / 84 holdings / 6 open
- With slot12:    **65.56B / CAGR 33.79% / DD -11.94% / 92 holdings / 7 open**

Trade count went up (more concurrent positions allowed) but realized P&L
similar. Slot12's E4 validation (FULL +0.26pp / OOS24-26 +1.65pp) is over
multi-year backtest — this 11mo window doesn't fully show it.

## Final 11-month V11 result (50B, 2025-06-09 → 2026-05-15, fully aligned)

- Final NAV: **65.56B** (+31.13%, CAGR 33.79%)
- MaxDD: -11.94%
- Net realized stock P&L: +6.21B
- Net ETF cash flow: -37.93B (parked, residual 42.91B + open lots)
- Unrealized open: +3.09B (incl. VHM/VIC RE_BACKLOG_BUY gains)
- 92 total holdings (7 still open), 59 unique tickers
- Stack: V11 (SV_TIGHT + P3) + D1 RE_BACKLOG + slot12 (max=12, 10% sizing)
  + Layer 3 v4 HYBRID + 50/50 BAL+VN30 + V6 ETF + ABANDONED_REFUND fix
  + ETF FIFO lots

## Files

- `simulate_holistic_nav.py` — engine with FIFO ETF lots + complete event_log
- `sim_v11_transparent.py` — sim script using lot-based open positions
- `verify_gates.py` — runs all 8 gates against current outputs (`python verify_gates.py`)
- `data/v11_transparent_*.csv` — outputs

## Known issue (not blocking)

`data/v11_transparent_open_positions.csv` is held by another process (probably
OneDrive sync or stale handle) — script now writes to `.new.csv` fallback. User
can rename when free, or kill the locker.
