# Kelly Q2_ONLY effect on V11 vs V12.1 architectures (TRUE prod ETF)

**Date**: 2026-05-23
**Period**: 2014-01-01 -> 2026-05-15 | NAV 50B (25B/25B split)
**State source**: TQ v3.4b (`vnindex_5state_tam_quan_v3_4b_full_history.csv`)
**BASELINE ETF**: `{3: 0.7}` (current production)
**Q2_ONLY ETF**: `{3: 1.0}` (proposed)

## Note on V121_ENS

V121_ENS in production switches VN30 <-> LAGGED based on M1+M3r AND-HOLD signal.
This script doesn't ensemble; instead it bounds Q2 effect:
- **Max Q2 impact**: V11 architecture (BAL+VN30 — both have ETF overlay)
- **Min Q2 impact**: V12.1 architecture (BAL+LAGGED — only BAL has ETF)
Ensemble Q2 effect lies between, weighted by signal occupancy.

## Results per window

| Period | Arm | CAGR | Sharpe | MaxDD | Calmar | Wealth |
|---|---|---:|---:|---:|---:|---:|
| FULL 2014-2026 | V11 base | +19.89% | +1.35 | -17.68% | +1.12 | 9.42x |
| FULL 2014-2026 | V11 Q2 | +22.21% | +1.37 | -25.91% | +0.86 | 11.94x |
| FULL 2014-2026 | V12.1 base | +14.52% | +1.18 | -17.17% | +0.85 | 5.35x |
| FULL 2014-2026 | V12.1 Q2 | +16.71% | +1.26 | -18.71% | +0.89 | 6.76x |
| Pre-OOS 2014-19 | V11 base | +13.37% | +1.32 | -17.68% | +0.76 | 2.12x |
| Pre-OOS 2014-19 | V11 Q2 | +14.27% | +1.16 | -25.91% | +0.55 | 2.22x |
| Pre-OOS 2014-19 | V12.1 base | +8.67% | +1.32 | -9.37% | +0.93 | 1.65x |
| Pre-OOS 2014-19 | V12.1 Q2 | +8.99% | +1.17 | -14.23% | +0.63 | 1.68x |
| OOS 2024-2026 | V11 base | +26.53% | +1.42 | -17.24% | +1.54 | 1.74x |
| OOS 2024-2026 | V11 Q2 | +32.61% | +1.60 | -18.39% | +1.77 | 1.95x |
| OOS 2024-2026 | V12.1 base | +23.42% | +1.32 | -17.17% | +1.36 | 1.65x |
| OOS 2024-2026 | V12.1 Q2 | +29.82% | +1.53 | -18.71% | +1.59 | 1.85x |
| Y2022 CRISIS | V11 base | +0.61% | +0.34 | -1.00% | +0.61 | 1.01x |
| Y2022 CRISIS | V11 Q2 | -0.34% | -0.11 | -3.21% | -0.11 | 1.00x |
| Y2022 CRISIS | V12.1 base | +1.06% | +0.72 | -0.87% | +1.22 | 1.01x |
| Y2022 CRISIS | V12.1 Q2 | -0.87% | -0.27 | -4.71% | -0.18 | 0.99x |
| Y2024 | V11 base | +10.16% | +0.86 | -11.58% | +0.88 | 1.10x |
| Y2024 | V11 Q2 | +12.99% | +1.04 | -10.49% | +1.24 | 1.13x |
| Y2024 | V12.1 base | +14.40% | +1.10 | -11.86% | +1.21 | 1.14x |
| Y2024 | V12.1 Q2 | +19.23% | +1.39 | -10.24% | +1.88 | 1.19x |
| Y2025 | V11 base | +62.44% | +2.40 | -15.91% | +3.93 | 1.62x |
| Y2025 | V11 Q2 | +68.28% | +2.43 | -17.21% | +3.97 | 1.68x |
| Y2025 | V12.1 base | +42.92% | +1.90 | -15.76% | +2.72 | 1.43x |
| Y2025 | V12.1 Q2 | +47.15% | +1.94 | -17.24% | +2.73 | 1.47x |

## Q2 deltas per architecture per window

| Period | Arch | dCAGR | dSharpe | dMaxDD |
|---|---|---:|---:|---:|
| FULL 2014-2026 | V11 | +2.33pp | +0.02 | -8.23pp |
| FULL 2014-2026 | V12.1 | +2.19pp | +0.08 | -1.54pp |
| Pre-OOS 2014-19 | V11 | +0.90pp | -0.16 | -8.23pp |
| Pre-OOS 2014-19 | V12.1 | +0.32pp | -0.15 | -4.86pp |
| OOS 2024-2026 | V11 | +6.08pp | +0.18 | -1.15pp |
| OOS 2024-2026 | V12.1 | +6.40pp | +0.22 | -1.54pp |
| Y2022 CRISIS | V11 | -0.95pp | -0.45 | -2.20pp |
| Y2022 CRISIS | V12.1 | -1.93pp | -1.00 | -3.84pp |
| Y2024 | V11 | +2.83pp | +0.18 | +1.09pp |
| Y2024 | V12.1 | +4.83pp | +0.29 | +1.62pp |
| Y2025 | V11 | +5.84pp | +0.03 | -1.30pp |
| Y2025 | V12.1 | +4.23pp | +0.04 | -1.49pp |