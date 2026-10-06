# 8L composite ranking — route-aware score (snapshot ~2026-05-29, market state NEUTRAL)
scored 140 tickers | weights encode: cheapness + engine/runway + cash-machine + moat + dislocation; banks=NPL-gate+PB/ROE; cyclicals=trough+dislocation+PB

  # tkr  route      verdict             engine           score     5F   liqB  components
  1 HAH  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆      108.6            54  L1_cash+13 L1_value+34 L2_engine+22 L3_cash+10 L4_moat+10 L6_runway+8 dislocation+5 liq+8 liq_rising+2
  2 NNC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        94.6 NARROW      1  L1_cash+10 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+8 dislocation+8
  3 CTR  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        92.6            18  L1_cash+4 L1_value+36 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+5 liq+6
  4 FPT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        92.6 NARROW    344  L1_cash+4 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq+8
  5 HSG  CYCLICAL   TROUGH_BUY          nan               92.6            21  PB+10 cmdty_pctile+17 dislocation+15 liq+6 regime+45
  6 NKG  CYCLICAL   TROUGH_BUY          nan               92.6            16  PB+10 cmdty_pctile+17 dislocation+15 liq+6 regime+45
  7 PTB  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       90.1             3  L1_cash+4 L1_value+40 L2_engine+22 L3_cash+10 L4_moat+5 L6_runway+1 dislocation+8 liq+2 liq_rising+2
  8 SMC  CYCLICAL   TROUGH_BUY          nan               86.6             1  PB+10 cmdty_pctile+17 dislocation+15 regime+45
  9 NCT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        86.1 NARROW      1  L1_value+43 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+2
 10 SCS  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        86.1 NARROW      4  L1_cash+7 L1_value+34 L2_engine+22 L4_moat+15 L6_runway+5 dislocation+5 liq+2
 11 FMC  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH◆   84.1             0  L1_cash+13 L1_value+42 L2_engine+3 L3_cash+10 L4_moat+5 L6_runway+8 dislocation+5 liq_rising+2
 12 VNM  COMPOUNDER CHEAP_QUALITY       -                 72.4   WIDE    195  L1_cash+4 L1_value+43 L2_engine+6 L4_moat+12 L6_runway+1 dislocation+2 liq+8 moat5f_dur+0
 13 TCL  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        71.6             0  L1_value+34 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+2 liq_rising+2
 14 BMP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        70.6 NARROW     10  L1_cash+1 L1_value+32 L2_engine+22 L4_moat+15 L5_margin-12 L6_runway+5 dislocation+5 liq+6
 15 NTP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        70.1 NARROW     11  L1_value+39 L2_engine+22 L4_moat+10 L5_margin-12 L6_runway+5 dislocation+2 liq+6 liq_rising+2
 16 IDC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   70.0 NARROW     46  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+15 L8_pbfloor+2 dislocation+5 liq+6
 17 NTC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   69.0 NARROW      1  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+5 liq_rising+2
 18 SIP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   69.0             4  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+5 liq+2
 19 DMC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        68.6             0  L1_cash+1 L1_value+42 L2_engine+22 L4_moat+5 L6_runway+1 dislocation+2
 20 LIX  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        68.1             0  L1_value+27 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8
 21 DHA  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        67.6 NARROW      1  L1_value+36 L2_engine+22 L4_moat+10 L6_runway+1 dislocation+2
 22 PVT  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    67.6           201  L1_cash+10 L1_value+34 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+2 liq+8 liq_rising+2
 23 KTS  SUGAR      TREND_DIP_BUY       nan               66.8             0  PB+8 cmdty_trend+7 dip+10 regime+40 roe+2
 24 HPG  CYCLICAL   cmdty_CHEAP         LOWROIC_GROWTH    65.6           396  PB+3 cmdty_pctile+17 dislocation+8 liq+8 regime+30
 25 BWE  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    64.1 NARROW      2  L1_cash+7 L1_value+41 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+2 liq+2
 26 PVS  COMPOUNDER CHEAP_QUALITY       nan               59.6           134  L1_cash+4 L1_value+40 L2_engine+6 L6_runway-2 dislocation+5 liq+8 liq_rising+2
 27 PGC  COMPOUNDER CHEAP_QUALITY       nan               59.1             2  L1_cash+10 L1_value+42 L2_engine+6 L4_moat+5 L6_runway-2 liq_rising+2
 28 GEG  POWER      PRE_INFLECTION_CHEA nan               59.0             3  PB+12 lifecycle+45 liq+2
 29 OIL  COMPOUNDER CHEAP_QUALITY       nan               58.1            40  L1_cash+7 L1_value+35 L2_engine+6 L6_runway-2 dislocation+8 liq+6 liq_rising+2
 30 PVD  COMPOUNDER CHEAP_QUALITY       nan               57.1           106  L1_cash+4 L1_value+35 L2_engine+6 L6_runway-2 dislocation+8 liq+8 liq_rising+2
 31 KHP  POWER      PRE_INFLECTION_CHEA nan               57.0             0  PB+12 lifecycle+45
 32 VNA  COMPOUNDER CHEAP_QUALITY       nan               56.1             0  L1_cash+7 L1_value+38 L2_engine+6 L4_moat+15 L5_margin-12 L6_runway-2 dislocation+8
 33 PVC  COMPOUNDER CHEAP_QUALITY       nan               54.1            10  L1_value+38 L2_engine+6 L6_runway-2 dislocation+8 liq+6 liq_rising+2
 34 DTD  COMPOUNDER VALUE_TRAP          COMPOUNDER ASSE   53.0 NARROW      1  L2_engine+22 L4_moat+10 L6_runway+5 L8_backlog+10 L8_pbfloor+8 L8_trap-10 dislocation+8
 35 SLS  SUGAR      TREND_UP            nan               52.8 NARROW      0  PB+8 cmdty_trend+7 dip+2 regime+28 roe+8

## Prioritized TOP-20 (by 8L composite)
  HAH(109), NNC(95), CTR(93), FPT(93), HSG(93), NKG(93), PTB(90), SMC(87), NCT(86), SCS(86), FMC(84), VNM(72), TCL(72), BMP(71), NTP(70), IDC(70), NTC(69), SIP(69), DMC(69), LIX(68)

## TOP-20 by route
  BANK (0): 
  CYCLICAL (3): HSG(93), NKG(93), SMC(87)
  SUGAR (0): 
  COMPOUNDER (17): HAH(109), NNC(95), CTR(93), FPT(93), PTB(90), NCT(86), SCS(86), FMC(84), VNM(72), TCL(72), BMP(71), NTP(70), IDC(70), NTC(69), SIP(69), DMC(69), LIX(68)

Caveat: composite is a PRIORITIZATION aid, not a buy signal. NEUTRAL state (FA/quality edge strongest in CRISIS/BEAR per fa-horizon study). Liquidity small names hard to deploy. SPECIAL_SITUATION (DGC/PAT) carry event risk not in score.