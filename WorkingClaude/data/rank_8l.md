# 8L composite ranking — route-aware score (snapshot ~2026-05-29, market state NEUTRAL)
scored 137 tickers | weights encode: cheapness + engine/runway + cash-machine + moat + dislocation; banks=NPL-gate+PB/ROE; cyclicals=trough+dislocation+PB

  # tkr  route      verdict             engine           score     5F   liqB  components
  1 CTR  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        97.9            20  L1_cash+10 L1_value+36 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+5 liq+6
  2 HAH  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       96.4            29  L1_cash+13 L1_value+36 L2_engine+22 L3_cash+10 L4_moat+10 L5_margin-12 L6_runway+8 dislocation+8 liq+6
  3 NCT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        94.4 NARROW      2  L1_cash+7 L1_value+43 L2_engine+22 L4_moat+15 L6_runway+8 liq+2 liq_rising+2
  4 CTG  BANK       CLEAN               nan               93.0             0  CAR+3 coverage+10 gate+40 npl+12 npl_trend+8 pb_vs_roe+10 roe+10
  5 FPT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        92.4 NARROW    595  L1_cash+4 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq+8
  6 ACB  BANK       CLEAN               nan               91.0             0  CAR+5 coverage+8 gate+40 npl+15 npl_trend+8 pb_vs_roe+7 roe+8
  7 NKG  CYCLICAL   TROUGH_BUY          nan               90.6            18  PB+10 cmdty_pctile+15 dislocation+15 liq+6 regime+45
  8 HSG  CYCLICAL   TROUGH_BUY          nan               90.6            32  PB+10 cmdty_pctile+15 dislocation+15 liq+6 regime+45
  9 NNC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        89.9 NARROW      1  L1_cash+7 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+8 dislocation+8
 10 SCS  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        87.4 NARROW      6  L1_cash+7 L1_value+34 L2_engine+22 L4_moat+15 L6_runway+5 dislocation+5 liq+4
 11 TCL  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        87.4             0  L1_cash+10 L1_value+43 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+2
 12 MBB  BANK       CLEAN               nan               87.0             0  CAR+5 coverage+5 gate+40 npl+12 npl_trend+8 pb_vs_roe+7 roe+10
 13 VCB  BANK       CLEAN               nan               84.0             0  CAR+5 coverage+10 gate+40 npl+15 npl_trend+8 pb_vs_roe+1 roe+5
 14 PTB  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       80.4             2  L1_cash+1 L1_value+39 L2_engine+22 L3_cash+10 L4_moat+5 L6_runway+1 dislocation+5 liq+2
 15 TCB  BANK       CLEAN               nan               80.0             0  CAR+6 coverage+8 gate+40 npl+12 npl_trend+5 pb_vs_roe+4 roe+5
 16 VGC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        77.4 NARROW     15  L1_cash+7 L1_value+28 L2_engine+22 L4_moat+5 L6_runway+1 L8_hybrid+5 dislocation+8 liq+6
 17 LIX  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        77.4             1  L1_cash+7 L1_value+28 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq_rising+2
 18 FMC  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH◆   76.9             1  L1_cash+13 L1_value+40 L2_engine+3 L3_cash+10 L4_moat+5 L6_runway+8 dislocation+2
 19 DHA  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        72.9 NARROW      1  L1_value+40 L2_engine+22 L4_moat+10 L6_runway+1 dislocation+5
 20 NTP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        72.9 NARROW      4  L1_cash+7 L1_value+38 L2_engine+22 L4_moat+10 L5_margin-12 L6_runway+5 dislocation+2 liq+4 liq_rising+2
 21 BID  BANK       CLEAN               nan               71.0             0  CAR+1 coverage+5 gate+40 npl+8 npl_trend+5 pb_vs_roe+4 roe+8
 22 SIP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   71.0             8  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+5 liq+4
 23 IDC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   70.0 NARROW     46  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+15 L8_pbfloor+2 dislocation+5 liq+6
 24 NTC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   69.0 NARROW      2  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+5 liq_rising+2
 25 VNM  COMPOUNDER CHEAP_QUALITY       -                 68.2   WIDE    208  L1_cash+4 L1_value+40 L2_engine+6 L4_moat+12 L6_runway+1 dislocation+2 liq+8 moat5f_dur+0
 26 VCP  POWER      PRE_INFLECTION_CHEA nan               67.0             0  PB+12 lifecycle+45 roe+10
 27 PVT  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    65.9            59  L1_cash+10 L1_value+28 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+8 liq+8
 28 TLG  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        65.2   WIDE      4  L1_cash+4 L1_value+30 L2_engine+22 L4_moat+12 L5_margin-12 L6_runway+5 dislocation+2 liq+4 liq_rising+2 moat5f_dur+0
 29 GEG  POWER      PRE_INFLECTION_CHEA nan               63.0            15  PB+12 lifecycle+45 liq+6
 30 BWE  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    61.9 NARROW      4  L1_cash+7 L1_value+42 L2_engine+3 L4_moat+5 L6_runway+8 liq+2
 31 OIL  COMPOUNDER CHEAP_QUALITY       nan               61.4            27  L1_cash+10 L1_value+38 L2_engine+6 L6_runway-2 dislocation+8 liq+6
 32 KHP  POWER      PRE_INFLECTION_CHEA nan               61.0             0  PB+12 lifecycle+45 roe+4
 33 HPG  CYCLICAL   cmdty_CHEAP         LOWROIC_GROWTH    59.6           442  PB+3 cmdty_pctile+15 dislocation+4 liq+8 regime+30
 34 POW  POWER      PRE_INFLECTION      nan               59.0           206  PB+7 lifecycle+40 liq+8 roe+4
 35 VNA  COMPOUNDER CHEAP_QUALITY       nan               58.9             0  L1_cash+4 L1_value+36 L2_engine+6 L4_moat+15 L6_runway-2 dislocation+5

## Prioritized TOP-20 (by 8L composite)
  CTR(98), HAH(96), NCT(94), CTG(93), FPT(92), ACB(91), NKG(91), HSG(91), NNC(90), SCS(87), TCL(87), MBB(87), VCB(84), PTB(80), TCB(80), VGC(77), LIX(77), FMC(77), DHA(73), NTP(73)

## TOP-20 by route
  BANK (5): CTG(93), ACB(91), MBB(87), VCB(84), TCB(80)
  CYCLICAL (2): NKG(91), HSG(91)
  SUGAR (0): 
  COMPOUNDER (13): CTR(98), HAH(96), NCT(94), FPT(92), NNC(90), SCS(87), TCL(87), PTB(80), VGC(77), LIX(77), FMC(77), DHA(73), NTP(73)

Caveat: composite is a PRIORITIZATION aid, not a buy signal. NEUTRAL state (FA/quality edge strongest in CRISIS/BEAR per fa-horizon study). Liquidity small names hard to deploy. SPECIAL_SITUATION (DGC/PAT) carry event risk not in score.