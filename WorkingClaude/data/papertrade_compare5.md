# Paper-Trade Comparison — 5 Systems

*Generated: 2026-07-13 15:36*

*Window: 2026-04-01 → 2026-07-10 (100 calendar days)*

*Init NAV: 50B VND fresh, all-cash, no positions (each system)*


## Headline metrics

| System | Final NAV | Total Ret | CAGR | Vol (ann) | Sharpe | Max DD | Calmar |
|---|---|---|---|---|---|---|---|
| **V11 Song Sinh + KELLY + DT5G ⭐** | 53.849B | +7.86% | +31.83% | 17.97% | +1.62 | -6.81% | +4.67 |
| **V12 Âm Dương (BAL+LAGGED) + DT5G ⭐** | 50.337B | +0.73% | +2.68% | 8.05% | +0.37 | -4.65% | +0.58 |
| **V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01** | 49.626B | -0.70% | -6.34% | 6.07% | -0.97 | -2.29% | -2.77 |
| **V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐** | 50.898B | +1.80% | +25.15% | 8.01% | +2.71 | -2.13% | +11.79 |
| **VNINDEX Buy & Hold (rebased 50B)** | 53.682B | +7.36% | +29.63% | 15.62% | +1.74 | -7.13% | +4.16 |

## Delta vs V23 (production baseline)

| System | ΔRet | ΔDD | Verdict |
|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | +6.06pp | -4.68pp | Return better, DD worse |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -1.07pp | -2.52pp | Both worse |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -2.49pp | -0.16pp | Both worse |
| VNINDEX Buy & Hold (rebased 50B) | +5.57pp | -5.00pp | Return better, DD worse |

## Grind lens — current drawdown & recent momentum

| System | Cur DD (from peak) | Underwater | Peak date | Trailing 1M | Trailing 3M |
|---|---|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | -3.7% | 63d | 2026-05-08 | +2.5% | +4.1% |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -3.1% | 64d | 2026-05-07 | +1.0% | -0.6% |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -1.1% | 9d | 2026-07-01 | +1.6% | — |
| V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐ | -2.1% | 9d | 2026-07-01 | +1.8% | — |
| VNINDEX Buy & Hold (rebased 50B) | -5.2% | 53d | 2026-05-18 | +1.7% | +5.3% |

*Grind = sustained underwater stretch where the book bleeds while the index holds/rises (style-divergence). V2.3's known weak spot is the 2025-08→ style-divergence grind (momentum lags the VIC-led megacap index); watch V2.3 trailing-3M vs VNINDEX.*

## Weekly NAV snapshot (every ~5 trading days)

| Date | V11 Song Sinh + KELLY + DT5G ⭐ | V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐ | VNINDEX Buy & Hold (rebased 50B) |
|---|---|---|---|---|---|
| 2026-04-01 | 49.92B | 49.97B | — | — | 50.00B |
| 2026-04-08 | 53.02B | 51.09B | — | — | 51.57B |
| 2026-04-15 | 52.54B | 50.97B | — | — | 52.87B |
| 2026-04-22 | 53.84B | 51.33B | — | — | 54.53B |
| 2026-05-04 | 54.02B | 50.89B | — | — | 54.44B |
| 2026-05-11 | 55.24B | 51.32B | — | — | 55.65B |
| 2026-05-18 | 55.16B | 51.62B | — | — | 56.61B |
| 2026-05-25 | 54.57B | 50.90B | — | — | 55.38B |
| 2026-06-01 | 53.76B | 51.18B | 49.97B | — | 54.16B |
| 2026-06-08 | 52.49B | 49.91B | 48.88B | — | 52.57B |
| 2026-06-15 | 52.27B | 49.52B | 48.99B | 50.17B | 52.83B |
| 2026-06-22 | 53.83B | 50.52B | 49.50B | 50.88B | 54.55B |
| 2026-06-29 | 54.45B | 50.71B | 49.96B | 51.67B | 54.46B |
| 2026-07-06 | 54.07B | 50.34B | 49.76B | 51.30B | 54.13B |
| 2026-07-10 | 53.85B | 50.34B | 49.63B | 50.90B | 53.68B |

## Files

- `data/pt_v11_tq34b_logs.csv` — V11 Song Sinh + KELLY + DT5G ⭐
- `data/pt_v12_macro_logs.csv` — V12 Âm Dương (BAL+LAGGED) + DT5G ⭐
- `data/pt_v4_dt5g_logs.csv` — V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01
- `data/pt_v22_dt5g_logs.csv` — V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐
- `data/papertrade_compare5.csv` — daily NAV all systems
