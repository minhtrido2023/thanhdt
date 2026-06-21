---
name: Stop -25% validation across periods
description: Multi-period stop-loss test (-15%/-18%/-20%/-22%/-25%/-28%/-30%) on BAL_Fin4 v10 50B. Confirms stop -20% is the robust choice; -25% only wins in pure bull periods, loses badly in 2021-2023 crash.
type: project
originSessionId: df3c1340-40c2-46c7-b6dc-247737308843
---
## Stop-loss validation (test_stop_validation.py, 2026-05-10)

Tested 7 stops × 7 periods = 49 BA-system simulations on BAL+Fin/RE-max-4 v10 at 50B. Output: `stop_validation_results.csv`.

### Δ Stop -25% vs -20% (production baseline)

| Period | ΔCAGR | ΔSharpe | ΔDD | ΔCalmar |
|---|---|---|---|---|
| Full 2014-2026 | **+0.33pp** | +0.00 | -0.2pp worse | +0.01 |
| 2014-2017 (calib) | -0.11pp | -0.01 | -0.3pp | -0.09 |
| 2018-2020 (chop+COVID) | -0.17pp | -0.02 | -0.3pp | -0.03 |
| **2021-2023 (bull+crash)** | **-2.97pp** ❌ | -0.02 | -0.8pp | -0.19 |
| 2024-2026 (recent bull) | +1.75pp | +0.05 | -1.9pp worse | -0.05 |
| IS 2014-2019 | -0.13pp | -0.03 | -0.2pp | -0.01 |
| OOS 2020-2026 | +0.68pp | +0.01 | -1.0pp | -0.06 |

### Verdict — Stop -20% is robust, -25% is fragile

- Full-period +0.33pp CAGR gain from -25% is real but small
- **In 2021-2023 specifically (the crash period user worried about), -25% LOSES -2.97pp CAGR** vs -20%. Stop -22% optimal there (26.03% CAGR vs -25%'s 23.06%)
- DD universally **worse** with -25% across ALL periods (deeper drawdowns by 0.2-1.9pp)
- Sharpe essentially identical (±0.05) across periods
- The "marginal win" comes mostly from 2024-2026 (recent bull where stops rarely fire)

### Best stop per period (CAGR-optimal)

| Period | Best stop | CAGR |
|---|---|---|
| Full 2014-2026 | -30% | 18.88% |
| 2014-2017 | -15% | 9.93% |
| 2018-2020 (chop+COVID) | -15% | 21.31% |
| **2021-2023 (bull+crash)** | **-22%** | 26.03% |
| 2024-2026 | -30% | 25.29% |
| IS 2014-2019 | -15% | 7.65% |
| OOS 2020-2026 | -28% | 34.38% |

Optimal stop varies dramatically by period — no universal best. Stop -20% is in top-3 by Sharpe in 6/7 periods and gives the lowest DD in 4/7 periods.

### Conclusion

**KEEP stop -20%.** The user's instinct was correct:
- Marginal full-period CAGR gain doesn't survive period segmentation
- DD trade-off works against you in every period
- Crash defense (the prime concern) is worse with -25%
