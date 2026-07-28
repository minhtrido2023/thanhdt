# Paper-Trade Comparison — 5 Systems

*Generated: 2026-07-28 15:40*

*Window: 2026-04-01 → 2026-07-27 (117 calendar days)*

*Init NAV: 50B VND fresh, all-cash, no positions (each system)*


## Headline metrics

| System | Final NAV | Total Ret | CAGR | Vol (ann) | Sharpe | Max DD | Calmar |
|---|---|---|---|---|---|---|---|
| **V11 Song Sinh + KELLY + DT5G ⭐** | 49.172B | -1.51% | -4.64% | 17.23% | -0.19 | -11.63% | -0.40 |
| **V12 Âm Dương (BAL+LAGGED) + DT5G ⭐** | 48.633B | -2.68% | -8.14% | 7.34% | -1.13 | -6.11% | -1.33 |
| **V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01** | 46.827B | -6.30% | -34.57% | 8.34% | -4.87 | -6.64% | -5.21 |
| **V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐** | 46.952B | -6.10% | -39.31% | 12.58% | -3.87 | -9.73% | -4.04 |
| **VNINDEX Buy & Hold (rebased 50B)** | 49.004B | -1.99% | -6.09% | 17.66% | -0.27 | -13.46% | -0.45 |

## Delta vs V23 (production baseline)

| System | ΔRet | ΔDD | Verdict |
|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | +4.59pp | -1.90pp | Return better, DD worse |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | +3.41pp | +3.62pp | Both better |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -0.20pp | +3.10pp | DD better, return worse |
| VNINDEX Buy & Hold (rebased 50B) | +4.10pp | -3.72pp | Return better, DD worse |

## Grind lens — current drawdown & recent momentum

| System | Cur DD (from peak) | Underwater | Peak date | Trailing 1M | Trailing 3M |
|---|---|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | -11.6% | 74d | 2026-05-14 | -9.7% | -9.4% |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -6.1% | 81d | 2026-05-07 | -4.2% | -5.3% |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -6.6% | 26d | 2026-07-01 | -6.5% | — |
| V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐ | -9.7% | 26d | 2026-07-01 | -8.7% | — |
| VNINDEX Buy & Hold (rebased 50B) | -13.4% | 70d | 2026-05-18 | -10.8% | -9.9% |

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
| 2026-06-29 | 54.28B | 50.67B | 49.96B | 51.68B | 54.46B |
| 2026-07-06 | 53.99B | 50.37B | 49.76B | 51.43B | 54.13B |
| 2026-07-13 | 52.82B | 49.93B | 49.07B | 50.31B | 52.87B |
| 2026-07-20 | 51.36B | 49.57B | 48.23B | 48.81B | 51.19B |
| 2026-07-27 | 49.17B | 48.63B | 46.83B | 46.95B | 49.00B |

## Files

- `data/pt_v11_tq34b_logs.csv` — V11 Song Sinh + KELLY + DT5G ⭐
- `data/pt_v12_macro_logs.csv` — V12 Âm Dương (BAL+LAGGED) + DT5G ⭐
- `data/pt_v4_dt5g_logs.csv` — V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01
- `data/pt_v22_dt5g_logs.csv` — V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐
- `data/papertrade_compare5.csv` — daily NAV all systems
