---
name: FA-system v6b spec (validated tier-level)
description: v6b adopt smoothed_EY valuation + rescued health + drop noise; A median 6.67→7.45%, all axes positive IC
type: project
originSessionId: 762b6179-ddcb-41b7-ac2b-ee8d2f143ccc
---
# FA-system v6b — final spec after multi-round exploration

**Script:** `test_fa_v6_combo.py` (test) | output csv pending generation
**Date:** 2026-05-13 | predecessor: v4 (production), v5 H3+H4 (rejected on canonical sim)

## Performance vs v4 baseline (Q4 forward profit_3M, 3,313 rows)

| Metric | v4 | v6b | Δ |
|---|---|---|---|
| A median | 6.67% | **7.45%** | +0.78pp |
| A mean | 7.31% | **8.11%** | +0.80pp |
| A WR | 66.3% | **67.7%** | +1.4pp |
| E median | -3.76% | -4.26% | -0.50 (deeper) |
| A−E spread | 10.43 | **11.71** | +1.28 |
| Monotonicity | ✓ | ✓ | |

## Key changes vs v4

### 1. Valuation axis — REDESIGNED (was IC -0.001 = noise, now +0.105)
**Replace v4's 6 z-score indicators with 3 yield-based indicators:**
- `smoothed_EY = mean(NP_P0..P3) / (OShares × Close)` — Shiller-style smoothed earnings yield (IC +0.124, BEST single indicator across all axes)
- `FCF_yield = sum(CF_OA_P0..P3 + CF_Invest_P0..P3) / MktCap` (IC +0.067)
- `magic_formula = mean(rank(ROIC5Y), rank(1/PE))` — Greenblatt (IC +0.072)

**Why v4 valuation failed:** PE_self_z, PB_self_z etc. are mean-reversion z-scores. They flip sign across periods (-0.036 P1 → +0.014 P2). Regime-dependent noise.

### 2. Health axis — RESCUED (was IC -0.045 = anti-signal, now +0.096)
**Replace Debt_Eq/IntCov/CashR with proper-direction balance sheet indicators:**
- `Cash_MktCap = Cash_P0 / MktCap` — balance sheet strength yield (IC +0.087, **new discovery**)
- `NetDebt_EBITDA_inv = -(StDebt + LtDebt - Cash) / EBITDA` (IC after inv +0.062)
- `IntCov_inv = -IntCov_P0` — **VN-specific: low IntCov = better** (boring stable cos underperform, IC after inv +0.083)

**Why v4 health failed:** Debt_Eq inverted backwards (in VN low-debt = boring = underperform). IntCov negative IC stable 11/12 years. v4 had it conceptually right (low debt good) but VN reality is opposite.

### 3. Drop noise indicators
- `FSCORE` (quality axis): IC +0.003 = essentially zero
- `NP_R` (growth axis): IC +0.023 = noise
- `Revenue_YoY_P0` (growth axis): IC +0.005 = noise

### 4. Keep v4 axis weights
IC-implied weights tested (v6c) but HURT — they overfit. v4 weights (quality 0.18 / stability 0.18 / cash 0.18 / shareholder 0.15 / growth 0.13 / health 0.08 / valuation 0.10) are near-optimal after redesign.

### 5. Skip MEGA-A elite sub-tier
v4 elite filter (A + stab_top_Q) gave WR 75.7%. **In v6 it doesn't help** — A tier already absorbs stability signal through redesigned axes (WR 67.7%). MEGA-A becomes redundant.

## Axis-level IC: all positive in v6

| Axis | v4 IC | v6 IC | Change |
|---|---|---|---|
| stability | +0.114 | +0.115 | ~ |
| shareholder | +0.108 | +0.109 | ~ |
| quality | +0.106 | +0.099 | -0.007 |
| cash | +0.104 | +0.095 | -0.009 |
| **valuation** | -0.001 | **+0.105** | **+0.106** 🚀 |
| **health** | -0.045 | **+0.096** | **+0.141** 🚀 |
| growth | +0.058 | +0.074 | +0.016 |

## Status

- [x] Tier-level validation (forward profit_3M) ✓
- [ ] Generate production CSV (fundamental_rating_v6.csv)
- [ ] Upload BQ table `tav2_bq.fa_ratings_v6`
- [ ] **WARNING:** v5 H3+H4 also won tier-level but FAILED canonical BA sim due to interactions with v10 scoring (Fin/RE bonus). v6 will likely have similar/worse impact on BA-system. User decided to focus on FA accuracy first, then re-tune BA v11.
- [ ] Next: canonical BA sim validation + plan v11 BA re-tune

## Reference indicator IC table (v6 single indicators)

**Valuation (new):**
- smoothed_EY: +0.124 stable ✓✓
- magic_formula: +0.072 stable ✓
- FCF_yield: +0.067 stable ✓

**Health (rescued):**
- Cash_MktCap: +0.087 (strong in P2, weak in P1 — regime concern)
- IntCov_inv: +0.083 stable across periods
- NetDebt_EBITDA_inv: +0.062 (mostly P2)

**Drop these (IC ~0 or noise):**
- FSCORE, NP_R, Revenue_YoY_P0, all v4 valuation, Debt_Eq_P0, CashR_P0, LT_CAGR (-0.023 noise)
