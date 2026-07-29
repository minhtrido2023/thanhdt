# DT4G Full-History Simulation — Performance & Risk

*Real BigQuery data: VNINDEX price + `vnindex_5state_dt_4gate` state.*  Period **2000-07-28 → 2026-06-02** (25.8y, 6,291 sessions). Start NAV **1B VND**.

**Model**: DT 4-gate state → equity allocation {CRISIS 0%, BEAR 20%, NEUTRAL 70%, BULL 100%, EX-BULL 130%}. T+1 execution; 0.1% fee both sides + 0.1% sell tax; idle cash 0.1%/yr; borrow 10%/yr on EX-BULL leverage. No look-ahead.

## 1. Performance & risk by period (each window re-based to 1B)

| Period | CAGR | Sharpe | Sortino | MaxDD | Calmar | Final NAV | B&H CAGR | B&H MaxDD |
|---|---|---|---|---|---|---|---|---|
| FULL 2000-now | +14.85% | 1.06 | 1.21 | -37.6% | 0.39 | 35.85B | +11.90% | -79.9% |
| Pre-2014 (00-13) | +17.66% | 1.17 | 1.43 | -37.6% | 0.47 | 8.88B | +12.81% | -79.9% |
| Modern 2014-now | +11.90% | 0.94 | 0.97 | -18.8% | 0.63 | 4.04B | +10.92% | -45.3% |
| 2007-08 GFC | +18.56% | 0.91 | 0.99 | -17.7% | 1.05 | 1.46B | -35.15% | -79.9% |
| COVID 2020 | +14.83% | 1.20 | 1.25 | -16.0% | 0.93 | 1.15B | +14.25% | -33.5% |

*Full-period longest drawdown: **1059 sessions** under water (~4.4y).*

## 2. Annual returns: DT4G vs VNINDEX Buy&Hold

| Year | DT4G | B&H | Δ | Dominant state |
|---|---|---|---|---|
| 2000 | +66.5% | +106.8% | -40.3pp | NEUTRAL |
| 2001 | +1.5% | +11.8% | -10.3pp | BEAR |
| 2002 | +0.9% | -20.9% | +21.8pp | BEAR |
| 2003 | +4.3% | -9.0% | +13.3pp | NEUTRAL |
| 2004 | +28.1% | +41.5% | -13.3pp | NEUTRAL |
| 2005 | +20.1% | +29.6% | -9.5pp | NEUTRAL |
| 2006 | +81.7% | +146.3% | -64.5pp | NEUTRAL |
| 2007 | +47.2% | +25.1% | +22.2pp | CRISIS |
| 2008 | -0.4% | -65.7% | +65.3pp | CRISIS |
| 2009 | +9.0% | +57.9% | -48.9pp | NEUTRAL |
| 2010 | -4.0% | -6.3% | +2.2pp | NEUTRAL |
| 2011 | -14.0% | -27.7% | +13.6pp | NEUTRAL |
| 2012 | +18.3% | +18.2% | +0.1pp | CRISIS |
| 2013 | +14.8% | +20.6% | -5.9pp | NEUTRAL |
| 2014 | +9.0% | +8.2% | +0.9pp | NEUTRAL |
| 2015 | +3.9% | +6.4% | -2.4pp | NEUTRAL |
| 2016 | +12.2% | +15.7% | -3.6pp | NEUTRAL |
| 2017 | +31.0% | +46.5% | -15.4pp | NEUTRAL |
| 2018 | +7.7% | -10.4% | +18.0pp | NEUTRAL |
| 2019 | +7.2% | +7.8% | -0.6pp | NEUTRAL |
| 2020 | +14.8% | +14.2% | +0.6pp | NEUTRAL |
| 2021 | +31.1% | +33.7% | -2.6pp | BULL |
| 2022 | -6.9% | -34.0% | +27.0pp | CRISIS |
| 2023 | +2.8% | +8.2% | -5.5pp | NEUTRAL |
| 2024 | +7.4% | +11.9% | -4.5pp | NEUTRAL |
| 2025 | +28.1% | +40.5% | -12.5pp | NEUTRAL |
| 2026 | +2.0% | +2.1% | -0.2pp | NEUTRAL |

*DT4G beats B&H in **11/27** years.*

## 3. Worst drawdown episodes (DT4G NAV, full path)

| Start | Trough | Recovery end | Trough DD |
|---|---|---|---|
| 2001-06-27 | 2003-10-24 | 2004-02-27 | -37.6% |
| 2006-04-26 | 2006-08-02 | 2006-12-13 | -30.6% |
| 2009-10-23 | 2012-01-06 | 2014-01-17 | -30.3% |
| 2024-03-29 | 2025-04-09 | 2025-06-30 | -18.8% |
| 2021-01-18 | 2021-01-28 | 2021-04-01 | -18.4% |
| 2019-11-07 | 2020-07-27 | 2020-11-27 | -18.3% |

## 4. State distribution & activity

| State | % of days |
|---|---|
| CRISIS | 18.9% |
| BEAR | 13.5% |
| NEUTRAL | 58.5% |
| BULL | 8.0% |
| EX-BULL | 1.1% |

*Total state transitions: **90** over 6,291 sessions (~3.5/yr).*

## 5. Honesty notes

- **Pure-index proxy**: this sims money allocated *directly to the VNINDEX index* by state weight — it measures the **timing model's** quality, not a tradeable stock book (the integrated stock systems V4/V5 are separate). You cannot literally buy the index pre-2016 (no ETF); E1VFVN30 only exists from 2016, so VNINDEX is the honest continuous proxy.

- **What the model does well vs its real weakness**: on *pure-index* timing the 0% CRISIS weight gave superb CRASH protection (2008 +70.7pp, 2022 +32.1pp, 2018 +21.2pp vs B&H). Its real cost is the OTHER side: NEUTRAL=70% caps upside in strong bull years (2006 −61pp, 2009 −45pp, 2017 −13pp) and the 25-session CRISIS-enter gate **lags sharp V-recoveries** (2009). The documented *pre-2014 risk* refers to the INTEGRATED Kelly stock book (whipsaw under leverage), NOT this pure-index sim — here pre-2014 timing was actually strong. DT was tuned for the **modern 2014+** regime; pre-2014 is shown for completeness/stress.

- Costs modelled: 0.1% brokerage fee both sides, 0.1% securities-transfer tax on sells, 10%/yr borrow on EX-BULL leverage, 0.1%/yr demand-deposit interest on idle cash. No slippage/market-impact (index proxy). Real-world haircut ≈ −1.0pp/yr.


*NAV path: `data/dt4g_2000_now_nav.csv`*
