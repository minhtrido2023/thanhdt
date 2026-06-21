# Phase D — Isolating Q2 overlay + production-complexity effects

## Setup

- **A** (this run): V5 stack with `cash_etf_states={3:0.7}` = V4 V121_ENS production config
- **B** (Phase B baseline): V5 stack with `cash_etf_states={3:1.0}` = V5 V121_ENS+Q2 production
- **C** (reference): `test_rolling_m3_v121_ensemble.py` log — bare V121_ENS validation:
  - max_pos=10 (not 12 → no 20% borrow); slippage=0.001 (vs 0.0); no SV_TIGHT/P3/D1; no HYBRID; default tier_weights

## FULL period (2014-01-02 → 2026-05-19, 12.4y, init 50B)

| Variant | CAGR% | Sharpe | MaxDD% | Calmar | Final B | Wealth x |
|---|---|---|---|---|---|---|
| C: test_rolling_m3 bare V121_ENS (simpler config) | +24.32 | 1.74 | -15.32 | 1.59 | — | 14.75x |
| A: V5 stack, {3:0.7} (no Q2) | +17.80 | 1.33 | -18.78 | 0.95 | 379.5 | 7.59x |
| B: V5 stack, {3:1.0} (Q2 ON, prod) | +18.34 | 1.27 | -21.98 | 0.83 | 401.7 | 8.03x |

## IS/OOS split

| Variant | CAGR% | Sharpe | MaxDD% | Calmar |
|---|---|---|---|---|
| A IS | +23.27 | 1.70 | -17.76 | 1.31 |
| B IS | +23.12 | 1.57 | -21.98 | 1.05 |
| C OOS 2024-26 (from test_rolling log) | +31.74 | 1.81 | -10.88 | 2.92 |
| A OOS | +8.45 | 0.68 | -18.78 | 0.45 |
| B OOS | +10.10 | 0.75 | -19.45 | 0.52 |

## Isolated effect estimates

- **Q2 overlay** (B − A): FULL +0.54pp / OOS +1.65pp CAGR
- **Production complexity** (A − C ref): FULL -6.52pp (includes leverage 120%, SV_TIGHT/P3/D1 filters, HYBRID entry)
- **Total V5 prod vs bare validation** (B − C): -5.98pp

## Year-by-year Q2 effect

| Year | A (no Q2) % | B (Q2 ON) % | dQ2 |
|---|---|---|---|
| 2014 | +3.39 | +3.39 | +0.00 |
| 2015 | +9.45 | +9.45 | +0.00 |
| 2016 | +10.22 | +9.92 | -0.31 |
| 2017 | +48.87 | +53.44 | +4.57 |
| 2018 | +4.45 | +5.61 | +1.17 |
| 2019 | -1.95 | -2.26 | -0.31 |
| 2020 | +59.30 | +62.60 | +3.30 |
| 2021 | +64.37 | +53.95 | -10.43 |
| 2022 | -4.23 | -2.91 | +1.32 |
| 2023 | -6.33 | -6.74 | -0.41 |
| 2024 | +9.99 | +11.19 | +1.20 |
| 2025 | +55.74 | +60.61 | +4.87 |
| 2026 | -7.68 | -6.33 | +1.36 |