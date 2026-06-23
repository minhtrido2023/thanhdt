# Paper-Trade Comparison — 5 Systems

*Generated: 2026-06-23 15:39*

*Window: 2026-04-01 → 2026-06-22 (82 calendar days)*

*Init NAV: 50B VND fresh, all-cash, no positions (each system)*


## Headline metrics

| System | Final NAV | Total Ret | CAGR | Vol (ann) | Sharpe | Max DD | Calmar |
|---|---|---|---|---|---|---|---|
| **V11 Song Sinh + KELLY + DT5G ⭐** | 54.031B | +8.22% | +42.20% | 19.74% | +1.93 | -6.85% | +6.16 |
| **V12 Âm Dương (BAL+LAGGED) + DT5G ⭐** | 50.546B | +1.15% | +5.20% | 8.84% | +0.63 | -4.82% | +1.08 |
| **V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01** | 49.508B | -0.93% | -15.02% | 6.95% | -2.23 | -2.31% | -6.50 |
| **V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐** | 50.498B | +1.00% | +39.01% | 7.05% | +5.10 | -0.53% | +73.94 |
| **VNINDEX Buy & Hold (rebased 50B)** | 54.550B | +9.10% | +47.40% | 16.81% | +2.46 | -7.13% | +6.65 |

## Delta vs V23 (production baseline)

| System | ΔRet | ΔDD | Verdict |
|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | +7.23pp | -6.33pp | Return better, DD worse |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | +0.15pp | -4.29pp | Return better, DD worse |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -1.93pp | -1.78pp | Both worse |
| VNINDEX Buy & Hold (rebased 50B) | +8.10pp | -6.60pp | Return better, DD worse |

## Grind lens — current drawdown & recent momentum

| System | Cur DD (from peak) | Underwater | Peak date | Trailing 1M | Trailing 3M |
|---|---|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | -3.7% | 45d | 2026-05-08 | -0.8% | — |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -2.9% | 46d | 2026-05-07 | -0.8% | — |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -0.9% | 21d | 2026-06-01 | — | — |
| V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐ | +0.0% | at high | 2026-06-22 | — | — |
| VNINDEX Buy & Hold (rebased 50B) | -3.6% | 35d | 2026-05-18 | -1.0% | — |

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
| 2026-06-08 | 52.68B | 49.93B | 48.88B | — | 52.57B |
| 2026-06-15 | 52.45B | 49.53B | 49.01B | 50.10B | 52.83B |
| 2026-06-22 | 54.03B | 50.55B | 49.51B | 50.50B | 54.55B |

## Files

- `data/pt_v11_tq34b_logs.csv` — V11 Song Sinh + KELLY + DT5G ⭐
- `data/pt_v12_macro_logs.csv` — V12 Âm Dương (BAL+LAGGED) + DT5G ⭐
- `data/pt_v4_dt5g_logs.csv` — V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01
- `data/pt_v22_dt5g_logs.csv` — V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐
- `data/papertrade_compare5.csv` — daily NAV all systems
