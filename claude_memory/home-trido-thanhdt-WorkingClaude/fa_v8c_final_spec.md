---
name: FA-system v8c_final spec (sector-specific sub-system)
description: Final FA spec với 6 sub-sector schemas; wins ở 6M/1Y/2Y horizons; tied ở 3M
type: project
originSessionId: 762b6179-ddcb-41b7-ac2b-ee8d2f143ccc
---
# FA-system v8c_final — selective sub-sector schemas

**Date:** 2026-05-13 | Scripts: `test_fa_v8c_full.py`, `test_fa_v8c_kcn_fix.py`, `test_fa_v8c_final.py`
**Status:** Tier-level validated. DEFERRED deployment until BA v11 re-tune (v5/v8 đã FAIL canonical BA sim).

## Sub-sector classification

```python
def get_subsector(icb_code, ticker):
    if icb_code == 8355:               return "BANK"
    if icb_code in (8775, 8777):       return "SECURITIES"
    if icb_code == 8536:               return "INSURANCE"
    if icb_code in (8633, 8637):
        if ticker in RESIDENTIAL_TICKERS: return "REIT_RES"
        return "REIT"  # KCN + everything else REIT
    if icb_code == 3353:               return "BLACKLIST_AUTO"  # force E tier
    return "DEFAULT"

RESIDENTIAL_TICKERS = {"VHM","NVL","DXG","KDH","NLG","AGG","KHG","HDG","CRE","FLC",
                       "IJC","HDC","TIG","QCG","DIG","DXS","HQC","API","AAV","BII",
                       "C21","ITC","SCR","VPI","CEO","TCH","NTL"}
```

## Schemas (each weight sums to 1.0)

### BANK (ICB 8355) — Q+V simple
```
quality:     [ROE_Min5Y, ROE_Trailing]                     × 0.40
shareholder: [DY_adj, Dividend_Min3Y]                       × 0.20
valuation:   [smoothed_EY, BY]                              × 0.40
```

### SECURITIES (ICB 8775/8777) — growth-focused
```
quality:     [ROE_Min5Y, ROE_Trailing]                     × 0.20
stability:   [NP_CV]                                        × 0.10
shareholder: [DY_adj, Dividend_Min3Y]                       × 0.10
growth:      [NP_R, NP_TTM_growth, NP_peak_ratio] (POS!)    × 0.35
valuation:   [smoothed_EY, BY]                              × 0.25
```

### INSURANCE (ICB 8536) — same as BANK (limited N=28 data)
```
quality:     [ROE_Min5Y, ROE_Trailing]                     × 0.40
shareholder: [DY_adj, Dividend_Min3Y]                       × 0.20
valuation:   [smoothed_EY, BY]                              × 0.40
```

### REIT_RES (residential developers, manual list) — value-quality
```
quality:     [ROE_Min5Y, ROIC5Y]                           × 0.25
valuation:   [smoothed_EY, EY, CFY]                         × 0.40
stability:   [NP_CV]                                        × 0.15
shareholder: [DY_adj, Dividend_Min3Y]                       × 0.10
growth:      [NP_peak_ratio]                                × 0.10
```

### REIT (ICB 8633/8637 non-RES — includes KCN, other dev) — v8b custom
```
quality:     [ROE_Min5Y, ROE_Trailing]                     × 0.20
cash:        [CF_OA_5Y, FCF_yield]                          × 0.20
shareholder: [DY_adj, Dividend_Min3Y, DY_sust]              × 0.20
valuation:   [smoothed_EY, BY, magic_pb]                    × 0.40
```

### DEFAULT (everything else) — v6b universal (within-sub-sector ranking)
```
quality:     [ROIC5Y, ROE_Min5Y]                           × 0.18
stability:   [NP_CV, Rev_CV, LT_CAGR]                       × 0.18
cash:        [CF_OA_5Y, CFOA_NP]                            × 0.18
shareholder: [DY_adj, Dividend_Min3Y, FCF_OA_ratio, DY_sust]× 0.15
growth:      [GPM_change, NP_peak_ratio, Rev_peak_ratio]    × 0.13
health:      [Cash_MktCap, NetDebt_EBITDA_inv, IntCov_inv]  × 0.08
valuation:   [smoothed_EY, FCF_yield, magic_pe]             × 0.10
```

### BLACKLIST_AUTO (ICB 3353)
- Force tier="E" — all FA signals are anti-predictive for VN auto sector (5/5 indicators with IC -0.22 to -0.26)
- N=42 obs; manual exclusion

## Tier assignment

Rank within (quarter, sub-sector) → tier:
- A: top 10% (pct ≥ 0.90)
- B: 70-90%
- C: 40-70%
- D: 15-40%
- E: bottom 15%

## Performance (validated on Q4 2014-2025, ~3000 obs)

### Overall tier ordering (profit_3M)

| Metric | v4 base | v6b | v8c_final |
|--------|---------|-----|-----------|
| A median | +6.67% | **+7.45%** | +7.39% |
| A WR | 66.3% | **67.7%** | 66.6% |
| A−E spread | 10.43 | **11.78** | 10.48 |

3M: v8c_final tied with v6b (slight loss on spread).

### Multi-horizon — v8c_final wins all longer horizons

| Horizon | v6b IC | v8c_final IC | Δ |
|---------|--------|--------------|---|
| profit_3M | +0.149 | +0.152 | +0.003 |
| **O6M** | +0.093 | **+0.113** | **+0.020** ✓ |
| **O1Y** | +0.092 | **+0.105** | **+0.013** ✓ |
| **O2Y** | +0.160 | **+0.174** | **+0.014** ✓ |

### Per-sub-sector A tier (v8c_final)

| Sub | A N | A median | A WR | Notes |
|---|---|---|---|---|
| SECURITIES | 26 | **+13.22%** | 65.4% | v6b had 0/237 in A |
| REIT_RES | 24 | **+10.91%** | **75.0%** | cleanest tier anywhere |
| BANK | 25 | +9.99% | 68.0% | fix v4 "B beats A" issue |
| DEFAULT | 186 | +7.43% | 67.7% | similar to v6b A |
| REIT | 40 | +5.58% | 57.5% | KCN absorbed (acceptable) |
| INSURANCE | 10 | +3.35% | 60% | small data |

## Key insights from exploration

1. **Sector-IC patterns are real but require sub-sector schemas, NOT weight tuning**
   - v5/v7 attempted weight-only tuning → FAIL (aggregation issue)
   - v8 with bespoke INDICATORS per sector → WIN

2. **Different sectors have fundamentally different signal structures:**
   - Banks: Quality + Value
   - Securities: GROWTH (counter-intuitive vs banks!)
   - REIT_RES: Value + Quality classical
   - REIT_KCN: tried growth-cash, broke — KCN too noisy at N=91
   - Materials: Cash flow dominant
   - Auto: ALL signals anti — blacklist

3. **FA signal strengthens at longer horizons** (smoothed_EY IC 0.081 at 3M → 0.182 at 2Y)
   → BA-system với hold dài (6M+) hấp thụ FA alpha tốt hơn

4. **"B beats A" syndrome** in some sectors (banks, KCN) — top decile by composite FA hits peaked-cycle stocks → mean revert. Fix: redesign indicators (banks: drop big-bank quality bias; KCN: stay broken — too noisy)

## Status & Next steps

- [x] Tier-level validation complete
- [ ] **DO NOT DEPLOY** to production yet — v5 and earlier attempts FAIL on canonical BA sim due to v10 scoring interactions
- [ ] Pending: BA v11 re-tune (separate work)

## ⏳ Pending future exploration

**Advance from customer data** — đặc biệt quan trọng cho REIT_KCN và residential developers:
- "Advance from customer" / "Người mua trả tiền trước" trên balance sheet = pre-sales backlog
- KEY indicator cho real estate cycle (booked but not recognized revenue)
- Sẽ giúp:
  - Fix KCN schema (early-cycle detection)
  - Improve REIT_RES timing
  - Phân biệt residential dev đang ở hot phase vs slow phase
- Currently NOT in `tav2_bq.ticker_financial` schema
- User sẽ thêm column này vào BQ → khi đó tiếp tục explore

## Resume next session

User confirmed: "khi có đủ dữ liệu về khoản mục advance from customer, chúng ta sẽ tiếp tục explore thêm. hôm nay chúng ta dừng ở đây, mai sẽ tiếp tục"

Next session actions (in priority):
1. Check if `advance_from_customer` (or similar) column added to BQ ticker_financial
2. If yes: rebuild KCN/REIT_RES schemas with pre-sales indicator
3. If no: continue with deployment planning OR BA v11 design
4. Possibly: deeper DEFAULT sub-pattern exploration (Industrials/Consumer/Tech sub-ICB)

---

## Update 2026-05-14

### BQ data confirmed available
26 new pre-sales columns added: `AdvCust_P0..P7`, `UnearnRev_P0..P7`, `Inventory_P0..P7`, `RE_Inventory`, `Close`, `Price`. Total 170 cols (was 144).

### Pre-sales IC findings (Q4 universe, ~3000 obs)
- **AdvCust_MktCap_yld** = AdvCust_P0 / MktCap → IC +0.144 at 3M, **+0.176 at 2Y**
- **TotalBacklog_MktCap_yld** = (AdvCust + UnearnRev) / MktCap → IC +0.093 at 3M, **+0.181 at 2Y**
- Per sub-sector:
  - REIT_KCN: AdvCust_MktCap_yld IC **+0.152** (top finding for KCN)
  - REIT_RES: AdvCust_MktCap_yld IC +0.105
  - REIT_OTHER: AdvCust_accel IC **-0.190** (anti-signal — momentum mean reverts)
  - DEFAULT (non-RE): pre-sales irrelevant (IC < 0.08)
- **Pre-sales work as VALUE indicator** (per market cap), not as growth rate. High backlog/MktCap = under-priced.

### KCN diagnosis — sector cycle problem
- All-KCN @ 3M: Mean **-3.88%**, Median -3.06%, WR **39.2%** (negative-expected!)
- All-KCN @ 1Y: Mean **+18.51%**, WR 61%
- All-KCN @ 2Y: Mean **+39.54%**, WR 55%
- → KCN needs LONG hold for FA alpha to compound. 3M too short for pre-sales → revenue cycle.

### KCN exclusion test for BA-45d (CONTRARY result)
Tested BA canonical sim WITH vs WITHOUT KCN tickers:
- FULL 2014-2026: WITH_KCN 16.87% / NO_KCN 16.06% (Δ -0.81pp)
- OOS 2024-2026: WITH_KCN 24.26% / NO_KCN 22.11% (Δ -2.15pp)
- → **Excluding KCN HURTS BA-45d empirically**, despite tier-level KCN being negative.
- Why: BA selects via TA+state+FA combo, not pure FA tier. TA momentum catches KCN good moments. Sector_limit 8:4 already caps exposure.

### Critical lesson (3rd confirmation)
**Tier-level FA analysis ≠ portfolio-level decisions**. Must [REDACTED] validate at canonical sim level.
1. v5 H3+H4 won tier-level, failed canonical sim
2. v7 sector weights won IC, failed tier ordering
3. KCN tier-level "bad", BA sim shows "actually good"

### Decision for BA-45d
- **KEEP KCN inclusive** in BA-45d universe
- v8c_final stays as documented (KCN merged into REIT bucket — current approach correct)
- DON'T deploy ba_ticker_filters.py KCN exclusion
- File `ba_ticker_filters.py` kept as template for long-hold session (which has opposite filter need)

### Long-hold strategy spawned to separate session
KCN/pre-sales alpha properly belongs in 6M-2Y hold strategy. New session spawned 2026-05-14 to design long-hold FA portfolio without touching BA scoring v10.

### Files reference
- `test_fa_presales_ic.py` — pre-sales IC analysis
- `test_fa_kcn_with_advcust.py` — KCN schema with pre-sales (V4 winner: IC +0.141, spread +15.80)
- `test_fa_kcn_diagnose.py` — sector cycle diagnosis
- `test_ba_kcn_exclusion.py` — BA canonical sim with/without KCN (confirms keep)
- `ba_ticker_filters.py` — exclusion module (NOT deployed for BA-45d; reserved for long-hold)

---

## Update 2026-05-14 — BA v11 build ATTEMPTED + FAILED on canonical sim

Script: `fundamental_rating_v8c.py`, `compare_ba_v11_vs_v10.py`, `compare_ba_v11b_v11c.py`
BQ table: `tav2_bq.fa_ratings_v8c` uploaded (12,606 rows)

### Phase 1 IC diagnostic (2014-2026 sub-periods)
12 timeless indicators confirmed across P2/P3/P4:
- smoothed_EY (+0.10 / +0.14 / +0.21, accelerating)
- NP_peak_ratio, IntCov_inv, NP_R, Cash_MktCap (all +0.10+ FULL)
- valuation_v6 axis IC +0.135 (vs v4 +0.048) — 2.8x improvement
- health_v6 axis IC +0.109 (vs v4 -0.053) — rescued
3 regime-flip: DY_adj, BY (1/PB), AdvCust_MktCap_yld universal

⚠ Data limit: `ticker` table only 2014+ (no pre-2014 prices). Cannot OOS test 2008 GFC without extending price data.

### Phase 2 BA v11 build — 3 variants tested
SIGNAL_V11 = SIGNAL_V10 modified:
- v11a: swap FA source v4 → v8c + DROP Fin/RE +10/-10 modifier
- v11b: swap FA source only (KEEP modifier)
- v11c: v11b + lower TA thresholds (170→165, 155→150)

### Results vs v10+v4 baseline

| Variant | FULL CAGR | FULL Sharpe | FULL DD | OOS CAGR | OOS Sharpe |
|---|---|---|---|---|---|
| **v10+v4 (baseline)** | **16.87%** | **1.18** | **-13.5%** | **24.26%** | **1.28** |
| v11a | 16.97 | 1.09 | -21.5 | 21.74 | 0.96 |
| v11b | 16.44 | 1.05 | -21.3 | 25.43 | 1.06 |
| v11c | 15.66 | 1.05 | -17.9 | 20.14 | 1.05 |

ALL 3 variants WORSE on Sharpe and MaxDD. v11b OOS CAGR +1.17pp but Sharpe -0.22.

### Root cause analysis (4th confirmation)
v10+v4 is **co-evolved optimum** for BA-45d. Tier-level FA improvements break:
1. SIGNAL_V10 + Fin/RE modifier tuned for v4 distribution
2. v8c shifts Securities/REIT into A → conflict with sector_limit 8:4
3. 45d hold too short for FA quality alpha (IC 0.08 at 3M vs 0.18 at 2Y)
4. Higher financial diversification → correlated drawdowns

### FINAL DECISION for BA-45d production

✅ **KEEP v10 + v4 FA** (current production stays)
- Stable 17.15% CAGR, Sharpe 1.21
- Risk-adjusted optimal for 45d hold
- Don't deploy any v11 variant

✅ **v8c spec STAYS DOCUMENTED** for:
- Long-hold strategy (separate session — LH-system built, CAGR 16.73%, OOS +23.5%)
- Live screening discovery in recommend_holistic.py (use v8c findings as filters before BA selection)

❌ **DON'T deploy** v8c to BA-45d production
❌ **DON'T extend** ticker prices to pre-2014 (data limit not blocking; v10+v4 baseline robust)

### Key insight crystallized
**FA improvements and BA improvements are SEPARATE optimization problems**.
- FA = stock ranking quality (tier ordering metrics)
- BA = portfolio construction for 45d hold
- BA system has co-evolved with v4 FA over 15 rounds
- Cannot blindly substitute FA → must redesign entire BA pipeline jointly
- For BA-45d: keep v10+v4 stable; FA exploration adds value in **separate long-hold strategy**, not as drop-in BA replacement
