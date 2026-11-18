# 8L composite ranking — route-aware score (snapshot ~2026-05-29, market state NEUTRAL)
scored 140 tickers | weights encode: cheapness + engine/runway + cash-machine + moat + dislocation; banks=NPL-gate+PB/ROE; cyclicals=trough+dislocation+PB

  # tkr  route      verdict             engine           score     5F   liqB  components
  1 CTR  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        99.8            11  L1_cash+7 L1_value+38 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+8 liq+6
  2 NCT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        94.3 NARROW      2  L1_cash+7 L1_value+43 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+2 liq_rising+2
  3 NNC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        94.3 NARROW      2  L1_cash+7 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+8 dislocation+8 liq+2 liq_rising+2
  4 PTB  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       93.3             2  L1_cash+10 L1_value+40 L2_engine+22 L3_cash+10 L4_moat+5 L6_runway+1 dislocation+8 liq+2
  5 HAH  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       93.3            27  L1_cash+13 L1_value+33 L2_engine+22 L3_cash+10 L4_moat+10 L5_margin-12 L6_runway+8 dislocation+8 liq+6
  6 FPT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        91.3 NARROW    484  L1_cash+1 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq+8 liq_rising+2
  7 VGC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        90.8 NARROW     27  L1_cash+7 L1_value+40 L2_engine+22 L4_moat+5 L6_runway+1 L8_hybrid+5 dislocation+8 liq+6 liq_rising+2
  8 SCS  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        87.8 NARROW      4  L1_cash+7 L1_value+34 L2_engine+22 L4_moat+15 L6_runway+5 dislocation+5 liq+4
  9 SMC  CYCLICAL   TROUGH_BUY          nan               87.6             1  PB+6 cmdty_pctile+20 dislocation+15 liq_rising+2 regime+45
 10 TCL  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        86.3             1  L1_cash+10 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+2 liq_rising+2
 11 FMC  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH◆   81.3             1  L1_cash+13 L1_value+43 L2_engine+3 L3_cash+10 L4_moat+5 L6_runway+8 dislocation+2 liq_rising+2
 12 PVT  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    80.3           105  L1_cash+10 L1_value+43 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+8 liq+8
 13 LIX  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        78.3             0  L1_value+36 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq_rising+2
 14 NKG  CYCLICAL   cmdty_CHEAP         nan               77.6            81  PB+10 cmdty_pctile+20 dislocation+8 liq+8 liq_rising+2 regime+30
 15 HSG  CYCLICAL   cmdty_CHEAP         nan               75.6            34  PB+10 cmdty_pctile+20 dislocation+8 liq+6 liq_rising+2 regime+30
 16 VNM  COMPOUNDER CHEAP_QUALITY       -                 75.1   WIDE    124  L1_cash+4 L1_value+43 L2_engine+6 L4_moat+12 L6_runway+1 dislocation+5 liq+8 moat5f_dur+1
 17 HPG  CYCLICAL   cmdty_CHEAP         LOWROIC_GROWTH    71.6           387  PB+6 cmdty_pctile+20 dislocation+8 liq+8 regime+30
 18 DHA  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        70.8 NARROW      1  L1_value+40 L2_engine+22 L4_moat+10 L6_runway+1 liq_rising+2
 19 KTS  SUGAR      TREND_DIP_BUY       nan               70.2             0  PB+8 cmdty_trend+10 dip+10 regime+40 roe+2
 20 IDC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   70.0 NARROW     36  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+15 L8_pbfloor+2 dislocation+5 liq+6
 21 SIP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   70.0             7  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+2 liq+4 liq_rising+2
 22 NTP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        69.3 NARROW      9  L1_cash+4 L1_value+39 L2_engine+22 L4_moat+10 L5_margin-12 L6_runway+5 dislocation+2 liq+4
 23 GAS  COMPOUNDER CHEAP_QUALITY       -                 69.3            76  L1_cash+4 L1_value+37 L2_engine+6 L4_moat+10 L6_runway+1 dislocation+8 liq+8
 24 DMC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        68.3             0  L1_value+43 L2_engine+22 L4_moat+5 L6_runway+1 dislocation+2
 25 BWE  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    66.8 NARROW      3  L1_cash+7 L1_value+42 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+2 liq+2 liq_rising+2
 26 PVP  COMPOUNDER CHEAP_QUALITY       nan               66.8            18  L1_cash+10 L1_value+38 L2_engine+6 L4_moat+5 L6_runway-2 dislocation+8 liq+6
 27 PGD  COMPOUNDER CHEAP_QUALITY       nan               62.3             0  L1_cash+7 L1_value+41 L2_engine+6 L4_moat+10 L6_runway-2 dislocation+5
 28 SLS  SUGAR      TREND_UP            nan               62.2 NARROW      0  PB+8 cmdty_trend+10 dip+6 liq_rising+2 regime+28 roe+8
 29 PVS  COMPOUNDER CHEAP_QUALITY       nan               61.3            71  L1_cash+4 L1_value+42 L2_engine+6 L6_runway-2 dislocation+8 liq+8
 30 PHP  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    60.8            22  L1_cash+1 L1_value+38 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+2 liq+6 liq_rising+2
 31 PGC  COMPOUNDER CHEAP_QUALITY       nan               59.3             1  L1_cash+10 L1_value+43 L2_engine+6 L4_moat+5 L6_runway-2 dislocation+2
 32 GEG  POWER      PRE_INFLECTION_CHEA nan               59.0             3  PB+12 lifecycle+45 liq+2
 33 PLX  COMPOUNDER CHEAP_QUALITY       nan               58.8           103  L1_cash+4 L1_value+40 L2_engine+6 L6_runway-2 dislocation+8 liq+8
 34 KHP  POWER      PRE_INFLECTION_CHEA nan               57.0             0  PB+12 lifecycle+45
 35 MWG  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    56.8           184  L1_value+36 L2_engine+3 L4_moat+5 L6_runway+5 dislocation+5 liq+8

## Prioritized TOP-20 (by 8L composite)
  CTR(100), NCT(94), NNC(94), PTB(93), HAH(93), FPT(91), VGC(91), SCS(88), SMC(88), TCL(86), FMC(81), PVT(80), LIX(78), NKG(78), HSG(76), VNM(75), HPG(72), DHA(71), KTS(70), IDC(70)

## TOP-20 by route
  BANK (0): 
  CYCLICAL (4): SMC(88), NKG(78), HSG(76), HPG(72)
  SUGAR (1): KTS(70)
  COMPOUNDER (15): CTR(100), NCT(94), NNC(94), PTB(93), HAH(93), FPT(91), VGC(91), SCS(88), TCL(86), FMC(81), PVT(80), LIX(78), VNM(75), DHA(71), IDC(70)

Caveat: composite is a PRIORITIZATION aid, not a buy signal. NEUTRAL state (FA/quality edge strongest in CRISIS/BEAR per fa-horizon study). Liquidity small names hard to deploy. SPECIAL_SITUATION (DGC/PAT) carry event risk not in score.