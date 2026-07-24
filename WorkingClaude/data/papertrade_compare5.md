# Paper-Trade Comparison — 5 Systems

*Generated: 2026-07-24 15:36*

*Window: 2026-04-01 → 2026-07-23 (113 calendar days)*

*Init NAV: 50B VND fresh, all-cash, no positions (each system)*


## Headline metrics

| System | Final NAV | Total Ret | CAGR | Vol (ann) | Sharpe | Max DD | Calmar |
|---|---|---|---|---|---|---|---|
| **V11 Song Sinh + KELLY + DT5G ⭐** | 49.190B | -1.47% | -4.68% | 18.18% | -0.18 | -12.43% | -0.38 |
| **V12 Âm Dương (BAL+LAGGED) + DT5G ⭐** | 48.469B | -3.01% | -9.41% | 8.51% | -1.12 | -6.91% | -1.36 |
| **V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01** | 47.362B | -5.23% | -31.41% | 8.43% | -4.18 | -5.94% | -5.28 |
| **V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐** | 47.624B | -4.75% | -34.52% | 12.81% | -3.13 | -8.44% | -4.09 |
| **VNINDEX Buy & Hold (rebased 50B)** | 49.896B | -0.21% | -0.67% | 17.74% | +0.05 | -13.46% | -0.05 |

## Delta vs V23 (production baseline)

| System | ΔRet | ΔDD | Verdict |
|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | +3.28pp | -3.98pp | Return better, DD worse |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | +1.74pp | +1.53pp | Both better |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -0.47pp | +2.50pp | DD better, return worse |
| VNINDEX Buy & Hold (rebased 50B) | +4.54pp | -5.01pp | Return better, DD worse |

## Grind lens — current drawdown & recent momentum

| System | Cur DD (from peak) | Underwater | Peak date | Trailing 1M | Trailing 3M |
|---|---|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | -11.6% | 70d | 2026-05-14 | -9.3% | -8.6% |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -6.4% | 77d | 2026-05-07 | -4.0% | -5.6% |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -5.6% | 22d | 2026-07-01 | -5.2% | — |
| V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐ | -8.4% | 22d | 2026-07-01 | -7.5% | — |
| VNINDEX Buy & Hold (rebased 50B) | -11.9% | 66d | 2026-05-18 | -9.5% | -8.5% |

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
| 2026-07-20 | 50.54B | 48.80B | 48.23B | 48.81B | 51.19B |
| 2026-07-23 | 49.19B | 48.47B | 47.36B | 47.62B | 49.90B |

## Files

- `data/pt_v11_tq34b_logs.csv` — V11 Song Sinh + KELLY + DT5G ⭐
- `data/pt_v12_macro_logs.csv` — V12 Âm Dương (BAL+LAGGED) + DT5G ⭐
- `data/pt_v4_dt5g_logs.csv` — V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01
- `data/pt_v22_dt5g_logs.csv` — V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐
- `data/papertrade_compare5.csv` — daily NAV all systems
