---
name: Release_Date filter exploration on BA-45d (canonical sim)
description: STATE_VAR (Fresh-Q only in BEAR/NEUTRAL state) beats current F1_60 production filter; deeper insight on Release_Date impact
type: project
originSessionId: 762b6179-ddcb-41b7-ac2b-ee8d2f143ccc
---
# Release_Date filter exploration — 2026-05-14

**Scripts**: `test_release_date_advanced.py` | NAV output: `ba_release_date_nav.csv` | log: `release_date_results.txt`

## Motivation

Existing production F1_60 filter (`recommend_holistic.py` FRESH_Q_MAX_DAYS=60) was validated on BAL leg only with ~+0.05pp CAGR / +0.12 Sharpe. Goal: test on **full canonical 50/50 BAL+VN30** sim and explore more sophisticated Release_Date filters.

## Methodology

Universe: SIGNAL_V10 + v4 FA, 2014-2026 canonical sim (50B, max=10, hold=45d, stop=-20%, slip=0.1%, sec_lim 8:4, liq caps). For each signal row, computed:
- `days_since_release`: days since most recent quarterly release for that ticker
- `days_to_next_release`: days until next upcoming release

10 variants tested.

## Results (FULL 2014-2026)

| Variant | CAGR | Sharpe | MaxDD | Calmar | Trades | Δ CAGR |
|---------|------|--------|-------|--------|--------|--------|
| **F0 baseline** | **16.87%** | 1.18 | -13.5% | 1.25 | 289 | — |
| F1_30 tight (30d) | 11.87 | 1.53 | -7.3% | 1.62 | 180 | -5.0 |
| F1_45 medium | 14.78 | 1.35 | -10.4 | 1.42 | 193 | -2.1 |
| **F1_60 (prod)** | 15.17 | 1.17 | -11.9 | 1.27 | 209 | **-1.7** ❌ |
| F1_90 loose | 16.79 | 1.18 | -13.9 | 1.21 | 290 | -0.1 |
| TIER_VAR (30/60 split) | 14.30 | 1.04 | -15.7 | 0.91 | 192 | -2.6 |
| **🏆 STATE_VAR** | **18.11** | **1.26** | -16.1 | 1.12 | 276 | **+1.25** ✓ |
| EARN_SEASON | 15.13 | 1.16 | -11.9 | 1.27 | 209 | -1.7 |
| TONEXT_30 ⚠ | 4.82 | 0.59 | -18.9 | 0.25 | 168 | -12.0 |
| TONEXT_60 ⚠ | 9.04 | 0.77 | -18.4 | 0.49 | 220 | -7.8 |

## OOS 2024-2026 confirmation

| Variant | CAGR | Sharpe | DD | Δ CAGR |
|---------|------|--------|-----|--------|
| F0 baseline | 24.26% | 1.28 | -13.0 | — |
| F1_45 medium | **27.11** | **1.72** | -9.2 | **+2.85** |
| F1_60 (prod) | 23.03 | 1.29 | -9.1 | -1.23 ❌ |
| **STATE_VAR** | **26.50** | **1.49** | -11.9 | **+2.25** ✓ |
| TONEXT_30 | 10.67 | 1.01 | -7.7 | -13.59 |

## Pre-OOS 2014-19 robustness

| Variant | CAGR | Sharpe |
|---------|------|--------|
| F0 baseline | 7.31% | 0.88 |
| F1_60 (prod) | 7.38 | 0.85 |
| **STATE_VAR** | **8.93** | **1.10** |

## Key Findings

### 1. 🚨 Production F1_60 filter actually LOSES CAGR on canonical
Memory's claim "+0.05pp CAGR" was BAL leg only. On full canonical 50/50:
- FULL CAGR: -1.7pp vs baseline
- OOS CAGR: -1.23pp vs baseline
- Sharpe tied (+0.01)
- → F1_60 trades CAGR for DD; net not a clear win on canonical

### 2. 🏆 STATE_VAR is the winner
Logic: Apply Fresh-Q 60d filter **only in state 1, 2, 3 (BEAR/CRISIS/NEUTRAL)**. In state 4, 5 (BULL), no filter — momentum dominates, FA quality less critical.

Wins across **all 3 periods** (FULL, OOS, Pre-OOS):
- +1.25 to +2.25 pp CAGR
- +0.08 to +0.22 Sharpe
- Slightly worse DD on FULL (-16.1 vs -13.5), better on OOS (-11.9 vs -13.0)

Trade count efficient: 276 (only 13 less than baseline 289), filters where it matters.

### 3. ⚠ TONEXT_30/60 (filter on days_to_NEXT release) is DISASTER
- TONEXT_30: -12.05pp CAGR FULL, -13.59pp OOS
- Anti-pattern: pre-release uncertainty noise > catalyst alpha
- **Don't entry before earnings**

### 4. Tighter than 60d over-filters
- F1_30: best Sharpe (+0.35) but kills CAGR (-5pp). Less filtering is more.
- F1_45: medium ground, best on OOS (+2.85 CAGR), inconsistent on FULL

### 5. Tier-stratified F1 (30d MEGA, 60d others) hurts
- TIER_VAR: -2.6pp CAGR, -0.13 Sharpe
- Over-strict on MEGA/MOMENTUM removes momentum alpha

### 6. EARN_SEASON ≈ F1_60 (most signals already in earnings months)

## Recommendation

### REPLACE F1_60 with STATE_VAR in production
- Modify `recommend_holistic.py` to use state-conditional fresh-Q
- 2014-2026 wins +2.94pp CAGR vs F1_60 on canonical 50/50
- OOS 2024-2026 wins +3.47pp CAGR

### Implementation
```python
# In recommend_holistic.py
def apply_fresh_q_filter(cand, state5_today, fresh_q_max_days=60):
    if state5_today in (1, 2, 3):  # BEAR / CRISIS / NEUTRAL
        # Apply standard 60d filter
        return cand[cand["days_since_release"].notna() &
                   (cand["days_since_release"] <= fresh_q_max_days)]
    # state 4, 5 (BULL): no filter
    return cand
```

### Caveat
- DD slightly worse FULL (-16.1 vs -13.5 baseline)
- Calmar similar (1.12 vs 1.25)
- Trade-off: catch upside in BULL but pay DD when state turns BEAR
- Need user confirmation before production deployment

## Files reference
- `test_release_date_advanced.py` — 10-variant test script
- `release_date_results.txt` — full output log
- `ba_release_date_nav.csv` — NAVs for all variants
- `test_state_var_stress.py` — BEAR-period decomposition (13 BEAR windows in 2014-2026)
- `state_var_bear_detail.csv` — per-window F0 vs SV stats
- Production filter location: `recommend_holistic.py` line 314 (FRESH_Q_MAX_DAYS=60)

## STATE_VAR validated empirically (2014-2026 BEAR decomposition)

13 BEAR periods identified in 2014-2026:
- **Aggregate BEAR-only**: F0 -6.31% vs STATE_VAR +4.52% → **+11.56pp relative outperformance**
- BULL aggregate: +0.17% Δ (≈ 0 as expected, filter doesn't activate)
- Specific big wins:
  - **2018 Q2 trade war**: F0 -11.42% / SV -2.82% (**+8.6pp save**, DD -12.4% → -3.6%)
  - **2024 Apr-Sep BEAR**: F0 -0.78% / SV +0.53% (DD -12.0% → -4.3%)

→ All FULL CAGR alpha (+1.25pp) comes from BEAR periods. BULL neutral, recovery -1pp minor lag.

## 2007-2013 FA principle stress test (quarterly Close from ticker_financial)

Script: `test_fa_ic_2007_2013_crisis.py`

Data: ticker_financial has Close from 2006 (130 tickers grow to 642). Forward returns computed via Close(Q+1)/Close(Q)-1.

### IC by regime (forward 1Q quarterly return)

| Regime | smoothed_EY | NP_peak | Cash_MktCap | NP_R |
|--------|-------------|---------|-------------|------|
| CRISIS_2008 (GFC, fwd mean -8.7%) | +0.072 | +0.092 | +0.080 | +0.090 |
| INFLATION_2011 | +0.233 | +0.192 | +0.160 | +0.173 |
| SIDEWAYS_2012-13 | +0.215 | +0.189 | +0.149 | +0.154 |
| 2007-13 FULL | +0.163 | +0.127 | +0.116 | +0.126 |

### Comparison: 2007-13 vs 2014-26 IC

12 indicators **timeless** (same sign both eras):
ROIC5Y, ROE_Min5Y, ROE_Trailing, FSCORE, NP_R, NP_peak_ratio, NP_CV, CF_OA_5Y, **smoothed_EY (+0.163 vs +0.143 — TOP)**, EY, Cash_MktCap, AdvCust_YoY.

2 indicators **regime-flip**: DY (pre-2014 -0.087, post-2014 +0.085); BY (1/PB) similar flip.

### Key insight cho STATE_VAR

- **FA signals WEAKER in crisis** (IC drops to +0.01-0.09 vs normal +0.10-0.20)
- **Don't flip in crisis**, just attenuate
- → Fresh-Q gating logic in STATE_VAR sound: filter activates when FA matters less, prevents stale picks from causing harm
- **Cannot BA-sim 2008 GFC directly** (need daily prices, ticker_financial only has quarterly Close)
- But FA principles confirmed robust across 20 years
