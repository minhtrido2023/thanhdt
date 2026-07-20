# Paper-Trade Comparison — 5 Systems

*Generated: 2026-07-20 15:39*

*Window: 2026-04-01 → 2026-07-17 (107 calendar days)*

*Init NAV: 50B VND fresh, all-cash, no positions (each system)*


## Headline metrics

| System | Final NAV | Total Ret | CAGR | Vol (ann) | Sharpe | Max DD | Calmar |
|---|---|---|---|---|---|---|---|
| **V11 Song Sinh + KELLY + DT5G ⭐** | 52.287B | +4.73% | +17.10% | 16.81% | +1.02 | -6.03% | +2.83 |
| **V12 Âm Dương (BAL+LAGGED) + DT5G ⭐** | 49.866B | -0.21% | -0.73% | 7.37% | -0.06 | -3.85% | -0.19 |
| **V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01** | 48.757B | -2.43% | -17.77% | 6.69% | -2.70 | -2.84% | -6.25 |
| **V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐** | 49.941B | -0.12% | -1.19% | 9.87% | -0.07 | -4.29% | -0.28 |
| **VNINDEX Buy & Hold (rebased 50B)** | 52.482B | +4.96% | +17.98% | 15.87% | +1.12 | -7.56% | +2.38 |

## Delta vs V23 (production baseline)

| System | ΔRet | ΔDD | Verdict |
|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | +4.85pp | -1.74pp | Return better, DD worse |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -0.10pp | +0.44pp | DD better, return worse |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -2.32pp | +1.45pp | DD better, return worse |
| VNINDEX Buy & Hold (rebased 50B) | +5.08pp | -3.27pp | Return better, DD worse |

## Grind lens — current drawdown & recent momentum

| System | Cur DD (from peak) | Underwater | Peak date | Trailing 1M | Trailing 3M |
|---|---|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | -6.0% | 64d | 2026-05-14 | -1.8% | -1.2% |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -3.7% | 71d | 2026-05-07 | -0.8% | -2.3% |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -2.8% | 16d | 2026-07-01 | -0.9% | — |
| V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐ | -4.0% | 16d | 2026-07-01 | -1.2% | — |
| VNINDEX Buy & Hold (rebased 50B) | -7.3% | 60d | 2026-05-18 | -2.4% | -1.8% |

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
| 2026-07-17 | 52.29B | 49.87B | 48.76B | 49.94B | 52.48B |

## Files

- `data/pt_v11_tq34b_logs.csv` — V11 Song Sinh + KELLY + DT5G ⭐
- `data/pt_v12_macro_logs.csv` — V12 Âm Dương (BAL+LAGGED) + DT5G ⭐
- `data/pt_v4_dt5g_logs.csv` — V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01
- `data/pt_v22_dt5g_logs.csv` — V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐
- `data/papertrade_compare5.csv` — daily NAV all systems
