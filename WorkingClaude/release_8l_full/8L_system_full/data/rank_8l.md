# 8L composite ranking — route-aware score (snapshot ~2026-05-29, market state NEUTRAL)
scored 139 tickers | weights encode: cheapness + engine/runway + cash-machine + moat + dislocation; banks=NPL-gate+PB/ROE; cyclicals=trough+dislocation+PB

  # tkr  route      verdict             engine           score     5F   liqB  components
  1 CTG  BANK       CLEAN               nan               93.0             0  CAR+3 coverage+10 gate+40 npl+12 npl_trend+8 pb_vs_roe+10 roe+10
  2 NCT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        92.7 NARROW      1  L1_cash+7 L1_value+43 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+2
  3 ACB  BANK       CLEAN               nan               91.0             0  CAR+5 coverage+8 gate+40 npl+15 npl_trend+8 pb_vs_roe+7 roe+8
  4 NNC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        90.2 NARROW      2  L1_cash+7 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+8 dislocation+8
  5 NKG  CYCLICAL   TROUGH_BUY          nan               89.0            39  PB+10 cmdty_pctile+13 dislocation+15 liq+6 regime+45
  6 TCL  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        87.7             1  L1_cash+10 L1_value+43 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+2
  7 MBB  BANK       CLEAN               nan               87.0             0  CAR+5 coverage+5 gate+40 npl+12 npl_trend+8 pb_vs_roe+7 roe+10
  8 HSG  CYCLICAL   TROUGH_BUY          nan               86.0            40  PB+10 cmdty_pctile+13 dislocation+12 liq+6 regime+45
  9 HAH  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       84.7            36  L1_cash+10 L1_value+30 L2_engine+22 L3_cash+10 L4_moat+10 L5_margin-12 L6_runway+8 dislocation+5 liq+6
 10 VCB  BANK       CLEAN               nan               84.0             0  CAR+5 coverage+10 gate+40 npl+15 npl_trend+8 pb_vs_roe+1 roe+5
 11 SCS  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        83.2 NARROW      6  L1_cash+7 L1_value+30 L2_engine+22 L4_moat+15 L6_runway+5 dislocation+5 liq+4
 12 TCB  BANK       CLEAN               nan               80.0             0  CAR+6 coverage+8 gate+40 npl+12 npl_trend+5 pb_vs_roe+4 roe+5
 13 FMC  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH◆   76.2             1  L1_cash+13 L1_value+40 L2_engine+3 L3_cash+10 L4_moat+5 L6_runway+8 dislocation+2
 14 VGC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        76.2 NARROW     29  L1_cash+7 L1_value+26 L2_engine+22 L4_moat+5 L6_runway+1 L8_hybrid+5 dislocation+8 liq+6
 15 CTR  COMPOUNDER CHEAP_1lens         COMPOUNDER        74.7            50  L1_cash+7 L1_value+15 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+2 liq+8 liq_rising+2
 16 DHA  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        73.2 NARROW      2  L1_value+36 L2_engine+22 L4_moat+10 L6_runway+1 dislocation+8
 17 FPT  COMPOUNDER CHEAP_1lens         COMPOUNDER        72.2 NARROW    820  L1_cash+4 L1_value+20 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq+8
 18 BID  BANK       CLEAN               nan               71.0             0  CAR+1 coverage+5 gate+40 npl+8 npl_trend+5 pb_vs_roe+4 roe+8
 19 BMP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        70.2 NARROW     23  L1_cash+4 L1_value+30 L2_engine+22 L4_moat+15 L5_margin-12 L6_runway+5 dislocation+5 liq+6
 20 SIP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   70.0            12  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+2 liq+6
 21 PTB  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       69.2             3  L1_cash+1 L1_value+30 L2_engine+22 L3_cash+10 L4_moat+5 L6_runway+1 dislocation+2 liq+2
 22 NTP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        67.7 NARROW      6  L1_cash+7 L1_value+28 L2_engine+22 L4_moat+10 L5_margin-12 L6_runway+5 dislocation+8 liq+4
 23 IDC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   67.0 NARROW     64  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+15 dislocation+2 liq+8
 24 VCP  POWER      PRE_INFLECTION_CHEA nan               67.0             0  PB+12 lifecycle+45 roe+10
 25 VNM  COMPOUNDER CHEAP_QUALITY       -                 66.0   WIDE    190  L1_cash+4 L1_value+37 L2_engine+6 L4_moat+12 L6_runway+1 dislocation+2 liq+8 moat5f_dur+0
 26 LIX  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        65.2             0  L1_cash+7 L1_value+20 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+5
 27 NTC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   64.0 NARROW      1  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+2
 28 GEG  POWER      PRE_INFLECTION_CHEA nan               63.0            15  PB+12 lifecycle+45 liq+6
 29 BWE  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    62.7 NARROW      6  L1_cash+7 L1_value+38 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+2 liq+4
 30 OIL  COMPOUNDER CHEAP_QUALITY       nan               61.2            46  L1_cash+10 L1_value+38 L2_engine+6 L6_runway-2 dislocation+8 liq+6
 31 KHP  POWER      PRE_INFLECTION_CHEA nan               61.0             0  PB+12 lifecycle+45 roe+4
 32 DTD  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   60.0 NARROW      2  L2_engine+22 L4_moat+10 L6_runway+5 L8_backlog+5 L8_pbfloor+8 dislocation+8 liq+2
 33 POW  POWER      PRE_INFLECTION      nan               59.0           206  PB+7 lifecycle+40 liq+8 roe+4
 34 HPG  CYCLICAL   cmdty_CHEAP         LOWROIC_GROWTH    58.0           574  PB+3 cmdty_pctile+13 dislocation+4 liq+8 regime+30
 35 VOS  COMPOUNDER CHEAP_QUALITY       nan               57.7            10  L1_value+34 L2_engine+6 L4_moat+10 L6_runway-2 dislocation+8 liq+6

## Prioritized TOP-20 (by 8L composite)
  CTG(93), NCT(93), ACB(91), NNC(90), NKG(89), TCL(88), MBB(87), HSG(86), HAH(85), VCB(84), SCS(83), TCB(80), FMC(76), VGC(76), CTR(75), DHA(73), FPT(72), BID(71), BMP(70), SIP(70)

## TOP-20 by route
  BANK (6): CTG(93), ACB(91), MBB(87), VCB(84), TCB(80), BID(71)
  CYCLICAL (2): NKG(89), HSG(86)
  SUGAR (0): 
  COMPOUNDER (12): NCT(93), NNC(90), TCL(88), HAH(85), SCS(83), FMC(76), VGC(76), CTR(75), DHA(73), FPT(72), BMP(70), SIP(70)

Caveat: composite is a PRIORITIZATION aid, not a buy signal. NEUTRAL state (FA/quality edge strongest in CRISIS/BEAR per fa-horizon study). Liquidity small names hard to deploy. SPECIAL_SITUATION (DGC/PAT) carry event risk not in score.