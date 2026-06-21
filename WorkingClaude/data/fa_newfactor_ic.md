# New-factor IC test (direction #2: dilution / accruals / fraud)

merged rows w/ profit_3M = 11,206 | IS=3,189 OOS=8,017
expected sign: all three NEGATIVE (higher issuance/accruals/redflags → worse)

## Standalone IC vs profit_3M
factor            IS_IC   OOS_IC   ALL_IC  cover%
-------------------------------------------------
net_issuance    +0.0441  -0.0510  -0.0311   98.7%
accruals        -0.0151  -0.0693  -0.0534   99.2%
redflag_cnt     -0.0639  -0.0321  -0.0405  100.0%

## Incremental IC after controlling for EW5 composite (partial rank-corr)
(this is the real test: does the factor predict BEYOND existing axes?)
factor          partial_IS  partial_OOS  partial_ALL
----------------------------------------------------
net_issuance       +0.0426      -0.0540      -0.0340
accruals           +0.0418      -0.0380      -0.0152
redflag_cnt        -0.0232      +0.0020      -0.0041

## Combined: EW5 vs EW5 + best new factors (sign-corrected, equal weight)
  EW5        IS=+0.1329  OOS=+0.0864  ALL=+0.0998
  EW5+new3   IS=+0.0830  OOS=+0.0723  ALL=+0.0762

## Tail-risk test (correct metric for a blow-up SCREEN, not a ranker)
For each factor: bucket rows, report crash prob P(profit_3M<-20%), 5th pctile, median.
A valid exclusion screen → worst bucket has materially higher crash prob / fatter left tail.

### net_issuance
bucket            N   crash%       p5   median
Q1 (low)      2,212     8.1%   -24.0%    0.00%
Q2            2,211    21.7%   -39.1%   -4.23%
Q3            2,211    10.6%   -27.5%   -0.25%
Q4            2,211    11.7%   -29.5%   -0.08%
Q5 (high)     2,211    16.6%   -35.6%   -2.44%

### accruals
bucket            N   crash%       p5   median
Q1 (low)      2,223     6.7%   -22.6%    1.75%
Q2            2,222    17.6%   -37.6%    0.40%
Q3            2,222    12.3%   -29.2%   -3.06%
Q4            2,222    20.2%   -39.0%   -4.14%
Q5 (high)     2,222    11.2%   -28.5%    0.00%

### redflag_cnt
bucket            N   crash%       p5   median
flags=0       3,038    11.8%   -29.8%   -0.26%
flags=1       4,217    13.2%   -32.9%   -0.76%
flags=2       2,801    15.2%   -33.0%   -1.74%
flags=3         992    16.3%   -36.7%   -2.86%
flags=4         158    18.4%   -43.4%   -4.24%
