# Integrated validation: bank FA sub-model in v11 BA-core book

daily signal rows 603,484 | 2014-01-02→2026-01-16
bank (8355) rows 209,426 | with bank_tier mapped 43,642

## FULL BA-core book (all sectors)
scenario                     N     mean   median    win% annualized
-------------------------------------------------------------------
GENERIC                 10,069    14.19%     8.24%    63.4%      70.0%
BANK-augmented           9,847    13.66%     7.21%    61.7%      66.9%

## BANK-only BA-core signals (where the change lands)
scenario                     N     mean   median    win% annualized
-------------------------------------------------------------------
GENERIC                  5,686    17.79%    11.68%    67.6%      92.5%
BANK-augmented           5,464    16.98%     9.79%    64.7%      87.2%

## BANK-only BA-core, OOS 2020+
scenario                     N     mean   median    win% annualized
-------------------------------------------------------------------
GENERIC                  5,122    17.96%    11.61%    67.3%      93.6%
BANK-augmented           4,922    16.95%     9.32%    64.0%      87.1%

## Composition change in bank signals (generic → bank-augmented)
group                          N   mean p3m    win%
---------------------------------------------------
ADDED by bank model          482     -2.18%   29.0%
REMOVED by bank model        704     10.44%   63.6%
kept in both               4,982     18.83%   68.1%

Read: if ADDED signals have higher mean/win than REMOVED, the bank model
improves selection (adds winners, drops losers among bank names).

## Quality channels for banks (where a quality ranker SHOULD help)
channel / scenario                   N   mean p3m    win%
---------------------------------------------------------
COMPOUNDER_BUY [GEN]             3,868      7.00%   58.3%
COMPOUNDER_BUY [BANK]            3,433      7.95%   59.5%

Quality-hold (A/B route) [GEN]  25,364      6.54%   57.6%
Quality-hold (A/B route) [BANK]  24,026      6.48%   57.1%

AVOID_faE (exclusion) [GEN]     21,753      5.96%   48.2%
AVOID_faE (exclusion) [BANK]    23,654      5.96%   48.5%

Read: for COMPOUNDER/quality-hold, HIGHER mean = bank model picks better
quality banks to hold. For AVOID_faE, LOWER mean = better blow-up exclusion.
