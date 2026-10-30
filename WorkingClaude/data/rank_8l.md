# 8L composite ranking — route-aware score (snapshot ~2026-05-29, market state NEUTRAL)
scored 140 tickers | weights encode: cheapness + engine/runway + cash-machine + moat + dislocation; banks=NPL-gate+PB/ROE; cyclicals=trough+dislocation+PB

  # tkr  route      verdict             engine           score     5F   liqB  components
  1 HAH  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆      104.7            42  L1_cash+13 L1_value+35 L2_engine+22 L3_cash+10 L4_moat+10 L6_runway+8 dislocation+5 liq+6
  2 CTR  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        92.7            13  L1_cash+4 L1_value+37 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+5 liq+6
  3 NCT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        92.7 NARROW      1  L1_cash+7 L1_value+43 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+2
  4 FPT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        91.7 NARROW    385  L1_cash+1 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq+8 liq_rising+2
  5 PTB  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       91.7             4  L1_cash+4 L1_value+40 L2_engine+22 L3_cash+10 L4_moat+5 L6_runway+1 dislocation+8 liq+4 liq_rising+2
  6 NNC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        90.7 NARROW      2  L1_cash+7 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+8 dislocation+8
  7 SCS  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        90.2 NARROW      7  L1_cash+7 L1_value+34 L2_engine+22 L4_moat+15 L6_runway+5 dislocation+5 liq+4 liq_rising+2
  8 SMC  CYCLICAL   TROUGH_BUY          nan               88.6             1  PB+10 cmdty_pctile+17 dislocation+15 liq_rising+2 regime+45
  9 VGC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        82.2 NARROW     35  L1_cash+4 L1_value+38 L2_engine+22 L4_moat+5 L6_runway+1 L8_hybrid+3 dislocation+5 liq+6 liq_rising+2
 10 FMC  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH◆   81.7             1  L1_cash+13 L1_value+43 L2_engine+3 L3_cash+10 L4_moat+5 L6_runway+8 dislocation+2 liq_rising+2
 11 LIX  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        77.7             1  L1_value+35 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq_rising+2
 12 PVT  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    76.7           162  L1_cash+10 L1_value+40 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+5 liq+8 liq_rising+2
 13 VNM  COMPOUNDER CHEAP_QUALITY       -                 75.5   WIDE    135  L1_cash+4 L1_value+43 L2_engine+6 L4_moat+12 L6_runway+1 dislocation+5 liq+8 moat5f_dur+1
 14 NKG  CYCLICAL   cmdty_CHEAP         nan               74.6            57  PB+10 cmdty_pctile+17 dislocation+8 liq+8 liq_rising+2 regime+30
 15 DHA  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        72.2 NARROW      1  L1_value+42 L2_engine+22 L4_moat+10 L6_runway+1 dislocation+2
 16 SIP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   71.0             4  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+5 liq+4
 17 TCL  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        70.7             1  L1_value+34 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+2 liq_rising+2
 18 IDC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   70.0 NARROW     42  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+15 L8_pbfloor+2 dislocation+5 liq+6
 19 NTP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        69.2 NARROW      8  L1_cash+4 L1_value+38 L2_engine+22 L4_moat+10 L5_margin-12 L6_runway+5 dislocation+2 liq+4
 20 HPG  CYCLICAL   cmdty_CHEAP         LOWROIC_GROWTH    68.6           390  PB+6 cmdty_pctile+17 dislocation+8 liq+8 regime+30
 21 HSG  CYCLICAL   cmdty_CHEAP         nan               68.6            38  PB+10 cmdty_pctile+17 dislocation+4 liq+6 liq_rising+2 regime+30
 22 KTS  SUGAR      TREND_DIP_BUY       nan               66.8             0  PB+8 cmdty_trend+7 dip+10 regime+40 roe+2
 23 DMC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        65.2             0  L1_value+42 L2_engine+22 L4_moat+5 L6_runway+1
 24 BWE  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    64.7 NARROW      3  L1_cash+7 L1_value+42 L2_engine+3 L4_moat+5 L6_runway+8 liq+2 liq_rising+2
 25 PVP  COMPOUNDER CHEAP_QUALITY       nan               64.7            28  L1_cash+10 L1_value+37 L2_engine+6 L4_moat+5 L6_runway-2 dislocation+5 liq+6 liq_rising+2
 26 PGD  COMPOUNDER CHEAP_QUALITY       nan               62.7             0  L1_cash+7 L1_value+41 L2_engine+6 L4_moat+10 L6_runway-2 dislocation+5
 27 PGC  COMPOUNDER CHEAP_QUALITY       nan               61.7             1  L1_cash+10 L1_value+43 L2_engine+6 L4_moat+5 L6_runway-2 dislocation+2 liq_rising+2
 28 PHP  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    61.7            17  L1_cash+1 L1_value+39 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+2 liq+6 liq_rising+2
 29 PVS  COMPOUNDER CHEAP_QUALITY       nan               60.7            88  L1_cash+4 L1_value+41 L2_engine+6 L6_runway-2 dislocation+8 liq+8
 30 PLX  COMPOUNDER CHEAP_QUALITY       nan               60.7           129  L1_cash+7 L1_value+38 L2_engine+6 L6_runway-2 dislocation+8 liq+8
 31 VOS  COMPOUNDER CHEAP_QUALITY       nan               59.2            14  L1_value+34 L2_engine+6 L4_moat+10 L6_runway-2 dislocation+8 liq+6 liq_rising+2
 32 GEG  POWER      PRE_INFLECTION_CHEA nan               59.0             3  PB+12 lifecycle+45 liq+2
 33 SLS  SUGAR      TREND_UP            nan               58.8 NARROW      0  PB+8 cmdty_trend+7 dip+6 liq_rising+2 regime+28 roe+8
 34 KHP  POWER      PRE_INFLECTION_CHEA nan               57.0             0  PB+12 lifecycle+45
 35 VNA  COMPOUNDER CHEAP_QUALITY       nan               55.7             0  L1_cash+7 L1_value+38 L2_engine+6 L4_moat+15 L5_margin-12 L6_runway-2 dislocation+8

## Prioritized TOP-20 (by 8L composite)
  HAH(105), CTR(93), NCT(93), FPT(92), PTB(92), NNC(91), SCS(90), SMC(89), VGC(82), FMC(82), LIX(78), PVT(77), VNM(76), NKG(75), DHA(72), SIP(71), TCL(71), IDC(70), NTP(69), HPG(69)

## TOP-20 by route
  BANK (0): 
  CYCLICAL (3): SMC(89), NKG(75), HPG(69)
  SUGAR (0): 
  COMPOUNDER (17): HAH(105), CTR(93), NCT(93), FPT(92), PTB(92), NNC(91), SCS(90), VGC(82), FMC(82), LIX(78), PVT(77), VNM(76), DHA(72), SIP(71), TCL(71), IDC(70), NTP(69)

Caveat: composite is a PRIORITIZATION aid, not a buy signal. NEUTRAL state (FA/quality edge strongest in CRISIS/BEAR per fa-horizon study). Liquidity small names hard to deploy. SPECIAL_SITUATION (DGC/PAT) carry event risk not in score.