# 8L composite ranking — route-aware score (snapshot ~2026-05-29, market state NEUTRAL)
scored 137 tickers | weights encode: cheapness + engine/runway + cash-machine + moat + dislocation; banks=NPL-gate+PB/ROE; cyclicals=trough+dislocation+PB

  # tkr  route      verdict             engine           score     5F   liqB  components
  1 HAH  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       97.0            25  L1_cash+13 L1_value+36 L2_engine+22 L3_cash+10 L4_moat+10 L5_margin-12 L6_runway+8 dislocation+8 liq+6
  2 CTG  BANK       CLEAN               nan               93.0             0  CAR+3 coverage+10 gate+40 npl+12 npl_trend+8 pb_vs_roe+10 roe+10
  3 NNC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        91.5 NARROW      2  L1_cash+7 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+8 dislocation+8
  4 ACB  BANK       CLEAN               nan               91.0             0  CAR+5 coverage+8 gate+40 npl+15 npl_trend+8 pb_vs_roe+7 roe+8
  5 NKG  CYCLICAL   TROUGH_BUY          nan               90.6            19  PB+10 cmdty_pctile+15 dislocation+15 liq+6 regime+45
  6 HSG  CYCLICAL   TROUGH_BUY          nan               90.6            34  PB+10 cmdty_pctile+15 dislocation+15 liq+6 regime+45
  7 NCT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        90.0 NARROW      2  L1_value+43 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+2 liq+2 liq_rising+2
  8 FPT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        90.0 NARROW    521  L1_cash+1 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq+8
  9 SCS  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        89.0 NARROW      6  L1_cash+7 L1_value+35 L2_engine+22 L4_moat+15 L6_runway+5 dislocation+5 liq+4
 10 CTR  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        88.5            21  L1_value+36 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+5 liq+6
 11 TCL  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        88.0             0  L1_cash+10 L1_value+43 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+2
 12 MBB  BANK       CLEAN               nan               87.0             0  CAR+5 coverage+5 gate+40 npl+12 npl_trend+8 pb_vs_roe+7 roe+10
 13 VCB  BANK       CLEAN               nan               84.0             0  CAR+5 coverage+10 gate+40 npl+15 npl_trend+8 pb_vs_roe+1 roe+5
 14 PTB  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       83.5             2  L1_cash+1 L1_value+40 L2_engine+22 L3_cash+10 L4_moat+5 L6_runway+1 dislocation+5 liq+2 liq_rising+2
 15 TCB  BANK       CLEAN               nan               80.0             0  CAR+6 coverage+8 gate+40 npl+12 npl_trend+5 pb_vs_roe+4 roe+5
 16 FMC  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH◆   79.5             1  L1_cash+13 L1_value+42 L2_engine+3 L3_cash+10 L4_moat+5 L6_runway+8 dislocation+2
 17 IDC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   75.0 NARROW     39  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 L8_pbfloor+2 dislocation+5 liq+6
 18 DHA  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        73.0 NARROW      1  L1_value+39 L2_engine+22 L4_moat+10 L6_runway+1 dislocation+5
 19 SIP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   71.0             7  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+5 liq+4
 20 BID  BANK       CLEAN               nan               71.0             0  CAR+1 coverage+5 gate+40 npl+8 npl_trend+5 pb_vs_roe+4 roe+8
 21 PVT  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    70.0            56  L1_value+42 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+8 liq+8
 22 LIX  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        70.0             0  L1_value+27 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq_rising+2
 23 VNM  COMPOUNDER CHEAP_QUALITY       -                 69.3   WIDE    280  L1_cash+4 L1_value+38 L2_engine+6 L4_moat+12 L6_runway+1 dislocation+2 liq+8 liq_rising+2 moat5f_dur+0
 24 BMP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        69.0 NARROW     22  L1_cash+1 L1_value+32 L2_engine+22 L4_moat+15 L5_margin-12 L6_runway+5 dislocation+2 liq+6 liq_rising+2
 25 NTC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   69.0 NARROW      1  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+5 liq_rising+2
 26 DMC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        67.5             0  L1_cash+1 L1_value+40 L2_engine+22 L4_moat+5 L6_runway+1 dislocation+2
 27 BWE  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    67.0 NARROW      5  L1_cash+7 L1_value+40 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+2 liq+4 liq_rising+2
 28 VCP  POWER      PRE_INFLECTION_CHEA nan               67.0             0  PB+12 lifecycle+45 roe+10
 29 NTP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        65.5 NARROW      3  L1_value+40 L2_engine+22 L4_moat+10 L5_margin-12 L6_runway+5 dislocation+2 liq+2
 30 HPG  CYCLICAL   cmdty_CHEAP         LOWROIC_GROWTH    63.6           540  PB+3 cmdty_pctile+15 dislocation+8 liq+8 regime+30
 31 PGC  COMPOUNDER CHEAP_QUALITY       nan               63.0             0  L1_cash+10 L1_value+43 L2_engine+6 L4_moat+5 L6_runway-2 dislocation+5
 32 GEG  POWER      PRE_INFLECTION_CHEA nan               63.0            15  PB+12 lifecycle+45 liq+6
 33 OIL  COMPOUNDER CHEAP_QUALITY       nan               62.5            24  L1_cash+10 L1_value+38 L2_engine+6 L6_runway-2 dislocation+8 liq+6
 34 TLG  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        61.3   WIDE      4  L1_cash+4 L1_value+30 L2_engine+22 L4_moat+12 L5_margin-12 L6_runway+5 dislocation+2 liq+2 moat5f_dur+0
 35 KHP  POWER      PRE_INFLECTION_CHEA nan               61.0             0  PB+12 lifecycle+45 roe+4

## Prioritized TOP-20 (by 8L composite)
  HAH(97), CTG(93), NNC(92), ACB(91), NKG(91), HSG(91), NCT(90), FPT(90), SCS(89), CTR(88), TCL(88), MBB(87), VCB(84), PTB(84), TCB(80), FMC(80), IDC(75), DHA(73), SIP(71), BID(71)

## TOP-20 by route
  BANK (6): CTG(93), ACB(91), MBB(87), VCB(84), TCB(80), BID(71)
  CYCLICAL (2): NKG(91), HSG(91)
  SUGAR (0): 
  COMPOUNDER (12): HAH(97), NNC(92), NCT(90), FPT(90), SCS(89), CTR(88), TCL(88), PTB(84), FMC(80), IDC(75), DHA(73), SIP(71)

Caveat: composite is a PRIORITIZATION aid, not a buy signal. NEUTRAL state (FA/quality edge strongest in CRISIS/BEAR per fa-horizon study). Liquidity small names hard to deploy. SPECIAL_SITUATION (DGC/PAT) carry event risk not in score.