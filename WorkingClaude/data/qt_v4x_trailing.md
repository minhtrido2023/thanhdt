# QT v4.x — trailing-stop-from-peak vs HOLD (per-position, 5Y window)

events 621 | GROWTH+BOTH=122 VALUE_FEAR=499
Capture = realized / 5Y-peak (winners, peak>20%). Higher = harvests more of the run.

## ALL entries (N=621)
strategy       med ret     mean   win%  capture
-----------------------------------------------
HOLD_5Y         +14.1%   +44.2%    58%      40%
TS25             -6.1%   +10.3%    39%       2%
TS35             -4.1%   +18.0%    44%      13%
TS50             -0.8%   +25.8%    48%      31%
TS35_act20       +8.0%   +31.4%    56%      26%

## VALUE_FEAR (N=499)
strategy       med ret     mean   win%  capture
-----------------------------------------------
HOLD_5Y         +15.7%   +45.0%    59%      41%
TS25             -5.8%   +11.7%    39%       3%
TS35             -3.7%   +20.2%    46%      19%
TS50             +0.0%   +29.2%    50%      34%
TS35_act20      +12.6%   +34.0%    57%      33%

## GROWTH+BOTH (N=122)
strategy       med ret     mean   win%  capture
-----------------------------------------------
HOLD_5Y          +6.8%   +41.1%    56%      35%
TS25             -7.3%    +4.5%    38%      -0%
TS35             -7.7%    +9.4%    37%      -1%
TS50             -3.8%   +12.1%    41%       1%
TS35_act20       +0.1%   +20.7%    50%      10%

## Face validity — TS35 vs HOLD on key names (best entry per name)
ticker etype          peak     HOLD     TS35     TS25
VTP    VALUE_FEAR    +554%    +244%    +316%    +157%
MWG    VALUE_FEAR    +189%    +123%      -4%     +13%
VCS    VALUE_FEAR    +110%      +4%      +4%     +20%
DGC    VALUE_FEAR    +104%     -14%     +25%     +44%
VNM    VALUE_FEAR     +34%     -16%     -13%      -0%

Read: trailing-stop WINS if it keeps multibaggers (VTP/MWG TS≈peak) while
cutting round-trips (VNM/DGC TS>HOLD). Best stop = highest mean+capture vs HOLD.
