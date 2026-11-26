# 8L composite ranking — route-aware score (snapshot ~2026-05-29, market state NEUTRAL)
scored 140 tickers | weights encode: cheapness + engine/runway + cash-machine + moat + dislocation; banks=NPL-gate+PB/ROE; cyclicals=trough+dislocation+PB

  # tkr  route      verdict             engine           score     5F   liqB  components
  1 CTR  COMPOUNDER CHEAP_QUALITY       COMPOUNDER       101.8            13  L1_cash+7 L1_value+38 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+8 liq+6 liq_rising+2
  2 NKG  CYCLICAL   TROUGH_BUY          nan               96.6            77  PB+10 cmdty_pctile+20 dislocation+12 liq+8 liq_rising+2 regime+45
  3 NNC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        94.3 NARROW      3  L1_cash+7 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+8 dislocation+8 liq+2 liq_rising+2
  4 NCT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        94.3 NARROW      2  L1_cash+7 L1_value+43 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+2 liq_rising+2
  5 HAH  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       93.3            24  L1_cash+13 L1_value+33 L2_engine+22 L3_cash+10 L4_moat+10 L5_margin-12 L6_runway+8 dislocation+8 liq+6
  6 PTB  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       92.8             2  L1_cash+10 L1_value+40 L2_engine+22 L3_cash+10 L4_moat+5 L6_runway+1 dislocation+8 liq+2
  7 SMC  CYCLICAL   TROUGH_BUY          nan               91.6             1  PB+10 cmdty_pctile+20 dislocation+15 liq_rising+2 regime+45
  8 FPT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        91.3 NARROW    514  L1_cash+1 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq+8 liq_rising+2
  9 SCS  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        90.8 NARROW      4  L1_cash+7 L1_value+34 L2_engine+22 L4_moat+15 L6_runway+5 dislocation+8 liq+4
 10 HPG  CYCLICAL   TROUGH_BUY          LOWROIC_GROWTH    90.6           388  PB+6 cmdty_pctile+20 dislocation+12 liq+8 regime+45
 11 TCL  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        89.3             0  L1_cash+10 L1_value+43 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+2 liq_rising+2
 12 VGC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        88.8 NARROW     15  L1_cash+7 L1_value+40 L2_engine+22 L4_moat+5 L6_runway+1 L8_hybrid+5 dislocation+8 liq+6
 13 FMC  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH◆   84.3             1  L1_cash+13 L1_value+43 L2_engine+3 L3_cash+10 L4_moat+5 L6_runway+8 dislocation+5 liq_rising+2
 14 PVT  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    80.3            99  L1_cash+10 L1_value+43 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+8 liq+8
 15 LIX  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        78.8             0  L1_value+36 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq_rising+2
 16 VNM  COMPOUNDER CHEAP_QUALITY       -                 77.1   WIDE    140  L1_cash+4 L1_value+43 L2_engine+6 L4_moat+12 L6_runway+1 dislocation+5 liq+8 liq_rising+2 moat5f_dur+1
 17 HSG  CYCLICAL   cmdty_CHEAP         nan               73.6            34  PB+10 cmdty_pctile+20 dislocation+8 liq+6 regime+30
 18 SIP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   73.0             6  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+5 liq+4 liq_rising+2
 19 KTS  SUGAR      TREND_DIP_BUY       nan               70.2             0  PB+8 cmdty_trend+10 dip+10 regime+40 roe+2
 20 IDC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   70.0 NARROW     33  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+15 L8_pbfloor+2 dislocation+5 liq+6
 21 GAS  COMPOUNDER CHEAP_QUALITY       -                 69.8            68  L1_cash+4 L1_value+38 L2_engine+6 L4_moat+10 L6_runway+1 dislocation+8 liq+8
 22 NTP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        69.3 NARROW      9  L1_cash+4 L1_value+39 L2_engine+22 L4_moat+10 L5_margin-12 L6_runway+5 dislocation+2 liq+4
 23 DHA  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        68.8 NARROW      1  L1_value+40 L2_engine+22 L4_moat+10 L6_runway+1
 24 DMC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        67.8             0  L1_value+42 L2_engine+22 L4_moat+5 L6_runway+1 dislocation+2
 25 PVP  COMPOUNDER CHEAP_QUALITY       nan               67.3            17  L1_cash+10 L1_value+39 L2_engine+6 L4_moat+5 L6_runway-2 dislocation+8 liq+6
 26 BWE  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    66.8 NARROW      3  L1_cash+7 L1_value+42 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+2 liq+2 liq_rising+2
 27 PGD  COMPOUNDER CHEAP_QUALITY       nan               62.8             0  L1_cash+7 L1_value+42 L2_engine+6 L4_moat+10 L6_runway-2 dislocation+5
 28 PHP  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    61.8            20  L1_cash+1 L1_value+40 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+2 liq+6 liq_rising+2
 29 PVS  COMPOUNDER CHEAP_QUALITY       nan               61.8            64  L1_cash+4 L1_value+42 L2_engine+6 L6_runway-2 dislocation+8 liq+8
 30 SLS  SUGAR      TREND_UP            nan               60.2 NARROW      0  PB+8 cmdty_trend+10 dip+6 regime+28 roe+8
 31 DPR  CYCLICAL   ELEVATED-SUPPORTED( ASSET_PLAY→NAV    59.4            11  L8_backlog+10 PB+10 cmdty_pctile+0 dislocation+15 liq+6 regime+18
 32 PGC  COMPOUNDER CHEAP_QUALITY       nan               59.3             1  L1_cash+10 L1_value+43 L2_engine+6 L4_moat+5 L6_runway-2 dislocation+2
 33 GEG  POWER      PRE_INFLECTION_CHEA nan               59.0             3  PB+12 lifecycle+45 liq+2
 34 PLX  COMPOUNDER CHEAP_QUALITY       nan               58.8            86  L1_cash+4 L1_value+40 L2_engine+6 L6_runway-2 dislocation+8 liq+8
 35 KHP  POWER      PRE_INFLECTION_CHEA nan               57.0             0  PB+12 lifecycle+45

## Prioritized TOP-20 (by 8L composite)
  CTR(102), NKG(97), NNC(94), NCT(94), HAH(93), PTB(93), SMC(92), FPT(91), SCS(91), HPG(91), TCL(89), VGC(89), FMC(84), PVT(80), LIX(79), VNM(77), HSG(74), SIP(73), KTS(70), IDC(70)

## TOP-20 by route
  BANK (0): 
  CYCLICAL (4): NKG(97), SMC(92), HPG(91), HSG(74)
  SUGAR (1): KTS(70)
  COMPOUNDER (15): CTR(102), NNC(94), NCT(94), HAH(93), PTB(93), FPT(91), SCS(91), TCL(89), VGC(89), FMC(84), PVT(80), LIX(79), VNM(77), SIP(73), IDC(70)

Caveat: composite is a PRIORITIZATION aid, not a buy signal. NEUTRAL state (FA/quality edge strongest in CRISIS/BEAR per fa-horizon study). Liquidity small names hard to deploy. SPECIAL_SITUATION (DGC/PAT) carry event risk not in score.