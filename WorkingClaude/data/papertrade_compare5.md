# Paper-Trade Comparison — 5 Systems

*Generated: 2026-06-29 15:36*

*Window: 2026-04-01 → 2026-06-25 (85 calendar days)*

*Init NAV: 50B VND fresh, all-cash, no positions (each system)*


## Headline metrics

| System | Final NAV | Total Ret | CAGR | Vol (ann) | Sharpe | Max DD | Calmar |
|---|---|---|---|---|---|---|---|
| **V11 Song Sinh + KELLY + DT5G ⭐** | 54.543B | +9.25% | +46.25% | 19.33% | +2.08 | -6.85% | +6.75 |
| **V12 Âm Dương (BAL+LAGGED) + DT5G ⭐** | 50.997B | +2.05% | +9.10% | 8.59% | +1.07 | -4.67% | +1.95 |
| **V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01** | 49.853B | -0.24% | -3.60% | 7.04% | -0.45 | -2.31% | -1.56 |
| **V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐** | 50.342B | +0.68% | +19.46% | 6.50% | +2.67 | -0.53% | +36.88 |
| **VNINDEX Buy & Hold (rebased 50B)** | 54.702B | +9.40% | +47.14% | 16.52% | +2.45 | -7.13% | +6.61 |

## Delta vs V23 (production baseline)

| System | ΔRet | ΔDD | Verdict |
|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | +8.57pp | -6.33pp | Return better, DD worse |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | +1.36pp | -4.14pp | Return better, DD worse |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -0.92pp | -1.78pp | Both worse |
| VNINDEX Buy & Hold (rebased 50B) | +8.72pp | -6.60pp | Return better, DD worse |

## Grind lens — current drawdown & recent momentum

| System | Cur DD (from peak) | Underwater | Peak date | Trailing 1M | Trailing 3M |
|---|---|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | -2.8% | 48d | 2026-05-08 | +0.4% | — |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -2.0% | 49d | 2026-05-07 | -0.3% | — |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -0.2% | 24d | 2026-06-01 | — | — |
| V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐ | -0.5% | 1d | 2026-06-24 | — | — |
| VNINDEX Buy & Hold (rebased 50B) | -3.4% | 38d | 2026-05-18 | -0.6% | — |

*Grind = sustained underwater stretch where the book bleeds while the index holds/rises (style-divergence). V2.3's known weak spot is the 2025-08→ style-divergence grind (momentum lags the VIC-led megacap index); watch V2.3 trailing-3M vs VNINDEX.*

## Weekly NAV snapshot (every ~5 trading days)

| Date | V11 Song Sinh + KELLY + DT5G ⭐ | V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐ | VNINDEX Buy & Hold (rebased 50B) |
|---|---|---|---|---|---|
| 2026-04-01 | 49.92B | 49.97B | — | — | 50.00B |
| 2026-04-08 | 53.02B | 51.09B | — | — | 51.57B |
| 2026-04-15 | 52.54B | 50.97B | — | — | 52.87B |
| 2026-04-22 | 53.84B | 51.33B | — | — | 54.53B |
| 2026-05-04 | 54.21B | 50.98B | — | — | 54.44B |
| 2026-05-11 | 55.44B | 51.43B | — | — | 55.65B |
| 2026-05-18 | 55.36B | 51.72B | — | — | 56.61B |
| 2026-05-25 | 54.78B | 51.00B | — | — | 55.38B |
| 2026-06-01 | 53.95B | 51.28B | 49.97B | — | 54.16B |
| 2026-06-08 | 52.68B | 50.01B | 48.88B | — | 52.57B |
| 2026-06-15 | 52.45B | 49.61B | 49.01B | 50.10B | 52.83B |
| 2026-06-22 | 54.03B | 50.62B | 49.51B | 50.46B | 54.55B |
| 2026-06-25 | 54.54B | 51.00B | 49.85B | 50.34B | 54.70B |

## Files

- `data/pt_v11_tq34b_logs.csv` — V11 Song Sinh + KELLY + DT5G ⭐
- `data/pt_v12_macro_logs.csv` — V12 Âm Dương (BAL+LAGGED) + DT5G ⭐
- `data/pt_v4_dt5g_logs.csv` — V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01
- `data/pt_v22_dt5g_logs.csv` — V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐
- `data/papertrade_compare5.csv` — daily NAV all systems
