# Paper-Trade 5 Systems — Full Backtest 2014-01-01 → 2026-05-15

*Generated: 2026-05-24*  •  *Init NAV: 50B per system*  •  *Engine: simulate_holistic_nav.simulate + LAGGED book + ensemble routing*

## Systems

| Tag | Name | Composition | State | ETF{state:frac} |
|---|---|---|---|---|
| V1 | V11 'Song Sinh'      | BAL (BA v11) + VN30 (BA on top-30)        | TQ34b | {3:0.7} |
| V2 | V12 'Am Duong'       | BAL + LAGGED_v12 (HL_3y, fixed 8%)        | TQ34b | {3:0.7} |
| V3 | V12 + LIVE Tinh Te   | BAL + LAGGED_v12                          | LIVE  | {3:0.7} |
| V4 | V12.1 Ensemble       | BAL + ensemble{VN30 \| LAGGED_v121 S2}    | TQ34b | {3:0.7} |
| V5 | V4 + Kelly Q2        | V4 with NEUTRAL ETF parking 100%          | TQ34b | {3:1.0} |

Ensemble signal: M1 (concentration) + M3r (rolling Top10 ADV momentum), AND-HOLD logic. M1==M3r flip set leg; otherwise keep last.

## A. Headline metrics by period

### FULL 2014-26

| System | CAGR | Sharpe | Sortino | MaxDD | Calmar | Wealth |
|---|---:|---:|---:|---:|---:|---:|
| V1 V11+TQ34b | +19.89% | +1.35 | +1.34 | -17.68% | +1.12 | 9.42x |
| V2 V12+TQ34b | +21.02% | +1.63 | +1.83 | -14.39% | +1.46 | 10.58x |
| V3 V12+LIVE | +20.41% | +1.58 | +1.82 | -16.21% | +1.26 | 9.94x |
| V4 V121_ENS | +23.55% | +1.66 | +1.77 | -15.72% | +1.50 | 13.66x |
| V5 V4+KellyQ2 | +25.71% | +1.70 | +1.87 | -16.93% | +1.52 | 16.93x |
| VNI B&H | +11.42% | +0.68 | +0.80 | -45.26% | +0.25 | 3.81x |

### OOS 2024-26

| System | CAGR | Sharpe | Sortino | MaxDD | Calmar | Wealth |
|---|---:|---:|---:|---:|---:|---:|
| V1 V11+TQ34b | +26.53% | +1.42 | +1.37 | -17.24% | +1.54 | 1.74x |
| V2 V12+TQ34b | +22.73% | +1.62 | +1.80 | -9.25% | +2.46 | 1.62x |
| V3 V12+LIVE | +21.76% | +1.56 | +1.77 | -9.10% | +2.39 | 1.59x |
| V4 V121_ENS | +29.75% | +1.64 | +1.77 | -15.36% | +1.94 | 1.85x |
| V5 V4+KellyQ2 | +36.16% | +1.84 | +2.08 | -14.94% | +2.42 | 2.08x |
| VNI B&H | +25.08% | +1.30 | +1.50 | -18.11% | +1.39 | 1.70x |

### IS 2014-19

| System | CAGR | Sharpe | Sortino | MaxDD | Calmar | Wealth |
|---|---:|---:|---:|---:|---:|---:|
| V1 V11+TQ34b | +13.37% | +1.32 | +1.64 | -17.68% | +0.76 | 2.12x |
| V2 V12+TQ34b | +13.84% | +1.43 | +1.73 | -14.39% | +0.96 | 2.17x |
| V3 V12+LIVE | +13.68% | +1.41 | +1.69 | -14.53% | +0.94 | 2.16x |
| V4 V121_ENS | +16.50% | +1.53 | +1.80 | -14.78% | +1.12 | 2.50x |
| V5 V4+KellyQ2 | +17.37% | +1.45 | +1.73 | -16.93% | +1.03 | 2.61x |
| VNI B&H | +11.35% | +0.76 | +0.98 | -27.08% | +0.42 | 1.90x |

### Mid 2018-23

| System | CAGR | Sharpe | Sortino | MaxDD | Calmar | Wealth |
|---|---:|---:|---:|---:|---:|---:|
| V1 V11+TQ34b | +20.14% | +1.28 | +1.23 | -16.46% | +1.22 | 3.00x |
| V2 V12+TQ34b | +23.72% | +1.67 | +1.87 | -12.11% | +1.96 | 3.58x |
| V3 V12+LIVE | +23.14% | +1.61 | +1.90 | -16.21% | +1.43 | 3.48x |
| V4 V121_ENS | +23.76% | +1.63 | +1.73 | -15.72% | +1.51 | 3.58x |
| V5 V4+KellyQ2 | +24.73% | +1.62 | +1.78 | -14.65% | +1.69 | 3.76x |
| VNI B&H | +2.13% | +0.21 | +0.24 | -45.26% | +0.05 | 1.13x |

### Bull 2020-21

| System | CAGR | Sharpe | Sortino | MaxDD | Calmar | Wealth |
|---|---:|---:|---:|---:|---:|---:|
| V1 V11+TQ34b | +59.92% | +2.19 | +2.21 | -16.46% | +3.64 | 2.55x |
| V2 V12+TQ34b | +60.50% | +2.70 | +3.19 | -12.11% | +5.00 | 2.57x |
| V3 V12+LIVE | +62.06% | +2.77 | +3.44 | -11.03% | +5.63 | 2.62x |
| V4 V121_ENS | +64.67% | +2.73 | +2.97 | -15.72% | +4.11 | 2.71x |
| V5 V4+KellyQ2 | +68.91% | +2.85 | +3.20 | -14.63% | +4.71 | 2.85x |
| VNI B&H | +24.55% | +1.11 | +1.15 | -33.51% | +0.73 | 1.55x |

### Bear 2022

| System | CAGR | Sharpe | Sortino | MaxDD | Calmar | Wealth |
|---|---:|---:|---:|---:|---:|---:|
| V1 V11+TQ34b | +0.61% | +0.34 | +0.24 | -1.00% | +0.61 | 1.01x |
| V2 V12+TQ34b | +4.63% | +0.52 | +0.44 | -9.34% | +0.50 | 1.05x |
| V3 V12+LIVE | -1.50% | -0.09 | -0.09 | -11.68% | -0.13 | 0.99x |
| V4 V121_ENS | +6.63% | +1.61 | +1.47 | -1.35% | +4.89 | 1.07x |
| V5 V4+KellyQ2 | +5.82% | +1.28 | +1.39 | -3.60% | +1.62 | 1.06x |
| VNI B&H | -34.39% | -1.58 | -2.02 | -40.34% | -0.85 | 0.66x |

### Recovery 2023

| System | CAGR | Sharpe | Sortino | MaxDD | Calmar | Wealth |
|---|---:|---:|---:|---:|---:|---:|
| V1 V11+TQ34b | -1.41% | -0.07 | -0.07 | -8.21% | -0.17 | 0.99x |
| V2 V12+TQ34b | +11.44% | +1.00 | +0.95 | -7.79% | +1.47 | 1.11x |
| V3 V12+LIVE | +11.95% | +1.03 | +1.02 | -7.68% | +1.56 | 1.12x |
| V4 V121_ENS | +2.06% | +0.24 | +0.23 | -8.00% | +0.26 | 1.02x |
| V5 V4+KellyQ2 | +2.97% | +0.29 | +0.29 | -8.58% | +0.35 | 1.03x |
| VNI B&H | +8.37% | +0.57 | +0.68 | -17.45% | +0.48 | 1.08x |

### Y2024

| System | CAGR | Sharpe | Sortino | MaxDD | Calmar | Wealth |
|---|---:|---:|---:|---:|---:|---:|
| V1 V11+TQ34b | +10.16% | +0.86 | +0.85 | -11.58% | +0.88 | 1.10x |
| V2 V12+TQ34b | +20.39% | +1.66 | +2.02 | -6.66% | +3.06 | 1.20x |
| V3 V12+LIVE | +22.65% | +1.75 | +2.17 | -6.56% | +3.46 | 1.23x |
| V4 V121_ENS | +8.46% | +0.69 | +0.72 | -10.96% | +0.77 | 1.08x |
| V5 V4+KellyQ2 | +10.72% | +0.83 | +0.91 | -10.18% | +1.05 | 1.11x |
| VNI B&H | +11.98% | +0.91 | +1.11 | -8.94% | +1.34 | 1.12x |

### Y2025

| System | CAGR | Sharpe | Sortino | MaxDD | Calmar | Wealth |
|---|---:|---:|---:|---:|---:|---:|
| V1 V11+TQ34b | +62.44% | +2.40 | +2.35 | -15.91% | +3.93 | 1.62x |
| V2 V12+TQ34b | +36.54% | +2.22 | +2.68 | -7.50% | +4.87 | 1.36x |
| V3 V12+LIVE | +32.77% | +2.04 | +2.49 | -8.87% | +3.69 | 1.33x |
| V4 V121_ENS | +76.99% | +3.20 | +3.82 | -7.49% | +10.28 | 1.76x |
| V5 V4+KellyQ2 | +84.90% | +3.24 | +3.97 | -8.08% | +10.50 | 1.84x |
| VNI B&H | +40.84% | +1.73 | +1.87 | -18.11% | +2.26 | 1.41x |

### 2026 YTD

| System | CAGR | Sharpe | Sortino | MaxDD | Calmar | Wealth |
|---|---:|---:|---:|---:|---:|---:|
| V1 V11+TQ34b | -4.35% | -0.12 | -0.11 | -14.58% | -0.30 | 0.98x |
| V2 V12+TQ34b | -2.00% | -0.08 | -0.07 | -9.25% | -0.22 | 0.99x |
| V3 V12+LIVE | -5.22% | -0.35 | -0.29 | -8.96% | -0.58 | 0.98x |
| V4 V121_ENS | -6.95% | -0.25 | -0.24 | -15.36% | -0.45 | 0.97x |
| V5 V4+KellyQ2 | +7.06% | +0.42 | +0.44 | -14.94% | +0.47 | 1.03x |
| VNI B&H | +25.28% | +1.11 | +1.41 | -16.38% | +1.54 | 1.09x |

## B. Annual returns (calendar years)

| Year | V1 V11+TQ34b | V2 V12+TQ34b | V3 V12+LIVE | V4 V121_ENS | V5 V4+KellyQ2 | VNI B&H |
|---|---:|---:|---:|---:|---:|---:|
| 2014 | +12.9% | +17.1% | +17.5% | +20.5% | +28.0% | +8.2% |
| 2015 | -4.5% | +0.6% | +0.5% | +1.3% | -1.8% | +6.4% |
| 2016 | +8.1% | +10.7% | +10.4% | +9.6% | +10.9% | +15.7% |
| 2017 | +48.6% | +36.6% | +34.5% | +47.9% | +49.5% | +46.5% |
| 2018 | +14.9% | +14.5% | +15.3% | +22.7% | +22.1% | -10.4% |
| 2019 | +2.9% | +4.4% | +4.4% | -0.9% | -1.3% | +7.8% |
| 2020 | +40.1% | +36.7% | +38.4% | +51.3% | +48.5% | +14.2% |
| 2021 | +77.9% | +86.3% | +87.3% | +74.4% | +86.5% | +33.7% |
| 2022 | +0.6% | +4.6% | -1.5% | +6.5% | +5.7% | -34.0% |
| 2023 | -1.4% | +11.3% | +11.8% | +2.0% | +2.9% | +8.2% |
| 2024 | +10.1% | +20.3% | +22.6% | +8.4% | +10.7% | +11.9% |
| 2025 | +62.0% | +36.3% | +32.5% | +76.4% | +84.2% | +40.5% |
| 2026 | -2.5% | -1.1% | -2.0% | -3.5% | +1.3% | +7.4% |

## C. State-conditional annualised return (TQ34b state, daily-mean * 252)

State 1=CRISIS, 2=BEAR, 3=NEUTRAL, 4=BULL, 5=EX-BULL.

| System | State 1 | State 2 | State 3 | State 4 | State 5 |
|---|---:|---:|---:|---:|---:|
| V1 V11+TQ34b | +7.0% | -1.9% | +20.9% | +38.7% | +56.4% |
| V2 V12+TQ34b | +10.3% | +7.5% | +21.3% | +46.0% | +22.2% |
| V3 V12+LIVE | +8.1% | +9.8% | +20.5% | +45.7% | +26.4% |
| V4 V121_ENS | +9.5% | +3.3% | +24.0% | +36.0% | +66.5% |
| V5 V4+KellyQ2 | +9.2% | +4.3% | +26.9% | +38.6% | +67.8% |
| VNI B&H | -1.3% | -7.7% | +18.2% | +22.0% | +37.7% |

Days in each state: S1=738d, S2=288d, S3=1553d, S4=325d, S5=178d

## D. V5 (Kelly Q2) vs V4 (baseline ensemble) — overlay validation

| Period | ΔCAGR | ΔSharpe | ΔDD | ΔCalmar | ΔWealth |
|---|---:|---:|---:|---:|---:|
| FULL 2014-26 | +2.16pp | +0.03 | -1.20pp | +0.02 | +3.27x |
| OOS 2024-26 | +6.40pp | +0.20 | +0.43pp | +0.48 | +0.22x |
| IS 2014-19 | +0.87pp | -0.08 | -2.15pp | -0.09 | +0.11x |
| Mid 2018-23 | +0.97pp | -0.01 | +1.07pp | +0.18 | +0.17x |

## E. Charts

- Equity curves (log): `data/papertrade_full_2014_2026_curves.png`
- Drawdown: `data/papertrade_full_2014_2026_drawdown.png`

## F. Source artifacts

- Daily NAV CSV: `data/full_5systems_2014_2026.csv` (columns: V1-V5 NAV + VNI + ensemble signal + states)
- Metrics CSV: `data/papertrade_full_2014_2026_metrics.csv`
- Run log: `data/full_5systems_run.log`
- Backtest engine: `simulate_holistic_nav.py` (canonical T+1 open exec, slippage 0.1% in / 0.15% out, tax 0.1%, ETF friction 0.15%, borrow 10%/yr, deposit 0%/yr)
- Builder script: `run_full_5systems_2014_2026.py`

## G. Caveats

1. **End date 2026-05-15**: signal pickle ba_v11_unified_12y_sig.pkl was generated up to that date. Live data extends to 2026-05-20.
2. **V1 ≡ V4 in early years if ensemble doesn't flip**: M1+M3r AND-HOLD signal needs ≥252 days history → first flip not until late 2014/early 2015.
3. **LAGGED book uses earnings_px / earnings_surprise_data pickles**: vintage 2026-05-20.
4. **All numbers backtested with knowledge of FA tier definitions, sector caps, overheat rules as they exist 2026-05-24** — no point-in-time fundamentals timeline for tier classification (well-known limitation).
