# Paper-Trade Comparison — 5 Systems

*Generated: 2026-07-01 15:38*

*Window: 2026-04-01 → 2026-06-30 (90 calendar days)*

*Init NAV: 50B VND fresh, all-cash, no positions (each system)*


## Headline metrics

| System | Final NAV | Total Ret | CAGR | Vol (ann) | Sharpe | Max DD | Calmar |
|---|---|---|---|---|---|---|---|
| **V11 Song Sinh + KELLY + DT5G ⭐** | 54.483B | +9.13% | +42.56% | 18.96% | +2.00 | -6.81% | +6.25 |
| **V12 Âm Dương (BAL+LAGGED) + DT5G ⭐** | 50.714B | +1.48% | +6.15% | 8.43% | +0.76 | -4.65% | +1.32 |
| **V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01** | 49.966B | -0.02% | -0.20% | 6.77% | +0.00 | -2.31% | -0.09 |
| **V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐** | 51.642B | +3.28% | +86.14% | 6.52% | +9.65 | -0.45% | +191.32 |
| **VNINDEX Buy & Hold (rebased 50B)** | 54.612B | +9.22% | +43.06% | 16.26% | +2.32 | -7.13% | +6.04 |

## Delta vs V23 (production baseline)

| System | ΔRet | ΔDD | Verdict |
|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | +5.84pp | -6.36pp | Return better, DD worse |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -1.80pp | -4.20pp | Both worse |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -3.30pp | -1.86pp | Both worse |
| VNINDEX Buy & Hold (rebased 50B) | +5.94pp | -6.68pp | Return better, DD worse |

## Grind lens — current drawdown & recent momentum

| System | Cur DD (from peak) | Underwater | Peak date | Trailing 1M | Trailing 3M |
|---|---|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | -2.6% | 53d | 2026-05-08 | +1.4% | — |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -2.3% | 54d | 2026-05-07 | -0.9% | — |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -0.3% | 4d | 2026-06-26 | -0.0% | — |
| V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐ | -0.0% | 1d | 2026-06-29 | — | — |
| VNINDEX Buy & Hold (rebased 50B) | -3.5% | 43d | 2026-05-18 | +0.8% | — |

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
| 2026-06-15 | 52.27B | 49.52B | 49.01B | 50.17B | 52.83B |
| 2026-06-22 | 53.83B | 50.52B | 49.51B | 50.86B | 54.55B |
| 2026-06-29 | 54.45B | 50.71B | 49.98B | 51.65B | 54.46B |
| 2026-06-30 | 54.48B | 50.71B | 49.97B | 51.64B | 54.61B |

## Files

- `data/pt_v11_tq34b_logs.csv` — V11 Song Sinh + KELLY + DT5G ⭐
- `data/pt_v12_macro_logs.csv` — V12 Âm Dương (BAL+LAGGED) + DT5G ⭐
- `data/pt_v4_dt5g_logs.csv` — V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01
- `data/pt_v22_dt5g_logs.csv` — V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐
- `data/papertrade_compare5.csv` — daily NAV all systems
