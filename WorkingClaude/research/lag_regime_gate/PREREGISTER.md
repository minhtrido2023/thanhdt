# LAG regime-vs-quality gate — PRE-REGISTRATION
Job Taylor_20260723_131958 · 2026-07-23 · author Taylor (quant)

## Motivation
User hypothesis: recent LAG (PEAD) weakness is mostly REGIME-driven ("thị trường xấu →
surprise không có nhiều ý nghĩa, NĐT sợ giảm hơn sợ tăng"), not name-selection-driven.
Design a gate more subtle than a blanket rating≤3 filter.

## Data (all point-in-time, no look-ahead)
- Events: `data/earnings_events_classified.csv` (post_ret = T+5→T+30 hold return, NP_R).
- Surprise: `data/earnings_surprise_data.pkl` (NP_P0..P4 → surprise_B_MA vs 4Q mean).
- Rating: `data/rating_8l_history.pkl` (asof eff_time ≤ entry_dt → truly PIT).
- Regime: `deploy_golive_dt5g_v4/dt5g_daily_reference.csv` (dt5g_state, dt4_state per date);
  `data/_cache_vnindex_2000_now.pkl` (VNINDEX Close/MA200/RSI → drawdown, 6M ret, vs-MA200).
- LAG engine: standalone ledger sim (from `analyze_2025_lagged_weakness.py`, canonical LAG
  spec: NP_R≥15 ∧ prior_n_good≥4 ∧ pa_HL3≥5, entry T+5, hold 25d, MAX_POS 12, POS 8%,
  liq cap 20%ADV×5, LIQ_MIN 2e9). Same engine for ALL variants → clean relative comparison.

## Regime attribution: regime measured AT ENTRY date (T+5), never after. DT5G reference only
covers to 2026-06-02, which spans every event that has a valid (25d-forward) post_ret.

## Questions
Q1 Decompose LAG-only equity curve 2014-2026; locate the decline period (quarter-level),
   rolling 1y Sharpe / hit-rate / avg-trade vs history.
Q2 IC(surprise, post_ret) and IC(NP_R, post_ret) split by regime bucket, with t-stats.
   Decide: does surprise IC go to ~0 / negative in bad regimes (signal dies) vs stay
   positive but smaller magnitude (risk-off dominates)?
Q3 NAV backtest of 4 variants (same engine):
   (a) BASELINE (no extra gate)
   (b) NAME-QUALITY gate: rating≤3
   (c) REGIME-CONDITIONAL: half-size / skip entry in bad regime (best proxy from Q2)
   (d) COMBO (b)+(c) — only if both pass individually.
   Metrics: CAGR/Sharpe/MaxDD/Calmar; walk-forward IS(2014-19)/OOS(2020+); LOO-by-year.
Q4 Recent-decline diagnosis: rating-fail %, surprise-inflation, regime mix of entries in
   the decline window; attribute the decline to quality vs regime with numbers.

## N_trials declared: ~10
  Regime proxies tried: {DT5G 5-state, VNI drawdown-from-peak, VNI 6M return, VNI vs MA200} (4)
  × gate forms {skip-bad, half-size-bad} (2)  + rating gate (1) + combo (1) + baseline (1).
  Report best-of honestly as multiple-testing-inflated; require OOS + LOO robustness.

## GO / NO-GO (a variant is "wire-worthy candidate" only if ALL hold)
1. OOS(2020+) Calmar ≥ baseline OOS Calmar AND OOS Sharpe ≥ baseline (not IS-only).
2. LOO-by-year: removing any single year keeps the full-period edge sign positive
   (edge not carried by 1-2 years).
3. DSR ≥ 0.95 on the chosen config's daily NAV.
4. quant-skeptic CONFIRMED before any production proposal.
Failing 1-3 → report as NO-GO / insurance-only, do NOT propose wiring.
This job proposes only; wires nothing. TRC stays HOLD regardless.
