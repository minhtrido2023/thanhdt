# 8L composite ranking — route-aware score (snapshot ~2026-05-29, market state NEUTRAL)
scored 140 tickers | weights encode: cheapness + engine/runway + cash-machine + moat + dislocation; banks=NPL-gate+PB/ROE; cyclicals=trough+dislocation+PB

  # tkr  route      verdict             engine           score     5F   liqB  components
  1 PTB  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       97.1             4  L1_cash+10 L1_value+40 L2_engine+22 L3_cash+10 L4_moat+5 L6_runway+1 dislocation+8 liq+4 liq_rising+2
  2 CTR  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        92.6            12  L1_cash+4 L1_value+37 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+5 liq+6
  3 NCT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        92.6 NARROW      1  L1_cash+7 L1_value+43 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+2
  4 FPT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        91.6 NARROW    442  L1_cash+1 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq+8 liq_rising+2
  5 NNC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        90.6 NARROW      2  L1_cash+7 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+8 dislocation+8
  6 SCS  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        90.1 NARROW      7  L1_cash+7 L1_value+34 L2_engine+22 L4_moat+15 L6_runway+5 dislocation+5 liq+4 liq_rising+2
  7 HAH  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       89.6            37  L1_cash+13 L1_value+32 L2_engine+22 L3_cash+10 L4_moat+10 L5_margin-12 L6_runway+8 dislocation+5 liq+6
  8 TCL  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        86.6             1  L1_cash+10 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+2 liq_rising+2
  9 SMC  CYCLICAL   TROUGH_BUY          nan               84.6             1  PB+6 cmdty_pctile+17 dislocation+15 liq_rising+2 regime+45
 10 VGC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        84.6 NARROW     34  L1_cash+4 L1_value+39 L2_engine+22 L4_moat+5 L6_runway+1 L8_hybrid+5 dislocation+5 liq+6 liq_rising+2
 11 FMC  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH◆   81.6             2  L1_cash+13 L1_value+43 L2_engine+3 L3_cash+10 L4_moat+5 L6_runway+8 dislocation+2 liq_rising+2
 12 LIX  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        78.1             1  L1_value+36 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq_rising+2
 13 PVT  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    75.1           151  L1_cash+10 L1_value+40 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+5 liq+8
 14 NKG  CYCLICAL   cmdty_CHEAP         nan               74.6            72  PB+10 cmdty_pctile+17 dislocation+8 liq+8 liq_rising+2 regime+30
 15 DHA  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        72.1 NARROW      1  L1_value+42 L2_engine+22 L4_moat+10 L6_runway+1 dislocation+2
 16 VNM  COMPOUNDER CHEAP_QUALITY       -                 71.9   WIDE    125  L1_cash+4 L1_value+43 L2_engine+6 L4_moat+12 L6_runway+1 dislocation+2 liq+8 moat5f_dur+0
 17 IDC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   70.0 NARROW     39  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+15 L8_pbfloor+2 dislocation+5 liq+6
 18 SIP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   70.0             4  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+2 liq+4 liq_rising+2
 19 HSG  CYCLICAL   cmdty_CHEAP         nan               68.6            43  PB+10 cmdty_pctile+17 dislocation+4 liq+6 liq_rising+2 regime+30
 20 GAS  COMPOUNDER CHEAP_QUALITY       -                 68.1            91  L1_cash+4 L1_value+36 L2_engine+6 L4_moat+10 L6_runway+1 dislocation+8 liq+8
 21 DMC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        68.1             0  L1_value+42 L2_engine+22 L4_moat+5 L6_runway+1 dislocation+2
 22 KTS  SUGAR      TREND_DIP_BUY       nan               66.8             0  PB+8 cmdty_trend+7 dip+10 regime+40 roe+2
 23 NTP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        66.6 NARROW      9  L1_cash+4 L1_value+38 L2_engine+22 L4_moat+10 L5_margin-12 L6_runway+5 liq+4
 24 PVP  COMPOUNDER CHEAP_QUALITY       nan               64.6            28  L1_cash+10 L1_value+37 L2_engine+6 L4_moat+5 L6_runway-2 dislocation+5 liq+6 liq_rising+2
 25 BWE  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    63.6 NARROW      3  L1_cash+7 L1_value+41 L2_engine+3 L4_moat+5 L6_runway+8 liq+2 liq_rising+2
 26 PGD  COMPOUNDER CHEAP_QUALITY       nan               62.6             0  L1_cash+7 L1_value+41 L2_engine+6 L4_moat+10 L6_runway-2 dislocation+5
 27 PHP  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    61.6            19  L1_cash+1 L1_value+39 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+2 liq+6 liq_rising+2
 28 HPG  CYCLICAL   cmdty_CHEAP         LOWROIC_GROWTH    61.6           440  PB+3 cmdty_pctile+17 dislocation+4 liq+8 regime+30
 29 PVS  COMPOUNDER CHEAP_QUALITY       nan               60.6            82  L1_cash+4 L1_value+41 L2_engine+6 L6_runway-2 dislocation+8 liq+8
 30 PGC  COMPOUNDER CHEAP_QUALITY       nan               59.6             1  L1_cash+10 L1_value+43 L2_engine+6 L4_moat+5 L6_runway-2 dislocation+2
 31 VOS  COMPOUNDER CHEAP_QUALITY       nan               59.1            13  L1_value+34 L2_engine+6 L4_moat+10 L6_runway-2 dislocation+8 liq+6 liq_rising+2
 32 GEG  POWER      PRE_INFLECTION_CHEA nan               59.0             3  PB+12 lifecycle+45 liq+2
 33 KHP  POWER      PRE_INFLECTION_CHEA nan               57.0             0  PB+12 lifecycle+45
 34 SLS  SUGAR      TREND_UP            nan               56.8 NARROW      0  PB+8 cmdty_trend+7 dip+6 regime+28 roe+8
 35 VNA  COMPOUNDER CHEAP_QUALITY       nan               56.1             0  L1_cash+7 L1_value+38 L2_engine+6 L4_moat+15 L5_margin-12 L6_runway-2 dislocation+8

## Prioritized TOP-20 (by 8L composite)
  PTB(97), CTR(93), NCT(93), FPT(92), NNC(91), SCS(90), HAH(90), TCL(87), SMC(85), VGC(85), FMC(82), LIX(78), PVT(75), NKG(75), DHA(72), VNM(72), IDC(70), SIP(70), HSG(69), GAS(68)

## TOP-20 by route
  BANK (0): 
  CYCLICAL (3): SMC(85), NKG(75), HSG(69)
  SUGAR (0): 
  COMPOUNDER (17): PTB(97), CTR(93), NCT(93), FPT(92), NNC(91), SCS(90), HAH(90), TCL(87), VGC(85), FMC(82), LIX(78), PVT(75), DHA(72), VNM(72), IDC(70), SIP(70), GAS(68)

Caveat: composite is a PRIORITIZATION aid, not a buy signal. NEUTRAL state (FA/quality edge strongest in CRISIS/BEAR per fa-horizon study). Liquidity small names hard to deploy. SPECIAL_SITUATION (DGC/PAT) carry event risk not in score.