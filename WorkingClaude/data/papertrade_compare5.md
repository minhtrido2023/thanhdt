# Paper-Trade Comparison — 5 Systems

*Generated: 2026-07-15 15:39*

*Window: 2026-04-01 → 2026-07-14 (104 calendar days)*

*Init NAV: 50B VND fresh, all-cash, no positions (each system)*


## Headline metrics

| System | Final NAV | Total Ret | CAGR | Vol (ann) | Sharpe | Max DD | Calmar |
|---|---|---|---|---|---|---|---|
| **V11 Song Sinh + KELLY + DT5G ⭐** | 52.694B | +5.55% | +20.87% | 17.04% | +1.21 | -5.56% | +3.76 |
| **V12 Âm Dương (BAL+LAGGED) + DT5G ⭐** | 50.016B | +0.08% | +0.29% | 7.49% | +0.08 | -3.85% | +0.08 |
| **V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01** | 48.986B | -1.98% | -15.59% | 6.65% | -2.41 | -2.33% | -6.68 |
| **V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐** | 50.362B | +0.72% | +8.31% | 8.95% | +0.93 | -3.27% | +2.54 |
| **VNINDEX Buy & Hold (rebased 50B)** | 53.045B | +6.09% | +23.07% | 15.71% | +1.41 | -7.13% | +3.24 |

## Delta vs V23 (production baseline)

| System | ΔRet | ΔDD | Verdict |
|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | +4.82pp | -2.29pp | Return better, DD worse |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -0.64pp | -0.58pp | Both worse |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -2.70pp | +0.94pp | DD better, return worse |
| VNINDEX Buy & Hold (rebased 50B) | +5.37pp | -3.85pp | Return better, DD worse |

## Grind lens — current drawdown & recent momentum

| System | Cur DD (from peak) | Underwater | Peak date | Trailing 1M | Trailing 3M |
|---|---|---|---|---|---|
| V11 Song Sinh + KELLY + DT5G ⭐ | -5.3% | 61d | 2026-05-14 | -0.1% | +2.0% |
| V12 Âm Dương (BAL+LAGGED) + DT5G ⭐ | -3.4% | 68d | 2026-05-07 | +0.4% | -1.2% |
| V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01 | -2.3% | 13d | 2026-07-01 | -0.0% | — |
| V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐ | -3.2% | 13d | 2026-07-01 | +0.4% | — |
| VNINDEX Buy & Hold (rebased 50B) | -6.3% | 57d | 2026-05-18 | +0.4% | +2.7% |

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
| 2026-06-15 | 52.73B | 49.80B | 48.99B | 50.15B | 52.83B |
| 2026-06-22 | 53.65B | 50.46B | 49.50B | 50.88B | 54.55B |
| 2026-06-29 | 54.28B | 50.67B | 49.96B | 51.67B | 54.46B |
| 2026-07-06 | 53.99B | 50.46B | 49.76B | 51.41B | 54.13B |
| 2026-07-13 | 52.82B | 50.06B | 49.07B | 50.30B | 52.87B |
| 2026-07-14 | 52.69B | 50.02B | 48.99B | 50.36B | 53.04B |

## Files

- `data/pt_v11_tq34b_logs.csv` — V11 Song Sinh + KELLY + DT5G ⭐
- `data/pt_v12_macro_logs.csv` — V12 Âm Dương (BAL+LAGGED) + DT5G ⭐
- `data/pt_v4_dt5g_logs.csv` — V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01
- `data/pt_v22_dt5g_logs.csv` — V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐
- `data/papertrade_compare5.csv` — daily NAV all systems
