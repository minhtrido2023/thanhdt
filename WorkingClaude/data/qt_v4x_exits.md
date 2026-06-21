# QT v4.x — archetype-conditional EXIT test (per-position, 5Y window)

events 621 | GROWTH+BOTH=122 VALUE_FEAR=499
Capture = realized exit return / 5Y peak (winners only, peak>20%). Higher = harvests more of the run.

## ALL entries  (N=621)
strategy      med ret     mean   win%  med capture
--------------------------------------------------
HOLD_5Y        +14.1%   +44.2%    58%          40%
OVERVALUED      +0.5%   +18.0%    51%          21%
DECEL           -0.3%    +1.6%    44%           0%
QTV4_ANY        -0.6%   +12.4%    46%           5%
ARCHETYPE       +1.0%   +16.3%    51%          17%

## VALUE_FEAR entries (expect OVERVALUED best)  (N=499)
strategy      med ret     mean   win%  med capture
--------------------------------------------------
HOLD_5Y        +15.7%   +45.0%    59%          41%
OVERVALUED      +1.3%   +18.9%    52%          24%
DECEL           -0.3%    +0.6%    43%           0%
QTV4_ANY        -0.6%   +12.8%    45%           4%
ARCHETYPE       +1.3%   +18.9%    52%          24%

## GROWTH+BOTH entries (expect DECEL > OVERVALUED)  (N=122)
strategy      med ret     mean   win%  med capture
--------------------------------------------------
HOLD_5Y         +6.8%   +41.1%    56%          35%
OVERVALUED      -0.7%   +14.4%    48%           7%
DECEL           -0.3%    +5.6%    48%           7%
QTV4_ANY        -0.7%   +10.4%    48%           8%
ARCHETYPE       -0.3%    +5.6%    48%           7%

## Median hold days by exit (GROWTH+BOTH)
  OVERVALUED 256d | DECEL 126d | ARCHETYPE 126d

Read: for GROWTH+BOTH, if DECEL median ret/capture > OVERVALUED, exiting on
deceleration (not on high valuation) harvests more — confirms user's thesis.
ARCHETYPE (value→OVR, growth→DECEL) vs QTV4_ANY shows if conditional beats one-size.
