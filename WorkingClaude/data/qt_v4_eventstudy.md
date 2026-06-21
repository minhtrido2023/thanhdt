# QT v4 (Buffett) as a FILTER — per-signal event study

Entry events (fresh triggers) 628 | tickers 62 | 2016-11-01→2026-05-12
Path mix: VALUE=421, GARP=183, BOTH=24

## (1)(2) Forward outcome of picks — hold to fixed horizon
horizon      N     med    mean   win% vsVNI med beatVNI%
--------------------------------------------------------
3M         582   +2.0%   +3.8%    56%     -1.8%      45%
6M         551   +3.0%   +6.8%    56%     -3.5%      42%
1Y         487   +1.0%  +15.7%    52%     -5.1%      44%
2Y         404  +11.2%  +29.7%    58%     -1.6%      49%
3Y         302  +30.4%  +52.0%    65%     +7.2%      54%

## By entry path (forward 1Y / 2Y median, beat-VNI%)
  VALUE  N= 421  1Y med=  +4.8% (beat 37%)  2Y med= +15.0% (beat 34%)
  GARP   N= 183  1Y med=  -8.9% (beat 27%)  2Y med=  +0.9% (beat 24%)
  BOTH   N=  24  1Y med=  +0.6% (beat 33%)  2Y med=  +2.4% (beat 33%)

## (3) WHEN TO EXIT — QT v4 rule-based exit vs holding to fixed horizon
Rule-based exits: 410/628 closed; 218 STILL_OPEN at data end
  rule exit:  median ret +9.3%  mean +27.0%  median hold 274d  win 57%
  hold 3M :  median ret +2.0%  mean +3.8%  win 56%  (N=582)
  hold 6M :  median ret +3.0%  mean +6.8%  win 56%  (N=551)
  hold 1Y :  median ret +1.0%  mean +15.7%  win 52%  (N=487)
  hold 2Y :  median ret +11.2%  mean +29.7%  win 58%  (N=404)
  hold 3Y :  median ret +30.4%  mean +52.0%  win 65%  (N=302)

Exit reason breakdown:
reason              N  med ret    mean  med hold   win%
FA_DEGRADE        217    -2.3%   +7.5%      224d    44%
GROWTH_BROKEN      77    -3.0%   -1.0%      455d    34%
OVERVALUED        116   +81.4%  +82.2%      561d    96%
STILL_OPEN        218    -4.2%  +29.9%      598d    41%

Read: if 'rule exit' mean/win ≈ or > best fixed-horizon hold, the exit rules add value.
If holding longer (2Y/3Y) beats rule exit, the rules exit too early (cut compounders).
