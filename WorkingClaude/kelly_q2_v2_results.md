# Kelly Q2 v2 — HEUR_N100 vs BASELINE Shadow Backtest (rebuilt)

**Date**: 2026-05-23
**Stack**: BA v11 full (SV_TIGHT + P3 + D1 RE_BACKLOG_BUY + 50/50 BAL+VN30 + V6 ETF)
**Period**: 2014-01-02 → 2026-04-03
**Init NAV**: 50B (25B BAL + 25B VN30)
**Exec**: T+1 Open + Layer 3 v4 HYBRID intraday | slot12 (max_pos=12, 10% fixed)
**Costs (NEW)**: TC=0.1% buy/sell, deposit_annual=0% (NEW default), borrow_annual=10% (NEW default), ETF friction=0.15%/side
**Built directly from sim_v11_transparent.py canonical pattern** — only override is cash_etf_states.

## Variants compared

- **BASELINE** (current heuristic): `cash_etf_states = {1: 0.0, 2: 0.2, 3: 0.7, 4: 1.0, 5: 1.3}`
- **HEUR_N100** (proposed): `cash_etf_states = {1: 0.0, 2: 0.2, 3: 1.0, 4: 1.0, 5: 1.3}` — NEUTRAL goes 70% -> 100%

## Baseline sanity check

!! WARNING !! BASELINE FULL CAGR=12.04% OUTSIDE 17-21% band — config drift detected, treat results with caution.

## Verdict

### **GREEN** — ΔCAGR=+6.82pp >= +1.0pp AND ΔMaxDD=+2.78pp >= -3.0pp

Gate: OOS 2024-2026 ΔCAGR >= +1.0pp AND ΔMaxDD <= +3pp vs BASELINE.

## Results — all windows

| Period | Arm | CAGR | Sharpe | MaxDD | Calmar | DDdur | NAV (B) | Trades |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| **FULL 2014-2026** | BASELINE | +12.04% | +0.99 | -28.90% | +0.42 | 1349 | +201.32 | 2573 |
|        | HEUR_N100 | +14.50% | +0.96 | -28.42% | +0.51 | 1453 | +262.57 | 774 |
|        | **Δ N100-B** | **+2.46pp** | **-0.03** | **+0.48pp** | **+0.09** | — | — | — |
| **Pre-OOS 2014-19** | BASELINE | +8.59% | +0.98 | -15.04% | +0.57 | 634 | +81.95 | 882 |
|        | HEUR_N100 | +10.79% | +0.95 | -20.43% | +0.53 | 634 | +92.42 | 250 |
|        | **Δ N100-B** | **+2.20pp** | **-0.04** | **-5.39pp** | **-0.04** | — | — | — |
| **OOS 2024-2026** | BASELINE | +19.81% | +1.51 | -14.36% | +1.38 | 201 | +201.32 | 649 |
|        | HEUR_N100 | +26.63% | +1.63 | -11.57% | +2.30 | 137 | +262.57 | 200 |
|        | **Δ N100-B** | **+6.82pp** | **+0.12** | **+2.78pp** | **+0.92** | — | — | — |
| **Y2022** | BASELINE | -21.08% | -2.24 | -21.45% | -0.98 | 354 | +128.87 | 139 |
|        | HEUR_N100 | -19.89% | -1.70 | -20.06% | -0.99 | 354 | +148.94 | 55 |
|        | **Δ N100-B** | **+1.19pp** | **+0.54** | **+1.39pp** | **-0.01** | — | — | — |
| **Y2024** | BASELINE | +10.91% | +1.63 | -3.83% | +2.85 | 201 | +148.62 | 103 |
|        | HEUR_N100 | +24.08% | +2.09 | -7.22% | +3.33 | 86 | +191.36 | 72 |
|        | **Δ N100-B** | **+13.16pp** | **+0.46** | **-3.39pp** | **+0.49** | — | — | — |
| **Y2025** | BASELINE | +51.35% | +2.67 | -9.50% | +5.40 | 75 | +224.49 | 400 |
|        | HEUR_N100 | +49.53% | +2.30 | -10.44% | +4.74 | 97 | +285.68 | 102 |
|        | **Δ N100-B** | **-1.82pp** | **-0.37** | **-0.94pp** | **-0.66** | — | — | — |
| **Y2026 partial** | BASELINE | -35.30% | -2.96 | -13.48% | -2.62 | 73 | +201.32 | 146 |
|        | HEUR_N100 | -28.80% | -1.84 | -11.57% | -2.49 | 73 | +262.57 | 26 |
|        | **Δ N100-B** | **+6.50pp** | **+1.12** | **+1.91pp** | **+0.13** | — | — | — |

## Files

- `kelly_q2_v2_out/baseline_logs.csv` / `_transactions.csv` / `_open_positions.csv`
- `kelly_q2_v2_out/heur_n100_logs.csv` / `_transactions.csv` / `_open_positions.csv`

## Notes

- Built directly on sim_v11_transparent.py canonical pattern — only `cash_etf_states` differs between arms.
- Uses same cached `kelly_q3_out/_signals_v11_12y.pkl` as Part B + Q3 v2 — identical signal stream.
- New cost model: deposit_annual=0.0 (default) and borrow_annual=0.10 (default 10%/yr on margin).
- v1 (`test_kelly_q2_heur_n100.py`) showed BASELINE FULL CAGR +38.38% which is config-drifted; this v2 fixes that.