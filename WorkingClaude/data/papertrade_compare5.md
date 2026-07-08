# Paper-Trade Comparison — 5 Systems

*Generated: 2026-07-08 15:35*

*Window: 2026-04-01 → 2026-07-07 (97 calendar days)*

*Init NAV: 50B VND fresh, all-cash, no positions (each system)*


## Headline metrics

| System | Final NAV | Total Ret | CAGR | Vol (ann) | Sharpe | Max DD | Calmar |
|---|---|---|---|---|---|---|---|
| **V11 Song Sinh + KELLY + DT5G ⭐** | 54.132B | +8.43% | +35.61% | 18.33% | +1.77 | -6.81% | +5.23 |
| **V12 Âm Dương (BAL+LAGGED) + DT5G ⭐** | 50.361B | +0.77% | +2.95% | 8.22% | +0.40 | -4.65% | +0.63 |
| **V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01** | 50.076B | +0.20% | +2.09% | 8.71% | +0.27 | -2.31% | +0.90 |
| **V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐** | 51.979B | +3.96% | +72.53% | 10.09% | +5.44 | -1.75% | +41.38 |
| **VNINDEX Buy & Hold (rebased 50B)** | 54.267B | +8.53% | +36.12% | 15.82% | +2.06 | -7.13% | +5.07 |

## Delta vs V23 (production baseline)

| System | ΔRet | ΔDD | Verdict |
|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | +4.47pp | -5.06pp | Return better, DD worse |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -3.18pp | -2.89pp | Both worse |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -3.75pp | -0.56pp | Both worse |
| VNINDEX Buy & Hold (rebased 50B) | +4.57pp | -5.37pp | Return better, DD worse |

## Grind lens — current drawdown & recent momentum

| System | Cur DD (from peak) | Underwater | Peak date | Trailing 1M | Trailing 3M |
|---|---|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | -3.2% | 60d | 2026-05-08 | +3.1% | +10.2% |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -3.0% | 61d | 2026-05-07 | +0.9% | +1.3% |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -0.3% | 6d | 2026-07-01 | +2.4% | — |
| V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐ | -0.0% | 6d | 2026-07-01 | — | — |
| VNINDEX Buy & Hold (rebased 50B) | -4.1% | 50d | 2026-05-18 | +3.2% | +10.3% |

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
| 2026-07-06 | 54.07B | 50.34B | 49.36B | 51.08B | 54.13B |
| 2026-07-07 | 54.13B | 50.36B | 50.08B | 51.98B | 54.27B |

## Files

- `data/pt_v11_tq34b_logs.csv` — V11 Song Sinh + KELLY + DT5G ⭐
- `data/pt_v12_macro_logs.csv` — V12 Âm Dương (BAL+LAGGED) + DT5G ⭐
- `data/pt_v4_dt5g_logs.csv` — V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01
- `data/pt_v22_dt5g_logs.csv` — V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐
- `data/papertrade_compare5.csv` — daily NAV all systems
