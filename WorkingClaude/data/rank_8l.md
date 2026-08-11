# 8L composite ranking — route-aware score (snapshot ~2026-05-29, market state NEUTRAL)
scored 138 tickers | weights encode: cheapness + engine/runway + cash-machine + moat + dislocation; banks=NPL-gate+PB/ROE; cyclicals=trough+dislocation+PB

  # tkr  route      verdict             engine           score     5F   liqB  components
  1 HAH  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆      108.6            25  L1_cash+13 L1_value+36 L2_engine+22 L3_cash+10 L4_moat+10 L6_runway+8 dislocation+8 liq+6
  2 NNC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        93.6 NARROW      2  L1_cash+7 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+8 dislocation+8 liq_rising+2
  3 NKG  CYCLICAL   TROUGH_BUY          nan               93.0            21  PB+10 cmdty_pctile+17 dislocation+15 liq+6 regime+45
  4 HSG  CYCLICAL   TROUGH_BUY          nan               93.0            28  PB+10 cmdty_pctile+17 dislocation+15 liq+6 regime+45
  5 CTG  BANK       CLEAN               nan               93.0             0  CAR+3 coverage+10 gate+40 npl+12 npl_trend+8 pb_vs_roe+10 roe+10
  6 CTR  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        91.6            24  L1_cash+4 L1_value+36 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+5 liq+6
  7 ACB  BANK       CLEAN               nan               91.0             0  CAR+5 coverage+8 gate+40 npl+15 npl_trend+8 pb_vs_roe+7 roe+8
  8 NCT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        90.1 NARROW      3  L1_value+43 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+2 liq+2 liq_rising+2
  9 FPT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        89.6 NARROW    555  L1_cash+1 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq+8
 10 SMC  CYCLICAL   TROUGH_BUY          nan               89.0             2  PB+10 cmdty_pctile+17 dislocation+15 liq+2 regime+45
 11 SCS  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        88.6 NARROW      6  L1_cash+7 L1_value+34 L2_engine+22 L4_moat+15 L6_runway+5 dislocation+5 liq+4
 12 MBB  BANK       CLEAN               nan               87.0             0  CAR+5 coverage+5 gate+40 npl+12 npl_trend+8 pb_vs_roe+7 roe+10
 13 PTB  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       86.6             2  L1_cash+4 L1_value+40 L2_engine+22 L3_cash+10 L4_moat+5 L6_runway+1 dislocation+5 liq+2 liq_rising+2
 14 VCB  BANK       CLEAN               nan               84.0             0  CAR+5 coverage+10 gate+40 npl+15 npl_trend+8 pb_vs_roe+1 roe+5
 15 TCB  BANK       CLEAN               nan               80.0             0  CAR+6 coverage+8 gate+40 npl+12 npl_trend+5 pb_vs_roe+4 roe+5
 16 FMC  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH◆   79.1             1  L1_cash+13 L1_value+42 L2_engine+3 L3_cash+10 L4_moat+5 L6_runway+8 dislocation+2
 17 PVT  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    77.1            70  L1_cash+10 L1_value+40 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+5 liq+8 liq_rising+2
 18 NTP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        72.6 NARROW      4  L1_value+40 L2_engine+22 L4_moat+10 L5_margin-12 L6_runway+5 dislocation+5 liq+4 liq_rising+2
 19 DHA  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        72.6 NARROW      1  L1_value+38 L2_engine+22 L4_moat+10 L6_runway+1 dislocation+5
 20 BID  BANK       CLEAN               nan               71.0             0  CAR+1 coverage+5 gate+40 npl+8 npl_trend+5 pb_vs_roe+4 roe+8
 21 VNM  COMPOUNDER CHEAP_QUALITY       -                 70.9   WIDE    351  L1_cash+1 L1_value+42 L2_engine+6 L4_moat+12 L6_runway+1 dislocation+2 liq+8 liq_rising+2 moat5f_dur+0
 22 LIX  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        70.1             0  L1_value+27 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq_rising+2
 23 IDC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   70.0 NARROW     39  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+15 L8_pbfloor+2 dislocation+5 liq+6
 24 TCL  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        69.6             0  L1_value+34 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+2
 25 BMP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        69.1 NARROW     21  L1_cash+1 L1_value+32 L2_engine+22 L4_moat+15 L5_margin-12 L6_runway+5 dislocation+2 liq+6 liq_rising+2
 26 SIP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   68.0             6  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+2 liq+4
 27 NTC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   67.0 NARROW      1  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+5
 28 VCP  POWER      PRE_INFLECTION_CHEA nan               67.0             0  PB+12 lifecycle+45 roe+10
 29 MWG  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    66.6           388  L1_cash+7 L1_value+36 L2_engine+3 L4_moat+5 L6_runway+5 dislocation+5 liq+8 liq_rising+2
 30 PGC  COMPOUNDER CHEAP_QUALITY       nan               65.1             0  L1_cash+10 L1_value+43 L2_engine+6 L4_moat+5 L6_runway-2 dislocation+5 liq_rising+2
 31 DMC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        65.1             0  L1_cash+1 L1_value+40 L2_engine+22 L4_moat+5 L6_runway+1
 32 BWE  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    64.1 NARROW      9  L1_cash+7 L1_value+39 L2_engine+3 L4_moat+5 L6_runway+8 liq+4 liq_rising+2
 33 HPG  CYCLICAL   cmdty_CHEAP         LOWROIC_GROWTH    64.0           585  PB+3 cmdty_pctile+17 dislocation+4 liq+8 liq_rising+2 regime+30
 34 GEG  POWER      PRE_INFLECTION_CHEA nan               63.0            15  PB+12 lifecycle+45 liq+6
 35 KHP  POWER      PRE_INFLECTION_CHEA nan               61.0             0  PB+12 lifecycle+45 roe+4

## Prioritized TOP-20 (by 8L composite)
  HAH(109), NNC(94), NKG(93), HSG(93), CTG(93), CTR(92), ACB(91), NCT(90), FPT(90), SMC(89), SCS(89), MBB(87), PTB(87), VCB(84), TCB(80), FMC(79), PVT(77), NTP(73), DHA(73), BID(71)

## TOP-20 by route
  BANK (6): CTG(93), ACB(91), MBB(87), VCB(84), TCB(80), BID(71)
  CYCLICAL (3): NKG(93), HSG(93), SMC(89)
  SUGAR (0): 
  COMPOUNDER (11): HAH(109), NNC(94), CTR(92), NCT(90), FPT(90), SCS(89), PTB(87), FMC(79), PVT(77), NTP(73), DHA(73)

Caveat: composite is a PRIORITIZATION aid, not a buy signal. NEUTRAL state (FA/quality edge strongest in CRISIS/BEAR per fa-horizon study). Liquidity small names hard to deploy. SPECIAL_SITUATION (DGC/PAT) carry event risk not in score.