# Adaptive persistence gate for DT 4-gate — R&D verdict: **NO-GO**

**Job** Taylor_20260723_054325 · **Date** 2026-07-23 · **Author** Taylor (quant)
**Files** `research/adaptive_gate_20260723/` (state_analysis.py, enc_analysis.py, run_ab.py,
final_summary.py, base_state.csv, vnindex.csv, nav_*.csv, out_*.log)

## The proposal (user)
Instead of a FIXED dwell to commit a DT-4gate state transition (production: `default=10`
sessions for NEUTRAL↔BEAR↔BULL, `enC/enX=25` into CRISIS/EX-BULL), use the **strength of
evidence** (price continuing to fall) to SHORTEN the confirmation window — e.g. if VNINDEX
falls ~3 consecutive sessions, commit NEUTRAL→BEAR after ~3 sessions instead of 10.

Sound intuition in the abstract. But the KB flags these params as a *robust plateau — do
not tune to history*, so this was tested with full multiple-testing discipline, NOT one
backtest.

## Pre-registration (declared on bus BEFORE any run)
Adaptive rule = shorten dwell for **de-risk moves only** (`ps < committed`; 1=CRISIS..5=EXBULL,
lower=more defensive) when `consecutive_down_closes(VNINDEX) >= K2` AND base persisted `>= K1`:
`need = min(default, K1)`. Re-risk moves untouched (keep the "slow to euphoria" asymmetry).
**N_trials = 10**: Family-1 (default-branch) K1∈{3,5}×K2∈{2,3,4,5} = 8; Family-2 (also shorten
enC into-CRISIS, K1c∈{10,15}) = 2. Primary = K1=3,K2=3. Baseline = production fixed dwell.
Metrics: (a) whipsaw/revert, (b) lead-time in real crashes + false de-risk in calm windows,
(c) performance via `run_5systems_prodspec STATE_OVERRIDE=dt5g` (the same ablation harness that
validated DT5G itself; macro cap is base-independent so `adaptiveDT5G = min(adaptiveDT4, cap)`
is faithful), (d) DSR/PBO if a winner is selected.

## Result: NO-GO on every criterion

### 1. Zero lead in EVERY real crash (metric b)
Real ≥15% VNINDEX drawdowns 2014-03, 2018-04, 2022-01, 2025, 2026 — adaptive reaches the
defensive state on the **exact same session** as fixed default=10 (lead = +0 everywhere).
**Why:** real VN crashes go NEUTRAL→**raw-CRISIS** (governed by `enC=25`), *not* NEUTRAL→raw-BEAR
(`default=10`, the path the user's example targets). And even the Family-2 enC-shortcut buys 0
lead: VN crashes fall in **choppy steps**, so a clean "3 consecutive down-closes" streak does
not align with the early-crisis window — by the time it fires, the 25-session gate is already
nearly satisfied (2018: all variants commit CRISIS on 2018-05-09; 2022: all on 2022-01-04).

### 2. The evidence proxy is REDUNDANT, not independent (the mechanistic root cause)
The v3.4b base state is itself **price-derived and very noisy**: it sits in raw-CRISIS on
**713/3130 days (22.8%)**, and **77% of raw-CRISIS onsets are FALSE** (17/22 onsets — no ≥8%
drop within 40d).
The fixed dwell (`enC=25`/`default=10`) is a **noise filter calibrated to exactly this noise
level**. "Price fell 3 days" is a *laggy echo* of the same price action that already drove the
base bearish — as confirming evidence it adds ≈no information, it only lets more of the 77%-false
signal commit early. **This is the real reason `default=10` is a robust plateau, not an accident.**

### 3. More churn, WORSE drawdown (metric a) — opposite of the goal
Adaptive adds +7 (primary) to +17 (K2=2) transitions and lifts false-panic commits (2→3).
MaxDD gets **worse** in most systems (V1 −19.8→−22.5%, V2 −13.9→−16.3%) because premature
de-risks whipsaw: de-risk → market bounces → re-risk higher → falls again = worse positioned.

### 4. Performance uniformly NEGATIVE (metric c) — full history 2014→2026-05, 50B, V4/V5 = prod
| config | DT5G days Δ | V4 CAGR | V5 CAGR | V4 ΔCAGR | V5 ΔCAGR | V5 MaxDD |
|---|---|---|---|---|---|---|
| **BASE (prod DT5G)** | — | 23.82% | 25.42% | — | — | −18.48% |
| primary K1=3,K2=3 | 144 | 22.58% | 24.45% | **−1.24** | **−0.97** | −18.77% |
| aggressive K2=2 | 249 | 22.52% | 24.15% | **−1.30** | **−1.27** | −18.36% |
| F2 enC-adaptive K1c=10 | 220 | 22.73% | 24.48% | **−1.09** | **−0.94** | −18.87% |

Every tested config (mild primary, aggressive, and the crisis-lead variant — spanning the
family) is negative on every affected system; Sharpe ≤ baseline; excess daily return
t = −0.85..−0.99. V3 (LIVE-table control) unchanged = override correctly isolated.

### 5. Refuted by the user's OWN motivating episode (per-year V5, base vs primary)
Drag concentrates in **2018 −3.32pp, 2024 −1.63pp, and 2026 YTD −7.33pp**. **2026 — the current
fall that motivated the idea — is where adaptive does the MOST damage** (−7.33pp): it de-risked
prematurely and got whipsawed. The single year it helped (2025 +3.29pp) is exactly the
reshuffle-luck the LOO discipline flags; net-of-years = a loss (4 win / 4 lose years, negative sum).

### 6. DSR/PBO — not reached
No config produced positive excess Sharpe over the incumbent (best-of-family excess Sharpe < 0),
so there is nothing to deflate. The multiple-testing gate is moot because the family's best
already loses to baseline. No quant-skeptic promotion needed — nothing to promote.

## Verdict
**Do NOT wire.** Production DT 4-gate params unchanged. DT5G production NOT modified in this job.
The fixed dwell is a calibrated noise filter against a noisy price-derived base; shortcutting it
on a price-based (hence redundant) evidence proxy strictly admits more noise, buys no crash lead,
and costs ~1pp CAGR with worse drawdown — most acutely in the very episode (2026) that motivated it.

## Honest caveat — what WOULD be needed
The user's underlying intuition ("strong *independent* evidence justifies faster commitment") is
sound in general; it fails HERE because VNINDEX down-closes are not independent of the base
signal. A future attempt would need a genuinely **orthogonal, faster-than-price** stress signal
(breadth collapse, credit/liquidity stress, intraday volume-spike that LEADS price) — a separate,
larger research program with its own overfitting risk and no current evidence it clears the bar.
