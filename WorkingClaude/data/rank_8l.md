# 8L composite ranking — route-aware score (snapshot ~2026-05-29, market state NEUTRAL)
scored 140 tickers | weights encode: cheapness + engine/runway + cash-machine + moat + dislocation; banks=NPL-gate+PB/ROE; cyclicals=trough+dislocation+PB

  # tkr  route      verdict             engine           score     5F   liqB  components
  1 HAH  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆      108.7            61  L1_cash+13 L1_value+34 L2_engine+22 L3_cash+10 L4_moat+10 L6_runway+8 dislocation+5 liq+8 liq_rising+2
  2 FPT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        93.2 NARROW    300  L1_cash+4 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq+8
  3 CTR  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        92.7            15  L1_cash+4 L1_value+36 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+5 liq+6
  4 PTB  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       91.7             4  L1_cash+4 L1_value+40 L2_engine+22 L3_cash+10 L4_moat+5 L6_runway+1 dislocation+8 liq+4 liq_rising+2
  5 NKG  CYCLICAL   TROUGH_BUY          nan               91.6            36  PB+10 cmdty_pctile+17 dislocation+12 liq+6 liq_rising+2 regime+45
  6 NNC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        91.2 NARROW      2  L1_cash+7 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+8 dislocation+8
  7 SCS  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        90.7 NARROW      6  L1_cash+7 L1_value+34 L2_engine+22 L4_moat+15 L6_runway+5 dislocation+5 liq+4 liq_rising+2
  8 NCT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        86.2 NARROW      1  L1_value+43 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+2
  9 SMC  CYCLICAL   TROUGH_BUY          nan               85.6             1  PB+10 cmdty_pctile+17 dislocation+12 liq_rising+2 regime+45
 10 FMC  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH◆   80.2             1  L1_cash+13 L1_value+41 L2_engine+3 L3_cash+10 L4_moat+5 L6_runway+8 dislocation+2 liq_rising+2
 11 LIX  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        77.7             0  L1_value+34 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq_rising+2
 12 VNM  COMPOUNDER CHEAP_QUALITY       -                 72.5   WIDE    162  L1_cash+4 L1_value+43 L2_engine+6 L4_moat+12 L6_runway+1 dislocation+2 liq+8 moat5f_dur+0
 13 TCL  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        71.7             0  L1_value+34 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+2 liq_rising+2
 14 IDC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   70.0 NARROW     46  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+15 L8_pbfloor+2 dislocation+5 liq+6
 15 PVT  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    69.7           186  L1_cash+10 L1_value+36 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+2 liq+8 liq_rising+2
 16 HSG  CYCLICAL   cmdty_CHEAP         nan               68.6            33  PB+10 cmdty_pctile+17 dislocation+4 liq+6 liq_rising+2 regime+30
 17 KTS  SUGAR      TREND_DIP_BUY       nan               66.8             0  PB+8 cmdty_trend+7 dip+10 regime+40 roe+2
 18 DHA  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        66.7 NARROW      1  L1_value+36 L2_engine+22 L4_moat+10 L6_runway+1 dislocation+2
 19 SIP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   66.0             3  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+2 liq+2
 20 NTP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        65.7 NARROW      8  L1_value+38 L2_engine+22 L4_moat+10 L5_margin-12 L6_runway+5 dislocation+2 liq+4
 21 DMC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        65.7             0  L1_value+42 L2_engine+22 L4_moat+5 L6_runway+1
 22 BWE  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    65.2 NARROW      3  L1_cash+7 L1_value+40 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+2 liq+2 liq_rising+2
 23 PVS  COMPOUNDER CHEAP_QUALITY       nan               62.7           112  L1_cash+4 L1_value+40 L2_engine+6 L6_runway-2 dislocation+8 liq+8 liq_rising+2
 24 HPG  CYCLICAL   cmdty_CHEAP         LOWROIC_GROWTH    61.6           404  PB+3 cmdty_pctile+17 dislocation+4 liq+8 regime+30
 25 PVP  COMPOUNDER CHEAP_QUALITY       nan               59.7            34  L1_cash+10 L1_value+34 L2_engine+6 L4_moat+5 L6_runway-2 dislocation+2 liq+6 liq_rising+2
 26 GEG  POWER      PRE_INFLECTION_CHEA nan               59.0             3  PB+12 lifecycle+45 liq+2
 27 OIL  COMPOUNDER CHEAP_QUALITY       nan               58.2            25  L1_cash+7 L1_value+35 L2_engine+6 L6_runway-2 dislocation+8 liq+6 liq_rising+2
 28 PGC  COMPOUNDER CHEAP_QUALITY       nan               57.7             2  L1_cash+10 L1_value+40 L2_engine+6 L4_moat+5 L6_runway-2 liq_rising+2
 29 KHP  POWER      PRE_INFLECTION_CHEA nan               57.0             0  PB+12 lifecycle+45
 30 PGD  COMPOUNDER CHEAP_QUALITY       nan               56.2             0  L1_cash+4 L1_value+40 L2_engine+6 L4_moat+10 L6_runway-2 dislocation+2
 31 NTC  COMPOUNDER VALUE_TRAP          COMPOUNDER ASSE   56.0 NARROW      1  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 L8_trap-10 dislocation+2 liq_rising+2
 32 VNA  COMPOUNDER CHEAP_QUALITY       nan               55.7             0  L1_cash+7 L1_value+38 L2_engine+6 L4_moat+15 L5_margin-12 L6_runway-2 dislocation+8
 33 PVD  COMPOUNDER CHEAP_QUALITY       nan               55.2            63  L1_cash+4 L1_value+35 L2_engine+6 L6_runway-2 dislocation+8 liq+8
 34 MCM  COMPOUNDER CHEAP_QUALITY       -                 53.2             1  L1_cash+1 L1_value+40 L2_engine+6 L4_moat+5 L6_runway+1 dislocation+2 liq_rising+2
 35 DTD  COMPOUNDER VALUE_TRAP          COMPOUNDER ASSE   53.0 NARROW      1  L2_engine+22 L4_moat+10 L6_runway+5 L8_backlog+10 L8_pbfloor+8 L8_trap-10 dislocation+8

## Prioritized TOP-20 (by 8L composite)
  HAH(109), FPT(93), CTR(93), PTB(92), NKG(92), NNC(91), SCS(91), NCT(86), SMC(86), FMC(80), LIX(78), VNM(72), TCL(72), IDC(70), PVT(70), HSG(69), KTS(67), DHA(67), SIP(66), NTP(66)

## TOP-20 by route
  BANK (0): 
  CYCLICAL (3): NKG(92), SMC(86), HSG(69)
  SUGAR (1): KTS(67)
  COMPOUNDER (16): HAH(109), FPT(93), CTR(93), PTB(92), NNC(91), SCS(91), NCT(86), FMC(80), LIX(78), VNM(72), TCL(72), IDC(70), PVT(70), DHA(67), SIP(66), NTP(66)

Caveat: composite is a PRIORITIZATION aid, not a buy signal. NEUTRAL state (FA/quality edge strongest in CRISIS/BEAR per fa-horizon study). Liquidity small names hard to deploy. SPECIAL_SITUATION (DGC/PAT) carry event risk not in score.