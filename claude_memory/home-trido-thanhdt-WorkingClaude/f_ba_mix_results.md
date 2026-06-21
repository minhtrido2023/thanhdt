---
name: F-system + BA-system mix results
description: Backtest mixing BA-system (stocks) with F_Balanced/F_HAdapted/F_Conservative (VN30F derivatives state-map) at various weights. Best Sharpe = 70-80% BA + 20-30% F_HAdapted (Sh 1.26-1.27 vs BA-only 1.21).
type: project
originSessionId: df3c1340-40c2-46c7-b6dc-247737308843
---
## F-system + BA-system mix (test_f_ba_mix.py, 2026-05-10)

Backtested 7 mix weights × 3 F-variants on 2014-2026 (3005 sessions).
F-system NAVs computed self-contained from BQ 5-state + VN30 underlying with TC=0.03%, roll cost 1.2%/yr (matches f_system_backtest.py F_MAPS).

### Standalone NAV comparison (full 2014-2026)

| System | CAGR | Sharpe | Sortino | MaxDD | Calmar | Wealth |
|---|---|---|---|---|---|---|
| **BA-system 50/50** | **17.15%** | **1.21** | 0.96 | -14.5% | **1.18** | 6.72× |
| F_HAdapted (futures) | 12.82% | 0.81 | 1.08 | -32.0% | 0.40 | 4.27× |
| F_Balanced (futures) | 6.88% | 0.52 | 0.51 | -24.1% | 0.29 | 2.23× |
| F_Conservative | 6.10% | 0.61 | 0.53 | -14.7% | 0.41 | 2.04× |
| H-system (cash) | 11.53% | 1.01 | 0.97 | -17.9% | 0.64 | 3.72× |
| B&H VNINDEX | 11.54% | 0.69 | 0.81 | -45.3% | 0.26 | 3.72× |

### Mix grid — BA × F_HAdapted (best mix variant)

| Mix BA / F | CAGR | Sharpe | DD | Calmar | Wealth |
|---|---|---|---|---|---|
| 100% / 0% (baseline) | 17.15% | 1.21 | -14.5% | 1.18 | 6.72× |
| **80% / 20%** | 16.42% | **1.26** ⭐ | -14.4% | 1.14 | 6.23× |
| **70% / 30%** | 16.03% | **1.27** ⭐ | -14.4% | 1.11 | 5.99× |
| 60% / 40% | 15.63% | 1.25 | -14.4% | 1.09 | 5.74× |
| 50% / 50% | 15.21% | 1.21 | -14.3% | 1.06 | 5.50× |

Mix with F_Balanced or F_Conservative HURTS both CAGR and Sharpe linearly. F_HAdapted is the only mix variant that adds positive value.

### Year-by-year (BA vs 80BA/20F_Bal vs F_Bal-only)

Critical years where F-system shines (counter-cyclical):
- **2018 (broad sell-off):** BA +11.1%, F_Bal **+38.0%**, mix80 +14.9% — F-system catches short side
- **2022 crash:** BA +2.6%, F_Bal **+19.8%**, mix80 +4.0% — F-system shorts BEAR
- 2024 (mild bull): BA +11.6%, F_Bal +3.4%, mix80 +10.8% — F-system flat

But F-system DRAGS in mega-bull years:
- 2021: BA **+94.4%**, F_Bal +2.2% — F flat through bull (state stayed BEAR/NEUTRAL too long)
- 2023: BA -4.5%, F_Bal -0.6% — both flat

### Verdict

- **Best Sharpe mix: 70-80% BA + 20-30% F_HAdapted** → +0.05 to +0.06 Sharpe vs BA-only
- Trade-off: -0.7 to -1.1pp CAGR
- DD essentially unchanged (~-14.4%)
- F-system serves as **portfolio insurance during BEAR** (2018, 2022)
- F-system is a **drag in stable bull years** (2014-2017, 2019, 2021)

### Recommendation

For users wanting **smoothest ride**: 80% BA + 20% F_HAdapted (Sharpe 1.26)
For users wanting **max returns**: stay 100% BA (CAGR 17.15%)
F_Balanced and F_Conservative variants do NOT improve mix — only F_HAdapted helps.

Note: Backtest treats them as a pseudo-portfolio (single NAV). In practice F-system uses futures (margin) and BA-system uses spot — separate capital pools, different tax/leverage profiles.

### Files
- `test_f_ba_mix.py` — driver
- `f_ba_mix_results.csv` — all 21 mix variants metrics
- `f_ba_mix_nav_traces.csv` — daily NAV traces for plotting

### Live integration (recommend_holistic.py)
F_HAdapted overlay status now printed daily by `recommend_holistic.py`. Each state maps to a target VN30F exposure (% of total NAV at 20% F-allocation):
- CRISIS: -20% NAV (max short)
- BEAR: -4% NAV (light short — counter-cyclical hedge while BA-cash)
- NEUTRAL: +14% NAV LONG
- BULL: +20% NAV LONG
- EX-BULL: +26% NAV LONG (leveraged)
Tested OK on BEAR (2026-03-30 → -4%) and BULL (2026-02-02 → +20%).
