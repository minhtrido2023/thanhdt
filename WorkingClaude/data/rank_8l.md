# 8L composite ranking — route-aware score (snapshot ~2026-05-29, market state NEUTRAL)
scored 140 tickers | weights encode: cheapness + engine/runway + cash-machine + moat + dislocation; banks=NPL-gate+PB/ROE; cyclicals=trough+dislocation+PB

  # tkr  route      verdict             engine           score     5F   liqB  components
  1 CTR  COMPOUNDER CHEAP_QUALITY       COMPOUNDER       101.4            13  L1_cash+7 L1_value+38 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+8 liq+6 liq_rising+2
  2 NCT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        94.4 NARROW      2  L1_cash+7 L1_value+43 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+2 liq_rising+2
  3 NNC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        94.4 NARROW      3  L1_cash+7 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+8 dislocation+8 liq+2 liq_rising+2
  4 PTB  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       93.4             2  L1_cash+10 L1_value+40 L2_engine+22 L3_cash+10 L4_moat+5 L6_runway+1 dislocation+8 liq+2
  5 HAH  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       92.9            25  L1_cash+13 L1_value+32 L2_engine+22 L3_cash+10 L4_moat+10 L5_margin-12 L6_runway+8 dislocation+8 liq+6
  6 SMC  CYCLICAL   TROUGH_BUY          nan               91.6             1  PB+10 cmdty_pctile+20 dislocation+15 liq_rising+2 regime+45
  7 FPT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        91.4 NARROW    531  L1_cash+1 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq+8 liq_rising+2
  8 TCL  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        86.4             0  L1_cash+10 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+2 liq_rising+2
  9 VGC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        85.9 NARROW     16  L1_cash+4 L1_value+40 L2_engine+22 L4_moat+5 L6_runway+1 L8_hybrid+5 dislocation+8 liq+6
 10 SCS  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        85.9 NARROW      4  L1_cash+7 L1_value+34 L2_engine+22 L4_moat+15 L6_runway+5 dislocation+5 liq+2
 11 FMC  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH◆   84.4             1  L1_cash+13 L1_value+43 L2_engine+3 L3_cash+10 L4_moat+5 L6_runway+8 dislocation+5 liq_rising+2
 12 NKG  CYCLICAL   cmdty_CHEAP         nan               81.6            74  PB+10 cmdty_pctile+20 dislocation+12 liq+8 liq_rising+2 regime+30
 13 PVT  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    80.4           102  L1_cash+10 L1_value+43 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+8 liq+8
 14 LIX  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        78.9             0  L1_value+36 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq_rising+2
 15 VNM  COMPOUNDER CHEAP_QUALITY       -                 77.2   WIDE    138  L1_cash+4 L1_value+43 L2_engine+6 L4_moat+12 L6_runway+1 dislocation+5 liq+8 liq_rising+2 moat5f_dur+1
 16 HSG  CYCLICAL   cmdty_CHEAP         nan               73.6            33  PB+10 cmdty_pctile+20 dislocation+8 liq+6 regime+30
 17 SIP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   73.0             6  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+5 liq+4 liq_rising+2
 18 HPG  CYCLICAL   cmdty_CHEAP         LOWROIC_GROWTH    71.6           386  PB+6 cmdty_pctile+20 dislocation+8 liq+8 regime+30
 19 DHA  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        70.4 NARROW      1  L1_value+40 L2_engine+22 L4_moat+10 L6_runway+1 liq_rising+2
 20 KTS  SUGAR      TREND_DIP_BUY       nan               70.2             0  PB+8 cmdty_trend+10 dip+10 regime+40 roe+2
 21 IDC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   70.0 NARROW     34  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+15 L8_pbfloor+2 dislocation+5 liq+6
 22 NTP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        69.4 NARROW      9  L1_cash+4 L1_value+39 L2_engine+22 L4_moat+10 L5_margin-12 L6_runway+5 dislocation+2 liq+4
 23 GAS  COMPOUNDER CHEAP_QUALITY       -                 69.4            69  L1_cash+4 L1_value+37 L2_engine+6 L4_moat+10 L6_runway+1 dislocation+8 liq+8
 24 DMC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        67.9             0  L1_value+42 L2_engine+22 L4_moat+5 L6_runway+1 dislocation+2
 25 PVP  COMPOUNDER CHEAP_QUALITY       nan               66.9            18  L1_cash+10 L1_value+38 L2_engine+6 L4_moat+5 L6_runway-2 dislocation+8 liq+6
 26 BWE  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    64.9 NARROW      3  L1_cash+7 L1_value+42 L2_engine+3 L4_moat+5 L6_runway+8 liq+2 liq_rising+2
 27 PGD  COMPOUNDER CHEAP_QUALITY       nan               62.4             0  L1_cash+7 L1_value+41 L2_engine+6 L4_moat+10 L6_runway-2 dislocation+5
 28 PVS  COMPOUNDER CHEAP_QUALITY       nan               61.4            67  L1_cash+4 L1_value+42 L2_engine+6 L6_runway-2 dislocation+8 liq+8
 29 PHP  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    60.9            21  L1_cash+1 L1_value+38 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+2 liq+6 liq_rising+2
 30 SLS  SUGAR      TREND_UP            nan               60.2 NARROW      0  PB+8 cmdty_trend+10 dip+6 regime+28 roe+8
 31 PGC  COMPOUNDER CHEAP_QUALITY       nan               59.4             1  L1_cash+10 L1_value+43 L2_engine+6 L4_moat+5 L6_runway-2 dislocation+2
 32 GEG  POWER      PRE_INFLECTION_CHEA nan               59.0             3  PB+12 lifecycle+45 liq+2
 33 PLX  COMPOUNDER CHEAP_QUALITY       nan               58.9            94  L1_cash+4 L1_value+40 L2_engine+6 L6_runway-2 dislocation+8 liq+8
 34 KHP  POWER      PRE_INFLECTION_CHEA nan               57.0             0  PB+12 lifecycle+45
 35 MWG  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    56.9           179  L1_value+36 L2_engine+3 L4_moat+5 L6_runway+5 dislocation+5 liq+8

## Prioritized TOP-20 (by 8L composite)
  CTR(101), NCT(94), NNC(94), PTB(93), HAH(93), SMC(92), FPT(91), TCL(86), VGC(86), SCS(86), FMC(84), NKG(82), PVT(80), LIX(79), VNM(77), HSG(74), SIP(73), HPG(72), DHA(70), KTS(70)

## TOP-20 by route
  BANK (0): 
  CYCLICAL (4): SMC(92), NKG(82), HSG(74), HPG(72)
  SUGAR (1): KTS(70)
  COMPOUNDER (15): CTR(101), NCT(94), NNC(94), PTB(93), HAH(93), FPT(91), TCL(86), VGC(86), SCS(86), FMC(84), PVT(80), LIX(79), VNM(77), SIP(73), DHA(70)

Caveat: composite is a PRIORITIZATION aid, not a buy signal. NEUTRAL state (FA/quality edge strongest in CRISIS/BEAR per fa-horizon study). Liquidity small names hard to deploy. SPECIAL_SITUATION (DGC/PAT) carry event risk not in score.