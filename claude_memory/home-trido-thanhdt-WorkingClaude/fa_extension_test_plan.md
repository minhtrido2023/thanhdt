---
name: FA-system extension test plan (pending)
description: 6 fundamental-analysis extensions queued for backtest against FA-system baseline; user wants me to remind them if forgotten
type: project
originSessionId: 762b6179-ddcb-41b7-ac2b-ee8d2f143ccc
---
# FA-system extensions — backtest in progress

**Started:** 2026-05-12. User asked Claude to test each of the 6 missing FA perspectives identified in conversation and report effectiveness.

## Evaluation framework
- Baseline: `fundamental_rating.py` (7-axis, 343 lines)
- Metric: forward `profit_3M` median/mean/winrate per tier; tier ordering must rank A > B > C > D > E
- Universe: same liquidity filter (Volume_3M_P50 × Close ≥ 1B VND)
- Cohort: Q4-only (canonical), all-quarters as secondary check
- Compare: tier separation = median(A) − median(E), plus mean spread and monotonicity

## Tests queued

| # | Test | Indicators | New column(s) | Where added |
|---|------|------------|---------------|-------------|
| 1 | Margin trajectory | GPM_P0..P7 slope, NPM_P0/P4 delta, EBITM_P0/P4 delta | `GPM_slope`, `NPM_delta`, `EBITM_delta` | growth axis or new "margin" axis |
| 2 | Beneish-lite M | DSO_P0/P4 delta, GPM_P0/P4 delta, FinLev_P0/P4 delta, AssetTurn delta | `M_score` composite | health or quality axis |
| 3 | Working capital | CashCycle_P4 − CashCycle_P0, AssetTurn_P0 − AssetTurn_P4, InvTurn delta | `CashCycle_impr`, `AssetTurn_impr` | quality axis |
| 4 | Solvency depth | (StDebt_P0 + LtDebt_P0 − Cash_P0)/EBITDA_P0, ST/Total debt, Altman Z'' | `NetDebt_EBITDA`, `ST_Total_Debt`, `Altman_Z` | health axis |
| 5 | ROIC trend | ROIC_Trailing vs ROIC5Y delta (ROIIC proxy) | `ROIC_trend` | quality axis |
| 6 | Industry modifier | Re-weight axes per ICB_Code (NH/CK/BH/CT) | weight schema | architectural |

## Data availability notes
- AR_P0 only one snapshot — can't do AR/Rev divergence trend, skip or use as point-in-time ratio
- OShares only one snapshot — can't do dilution trend within single row; would need cross-quarter pull
- ROIIC ideal needs ΔNOPAT/ΔIC over 5Y but totalAsset_P0 only one snapshot → use ROIC_Trailing vs ROIC5Y as proxy

## Status
- [ ] Baseline numbers (current run)
- [ ] Test 1 Margin trajectory
- [ ] Test 2 Beneish-lite
- [ ] Test 3 Working capital
- [ ] Test 4 Solvency depth
- [ ] Test 5 ROIC trend
- [ ] Test 6 Industry modifier
- [ ] Consolidated v5 recommendation

## How to resume / remind user
If conversation drops or user asks "where were we with FA extensions" / "FA testing" / "trục mới cho FA":
1. Read this file
2. Check todo list status
3. Look in `WorkingClaude/` for `test_fa_ext_*.py` scripts and `fa_ext_results.csv`
4. Resume from first unchecked box

User explicitly said: "bạn chạy thử từng góc nhìn... rồi lại tiếp tục nhớ nhắc tôi nếu tôi quên"
