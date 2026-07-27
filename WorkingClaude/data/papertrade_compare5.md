# Paper-Trade Comparison — 5 Systems

*Generated: 2026-07-27 15:40*

*Window: 2026-04-01 → 2026-07-24 (114 calendar days)*

*Init NAV: 50B VND fresh, all-cash, no positions (each system)*


## Headline metrics

| System | Final NAV | Total Ret | CAGR | Vol (ann) | Sharpe | Max DD | Calmar |
|---|---|---|---|---|---|---|---|
| **V11 Song Sinh + KELLY + DT5G ⭐** | 49.638B | -0.57% | -1.83% | 17.26% | -0.02 | -10.80% | -0.17 |
| **V12 Âm Dương (BAL+LAGGED) + DT5G ⭐** | 48.905B | -2.14% | -6.69% | 7.33% | -0.91 | -5.59% | -1.20 |
| **V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01** | 47.115B | -5.72% | -33.36% | 8.37% | -4.50 | -6.06% | -5.50 |
| **V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐** | 47.242B | -5.52% | -38.25% | 12.73% | -3.56 | -9.18% | -4.17 |
| **VNINDEX Buy & Hold (rebased 50B)** | 49.506B | -0.99% | -3.13% | 17.68% | -0.09 | -13.46% | -0.23 |

## Delta vs V23 (production baseline)

| System | ΔRet | ΔDD | Verdict |
|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | +4.94pp | -1.62pp | Return better, DD worse |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | +3.38pp | +3.59pp | Both better |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -0.20pp | +3.11pp | DD better, return worse |
| VNINDEX Buy & Hold (rebased 50B) | +4.53pp | -4.28pp | Return better, DD worse |

## Grind lens — current drawdown & recent momentum

| System | Cur DD (from peak) | Underwater | Peak date | Trailing 1M | Trailing 3M |
|---|---|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | -10.8% | 71d | 2026-05-14 | -8.3% | -9.0% |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -5.6% | 78d | 2026-05-07 | -3.7% | -5.1% |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -6.1% | 23d | 2026-07-01 | -5.5% | — |
| V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐ | -9.2% | 23d | 2026-07-01 | -8.0% | — |
| VNINDEX Buy & Hold (rebased 50B) | -12.5% | 67d | 2026-05-18 | -9.5% | -9.9% |

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
| 2026-07-24 | 49.64B | 48.90B | 47.12B | 47.24B | 49.51B |

## Files

- `data/pt_v11_tq34b_logs.csv` — V11 Song Sinh + KELLY + DT5G ⭐
- `data/pt_v12_macro_logs.csv` — V12 Âm Dương (BAL+LAGGED) + DT5G ⭐
- `data/pt_v4_dt5g_logs.csv` — V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01
- `data/pt_v22_dt5g_logs.csv` — V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐
- `data/papertrade_compare5.csv` — daily NAV all systems
