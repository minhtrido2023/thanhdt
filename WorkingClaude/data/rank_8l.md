# 8L composite ranking — route-aware score (snapshot ~2026-05-29, market state NEUTRAL)
scored 140 tickers | weights encode: cheapness + engine/runway + cash-machine + moat + dislocation; banks=NPL-gate+PB/ROE; cyclicals=trough+dislocation+PB

  # tkr  route      verdict             engine           score     5F   liqB  components
  1 HAH  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆      108.3            52  L1_cash+13 L1_value+34 L2_engine+22 L3_cash+10 L4_moat+10 L6_runway+8 dislocation+5 liq+8 liq_rising+2
  2 FPT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        92.8 NARROW    332  L1_cash+4 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq+8
  3 NCT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        92.8 NARROW      1  L1_cash+7 L1_value+43 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+2
  4 CTR  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        92.3            14  L1_cash+4 L1_value+36 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+5 liq+6
  5 PTB  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       91.3             4  L1_cash+4 L1_value+40 L2_engine+22 L3_cash+10 L4_moat+5 L6_runway+1 dislocation+8 liq+4 liq_rising+2
  6 NNC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        90.8 NARROW      2  L1_cash+7 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+8 dislocation+8
  7 SCS  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        90.3 NARROW      7  L1_cash+7 L1_value+34 L2_engine+22 L4_moat+15 L6_runway+5 dislocation+5 liq+4 liq_rising+2
  8 SMC  CYCLICAL   TROUGH_BUY          nan               88.6             1  PB+10 cmdty_pctile+17 dislocation+15 liq_rising+2 regime+45
  9 FMC  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH◆   81.8             1  L1_cash+13 L1_value+43 L2_engine+3 L3_cash+10 L4_moat+5 L6_runway+8 dislocation+2 liq_rising+2
 10 LIX  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        78.3             1  L1_value+36 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq_rising+2
 11 NKG  CYCLICAL   cmdty_CHEAP         nan               76.6            44  PB+10 cmdty_pctile+17 dislocation+12 liq+6 liq_rising+2 regime+30
 12 VNM  COMPOUNDER CHEAP_QUALITY       -                 72.1   WIDE    143  L1_cash+4 L1_value+43 L2_engine+6 L4_moat+12 L6_runway+1 dislocation+2 liq+8 moat5f_dur+0
 13 TCL  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        70.8             0  L1_value+34 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+2 liq_rising+2
 14 NTP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        69.8 NARROW      8  L1_cash+4 L1_value+39 L2_engine+22 L4_moat+10 L5_margin-12 L6_runway+5 dislocation+2 liq+4
 15 HSG  CYCLICAL   cmdty_CHEAP         nan               68.6            34  PB+10 cmdty_pctile+17 dislocation+4 liq+6 liq_rising+2 regime+30
 16 PVT  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    68.3           186  L1_cash+10 L1_value+34 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+2 liq+8 liq_rising+2
 17 SIP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   68.0             4  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+2 liq+4
 18 KTS  SUGAR      TREND_DIP_BUY       nan               66.8             0  PB+8 cmdty_trend+7 dip+10 regime+40 roe+2
 19 DHA  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        66.3 NARROW      1  L1_value+36 L2_engine+22 L4_moat+10 L6_runway+1 dislocation+2
 20 HPG  CYCLICAL   cmdty_CHEAP         LOWROIC_GROWTH    65.6           382  PB+3 cmdty_pctile+17 dislocation+8 liq+8 regime+30
 21 DMC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        65.3             0  L1_value+42 L2_engine+22 L4_moat+5 L6_runway+1
 22 IDC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   65.0 NARROW     47  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+15 dislocation+2 liq+6
 23 PVS  COMPOUNDER CHEAP_QUALITY       nan               62.3           107  L1_cash+4 L1_value+40 L2_engine+6 L6_runway-2 dislocation+8 liq+8 liq_rising+2
 24 BWE  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    61.8 NARROW      3  L1_cash+7 L1_value+39 L2_engine+3 L4_moat+5 L6_runway+8 liq+2 liq_rising+2
 25 PVP  COMPOUNDER CHEAP_QUALITY       nan               59.3            32  L1_cash+10 L1_value+34 L2_engine+6 L4_moat+5 L6_runway-2 dislocation+2 liq+6 liq_rising+2
 26 VOS  COMPOUNDER CHEAP_QUALITY       nan               59.3            16  L1_value+34 L2_engine+6 L4_moat+10 L6_runway-2 dislocation+8 liq+6 liq_rising+2
 27 GEG  POWER      PRE_INFLECTION_CHEA nan               59.0             3  PB+12 lifecycle+45 liq+2
 28 PGC  COMPOUNDER CHEAP_QUALITY       nan               57.8             1  L1_cash+10 L1_value+41 L2_engine+6 L4_moat+5 L6_runway-2 liq_rising+2
 29 NTC  COMPOUNDER VALUE_TRAP          COMPOUNDER ASSE   57.0 NARROW      1  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 L8_trap-10 dislocation+5
 30 KHP  POWER      PRE_INFLECTION_CHEA nan               57.0             0  PB+12 lifecycle+45
 31 SLS  SUGAR      TREND_UP            nan               56.8 NARROW      0  PB+8 cmdty_trend+7 dip+6 regime+28 roe+8
 32 OIL  COMPOUNDER CHEAP_QUALITY       nan               55.8            22  L1_cash+7 L1_value+35 L2_engine+6 L6_runway-2 dislocation+8 liq+6
 33 PGD  COMPOUNDER CHEAP_QUALITY       nan               55.8             0  L1_cash+4 L1_value+40 L2_engine+6 L4_moat+10 L6_runway-2 dislocation+2
 34 VNA  COMPOUNDER CHEAP_QUALITY       nan               55.3             0  L1_cash+7 L1_value+38 L2_engine+6 L4_moat+15 L5_margin-12 L6_runway-2 dislocation+8
 35 PVD  COMPOUNDER CHEAP_QUALITY       nan               54.8            71  L1_cash+4 L1_value+35 L2_engine+6 L6_runway-2 dislocation+8 liq+8

## Prioritized TOP-20 (by 8L composite)
  HAH(108), FPT(93), NCT(93), CTR(92), PTB(91), NNC(91), SCS(90), SMC(89), FMC(82), LIX(78), NKG(77), VNM(72), TCL(71), NTP(70), HSG(69), PVT(68), SIP(68), KTS(67), DHA(66), HPG(66)

## TOP-20 by route
  BANK (0): 
  CYCLICAL (4): SMC(89), NKG(77), HSG(69), HPG(66)
  SUGAR (1): KTS(67)
  COMPOUNDER (15): HAH(108), FPT(93), NCT(93), CTR(92), PTB(91), NNC(91), SCS(90), FMC(82), LIX(78), VNM(72), TCL(71), NTP(70), PVT(68), SIP(68), DHA(66)

Caveat: composite is a PRIORITIZATION aid, not a buy signal. NEUTRAL state (FA/quality edge strongest in CRISIS/BEAR per fa-horizon study). Liquidity small names hard to deploy. SPECIAL_SITUATION (DGC/PAT) carry event risk not in score.