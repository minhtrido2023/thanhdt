# 8L composite ranking — route-aware score (snapshot ~2026-05-29, market state NEUTRAL)
scored 137 tickers | weights encode: cheapness + engine/runway + cash-machine + moat + dislocation; banks=NPL-gate+PB/ROE; cyclicals=trough+dislocation+PB

  # tkr  route      verdict             engine           score     5F   liqB  components
  1 CTG  BANK       CLEAN               nan               93.0             0  CAR+3 coverage+10 gate+40 npl+12 npl_trend+8 pb_vs_roe+10 roe+10
  2 NCT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        92.6 NARROW      1  L1_cash+7 L1_value+43 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+2
  3 CTR  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        92.6            34  L1_cash+7 L1_value+34 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+5 liq+6
  4 ACB  BANK       CLEAN               nan               91.0             0  CAR+5 coverage+8 gate+40 npl+15 npl_trend+8 pb_vs_roe+7 roe+8
  5 NNC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        90.1 NARROW      2  L1_cash+7 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+8 dislocation+8
  6 TCL  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        87.6             0  L1_cash+10 L1_value+43 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+2
  7 MBB  BANK       CLEAN               nan               87.0             0  CAR+5 coverage+5 gate+40 npl+12 npl_trend+8 pb_vs_roe+7 roe+10
  8 HAH  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       85.1            33  L1_cash+10 L1_value+30 L2_engine+22 L3_cash+10 L4_moat+10 L5_margin-12 L6_runway+8 dislocation+5 liq+6
  9 VCB  BANK       CLEAN               nan               84.0             0  CAR+5 coverage+10 gate+40 npl+15 npl_trend+8 pb_vs_roe+1 roe+5
 10 SCS  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        83.1 NARROW      6  L1_cash+7 L1_value+30 L2_engine+22 L4_moat+15 L6_runway+5 dislocation+5 liq+4
 11 TCB  BANK       CLEAN               nan               80.0             0  CAR+6 coverage+8 gate+40 npl+12 npl_trend+5 pb_vs_roe+4 roe+5
 12 FMC  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH◆   76.1             1  L1_cash+13 L1_value+40 L2_engine+3 L3_cash+10 L4_moat+5 L6_runway+8 dislocation+2
 13 VGC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        73.6 NARROW     28  L1_cash+7 L1_value+26 L2_engine+22 L4_moat+5 L6_runway+1 L8_hybrid+3 dislocation+8 liq+6
 14 SIP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   73.0            11  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+5 liq+6
 15 FPT  COMPOUNDER CHEAP_1lens         COMPOUNDER        72.6 NARROW    690  L1_cash+4 L1_value+20 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq+8
 16 PTB  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       72.6             3  L1_cash+1 L1_value+31 L2_engine+22 L3_cash+10 L4_moat+5 L6_runway+1 dislocation+5 liq+2
 17 DHA  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        71.1 NARROW      2  L1_value+36 L2_engine+22 L4_moat+10 L6_runway+1 dislocation+5 liq+2
 18 BID  BANK       CLEAN               nan               71.0             0  CAR+1 coverage+5 gate+40 npl+8 npl_trend+5 pb_vs_roe+4 roe+8
 19 IDC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   70.0 NARROW     57  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+15 dislocation+5 liq+8
 20 VNM  COMPOUNDER CHEAP_QUALITY       -                 69.9   WIDE    177  L1_cash+4 L1_value+38 L2_engine+6 L4_moat+12 L6_runway+1 dislocation+5 liq+8 moat5f_dur+1
 21 NTC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   67.0 NARROW      1  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+5
 22 VCP  POWER      PRE_INFLECTION_CHEA nan               67.0             0  PB+12 lifecycle+45 roe+10
 23 BMP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        66.1 NARROW     20  L1_cash+4 L1_value+28 L2_engine+22 L4_moat+15 L5_margin-12 L6_runway+5 dislocation+2 liq+6
 24 LIX  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        65.1             0  L1_cash+7 L1_value+20 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+5
 25 GEG  POWER      PRE_INFLECTION_CHEA nan               63.0            15  PB+12 lifecycle+45 liq+6
 26 BWE  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    62.1 NARROW      5  L1_cash+7 L1_value+38 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+2 liq+4
 27 NTP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        61.6 NARROW      4  L1_cash+7 L1_value+28 L2_engine+22 L4_moat+10 L5_margin-12 L6_runway+5 dislocation+2 liq+4
 28 OIL  COMPOUNDER CHEAP_QUALITY       nan               61.6            33  L1_cash+10 L1_value+38 L2_engine+6 L6_runway-2 dislocation+8 liq+6
 29 KHP  POWER      PRE_INFLECTION_CHEA nan               61.0             0  PB+12 lifecycle+45 roe+4
 30 POW  POWER      PRE_INFLECTION      nan               59.0           206  PB+7 lifecycle+40 liq+8 roe+4
 31 DTD  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   58.0 NARROW      2  L2_engine+22 L4_moat+10 L6_runway+5 L8_backlog+5 L8_pbfloor+8 dislocation+8
 32 VNA  COMPOUNDER CHEAP_QUALITY       nan               57.6             0  L1_cash+4 L1_value+34 L2_engine+6 L4_moat+15 L6_runway-2 dislocation+5
 33 PVS  COMPOUNDER CHEAP_QUALITY       nan               57.6           130  L1_cash+1 L1_value+41 L2_engine+6 L6_runway-2 dislocation+8 liq+8
 34 NAB  BANK       WATCH               nan               56.0             0  CAR+3 coverage+2 gate+15 npl+8 npl_trend+8 pb_vs_roe+10 roe+10
 35 VOS  COMPOUNDER CHEAP_QUALITY       nan               55.1            10  L1_value+34 L2_engine+6 L4_moat+10 L6_runway-2 dislocation+8 liq+4

## Prioritized TOP-20 (by 8L composite)
  CTG(93), NCT(93), CTR(93), ACB(91), NNC(90), TCL(88), MBB(87), HAH(85), VCB(84), SCS(83), TCB(80), FMC(76), VGC(74), SIP(73), FPT(73), PTB(73), DHA(71), BID(71), IDC(70), VNM(70)

## TOP-20 by route
  BANK (6): CTG(93), ACB(91), MBB(87), VCB(84), TCB(80), BID(71)
  CYCLICAL (0): 
  SUGAR (0): 
  COMPOUNDER (14): NCT(93), CTR(93), NNC(90), TCL(88), HAH(85), SCS(83), FMC(76), VGC(74), SIP(73), FPT(73), PTB(73), DHA(71), IDC(70), VNM(70)

Caveat: composite is a PRIORITIZATION aid, not a buy signal. NEUTRAL state (FA/quality edge strongest in CRISIS/BEAR per fa-horizon study). Liquidity small names hard to deploy. SPECIAL_SITUATION (DGC/PAT) carry event risk not in score.