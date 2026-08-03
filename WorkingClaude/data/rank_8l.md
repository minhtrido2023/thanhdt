# 8L composite ranking — route-aware score (snapshot ~2026-05-29, market state NEUTRAL)
scored 138 tickers | weights encode: cheapness + engine/runway + cash-machine + moat + dislocation; banks=NPL-gate+PB/ROE; cyclicals=trough+dislocation+PB

  # tkr  route      verdict             engine           score     5F   liqB  components
  1 HAH  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆      109.0            26  L1_cash+13 L1_value+36 L2_engine+22 L3_cash+10 L4_moat+10 L6_runway+8 dislocation+8 liq+6
  2 CTG  BANK       CLEAN               nan               93.0             0  CAR+3 coverage+10 gate+40 npl+12 npl_trend+8 pb_vs_roe+10 roe+10
  3 NNC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        92.0 NARROW      2  L1_cash+7 L1_value+41 L2_engine+22 L4_moat+10 L6_runway+8 dislocation+8
  4 ACB  BANK       CLEAN               nan               91.0             0  CAR+5 coverage+8 gate+40 npl+15 npl_trend+8 pb_vs_roe+7 roe+8
  5 NKG  CYCLICAL   TROUGH_BUY          nan               90.6            20  PB+10 cmdty_pctile+15 dislocation+15 liq+6 regime+45
  6 HSG  CYCLICAL   TROUGH_BUY          nan               90.6            32  PB+10 cmdty_pctile+15 dislocation+15 liq+6 regime+45
  7 NCT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        90.0 NARROW      2  L1_value+43 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+2 liq+2 liq_rising+2
  8 FPT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        89.5 NARROW    572  L1_cash+1 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq+8
  9 SCS  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        89.0 NARROW      6  L1_cash+7 L1_value+35 L2_engine+22 L4_moat+15 L6_runway+5 dislocation+5 liq+4
 10 CTR  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        88.0            22  L1_value+36 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+5 liq+6
 11 MBB  BANK       CLEAN               nan               87.0             0  CAR+5 coverage+5 gate+40 npl+12 npl_trend+8 pb_vs_roe+7 roe+10
 12 SMC  CYCLICAL   TROUGH_BUY          nan               86.6             3  PB+10 cmdty_pctile+15 dislocation+15 liq+2 regime+45
 13 PTB  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       86.0             2  L1_cash+4 L1_value+39 L2_engine+22 L3_cash+10 L4_moat+5 L6_runway+1 dislocation+5 liq+2 liq_rising+2
 14 VCB  BANK       CLEAN               nan               84.0             0  CAR+5 coverage+10 gate+40 npl+15 npl_trend+8 pb_vs_roe+1 roe+5
 15 TCB  BANK       CLEAN               nan               80.0             0  CAR+6 coverage+8 gate+40 npl+12 npl_trend+5 pb_vs_roe+4 roe+5
 16 PVT  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    79.5            57  L1_cash+10 L1_value+42 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+8 liq+8
 17 FMC  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH◆   79.5             1  L1_cash+13 L1_value+42 L2_engine+3 L3_cash+10 L4_moat+5 L6_runway+8 dislocation+2
 18 VNM  COMPOUNDER CHEAP_QUALITY       -                 74.3   WIDE    287  L1_cash+4 L1_value+43 L2_engine+6 L4_moat+12 L6_runway+1 dislocation+2 liq+8 liq_rising+2 moat5f_dur+0
 19 DHA  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        73.0 NARROW      1  L1_value+39 L2_engine+22 L4_moat+10 L6_runway+1 dislocation+5
 20 TCL  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        71.5             0  L1_value+34 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+2 liq_rising+2
 21 BID  BANK       CLEAN               nan               71.0             0  CAR+1 coverage+5 gate+40 npl+8 npl_trend+5 pb_vs_roe+4 roe+8
 22 SIP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   71.0             7  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+5 liq+4
 23 LIX  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        70.0             0  L1_value+27 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq_rising+2
 24 IDC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   70.0 NARROW     39  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+15 L8_pbfloor+2 dislocation+5 liq+6
 25 BMP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        69.0 NARROW     24  L1_cash+1 L1_value+32 L2_engine+22 L4_moat+15 L5_margin-12 L6_runway+5 dislocation+2 liq+6 liq_rising+2
 26 NTC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   69.0 NARROW      1  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+5 liq_rising+2
 27 VCP  POWER      PRE_INFLECTION_CHEA nan               67.0             0  PB+12 lifecycle+45 roe+10
 28 NTP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        65.5 NARROW      3  L1_value+40 L2_engine+22 L4_moat+10 L5_margin-12 L6_runway+5 dislocation+2 liq+2
 29 MWG  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    64.5           358  L1_cash+7 L1_value+36 L2_engine+3 L4_moat+5 L6_runway+5 dislocation+5 liq+8
 30 PVS  COMPOUNDER CHEAP_QUALITY       nan               64.5           107  L1_cash+4 L1_value+42 L2_engine+6 L6_runway-2 dislocation+8 liq+8 liq_rising+2
 31 BWE  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    64.5 NARROW      5  L1_cash+7 L1_value+40 L2_engine+3 L4_moat+5 L6_runway+8 liq+4 liq_rising+2
 32 DMC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        64.0             0  L1_cash+1 L1_value+39 L2_engine+22 L4_moat+5 L6_runway+1
 33 GEG  POWER      PRE_INFLECTION_CHEA nan               63.0            15  PB+12 lifecycle+45 liq+6
 34 PGC  COMPOUNDER CHEAP_QUALITY       nan               62.0             0  L1_cash+10 L1_value+43 L2_engine+6 L4_moat+5 L6_runway-2 dislocation+2 liq_rising+2
 35 PLX  COMPOUNDER CHEAP_QUALITY       nan               61.0            76  L1_cash+7 L1_value+38 L2_engine+6 L6_runway-2 dislocation+8 liq+8

## Prioritized TOP-20 (by 8L composite)
  HAH(109), CTG(93), NNC(92), ACB(91), NKG(91), HSG(91), NCT(90), FPT(90), SCS(89), CTR(88), MBB(87), SMC(87), PTB(86), VCB(84), TCB(80), PVT(80), FMC(80), VNM(74), DHA(73), TCL(72)

## TOP-20 by route
  BANK (5): CTG(93), ACB(91), MBB(87), VCB(84), TCB(80)
  CYCLICAL (3): NKG(91), HSG(91), SMC(87)
  SUGAR (0): 
  COMPOUNDER (12): HAH(109), NNC(92), NCT(90), FPT(90), SCS(89), CTR(88), PTB(86), PVT(80), FMC(80), VNM(74), DHA(73), TCL(72)

Caveat: composite is a PRIORITIZATION aid, not a buy signal. NEUTRAL state (FA/quality edge strongest in CRISIS/BEAR per fa-horizon study). Liquidity small names hard to deploy. SPECIAL_SITUATION (DGC/PAT) carry event risk not in score.