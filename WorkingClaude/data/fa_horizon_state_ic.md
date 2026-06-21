# FA edge by HORIZON × market state (DT5G)

rows 10,955 | 2014-04-29→2026-05-08
  3M: 10,332 with fwd return
  6M: 9,999 with fwd return
  1Y: 9,312 with fwd return
  2Y: 8,043 with fwd return

## (A) FA composite IC by horizon (overall) — does edge rise with time held?
factor               3M       6M       1Y       2Y
--------------------------------------------------
total(7ax)      +0.0606  +0.0703  +0.0591  +0.1133
EW5(5ax)        +0.0658  +0.0735  +0.0607  +0.1145
quality         +0.0278  +0.0275  +0.0133  +0.0446

Hypothesis ✓ if IC increases left→right (FA predicts long horizon better than short).

## (B1) RANKING — total_score IC by DT5G state × horizon
(can FA still rank winners inside each regime?)
state            3M       6M       1Y       2Y       N
------------------------------------------------------------
CRISIS      +0.1166  +0.1342  +0.1096  +0.1412   2,042
BEAR        +0.0666  +0.0344  +0.0334  +0.2086   1,005
NEUTRAL     +0.0489  +0.0556  +0.0505  +0.0551   5,399
BULL        +0.0705  +0.0767  +0.0873  +0.1584   2,229
EX-BULL     -0.0576  +0.0022  -0.3001  +0.0945     280

## (B2) ABSOLUTE — does the BEST FA make money, or just fall less?
median forward return: TOP quintile (best FA) vs BOTTOM quintile, by state

### Horizon 3M
state       TOP med  BOT med   spread TOP win%      N
CRISIS        -2.5%    -6.9%    +4.4%      43%  2,042
BEAR          -4.9%    -6.0%    +1.1%      36%  1,005
NEUTRAL       +1.0%    -0.8%    +1.7%      52%  4,778
BULL          +5.2%    -1.2%    +6.3%      64%  2,227
EX-BULL       +7.5%   +18.4%   -11.0%      75%    280

### Horizon 6M
state       TOP med  BOT med   spread TOP win%      N
CRISIS        +0.9%    -9.0%    +9.9%      51%  2,042
BEAR          +1.6%    -4.6%    +6.2%      54%  1,005
NEUTRAL       +1.7%    -0.5%    +2.1%      53%  4,690
BULL         +10.9%    +5.5%    +5.3%      70%  1,982
EX-BULL      +26.3%   +29.2%    -2.9%      84%    280

### Horizon 1Y
state       TOP med  BOT med   spread TOP win%      N
CRISIS        -3.9%   -11.9%    +8.0%      46%  2,042
BEAR         +10.8%    +5.9%    +4.9%      62%  1,005
NEUTRAL       +6.9%    +2.6%    +4.3%      59%  4,008
BULL         +11.6%    -1.0%   +12.6%      61%  1,977
EX-BULL      +51.7%  +140.9%   -89.1%      89%    280

### Horizon 2Y
state       TOP med  BOT med   spread TOP win%      N
CRISIS        +7.5%    -5.5%   +13.0%      59%  1,709
BEAR         +28.7%    -1.3%   +30.1%      79%  1,005
NEUTRAL      +18.2%    +6.1%   +12.1%      65%  3,392
BULL          +7.2%   -18.2%   +25.4%      59%  1,657
EX-BULL      +12.2%    +0.2%   +12.0%      59%    280

Read: spread>0 = FA ranks correctly in that regime (resilience). TOP med<0 with
TOP win%<50 = even best FA loses money → 'FA can't save you' regime (crisis).
