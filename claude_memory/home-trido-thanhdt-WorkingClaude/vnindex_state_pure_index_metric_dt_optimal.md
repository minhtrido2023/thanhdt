---
name: vnindex-state-pure-index-metric-dt-optimal
description: "On the PURE-VNINDEX money sim (state→allocation, the Kelly-style metric), DT_10_25_25 Pareto-dominates Tinh Te + v3.4b. Synthesis attempts all fail — DT already IS the synthesis. Frontier: DD vs transitions trade-off cannot be beaten."
metadata: 
  node_type: memory
  type: project
  originSessionId: 35a9082c-d5db-4cc6-9b0e-b6a9ddbd29e1
---

# DT_10_25_25 optimal on pure-VNINDEX money metric (2026-05-28)

User reframed the eval metric: measure market-state models by **money invested directly into VN-INDEX** (state→allocation weight, `simulate_state_timing.py`), balancing absolute return against **transition frequency** (a real Kelly-weighted stock portfolio needs time to rotate, so excessive state flips are costly). This differs from all prior work which measured via INTEGRATED stock-portfolio backtests (V11/V5).

## Head-to-head on pure-VNINDEX sim (1B VND, T+1, TC0.1%, dep6%/bor10%), MODERN 2014-2026

| Model | NAV | CAGR | Sharpe | MaxDD | Calmar | **Transitions** |
|-------|-----|------|--------|-------|--------|-----------------|
| Buy&Hold | 3.74B | 11.2% | 0.35 | -45.3% | 0.25 | — |
| Tinh Te | 5.31B | 14.4% | 0.70 | **-15.9%** (2016) | 0.91 | 162 |
| v3.4b | 4.18B | 12.2% | 0.54 | -18.4% | 0.67 | 155 |
| **DT_10_25_25** | **5.72B** | **15.1%** | 0.71 | -18.4% (2021) | 0.82 | **53** |

**DT Pareto-dominates on the user's stated objective: most money AND fewest transitions (1/3 of the others).**

## Key structural findings

1. **DT_10_25_25 = v3.4b `state` base + asymmetric causal commitment filter** (`build_dt_variants_csv.py`: `min_stay_causal_asym`, default_min=10, CRISIS & EXBULL need 25 days to commit). So DT ALREADY combines v3.4b's bull-staying base + transition discipline. The "synthesis" the user wanted is DT itself.

2. **v3.4b's huge integrated-V11 edge (21.1% CAGR) does NOT show up on pure-VNINDEX** — it's the WORST of the 3 here (4.18B). v3.4b's alpha is stock-SELECTION timing (don't derisk the stock book on false US fear in bull), not index-ALLOCATION. Lesson: **the eval metric determines the winner** — never quote a state model's superiority without naming the metric.

3. **Synthesis attempts ALL fail to beat DT** (`_synth_experiment.py`, `_synth_floor.py`):
   - Asym filter on Tinh Te composite → DD blows -15.9% → -24.5% (the 25-day delay defeats Tinh Te's fast defensive entry, which is the source of its low DD).
   - v3.4b bull-aware lock added to DT → no effect (DT already slow-to-derisk).
   - Tinh Te fast-CRISIS protective floor on DT → DD stays -18.1%, transitions balloon 65-125. DT's -18.4% DD is NOT caused by slow crisis detection.
   - Faster up-confirm (default 5-7 instead of 10) → recovers 2020 V-shape (+20-23% vs +17.8%) but craters NAV to 4.5-4.7B everywhere else. DT(10,25,25) is the optimum.

4. **DD vs transitions is a genuine efficient frontier.** Tinh Te's lower DD (-15.9%) is BOUGHT with twitchiness (162 transitions = jump out fast). DT's calm (53 transitions) costs +2.5pp DD. The two max-DDs are in different years (2016 vs 2021) so protection can't transfer. You cannot have both minimal-DD and minimal-transitions.

5. **DT's only real weakness = 2020 V-recovery lag** (+17.8% vs Tinh Te +31.9%) — the documented "CRISIS-confirm-too-slow" issue. DT wins 8/13 years incl. defensive (2015, 2022 +6.1pp) and bull (2021 +13.4pp, 2025 +4.5pp).

## Recommendation
**Adopt DT_10_25_25 as the market-state foundation for Kelly-weighted whole-market investing.** Caveats: (a) NOT pre-2014 safe (memory [[v5-kelly-dt-smoothing]]: -9.3pp 2008 GFC, misses fast V-recovery); modern 2014+ only. (b) 2020-type sharp V-recovery is a live risk.

## Operational gap discovered
**BQ `vnindex_5state` (LIVE) is byte-identical to `vnindex_5state_tam_quan_v34b_clean`** — i.e. LIVE currently serves v3.4b, NOT Tinh Te (memory said Tinh Te is LIVE). Real Tinh Te only exists as local `vnindex_5state.csv` (CRISIS 19.9% — matches its memory). DT exists only as local CSV `vnindex_5state_dt_10_25_25.csv`, not in BQ. To adopt DT, must deploy to BQ + verify which series LIVE should serve.

## Refinement attempts — DT canonical confirmed optimal across 3 families (2026-05-28)

User pushed three refinement ideas; all three empirically confirm DT_10_25_25 sits at the optimum on the pure-VNINDEX money metric. This is robust validation, not failure — DT's edge IS patient slow confirmation, which can't be improved by adding speed (in VN market most fast signals are noise, not regime change).

1. **Combine Tinh Te composite + bull-lock + crisis-floor** → all worse (asym-on-TinhTe blows DD to -24.5%; bull-lock no-op; crisis-floor no DD gain, +churn). See [[vnindex-state-pure-index-metric-dt-optimal]] body above.

2. **4-gate directional (decouple enter/exit of CRISIS & EXBULL)** — `_dt_directional.py`, `asym_dir(default, enterC, exitC, enterX, exitX)`. The 4-gate STRUCTURE is correct/cleaner than DT's pending-state-only keying, but grid (~56 configs) shows canonical thresholds (enter=25/25, exit=10/10) already at the top of the 4.88-5.74B modern NAV range. Findings:
   - **exit-EXBULL is empirically irrelevant** (3→10 changes nothing, any period incl. 2008) — EXBULL only 6% of days, 130% leverage cost tiny in fixed-alloc sim.
   - **exit-crisis=7** is the single defensible micro-tune IF modern-only: +0.9pp 2020 recovery, +0.32pp full CAGR, but WORSENS 2008 crash DD (-26.9% vs -23.3%) → only safe because DT is 2014+ only.
   - **enter-crisis tension**: fast(15) gives best 2008 crash protection (DD0708 -18.5%) but bleeds modern bull (NAV 5.03B, false alarms); slow(25) modern-optimal.
   - DD -18.4% modern is IMMOVABLE by any gate param (early-2021 within-bull dip = participation cost, not exit-timing).

3. **Regime-adaptive** — `_dt_adaptive.py`. Shrink thresholds (×0.3-0.5, floor 3-5) when turbulent (trailing 20d vol > expanding p60/70/80). DOES capture 2020 V-recovery much better (+27.4% vs +17.8%) and improves 2008 crash DD (-19.9% vs -23.3%), BUT every variant LOSES modern money (best 4.83B vs canonical 5.72B, -1.6pp CAGR) + more churn. Reason: vol spikes happen inside normal bull corrections (11-28% of days) → premature commits → whipsaw swamps the tail-capture gain. **Trades return for tail protection — a risk-preference choice, not an optimization.** If user prioritizes crash survival over money: p70 shrink0.5 floor5 (DD0708 -19.9%, better 2020) at known -1.6pp modern CAGR cost.

**Net**: keep canonical DT_10_25_25. The 4-gate structure is worth adopting as the cleaner parameterization even though optimal params ≈ canonical. exit-EXBULL value (if any) would only show under true Kelly weighting / integrated stock portfolio (untested — EXBULL leverage cost under-represented in fixed-alloc VNINDEX sim).

## DT 4-gate FINAL — production params 10/25/10/25/10 (2026-05-28)

Final production = 4-gate structure with all-canonical params `default=10, enter_crisis=25, exit_crisis=10, enter_exbull=25, exit_exbull=10`. **Behaviorally IDENTICAL to DT_10_25_25 (0% state diffs)** — the 4-gate is just the cleaner/explicit parameterization. exit_crisis=7 was tried (user initially chose it for modern-only V-recovery capture) but REJECTED after the integrated Kelly test (worse DD/Calmar, see section above).

- **Production builder**: `build_dt_4gate.py` (clean, causal `asym_dir_commit`, docstring explains the exit_crisis=7→10 rejection). Base = `vnindex_5state_tam_quan_v3_4b_full_history.csv`.
- **Output CSV**: `vnindex_5state_dt_4gate.csv` (6286 rows, → 2026-05-26). 93 transitions, CRISIS 18.0%, latest state = NEUTRAL(3).
- **BQ table**: `tav2_bq.vnindex_5state_dt_4gate` (loaded 2026-05-28, exit=10 version).
- Integrated V5 Kelly: +1.96pp Full vs TQ34b, Calmar 0.90, DD -24.5% (best Kelly config).
- **NOT promoted to LIVE** `vnindex_5state` (still = v3.4b). User chose to validate integrated first (done). Promotion still pending user decision (affects downstream `recommend_holistic`).

## Integrated Kelly (V5) test — exit_crisis=7 FAILS, keep exit_crisis=10 (2026-05-28)

User asked to test DT_4gate integrated with real systems, especially Kelly. `test_v5_dt4gate_integrated.py` (V5 = 50/50 BAL+VN30, ETF_KELLY {3:1.0}, 50B NAV, T+1 open, 2014-2026). DT_4gate differs from DT_canonical by EXACTLY ONE thing: exit_crisis 10→7.

| V5 combo | Final | CAGR | IS | OOS | MaxDD | Sharpe | Calmar |
|----------|-------|------|-----|-----|-------|--------|--------|
| V5_TQ_KELLY (old canonical) | 488B | 20.25% | 13.12% | 27.30% | -27.4% | 1.32 | 0.74 |
| **V5_DT_canonical_KELLY** | 592B | 22.15% | 15.15% | 29.12% | **-24.5%** | 1.33 | **0.90** |
| V5_DT_4gate_KELLY (exitC=7) | 596B | 22.22% | 15.09% | 29.33% | -27.0% | 1.33 | 0.82 |

- **DT vs TQ34b: +1.96pp Full** (matches memory +1.90pp — implementation validated ✓). DT is a big win for Kelly.
- **DT_4gate vs DT_canonical: +0.07pp Full (noise) BUT DD -27.0% vs -24.5% (worse 2.5pp), Calmar 0.82 vs 0.90 (worse).**

**KEY LESSON**: exit_crisis=7 looked marginally better on the pure-VNINDEX fixed-alloc sim (caught 2020 +0.9pp), but under real Kelly leverage it HURTS risk-adjusted return — faster CRISIS exit = earlier risk re-entry = whipsaw = deeper DD. The pure-index metric under-weights drawdown; Kelly (100% NEUTRAL parking + 130% EXBULL) amplifies the cost of premature re-entry.

**FINAL: for Kelly/integrated, use exit_crisis=10 (= DT_canonical = DT_4gate with all-canonical params 10/25/10/25/10).** The 4-gate STRUCTURE is fine/cleaner, but exit_crisis=7 is rejected. V5_DT_canonical_KELLY (Calmar 0.90, DD -24.5%, +1.96pp vs TQ) is the recommended Kelly config. BASE ref: V1_DT4_BASE +0.55pp vs V1_TQ_BASE (DD -17.2 vs -19.2, Calmar 1.23 vs 1.08) — DT helps BASE modestly too. NAV series: `data/v5_dt4gate_integrated_nav.csv`.

## DT 4-gate × paper-trade architectures (ex-ensemble) — combines well (2026-05-28)

`test_v12_ensemble_dt.py` (DT_10_25_25 ≡ DT_4gate, 0% diff). ETF_BASE {3:0.7}. DT vs TQ34b per architecture:

| Arch | Full CAGR TQ→DT | ΔFull | ΔIS | ΔOOS20-26 | ΔOOS24-26 | DD |
|------|------------------|-------|-----|-----------|-----------|-----|
| **V11** (BAL+VN30) | 19.61→20.91% | **+1.30** | +2.30 | +0.33 | +0.50 | **-16.7 vs -18.5 ✓** |
| **V12** (BAL+LAGGED) | 20.98→22.05% | +1.06 | +1.38 | +0.76 | +0.54 | -14.3≈-14.4 |
| **V12.1** (LAG+S2) | 21.83→22.81% | +0.99 | +1.34 | +0.65 | +0.52 | -14.7≈-14.8 |
| ENS→V12 | 23.29→23.82% | +0.53 | +1.16 | **-0.06** | **-0.59** | worse |
| ENS→V12.1 | 23.94→24.41% | +0.46 | +1.12 | **-0.15** | **-0.61** | worse |

**Conclusion: YES, DT 4-gate combines effectively with all 3 non-ensemble paper-trade systems (V11/V12/V12.1) — POSITIVE in every period (Full/IS/OOS), +1.0 to +1.3pp Full CAGR.** V11 wins most (+1.30pp + real DD improvement -16.7 vs -18.5, simplest arch → DT's fewer transitions help most). V12/V12.1 gain return but DD already low (LAGGED state-independent) so DT only adds return. Benefit DECREASES with architecture complexity (V11 1.30 > V12 1.06 > V12.1 0.99). DT slightly lowers Sharpe on V12/V12.1 (1.61 vs 1.63, concentrated exposure) but CAGR dominates; V11 is clean all-round win. **Ensemble = correctly excluded: DT HURTS recent OOS (24-26: -0.59 to -0.61pp), ensemble pre-empts state timing → DT redundant + slow CRISIS confirm hurts in 2024-26.** Best static+DT: V12.1+DT (22.81%/Sh1.62/DD-14.7%). V12+LIVE paper-trade (LIVE=v3.4b) → swap to DT gains ~+1pp like V12+TQ34b. NAV: `data/v12_ensemble_dt_nav.csv`.

## Paper-trade shadow A/B set up (2026-05-28)

Goal: live-validate DT 4-gate on non-ensemble paper systems, decide end June 2026. Discovery: `pt_v11_tq34b.py` was ALREADY upgraded to DT_10_25_25+KELLY (2026-05-27) — so V11 paper-trade is already on DT. The only non-ensemble system still on raw TQ34b was **V12** (`pt_v12_tq34b.py`, BAL+LAGGED, BASE ETF). So the live A/B = V12+DT4 vs V12+TQ34b.

- **Created `pt_v12_dt4.py`** (clone of pt_v12_tq34b.py). State = DT 4-gate computed ON-THE-FLY via `_dt_4gate` (default=10/enC=25/exC=10/enX=25/exX=10) from the live `vnindex_5state_tam_quan_v34b_clean` table (2014+ warmup → slice to window). On-the-fly avoids stale-BQ-table problem; ≡ DT_10_25_25. Outputs `data/pt_v12_dt4_*`. Verified runs + reconciles ($0.00 diff).
- **Wired into `papertrade_daily.bat`** as step [3/6] (scheduled task picks it up automatically — no scheduler change).
- **`papertrade_compare.py`**: added V12_DT4 arm + dedicated "V12_DT4 vs V12_TQ34b — DT 4-gate A/B (DECISION: end June 2026)" section with gate (🟢 SWITCH if ΔRet>-0.5pp & ΔDD>-1pp / 🟡 HOLD / 🔴 KEEP TQ). Output `data/papertrade_compare5.md`.
- **Initial reading (Apr1→May19, ~32 sessions)**: V12_DT4 +3.36% vs V12_TQ34b +2.03% = **+1.34pp** (matches backtest +1.06pp), DD -0.95 vs -0.87 (≈), Sharpe 3.03 vs 3.44. Verdict 🟢 but short-window caveat.
- Decision date: end June 2026 (~3mo live data). Read `data/papertrade_compare5.md`.

## LAGGED cache refresh FIXED (2026-05-28)

Root cause of the stale paper-trade window: the 4 LAGGED-leg caches use a "load-if-exists, never refresh" pattern in their original builders (analyze_earnings_reaction.py, backtest_lagged_pos.py, research_earnings_surprise.py) — once the .pkl exists they are never re-pulled. So `pt_dates.detect_end_date()` (capped at lagged_pos_ov.pkl max) froze END_DATE at the build date (2026-05-19).

**Fix: created `refresh_lagged_caches.py`** (uses simulate_holistic_nav.bq for consistent auth):
1. `earnings_px.pkl` — incremental append (Close, time > max).
2. `lagged_pos_ov.pkl` — incremental append (Open+Volume_3M_P50, time > max, existing tickers). THIS is the END_DATE driver.
3. `earnings_surprise_data.pkl` — full re-pull (cheap, ~57k rows).
4. `earnings_events_classified.csv` — re-pull raw events + recompute pre/rel/post returns + pattern from fresh px pivot (inlined classify logic from analyze_earnings_reaction.py).

Wired into `papertrade_daily.bat` as **step [0/6]** (runs before all sims). After first run: px & ov both extended 05-19 → 05-27, detect_end_date now returns 05-27. NOTE: events_classified Release_Date max lags ~6wk (needs +30 forward trading days for post_ret window — correct/expected, not a bug). BQ ticker data itself is T-1 fresh (max = yesterday).

## End-June decision reminder (LOCAL scheduled task, 2026-05-28)

Note: `/schedule` skill creates REMOTE cloud agents that CANNOT access local paper-trade data → wrong tool. Used a LOCAL Windows Task Scheduler task instead. (Confirmed `PaperTrade3Sys` task IS live and runs `papertrade_daily.bat` daily — so it now executes the new refresh step [0/6] + pt_v12_dt4 step [3/6]; data will be current by the reminder date.)
- **Task `DT4DecisionReview`**: one-time, **[REDACTED] 09:00 local** (Mon). Runs `dt4_decision_review.bat` → `dt4_decision_review.py`: refreshes papertrade_compare.py, extracts the V12_DT4-vs-TQ34b A/B block + headline table, writes `data/DT4_DECISION_REVIEW.md` (with decision instructions), best-effort MessageBox popup.
- Hardened via PowerShell: DisallowStartIfOnBatteries=False, StopIfGoingOnBatteries=False, StartWhenAvailable=True (fires even on battery / catches up if machine was off).
- Latest A/B reading (window → 05-26): V12_DT4 vs TQ34b ΔRet +1.33pp, ΔDD -0.01pp, verdict 🟢 SWITCH.

## DT4G full-history sim + realistic costs + improvement ablation (2026-05-29)

User asked to re-run DT4G (= DT 4-gate `vnindex_5state_dt_4gate`) full history 2000→now, 1B VND, honest sim on REAL BQ prices. KEY: BQ `tav2_bq.ticker` VNINDEX actually goes back to **2000-07-28** (6286 rows, == DT4 state range) — full sim is possible on real index price, no CSV needed. `sim_dt4g_2000_now.py` (state→alloc {0,.2,.7,1,1.3}, T+1, no look-ahead).

**Cost correction (user)**: deposit 6%→**0.1%** (demand deposit, VN has no deep MMF) + add **0.1% sell tax** (VN securities-transfer tax, sell-side only) on top of 0.1% fee both sides. Impact HUGE: idle-cash rate inflated old results ~+3pp CAGR because model is ~32% of days in CRISIS/BEAR (big cash). Honest baseline: **Full +15.08% / Modern +12.26% (4.19B) / MaxDD −37.6% full, −18.8% modern**, Sh 1.08. (Modern 12.26% now matches old v3.4b pure-index 12.2%, not DT's old proxy-inflated 15.1%.) Pure-index DT NAILS crashes (2008 +70.7pp, 2022 +32pp vs B&H); weakness = NEUTRAL 70% caps bull upside + slow V-recovery. Beats B&H 11/27 yrs raw but dominates on risk-adj (B&H DD −79.9%).

**Improvement ablation** `sim_dt4g_improve.py` (3 ideas tested on corrected baseline):
- **#2 TREND OVERLAY = ADOPT**: NEUTRAL 70%→90% when VNINDEX>MA200 & RSI≤0.72 (full history). Modern +1.05pp, **MaxDD preserved**. Gains exactly in bull yrs (2006 +12.8pp, 2017 +8.6pp, 2025 +3.8pp); crash yrs identical (2008/2022 unchanged). Decouples defense from upside-cap as designed.
- **#4 CONFIRM-DWELL 10 = ADOPT w/ #2**: global Δw no-trade band USELESS (state jumps ≥0.2 > band); debounce at MA200-cross source cuts rebal **326→136 (−58%)** same return/DD.
- **#3 BREADTH THRUST = REJECT**: even fair-tested (breadth ≥50 names from 2007) blows MaxDD −37.6%→**−53.2%**, halves Sharpe — re-enters into continuing crashes (2008 GFC +19.5%→+8.2%). Helps only 2020 (+25 vs +15). Confirms vol-adaptive whipsaw failure. Breadth (%>MA50 over ticker_prune) only reliable from 2007 (univ ≥50).
- **#1 BOND-CASH sleeve = biggest lever** (user agreed: VN no MMF → simulated short-dur gov-bond for idle cash is realistic). User CORRECTED flat-5%: VN 1Y gov-bond is NOT >5% now (~2% in 2020-25; 10Y ~4.3% Mar-2026). Built TIME-VARYING VGB_1Y annual map (~8% early-2000s, **peak 14% 2008 / 12% 2011**, →~2% 2020-25; anchored to real: peak 20% Jun-08, 12% 2010H1&2011H2). Effect: **+2.2pp modern**, big FULL boost (2008/2011 parked cash earned 12-14% → GFC sub-period CAGR +30%). Sharpe now uses FIXED 0.1% rf hurdle all variants (comparable, no artifact).
- **RECOMMENDED**: DT4G + #2 + #4 + time-varying bond-cash → **Full +19.17% / Modern +14.49% / MaxDD −34.8% / Sharpe 1.25 (best)**, 136 rebal. (flat-5% earlier gave 18.12/15.03/−36.7 — superseded by honest time-var.)
- OPEN next: (a) integrate #2 trend overlay into real Kelly stock book (V5) — does +1pp hold?

## CONSOLIDATED MACRO OVERLAY — rates/US-panic/SBV fused into ONE layer (2026-05-29)

User insight: crisis years show rate spikes — can rates aid regime detection? Validated YES on real data. Then user asked to CONSOLIDATE with existing rules (US panic, SBV policy) into one module to avoid rule-sprawl. Files: `test_rates_regime_signal.py`, `sim_dt4g_macro_overlay.py`, `test_v5_macro_integrated.py`.

**Rate signal validation** (`test_rates_regime_signal.py`, real `macro_daily.csv` lending_rate 2000+, lagged 21d, causal): rate 6m-MOMENTUM is best (IC −0.11/−0.15/−0.16 at 20/60/120d). Rates RISING fast → fwd60 −2.5%/fwd120 −3.8% (vs flat +10.5%); rates PEAK→fall → fwd120 **+17.1%** (vs +8.6% avg) = recovery signal. Level matters less than momentum (real_rate IC≈0). BUT only 6/18 CRISIS onsets preceded by high rates → COMPLEMENT (catches inflation/tightening crises 2008/2011/2022, NOT shock crises COVID/2018).

**ONE consolidated module** (`sim_dt4g_macro_overlay.py`) — avoids overlap: Pillar A DOMESTIC MONEY = SBV *refi* 6m-momentum (uses `sbv_macro_overlay.SBV_REFI_EVENTS`; subsumes both "SBV policy" + domestic-rate finding = same driver, no double-count). Pillar B US PANIC = VIX+SPX-DD validated 3-tier (`analyze_us_vn_linkage.py`). Folds in v3.4b BULL-AWARE BYPASS (VNI r6m>15% & >MA200 → ignore Pillar B, keep A; fixes US-override-wrong-in-bull). DXY omitted (weakest, overlaps US). Asymmetric: stress→CAP state ceiling (de-risk early); SBV-cut+US-calm→FLOOR NEUTRAL (re-enter early, rate-driven fix for V-recovery lag that breadth-thrust failed).
- **(a) Confirmed-easing refinement** — NON-OVERFIT a-priori rule (NOT fitted to history): easing must persist ≥10 sessions (same dwell as trend) AND price turn up (Close>Close[t−10]). Avoids re-levering into falling market on monetary signal alone. Pure-index result: Full +19.86% (vs +19.17% base), modern +14.53% (drag REMOVED, was −0.23pp), 2011 +13.49% (vs base +1.44%, DD −23.3→−8.3), COVID +20.71% (vs +16.39%), GFC Sharpe 1.39→1.80. Sharpe 1.25→1.37. Net positive full+modern.
- **(b) Integrated V5/V1 Kelly test** (`test_v5_macro_integrated.py`, 2014-26, macro injected as cap/floor on DT4 state → differs ~106/3089 modern days, 95 de-risk/11 re-risk): MACRO = **REAL ALPHA under leverage**. KELLY (V5): +19.19%→**20.06%** (+0.88pp Full, **+1.90pp OOS20-26**), Sharpe 1.19→1.24, but DD −19.1→−20.9 / Calmar 1.00→0.96 WORSE (Kelly amplifies recovery re-entry risk). BASE (V1): +19.03→19.66 (+0.63pp Full, +1.31pp OOS), DD −17.8→**−17.3 BETTER**, Calmar 1.07→**1.14**, Sharpe ↑ = CLEAN WIN. Alpha concentrated 2020-22 (+4pp: 28.69→32.70 = COVID recovery + 2022 defense); IS14-19 neutral. **CAVEAT: few independent macro-crisis events in modern V5 window (essentially 2020+2022) → confidence MODERATE not high.** Causal (refi=announce date, US lag T-1). **RECOMMEND: adopt macro layer with BASE (return+risk both better); with KELLY = more return at slightly higher DD (return-seeker choice).** NAV: `data/v5_macro_integrated_nav.csv`, `data/dt4g_macro_overlay_*`.

## Macro overlay — robustness validation + paper-trade deploy (2026-05-29, step 1+2)

**Step 1 VALIDATION** (`validate_macro_overlay.py` → `data/validate_macro_report.md`): (A) Parameter sensitivity one-at-a-time = ROBUST PLATEAU: every variation of US/SBV thresholds, easing-confirm dwell, price-confirm lookback, refi lag gives Full ΔCAGR ∈ [+0.39,+0.76]pp — EXCEPT bull_bypass=False (−0.67pp), which CONFIRMS bull-bypass is structural-necessary not a tuned knob. (B) Pure-index modern LOO: modern pure-index alpha is only +0.05pp (negligible) → macro's modern value is NOT index-allocation; it's leverage/stock-book interaction (shows only integrated). (C) Per-year integrated attribution (from saved NAV): alpha DISTRIBUTED across 6 yrs (2014+4.1/2018+2.1/2020+1.2/2021+7.3/2022+3.6/2023+2.0 positive; 2015 −5.2 cost from China-devaluation US cap, 2019/24/25 small neg) — NOT a single-event fluke, but real dispersion → MODERATE confidence. (D) Cost-stress TC 0.3% (`SLIP=0.003 FRICT=0.003 python test_v5_macro_integrated.py`): alpha SHRINKS ~half but SURVIVES positive: KELLY +0.32pp / BASE +0.37pp Full (OOS ~+1pp); BASE keeps better DD/Calmar. VERDICT: robust enough to paper-trade; BASE recommended.

**Step 2 DEPLOY** — reusable live module + shadow A/B:
- **`macro_state_live.py`** = production module `get_macro_state(start,end,bq)` → macro-adjusted 5-state (DT4 base from TQ34b-clean+_dt_4gate, cap/floor from fused SBV refi + US VIX/SPX + bull-bypass + confirmed-easing). Causal. Params frozen (validated plateau). Standalone test: 2024-26 diverges 18d (all de-risk, Apr-2025 tariff scare); latest 2026-05-26 = NEUTRAL (no cap) == DT4.
- **`pt_v12_macro.py`** = clone of pt_v12_dt4.py with state swapped to macro_state_live (BASE/V6 ETF = recommended config). Transparent outputs `data/pt_v12_macro_*`. Runs+reconciles (≡ pt_v12_dt4 when 0 state-diff, as now).
- Wired: `papertrade_daily.bat` step [3b]; `papertrade_compare.py` added V12_MACRO arm + "V12_MACRO vs V12_DT4" A/B section (delta = pure macro overlay since both share DT4 base). Current window 2026-04→05: **0 divergence ⚪ (benign — macro inactive, as expected; diverges only on US-panic/SBV event)**.
- KEY HONEST NOTE: macro alpha is EVENT-DRIVEN — paper-trade shows ~0 until a macro stress/easing episode; can't be read in benign windows. Decision needs a macro event in the live window.

## Macro cap WHIPSAW fix — confirmation dwell K=7 (2026-05-29)
User flagged Apr-2025 (Trump-tariff VIX oscillation) caused ~7-10 meaningless 1-3 day macro transitions — wanted balance like smooth DT4-only (93 transitions). ROOT CAUSE: defensive cap reacted INSTANTLY (capped when VIX/SPX crossed threshold, released the moment it crossed back) — easing leg had confirm-10 but cap had NO dwell = asymmetric whipsaw. FIX (`tune_macro_smoothing.py` → `data/tune_macro_smoothing.md`): causal CAP-COMMIT dwell — a new cap level must persist K sessions to commit (debounces tighten AND release). Grid K=0/3/5/7/10: **K=7 chosen** — transitions 192→**112** (DT4=93; ~19 residual = real crisis interventions), **Apr-2025 7→0 flicker**, Full CAGR +19.66→**+20.10%** (whipsaw was net COST — removing it IMPROVES return, user's "vô nghĩa" intuition confirmed), crisis protection INTACT (2011 +11.4→+12.4%, 2008/2020/2022 kept; real crises persist >7d so still commit). Both legs now have causal dwell: cap=7-session persist, easing=10-session+price-confirm. APPLIED: `macro_state_live.py` (P['cap_commit']=7 + _commit()), `sim_dt4g_macro_overlay.py` (CAP_COMMIT=7). Regenerated `vnindex_5state_dt4_macro.csv`, `data/dt4g_macro_overlay_nav.csv`, HTML dashboards (`dt4g_macro_system.html` + `dt4g_macro_transitions.html` now 112 trans; BQ cross-check max|Δ|=0.0). In 2024-26 live window macro now 0-diff from DT4 (Apr-2025 scare debounced away — DT4 handles short scares, macro only fires on persistent crises). NAV 1B→113.3B full / B&H 18.8B.
## CANONICAL NAME: DT5G (2026-05-29)
**DT5G** = DT 4-gate (4 state gates) + **Macro 5th gate** (macro overlay: SBV refi money + US panic VIX/SPX, bull-aware bypass, **cap-commit K=7** anti-whipsaw, confirmed easing). The "5" = the macro confirmation gate on top of the 4 state gates — NOT a 5-gate state filter ("DT 5-gate" does NOT exist, grep-verified; slot free). DT5G ≡ DT4G in benign windows, diverges only on persistent macro stress/easing. Full sim 2000→now: CAGR +20.10%, Sharpe 1.36, MaxDD −34.7%, 1B→113.3B (vs B&H 18.8B), 112 transitions. Display name = DT5G everywhere; underlying files keep `dt4g_macro_*` / `macro_state_live.py` names (pipeline stability). Cross-refs: was called "DT4G+macro" in prior session notes above = same thing.

## DT4G+MACRO ADOPTED as production base for paper-trade (2026-05-29)
User decision: macro trusted enough (backtest evidence, NOT paper-trade — macro is event-driven so benign-window A/B can't validate it; adopt-before-event insurance logic). **DT4G+macro = universal base** for non-ensemble paper-trade systems.
- **V11** (`pt_v11_tq34b.py`): state DT_10_25_25 → **DT4G+macro** via `macro_state_live.get_macro_state()`. Keeps KELLY. Runs+reconciles ($0 diff).
- **V12** production = `pt_v12_macro.py` (DT4G+macro). **RETIRED from daily run**: `pt_v12_tq34b` (old TQ base) + `pt_v12_dt4` (DT-only shadow) — superseded.
- `papertrade_daily.bat` trimmed to 4 sims + compare; `papertrade_compare.py` SYSTEMS=[V11,V12(=macro),V121_ENS,V121_Kelly], removed obsolete DT4-vs-TQ & macro-vs-DT4 A/B sections.
- **ENSEMBLE VALIDATION (`test_v12_ensemble_dt.py` + DT4_MACRO arm)**: user chose "validate first" — CONFIRMED DT4G+macro HURTS ensemble: ENS→V12.1 FULL −0.14pp / **OOS20-26 −2.30pp** / Sharpe 1.52→1.48 / DD worse (IS +2.07pp only). Matches prior research (ensemble pre-empts state timing → DT redundant+harmful OOS; macro ~0 doesn't rescue). **DECISION: V121 ensemble STAYS on TQ34b.** (`data/v12_ensemble_dt_nav.csv` has all 3 state arms.)
- Net: V11/V12 on DT4G+macro; ensemble on TQ34b. Single state source = `macro_state_live.py` (cap-commit K=7). `pt_dt4_vs_tq34b_ab` (V1-V5 foundation A/B, end-June) left as-is.

## HTML deliverables for full-2000 verifiable sim: `sim_dt4g_macro_html.py` builds dt4g_macro_system.html (overview + merged 3-strategy×3-period table + LIVE BQ cross-check tab showing max|Δ|=0) + dt4g_macro_transitions.html (VNINDEX colored by state + transition table). Verifiable daily CSV `data/dt4g_macro_sim_daily.csv`. Did NOT overwrite canonical vnindex_5state_system.html/vnindex_transitions_v2.html.
- Files: `sim_dt4g_2000_now.py`, `sim_dt4g_improve.py`, `data/dt4g_2000_now_report.md`, `data/dt4g_improve_report.md` (+ _nav.csv each).

## Files
- `simulate_state_timing.py` — pure-VNINDEX money sim (STATE_ALLOC 0/0.2/0.7/1.0/1.3)
- `build_dt_variants_csv.py` — DT asym-commit builder (defines the algorithm)
- `_cmp_3models.py`, `_synth_experiment.py`, `_synth_floor.py` — this analysis (temp scripts)
- `vnindex_5state_dt_10_25_25.csv` — DT series

## Cross-refs
- [[v5-kelly-dt-smoothing]] — DT helps Kelly (V5) via transition-friction reduction; pre-2014 risk
- [[cross-architecture-synthesis]] — DT benefit context-dependent in integrated systems
- [[ng-h-nh-tinh-t-current-live-5-state]] — Tinh Te spec
