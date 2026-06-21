# Rubber cyclical prototype — commodity regime × stock dislocation

rubber tickers available: ['DPR', 'DRI', 'GVR', 'HRC', 'PHR', 'TRC']
rubber price range: 1.20-6.26 USD/kg, latest 2.39 (2026-03-01), good=True pctile5y=0.95

## Forward return by rubber regime × stock dislocation (all rubber stocks pooled)
bucket                        N   1Y med  1Ywin   2Y med  2Ywin
----------------------------------------------------------------
rubber GOOD + stock DEEP dd<-25%   96       -1%     44%      +20%     52%
rubber GOOD + stock normal  412       -0%     45%       -1%     38%
rubber WEAK + stock DEEP dd<-25%  179      +37%     79%      +69%     87%
rubber WEAK + stock normal  329      +11%     57%      +23%     65%

## rubber GOOD × deep-dd × market state
state                         N   1Y med  1Ywin   2Y med  2Ywin
CRISIS                       13      -31%     23%       -3%     38%
NEUTRAL                      14      +27%     43%     +116%     48%
ALL states                   96       -1%     44%      +20%     52%

## Baselines
  ALL obs                    1016       +7%     55%      +21%     56%
  rubber GOOD (any dd)        508       -0%     45%       +2%     41%
  rubber WEAK (any dd)        508      +18%     65%      +37%     73%

## Face validity — DRI near the April-2025 dislocation
  date          Close   dd52    PB  rubber  goodstate       f1y
  2024-09-30    11210   -18%  1.81    2.65  TrueNEUTRAL     +1%
  2024-10-31    11120   -18%  1.54    2.63  TrueNEUTRAL     +5%
  2024-11-29    12150   -11%  1.68    2.29  TrueNEUTRAL     +7%
  2024-12-31    12150   -11%  1.68    2.38  TrueNEUTRAL    +12%
  2025-01-24    12150   -11%  1.68    2.37  TrueNEUTRAL     +3%
  2025-02-28    15520    -4%  2.00    2.41  TrueNEUTRAL     -9%
  2025-03-31    13600   -16%  1.76    2.36  TrueBULL        -9%
  2025-04-29    10800   -33%  1.23    2.13  TrueBULL       +31%
  2025-05-30    11380   -29%  1.29    2.19  TrueNEUTRAL   +nan%
  2025-06-30    12730   -21%  1.45    2.16  TrueNEUTRAL   +nan%
  2025-07-31    13000   -19%  1.53    2.23  TrueNEUTRAL   +nan%

Read: if 'rubber GOOD × deep-dd' >> baselines (esp. in CRISIS/BEAR), the cyclical
framework works — buy quality cyclical when commodity strong + price dislocated.
