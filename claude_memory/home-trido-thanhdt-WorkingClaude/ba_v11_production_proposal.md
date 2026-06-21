---
name: BA v11 production proposal — STATE_VAR + P3 + state-tight Fresh-Q
description: Combined filter stack tested. V4 winner +2.50pp FULL CAGR, +3.20pp OOS, all 3 periods consistent improvement
type: project
originSessionId: 762b6179-ddcb-41b7-ac2b-ee8d2f143ccc
---
# BA v11 production candidate — V4 (SV_TIGHT + P3)

**Script**: `test_state_var_with_p3.py` | NAV: `ba_state_p3_combinations.csv` | log: `state_p3_results.txt`
**Date**: 2026-05-14

## Spec

```python
# In recommend_holistic.py / SIGNAL_V10 → SIGNAL_V11
def filter_v11(cand, state5_today, vni_close_today, vni_ma200_today):
    # P3: skip new bull buys when VNI/MA200 > 1.30 (overheated)
    if vni_ma200_today > 0 and vni_close_today / vni_ma200_today > 1.30:
        BUY_TYPES = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S",
                     "MOMENTUM_QUALITY","DEEP_VALUE_RECOVERY","S_PRO"}
        cand = cand[~cand["play_type"].isin(BUY_TYPES)]

    # State-conditional Fresh-Q:
    if state5_today == 1:        # CRISIS
        return cand[cand["days_since_release"] <= 30]   # super tight
    if state5_today in (2, 3):   # BEAR/NEUTRAL
        return cand[cand["days_since_release"] <= 60]   # standard
    return cand   # BULL (4,5): no filter
```

## Performance (canonical 50/50 BAL+VN30, 2014-2026)

| Period | V0 baseline | V4 SV_TIGHT+P3 | Δ |
|--------|-------------|----------------|---|
| **FULL 2014-2026** | 16.87% / 1.18 / -13.5% | **19.37% / 1.37 / -16.1%** | **+2.50pp / +0.20 Sh** |
| **OOS 2024-2026** | 24.26% / 1.28 / -13.0% | **27.45% / 1.54 / -10.9%** | **+3.20pp / +0.26 / DD-2.1pp better** |
| **Pre-OOS 2014-19** | 7.31% / 0.88 / -13.1% | **9.71% / 1.63 / -7.6%** | **+2.40pp / +0.74 Sh** |

## Why it works (stacking decomposition)

Two filters operate on independent mechanisms:
- **STATE_VAR** (Fresh-Q gating in non-BULL): blocks stale FA picks when market regime makes FA quality matter more
- **P3** (overheated guard): blocks new buys when broad market is at extension (VNI/MA200 > 1.30)

| Filter alone | Δ CAGR FULL |
|--------------|-------------|
| V1 STATE_VAR | +1.25pp |
| V2 P3 | +1.35pp |
| V3 STATE_VAR + P3 | +2.09pp (≈ sum minus small overlap) |
| **V4 SV_TIGHT + P3** | **+2.50pp** (+0.41pp from tightening state-1 to 30d) |

Both filters near-additive → operating on different signal failures.

## Variant comparison (all + P3)

| Variant | FULL CAGR | FULL Sharpe | OOS CAGR | OOS Sharpe |
|---------|-----------|-------------|----------|------------|
| V3 STATE_VAR(60/60/60) | +2.09 | +0.16 | +3.37 | +0.25 |
| **V4 SV_TIGHT(30/60/60) ✓ pick** | **+2.50** | **+0.20** | +3.20 | +0.26 |
| V5 SV_TIGHT_ALL(30/30/30) | +0.83 | +0.17 | +3.27 | +0.32 (best Sh) |
| V6 SV_LOOSE(60/60/90) | +1.37 | +0.14 | +2.21 | +0.24 |

V4 is the sweet spot: tight on state-1 (CRISIS, when FA noise highest), standard on state-2/3.
V5 over-filters (state-2/3 doesn't need 30d). V6 under-filters.

## Drawdown trade-off

| Metric | V0 | V4 |
|--------|----|----|
| FULL MaxDD | -13.5% | -16.1% (worse 2.6pp) |
| OOS MaxDD | -13.0% | -10.9% (better 2.1pp) |
| Pre-OOS MaxDD | -13.1% | -7.6% (much better 5.5pp) |

V4 has SLIGHTLY worse FULL MaxDD but BETTER OOS and Pre-OOS DD.

Cause: pre-2018 trade war period DD pattern shifted by P3 (avoided some recovery rallies). Post-2018 era V4 has cleaner DD.

## Production deployment plan

1. **Modify** `recommend_holistic.py`:
   - Replace `FRESH_Q_MAX_DAYS = 60` constant with state-conditional function
   - Add P3 overheated filter (compute VNI/MA200 in classify step)
2. **Live shadow test** 2-4 weeks: log both v10 picks and v11 picks, compare
3. **Switch to v11** if shadow test confirms expected reduction in stale picks
4. **Monitor**: tracking metrics on:
   - Days where Fresh-Q filter activates
   - Days where P3 blocks buys
   - Picks made under each regime

## DEPLOYMENT STATUS — 2026-05-15

### ✅ DEPLOYED TO PRODUCTION

User approved V11 (V4_COMPOSITE + SV_TIGHT) deploy on 2026-05-15. Implementation in `recommend_holistic.py`:

**Code changes:**
- Added constants: `BUY_TIERS_V11`, `FRESH_Q_BY_STATE`, `P3_VNI_MA200_THRESHOLD = 1.30`, `P3_VNI_RSI_THRESHOLD = 0.75`
- Added query: `VNI_OVERHEAT_QUERY` (fetches VNI Close, MA200, ratio, D_RSI for target date)
- Modified `select_book()`: accepts `state5_today`, `vni_ma200_ratio`, `vni_d_rsi` parameters; implements V11 filter logic
- Modified `main()`: fetches VNI overheat metrics, passes to select_book for both BAL and VN30 books

**Validation:**
- Synthetic test of 6 scenarios all PASS:
  1. BULL no overheat → no filter (6 picks)
  2. NEUTRAL → SV_TIGHT 60d removes 3 stale (6 picks)
  3. CRISIS → SV_TIGHT 30d removes 7 stale (2 picks — strict)
  4. State5=5 + ratio=1.35 → P3 blocks all 9 buys (0 picks)
  5. State=4 + ratio=1.35 + RSI=0.78 → P3 via RSI blocks all (0 picks)
  6. State=4 + ratio=1.35 + RSI=0.65 → no regime confirm → no filter (6 picks ✓)

**Pre-existing issue (unrelated to V11)**: `tav2_bq.ticker_1m` table missing from BQ — SCORE_SQL's UNION ALL fallback fails. Affects live `recommend_holistic.py` invocation but not V11 logic itself. Fix separately.

## ⏳ Pre-2014 stress test — pending tomorrow (2026-05-16)

User will upload pre-2014 daily ticker prices. When ready:

1. Verify pre-2014 data: `bq query "SELECT MIN(time), MAX(time) FROM tav2_bq.ticker"`
2. Verify pre-2014 VNINDEX data (needed for VNI/MA200 ratio)
3. Verify `vnindex_5state` extends pre-2014 (already has state5 from 2007 per ticker_financial Close data)
4. Adapt `test_state_var_with_p3.py` with START_DATE = "2007-01-01"
5. Test V11 (V4_COMPOSITE) vs v10 baseline on 2007-2013 era
6. Critical periods to validate:
   - 2008 Q3-Q4 GFC (mean VNI -8.7% per ticker_financial quarterly returns)
   - 2011 inflation crisis (state5 was BEAR for 37+106d)
   - 2012 sideways (multiple BEAR windows)
7. Document results here under new "Pre-2014 stress test results" section
8. Verdict criteria:
   - GREEN: V11 beats v10 in 2008 GFC + 2011 crisis (DD better, CAGR comparable)
   - YELLOW: marginal improvement — note caveat
   - RED: V11 breaks in 2008-2011 — investigate regime drift

## Comparison to v8c FA path

Earlier this session attempted BA v11 = SIGNAL_V10 + v8c FA → all variants FAILED canonical sim (Sharpe/DD worse).
This v11 = SIGNAL_V10 + v4 FA + STATE_VAR/P3 filter improvements → WINS all metrics.

**Different design philosophy**:
- v8c attempted to improve picks at the TIER level (FA refactor) → broke BA co-evolution
- V4 SV+P3 improves picks at the TIMING level (filter when to apply) → respects BA co-evolution

→ Filter timing (when to skip) > Pick quality refactor (FA tier rework) for BA-45d production.

## Pending validations

- [ ] Implement in `recommend_holistic.py` (production code change)
- [ ] Test live picks for 2-4 weeks before full switch
- [ ] Monitor 2025-H2-2026 Q1 BEAR period was the recent trigger — confirm V4 captures the alpha live

## Pre-2014 stress test (when daily prices uploaded)

User plans to upload pre-2014 daily prices. When available, run:
- `compare_ba_canonical_v4_vs_v5.py` template extended to 2007-2013
- Test V4 (SV_TIGHT + P3) performance during 2008 GFC, 2011 inflation
- State5 model needs retro-fit for pre-2014 (already has data per `vnindex_5state` 2007-2013)
- VNI/MA200 ratio needs pre-2014 VNI (need full pre-2014 VNINDEX from user upload)

## Dynamic overheat threshold test (2026-05-14)

Script: `test_v4_dynamic_overheat.py` | NAVs: `ba_v4_dynamic_overheat.csv`

Tested 8 dynamic threshold variants vs V4_BASE (static 1.30):

| Variant | FULL Δ CAGR | OOS Δ CAGR | Verdict |
|---------|-------------|------------|---------|
| **V4_BASE (1.30 static)** | — | — | **Winner overall** |
| V4_STATE_AWARE (1.20 in state5, 1.30 in state4) | +0.12 | +0.78 | Marginal — same as base in practice |
| V4_TREND_RISING + >1.30 | +0.07 | -0.08 | ≈ base (most >1.30 days are rising) |
| V4_HIGHER (1.40) | -0.90 | -0.81 | Under-filter |
| V4_LOWER (1.25) | -0.72 | +0.46 | Mixed, over-defensive on FULL |
| V4_LOWER-2 (1.20) | -4.27 | -1.02 | Way over-defensive |
| V4_PERC90_5Y | -5.02 | -0.58 | Adaptive overfits |
| V4_PERC95_5Y | -3.01 | **+1.22** | OOS best but FULL/Pre-OOS bad |
| V4_GRADIENT | -1.01 | +1.11 | Inconsistent across periods |

### Why static 1.30 wins

1. **Only 31 overheated days in 12 years** (~0.5% trading) → too few data points to fit dynamic logic
2. **Adaptive percentile overfits to recent** — early years (2014-2018) have short history baseline
3. **State-aware logic identical in practice** — state 5 + ratio 1.20-1.30 is too rare
4. **Lower thresholds (1.20, 1.25) over-defensive** — miss BULL rallies
5. **Higher (1.40) under-filters** — too late to react
6. **Trend-aware (rising) doesn't help** — most >1.30 days have ratio still rising

### Recommendation: keep V4_BASE static 1.30
- Simplicity wins
- Static threshold robust across all 4 test periods
- No clear improvement from dynamic logic
- Less overfit risk

## Adaptive overheat exploration (2026-05-14, robustness concerns)

User concern: "có cách nào adap kịp nếu market thay đổi?"

Script: `test_v4_adaptive_overheat.py` | NAVs: `ba_v4_adaptive_overheat.csv`

Tested 7 adaptive mechanisms:

| Variant | FULL Δ CAGR | OOS Δ CAGR | Mid Δ CAGR | Pre-OOS Δ |
|---------|-------------|------------|------------|-----------|
| **V4_BASE (1.30 static)** | — | — | — | — |
| **V4_COMPOSITE (1.30 + state5/RSI)** | **+0.40** | -0.45 | **+0.99** | **+0.73** |
| V4_ENSEMBLE (2 of 3 signals) | -0.61 | +0.60 | -1.48 | -1.05 |
| V4_STATE5_BUNDLE (5→4 transition) | -0.90 | -0.81 | -1.61 | -0.75 |
| V4_WALKFWD (5Y p95) | -3.01 | +1.22 | -5.30 | -4.10 |
| V4_ZSCORE_2SD | -3.36 | -0.40 | -5.50 | -4.09 |
| V4_ZSCORE_1.5SD | **-7.39** | -6.48 | **-11.75** | -4.50 |

### Key findings

1. **Aggressive adaptive (Z-score, percentile) DESTROYS alpha** (-3 to -7pp CAGR)
   - Rolling baselines trượt với recent trends → whipsaw
   - When BULL extends, threshold rises automatically → rarely activates
   - When correction, threshold falls → over-filters
2. **V4_COMPOSITE wins marginally + adds ROBUSTNESS layer**
   - Logic: `ratio > 1.30 AND (state5 == 5 OR RSI > 75)`
   - Static 1.30 anchor + regime confirmation via state5/RSI
   - State5 and RSI inherently adapt (5-state model retrains, RSI universal)
   - +0.40 FULL CAGR, +0.99 Mid, +0.73 Pre-OOS
   - Slight loss OOS (-0.45) and Sharpe (-0.06)
3. **Walk-forward percentile only wins OOS** — overfits to recent
4. **Pure state5 transition signal weak alone** — needs ratio anchor

### Robustness story for production

BA-system has multi-layer defense — VNI/MA200 = 1.30 is just one layer:
- 5-state regime model (data-driven, adapts via retraining)
- TA score PE-extension warnings
- Sector limits
- Stop-loss -20%
- QWF quarterly drift detection

If 1.30 structurally obsolete:
- 5-state model still catches new regime patterns
- RSI threshold universal
- V4_COMPOSITE's regime confirmation acts as automatic fail-safe

### FINAL V11 spec (robustness-enhanced)

```python
def filter_v11(cand, state5_today, days_since_release, vni_ratio, vni_rsi):
    # P3 COMPOSITE: numeric + regime confirmation
    if vni_ratio > 1.30 and (state5_today == 5 or vni_rsi > 75):
        cand = cand[~cand["play_type"].isin(BUY_TYPES)]
    # SV_TIGHT: state-conditional Fresh-Q
    if state5_today == 1:
        return cand[days_since_release <= 30]
    if state5_today in (2, 3):
        return cand[days_since_release <= 60]
    return cand  # BULL: no filter
```

### Performance vs v10 baseline (all 4 periods)

| Period | v10 baseline | V11 (V4_COMPOSITE) | Δ |
|--------|--------------|---------------------|---|
| FULL 2014-2026 | 16.87% / 1.18 | **19.77% / 1.31** | **+2.90pp / +0.13** |
| OOS 2024-2026 | 24.26% / 1.28 | 27.00% / 1.53 | +2.74pp / +0.25 |
| Mid 2018-2023 | 20.09% / 1.19 | **25.18% / 1.33** | **+5.09pp** |
| Pre-OOS 2014-19 | 7.31% / 0.88 | **10.44% / 1.05** | **+3.13pp / +0.17** |

ALL 4 periods improve materially. Plus inherent robustness via regime co-confirmation.

### Monitoring layer (for production)

Add to `qwf_hybrid_v3.py`:
```python
overheat_days_last_4q = count_overheat_v11_triggers(trailing=4)
if overheat_days_last_4q < 3:
    alert("Overheat filter rarely triggering — check if threshold structurally obsolete")
if overheat_days_last_4q > 60:
    alert("Overheat triggering excessively — review threshold")
```

Quarterly QWF reviews will catch any structural drift.

---

## Pre-2014 stress test (2026-05-16)

**Setup**:
- Built `tav2_bq.fa_ratings_pre2014` (5,118 rows, 471 tickers, 2006Q1–2013Q4) via `build_fa_ratings_pre2014.py`.
  - Used weighted mean over AVAILABLE axes (≥4/7 axes required) since pre-2014 shareholder (DY 85% NaN, Dividend_Min3Y 99% NaN) and valuation (PE 85% NaN, PE_MA5Y ~100% NaN) data sparse.
  - FA tier validation pre-2014: A>B>C>D>E monotonic preserved (medians −0.39% / −6.12% / −9.33% / −12.52% / −14.39%).
- Adapted SIGNAL_V10 via `sim_v11_pre2014.py`:
  - UNION `fa_ratings` + `fa_ratings_pre2014`
  - Computed VNINDEX_RSI_Max3M from VNINDEX D_RSI rolling MAX(60) inline
  - Dropped `ticker_prune` universe filter (table empty pre-2014) → use full ticker + `MA200 IS NOT NULL` quality gate
  - Relaxed liq threshold 1B → 100M VND (pre-2014 market thin)

**Stress test results — 2007-01-01 → 2013-12-31, INIT 1B VND**:

| Variant | Final | CAGR | Sharpe | MaxDD | Calmar | Trades | WR | Stops |
|---------|------:|-----:|-------:|------:|-------:|-------:|---:|------:|
| BA v10 (baseline) | 1.320B | +4.05% | 0.73 | -13.68% | 0.30 | 19 | 57.9% | 3 |
| **BA v11 (SV_TIGHT + P3)** | **1.329B** | **+4.15%** | **0.76** | **-13.66%** | 0.30 | 18 | **61.1%** | 3 |
| VNI buy&hold | 0.681x | **-5.35%** | 0.19 | **-79.88%** | -0.07 | — | — | — |

**V11 vs v10 delta**: CAGR +0.11pp / Sharpe +0.03 / DD ≈ same / Calmar ≈ same

**Year-by-year V11**:
| Year | YoY | Trades | Event |
|------|----:|-------:|-------|
| 2007 | +8.9% | 10 | Bull peak |
| 2008 | +3.0% | **0** | **🛡️ 2008 GFC — sat in cash** (VNI -65%) |
| 2009 | +4.4% | 3 | Recovery |
| 2010 | -1.4% | 3 | Choppy (67% stop rate) |
| 2011 | +3.0% | **0** | **🛡️ Inflation crisis — sat in cash** |
| 2012 | +3.0% | 0 | Sideways |
| 2013 | +8.4% | 2 | Late recovery |

### Verdict: 🟢 GREEN

1. **No regime break** — V11 ≥ v10 on all metrics in pre-2014 era.
2. **System defensive capability confirmed**: BA preserves capital (+33% over 7y) while VNI loses -32% — alpha +65pp through 2008 GFC + 2011 inflation crisis.
3. **State5 + AVOID_bear** correctly blocks 100% of trades in crisis years (2008, 2011, 2012) — exactly as designed.
4. **P3 COMPOSITE** blocked 338 signals (mostly 2007 bull peak) — exactly as designed.

### Caveats / Open items

- Trade count low (18-19 trades / 7y) → statistical confidence in V11 vs v10 delta is weak (point estimate only, not significant).
- Pre-2014 PE/PE_MA5Y mostly NaN → COMPOUNDER_BUY tier effectively disabled (this tier is rare even post-2014 so impact is small).
- Pre-2014 valuation axis of fa_ratings_pre2014 falls back to industry peer median (cross-sectional) instead of self-history z-score.
- Universe smaller (471 tickers pre-2014 vs ~1,250 post-2014).
- ticker_prune filter replaced by `MA200 IS NOT NULL` → slightly looser quality gate.

### Files

- `build_fa_ratings_pre2014.py` — FA tier builder
- `fundamental_rating_pre2014_all.csv` — 5,118 ratings
- `tav2_bq.fa_ratings_pre2014` — uploaded BQ table
- `sim_v11_pre2014.py` — adapted sim driver
- `sim_v1{0,1}_pre2014_{nav,trades}.csv` — raw outputs
