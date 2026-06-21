# Kelly Q2 — HEUR_N100 vs BASELINE Shadow Backtest Results

**Date**: 2026-05-21
**Stack**: BA v11 full (SV_TIGHT + P3 + D1 RE_BACKLOG_BUY + 50/50 BAL+VN30 + V6 ETF)
**Period**: 2014-01-02 → 2026-04-03
**Init NAV**: 50B (25B BAL + 25B VN30)
**Exec**: T+1 Open + Layer 3 v4 HYBRID intraday | slot12 (max_pos=12, 10% fixed)
**Costs**: TC=0.1% buy/sell, deposit=0%, borrow=0%, ETF friction=0.15%/side
**ETF underlying**: real E1VFVN30 from 2016-01-07; VNINDEX-proxy 2014-2015 (same in both arms)

## Variants compared

- **BASELINE** (current heuristic): `cash_etf_states = {1: 0.0, 2: 0.2, 3: 0.7, 4: 1.0, 5: 1.3}`
- **HEUR_N100** (proposed): `cash_etf_states = {1: 0.0, 2: 0.2, 3: 1.0, 4: 1.0, 5: 1.3}` — NEUTRAL goes 70% → 100%

## Verdict

### **GREEN** — ΔCAGR=+1.48pp ≥ +1.0pp AND ΔMaxDD=+1.13pp ≥ -3.0pp

Gate (per spec §1.5 / §4.1): OOS 2024-2026 ΔCAGR ≥ +1.0pp AND ΔMaxDD ≤ +3pp vs BASELINE.

## Results — all windows

| Period | Arm | CAGR | Sharpe | MaxDD | Calmar | DDdur | NAV (B) | Trades |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| **FULL 2014-2026** | BASELINE | +38.38% | +0.34 | -17.21% | +2.23 | 861 | +2669.05 | 4027 |
|        | HEUR_N100 | +45.60% | +0.32 | -22.25% | +2.05 | 973 | +4976.34 | 1112 |
|        | **Δ N100−B** | **+7.22pp** | **-0.01** | **-5.04pp** | **-0.18** | — | — | — |
| **Pre-OOS 2014-19** | BASELINE | +63.67% | +0.43 | -12.69% | +5.02 | 704 | +956.98 | 1578 |
|        | HEUR_N100 | +79.29% | +0.43 | -16.84% | +4.71 | 643 | +1651.45 | 319 |
|        | **Δ N100−B** | **+15.61pp** | **-0.00** | **-4.15pp** | **-0.31** | — | — | — |
| **OOS 2024-2026** | BASELINE | +21.49% | +1.59 | -12.67% | +1.70 | 175 | +2669.05 | 940 |
|        | HEUR_N100 | +22.97% | +1.49 | -11.54% | +1.99 | 167 | +4976.34 | 257 |
|        | **Δ N100−B** | **+1.48pp** | **-0.10** | **+1.13pp** | **+0.29** | — | — | — |
| **Y2022** | BASELINE | -13.42% | -1.71 | -13.61% | -0.99 | 354 | +1601.88 | 189 |
|        | HEUR_N100 | -15.17% | -1.40 | -15.25% | -0.99 | 359 | +2859.27 | 50 |
|        | **Δ N100−B** | **-1.75pp** | **+0.31** | **-1.64pp** | **-0.01** | — | — | — |
| **Y2024** | BASELINE | +11.74% | +1.76 | -3.83% | +3.06 | 175 | +1923.88 | 188 |
|        | HEUR_N100 | +15.42% | +1.74 | -5.73% | +2.69 | 167 | +3604.78 | 136 |
|        | **Δ N100−B** | **+3.67pp** | **-0.02** | **-1.90pp** | **-0.37** | — | — | — |
| **Y2025** | BASELINE | +51.23% | +2.62 | -10.02% | +5.11 | 75 | +2903.87 | 548 |
|        | HEUR_N100 | +50.32% | +2.33 | -10.44% | +4.82 | 97 | +5409.79 | 101 |
|        | **Δ N100−B** | **-0.91pp** | **-0.30** | **-0.42pp** | **-0.29** | — | — | — |
| **Y2026 partial** | BASELINE | -28.29% | -2.08 | -10.98% | -2.58 | 73 | +2669.05 | 204 |
|        | HEUR_N100 | -28.56% | -1.82 | -11.54% | -2.47 | 73 | +4976.34 | 20 |
|        | **Δ N100−B** | **-0.27pp** | **+0.26** | **-0.56pp** | **+0.10** | — | — | — |

## Per-year breakdown

(see same table above for Y2022/Y2024/Y2025/Y2026)


## Files

- `kelly_q2_out/baseline_logs.csv` / `_transactions.csv` / `_open_positions.csv`
- `kelly_q2_out/heur_n100_logs.csv` / `_transactions.csv` / `_open_positions.csv`

## Notes

- Both arms run with identical signal stream, intraday alt-fill, sector caps,
  liquidity gates, and ETF underlying — only the `cash_etf_states` dict differs.
- Real E1VFVN30 prices used 2016-01-07 → end. Pre-2016 the ETF leg uses VNINDEX
  proxy (identical effect on both arms, cancels in the diff).
- 50/50 BAL + VN30 NAVs summed; per-book breakdown in the logs CSVs.
- DDdur = longest underwater stretch in calendar days inside the window.
- Verdict gate applied to OOS 2024-2026 window per spec §1.5 / §4.1.