# Paper-Trade Comparison — 5 Systems

*Generated: 2026-06-24 15:39*

*Window: 2026-04-01 → 2026-06-23 (83 calendar days)*

*Init NAV: 50B VND fresh, all-cash, no positions (each system)*


## Headline metrics

| System | Final NAV | Total Ret | CAGR | Vol (ann) | Sharpe | Max DD | Calmar |
|---|---|---|---|---|---|---|---|
| **V11 Song Sinh + KELLY + DT5G ⭐** | 54.192B | +8.55% | +43.46% | 19.56% | +1.98 | -6.83% | +6.36 |
| **V12 Âm Dương (BAL+LAGGED) + DT5G ⭐** | 50.547B | +1.15% | +5.15% | 8.76% | +0.63 | -4.82% | +1.07 |
| **V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01** | 49.631B | -0.69% | -10.78% | 6.83% | -1.55 | -2.29% | -4.71 |
| **V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐** | 50.544B | +1.09% | +39.00% | 6.63% | +5.18 | -0.52% | +75.36 |
| **VNINDEX Buy & Hold (rebased 50B)** | 54.877B | +9.75% | +50.62% | 16.68% | +2.59 | -7.13% | +7.10 |

## Delta vs V23 (production baseline)

| System | ΔRet | ΔDD | Verdict |
|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | +7.46pp | -6.31pp | Return better, DD worse |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | +0.06pp | -4.30pp | Return better, DD worse |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -1.77pp | -1.77pp | Both worse |
| VNINDEX Buy & Hold (rebased 50B) | +8.67pp | -6.61pp | Return better, DD worse |

## Grind lens — current drawdown & recent momentum

| System | Cur DD (from peak) | Underwater | Peak date | Trailing 1M | Trailing 3M |
|---|---|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | -3.5% | 46d | 2026-05-08 | -1.1% | — |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -2.9% | 47d | 2026-05-07 | -0.9% | — |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -0.7% | 22d | 2026-06-01 | — | — |
| V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐ | +0.0% | at high | 2026-06-23 | — | — |
| VNINDEX Buy & Hold (rebased 50B) | -3.1% | 36d | 2026-05-18 | -0.9% | — |

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
| 2026-06-08 | 52.69B | 49.93B | 48.88B | — | 52.57B |
| 2026-06-15 | 52.46B | 49.53B | 48.99B | 50.10B | 52.83B |
| 2026-06-22 | 54.06B | 50.55B | 49.50B | 50.52B | 54.55B |
| 2026-06-23 | 54.19B | 50.55B | 49.63B | 50.54B | 54.88B |

## Files

- `data/pt_v11_tq34b_logs.csv` — V11 Song Sinh + KELLY + DT5G ⭐
- `data/pt_v12_macro_logs.csv` — V12 Âm Dương (BAL+LAGGED) + DT5G ⭐
- `data/pt_v4_dt5g_logs.csv` — V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01
- `data/pt_v22_dt5g_logs.csv` — V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐
- `data/papertrade_compare5.csv` — daily NAV all systems
