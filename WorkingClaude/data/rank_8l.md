# 8L composite ranking — route-aware score (snapshot ~2026-05-29, market state NEUTRAL)
scored 138 tickers | weights encode: cheapness + engine/runway + cash-machine + moat + dislocation; banks=NPL-gate+PB/ROE; cyclicals=trough+dislocation+PB

  # tkr  route      verdict             engine           score     5F   liqB  components
  1 HAH  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆      108.5            36  L1_cash+13 L1_value+36 L2_engine+22 L3_cash+10 L4_moat+10 L6_runway+8 dislocation+8 liq+6
  2 CTG  BANK       CLEAN               nan               93.0             0  CAR+3 coverage+10 gate+40 npl+12 npl_trend+8 pb_vs_roe+10 roe+10
  3 HSG  CYCLICAL   TROUGH_BUY          nan               93.0            24  PB+10 cmdty_pctile+17 dislocation+15 liq+6 regime+45
  4 NKG  CYCLICAL   TROUGH_BUY          nan               93.0            18  PB+10 cmdty_pctile+17 dislocation+15 liq+6 regime+45
  5 NNC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        91.5 NARROW      2  L1_cash+7 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+8 dislocation+8
  6 CTR  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        91.5            25  L1_cash+4 L1_value+36 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+5 liq+6
  7 ACB  BANK       CLEAN               nan               91.0             0  CAR+5 coverage+8 gate+40 npl+15 npl_trend+8 pb_vs_roe+7 roe+8
  8 PTB  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       89.5             3  L1_cash+4 L1_value+40 L2_engine+22 L3_cash+10 L4_moat+5 L6_runway+1 dislocation+8 liq+2 liq_rising+2
  9 FPT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        89.0 NARROW    472  L1_cash+1 L1_value+39 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq+8
 10 SMC  CYCLICAL   TROUGH_BUY          nan               89.0             2  PB+10 cmdty_pctile+17 dislocation+15 liq+2 regime+45
 11 SCS  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        88.5 NARROW      5  L1_cash+7 L1_value+34 L2_engine+22 L4_moat+15 L6_runway+5 dislocation+5 liq+4
 12 NCT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        88.0 NARROW      2  L1_value+43 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+2 liq+2
 13 MBB  BANK       CLEAN               nan               87.0             0  CAR+5 coverage+5 gate+40 npl+12 npl_trend+8 pb_vs_roe+7 roe+10
 14 VCB  BANK       CLEAN               nan               84.0             0  CAR+5 coverage+10 gate+40 npl+15 npl_trend+8 pb_vs_roe+1 roe+5
 15 FMC  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH◆   81.0             0  L1_cash+13 L1_value+42 L2_engine+3 L3_cash+10 L4_moat+5 L6_runway+8 dislocation+2 liq_rising+2
 16 TCB  BANK       CLEAN               nan               80.0             0  CAR+6 coverage+8 gate+40 npl+12 npl_trend+5 pb_vs_roe+4 roe+5
 17 PVT  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    76.0            92  L1_cash+10 L1_value+39 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+5 liq+8 liq_rising+2
 18 DHA  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        75.5 NARROW      2  L1_value+38 L2_engine+22 L4_moat+10 L6_runway+1 dislocation+5 liq+2 liq_rising+2
 19 BID  BANK       CLEAN               nan               71.0             0  CAR+1 coverage+5 gate+40 npl+8 npl_trend+5 pb_vs_roe+4 roe+8
 20 VNM  COMPOUNDER CHEAP_QUALITY       -                 70.3   WIDE    289  L1_cash+1 L1_value+42 L2_engine+6 L4_moat+12 L6_runway+1 dislocation+2 liq+8 liq_rising+2 moat5f_dur+0
 21 LIX  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        70.0             0  L1_value+27 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq_rising+2
 22 IDC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   70.0 NARROW     36  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+15 L8_pbfloor+2 dislocation+5 liq+6
 23 TCL  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        69.5             0  L1_value+34 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+2
 24 NTP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        68.5 NARROW     10  L1_value+40 L2_engine+22 L4_moat+10 L5_margin-12 L6_runway+5 dislocation+2 liq+4 liq_rising+2
 25 SIP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   68.0             4  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+2 liq+4
 26 BMP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        67.5 NARROW     13  L1_cash+1 L1_value+32 L2_engine+22 L4_moat+15 L5_margin-12 L6_runway+5 dislocation+2 liq+6
 27 BWE  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    67.0 NARROW      6  L1_cash+7 L1_value+40 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+2 liq+4 liq_rising+2
 28 VCP  POWER      PRE_INFLECTION_CHEA nan               67.0             0  PB+12 lifecycle+45 roe+10
 29 DMC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        67.0             0  L1_cash+1 L1_value+40 L2_engine+22 L4_moat+5 L6_runway+1 dislocation+2
 30 NTC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   67.0 NARROW      1  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+5
 31 GEG  POWER      PRE_INFLECTION_CHEA nan               63.0            15  PB+12 lifecycle+45 liq+6
 32 PGC  COMPOUNDER CHEAP_QUALITY       nan               62.0             1  L1_cash+10 L1_value+43 L2_engine+6 L4_moat+5 L6_runway-2 dislocation+2 liq_rising+2
 33 HPG  CYCLICAL   cmdty_CHEAP         LOWROIC_GROWTH    62.0           486  PB+3 cmdty_pctile+17 dislocation+4 liq+8 regime+30
 34 KHP  POWER      PRE_INFLECTION_CHEA nan               61.0             0  PB+12 lifecycle+45 roe+4
 35 MWG  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    61.0           271  L1_cash+7 L1_value+35 L2_engine+3 L4_moat+5 L6_runway+5 dislocation+2 liq+8

## Prioritized TOP-20 (by 8L composite)
  HAH(108), CTG(93), HSG(93), NKG(93), NNC(92), CTR(92), ACB(91), PTB(90), FPT(89), SMC(89), SCS(88), NCT(88), MBB(87), VCB(84), FMC(81), TCB(80), PVT(76), DHA(76), BID(71), VNM(70)

## TOP-20 by route
  BANK (6): CTG(93), ACB(91), MBB(87), VCB(84), TCB(80), BID(71)
  CYCLICAL (3): HSG(93), NKG(93), SMC(89)
  SUGAR (0): 
  COMPOUNDER (11): HAH(108), NNC(92), CTR(92), PTB(90), FPT(89), SCS(88), NCT(88), FMC(81), PVT(76), DHA(76), VNM(70)

Caveat: composite is a PRIORITIZATION aid, not a buy signal. NEUTRAL state (FA/quality edge strongest in CRISIS/BEAR per fa-horizon study). Liquidity small names hard to deploy. SPECIAL_SITUATION (DGC/PAT) carry event risk not in score.