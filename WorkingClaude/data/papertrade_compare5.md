# Paper-Trade Comparison — 5 Systems

*Generated: 2026-07-31 15:36*

*Window: 2026-04-01 → 2026-07-30 (120 calendar days)*

*Init NAV: 50B VND fresh, all-cash, no positions (each system)*


## Headline metrics

| System | Final NAV | Total Ret | CAGR | Vol (ann) | Sharpe | Max DD | Calmar |
|---|---|---|---|---|---|---|---|
| **V11 Song Sinh + KELLY + DT5G ⭐** | 51.183B | +2.52% | +7.87% | 17.48% | +0.52 | -11.57% | +0.68 |
| **V12 Âm Dương (BAL+LAGGED) + DT5G ⭐** | 49.040B | -1.87% | -5.58% | 7.47% | -0.73 | -6.44% | -0.87 |
| **V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01** | 48.134B | -3.68% | -20.72% | 9.34% | -2.31 | -6.64% | -3.12 |
| **V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐** | 48.381B | -3.24% | -21.76% | 13.71% | -1.66 | -9.73% | -2.24 |
| **VNINDEX Buy & Hold (rebased 50B)** | 51.225B | +2.45% | +7.65% | 18.03% | +0.50 | -13.46% | +0.57 |

## Delta vs V23 (production baseline)

| System | ΔRet | ΔDD | Verdict |
|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | +5.76pp | -1.83pp | Return better, DD worse |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | +1.37pp | +3.30pp | Both better |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -0.44pp | +3.10pp | DD better, return worse |
| VNINDEX Buy & Hold (rebased 50B) | +5.69pp | -3.72pp | Return better, DD worse |

## Grind lens — current drawdown & recent momentum

| System | Cur DD (from peak) | Underwater | Peak date | Trailing 1M | Trailing 3M |
|---|---|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | -8.0% | 77d | 2026-05-14 | -6.4% | -5.9% |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -5.3% | 84d | 2026-05-07 | -3.4% | -4.0% |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -4.0% | 29d | 2026-07-01 | -4.0% | — |
| V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐ | -7.0% | 29d | 2026-07-01 | -7.0% | — |
| VNINDEX Buy & Hold (rebased 50B) | -9.5% | 73d | 2026-05-18 | -6.6% | -5.9% |

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
| 2026-06-08 | 52.57B | 49.98B | 48.88B | — | 52.57B |
| 2026-06-15 | 52.75B | 49.78B | 48.99B | 50.17B | 52.83B |
| 2026-06-22 | 53.68B | 50.43B | 49.50B | 50.88B | 54.55B |
| 2026-06-29 | 54.33B | 50.63B | 49.96B | 51.68B | 54.46B |
| 2026-07-06 | 54.04B | 50.33B | 49.76B | 51.43B | 54.13B |
| 2026-07-13 | 52.86B | 49.86B | 49.07B | 50.31B | 52.87B |
| 2026-07-20 | 51.39B | 49.17B | 48.23B | 48.81B | 51.19B |
| 2026-07-27 | 49.21B | 48.47B | 46.83B | 46.95B | 49.00B |
| 2026-07-30 | 51.18B | 49.04B | 48.13B | 48.38B | 51.23B |

## Files

- `data/pt_v11_tq34b_logs.csv` — V11 Song Sinh + KELLY + DT5G ⭐
- `data/pt_v12_macro_logs.csv` — V12 Âm Dương (BAL+LAGGED) + DT5G ⭐
- `data/pt_v4_dt5g_logs.csv` — V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01
- `data/pt_v22_dt5g_logs.csv` — V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐
- `data/papertrade_compare5.csv` — daily NAV all systems
