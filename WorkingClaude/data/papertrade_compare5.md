# Paper-Trade Comparison — 5 Systems

*Generated: 2026-08-12 15:36*

*Window: 2026-04-01 → 2026-08-11 (132 calendar days)*

*Init NAV: 50B VND fresh, all-cash, no positions (each system)*


## Headline metrics

| System | Final NAV | Total Ret | CAGR | Vol (ann) | Sharpe | Max DD | Calmar |
|---|---|---|---|---|---|---|---|
| **V11 Song Sinh + KELLY + DT5G ⭐** | 51.936B | +4.03% | +11.55% | 17.17% | +0.72 | -11.57% | +1.00 |
| **V12 Âm Dương (BAL+LAGGED) + DT5G ⭐** | 49.295B | -1.36% | -3.71% | 7.28% | -0.48 | -6.44% | -0.58 |
| **V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01** | 48.333B | -3.28% | -15.78% | 9.36% | -1.72 | -6.64% | -2.38 |
| **V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐** | 49.524B | -0.95% | -5.57% | 13.78% | -0.34 | -9.77% | -0.57 |
| **VNINDEX Buy & Hold (rebased 50B)** | 52.069B | +4.14% | +11.88% | 17.53% | +0.73 | -13.46% | +0.88 |

## Delta vs V23 (production baseline)

| System | ΔRet | ΔDD | Verdict |
|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | +4.98pp | -1.80pp | Return better, DD worse |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -0.40pp | +3.33pp | DD better, return worse |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -2.33pp | +3.13pp | DD better, return worse |
| VNINDEX Buy & Hold (rebased 50B) | +5.09pp | -3.69pp | Return better, DD worse |

## Grind lens — current drawdown & recent momentum

| System | Cur DD (from peak) | Underwater | Peak date | Trailing 1M | Trailing 3M |
|---|---|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | -6.7% | 89d | 2026-05-14 | -1.7% | -6.7% |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -4.8% | 96d | 2026-05-07 | -1.1% | -4.6% |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -3.6% | 41d | 2026-07-01 | -1.5% | — |
| V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐ | -4.8% | 41d | 2026-07-01 | -1.5% | — |
| VNINDEX Buy & Hold (rebased 50B) | -8.0% | 85d | 2026-05-18 | -1.5% | -7.9% |

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
| 2026-06-15 | 52.75B | 49.78B | 48.99B | 50.16B | 52.83B |
| 2026-06-22 | 53.68B | 50.43B | 49.50B | 50.88B | 54.55B |
| 2026-06-29 | 54.33B | 50.63B | 49.96B | 51.66B | 54.46B |
| 2026-07-06 | 54.04B | 50.33B | 49.76B | 51.42B | 54.13B |
| 2026-07-13 | 52.86B | 49.86B | 49.07B | 50.30B | 52.87B |
| 2026-07-20 | 51.39B | 49.17B | 48.23B | 48.79B | 51.19B |
| 2026-07-27 | 49.21B | 48.47B | 46.83B | 46.92B | 49.00B |
| 2026-08-03 | 51.79B | 49.24B | 48.43B | 49.19B | 51.76B |
| 2026-08-10 | 51.92B | 49.29B | 48.39B | 49.73B | 52.17B |
| 2026-08-11 | 51.94B | 49.30B | 48.33B | 49.52B | 52.07B |

## Files

- `data/pt_v11_tq34b_logs.csv` — V11 Song Sinh + KELLY + DT5G ⭐
- `data/pt_v12_macro_logs.csv` — V12 Âm Dương (BAL+LAGGED) + DT5G ⭐
- `data/pt_v4_dt5g_logs.csv` — V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01
- `data/pt_v22_dt5g_logs.csv` — V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐
- `data/papertrade_compare5.csv` — daily NAV all systems
