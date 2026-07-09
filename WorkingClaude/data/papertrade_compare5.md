# Paper-Trade Comparison — 5 Systems

*Generated: 2026-07-09 15:35*

*Window: 2026-04-01 → 2026-07-08 (98 calendar days)*

*Init NAV: 50B VND fresh, all-cash, no positions (each system)*


## Headline metrics

| System | Final NAV | Total Ret | CAGR | Vol (ann) | Sharpe | Max DD | Calmar |
|---|---|---|---|---|---|---|---|
| **V11 Song Sinh + KELLY + DT5G ⭐** | 54.212B | +8.59% | +35.94% | 18.19% | +1.79 | -6.81% | +5.28 |
| **V12 Âm Dương (BAL+LAGGED) + DT5G ⭐** | 50.450B | +0.95% | +3.60% | 8.17% | +0.48 | -4.65% | +0.77 |
| **V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01** | 50.098B | +0.25% | +2.48% | 8.46% | +0.31 | -2.31% | +1.07 |
| **V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐** | 52.025B | +4.05% | +71.11% | 9.16% | +5.80 | -1.75% | +40.57 |
| **VNINDEX Buy & Hold (rebased 50B)** | 54.427B | +8.85% | +37.19% | 15.70% | +2.11 | -7.13% | +5.22 |

## Delta vs V23 (production baseline)

| System | ΔRet | ΔDD | Verdict |
|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | +4.54pp | -5.06pp | Return better, DD worse |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -3.10pp | -2.89pp | Both worse |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -3.80pp | -0.56pp | Both worse |
| VNINDEX Buy & Hold (rebased 50B) | +4.80pp | -5.37pp | Return better, DD worse |

## Grind lens — current drawdown & recent momentum

| System | Cur DD (from peak) | Underwater | Peak date | Trailing 1M | Trailing 3M |
|---|---|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | -3.1% | 61d | 2026-05-08 | +3.3% | +9.4% |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -2.9% | 62d | 2026-05-07 | +1.1% | +1.2% |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -0.3% | 7d | 2026-07-01 | +2.4% | — |
| V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐ | +0.0% | at high | 2026-07-08 | — | — |
| VNINDEX Buy & Hold (rebased 50B) | -3.9% | 51d | 2026-05-18 | +3.4% | +10.5% |

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
| 2026-07-08 | 54.21B | 50.45B | 50.10B | 52.03B | 54.43B |

## Files

- `data/pt_v11_tq34b_logs.csv` — V11 Song Sinh + KELLY + DT5G ⭐
- `data/pt_v12_macro_logs.csv` — V12 Âm Dương (BAL+LAGGED) + DT5G ⭐
- `data/pt_v4_dt5g_logs.csv` — V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01
- `data/pt_v22_dt5g_logs.csv` — V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐
- `data/papertrade_compare5.csv` — daily NAV all systems
