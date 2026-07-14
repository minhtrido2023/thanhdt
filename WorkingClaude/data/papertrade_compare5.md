# Paper-Trade Comparison — 5 Systems

*Generated: 2026-07-14 15:37*

*Window: 2026-04-01 → 2026-07-13 (103 calendar days)*

*Init NAV: 50B VND fresh, all-cash, no positions (each system)*


## Headline metrics

| System | Final NAV | Total Ret | CAGR | Vol (ann) | Sharpe | Max DD | Calmar |
|---|---|---|---|---|---|---|---|
| **V11 Song Sinh + KELLY + DT5G ⭐** | 52.321B | +4.80% | +18.08% | 17.53% | +1.05 | -5.97% | +3.03 |
| **V12 Âm Dương (BAL+LAGGED) + DT5G ⭐** | 49.719B | -0.51% | -1.80% | 7.81% | -0.20 | -4.02% | -0.45 |
| **V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01** | 49.071B | -1.81% | -14.66% | 6.75% | -2.23 | -2.29% | -6.41 |
| **V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐** | 50.309B | +0.62% | +7.29% | 9.17% | +0.81 | -3.27% | +2.23 |
| **VNINDEX Buy & Hold (rebased 50B)** | 52.866B | +5.73% | +21.85% | 15.81% | +1.35 | -7.13% | +3.07 |

## Delta vs V23 (production baseline)

| System | ΔRet | ΔDD | Verdict |
|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | +4.18pp | -2.70pp | Return better, DD worse |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -1.13pp | -0.74pp | Both worse |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -2.42pp | +0.98pp | DD better, return worse |
| VNINDEX Buy & Hold (rebased 50B) | +5.11pp | -3.86pp | Return better, DD worse |

## Grind lens — current drawdown & recent momentum

| System | Cur DD (from peak) | Underwater | Peak date | Trailing 1M | Trailing 3M |
|---|---|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | -6.0% | 60d | 2026-05-14 | -0.4% | +0.9% |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -4.0% | 67d | 2026-05-07 | -0.2% | -2.0% |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -2.2% | 12d | 2026-07-01 | +0.5% | — |
| V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐ | -3.3% | 12d | 2026-07-01 | +0.8% | — |
| VNINDEX Buy & Hold (rebased 50B) | -6.6% | 56d | 2026-05-18 | +0.5% | +2.9% |

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
| 2026-06-22 | 53.65B | 50.46B | 49.50B | 50.88B | 54.55B |
| 2026-06-29 | 54.28B | 50.65B | 49.96B | 51.67B | 54.46B |
| 2026-07-06 | 53.61B | 50.13B | 49.76B | 51.43B | 54.13B |
| 2026-07-13 | 52.32B | 49.72B | 49.07B | 50.31B | 52.87B |

## Files

- `data/pt_v11_tq34b_logs.csv` — V11 Song Sinh + KELLY + DT5G ⭐
- `data/pt_v12_macro_logs.csv` — V12 Âm Dương (BAL+LAGGED) + DT5G ⭐
- `data/pt_v4_dt5g_logs.csv` — V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01
- `data/pt_v22_dt5g_logs.csv` — V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐
- `data/papertrade_compare5.csv` — daily NAV all systems
