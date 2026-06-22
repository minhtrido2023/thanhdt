# Paper-Trade Comparison — 5 Systems

*Generated: 2026-06-22 15:34*

*Window: 2026-04-01 → 2026-06-19 (79 calendar days)*

*Init NAV: 50B VND fresh, all-cash, no positions (each system)*


## Headline metrics

| System | Final NAV | Total Ret | CAGR | Vol (ann) | Sharpe | Max DD | Calmar |
|---|---|---|---|---|---|---|---|
| **V11 Song Sinh + KELLY + DT5G ⭐** | 53.048B | +6.26% | +32.86% | 19.88% | +1.55 | -6.98% | +4.71 |
| **V12 Âm Dương (BAL+LAGGED) + DT5G ⭐** | 49.916B | -0.12% | -0.54% | 8.81% | -0.02 | -5.02% | -0.11 |
| **V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01** | 49.268B | -1.41% | -26.32% | 6.75% | -4.05 | -2.32% | -11.35 |
| **V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐** | 49.881B | -0.24% | -10.30% | 4.60% | -2.15 | -0.53% | -19.56 |

## Delta vs V23 (production baseline)

| System | ΔRet | ΔDD | Verdict |
|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | +6.49pp | -6.45pp | Return better, DD worse |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | +0.12pp | -4.50pp | Return better, DD worse |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -1.17pp | -1.79pp | Both worse |

## Grind lens — current drawdown & recent momentum

| System | Cur DD (from peak) | Underwater | Peak date | Trailing 1M | Trailing 3M |
|---|---|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | -5.3% | 41d | 2026-05-08 | -3.4% | — |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -3.9% | 42d | 2026-05-07 | -3.1% | — |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -1.4% | 17d | 2026-06-01 | — | — |
| V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐ | -0.5% | 1d | 2026-06-18 | — | — |

*Grind = sustained underwater stretch where the book bleeds while the index holds/rises (style-divergence). V2.3's known weak spot is the 2025-08→ style-divergence grind (momentum lags the VIC-led megacap index); watch V2.3 trailing-3M vs VNINDEX.*

## Weekly NAV snapshot (every ~5 trading days)

| Date | V11 Song Sinh + KELLY + DT5G ⭐ | V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐ |
|---|---|---|---|---|
| 2026-04-01 | 49.92B | 49.97B | — | — |
| 2026-04-08 | 53.02B | 51.09B | — | — |
| 2026-04-15 | 52.54B | 50.97B | — | — |
| 2026-04-22 | 53.79B | 51.29B | — | — |
| 2026-05-04 | 54.08B | 50.87B | — | — |
| 2026-05-11 | 55.38B | 51.37B | — | — |
| 2026-05-18 | 55.29B | 51.67B | — | — |
| 2026-05-25 | 54.79B | 51.03B | — | — |
| 2026-06-01 | 53.88B | 51.20B | 49.97B | — |
| 2026-06-08 | 52.46B | 49.70B | 48.87B | — |
| 2026-06-15 | 52.27B | 49.35B | 49.01B | 49.92B |
| 2026-06-19 | 53.05B | 49.92B | 49.27B | 49.88B |

## Files

- `data/pt_v11_tq34b_logs.csv` — V11 Song Sinh + KELLY + DT5G ⭐
- `data/pt_v12_macro_logs.csv` — V12 Âm Dương (BAL+LAGGED) + DT5G ⭐
- `data/pt_v4_dt5g_logs.csv` — V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01
- `data/pt_v22_dt5g_logs.csv` — V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐
- `data/papertrade_compare5.csv` — daily NAV all systems
