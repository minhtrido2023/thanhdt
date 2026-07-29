# Paper-Trade Comparison — 5 Systems

*Generated: 2026-07-29 15:40*

*Window: 2026-04-01 → 2026-07-28 (118 calendar days)*

*Init NAV: 50B VND fresh, all-cash, no positions (each system)*


## Headline metrics

| System | Final NAV | Total Ret | CAGR | Vol (ann) | Sharpe | Max DD | Calmar |
|---|---|---|---|---|---|---|---|
| **V11 Song Sinh + KELLY + DT5G ⭐** | 49.496B | -0.86% | -2.64% | 17.16% | -0.07 | -11.57% | -0.23 |
| **V12 Âm Dương (BAL+LAGGED) + DT5G ⭐** | 48.464B | -3.02% | -9.06% | 7.39% | -1.25 | -6.44% | -1.41 |
| **V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01** | 47.010B | -5.93% | -32.41% | 8.35% | -4.45 | -6.64% | -4.88 |
| **V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐** | 47.073B | -5.85% | -37.42% | 12.46% | -3.63 | -9.76% | -3.83 |
| **VNINDEX Buy & Hold (rebased 50B)** | 49.345B | -1.31% | -4.00% | 17.60% | -0.15 | -13.46% | -0.30 |

## Delta vs V23 (production baseline)

| System | ΔRet | ΔDD | Verdict |
|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | +4.99pp | -1.80pp | Return better, DD worse |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | +2.83pp | +3.32pp | Both better |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -0.08pp | +3.12pp | DD better, return worse |
| VNINDEX Buy & Hold (rebased 50B) | +4.54pp | -3.69pp | Return better, DD worse |

## Grind lens — current drawdown & recent momentum

| System | Cur DD (from peak) | Underwater | Peak date | Trailing 1M | Trailing 3M |
|---|---|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | -11.1% | 75d | 2026-05-14 | -8.9% | -8.8% |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -6.4% | 82d | 2026-05-07 | -4.3% | -5.0% |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -6.3% | 27d | 2026-07-01 | -5.9% | — |
| V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐ | -9.5% | 27d | 2026-07-01 | -8.9% | — |
| VNINDEX Buy & Hold (rebased 50B) | -12.8% | 71d | 2026-05-18 | -9.4% | -10.4% |

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
| 2026-07-27 | 49.21B | 48.47B | 46.83B | 46.94B | 49.00B |
| 2026-07-28 | 49.50B | 48.46B | 47.01B | 47.07B | 49.34B |

## Files

- `data/pt_v11_tq34b_logs.csv` — V11 Song Sinh + KELLY + DT5G ⭐
- `data/pt_v12_macro_logs.csv` — V12 Âm Dương (BAL+LAGGED) + DT5G ⭐
- `data/pt_v4_dt5g_logs.csv` — V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01
- `data/pt_v22_dt5g_logs.csv` — V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐
- `data/papertrade_compare5.csv` — daily NAV all systems
