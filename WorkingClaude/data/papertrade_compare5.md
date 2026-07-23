# Paper-Trade Comparison — 5 Systems

*Generated: 2026-07-23 15:36*

*Window: 2026-04-01 → 2026-07-22 (112 calendar days)*

*Init NAV: 50B VND fresh, all-cash, no positions (each system)*


## Headline metrics

| System | Final NAV | Total Ret | CAGR | Vol (ann) | Sharpe | Max DD | Calmar |
|---|---|---|---|---|---|---|---|
| **V11 Song Sinh + KELLY + DT5G ⭐** | 48.731B | -2.39% | -7.59% | 18.21% | -0.35 | -12.43% | -0.61 |
| **V12 Âm Dương (BAL+LAGGED) + DT5G ⭐** | 48.220B | -3.51% | -11.00% | 8.50% | -1.33 | -6.91% | -1.59 |
| **V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01** | 47.175B | -5.60% | -33.82% | 8.42% | -4.62 | -5.94% | -5.69 |
| **V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐** | 47.506B | -4.99% | -36.61% | 13.67% | -3.18 | -8.66% | -4.23 |
| **VNINDEX Buy & Hold (rebased 50B)** | 48.990B | -2.02% | -6.44% | 17.54% | -0.29 | -13.46% | -0.48 |

## Delta vs V23 (production baseline)

| System | ΔRet | ΔDD | Verdict |
|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | +2.60pp | -3.76pp | Return better, DD worse |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | +1.48pp | +1.75pp | Both better |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -0.61pp | +2.72pp | DD better, return worse |
| VNINDEX Buy & Hold (rebased 50B) | +2.97pp | -4.79pp | Return better, DD worse |

## Grind lens — current drawdown & recent momentum

| System | Cur DD (from peak) | Underwater | Peak date | Trailing 1M | Trailing 3M |
|---|---|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | -12.4% | 69d | 2026-05-14 | -9.3% | -9.3% |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -6.9% | 76d | 2026-05-07 | -4.3% | -5.9% |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -5.9% | 21d | 2026-07-01 | -4.9% | — |
| V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐ | -8.7% | 21d | 2026-07-01 | -7.4% | — |
| VNINDEX Buy & Hold (rebased 50B) | -13.5% | 65d | 2026-05-18 | -10.7% | -9.0% |

*Grind = sustained underwater stretch where the book bleeds while the index holds/rises (style-divergence). V2.3's known weak spot is the 2025-08→ style-divergence grind (momentum lags the VIC-led megacap index); watch V2.3 trailing-3M vs VNINDEX.*

## Weekly NAV snapshot (every ~5 trading days)

| Date | V11 Song Sinh + KELLY + DT5G ⭐ | V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐ | VNINDEX Buy & Hold (rebased 50B) |
|---|---|---|---|---|---|
| 2026-04-01 | 49.92B | 49.97B | — | — | 50.00B |
| 2026-04-08 | 53.02B | 51.09B | — | — | 51.57B |
| 2026-04-15 | 52.54B | 50.97B | — | — | 52.87B |
| 2026-04-22 | 53.84B | 51.33B | — | — | 54.53B |
| 2026-05-04 | 54.36B | 51.07B | — | — | 54.44B |
| 2026-05-11 | 54.98B | 51.17B | — | — | 55.65B |
| 2026-05-18 | 55.16B | 51.60B | — | — | 56.61B |
| 2026-05-25 | 54.34B | 50.78B | — | — | 55.38B |
| 2026-06-01 | 53.74B | 51.18B | 49.97B | — | 54.16B |
| 2026-06-08 | 52.56B | 49.98B | 48.88B | — | 52.57B |
| 2026-06-15 | 52.73B | 49.80B | 48.99B | 50.17B | 52.83B |
| 2026-06-22 | 53.65B | 50.44B | 49.50B | 50.88B | 54.55B |
| 2026-06-29 | 54.28B | 50.65B | 49.96B | 51.68B | 54.46B |
| 2026-07-06 | 53.42B | 49.98B | 49.76B | 51.43B | 54.13B |
| 2026-07-13 | 52.29B | 49.48B | 49.07B | 50.31B | 52.87B |
| 2026-07-20 | 50.54B | 48.80B | 48.23B | 48.80B | 51.19B |
| 2026-07-22 | 48.73B | 48.22B | 47.17B | 47.51B | 48.99B |

## Files

- `data/pt_v11_tq34b_logs.csv` — V11 Song Sinh + KELLY + DT5G ⭐
- `data/pt_v12_macro_logs.csv` — V12 Âm Dương (BAL+LAGGED) + DT5G ⭐
- `data/pt_v4_dt5g_logs.csv` — V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01
- `data/pt_v22_dt5g_logs.csv` — V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐
- `data/papertrade_compare5.csv` — daily NAV all systems
