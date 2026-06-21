# Phase E — Ablation + ALL-Variants Synthesis

## All measured variants (FULL / IS / OOS)

| Variant | Period | CAGR% | Sharpe | MaxDD% | Calmar | Final B |
|---|---|---|---|---|---|---|
| B   baseline V5 prod (12pos, Q2, HYBRID, SV_TIGHT, D1) | FULL | +18.34 | 1.27 | -21.98 | 0.83 | 401.7 |
| B   baseline V5 prod (12pos, Q2, HYBRID, SV_TIGHT, D1) | IS 14-21 | +23.12 | 1.57 | -21.98 | 1.05 | 263.7 |
| B   baseline V5 prod (12pos, Q2, HYBRID, SV_TIGHT, D1) | OOS 22-26 | +10.10 | 0.75 | -19.45 | 0.52 | 401.7 |
| C-D diversify (max_pos20, 5%/slot) | FULL | +18.22 | 1.38 | -18.62 | 0.98 | 396.7 |
| C-D diversify (max_pos20, 5%/slot) | IS 14-21 | +23.31 | 1.69 | -18.62 | 1.25 | 266.9 |
| C-D diversify (max_pos20, 5%/slot) | OOS 22-26 | +9.49 | 0.79 | -15.26 | 0.62 | 396.7 |
| C-S soft-stop -15% trim50% | FULL | +18.34 | 1.28 | -21.82 | 0.84 | 401.7 |
| C-S soft-stop -15% trim50% | IS 14-21 | +22.61 | 1.56 | -21.82 | 1.04 | 255.1 |
| C-S soft-stop -15% trim50% | OOS 22-26 | +10.95 | 0.80 | -18.69 | 0.59 | 401.7 |
| C-DS D+S combined | FULL | +17.88 | 1.36 | -18.30 | 0.98 | 382.8 |
| C-DS D+S combined | IS 14-21 | +22.56 | 1.65 | -18.30 | 1.23 | 254.3 |
| C-DS D+S combined | OOS 22-26 | +9.81 | 0.82 | -14.57 | 0.67 | 382.8 |
| D   V5 no Q2 ({3:0.7}) | FULL | +17.80 | 1.33 | -18.78 | 0.95 | 379.5 |
| D   V5 no Q2 ({3:0.7}) | IS 14-21 | +23.27 | 1.70 | -17.76 | 1.31 | 266.2 |
| D   V5 no Q2 ({3:0.7}) | OOS 22-26 | +8.45 | 0.68 | -18.78 | 0.45 | 379.5 |
| E1  max_pos 12→10 (no over-leverage) | FULL | +20.25 | 1.40 | -21.83 | 0.93 | 489.7 |
| E1  max_pos 12→10 (no over-leverage) | IS 14-21 | +25.91 | 1.74 | -21.83 | 1.19 | 315.5 |
| E1  max_pos 12→10 (no over-leverage) | OOS 22-26 | +10.58 | 0.78 | -18.94 | 0.56 | 489.7 |
| E2  no HYBRID entry | FULL | +18.25 | 1.27 | -21.98 | 0.83 | 398.0 |
| E2  no HYBRID entry | IS 14-21 | +23.12 | 1.57 | -21.98 | 1.05 | 263.7 |
| E2  no HYBRID entry | OOS 22-26 | +9.87 | 0.73 | -19.45 | 0.51 | 398.0 |
| E3  no SV_TIGHT filter | FULL | +17.28 | 1.20 | -24.61 | 0.70 | 359.4 |
| E3  no SV_TIGHT filter | IS 14-21 | +21.21 | 1.44 | -24.61 | 0.86 | 232.6 |
| E3  no SV_TIGHT filter | OOS 22-26 | +10.46 | 0.76 | -20.86 | 0.50 | 359.4 |
| E4  no D1 RE_BACKLOG | FULL | +19.68 | 1.35 | -21.03 | 0.94 | 461.6 |
| E4  no D1 RE_BACKLOG | IS 14-21 | +25.65 | 1.70 | -21.03 | 1.22 | 310.4 |
| E4  no D1 RE_BACKLOG | OOS 22-26 | +9.51 | 0.71 | -19.88 | 0.48 | 461.6 |

## OOS 2022-2026 leaderboard (ranked by Calmar)

| Rank | Variant | CAGR% | Sharpe | MaxDD% | Calmar |
|---|---|---|---|---|---|
| 1 | C-DS D+S combined | +9.81 | 0.82 | -14.57 | 0.67 |
| 2 | C-D diversify (max_pos20, 5%/slot) | +9.49 | 0.79 | -15.26 | 0.62 |
| 3 | C-S soft-stop -15% trim50% | +10.95 | 0.80 | -18.69 | 0.59 |
| 4 | E1  max_pos 12→10 (no over-leverage) | +10.58 | 0.78 | -18.94 | 0.56 |
| 5 | B   baseline V5 prod (12pos, Q2, HYBRID, SV_TIGHT, D1) | +10.10 | 0.75 | -19.45 | 0.52 |
| 6 | E2  no HYBRID entry | +9.87 | 0.73 | -19.45 | 0.51 |
| 7 | E3  no SV_TIGHT filter | +10.46 | 0.76 | -20.86 | 0.50 |
| 8 | E4  no D1 RE_BACKLOG | +9.51 | 0.71 | -19.88 | 0.48 |
| 9 | D   V5 no Q2 ({3:0.7}) | +8.45 | 0.68 | -18.78 | 0.45 |

## Hard winners (no estimates)

- **Max OOS Calmar**: C-DS D+S combined
  - Calmar 0.674 | CAGR +9.81% | DD -14.57% | Sharpe 0.82
- **Max OOS CAGR**: C-S soft-stop -15% trim50%
  - CAGR +10.95% | Calmar 0.586 | DD -18.69% | Sharpe 0.80
- **Best OOS MaxDD**: C-DS D+S combined
  - DD -14.57% | CAGR +9.81% | Calmar 0.674