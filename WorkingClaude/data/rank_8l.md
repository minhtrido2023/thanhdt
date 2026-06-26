# 8L composite ranking — route-aware score (snapshot ~2026-05-29, market state NEUTRAL)
scored 137 tickers | weights encode: cheapness + engine/runway + cash-machine + moat + dislocation; banks=NPL-gate+PB/ROE; cyclicals=trough+dislocation+PB

  # tkr  route      verdict             engine           score     5F   liqB  components
  1 CTR  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        94.1            30  L1_cash+7 L1_value+36 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+5 liq+6
  2 CTG  BANK       CLEAN               nan               93.0             0  CAR+3 coverage+10 gate+40 npl+12 npl_trend+8 pb_vs_roe+10 roe+10
  3 FPT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        92.6 NARROW    660  L1_cash+4 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq+8
  4 ACB  BANK       CLEAN               nan               91.0             0  CAR+5 coverage+8 gate+40 npl+15 npl_trend+8 pb_vs_roe+7 roe+8
  5 NCT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        90.6 NARROW      1  L1_cash+7 L1_value+43 L2_engine+22 L4_moat+15 L6_runway+8
  6 NNC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        90.1 NARROW      2  L1_cash+7 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+8 dislocation+8
  7 HAH  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       89.1            34  L1_cash+10 L1_value+34 L2_engine+22 L3_cash+10 L4_moat+10 L5_margin-12 L6_runway+8 dislocation+5 liq+6
  8 SCS  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        88.1 NARROW      7  L1_cash+7 L1_value+34 L2_engine+22 L4_moat+15 L6_runway+5 dislocation+5 liq+4
  9 TCL  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        87.6             0  L1_cash+10 L1_value+43 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+2
 10 MBB  BANK       CLEAN               nan               87.0             0  CAR+5 coverage+5 gate+40 npl+12 npl_trend+8 pb_vs_roe+7 roe+10
 11 VCB  BANK       CLEAN               nan               84.0             0  CAR+5 coverage+10 gate+40 npl+15 npl_trend+8 pb_vs_roe+1 roe+5
 12 TCB  BANK       CLEAN               nan               80.0             0  CAR+6 coverage+8 gate+40 npl+12 npl_trend+5 pb_vs_roe+4 roe+5
 13 VGC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        77.1 NARROW     24  L1_cash+7 L1_value+28 L2_engine+22 L4_moat+5 L6_runway+1 L8_hybrid+5 dislocation+8 liq+6
 14 FMC  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH◆   76.6             1  L1_cash+13 L1_value+40 L2_engine+3 L3_cash+10 L4_moat+5 L6_runway+8 dislocation+2
 15 PTB  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       76.1             3  L1_cash+1 L1_value+38 L2_engine+22 L3_cash+10 L4_moat+5 L6_runway+1 dislocation+2 liq+2
 16 DHA  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        74.1 NARROW      2  L1_value+38 L2_engine+22 L4_moat+10 L6_runway+1 dislocation+5 liq+2
 17 SIP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   73.0            11  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+5 liq+6
 18 VNM  COMPOUNDER CHEAP_QUALITY       -                 72.4   WIDE    168  L1_cash+4 L1_value+40 L2_engine+6 L4_moat+12 L6_runway+1 dislocation+5 liq+8 moat5f_dur+1
 19 LIX  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        71.1             0  L1_cash+7 L1_value+26 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+5
 20 BID  BANK       CLEAN               nan               71.0             0  CAR+1 coverage+5 gate+40 npl+8 npl_trend+5 pb_vs_roe+4 roe+8
 21 IDC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   70.0 NARROW     55  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+15 dislocation+5 liq+8
 22 NTP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        68.1 NARROW      4  L1_cash+7 L1_value+36 L2_engine+22 L4_moat+10 L5_margin-12 L6_runway+5 dislocation+2 liq+2
 23 NTC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   67.0 NARROW      1  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+5
 24 VCP  POWER      PRE_INFLECTION_CHEA nan               67.0             0  PB+12 lifecycle+45 roe+10
 25 BWE  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    64.6 NARROW      5  L1_cash+7 L1_value+42 L2_engine+3 L4_moat+5 L6_runway+8 liq+4
 26 PVT  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    63.6            80  L1_cash+10 L1_value+26 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+8 liq+8
 27 GEG  POWER      PRE_INFLECTION_CHEA nan               63.0            15  PB+12 lifecycle+45 liq+6
 28 OIL  COMPOUNDER CHEAP_QUALITY       nan               62.1            30  L1_cash+10 L1_value+38 L2_engine+6 L6_runway-2 dislocation+8 liq+6
 29 VNA  COMPOUNDER CHEAP_QUALITY       nan               62.1             0  L1_cash+4 L1_value+36 L2_engine+6 L4_moat+15 L6_runway-2 dislocation+8
 30 KHP  POWER      PRE_INFLECTION_CHEA nan               61.0             0  PB+12 lifecycle+45 roe+4
 31 POW  POWER      PRE_INFLECTION      nan               59.0           206  PB+7 lifecycle+40 liq+8 roe+4
 32 DTD  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   58.0 NARROW      2  L2_engine+22 L4_moat+10 L6_runway+5 L8_backlog+5 L8_pbfloor+8 dislocation+8
 33 PVS  COMPOUNDER CHEAP_QUALITY       nan               57.6           123  L1_cash+1 L1_value+41 L2_engine+6 L6_runway-2 dislocation+8 liq+8
 34 BMP  COMPOUNDER CHEAP_1lens         COMPOUNDER        56.1 NARROW     21  L1_cash+4 L1_value+18 L2_engine+22 L4_moat+15 L5_margin-12 L6_runway+5 dislocation+2 liq+6
 35 DMC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        56.1             0  L1_cash+4 L1_value+28 L2_engine+22 L4_moat+5 L6_runway+1

## Prioritized TOP-20 (by 8L composite)
  CTR(94), CTG(93), FPT(93), ACB(91), NCT(91), NNC(90), HAH(89), SCS(88), TCL(88), MBB(87), VCB(84), TCB(80), VGC(77), FMC(77), PTB(76), DHA(74), SIP(73), VNM(72), LIX(71), BID(71)

## TOP-20 by route
  BANK (6): CTG(93), ACB(91), MBB(87), VCB(84), TCB(80), BID(71)
  CYCLICAL (0): 
  SUGAR (0): 
  COMPOUNDER (14): CTR(94), FPT(93), NCT(91), NNC(90), HAH(89), SCS(88), TCL(88), VGC(77), FMC(77), PTB(76), DHA(74), SIP(73), VNM(72), LIX(71)

Caveat: composite is a PRIORITIZATION aid, not a buy signal. NEUTRAL state (FA/quality edge strongest in CRISIS/BEAR per fa-horizon study). Liquidity small names hard to deploy. SPECIAL_SITUATION (DGC/PAT) carry event risk not in score.