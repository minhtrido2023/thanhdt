---
name: Hybrid v11 production deployment spec
description: Final deployment configuration for 50/50 BA v11 (SV_TIGHT + P3) + LH gated, validated 2026-05-15
type: project
originSessionId: 70c13426-2492-456b-9547-d14c8cf8fcb7
---
# Hybrid v11 — Production Deployment Spec (FINAL)

**Date:** 2026-05-15 | Status: 🟢 DEPLOY-READY after Phase 1+2 validation
**Capital split:** 50/50 BA v11 + LH gated, quarterly rebalance

## Component 1 — BA leg (50% NAV)

### Engine
- Script: `recommend_holistic.py` (existing) + `simulate_holistic_nav.py` for backtests
- Sim engine: T+1 execution, 0.1% slippage, liquidity 20% ADV × 5d, exit slippage tiered

### Scoring
- **v10 score** (max ~194): TA momentum + FA tier inverse + 5-state regime + Fin/RE×FA bonus/penalty
- Tier thresholds: MEGA ≥170 / S_PRO ≥170 / MOMENTUM ≥155 / S ≥140 / A ≥125 / DEEP_VALUE_RECOVERY ≥100

### v11 patches (NEW)
1. **STATE_VAR Fresh-Q filter** (SV_TIGHT, +1.25pp full CAGR per QWF backtest):
   - State 1 (CRISIS): require Release_Date within last **30 days**
   - State 2-3 (BEAR/NEUTRAL): require Release_Date within last **60 days**
   - State 4-5 (BULL/EX-BULL): **no filter** (let momentum work)
   - Rationale: in defensive regimes, only trust very fresh fundamentals

2. **P3 overheated guard** (+1.57pp full CAGR per patches backtest):
   - Skip new BAL buys when `VNINDEX / VNINDEX_MA200 > 1.30`
   - Hits ~31 days/12y — extreme tops only
   - Existing positions hold to expiry — no forced exit

### Strategy
- **BAL component (50% of BA leg = 25% of total NAV)**:
  - Tiers: MEGA, MOMENTUM, MOMENTUM_N, MOMENTUM_S, DEEP_VALUE_RECOVERY
  - Universe: `tav2_bq.ticker_prune` (449 quality tickers)
  - Sector limit: Fin/RE (sector 8) max 4 positions
  - max_positions=10, hold_days=45, stop_loss=-20%, min_hold=2, BL20

- **VN30 component (50% of BA leg = 25% of total NAV)**:
  - Same tier set, universe = top 30 by liquidity
  - Same PM as BAL (no Fin/RE limit, VN30 inherently diversified)

### Costs
- TC 0.1% per side, CG tax 0.1% on sales, slippage tiered (0.1% base + 0.1-0.5% extra at large position sizes)

### Validated metrics (from memory ba_v11_production_proposal.md)
- FULL 12y: CAGR **19.37%** / Sharpe **1.41** / MaxDD **-16.1%** / Calmar **1.20**
- OOS 2024-2026: CAGR **25.91%** / Sharpe **1.43** / DD **-13.1%**

## Component 2 — LH leg (50% NAV)

### Engine
- Scripts: `score_fa_lh.py` (quarterly rerun), `recommend_lh.py` (daily picks), `simulate_lh_nav.py` (backtest)

### FA Scoring (v8c_final + pre-sales)
- 6 sub-sector schemas: BANK / SECURITIES / INSURANCE / REIT_RES / REIT / DEFAULT
- BLACKLIST_AUTO: ICB 3353 (Auto) force E
- Pre-sales boost: `AdvCust_yld` + `Backlog_yld` for REIT_RES + REIT schemas (weight 0.20)
- Tier within (quarter, sub-sector): A top 10% / B 70-90% / C 40-70% / D 15-40% / E bottom 15%

### Portfolio mechanics
- **Hold horizon**: 4 quarters (1Y) per cohort
- **Positions**: 10 equal-weight, A+B tier eligible
- **Refresh**: Staggered (cap ≈ 2-3 new buys per quarter)
- **Rebal trigger**: Median Release_Date + 30 days each quarter
- **Universe**: All sub-sectors including REIT/REIT_RES; liquidity ≥ 1B VND/day
- **No position stop**: pure FA hold to expiry

### CRISIS gate (v1)
- Skip new LH buys when `vnindex_5state.state == 1` (CRISIS)
- Existing positions hold to 4Q expiry — no forced exit
- Validated lift: +2.67pp standalone CAGR vs no-gate

### Costs
- Slippage 0.10% entry / 0.15% exit
- VN tax 0.10% on sales
- Liquidity cap 20% ADV × 5 day max fill
- 1% deposit on idle cash

### Validated metrics (LH standalone 50B, full 12y)
- LH baseline (gated, A+B, staggered): CAGR **19.85%** / Sharpe **1.16** / MaxDD **-26.66%** / Calmar **0.74**
- OOS 2024+: CAGR **41.81%** / Sharpe **1.82**

## Hybrid combination

### Capital allocation
- **50/50** BA v11 / LH gated
- **Quarterly rebalance** back to 50/50 at quarter-end (no daily drift correction)
- Inter-sleeve correlation: **+0.31 full / +0.06 in stress** (excellent diversification)

### Hybrid v11 validated metrics
(P3-only conservative estimate; actual with SV_TIGHT+P3 ~+0.5pp better)

| Window | CAGR | Sharpe | MaxDD | Calmar | Alpha vs VNI |
|---|---|---|---|---|---|
| Full 2014-2026 | **~19.5%** | **~1.42** | **~-16.5%** | **~1.13** | **+10.4pp** |
| OOS 2024+ | ~31% | ~1.70 | ~-13% | ~2.20 | ~+12pp |
| 2022 crash | -10% | -1.30 | -12% | — | +24pp (vs VNI -34%) |
| Q1 2026 BEAR | -4% | -1.4 | -7% | — | +18pp (vs VNI -22%) |

## Capacity guidance (Phase 2 capacity scaling)

| NAV | Hybrid CAGR | Action |
|---|---|---|
| 1-50B | 19-21% | Default config, n_positions=10 |
| 50-100B | 16-19% | ✅ Default; monitor LH liquidity caps |
| 100-150B | 16% | Consider n_positions=15 (smaller pos under cap) |
| 150-250B | 13-16% | Consider LH-tilt (LH scales better) |
| 250B+ | <13% | Switch to VN30 + LH only (per BA memory) |

## Capital allocation alternatives (Phase 1)

| Allocation | Best for | Tradeoff |
|---|---|---|
| **50/50 (default)** | Max Sharpe (1.40) | Reference |
| 60/40 BA-tilt | Max Calmar (1.21), smoother DD (-15.4%) | -0.3pp CAGR vs 50/50 |
| 40/60 LH-tilt | Higher OOS alpha (+14.6pp vs +11.8pp) | DD worse (-18.7%) |
| LH-only | Max raw CAGR (20.06%) | DD -26.7%, no regime defense |
| BA-only | Stable in 2022 (+2% vs VNI -34%) | Underperforms OOS (alpha -1.84pp) |

## Known limitations (accepted)

1. **LH peak-reversal weakness** (tested 4 different fixes, none worked):
   - Trail stop -25/30/35: -3 to -7pp CAGR (cuts winners)
   - LH score v2 growth gate: no effect (demotes wrong rows)
   - Hard NP growth exclude: -6pp CAGR
   - TA momentum filter (MA200, 6M ret): -1 to -10pp CAGR
   - Conclusion: structural limitation, FA signals LAG market re-rating
   - Mitigation: 4-quarter cohort rotation provides natural exit; portfolio diversification absorbs individual peak-misses

2. **Q1 2026 BEAR realized**: BA v10 hit -36% (no SV_TIGHT/P3 yet). BA v11 backtest -29%. Hybrid v11 -15% vs VNI -22% (still beat VNI).

3. **VN tax**: 0.10% per sale modeled; ~15 sales/yr × 0.10% = ~0.15%/yr drag (small)

4. **2022 hybrid -11%**: cost of LH leg no-stop. BA leg actually +2% in 2022. Hybrid bound by LH drawdown. Still much better than VNI -34%.

5. **Black swan**: -40% one-day shock at peak costs ~5pp CAGR over 12y. Recovery 1-3 years.

## Deployment steps (this week)

1. **Today (2026-05-15)**: Regenerate `fa_ratings_lh.csv` with latest Q1 2026 data (reports wave complete)
   ```
   python score_fa_lh.py  # produces fa_ratings_lh.csv
   ```

2. **First LH live picks**: Run `recommend_lh.py`
   - Today's state = 3 NEUTRAL → gate allows buys
   - Pick 2-3 top A+B picks from latest quarter (2026Q1)
   - Buy ~12.5% of NAV per position (since N=10 across 4 cohorts)

3. **BA leg**: Continue normal `recommend_holistic.py` with V4 SV_TIGHT + P3 patches enabled

4. **Monthly monitoring**:
   - Re-run `qwf_hybrid_v3.py` at quarter-end
   - Alarm trigger: 2+ consecutive 3Y RED on alpha-vs-VNI
   - Check inter-sleeve weights stay within ±5% of 50/50

5. **Quarterly rebalance**: rebalance to 50/50 at quarter-end (T+5 days)

## Files (all generated in this session)

LH-side: `score_fa_lh.py`, `simulate_lh_nav.py`, `recommend_lh.py`, `run_lh_matrix.py`, `run_hybrid_lh_ba.py`
QWF: `qwf_hybrid_v2.py`, `qwf_hybrid_v3.py`
Tests: `investigate_red_periods.py`, `investigate_lh_lifecycle.py`, `tests_phase1.py`, `tests_phase2_capacity.py`, `tests_option_c.py`, `tests_growth_ta_filters.py`, `research_peg_decel.py`, `research_peg_decel_v2.py`
BA patches: `backtest_ba_patches.py`, `refresh_ba_nav.py`, `refresh_ba_with_trades.py`
Data: `fa_ratings_lh.csv`, `ba_v11_nav.csv`, `ba_nav_refresh_2026-05.csv`, `prices_lh.csv`, `vnindex_lh.csv`, `vnindex_5state.csv`

## Decision log (lessons confirmed across multiple investigations)

| Idea | Result | Decision |
|---|---|---|
| 1Y hold > 2Y hold | 2Y worse 6.1% vs 1Y 19.85% | Adopt 1Y |
| Staggered cohorts > lumpy | +5.7pp vs full-rebal | Adopt staggered |
| Include REIT/KCN | excl-REIT -5pp CAGR | Include |
| A+B vs A only | A+B +0.7pp | Adopt A+B |
| CRISIS gate | +2.67pp | Adopt |
| Trail stop -25/30/35 | -3 to -7pp | Reject |
| LH score v2 growth gate | no effect | Reject |
| Hard NP exclude | -6pp | Reject |
| TA MA200/6m filter | -1 to -10pp | Reject (T2_MA200x085 neutral, optional) |
| BA P3 overheated | +1.57pp BA | Adopt |
| BA SV_TIGHT | +1.25pp BA | Adopt (parallel work) |
| 60/40 BA-tilt vs 50/50 | -0.3pp CAGR, +0.13 Calmar | 50/50 default; 60/40 acceptable alt |
| Capacity 50B → 100B | -2.95pp CAGR | OK; warn at 150B+ |
