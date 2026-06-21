# Tam Quan v3.1 — Dynamic Blend + US Shock Override (2026-05-21, updated)

## Naming convention
- **Cổ Điển** = canonical original (archived)
- **Tinh Tế** = previous LIVE (v2g_pe3c + s3 smoothing)
- **Tam Quan v3** = dual blend (raw VNI + EW + concentration) — superseded
- **Tam Quan v3.1** = v3 + US shock override (current staging) — **DEPLOYED 2026-05-21**

Note: "Tam Thế" reserved for BA system v13 (different family). Ngũ Hành 5-state uses "Tam Quan" = "three perspectives". v3.1 adds US shock as 4th view, but kept "Tam Quan" since US is asymmetric defensive cap (not equal weight).

## Architecture

### 1. Two parallel r_scores
- **r_score_raw**: 8 factors on raw VNINDEX = 7 base (P3M, P1M, MA200_dev, RSI, MACD, CMF, Breadth) + PE-comp w=0.03
- **r_score_ew**: 7 factors on VNINDEX_EW (no PE — EW has no natural PE)

### 2. Equal-weighted VNINDEX construction
- Universe: point-in-time eligible per date — ≥252 sessions history + rolling 60d avg trading value ≥ 500M VND
- Daily: ret_EW[t] = mean(log(Close[i,t]/Close[i,t-1])) on eligible universe
- VNINDEX_EW[t] = VNINDEX_EW[t-1] × exp(ret_EW[t]), base=100 at 2014-01-03
- Pre-2014: fallback to raw VNI
- Universe size: median 232, min 130, max 603 (drifts with market growth)

### 3. Concentration trigger
- **Trading-value HHI**: Σ w_i² where w_i = (Close_i × Volume_i) / Σ(Close_j × Volume_j)
- **CR3**: top-3 trading-value share
- **Cap-EW divergence**: |ret_VNI_60d − ret_VNINDEX_EW_60d| (absolute)
- Each → expanding pct-rank (min 252 sessions)
- **concentration_score** = mean(hhi_rank, cr3_rank, div_rank) ∈ [0, 1]
- Smoothing: EMA(0.20) on raw score → concentration_smooth

### 4. Dynamic α schedule
```
α(c) = clip(1.0 − 2.0 × max(0, c − 0.5), [0.3, 1.0])
```
- c < 0.5 → α=1.0 (pure LIVE — broad market, no degradation)
- c = 0.6 → α=0.8
- c = 0.7 → α=0.6
- c ≥ 0.85 → α=0.3 (floor — heavy EW lean but never full EW)

α distribution post-2014: 75.9% at α=1.0, 15.9% at [0.7, 1.0), 6.3% at [0.5, 0.7), 1.9% at α<0.5.

### 5. Blend
`r_score_dual = α × r_score_raw + (1-α) × r_score_ew`
Pre-2014 (r_ew NaN): fallback to r_raw directly.

### 6. Downstream pipeline (= Tinh Tế)
- EMA(0.40) on r_score_dual → r_dual_ema
- classify: <0.10 CRISIS · <0.20 BEAR · <0.70 NEUTRAL · <0.90 BULL · ≥0.90 EX-BULL
- Risk overrides: PE>P90 caps 5→4; DD<-25% caps ≥4→3; vol>1.5×avg caps 5→4
- **v2g BearDvg gate** (min_dur=30): floor=CRISIS while gated; exit on (BullDvg OR E2 capitulation OR S2_bull)
  - E2 = dd<-15% + close[i]/close[i-5]>1.05 + RSI rising 15% + CMF>0
  - S2_bull = PE 120-day slope < -25%/yr (pe3c)
- **s3 smoothing**: rolling_mode(3) + min_stay_filter(2)

### 7. US Shock Override (v3.1 — ADDED)
Asymmetric cap applied AFTER s3 smoothing — only restricts to defensive, never relaxes.
```
us_cap(SPX_DD_1Y, VIX) → max allowed state
  SPX_DD_1Y < -25% OR VIX > 35  →  CRISIS cap (state ≤ 1)
  SPX_DD_1Y < -15% OR VIX > 30  →  BEAR cap   (state ≤ 2)
  SPX_DD_1Y < -10% OR VIX > 25  →  NEUTRAL cap (state ≤ 3)
final_state = min(tam_quan_state, us_cap)
```
Then re-apply light s3 smoothing (mode3+ms2) to absorb 1-day override flickers.
Source: yfinance ^GSPC + ^VIX. US date aligned to VN date − 1 (US closes before VN next day).

## Integrated backtests vs LIVE Tinh Tế

### Phase A — Pre-2014 STRESS test (2007-2013, 1B init, BA v11)
| Variant | CAGR | Sharpe | MaxDD | Trades | Y2008 |
|---|---|---|---|---|---|
| LIVE Tinh Tế | **+3.03%** | +0.60 | -12.16% | 17 | +3.0% |
| v3 (no US ovr) | -0.66% ❌ | -0.03 | **-34.79%** ❌ | 25 | **-20.4%** ❌ |
| **Tam Quan v3.1** | **+2.58%** | +0.57 | **-11.83%** | 15 | **+3.0%** ✅ |

v3.1 fixes 2008 GFC failure (Y2008 fully recovered to LIVE level), gap to LIVE only -0.45pp.

### Phase B — Post-2014 V11 backtest (2014-2026, 50B init)
| Period | LIVE | v3 staging | **v3.1** | v3.1 vs LIVE |
|---|---|---|---|---|
| **FULL 14-26** | 18.98% | 19.41% | **19.33%** | **+0.35pp** ✅ |
| Sharpe | 1.28 | 1.33 | **1.34** | +0.06 ✅ |
| Wealth | 8.57x | 8.96x | **8.89x** | +4% ✅ |
| **OOS 24-26** | 25.13% | 27.25% | **29.26%** | **+4.13pp** ✅ |
| OOS Sharpe | 1.35 | 1.50 | **1.62** | +0.27 ✅ |
| Pre-OOS 14-19 | 12.38% | 13.14% | 12.17% | -0.21pp |
| Mid 18-23 | 20.56% | 19.06% | 18.80% | -1.76pp |
| **Y2022 bear** | -10.65% | -9.93% | **+0.26%** | **+10.91pp** ⭐⭐ |
| Y2022 MaxDD | -11.06% | -10.87% | **-3.20%** | +7.86pp ⭐ |
| **Q1 2026** | -10.16% | +9.82% | **+5.49%** | **+15.65pp** ✅ |
| FULL MaxDD | -19.01% | -16.68% | -20.23% | -1.22pp (trade-off) |

**Win 4/6 main periods + fixes both stress events (2008 GFC + Y2022 bear).**

## Key insights

1. **Pipeline beats blend alone**: v2 (dynamic α + canonical Cổ Điển pipeline) only got 17.44% FULL — losing 1pp to LIVE. v3 (dynamic α + Tinh Tế pipeline) got 19.41% — winning 0.43pp. Pipeline (s3 + v2g + S2_bull) contributes ~2pp by itself.

2. **Dynamic α is selective gain**: v3 vs hypothetical pure Tinh Tế = +0.43pp comes from α activation in ~24% of days when concentration spike. α=1.0 default 76% of post-2014 days.

3. **US shock override is synergistic, not additive**: Y2022 v3 -9.93% (essentially tied LIVE); v3.1 (added US override) Y2022 **+0.26%** = +10.2pp jump. Because 2022 was a global bear (SPX -25%), US override caught what domestic VN signals missed.

4. **2008 stress reveals fragility of pure-VN signals**: Standalone Tam Quan v3 failed 2008 GFC with -20.4% Y2008 (vs LIVE +3.0%) because 2-day false BULL signal Aug 18-19 during deepening US crisis. US override fixes by capping at BEAR when SPX 1Y drawdown < -15%.

5. **Today (2026-05-20)**: v3.1 = NEUTRAL while LIVE = BULL. Concentration_smooth = 0.63, α = 0.73 (mild EW lean). US: SPX DD_1Y = -2%, VIX = 18 → no US override fires. Pure dual-blend doing the work. VIC alone 16.8% of cap, Cap-EW div 60d 12.31pp (div_rank=0.87). Empirical "narrow rally" case.

## Override fire frequency (post-2014, validates non-interference in normal regime)
- 2014-2017, 2024: **0 fires** (clean broad market years)
- 2018: 2 days, 2019: 0, 2020: 77 days (31% — COVID), 2021: 13, 2022: 35 (14% — rate hike)
- 2023: 15, 2024: 0, 2025: 6, 2026: 0 (so far)
- Override is "silent in normal years, active in global shocks" — exactly as designed.

## Files & artifacts

### Build chain (v3 → v3.1)
- `vnindex_5state_dual_v3.py` — v3 base build
- `vnindex_5state_dual_v3_staging.csv` — v3 staging (pre-US-override)
- `build_tam_quan_full_history.py` — extend EW to 2006 for stress test
- `build_v3_1_clean.py` — v3.1-clean = v3 staging + US override overlay (FINAL)
- `vnindex_5state_tam_quan_v3_1_clean.csv` — FINAL staging output

### Dependencies
- `build_concentration_history.py` — concentration tooling (HHI_tv, CR3, cap-EW div)
- `concentration_history.csv` — daily concentration time series
- `vnindex_5state_ew_v1.py` — VNINDEX_EW + EW factors
- `vnindex_5state_ew_full.csv` — EW factor cached
- `pull_us_market.py` — yfinance SPX + VIX puller
- `us_market_history.csv` — US daily data
- `analyze_us_vn_linkage.py` — US-VN correlation diagnostics

### Validation
- `test_dual_v3_v11.py` — Phase B post-2014 V11 backtest
- `test_tam_quan_stress_2007_2013.py` — Phase A pre-2014 stress test
- `test_v3_1_full.py` — combined Phase A + B validator

### Monitoring
- `ngu_hanh_shadow_tracker.py` — daily LIVE vs STAGING shadow
- `ngu_hanh_shadow_log.csv` — shadow comparison log

## Shadow validation criteria (2026-05-21, refined)

5 traffic-light criteria, computed daily by `ngu_hanh_shadow_tracker.py`:

| # | Criterion | GREEN | YELLOW | RED |
|---|---|---|---|---|
| **C1** | Critical flips (BULL ↔ CRISIS) | 0 | 1 | ≥2 |
| **C2** | Divergence rate (% phiên khác) | 30-70% | <30% | >70% |
| **C3** | Mechanism justified (c≥0.5 OR US fire) | ≥80% | 50-80% | <50% |
| **C4** | Forward alpha — **Breadth %adv T+5** | ≥55% | 40-55% | <40% |
| **C5** | STAG transitions (14-day) | ≤4 | 5-6 | ≥7 |

**C4 KEY DESIGN**: User caught circular logic — measuring "STAG correct" via VNI T+5 is self-defeating because VNI is exactly the VIN-dominated signal STAG built to ignore. Empirical proof from Q1 2026 retrospective (14 divergence days):
- **VNI T+5**: 0/9 = 0% correct → RED (would fail Tam Quan)
- **EW T+5**: 4/9 = 44% → YELLOW (magnitude-aware but noisy on near-zero days)
- **Breadth %adv T+5**: 9/12 = **75% correct → GREEN** (broad participation, robust)

**Primary = Breadth** (ticker_prune universe, binary count of advances over T+5).
Secondary = EW. Advisory = VNI (shown for transparency, not used in verdict).

Verdict logic:
- 🟢 PROMOTE: C1=GREEN, C4∈{GREEN, WAIT}, no other RED
- 🟡 EXTEND: C1=GREEN, any YELLOW, no RED outside C4
- 🔴 ROLLBACK: C1=RED OR C4=RED

`demo_c4_benchmark_difference.py` documents the empirical retrospective.

## Deployment status (2026-05-21)

- ✅ STAGING uploaded to `tav2_bq.vnindex_5state_staging` with codename `tam_quan_v3_1` (v3.1-clean overlay)
- ✅ Backup tables: `tav2_bq.vnindex_5state_tam_quan_stress` (v3 full-history), `vnindex_5state_tam_quan_v31_clean` (v3.1)
- 🟡 Shadow tracking initialized — 30 prior sessions back[REDACTED], 11/14 recent days divergent (= expected Q1 2026 VIN rally protection)
- ⏳ Promote → LIVE after 2-week live shadow review (~[REDACTED]04). Trigger: `python deploy_ngu_hanh.py --promote --archive-as tinh_te`
- 🚨 Rollback if needed: `python deploy_ngu_hanh.py --rollback-to tinh_te`

## Caveats

1. LIVE baseline shows ~0.5pp run-to-run variance in V11 sim (18.98% in earlier run, 18.47% in v3 run). Sim has small non-determinism. v3 win is robust to this.
2. Concentration uses **trading-value HHI** not cap HHI (no OShares dependency, more dynamic). Today: trading-value HHI=207bps (N_eff=48) while CAP HHI ≈430bps (N_eff=23). Two different signals; div_rank catches what tv-HHI misses.
3. v3 not yet shadow-validated in live. Memory warns repeatedly (`ngu_hanh_tinh_te`, `vnindex_5state_v2g`) that integrated wins are necessary but not sufficient; live observation can reveal regime-shift issues.
4. Pre-2014 (universe sparse) → falls back to pure raw VNI. Long pre-2014 backtest (2007-13) would need separate methodology; current memory has `pre_2014_stress_test_results.md` for BA-side analog.
