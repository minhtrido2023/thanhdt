---
name: Backfill simulation reality check — intraday stop fails on real BA-system flow
description: Synthetic backtest 51K events said intraday stop +8.5pp/event. Real 18-event journal sim says -5.4pp. FP rate 40% (vs 17% synthetic). DISABLE intraday stop in production; use SHADOW logging mode instead.
type: project
originSessionId: 90878235-541c-4207-a725-44398117b136
---
Scripts: `layer3_backfill_simulation.py` (main), `layer3_backfill_stop_variants.py` (V1-V6), `layer3_backfill_v2.py` (V7-V10). Outputs: `layer3_backfill_results.csv`, `layer3_stop_variants*.csv`.

**Why this matters:** earlier synthetic backtest on universe top30/midcap/penny (51,071 events) showed intraday stop saves +8.5pp/event vs EoD wait. This made paper trade adopt ACTIVE intraday stop. **Backfill on 18 actual BA-system journal BUYs (Aug 2025-Apr 2026) shows OPPOSITE.**

**Key numbers from 18-event backfill (real BA-system flow):**
- Total cumulative lift: −23.79pp (new rule WORSE than journal)
- STOP_INTRADAY 5 events: mean −20.20% locked vs journal mean −14.82% → lift −5.38pp ❌
- TIME_X1 13 events: mean −2.62% vs journal −2.86% → lift +0.24pp ✓ (small positive)
- Stop FP rate: 2/5 = **40%** (vs 17% in synthetic). FP loss: −17.83pp/event avg.
- Hit rate (lift > 0): 50%

**Variants tested (V1-V10), best results:**
- V8 (stop −22% hard): -10.45pp total — least bad of intraday stops
- V10 (EoD-confirmed stop next-day OPEN): -10.68pp total
- V9 (NO stop, all TIME_X1): -28.24pp total — surprising: still negative because TIME_X1 vs journal sell mechanics differ
- **NO variant beats journal baseline consistently**

**Why discrepancy synthetic vs real:** BA-system selects tickers with HIGH intraday volatility (DEEP_VALUE plays especially). These have more intraday wicks that don't confirm at close. 40% FP rate on actual flow vs 17% on universe-wide.

**Two egregious FP cases (illustrative):**
- HLD 2026-01-05: journal exit TIME −1.31% (recovered). New intraday stop fired at −20.20% → loss −18.89pp
- TCB 2026-01-26: journal exit TIME −3.43%. New intraday stop fired at −20.20% → loss −16.77pp

**Production decision (paper_trade_daily.py):**
- `STOP_MODE = "SHADOW"` (default): log every intraday stop event but don't exit
- `STOP_MODE = "ACTIVE"` available for future enabling after more data
- Adds `STOP_EOD_CONFIRMED` exit when EoD close ≤ stop_lvl (matches journal-style stop)
- Keeps entry rules (T1115 / S2) and X1 sell timing — these showed small positive lift on TIME exits

**Bigger takeaway about backtest design:**
- Synthetic universe-wide backtests can mislead when production flow has different distribution
- For BA-system specifically, future improvements must be validated on JOURNAL events (small sample but real), not just universe simulation
- 18 events is small — paper trade over 3+ months needed for reliable conclusion
- SHADOW logging during paper trade is the cheapest way to build that sample

**Caveats:**
- Sample n=18 is small; 1 fluke event can swing aggregate
- X1 limit sell on journal sell_date may differ from journal's actual exit mechanism — comparison is APPROXIMATE, not strict A/B
- Full evaluation requires re-running BA-system simulate with the new rules embedded (requires modifying simulate_holistic_nav.py — bigger project)
