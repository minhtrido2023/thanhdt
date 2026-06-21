# DT5G Macro Overlay — Event-Level Audit

*Period 2014-01-01 → 2026-05-15 | 3082 sessions. Macro state differs from DT4 on **49 sessions (1.6%)** across **4 distinct episodes** (4 de-risk, 0 re-risk).*

> Sparsity is the headline: a macro overlay validated on a handful of episodes cannot be confirmed by aggregate CAGR or even by a single IS/OOS split — each side of the split may contain only 1-3 events. Read the per-episode forward returns below.

## A. Episode ledger

**EpRet% = VNINDEX return DURING the differ-window** (the only stretch DT5G actually deviates from DT4) — this is the overlay's marginal cost/benefit. T+20/T+60 are from episode START and are REFERENCE ONLY: once the base state_dt4 catches up (CRISIS exit ≈10 sessions), both systems agree, so those horizons mix in BASE-machine behavior, NOT the overlay's effect. Read EpRet, not T+60.

| Start | End | Type | Dur | DT4→DT5G | Driver | InBull | **EpRet%** | T+20%(ref) | T+60%(ref) |
|---|---|---|---|---|---|---|---|---|---|
| 2020-03-16 | 2020-04-03 | DE-RISK | 14 | BEAR→CRISIS | US | no | **-6.2** | +2.6 | +16.0 |
| 2020-05-26 | 2020-05-26 | DE-RISK | 1 | NEUTRAL→CRISIS | US | no | **+0.0** | -0.1 | -2.6 |
| 2023-02-07 | 2023-03-16 | DE-RISK | 28 | NEUTRAL→BEAR | US+SBV | no | **-1.7** | -2.6 | -2.4 |
| 2023-04-04 | 2023-04-11 | DE-RISK | 6 | NEUTRAL→BEAR | SBV | no | **-0.8** | -3.5 | +3.9 |

## B. Does DE-RISK precede weakness? (correctness test — use EpRet, the differ-window)

- De-risk episodes: **4**

- **Mean VNINDEX return DURING the de-risk differ-window: -2.18%** (median -1.28%; 100% of episodes ≤0). Negative = overlay correctly held cash through a falling tape. This is the metric that judges the overlay.
- (Reference only) Mean T+60 from start: +3.71% — do NOT read as overlay cost: after CRISIS exit (~10 sessions) the base state_dt4 governs, so this horizon reflects the BASE machine's recovery lag, which is identical for DT4 and DT5G.
- **Bull-failure check**: de-risk episodes that fired inside a confirmed bull = **0** ✅ (bull-bypass held).

## C. Does RE-RISK (easing floor) precede strength?

- No re-risk episodes.

## D. Driver concentration

| Driver | #episodes | mean dur | mean T+60% |
|---|---|---|---|
| SBV | 1 | 6 | +3.87 |
| US | 2 | 8 | +6.68 |
| US+SBV | 1 | 28 | -2.40 |

## E. Verdict on overfit / walk-forward

- **Effective sample size = 4 episodes** (4 de-risk). This is the number that governs overfit risk — NOT the ~3000 sessions.
- A standard IS(2014-19)/OOS(2020-now) split divides these few episodes; if either side has <3 episodes, that split is statistically near-meaningless on its own and must be read alongside this per-episode ledger.
---

## F. Integrated V4/V5 prod-spec ablation (DT4 vs DT5G) — 2014→2026-05, 50B

Harness: run_5systems_prodspec.py with STATE_OVERRIDE={dt4,dt5g} (swaps the TQ34b
state for macro_state_live state_dt4 / state; all other prod-spec machinery identical).
V3 (LIVE state, NOT overridden) = identical in both runs → harness-integrity control.

| System | DT4 CAGR | DT5G CAGR | Δ Full | Δ IS 2014-19 | Δ OOS 2020-now |
|---|---|---|---|---|---|
| V4 (V121_ENS) | 20.18% | 20.45% | +0.27pp | **+0.00pp** | +0.54pp |
| V5 (Kelly)    | 23.23% | 23.67% | +0.43pp | **+0.00pp** | +0.88pp |
| V3 (LIVE ctrl)| 18.53% | 18.53% | +0.00   | +0.00        | +0.00          |

### Per-year delta = leave-one-EVENT-out (V5)
2014-19: 0.00 every year (IS empty). 2020 +0.37 (COVID). 2021 −0.20. 2022 0.00.
**2023 +5.00 (entire edge).** 2024 −0.17. **2025 −0.89 (overlay HURTS in bull).** 2026 +0.03.

→ Drop 2023 alone ⇒ sum of remaining deltas ≈ −0.86pp ⇒ DT5G ≤ DT4. The net positive
edge rests on ONE macro episode (2023 tightening). Easing arm never fired in 12y.

## G. FINAL VERDICT
1. Walk-forward IS/OOS is the WRONG tool: IS Δ = exactly 0.00pp (overlay dormant
   in-sample). OOS "outperformance" is a tautology, not robustness evidence.
2. Risk = event-sparsity (n=4 episodes, n=1 substantive), NOT parameter overfit
   (params are a robust plateau; all de-risks landed on real weakness; bull-bypass held).
3. Deploy DT5G as a FAIL-SAFE RISK GATE (as get_gated_state already does), not a
   return-enhancer. Forward edge ≈ 0 in normal/bull years (−0.89pp in 2025 bull),
   positive only when genuine macro stress recurs (2023-style). Insurance, not alpha.
4. macro_state_live.py docstring "+0.88/+0.63pp full" is overstated; prod-spec truth
   is +0.43 (V5) / +0.27 (V4) full. Correct it.
