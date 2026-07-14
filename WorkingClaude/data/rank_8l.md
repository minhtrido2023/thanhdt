# 8L composite ranking — route-aware score (snapshot ~2026-05-29, market state NEUTRAL)
scored 137 tickers | weights encode: cheapness + engine/runway + cash-machine + moat + dislocation; banks=NPL-gate+PB/ROE; cyclicals=trough+dislocation+PB

  # tkr  route      verdict             engine           score     5F   liqB  components
  1 HAH  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆      105.0            32  L1_cash+13 L1_value+36 L2_engine+22 L3_cash+10 L4_moat+10 L6_runway+8 dislocation+5 liq+6
  2 NCT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        94.5 NARROW      2  L1_cash+7 L1_value+43 L2_engine+22 L4_moat+15 L6_runway+8 liq+2 liq_rising+2
  3 NNC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        93.5 NARROW      1  L1_cash+10 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+8 dislocation+8
  4 SCS  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        93.0 NARROW      6  L1_cash+7 L1_value+40 L2_engine+22 L4_moat+15 L6_runway+5 dislocation+5 liq+4
  5 CTG  BANK       CLEAN               nan               93.0             0  CAR+3 coverage+10 gate+40 npl+12 npl_trend+8 pb_vs_roe+10 roe+10
  6 FPT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        92.0 NARROW    594  L1_cash+4 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq+8
  7 ACB  BANK       CLEAN               nan               91.0             0  CAR+5 coverage+8 gate+40 npl+15 npl_trend+8 pb_vs_roe+7 roe+8
  8 NKG  CYCLICAL   TROUGH_BUY          nan               90.6            22  PB+10 cmdty_pctile+15 dislocation+15 liq+6 regime+45
  9 CTR  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        89.5            21  L1_cash+7 L1_value+31 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+5 liq+6
 10 PTB  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       89.0             2  L1_cash+10 L1_value+38 L2_engine+22 L3_cash+10 L4_moat+5 L6_runway+1 dislocation+5 liq+2
 11 HSG  CYCLICAL   TROUGH_BUY          nan               87.6            32  PB+10 cmdty_pctile+15 dislocation+12 liq+6 regime+45
 12 TCL  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        87.5             0  L1_cash+10 L1_value+43 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+2
 13 MBB  BANK       CLEAN               nan               87.0             0  CAR+5 coverage+5 gate+40 npl+12 npl_trend+8 pb_vs_roe+7 roe+10
 14 VCB  BANK       CLEAN               nan               84.0             0  CAR+5 coverage+10 gate+40 npl+15 npl_trend+8 pb_vs_roe+1 roe+5
 15 TCB  BANK       CLEAN               nan               80.0             0  CAR+6 coverage+8 gate+40 npl+12 npl_trend+5 pb_vs_roe+4 roe+5
 16 LIX  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        77.0             0  L1_cash+7 L1_value+28 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq_rising+2
 17 FMC  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH◆   77.0             1  L1_cash+13 L1_value+40 L2_engine+3 L3_cash+10 L4_moat+5 L6_runway+8 dislocation+2
 18 VGC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        77.0 NARROW     16  L1_cash+7 L1_value+28 L2_engine+22 L4_moat+5 L6_runway+1 L8_hybrid+5 dislocation+8 liq+6
 19 BMP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        74.0 NARROW     24  L1_cash+4 L1_value+34 L2_engine+22 L4_moat+15 L5_margin-12 L6_runway+5 dislocation+2 liq+6 liq_rising+2
 20 DHA  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        73.5 NARROW      2  L1_value+40 L2_engine+22 L4_moat+10 L6_runway+1 dislocation+5
 21 VNM  COMPOUNDER CHEAP_QUALITY       -                 72.3   WIDE    173  L1_cash+4 L1_value+40 L2_engine+6 L4_moat+12 L6_runway+1 dislocation+5 liq+8 moat5f_dur+1
 22 SIP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   71.0             8  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+5 liq+4
 23 BID  BANK       CLEAN               nan               71.0             0  CAR+1 coverage+5 gate+40 npl+8 npl_trend+5 pb_vs_roe+4 roe+8
 24 IDC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   70.0 NARROW     48  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+15 L8_pbfloor+2 dislocation+5 liq+6
 25 NTP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        70.0 NARROW      5  L1_cash+4 L1_value+38 L2_engine+22 L4_moat+10 L5_margin-12 L6_runway+5 dislocation+2 liq+4 liq_rising+2
 26 NTC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   69.0 NARROW      1  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+5 liq_rising+2
 27 VCP  POWER      PRE_INFLECTION_CHEA nan               67.0             0  PB+12 lifecycle+45 roe+10
 28 PVT  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    64.0            67  L1_cash+10 L1_value+26 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+8 liq+8
 29 GEG  POWER      PRE_INFLECTION_CHEA nan               63.0            15  PB+12 lifecycle+45 liq+6
 30 KHP  POWER      PRE_INFLECTION_CHEA nan               61.0             0  PB+12 lifecycle+45 roe+4
 31 TLG  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        59.8   WIDE      4  L1_cash+1 L1_value+30 L2_engine+22 L4_moat+12 L5_margin-12 L6_runway+5 dislocation+2 liq+4 moat5f_dur+0
 32 HPG  CYCLICAL   cmdty_CHEAP         LOWROIC_GROWTH    59.6           461  PB+3 cmdty_pctile+15 dislocation+4 liq+8 regime+30
 33 VNA  COMPOUNDER CHEAP_QUALITY       nan               59.0             0  L1_cash+4 L1_value+36 L2_engine+6 L4_moat+15 L6_runway-2 dislocation+5
 34 BWE  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    59.0 NARROW      4  L1_cash+4 L1_value+42 L2_engine+3 L4_moat+5 L6_runway+8 liq+2
 35 POW  POWER      PRE_INFLECTION      nan               59.0           206  PB+7 lifecycle+40 liq+8 roe+4

## Prioritized TOP-20 (by 8L composite)
  HAH(105), NCT(94), NNC(94), SCS(93), CTG(93), FPT(92), ACB(91), NKG(91), CTR(90), PTB(89), HSG(88), TCL(88), MBB(87), VCB(84), TCB(80), LIX(77), FMC(77), VGC(77), BMP(74), DHA(74)

## TOP-20 by route
  BANK (5): CTG(93), ACB(91), MBB(87), VCB(84), TCB(80)
  CYCLICAL (2): NKG(91), HSG(88)
  SUGAR (0): 
  COMPOUNDER (13): HAH(105), NCT(94), NNC(94), SCS(93), FPT(92), CTR(90), PTB(89), TCL(88), LIX(77), FMC(77), VGC(77), BMP(74), DHA(74)

Caveat: composite is a PRIORITIZATION aid, not a buy signal. NEUTRAL state (FA/quality edge strongest in CRISIS/BEAR per fa-horizon study). Liquidity small names hard to deploy. SPECIAL_SITUATION (DGC/PAT) carry event risk not in score.