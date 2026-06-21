# Integrated test: 2 FA quick wins (v11 BA-core, realized profit_3M)

daily rows 603,484 | base_tier cover 92% | ew5 cover 92% | redflag cover 99%

## FULL BA-core book — annualized = 4 compounded 3M trades
scenario                         N     mean   median    win%  annualiz
----------------------------------------------------------------------
BASELINE 7-axis             10,069    14.19%     8.24%    63.4%      70.0%
EW5 (drop health+val)       10,079    14.64%     7.75%    62.3%      72.7%
BASE + redflag≥3 excl        9,434    14.07%     8.02%    63.0%      69.3%

## FULL BA-core book — OOS 2020+
scenario                         N     mean   median    win%  annualiz
----------------------------------------------------------------------
BASELINE 7-axis              8,937    14.93%     8.83%    64.4%      74.5%
EW5                          8,942    15.42%     8.33%    63.3%      77.5%
BASE + redflag≥3 excl        8,339    14.82%     8.53%    64.0%      73.8%

## EW5 composition change (baseline → EW5)
group                          N   mean p3m    win%
---------------------------------------------------
ADDED by EW5               1,566     11.69%   54.9%
REMOVED by EW5             1,556      8.77%   62.0%
kept                       8,513     15.18%   63.6%

## redflag≥3 exclusion — profile of BA-core signals it removes
  removed 635 signals | mean p3m +16.03% | win 68.3% | crash<-20%: 6.3%
  (kept signals: mean +14.07% | win 63.0% | crash<-20%: 8.5%)
  → exclusion HELPS if removed signals are worse (lower mean/win, higher crash) than kept.
