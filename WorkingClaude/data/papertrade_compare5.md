# Paper-Trade Comparison — 5 Systems

*Generated: 2026-07-17 15:40*

*Window: 2026-04-01 → 2026-07-16 (106 calendar days)*

*Init NAV: 50B VND fresh, all-cash, no positions (each system)*


## Headline metrics

| System | Final NAV | Total Ret | CAGR | Vol (ann) | Sharpe | Max DD | Calmar |
|---|---|---|---|---|---|---|---|
| **V11 Song Sinh + KELLY + DT5G ⭐** | 52.598B | +5.35% | +19.69% | 16.88% | +1.15 | -5.95% | +3.31 |
| **V12 Âm Dương (BAL+LAGGED) + DT5G ⭐** | 50.029B | +0.11% | +0.38% | 7.40% | +0.09 | -3.85% | +0.10 |
| **V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01** | 48.959B | -2.03% | -15.34% | 6.73% | -2.29 | -2.84% | -5.40 |
| **V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐** | 50.252B | +0.50% | +5.38% | 9.87% | +0.56 | -4.29% | +1.25 |
| **VNINDEX Buy & Hold (rebased 50B)** | 52.975B | +5.95% | +22.03% | 15.87% | +1.34 | -7.56% | +2.91 |

## Delta vs V23 (production baseline)

| System | ΔRet | ΔDD | Verdict |
|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | +4.85pp | -1.65pp | Return better, DD worse |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -0.39pp | +0.44pp | DD better, return worse |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -2.53pp | +1.45pp | DD better, return worse |
| VNINDEX Buy & Hold (rebased 50B) | +5.45pp | -3.27pp | Return better, DD worse |

## Grind lens — current drawdown & recent momentum

| System | Cur DD (from peak) | Underwater | Peak date | Trailing 1M | Trailing 3M |
|---|---|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | -5.5% | 63d | 2026-05-14 | +0.0% | +0.1% |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -3.4% | 70d | 2026-05-07 | +0.2% | -1.8% |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -2.4% | 15d | 2026-07-01 | +0.2% | — |
| V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐ | -3.4% | 15d | 2026-07-01 | -0.3% | — |
| VNINDEX Buy & Hold (rebased 50B) | -6.4% | 59d | 2026-05-18 | -0.1% | +0.2% |

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
| 2026-07-16 | 52.60B | 50.03B | 48.96B | 50.25B | 52.97B |

## Files

- `data/pt_v11_tq34b_logs.csv` — V11 Song Sinh + KELLY + DT5G ⭐
- `data/pt_v12_macro_logs.csv` — V12 Âm Dương (BAL+LAGGED) + DT5G ⭐
- `data/pt_v4_dt5g_logs.csv` — V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01
- `data/pt_v22_dt5g_logs.csv` — V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐
- `data/papertrade_compare5.csv` — daily NAV all systems
