# Session Handoff — V11 Transparent Sim Bugs to Fix

**Date**: 2026-05-18
**From session**: df3c1340-40c2-46c7-b6dc-247737308843
**Status**: ⚠ Two critical bugs identified by user, need fix in new session

## Bugs to fix

### Bug 1: NNC has buys but no sell in transactions.csv

**Symptom**: User checked `data/v11_transparent_transactions.csv` and found
NNC ticker has 3 buy rows but ZERO sell rows. NNC is NOT in
`data/v11_transparent_open_positions.csv` either, so it's not a held position.

**Hypothesis**: The position got closed via one of the simulator's sell paths
that does NOT log to `event_log`. The current `event_log` patches only cover:
- Line 651-672: entry buy fill ✓
- Line 295-325: pending_exits T+1 Open sell ✓
- Line 778+: EOD force-close sell ✓ (only when force_close_eod=True)

**Missing event_log capture**:
- Line 421-447: partial profit-taking sells (not in V11 config so likely not the bug, but should add)
- Line 457-491: legacy T-close exits (t1_open_exec=False — not in V11 config)
- Line 596-635: eviction in entry loop (not in V11 but should add)
- **Line 717-720: abandoned-partial REFUND** (likely THE BUG for NNC — when sector cap or liquidity caps cause pending entry to abandon, any partial fill gets refunded to `cash += ...` without log)
- Any other `cash +=` sites in simulate_holistic_nav.py

**Action**: Audit ALL `cash +=` and `cash -=` sites in simulate_holistic_nav.py,
add event_log capture for each. Then NNC will either show its sell event OR
be flagged as "ABANDONED_REFUND" with proper transaction record.

### Bug 2: E1VFVN30 open position dates are hallucinated

**Symptom**: `data/v11_transparent_open_positions.csv` shows ETF positions with:
- `entry_date = 2025-06-09` (= first day of sim)
- `days_held = 340` (= total period length)

These are NOT real — ETF goes through many rebalance buys/sells, no single
entry_date is correct.

**Root cause**: In `sim_v11_transparent.py` around line 350-380, I added phantom
ETF entries with hard-coded `entry_date=common[0]` and computed `days_held`
from common[0] to common[-1]. This is hallucinated metadata.

**Fix — two options**:

**Option A** (simpler): Remove ETF from "open positions" section entirely.
Report ETF in a SEPARATE block with:
- Total ETF buys (real cash out)
- Total ETF sells (real cash in)
- Total friction
- Current ETF mark value (from cash_etf at end)
- ETF P&L = (sells + mark) - buys - friction
- No entry_date, no days_held — those don't apply to a rebalancing sub-balance

**Option B** (more rigorous, user-requested transparency): FIFO accounting.
Each ETF buy creates a "lot" with entry_date, shares, cost_basis. Each ETF
sell consumes oldest lot first. At end of period, remaining lots = "open ETF
positions" with REAL entry_dates (the buy date) and REAL days_held.

User likely prefers Option B because it's verifiable from transactions.csv.

## Production specs to maintain (from earlier in this session)

These were FIXED in this session — verify they survive the rework:

1. **Fee constants**: `TC_BUY=0.0015` (0.15%), `TC_SELL=0.0015`, `CG_TAX=0.001`
2. **No interest**: `deposit_annual=0` in sim script (and gated in simulator)
3. **Slippage** (user direction 2026-05-18):
   - OK to include slippage as a real cost (money out) — more realistic
   - BUT must be documented clearly so each transaction is traceable
   - Recommended: **separate `slippage` column** in transactions CSV, distinct
     from `fee` (broker TC) and `tax` (CG PIT). Each row shows:
       - `buy_amount` = clean share cost (shares × market_price)
       - `fee` = broker TC = buy_amount × 0.0015
       - `slippage` = price impact = buy_amount × slip_rate (separate)
       - `tax` = 0 on buy / buy_amount × 0.001 on sell
       - **Total cash deducted on buy** = buy_amount + fee + slippage
       - **Total cash received on sell** = sell_amount − fee − slippage − tax
   - Alternative: keep `fee` column merged (TC + tax + slip) BUT add explicit
     note in report + per-row `slip_pct` field. User must be able to follow.
   - If slippage=0 stays (no slippage), state that explicitly in report header.
4. **Real E1VFVN30**: Use `tav2_bq.ticker WHERE ticker='E1VFVN30'`, NOT VNINDEX proxy
5. **ETF fees off** (already in real price): `etf_mgmt_fee_annual=0`, `etf_tracking_drag_annual=0`
6. **ETF rebalance friction**: `etf_rebalance_friction=0.0015` (0.15% per side)
7. **Day 0 NAV exact**: Must = 50,000,000,000 (not 50,001,984,126)
8. **Event log buy semantics**:
   - `buy_amount` = shares × market_price (CLEAN, excludes fee)
   - `fee` = transaction cost (separate column)
   - Cash deducted = `buy_amount + fee`
9. **Event log sell semantics**:
   - `sell_amount` = shares × market_price (CLEAN, excludes fee)
   - `fee` = TC_sell + CG_TAX + tiered_slip
   - Cash received = `sell_amount - fee`
10. **Per-book daily columns** in logs CSV: `BAL_cash, BAL_stocks, BAL_etf,
    VN30_cash, VN30_stocks, VN30_etf` — sum must equal NAV
11. **MTM_UNREALIZED phantom rows**: at end of period, add phantom sell rows
    with `reason='MTM_UNREALIZED'` so analyze_portfolio.py computes correct
    P&L including unrealized. Filter `reason != 'MTM_UNREALIZED'` to see real
    activity only.

## Stack & period

- Period: 2025-06-09 → 2026-05-18 (today; intraday data ends ~2026-05-15)
- Initial NAV: 50e9 VND (split 25e9 BAL + 25e9 VN30)
- V11 stack: SV_TIGHT (Fresh-Q state-conditional) + P3 (overheat block) +
  RE_BACKLOG_BUY tier + V6 ETF parking (70% idle cash in NEUTRAL state=3)
- Layer 3 v4 HYBRID: BUY T+1 14:45 ATC for T1_TOP (ADV ≥ 50B/day),
  T+1 11:15 market for non-TOP. SELL stays T+1 Open (canonical).
- 50/50 BAL+VN30 book split, max_positions=10/book, hold_days=45, stop=-20%,
  sector_limit Fin/RE max 4, min_hold=2, BL20 re-entry blacklist

## Key files

- `simulate_holistic_nav.py` — sim engine
- `sim_v11_transparent.py` — sim script (has the ETF hallucination bug)
- `analyze_portfolio.py` — USER'S tool, DO NOT modify
- `signal_v10_sql.py` — SIGNAL_V10 BQ constant
- `data/v11_transparent_logs.csv` — daily NAV + per-book cols + cash_etf
- `data/v11_transparent_transactions.csv` — buy/sell + ETF rebalance + MTM phantoms
- `data/v11_transparent_open_positions.csv` — open positions snapshot (HAS ETF DATE BUG)
- `data/v11_transparent_report.md` — analyze_portfolio output + reconciliation
- `intraday_full.pkl` — 335 tickers × 15m bars 2023-09 → 2026-05

## Verification gate

A correct run must satisfy:
1. Day 0 NAV = exactly 50,000,000,000
2. Every BUY in transactions.csv has matching ticker activity in actions
3. Every position that closed has BOTH a buy AND a sell row in transactions.csv
4. Every position still open at end has a row in open_positions.csv with
   `entry_date` = ACTUAL buy date (not common[0])
5. For every date D and ticker T in CSV: sum(cash deductions for T on D from
   buy_amount + fee) - sum(cash inflows from sell_amount - fee) = net cash
   change for that ticker that day
6. Per-book columns sum to NAV: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash +
   VN30_stocks + VN30_etf = nav` (each row exactly)
7. End cash residual (after subtracting all real cash flows from transactions
   from initial 50B) should equal the ETF appreciation that's been rebalanced
   into cash side (this number can be computed from logs CSV)
8. Final NAV = end cash + end ETF + end open stock mark value (exact, ±1 VND)

## What user said verbatim

> "tôi kiểm tra lại, giao dịch NNC chỉ thấy mua vào, không có bán ra. chuyện gì
> xảy ra vậy, E1VFVN30, trong open position, thì ngày mua vào cho vị thế open
> là sai hoàn toàn, bạn đã bị hallucination tương đối rồi. Hãy chuyển sang một
> session mới, và làm lại cho tôi. chú ý những mistake tôi nêu ra"

---

## Memory references in this session

- `MEMORY.md` index now mentions real E1VFVN30/VN30 + transparent sim
  infrastructure (correct)
- `t1_intraday_buypoint_results.md` — Layer 3 v4 results (correct)
- `layer3_v4_shadow_tracker.md` — paper-trade shadow (correct)
- Memory does NOT yet mention these 2 bugs — new session should add a note
  after fixing.
