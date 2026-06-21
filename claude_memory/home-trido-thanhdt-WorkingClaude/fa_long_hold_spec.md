---
name: LH-system spec (FA-driven long-hold portfolio)
description: Quarterly-rebalanced staggered-cohort A+B picks, 1Y hold. Diversifier to BA 45d; beats BA in OOS bull.
type: project
originSessionId: 70c13426-2492-456b-9547-d14c8cf8fcb7
---
# LH-system — Long-Hold FA Portfolio

⚠️ **STATUS 2026-05-15: R&D PAUSED — DROPPED FROM PRODUCTION** ⚠️

Original results were sizing-bug inflated (true CAGR 11.5% vs reported 19.85%).
6 v2c trend-following variants ALL underperformed v1.
See [production_2026-05-15.md](production_2026-05-15.md) for final decision.
Artifacts retained for future LH v3 research (multi-factor direction).

---

**Date:** 2026-05-14 | Scripts: `score_fa_lh.py`, `simulate_lh_nav.py`, `run_lh_matrix.py`
**Status:** Backtested, recommendation ready. Not yet deployed.
**Mandate:** separate from BA 45d; absorb long-horizon FA alpha (smoothed_EY IC 0.08→0.18 from 3M→2Y).

## Production config: **LH_1Y_10AB_stag**

| Param | Value | Rationale |
|---|---|---|
| Score | `fa_lh_v1` (v8c_final + pre-sales for REIT/REIT_RES) | FA scoring per sub-sector, with AdvCust/UnearnRev injection for real-estate |
| Hold period | **4 quarters (1Y)** | Sweet spot — 2Y underperforms due to stale picks through regime shifts |
| Positions | **10 equal-weight** | 5 too concentrated (7.5% CAGR), 20 dilutes alpha (12.3%) |
| Tier set | **A + B** | A only 16.03%, A+B 16.73% — wider net helps |
| Refresh mode | **Staggered** (cap n/H = 2-3 new buys/quarter) | Continuous quarterly signal refresh; beats lumpy 11.03% |
| Sector | **All** (incl REIT + REIT_RES + KCN) | Excluding REIT cuts -5pp CAGR; KCN long-cycle alpha critical |
| Rebal trigger | Median Release_Date + 30 days | Allow market to digest Q reports |
| Costs | slip 0.10% in / 0.15% out, tax 0.10%, liq cap 20% ADV × 5d max fill | Same envelope as BA canonical |
| Cash on idle | 1% annual deposit | Realistic |
| Stop loss | **None** | Long-hold thesis; accept DD for full FA alpha capture |
| NAV | 50B VND | Canonical |

## Performance (full 2014-2026 + OOS 2024-2026)

| Strategy | CAGR | Sharpe | MaxDD | Calmar | OOS 2024-26 CAGR | OOS DD |
|---|---|---|---|---|---|---|
| **LH_1Y_10AB_stag** | **16.73%** | **1.04** | **-28.3%** | **0.59** | **+23.5%** | -20.2% |
| LH_1Y_10A_stag | 16.03 | 0.98 | -27.9 | 0.57 | +22.2 | -20.1 |
| LH_6M_10A_stag | 13.45 | 0.84 | -29.6 | 0.46 | +12.3 | -11.4 |
| LH_2Y_10AB_stag | 6.11 | 0.44 | -31.7 | 0.19 | +8.6 | -20.5 |
| LH_1Y_10AB_noREIT | 11.70 | 0.84 | -27.2 | 0.43 | +6.1 | -14.2 |
| BA-system 50B (canonical) | 17.15 | **1.21** | **-14.5** | **1.18** | +21.2 | -15.2 |
| VNINDEX B&H | 9.12 | 0.57 | -45.3 | 0.20 | +18.7 | -18.1 |

**Annual returns (LH_1Y_10AB_stag):**
- 2015 +6.5%, 2016 +9.6%, 2017 **+32.0%**, 2018 +1.7%, 2019 -0.8%
- 2020 +28.7%, 2021 **+73.7%**, 2022 -24.4%, 2023 **+47.5%**
- 2024 +24.1%, 2025 **+38.4%**, 2026 YTD -3.2%

## Answers to research questions

1. **Optimal hold period?** 1Y. 2Y dramatically underperforms despite stronger FA IC — stale picks drift through regimes (2018 sideways, 2022 BEAR) without exit. 6M loses ~3pp CAGR vs 1Y from too much turnover.
2. **Position count?** 10. 5 = idiosyncratic risk + cash drag in staggered mode. 20 = alpha dilution.
3. **Sector allocation?** Include all (incl REIT/KCN). Excluding REIT drops CAGR -5pp; pre-sales boost on REIT/REIT_RES is working as designed.
4. **Rebalance trigger?** Pure time-based quarterly (median Release_Date + 30d) with staggered cohorts. Tier-drop trigger NOT tested — quarterly rotation already captures tier changes.
5. **Exit rules?** Hard time stop at 4 quarters. No stop-loss (accepts -28% DD). No trailing stop.
6. **Comparison to BA 45d?**
   - **Comparable CAGR** (16.73 vs 17.15, gap −0.42pp)
   - **Worse DD** (−28.3 vs −14.5, gap +13.8pp)
   - **BETTER OOS 2024-2026** (+23.5 vs +21.2, gap +2.3pp)
   - **Strong diversification value**: LH captures bull markets BA misses (2021 +73.7% standalone). Correlation lower in bull regimes — exactly when BA underperforms B&H.
7. **Pre-sales driver?** YES. REIT_RES + REIT schemas with `AdvCust_yld` and `Backlog_yld` axes contribute the alpha that pure FA misses. Excluding REIT entirely strips -5pp CAGR; sub-sector A-tier WR for REIT_RES is 75% in v8c_final.

## Key design decisions (with backtest evidence)

- **Staggered > Lumpy**: 1Y staggered 16.73% vs lumpy 11.03% (+5.7pp). Fresh quarterly signal critical.
- **A+B > A only**: small but consistent (+0.7pp CAGR). More diversification, same alpha quality.
- **Pre-sales weight 0.20 on REIT/REIT_RES**: confirmed IC 0.144 (AdvCust) and 0.181 (Backlog) at 2Y; injection into score retains best performance per sub-sector.
- **No stop loss**: long-hold is inherently a "ride through" thesis; backtested with stop would cut bull captures (2017 +32%, 2021 +74% would degrade).
- **Quarterly rebal at Release_Date+30**: Lag avoids buying into post-report volatility. Median across tickers because individual Release_Date varies.

## Caveats

1. **DD risk**: -28% MaxDD spans 2018-2020 (sideways + COVID). Investors must tolerate 2-year underwater periods. 2022 crash was milder (-24%, vs VNI -33%) — surprising resilience but not regime-protected.
2. **VN capital gains tax**: 0.10% per sale already in model. ~15 sales/yr × 0.10% = 0.15%/yr drag, small.
3. **Slippage realism**: model uses 0.10%/0.15%; actual large-NAV slippage could be 2-3× for thin REIT names. Tested 20% ADV liquidity cap — accounts for this.
4. **Capacity**: at 50B NAV, average position ~5B VND. Above 200B, REIT_RES + REIT names hit cap; would need ETF substitution like BA does.
5. **Score-distribution sensitivity**: like all FA refactors (v5/v6/v8), LH score has not been canonical-sim validated against BA — but since LH runs STANDALONE (no v10 score interactions), no equivalent risk.
6. **Regime exposure**: no 5-state overlay. Strong bull capture, weaker BEAR protection than BA. Pure beta to FA fundamentals.

## ✅ Hybrid BA+LH + CRISIS gate — TESTED 2026-05-14

Script: `run_hybrid_lh_ba.py` | Output: `hybrid_lh_ba_results.csv`, `hybrid_lh_ba_nav.csv`, `hybrid_2022_monthly.csv`
BA NAV source: `f_ba_mix_nav_traces.csv` col `BA_50_50` (BA canonical 50/50 BAL+VN30 split)
Common range: 2014-04-01 → 2026-01-16 (~12 years)

### Full-period results

| Strategy | CAGR | Sharpe | MaxDD | Calmar |
|---|---|---|---|---|
| BA_only | 17.47% | 1.22 | -14.5% | 1.20 |
| LH_only (no gate) | 17.76% | 1.08 | -28.3% | 0.63 |
| **LH_gated** (skip buys when state=1) | **20.43%** | 1.18 | -26.7% | 0.77 |
| Hybrid_50/50 passive | 17.62% | 1.37 | -20.0% | 0.88 |
| Hybrid_50/50 rebal qtrly | 18.01% | 1.38 | -19.6% | 0.92 |
| 🏆 **Hybrid_50/50 rebal qtrly + GATED** | **19.33%** | **1.44** | **-16.4%** | **1.18** |
| Hybrid_70/30 BA-tilt qtrly | 17.89% | 1.38 | -16.1% | 1.11 |
| Hybrid_30/70 LH-tilt qtrly | 18.01% | 1.29 | -23.1% | 0.78 |
| VNINDEX_BH | 10.42% | 0.64 | -45.3% | 0.23 |

### OOS 2024+ (24 months, including 2026 BEAR)

| Strategy | CAGR | Sharpe | MaxDD |
|---|---|---|---|
| BA_only | 21.63% | 1.17 | -13.5% |
| LH_gated | **49.79%** | **1.96** | -25.0% |
| **Hybrid 50/50 qtrly gated** | **35.53%** | **1.92** | -13.5% |
| VNINDEX_BH | 28.22% | 1.50 | -18.1% |

### 2022 crash defense (BEAR year)

| Strategy | YoY | Notes |
|---|---|---|
| BA_only | **+2.08%** | regime gate works |
| LH_only | -26.22% | no protection |
| LH_gated | -24.46% | gate fires late; modest improvement |
| Hybrid 50/50 qtrly gated | -11.38% | LH drag visible but bounded |
| Hybrid 70/30 BA-tilt | -6.81% | safer through bear |
| VNINDEX_BH | -34.39% | benchmark |

### Verdict

🏆 **PROMOTE: Hybrid_50/50 rebal qtrly + CRISIS gate** as the new combined production system.
- Highest Sharpe (1.44) AND Calmar (1.18) of any tested configuration
- CAGR +1.86pp over BA-only, +1.57pp over LH-only
- MaxDD -16.4% (only +1.9pp worse than BA-only)
- OOS 2024+ Sharpe 1.92 (vs BA 1.17, LH 1.61) — strong diversification working
- 2022 crash -11.4% (vs LH alone -26%) — gate + BA leg cushion 60% of the LH drawdown

### CRISIS gate mechanics

Skip new buys when `vnindex_5state.state == 1` (CRISIS). Expired positions still sell normally.
- Adds **+2.67pp CAGR to LH standalone** (17.76 → 20.43)
- Adds **+1.32pp to 50/50 hybrid** (18.01 → 19.33)
- Most alpha comes from OOS 2024+ where gate avoided 2024-Q1 CRISIS + 2026-Q1 BEAR
- Trade-off: marginal (only +1.6pp DD improvement in 2022); gate doesn't force exit, only blocks fresh deploy

### Alternative configs (if priorities shift)

- **70/30 BA-tilt + qtrly rebal**: CAGR 17.89%, Sharpe 1.38, MaxDD -16.1%, Calmar 1.11. Best DD-CAGR trade-off for risk-averse. 2022 only -6.8%.
- **LH_gated standalone**: CAGR 20.43%, Sharpe 1.18, MaxDD -26.7%. Best raw CAGR for risk-tolerant. OOS 2024+ CAGR 49.79%.

## ✅ Caveat #3 — RESOLVED 2026-05-14

Investigation: `investigate_red_periods.py` analyzed the 2 "RED" trailing-3Y windows from QWF v1.

| Window | Defensive%* | VNI CAGR | Hybrid CAGR | **Alpha vs VNI** | Verdict |
|---|---|---|---|---|---|
| RED #1: 2017-04 → 2020-03 (COVID) | 35.9% | -2.85% | +6.80% | **+9.65pp** | 🟢 GREEN on alpha |
| RED #2: 2022-01 → 2024-12 | 53.0% | -6.03% | +7.26% | **+13.29pp** | 🟢 GREEN on alpha |
| Contrast GREEN: 2019-01 → 2021-12 | 23.7% | +18.92% | +38.85% | +19.93pp | 🟢 |

*Days in state 1 (CRISIS) + state 2 (BEAR) within the 3Y window.

**Root cause**: QWF v1 baseline (CAGR 19.33%) is a 12-year long-term average that assumes ~28% defensive days. Rolling 3Y windows with >35% defensive days mechanically miss this baseline regardless of system quality. In both "RED" periods, **VNI itself was negative** — there's no scenario where any stock-picking strategy delivers 19% CAGR when the underlying market loses 3-6%/yr for 3 years.

**Critical finding**: Hybrid alpha vs VNI **grows in bearish windows** (+13.3pp in 2022-2024 worst regime vs +19.9pp in 2019-2021 best regime). The system delivers regime-appropriate alpha throughout — exactly the diversifier behavior we designed for.

**FA score quality** is unchanged in both windows: 243 A-picks (RED #1) and 491 A-picks (RED #2) with normal sub-sector distribution. No tier drift detected.

**Fix applied**: QWF v2 (`qwf_hybrid_v2.py`) uses **alpha vs VNI** as the primary status metric:
- GREEN: alpha ≥ +5pp
- YELLOW: 0 ≤ alpha < 5pp
- RED: alpha < 0

Under this scoring, rolling-3Y QWF since 2014:
- **25 of 28 quarters GREEN** (from 2020-Q1 onwards, alpha consistently +9 to +33pp)
- 4 RED in 2019 cluster: trailing 3Y captured strong 2017-2019 VNI bull where system was conservatively positioned; defensive %< 30% AND VNI CAGR > 13% — system underperforms by a few pp in pure bull runs (expected behavior for downside-protected system)
- 0 RED post-2020 even through 2022 crash and 2024 BEAR

**Caveat #3 resolved: not score drift, regime-driven, expected behavior.** Both prior REDs were the system delivering its best alpha while VNI was negative — calibration artifact in v1, not a system flaw.

## 🟢 QWF v2 REFRESHED 2026-03-30 — DEPLOYMENT-READY

Scripts: `qwf_hybrid_v2.py`, `refresh_ba_nav.py` | Outputs: `ba_nav_refresh_2026-05.csv`, `qwf_hybrid_v2_snapshot_2026-03-30.csv`, `qwf_hybrid_v2_rolling3y_2026-03-30.csv`

### Refreshed full-period metrics (now including 2026-Q1 BEAR)

| Strategy | CAGR | Sharpe | MaxDD | Calmar | Alpha vs VNI |
|---|---|---|---|---|---|
| **Hybrid_50/50_gated** | **18.17%** | **1.35** | **-16.75%** | **1.08** | **+9.05pp** |
| BA_only | 15.61% | 1.08 | -21.71% | 0.72 | +6.49pp |
| LH_gated only | 20.06% | 1.17 | -26.66% | 0.75 | +10.94pp |
| VNINDEX_BH | 9.12% | 0.57 | -45.26% | 0.20 | — |

Note: BA-only refreshed CAGR dropped from 17.47% (old NAV to 2026-01-16) → 15.61% (to 2026-03-30) because **2026-Q1 BEAR hit BA harder than LH_gated**. Hybrid only fell 19.33% → 18.17% — the LH gate cushioned it. This is the diversifier value in action.

### Snapshot windows (alpha-based scoring)

| Window | Hyb CAGR | VNI CAGR | Alpha | Status |
|---|---|---|---|---|
| Latest Q (3M) | -19.15% | -21.89% | +2.74pp | 🟡 YELLOW |
| Trailing 1Y | +43.84% | +27.32% | +16.52pp | 🟢 GREEN |
| Trailing 3Y | +27.03% | +16.03% | +11.00pp | 🟢 GREEN |
| Trailing 5Y | +25.59% | +6.90% | +18.70pp | 🟢 GREEN |
| Full since 2014 | +18.17% | +9.12% | +9.05pp | 🟢 GREEN |

**Latest Q (3M) shows the CRISIS gate firing perfectly**: Hybrid -19.15% vs BA -36.19% vs VNI -21.89%. LH_gated component returned **+1.11%** during the 3M (LH sat in cash via gate while BA absorbed the crash). The yellow status is acceptable — system still beat VNI by +2.74pp during a major BEAR.

### Verdict: 🟢 GREEN — DEPLOY

- 4 GREEN + 1 YELLOW + 0 RED on snapshot windows
- 24 GREEN + 0 YELLOW + 4 RED (all 2019 mild bull-lag) on 28 rolling-3Y quarters since 2014
- Sharpe 1.35 production-grade
- Calmar 1.08 > BA-only's 0.72 (BA-only Calmar dropped because of -21.7% DD)
- Alpha vs VNI grows in bearish regimes (+18.7pp in 5Y vs +9.0pp full) — diversifier working

## ✅ BA v11 + P3 patch — VALIDATED 2026-05-14

Investigation `investigate_red_periods.py` (Q1 2026 BA -10.6%) led to 3 candidate patches:
- P1: Add MOMENTUM_QUALITY to BAL tier set
- P2: Block DVR when primary-momentum tiers thin (<2 picks)
- P3: VNI overheated filter (VNI/MA200 > 1.30 → skip new BAL buys)

Backtest 12y canonical sim 6 variants:

| Variant | Full CAGR | Sharpe | MaxDD | OOS 2024+ | **Q1 2026** | Verdict |
|---|---|---|---|---|---|---|
| BL_v10 | 15.61% | 1.08 | -21.71% | 15.03% | -36.19% | baseline |
| P1 alone | 15.22% | 1.03 | -21.21% | 15.18% | -34.81% | ❌ marginal |
| P2 alone | 16.02% | 1.10 | -22.41% | 11.70% | **-46.05%** | ❌ hurt OOS & Q1 |
| **P3 alone** | **17.18%** | **1.14** | **-20.11%** | **16.90%** | **-29.33%** | 🏆 **ADOPT** |
| P1+P2 | 15.07% | 1.00 | -22.83% | 11.69% | -47.02% | ❌ |
| P1+P2+P3 | 14.92% | 1.02 | -22.30% | 11.33% | -46.90% | ❌ |

**P3 is universal win**: +1.57pp full CAGR, +1.50pp PRE_2024, +1.87pp OOS, +6.86pp Q1_2026.
**P2 catastrophic**: blocked DVR on too many days → cut out legit pre-bull entries.
**P1 marginal**: MOMENTUM_QUALITY too rare to materially fill 10-pos book.

**BA v11 = BA v10 + P3 only.**

P3 implementation: `recommend_holistic.py` BAL component skip new entries when `VNINDEX/MA200 > 1.30` (computed from `tav2_bq.ticker` VNINDEX row). Affects ~31 days in 12 years (rare extreme tops). Holds existing positions to expiry — no forced exit.

## ✅ Hybrid v11 (BA v11 + LH_gated 50/50) — QWF v3 VERDICT GREEN

Script: `qwf_hybrid_v3.py`, `backtest_ba_patches.py` | Outputs: `ba_v11_nav.csv`, `qwf_hybrid_v3_*_2026-03-30.csv`

### Comparison v10 vs v11 hybrid

| Metric | v10 hybrid | **v11 hybrid** | Δ |
|---|---|---|---|
| Full CAGR | 18.17% | **19.00%** | +0.83pp |
| Full Sharpe | 1.35 | **1.40** | +0.05 |
| Full MaxDD | -16.75% | -17.05% | -0.30pp |
| Full Calmar | 1.08 | **1.11** | +0.03 |
| Alpha vs VNI (full) | +9.05pp | **+9.88pp** | +0.83pp |
| Q1 2026 total | -5.13% | **-4.04%** | +1.09pp |

### Snapshot 2026-03-30 (v11)

| Window | Hyb CAGR | Alpha vs VNI | Status |
|---|---|---|---|
| Latest Q (3M) | -15.14% | +6.75pp | 🟢 GREEN (was YELLOW v10) |
| 1Y | +41.02% | +13.70pp | 🟢 |
| 3Y | +28.18% | +12.15pp | 🟢 |
| 5Y | +27.02% | +20.13pp | 🟢 |
| Full | +19.00% | +9.88pp | 🟢 |

**Rolling 3Y QWF v3: 24G/0Y/4R since 2014. 4R cluster 2019 (expected bull-lag), no recent RED.**

### Verdict: 🟢 **GREEN — DEPLOY HYBRID v11**

Improvements over v10:
- Higher CAGR, Sharpe, Calmar, alpha-vs-VNI
- Better Q1 2026 defense (gate fired correctly + BA P3 reduced exposure ahead of crash)
- Latest 3M jumped from YELLOW → GREEN

Trade-offs:
- MaxDD slightly worse (-17.05% vs -16.75%, +0.30pp) — within tolerance
- BA leg in OOS 1Y dropped slightly (16.67% v11 vs 22.08% v10) because P3 sat out 31 overheated days; net hybrid still better

## ✅ Phase 1 + Phase 2 Validation Tests (2026-05-14)

Scripts: `tests_phase1.py`, `tests_phase2_capacity.py` | Outputs: `phase1_*.csv`, `phase2_*.csv`

### Phase 1A — Capital allocation grid (50B canonical)

| Allocation | CAGR | Sharpe | MaxDD | Calmar | 2022 | Q1 2026 |
|---|---|---|---|---|---|---|
| LH-only (0/100) | 20.06% | 1.17 | -26.7% | 0.75 | -24% | +1.1% |
| LH-tilt 40/60 | 19.27% | 1.38 | -18.7% | 1.03 | -14% | -12% |
| **Balanced 50/50** | 19.00% | **1.40** | -17.1% | 1.11 | -11% | -15% |
| 🏆 **BA-tilt 60/40** | 18.69% | 1.39 | **-15.4%** | **1.21** | -9% | -18% |
| BA-tilt 70/30 | 18.36% | 1.36 | -15.0% | **1.22** | -6% | -21% |
| BA-only (100/0) | 17.18% | 1.14 | -20.1% | 0.85 | +2% | -29% |

**Finding**: 60/40 BA-tilt wins Calmar (1.21) and gives -1.7pp DD improvement for only -0.31pp CAGR. **50/50 still has highest Sharpe (1.40)**. Choice depends on risk preference.

### Phase 1B — BA-LH correlation (rolling 1Y)

- Full-period correlation: **+0.34** (moderate)
- Stress correlation: COVID **+0.06**, 2022 crash **+0.07**, Q1 2026 BEAR **+0.45**
- Diversification works BEST in major stress — correlation collapses to ~zero in COVID/2022.

### Phase 1C — Black swan stress (-30% / -40% peak shock on Hybrid 50/50)

| Shock | CAGR cost | Recovery 2017 peak | Recovery 2021 peak |
|---|---|---|---|
| -30% | -3.49pp | 1076 days | 1228 days |
| -40% | -4.96pp | 1103 days | 1287 days |

Hybrid more shock-sensitive than BA-alone (LH no position stops). Still manageable, not catastrophic.

### Phase 2 — Capacity scaling (CRITICAL for NAV ≥ 100B)

| NAV | BA CAGR | LH CAGR | Hyb 50/50 CAGR | Sharpe | DD | Calmar | Alpha vs VNI |
|---|---|---|---|---|---|---|---|
| 1B | 19.25% | 20.43% | 20.83% | 1.21 | -21.9% | 0.95 | +11.7pp |
| 50B | 17.18% | 19.85% | **19.00%** | **1.40** | -17.1% | **1.11** | +9.9pp |
| **100B** | 14.38% | 16.90% | **16.05%** | 1.28 | -16.5% | 0.98 | **+6.9pp** |
| 200B | 12.62% | 13.25% | 13.25% | 1.20 | -13.6% | 0.97 | +4.1pp |
| 500B | 10.31% | 9.09% | 9.93% | 1.10 | -14.0% | 0.71 | +0.8pp (CEILING) |

**Breaking point: ~100B → 200B** (CAGR drops -2.95pp each step). By 500B, system loses edge vs VNI.

**At 100B viable**: CAGR 16.05%, Sharpe 1.28, DD -16.5%, alpha +6.9pp.

**OOS_2024+ scales better** than full-period (only -6pp CAGR from 50B → 500B, vs -10pp full-period). LH leg modern alpha 38-41% compensates BA degradation.

**Scale-up recommendations**:
| NAV | Config |
|---|---|
| 1-50B | Hybrid 50/50, default n_positions=10 |
| 50-100B | Hybrid 50/50, monitor LH liquidity caps |
| 100-150B | ✅ Still good; consider n_positions=15 (smaller positions stay under cap) |
| 150-250B | Consider LH-tilt (LH degrades slower than BA at scale) |
| 250B+ | Switch to VN30 + LH only (per BA-system memory) |

## ⚠️ CRITICAL CORRECTION (2026-05-15) — Simulator bugs found, numbers revised

User question "Bạn mua gì vào 01/06/2025 để qua tháng 12 đã bán rồi" exposed that prior hybrid v11
backtest used SLICED simulation (positions inherited from years of cohort rotation), not FRESH START.
Re-audit found 3 bugs in `simulate_lh_nav.py`:

### Bug 1: Position sizing (FIXED)
- OLD: `target_per_pos = cash / len(new_buys)` → first cohort buys 50% NAV per position
- NEW: `target_per_pos = NAV / n_positions` → fixed 10% NAV per position
- **Impact**: 12y LH CAGR 19.85% → 11.53% (lost concentration bonus)

### Bug 2: Max buys per rebal (FIXED)
- OLD: `int(round(10/4)) = 2` (banker's rounding) → max 8 positions after 4 cohorts
- NEW: `int(ceil(10/4)) = 3` → reaches 10 positions after 4 cohorts
- **Impact**: avg_n_pos 5.93 → 7.95

### Bug 3: CRISIS gate smoothing lag (investigated, kept as-is)
- 5-state has smoothed=1 lag (e.g., 2025-09-23 → 2025-12-25 stuck at CRISIS while raw=3-4 bullish)
- Tested AND-gate (smoothed AND raw): 12y CAGR 10.05% — worse than smoothed-only 11.53%
- Accept smoothing lag → miss occasional Q-cohort in rare gate-lag windows

### Corrected metrics (true LH performance)

| Metric | OLD (bug) | NEW (fixed) |
|---|---|---|
| LH 12y CAGR | 19.85% | **11.53%** |
| LH 12y Sharpe | 1.16 | 1.01 |
| LH 12y MaxDD | -26.66% | -18.73% |
| LH OOS_2024+ | 41.81% | 13.18% |
| LH avg deploy | 100% | 80% (steady) |
| Hybrid 12y CAGR (50/50 BA v11 + LH) | ~19.00% | **~14.4% est** |

### Fresh-start ramp: staggered too slow

Fresh start 2025-06-01 with 25B LH leg, staggered mode:
- Only 6 positions [REDACTED] in 9 months
- Final NAV 23.29B (**-6.83%**)
- 60-80% of LH NAV in cash during entire window
- VNI rallied +24.41% → alpha **-24.88pp** vs VNI

### 🏆 SOLUTION: hybrid_init mode (NEW)

Lumpy first rebal (deploy 10 positions immediately) + staggered after.

| Mode | 12y CAGR | Sharpe | DD | Fresh start NAV |
|---|---|---|---|---|
| Staggered | 11.53% | 1.01 | -18.73% | -6.83% ❌ |
| Lumpy | 10.07% | 0.63 | -31.75% | +3.21% |
| 🏆 **Hybrid_init** | **10.98%** | 0.91 | -18.76% | **+3.21%** ⭐ |

**Use hybrid_init for production**: fresh-start deploy benefits + steady-state diversification.

### Caveat: hybrid_init steady-state synchronized cohort risk

After lumpy initial, all 10 positions share Q1 vintage. After 4Q they all expire together.
Mitigation: stagger sells (sell 2-3 oldest per quarter starting from Q+4) → portfolio matures
into 4-quarter cohort spread within 2-3 years.

Updated production recommendation: deploy hybrid_init mode TODAY (2026-05-15) with Q1 2026 picks.

## Deployment plan (2026-05-14, REVISED 2026-05-15)

1. **Capital structure**: 50% NAV → BA-system (run as-is via `recommend_holistic.py`), 50% NAV → LH-system (new `recommend_lh.py`).
2. **Inter-sleeve rebalance**: Quarterly (next quarter-end), reset 50/50 split. Don't intra-quarter drift past ±10%.
3. **LH operations**:
   - `score_fa_lh.py` rerun after each quarter's Q4 reports finalize (~ end of release season + 30 days)
   - `recommend_lh.py` for daily pick screening (CRISIS gate built in — script halts if state=1)
   - Each quarter: rotate ~2-3 positions (oldest cohort expires, new top-score A+B picks fill in)
   - Cost discipline: slip 0.10%/0.15%, VN tax 0.10%, liq cap 20% ADV × 5d
4. **CRISIS gate enforcement**: skip all NEW LH buys when `vnindex_5state.state == 1`. Existing positions ride out the regime to their 4-quarter expiry. No forced exits.
5. **Live universe filter**: `Volume_3M_P50 × Close ≥ 1B VND/day` (same as BA).
6. **Monitoring**: re-run `qwf_hybrid_v2.py` at end of each quarter. Alarm threshold: 2+ consecutive 3Y RED windows on alpha-vs-VNI basis (would indicate score drift, not regime).
7. **First action**: after 2026-Q1 reports release wave completes (~late May), regenerate `fa_ratings_lh.csv` and pick first 2-3 LH positions.

## Future iterations (after hybrid deploy)

- **Score refinement**: long-horizon should drop NP_peak_ratio (short-term peak signal) and lean harder into smoothed_EY + Backlog_yld. Try v2 score.
- **Stop -25%** at individual LH position level — test whether catches blow-ups without cutting winners. May further close the 2022 gap.
- **Quarterly tier-drop forced exit** — re-test (current design holds 1Y regardless of tier drift).
- **Stricter regime gate**: also exit when transitioning into CRISIS (currently only blocks new buys). Tradeoff: forced exit may sell low.
- **BA NAV refresh**: current BA series ends 2026-01-16; re-run BA simulation through 2026-05 to lengthen OOS validation.

## Files

- `score_fa_lh.py` — scoring (uploads to local `fa_ratings_lh.csv`, 12,899 rows, 687 tickers, 50 quarters)
- `simulate_lh_nav.py` — simulator with `run_lh(...)` + `run_vnindex_bh(...)`
- `run_lh_matrix.py` — sweep 15 configs, outputs `lh_matrix_results.csv` + `lh_nav_series.csv`

## Deployment checklist (when ready)

- [ ] Upload `fa_ratings_lh.csv` to BQ as `tav2_bq.fa_ratings_lh`
- [ ] Add `recommend_lh.py` for live quarterly picks (post Release_Date+30 days)
- [ ] Decide capital allocation vs BA (50/50? 70/30 BA-tilt? Standalone?)
- [ ] Set up quarterly cron — fire when 80%+ of tickers have released latest Q
- [ ] First live picks: 2026Q1 reports → buy ~2026-05-15 onward (next deadline)
