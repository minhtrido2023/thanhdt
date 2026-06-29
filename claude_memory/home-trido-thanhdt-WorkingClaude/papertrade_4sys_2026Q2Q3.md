---
name: papertrade-4sys-2026q2q3
description: 4-system paper-trade comparison Apr-Aug 2026 — V11+TQ34b vs V12+TQ34b vs V12+LIVE vs V12.1+Ensemble(M1+M3r)+TQ34b
metadata: 
  node_type: memory
  type: project
  originSessionId: a2603c03-3fca-4e15-8a88-84014af0cd38
---

# Paper-Trade 4 Systems — 2026-Q2/Q3 (Apr 1 → Aug 31, 2026)

**Why:** decision target Sept 2026 for production system. 4-way head-to-head: 3 baselines + ensemble candidate from concentration-switch research (2026-05-22).

**How to apply:** monitor daily, decision at end of August.

## Systems

| Key | Spec | Driver script |
|-----|------|---------------|
| `V11_TQ34b` | V11 Song Sinh (BAL+VN30+ETF) + Tam Quan v3.4b state | `pt_v11_tq34b.py` |
| `V12_TQ34b` | V12 Âm Dương (BAL+LAGGED HL_3y+ETF) + Tam Quan v3.4b | `pt_v12_tq34b.py` |
| `V12_LIVE` | V12 Âm Dương + LIVE Ngũ Hành Tinh Tế (production state) | `pt_v12_live.py` |
| **`V121_ENS` ⭐** | V12.1 ÂD-TT (S2 sizing on LAGGED) + **M1+M3r AND-HOLD ensemble** + TQ v3.4b | `pt_v121_ensemble.py` |

**V121_ENS architecture**: 25B BAL leg [REDACTED]-on. 25B switched leg routes between VN30 (V11 mode) and LAGGED V12.1 (V12 mode) based on AND-HOLD ensemble of:
- M1 = VNI − Equal-Weight 6M return (winner-takes-all detector)
- M3r = Top10 (rolling 1Y ADV) − all-prune 6M return (no lookahead)
- Rule: both > expanding-median (252d warmup) → V11; both < → V12; disagree → keep current. Switch cost 0.5% per flip.

## Backtest validation (test_rolling_m3_v121_ensemble.py)

| Window | V11 | V12 | V12.1 | **V121_ENS** |
|---|---:|---:|---:|---:|
| FULL 14-26 CAGR | 21.14% | 22.29% | 23.03% | **24.70%** |
| OOS 24-26 CAGR | 28.88% | 23.93% | 23.43% | **31.92%** |
| Sharpe OOS | 1.57 | 1.71 | 1.64 | **1.81** |
| MaxDD OOS | -16.91% | -8.70% | -10.11% | -10.89% |

V121_ENS wins FULL CAGR (+1.67pp vs V12.1 static, +3.56pp vs V11). 26 flips/12y (~2.2/yr). Y2024 weak (+11.3% vs V12 +22.9%, AND-HOLD held V11 too long in sideways/recovery year).

## Outputs

- `data/pt_v121_ens_logs.csv` — daily NAV + cash + active_leg + ens_signal
- `data/pt_v121_ens_transactions.csv` — buys/sells + ETF + SWITCH events (book="SWITCH") + MTM phantoms
- `data/pt_v121_ens_open_positions.csv` — open positions at end (BAL + active leg)
- `data/pt_v121_ens_report.md` — reconciliation + switch events log
- `data/papertrade_compare4.md` / `.csv` — combined 4-way report (replaces ...compare3.*)

## Operations

- **Scheduler**: Windows scheduled task `PaperTrade3Sys` runs `papertrade_daily.bat` at 15:30 daily. Bat updated 2026-05-22 to include step [4/5] `pt_v121_ensemble.py` before final compare.
- **Common base date**: 2026-04-01, 50B fresh start each system (independent).
- **State source**: `tav2_bq.vnindex_5state_tam_quan_v34b_clean` for TQ34b variants; `tav2_bq.vnindex_5state` (LIVE) for V12_LIVE.

## Initial readings (smoke-test 2026-05-22, window 32 trading days)

| System | Total Ret | CAGR | Sharpe | MaxDD |
|---|---:|---:|---:|---:|
| V11 + TQ34b | +3.32% | +28.18% | +3.60 | -1.81% |
| V12 + TQ34b | +0.96% | +7.52% | +1.82 | -1.43% |
| V12 + LIVE | +1.88% | +15.23% | +1.45 | -1.83% |
| **V121_ENS** | +3.32% | +28.18% | +3.60 | -1.81% |
| VNI B&H | +12.33% | +142.27% | +5.33 | -1.64% |

V121_ENS = V11 in this window (ensemble held V11/VN30, 0 flips). Divergence will appear when M1 or M3r flips. All 4 systems trailing VNI B&H +12.33% by 9-11pp — same Q1-2026 pattern as backtest (v3.4b NEUTRAL conservatism cost during rally).

## GO-LIVE timeline PULLED FORWARD (2026-05-28)

User wants to **go live early June 2026**, deciding the foundation **2026-05-29 (tomorrow)** — leaning **V4 + DT4-gate**. I rescheduled Windows task **`DT4FoundationDecision`** from [REDACTED]30 → **2026-05-29 16:00** (runs after the 15:30 daily refresh) and set `pt_dt4_vs_tq34b_ab.py` `DECISION_DATE="2026-05-29"`. That A/B (`data/pt_dt4_vs_tq34b_ab_report.md` / copied to `DT4_FOUNDATION_DECISION.md`) is the go-live evidence: V1–V5 on DT4 vs TQ34b foundation, fresh SIGNAL_V11, real E1VFVN30, prod-spec, 50B each.

**Live A/B standing (window 2026-01-01 → 05-26): DT4 sweeps TQ34b 5-0.** V4: DT4 −2.24% vs TQ34b −9.28% (Δ+7.04pp, DD −13.3 vs −14.8). V5: DT4 −0.41% vs TQ34b −10.81% (Δ+10.40pp). All negative (captures the early-2026 drawdown window) → systems protecting capital; verdict label "🟡 INCONCLUSIVE (short window)".

**How to apply / honest framing**: the live window is short (~5 mo, ~8 weeks since Apr-1 fresh-start) → low statistical power; treat live A/B as an **execution sanity-check** (does it deploy/behave sensibly, no blow-up), NOT the deciding statistical evidence. Lean the **structural choice on the 12y backtest**: V4+DT4 = 22.47%/Sh1.56/Calmar1.24/DD−18.1% (balanced, user's lean) vs V5+DT4 = 23.43%/Sh1.46/Calmar1.12/DD−20.8% (max return, deeper DD). Both DT4 > TQ34b confirmed live + backtest. Apply ~−1.5pp/yr real-world haircut to any backtest CAGR. The `DT4DecisionReview` task (V12-only, [REDACTED]) is now stale relative to this V1–V5 decision — V12 isn't the candidate. Verified by `sim_v5_dt4_transparent.py` (transparent per-leg, 4-gate reconciliation matches canonical).

## Macro-smooth overlay on PROD SPEC — official A/B (2026-05-29)

Tested DT4 vs **DT4+macro-smooth** on the real prod-spec harness (`run_5systems_dt4.py`, now env-parametrized `DT_TABLE`; macro state uploaded to BQ `tav2_bq.vnindex_5state_dt4_macro`, 6286 rows). Macro = SBV refi 6m-momentum + US VIX/SPX fused into one asymmetric cap/floor on the DT4 state, with cap-confirmation dwell K (the "smooth" debounce; tune table `data/tune_macro_smoothing.md` → K≈3-7). Full 2014→2026-05-15:

| Hệ | DT4 | +macro | Δ |
|---|---|---|---|
| **V4** | 22.47%/Sh1.56/DD−18.13/Cal1.24 | 21.92%/Sh1.54/**DD−16.66**/Cal1.32 | **−0.55pp CAGR, DD +1.47pp better, OOS24 −2.49pp** |
| **V5** | 23.43%/Sh1.46/DD−20.84/Cal1.12 | **24.54%/Sh1.52/DD−19.50/Cal1.26** | **+1.11pp CAGR, +0.06 Sh, +0.14 Cal, DD +1.34pp better; OOS20 +1.30pp, OOS24 +0.47pp** |

**Verdict (OVERTURNS the reduced-harness "macro inert ~+0.05pp" reading)**: on prod spec macro splits by system. **V5 (KELLY): macro is a genuine net win** — its cap-de-risk trims V5's deep-DD weakness (−20.8→−19.5) AND adds +1.1pp CAGR; V5+macro Calmar 1.26 ≈ V4-plain 1.24 but at higher CAGR. **V4 (BASE): macro NOT worth it** — costs −0.55pp full / −2.5pp OOS24 (over-de-risks the 2024-26 bull), DD help marginal because BASE's 30% cash buffer already overlaps the macro de-risk. Why prod-spec ≠ reduced-harness: prod deploys more capital → the macro "brake" has more exposure to protect (opposite of DT-parking which mattered LESS with more deployment).

**REVISED stance (2026-05-29, user pushback — accepted): macro = cheap DORMANT tail-hedge, worth including for BOTH V4 and V5.** User named it **"DT5" = DT4 + macro overlay**. My earlier "V4: macro not worth it" over-weighted raw CAGR; on RISK-ADJUSTED terms macro improves BOTH: V4 DD −18.13→−16.66 / Calmar 1.24→1.32; V5 DD −20.84→−19.50 / Calmar 1.12→1.26. Footprint is tiny — vs true DT4 gate, macro changes state on **only 60/3089 modern days (1.9%)**, concentrated 2014(11)/2020(15)/2023(34), **ZERO in 2015-19, 2021-22, 2024, 2025, 2026**; 49/60 are cap-DOWN (de-risk). **Currently dormant: macro state = DT4 = 3 (NEUTRAL) as of 2026-05.** Key nuance: the OOS24 CAGR gaps (V4 −2.49pp, V5 +0.47pp) are NOT macro acting in 2024-26 (0 diffs) — they're **path-dependent echoes of the 2023 caps** (de-risked 2023 → different carry into 2024). So at go-live macro changes NOTHING near-term; it only arms in a stress regime (SBV-tighten/US-panic). **The only real caveat is OPERATIONAL not performance**: macro has never fired in live production → when it needs to (stress), the daily SBV-refi + US-VIX/SPX fetch (`macro_state_live.py`) MUST be reliable; a broken macro feed = no protection exactly when needed. Recommendation: include DT5 (macro) in the go-live candidate for whichever of V4/V5 is chosen, conditioned on a robust macro data pipeline. Files: `run_5systems_dt4.py` (DT_TABLE env), BQ `tav2_bq.vnindex_5state_dt4_macro`, `data/5sys_dt4_macro_nav.csv`, `sim_dt4g_macro_overlay.py`, `vnindex_5state_dt4_macro.csv`, `data/dt4g_macro_overlay_report.md`, `data/validate_macro_report.md`.

## Macro pipeline health-check + fail-safe wired (2026-05-29, pre-go-live)

Built `macro_healthcheck.py` (Tier 1 staleness + Tier 2 sanity/frozen-feed + Tier 5 liveness/heartbeat + Tier 6 fail-safe). Checks the 4 DT5G inputs: BQ `vnindex_5state_tam_quan_v34b_clean` + BQ `ticker` VNINDEX (freshness in TRADING days via np.busday_count, max 3td), `us_market_history.csv` (fresh+range+frozen-VIX), `SBV_REFI_EVENTS` (value-range + INFO age reminder — can't auto-detect a missed SBV change). End-to-end probe calls `get_macro_state`. Writes `data/macro_health.json` + `macro_health_last_success.txt` heartbeat + `MACRO_HEALTH_ALERT.md`; Telegram alert on non-HEALTHY (via `telegram_recommend.send_telegram_text`); exit 0/1/2. SEV1 if a feed is stale/broken WHILE market stressed (VIX>MA252 or VNI<MA200).

**Fail-safe primitive**: added `macro_state_live.get_gated_state(start,end)` — reads `macro_health.json`, returns DT5G `state` only if status≠FAILED AND recommended==DT5G_macro AND report fresh (≤1440min); else **fail-CLOSED to DT4-only** (the `state_dt4` column get_macro_state already returns). Production state access should go through this, NOT get_macro_state directly. Tested: health FAILED → returns DT4_only. ✓

**US feed fixed**: `pull_us_market.py` had hardcoded `end="2026-05-21"` (why feed was stuck at 05-20) → now dynamic `end=now+2d` + trims trailing incomplete sessions (today's VIX-in/SPX-pending row). Re-pulled → fresh to 05-28.

**Wired into `papertrade_daily.bat`**: `[0a] pull_us_market` (early) + `[0c] macro_healthcheck` (after state/US, before pt consumers). NOTE: bat already adopted DT4G+macro as base (pt_v11_tq34b + pt_v12_macro; pt_v12_tq34b/pt_v12_dt4 retired); ensemble V121 still on TQ34b pending integrated validation.

**State now SELF-UPDATES from ticker (2026-05-29, user directive — RESOLVED the stale-table blocker).** Decision: do NOT depend on the lagging BQ `vnindex_5state_tam_quan_v34b_clean` table; recompute the v3.4b base from fresh BQ `ticker` via the canonical chain. Done: (1) ran the rebuild chain (rm pkl caches → `vnindex_5state_ew_v1` → `build_concentration_history` → `vnindex_5state_dual_v3` → `STATE_WORKDIR=MAIN deploy_v3_4b_package/build_v3_1_clean` → cp to `_full_history` → `build_v3_4_bull_aware` → `build_dt_4gate`), LOCAL CSVs only, BQ deploy SKIPPED — fresh to 05-28 (NEUTRAL=3). (2) `macro_state_live.get_macro_state` now reads the LOCAL `vnindex_5state_tam_quan_v3_4b_full_history.csv` (BQ table fallback only if missing). (3) `macro_healthcheck.py` Tier-1 source #1 changed to the local CSV freshness. (4) INFO checks (SBV verify-reminder for long-stable refi) no longer degrade status / no longer alert — fixed daily Telegram noise. (5) wrapped the chain in **`rebuild_state_from_ticker.bat`** (local-only, bug-guards: del caches + STATE_WORKDIR) and wired it into `papertrade_daily.bat` as `[0a2]` (after pull_us_market, before healthcheck) → state self-updates daily. **Result: health-check HEALTHY, `get_gated_state` serves DT5G_macro, state fresh to 05-28.** Macro still dormant (cap=9/easing=False). Note: BQ `vnindex_5state` / `v34b_clean` are no longer on the macro critical path, but `recommend_holistic.py` (BA live) still reads BQ `vnindex_5state` — that LIVE table still needs its own deploy if BA-live consumes it.

## GO-LIVE deploy package built (2026-05-29): `deploy_golive_dt5g_v4/`

Dev go-live deploy for **V4 (V121_ENS + BASE {3:0.7}) on DT5G** (gated state, fail-safe DT4), output = daily order/position recommendations. Two layers as user scoped ("1=DT5G, 2=V4+DT5G"):
- **Layer 1 (DT5G engine)**: `publish_gated_state.py` → `macro_state_live.get_gated_state` → publishes gated series to BQ `tav2_bq.vnindex_5state_dt5g_live` (3091 rows to 05-28) + `golive_state_today.json`. Depends on pull_us_market → rebuild_state_from_ticker → macro_healthcheck run first.
- **Layer 2 (V4 recommender)**: `golive_recommend.py` → reads SIGNAL_V11 with state5 from `vnindex_5state_dt5g_live`, applies D1+SV_TIGHT+overheat, builds BAL + (ensemble-mode) VN30/LAGGED books, BASE ETF parking, → `out/golive_recommendations_<DATE>.{md,csv}`. Same logic as run_5systems_dt4 V4 leg, point-in-time "today".
- **Orchestrator** `golive_daily.bat` (5 steps), `README.md`, `requirements.txt`.
- **To switch to V5**: change `ETF_BASE` → `{3:1.0}` in golive_recommend.py (only knob).
- All steps tested OK end-to-end. Test day 2026-05-28 NEUTRAL → 0 new BAL/VN30 entries (correct: no signals in V4 tiers; only COMPOUNDER_BUY KLB/PAN which V4 doesn't trade), action = hold + park 70%. gate served DT5G_macro (health HEALTHY). bq load reuses `simulate_holistic_nav.BQ_BIN` + shell=True (bq is a Windows .cmd, not on python subprocess PATH).

## Related research files

- [[tam_quan_v3_4b_dinh_tam]] — state-source codename
- [[ba_v12_1_am_duong_tinh_te]] — V12.1 spec with S2 sizing
- `compare_v11_v12_v121_with_v34b.py` — first comparison (no switching)
- `compare_v11_v12_concentration_switch.py` — M1/M2/M3 single-metric switches
- `test_m1_m3_ensemble.py` — AND/OR consensus on top of M1+M3 static
- `test_rolling_m3_v121_ensemble.py` — final validation with rolling M3 + V12.1 LAGGED → produced V121_ENS spec
