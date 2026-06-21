# LAGGED_POS — HL_3y Production Spec

**Status**: ✅ Validated lookahead-free, paper-trade live from 2026-04-01
**Date**: 2026-05-20

## Naming convention (locked)

| Casual | Formal | Architecture | Status |
|---|---|---|---|
| **v11** | BA v11 "Song Sinh" 🐦 | BAL + VN30 + ETF | Production current (19.42% / Sh 1.32 / DD -19%) |
| **v12** | BA v12 "Âm Dương" ☯️ | BAL + **LAGGED HL_3y** + ETF | Deploy candidate ⭐ (21.37% / Sh 1.67 / DD -14.9%) |
| **v12 light** | BA v12L "Âm Dương nhẹ" | BAL40 + LAGGED10 + ETF | Bull-year resilient variant (21.36% / Sh 1.56) |
| v13 | BA v13 "Tam Thế" 🔱 | +1 strategy mới | Future |
| v14 | BA v14 "Tứ Trụ" 🏛️ | 4 strategies | Future |

**v12 vs v11 key wins** (12y backtest):
- CAGR: 19.42% → **21.37%** (+1.95pp)
- Sharpe: 1.32 → **1.67** (+0.35, +26%)
- MaxDD: −19.0% → **−14.9%** (better 22%)
- Y2022 bear: −12.95% → **−3.07%** (+9.88pp defensive)
- 12y Wealth: 8.98x → **10.96x** (+22%)
- Capacity sweet spot: **50-100B** (above 200B degrades)
- Trade-off: Y2025 bull lag −16.6pp (acceptable given annual win rate 8/12)

## Core idea

Mua stock ở **T+5 trading days sau ngày báo cáo tài chính tốt** (NP_R ≥ 15%), hold 25 days, sell ở T+30 Open. Universe = tickers có lịch sử post-release drift ≥ 5% trung bình (weighted exp decay 3-year half-life).

## Strategy params (validated CAND_B + post_min_5)

| Param | Value |
|---|---|
| `HALF_LIFE_YEARS` | **3.0** (exp decay weight, user-picked match VN earnings cycle 3-5y) |
| `POST_RET_MIN` | **5.0** (was 8.0 — broader universe with HL_3y quality filtering) |
| `N_GOOD_MIN` | **4** (min prior good events) |
| `NPR_MIN` | 0.15 (15% NP YoY) |
| `ENTRY_OFFSET` | 5 trading days after Release_Date |
| `HOLD_DAYS` | 25 trading days |
| `MAX_POSITIONS` | 12 concurrent |
| `POS_PCT` | 0.08 (8% NAV/position) |
| `LIQ_MIN_VND` | 2e9 (2B/day) |
| `LIQ_CAP_PCT` | 0.20 (20% ADV cap) |
| `MAX_FILL_DAYS` | 5 |
| Slip in/out, tax | 0.1% / 0.15% / 0.1% |
| Deposit rate | 1%/yr cash |

## Profile computation (HL_3y exp decay, NO LOOKAHEAD)

For each event i of ticker tk, compute `prior_avg_post_good` using only events j < i (sorted by Release_Date):

```python
for j in good_events_before_i:
    age_yrs = (release_date_i - release_date_j).days / 365.25
    weight_j = exp(-ln(2) × age_yrs / 3.0)
prior_avg_post_good = sum(post_ret_j × weight_j) / sum(weight_j)
```

**Lookahead-free verification (2026-05-20)**:
- STRICT_BUFFER test (only include events with ≥45 day maturation): IDENTICAL result (17.05% CAGR)
- Only 3 events affected by buffer (out of 52,950). Quarterly cadence >> 42-day post window
- T+45 entry test confirmed alpha is structurally in T+5→T+30 window

## Backtest performance

### Honest 12y (2014-04 → 2026-05)

| Metric | Value | Note |
|---|---|---|
| CAGR | **17.05%** (default) / **19.33%** (post_min_5 winner) | Approaching BA v11 19.42% |
| Sharpe | **1.41** (default) / **1.43** (winner) | |
| MaxDD | −17.59% (default) / **−15.7%** (winner) | Better than BA v11 (−18.96%) |
| Calmar | 0.97 / **1.23** | |
| Annual WR | 12/12 years positive | No negative years |
| Worst year | 2015 +0.72% | |
| Best year | 2021 +122% | |

### Walk-forward OOS (HL_3y CAND_B baseline)

| Window | CAGR | Sharpe | Note |
|---|---|---|---|
| P2_OOS 19-26 | **+25.60%** | 1.74 | Strong |
| P4_OOS 21-26 | **+31.91%** | 1.81 | Strongest |
| P6_OOS 23-26 | +24.11% | 1.40 | Calmar 1.90 best |

**OOS ALWAYS beats IS** — strategy matures with universe history, not overfit.

### Defensive performance

| Period | LAGGED HL_3y | BA v11 | VNI | Note |
|---|---|---|---|---|
| Y2022 (bear) | **+7.77%** | −12.95% | −34.39% | LAGGED defensive WIN |
| Q1 2026 (recovery rally) | **+9.21%** | −5.41% | +25.28% | LAGGED captures, BA misses |

## Universe stats

- Total events 2009-2026: 52,950
- Events with prior_n_good ≥ 4: 39,958
- Qualified events (HL_3y ≥ 5% + n ≥ 4): ~12,000 over 16 years
- Universe size at any time: ~80-200 tickers (varies)

## Comparison vs other variants (12y)

| Profile | CAGR | Sharpe | DD | Verdict |
|---|---|---|---|---|
| EQUAL (cũ) | 13.09% | 1.16 | −22.4% | baseline |
| **HL_3y** | **17.05%** | **1.41** | **−17.6%** | ⭐ winner |
| HL_2y | 16.31% | 1.39 | −18.0% | sharper but less stable |
| HL_4y | 15.29% | 1.27 | −22.9% | too smooth |
| TIME_4y window | 17.25% | 1.51 | −17.0% | cliff effect issue |
| ROLL_N12 | 15.28% | 1.28 | −18.2% | |
| ROLL_N16 | 13.18% | 1.15 | −25.9% | poor |
| TREND filter | 9.51% | 1.05 | −20.2% | too restrictive |

## Tuning history (R3 results under HL_3y)

| Config | CAGR | Notes |
|---|---|---|
| **post_min_5** (winner Calmar) | **19.33%** | **Sh 1.43 / DD −15.7% / Cal 1.23** |
| pos_pct_0.12 (winner CAGR) | **20.65%** | DD −20.6% |
| max14_pos10 | 19.80% | |
| pos_pct_0.10 | 19.28% | |
| BASELINE (12/0.08) | 17.05% | |

## Why HL_3y works

User's hypothesis (validated): equal-weighted mean treats 10-year-old events same as recent → catches "stale alpha" tickers. HL_3y:

1. **Catches structural regime changes**: ticker tốt 5 năm trước nhưng giờ chết → filtered out
2. **Half-life 3y match VN earnings cycle** (3-5 năm typical)
3. **Smooth decay** (no cliff like ROLL or TIME window)
4. **Recent events weighted heavier** but old events still contribute

## Integration tests

| Test | Result | Verdict |
|---|---|---|
| LAGGED + BA v11 (BONUS bonus in score) | −0.16pp CAGR | ❌ no synergy |
| LAGGED + BA v11 (BLACK filter) | −1.02pp | ❌ hurts |
| LAGGED + BA v11 (BOTH) | −1.20pp | ❌ hurts most |
| Hybrid BA 80/20 LAGGED (EQUAL) | +0.12 Sh / −0.35pp CAGR | Mild trade-off |
| Hybrid BA 50/50 LAGGED (EQUAL) | +0.23 Sh / −0.91pp CAGR | Risk-adj win |
| Hybrid with HL_3y | **PENDING** | TBD |

## Files

| File | Purpose |
|---|---|
| `analyze_earnings_reaction.py` | Build event classification |
| `earnings_events_classified.csv` | 52,950 events |
| `lagged_pos_papertrade.py` | **Production paper-trade tracker (HL_3y)** |
| `validate_lagged_hl3y.py` | Walk-forward + tune + annual breakdown |
| `verify_hl3y_no_lookahead.py` | Lookahead verification |
| `test_lagged_timedecay.py` | 8 variants comparison |
| `lagged_paper_state.json` | Current paper-trade state |

## Paper-trade live status (as of 2026-05-20)

- Started: 2026-04-01 (49 days running)
- NAV: 49.50B (−1.00% vs 50B init)
- Open positions: 8 (HCM +14%, PVP +7%, others mixed)
- Closed: 4 trades, WR 25%, avg −1.07%
- VNI same period: +12.33% → Alpha −13.33pp (vs −17.74pp with old EQUAL filter)
- Cash buffer: 18.1B (37%) — has flexibility for new signals

## Production deploy decision

✅ **HL_3y is production-ready** for LAGGED_POS standalone or as overlay
❌ **Don't integrate into BA v11 score** (proven no synergy)
🤔 **Hybrid weight test pending** — to find optimal 70/30 / 80/20 / 50/50 split

## Caveat

- Strategy works best in **bear/sideways/flat regime**
- **Worst in euphoric bull** (+5 to +20% VNI) — gets bypassed by broad rally
- Current Q2 2026 is a STRONG bull recovery → LAGGED bound to underperform near-term
- Re-evaluate after 6 months of paper-trade (~Q3 2026)
