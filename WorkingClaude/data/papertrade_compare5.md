# Paper-Trade Comparison — 5 Systems

*Generated: 2026-07-02 15:38*

*Window: 2026-04-01 → 2026-07-01 (91 calendar days)*

*Init NAV: 50B VND fresh, all-cash, no positions (each system)*


## Headline metrics

| System | Final NAV | Total Ret | CAGR | Vol (ann) | Sharpe | Max DD | Calmar |
|---|---|---|---|---|---|---|---|
| **V11 Song Sinh + KELLY + DT5G ⭐** | 54.720B | +9.60% | +44.49% | 18.82% | +2.07 | -6.81% | +6.53 |
| **V12 Âm Dương (BAL+LAGGED) + DT5G ⭐** | 50.824B | +1.70% | +7.00% | 8.37% | +0.86 | -4.65% | +1.51 |
| **V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01** | 50.246B | +0.54% | +6.84% | 6.87% | +0.94 | -2.31% | +2.96 |
| **V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐** | 51.993B | +3.99% | +104.18% | 6.52% | +10.83 | -0.45% | +231.40 |
| **VNINDEX Buy & Hold (rebased 50B)** | 54.823B | +9.65% | +44.72% | 16.14% | +2.40 | -7.13% | +6.27 |

## Delta vs V23 (production baseline)

| System | ΔRet | ΔDD | Verdict |
|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | +5.62pp | -6.36pp | Return better, DD worse |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -2.29pp | -4.20pp | Both worse |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -3.44pp | -1.86pp | Both worse |
| VNINDEX Buy & Hold (rebased 50B) | +5.66pp | -6.68pp | Return better, DD worse |

## Grind lens — current drawdown & recent momentum

| System | Cur DD (from peak) | Underwater | Peak date | Trailing 1M | Trailing 3M |
|---|---|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | -2.1% | 54d | 2026-05-08 | +2.4% | — |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -2.1% | 55d | 2026-05-07 | -0.6% | — |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | +0.0% | at high | 2026-07-01 | +1.0% | — |
| V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐ | +0.0% | at high | 2026-07-01 | — | — |
| VNINDEX Buy & Hold (rebased 50B) | -3.1% | 44d | 2026-05-18 | +2.2% | — |

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
| 2026-07-01 | 54.72B | 50.82B | 50.25B | 51.99B | 54.82B |

## Files

- `data/pt_v11_tq34b_logs.csv` — V11 Song Sinh + KELLY + DT5G ⭐
- `data/pt_v12_macro_logs.csv` — V12 Âm Dương (BAL+LAGGED) + DT5G ⭐
- `data/pt_v4_dt5g_logs.csv` — V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01
- `data/pt_v22_dt5g_logs.csv` — V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐
- `data/papertrade_compare5.csv` — daily NAV all systems
