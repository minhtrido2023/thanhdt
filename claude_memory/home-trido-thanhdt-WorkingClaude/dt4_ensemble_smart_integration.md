---
name: dt4-ensemble-smart-integration
description: "DT4 integration into V121_ENS. Reduced harness suggested DECOUPLE+weekly was a +2.9pp win — but PROD-SPEC re-validation (run_prodspec_dt_v6.py) REVERSES it: DT-parking does NOT beat V5/V121_Kelly; gains shrink to ~0 vs V4 BASE; WEEKLY cadence FAILS on prod spec. V5 (KELLY) stays champion. Reduced-harness gains were artifacts."
metadata:
  node_type: memory
  type: project
  originSessionId: 08a5052c-9cbc-4e6a-a377-48ffb1d4f142
---

# DT4 × ensemble (V121_ENS) — smart integration (2026-05-28)

User: "DT4 vượt trội TQ34b; tích hợp vào Kelly ensemble paper-trade sao cho hợp lý hơn thay vì tích hợp thô như trước." Scope chosen: **backtest research only, no paper-trade changes**. User selected ALL 4 designs + a 5th custom (switch-decision timeframe).

## ⚠️ TOP-LINE VERDICT (read this first — PROD-SPEC re-validation, 2026-05-28)
The reduced-harness research below (phases 1-4) suggested DECOUPLE {3:0.85}+weekly was a +2.9pp win. **The user then asked to compare directly against V5 production. On the FULL prod spec (`run_prodspec_dt_v6.py`, identical to `run_5systems_prodspec.py`: max_pos=12, tier_weights 10%, RE_BACKLOG_BUY, SV_TIGHT, t1_open_exec), the win EVAPORATES:**

| Arm (prod spec) | Full | IS | OOS20 | OOS24 | DD | Calmar | Sharpe | flips |
|---|---|---|---|---|---|---|---|---|
| V4 BASE daily (canon) | 24.24% | 16.10 | 32.35 | 30.97 | **-15.98%** | **1.52** | **1.71** | 26 |
| V4 BASE weekly | 23.34% | — | — | 30.59 | -18.08% | 1.29 | 1.65 | 18 |
| **V5 KELLY daily (=V121_Kelly)** | **25.82%** | 16.31 | **35.40** | **36.57** | -18.41% | 1.40 | **1.71** | 26 |
| V5 KELLY weekly | 25.15% | — | — | 36.29 | -23.16% | 1.09 | 1.66 | 18 |
| V6 DT085 daily | 24.50% | **18.38** | 30.54 | 31.71 | -16.30% | 1.50 | 1.62 | 26 |
| V6 DT085 weekly | 23.18% | — | — | 31.07 | -17.29% | 1.34 | 1.51 | 18 |
| V6b DT KELLY daily | 24.18% | 16.78 | 31.57 | 34.92 | -17.43% | 1.39 | 1.56 | 26 |

**Conclusions (decision-grade):**
1. **DT does NOT beat V5/V121_Kelly.** V5 wins return (25.82 vs 24.50, +1.32pp), OOS24 (+4.86pp), AND Sharpe (1.71 vs 1.62). DT085 only wins DD (-16.3 vs -18.4) + Calmar (1.50 vs 1.40).
2. **DT085 is even DOMINATED by V4 BASE** on risk-adjusted terms: V4 Sharpe 1.71 > 1.62, Calmar 1.52 > 1.50, DD -15.98 better, at only -0.26pp Full. DT-parking adds ~nothing over plain BASE on prod spec.
3. **WEEKLY cadence FAILS on prod spec** — hurts EVERY arm (V4 -0.90, V5 -0.67 + DD -23%!, V6 -1.32) and worsens DD. The reduced-harness E0 "weekly +1.05pp" finding does NOT generalize (prod-spec uses cached M1 + t1_open + 26 vs 29 flips → weekly delays beneficial flips). **Keep DAILY.**
4. **WHY DT shrank**: prod spec deploys more capital (max_pos=12 + tier_weights + RE_BACKLOG) → less idle cash → the ETF-parking channel (DT's ONLY lever, since SVT inert) matters far less. Same "diminishing-returns-with-architecture-complexity" law as [[cross-architecture-synthesis]]. The reduced harness's leakier legs gave parking (and DT) artificial room.
5. **Lesson reinforced**: NEVER quote a DT-integration delta from a reduced/research harness as decision-grade — re-validate on prod spec. Reduced harness said +2.9pp; prod spec says ~0 vs V4 / negative vs V5.

### V12 (non-ensemble) prod-spec state test — DT4 also does NOT beat LIVE/TQ34b (2026-05-28)
`run_prodspec_v12_state.py` — V12 = BAL + LAGGED, only BAL-parking state varies (BASE {3:0.7}):

| Arm | Full | IS | OOS20 | OOS24 | DD | Sharpe |
|---|---|---|---|---|---|---|
| V12 +TQ34b | 21.21% | 13.59 | 28.80 | 23.51 | -14.43% | 1.64 |
| V12 +LIVE | 21.22% | 13.59 | 28.82 | 23.57 | -14.43% | 1.64 |
| V12 +DT4 | 21.07% | **14.63** | 27.45 | 22.86 | -14.33% | 1.60 |
| V12.1+LIVE | 22.10% | 14.23 | 29.96 | 23.36 | -15.34% | 1.64 |
| V12.1+DT4 | 21.96% | 15.24 | 28.64 | 22.71 | -15.22% | 1.61 |

- **LIVE ≡ TQ34b confirmed: 4/3082 state diffs** (LIVE BQ table = v3.4b). DT differs on 1085/3082 days but nets ~0.
- **V12+DT4 = -0.15pp Full vs LIVE; WORSE on OOS20 (-1.37) + OOS24 (-0.71) + Sharpe (1.60 vs 1.64); only -0.1pp better DD.** DT better IS (+1.04) but worse everywhere else. Same collapse as ensemble (prod spec deploys more → idle cash small → parking channel muted).
- **The reduced-harness "V12+DT +1.06pp" did NOT survive prod spec.** And the live A/B (pt_v12_dt4 vs pt_v12_tq34b) +1.33pp reading is a ~32-session window (Apr-May 2026) = path-dependent noise; the 12y prod-spec says slightly negative. ⚠️ **Re-weight the end-June V12_DT4 decision toward KEEP-TQ34b** — short-window live lead contradicts 12y prod-spec.
- Harness validated: V12+TQ34b=21.21% == 5-system V2; V12+LIVE=21.22% == V3. ✓

**Recommendation: keep V5 (V121_Kelly) as champion. Do NOT deploy DT-parking or weekly cadence into the ensemble. DT4 also not worth it for V12 on prod spec.** If a lower-DD variant is ever wanted, V4 BASE already gives Calmar 1.52 / Sharpe 1.71 / DD -16% — better than DT085. Files: `run_prodspec_dt_v6.py`, `data/prodspec_dt_v6_nav.csv`.

---
### Reduced-harness research (phases 1-4) — superseded by the prod-spec verdict above, kept for the mechanism findings

## Harness note (important for reading ALL ensemble numbers)
Production-faithful canonical V121_ENS in this harness = **Full 21.37%, OOS24 30.26%, DD -17.64%, Sharpe 1.49, 29 flips** — NOT the documented 24.7%. Reason: I recompute M1/M3r live from BQ over `ticker_prune` (LAG-126) **exactly as the live `pt_v121_ensemble.py` does** (29 flips ≈ live 26). The 24.7% came from an OLDER cached signal CSV (`compare_v11_v12_concentration_switch.csv`) with a different universe. **Trust the BQ-recompute number; treat older cached-signal ensemble CAGRs as inflated.** All Δ below are within this harness (apples-to-apples).

## WINNER: DECOUPLE + WEEKLY cadence
**DT4 drives ONLY the ETF parking dial at intensity {3:0.85}; TQ34b keeps SVT; switch decided weekly (cad=5, min-dwell=40).**

| Config | Full | ΔFull | OOS24 | ΔO24 | DD | Sharpe | flips |
|--------|------|-------|-------|------|-----|--------|-------|
| CANON (daily, TQ park 0.7) | 21.37% | — | 30.26% | — | -17.64% | 1.49 | 29 |
| DEC park=DT {3:0.7} daily | 22.45% | +1.09 | 29.62% | -0.65 | **-15.90%** | 1.48 | 29 |
| **DEC {3:0.85} daily** | 23.39% | +2.02 | 32.33% | +2.07 | -17.13% | 1.50 | 29 |
| DEC {3:1.0}(KELLY) daily | 22.61% | +1.24 | **34.53%** | +4.26 | -18.70% | 1.43 | 29 |
| **DEC {3:0.85} WEEKLY ⭐** | **24.26%** | **+2.90** | 32.06% | +1.79 | -17.13% | **1.53** | **19** |
| CANON WEEKLY (no DT) | 22.41% | +1.05 | 29.94% | -0.32 | -17.64% | 1.56 | 19 |

Decomposes into 2 independent levers (sub-additive, clean): **parking 0.7→0.85 via DT smoothing ≈ +2.0pp**; **weekly switch cadence ≈ +1.0pp**. Pareto improvement vs the BASE-parking canonical (more return, DD≈flat-better, Sharpe up, half-fewer flips).

## BUT vs V121_Kelly (TQ34b + full KELLY {3:1.0}) — it's a FRONTIER TRADEOFF, not a clean DT win (phase4, 2026-05-28)
User asked: how does the DT winner compare to just cranking TQ34b parking to full KELLY (no DT)? Ran TQ-park sweep. All WEEKLY cadence:

| Config | Full | OOS24 | DD | Sharpe | flips |
|--------|------|-------|-----|--------|-------|
| Canonical TQ {3:0.7} | 22.41% | 29.94% | -17.64% | 1.56 | 19 |
| TQ {3:0.85} | 23.02% | 33.25% | -19.83% | 1.56 | 19 |
| **V121_Kelly = TQ {3:1.0}** | **24.40%** | **36.52%** | **-21.82%** | **1.57** | 19 |
| **DT {3:0.85} (the "winner")** | 24.26% | 32.06% | **-17.13%** | 1.53 | 19 |
| DT {3:1.0} | 23.64% | 34.33% | -18.70% | 1.47 | 19 |

**V121_Kelly ≈ DT{0.85} on Full (24.40 vs 24.26, noise) and Sharpe (1.57 vs 1.53); V121_Kelly WINS OOS24 +4.46pp; DT{0.85} WINS DD by 4.7pp (-17.1 vs -21.8).** So full-KELLY-on-TQ is the aggressive frontier corner (max return + max OOS24, deep DD, SIMPLER — no DT/2nd state series); DT{0.85} is the balanced corner (same return, much lower DD, smoother).

**DT's TRUE value = drawdown efficiency, not raw return.** Two clean framings:
- **iso-intensity**: at SAME parking %, DT-park < DD than TQ-park [REDACTED]. At 0.85 DT Pareto-DOMINATES TQ (24.26/-17.1 vs 23.02/-19.8). At 1.0 DT trades -0.76pp return for +3.1pp DD.
- **iso-drawdown (~-17%)**: TQ can only run {3:0.7}=22.41%; DT can run {3:0.85}=24.26% at the same DD → **DT delivers +1.85pp CAGR at iso-DD.** To match DT{0.85}'s return with TQ you must go {3:1.0} and eat -4.7pp more DD.
- DT CANNOT match the absolute max-return corner (TQ{1.0}=24.40/OOS24 36.52) — its smoothing/0.85-cap holds back the aggressive 2024-26 rally upside.

**Recommendation depends on DD tolerance.** If max return/Sharpe and -22% DD is acceptable → **V121_Kelly (TQ {3:1.0}) is marginally better AND simpler** (no DT). If smooth path / -17% DD at ~same return matters (user's stated Kelly-portfolio path concern) → **DT DECOUPLE {3:0.85}**. NAV: `data/dt_ens_phase4` (printed; script `research_dt_ens_phase4.py`).

## Why {3:0.85} not full KELLY {3:1.0}
0.7 = too much idle cash drag (best DD though); 1.0 = over-commits index in NEUTRAL → worst DD (-18.70) when DT-NEUTRAL is actually pre-bear; **0.85 = keeps 15% cash buffer, best risk-adjusted.** KELLY only wins raw OOS24 (+4.26) at DD/Sharpe cost. Adding BEAR parking `{2:0.4,3:0.85}` HURTS (+0.28pp only — parking in BEAR adds index beta while index falling). REJECT.

## MECHANISM (the key insight — validates user's "crude was the problem")
1. **SVT/overheat channel is INERT.** Control test: opposite-decouple (SVT=DT, park=TQ) → legs **byte-identical** to canonical (BAL 240.40B / VN30 217.09B). System is **capacity-constrained** (max_pos=10, hold=45d) not signal-constrained, so which state feeds SVT doesn't change executed trades. Confirms the prior C3_clean "capacity-bound" finding.
2. **→ 100% of the DT benefit flows through ETF PARKING.** DT's 53 vs 155 transitions = less rebalance friction + smoother regime read for the Kelly dial — exactly DT's documented strength (pure-VNINDEX Kelly metric, V5 KELLY +1.96pp). The crude swap conflated channels AND was anchored on the inflated cached-signal baseline.
3. **Switch-decision timeframe (custom Q):** keep 126d (6M) lookback — faster 63d (noisy, 39 flips, OOS24 -3pp) and slower 252d both worse. The lever is **CADENCE: weekly (5d) + ~40d min-dwell** → +1.05pp, flips 29→19, Sharpe up. **Monthly (21d) too coarse** (OOS24 -3.66pp, misses recent regime). Daily = whipsaw.

## FAILURES (don't retry)
- **E1 — DT-Kelly parking on LAGGED idle cash: FAILS** (BASE -0.15pp, KELLY -0.70pp, DD worse). Counterintuitive-but-sound: ensemble picks LAGGED leg precisely when concentration/index is WEAK (V12 mode); parking LAGGED idle cash INTO the index = buying the laggard. LAGGED's low-beta idle cash is a defensive FEATURE; parking removes it. Standalone LAGGED NAV jumps 319→407B with parking but it's the wrong beta at the wrong time inside the ensemble.
- **E4 — DT CRISIS override (switched leg→ETF/cash): ≈neutral.** CRISIS→ETF -0.94pp; CRISIS→CASH -0.03pp (flat) but best Sharpe 1.53. DT-CRISIS rarely fires modern 2014+. Not worth the complexity.
- **Any COMBO including E1: DD damage** (-24 to -25%). E3+E1KELLY+weekly = +1.25pp Full but DD -24.57%.

## Caveats / next
- **Backtest-research only** (user's scope). NOT wired into `pt_v121_ensemble.py` / scheduler.
- **Modern-era (2014+) only.** DT parking-channel inherits DT's pre-2014 V-recovery-lag risk (see [[v5-kelly-dt-smoothing]] — DT misses 2009). Don't deploy pre-2014.
- VNINDEX-proxy used for switched-ETF leg (harness consistency w/ crude baseline); real `pt_v121_ensemble.py` uses real E1VFVN30 — re-validate intensity on real ETF before any paper-trade arm.
- If promoting: create `pt_v121_ens_dt.py` A/B arm (DEC {3:0.85} + weekly) vs canonical, decide after live window — same pattern as the V12_DT4 A/B.
- Files: `research_dt_ens_phase1.py` (harness+E0 cadence/horizon), `_phase2.py` (E1-E4+combos), `_phase3.py` (intensity sweep + inert-SVT control). Data: `data/dt_ens_e0_sweep.csv`, `dt_ens_phase2_nav.csv`, `dt_ens_phase3_sweep.csv`, `dt_ens_legs.pkl`.

## Cross-refs
- [[papertrade-4sys-2026q2q3]] — V121_ENS spec being improved
- [[cross-architecture-synthesis]] — earlier "DT hurts ensemble" finding (was crude-swap on inflated baseline)
- [[v5-kelly-dt-smoothing]] — DT helps the Kelly/parking dial (same mechanism)
- [[vnindex-state-pure-index-metric-dt-optimal]] — DT optimal for index allocation
