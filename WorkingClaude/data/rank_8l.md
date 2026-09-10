# 8L composite ranking — route-aware score (snapshot ~2026-05-29, market state NEUTRAL)
scored 140 tickers | weights encode: cheapness + engine/runway + cash-machine + moat + dislocation; banks=NPL-gate+PB/ROE; cyclicals=trough+dislocation+PB

  # tkr  route      verdict             engine           score     5F   liqB  components
  1 HAH  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆      108.5            34  L1_cash+13 L1_value+36 L2_engine+22 L3_cash+10 L4_moat+10 L6_runway+8 dislocation+8 liq+6
  2 HSG  CYCLICAL   TROUGH_BUY          nan               94.0            23  PB+10 cmdty_pctile+18 dislocation+15 liq+6 regime+45
  3 NKG  CYCLICAL   TROUGH_BUY          nan               94.0            16  PB+10 cmdty_pctile+18 dislocation+15 liq+6 regime+45
  4 CTR  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        92.0            19  L1_cash+4 L1_value+36 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+5 liq+6
  5 NNC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        91.5 NARROW      1  L1_cash+7 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+8 dislocation+8
  6 PTB  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       90.0             3  L1_cash+4 L1_value+40 L2_engine+22 L3_cash+10 L4_moat+5 L6_runway+1 dislocation+8 liq+2 liq_rising+2
  7 SCS  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        88.5 NARROW      4  L1_cash+7 L1_value+34 L2_engine+22 L4_moat+15 L6_runway+5 dislocation+5 liq+4
  8 NCT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        88.0 NARROW      2  L1_value+43 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+2 liq+2
  9 SMC  CYCLICAL   TROUGH_BUY          nan               88.0             2  PB+10 cmdty_pctile+18 dislocation+15 regime+45
 10 FPT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        85.5 NARROW    467  L1_cash+1 L1_value+38 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+5 liq+8
 11 FMC  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH◆   82.5             0  L1_cash+13 L1_value+42 L2_engine+3 L3_cash+10 L4_moat+5 L6_runway+8 dislocation+5
 12 PVT  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    74.5           108  L1_cash+10 L1_value+38 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+5 liq+8 liq_rising+2
 13 DHA  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        73.0 NARROW      2  L1_value+37 L2_engine+22 L4_moat+10 L6_runway+1 dislocation+5 liq_rising+2
 14 IDC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   73.0 NARROW     33  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+15 L8_pbfloor+2 dislocation+8 liq+6
 15 TCL  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        71.5             0  L1_value+34 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+2 liq_rising+2
 16 BMP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        70.5 NARROW     12  L1_cash+1 L1_value+32 L2_engine+22 L4_moat+15 L5_margin-12 L6_runway+5 dislocation+5 liq+6
 17 VNM  COMPOUNDER CHEAP_QUALITY       -                 68.8   WIDE    206  L1_cash+1 L1_value+42 L2_engine+6 L4_moat+12 L6_runway+1 dislocation+2 liq+8 moat5f_dur+0
 18 LIX  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        68.0             0  L1_value+27 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8
 19 NTC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   67.0 NARROW      1  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+5
 20 NTP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        66.5 NARROW     13  L1_value+38 L2_engine+22 L4_moat+10 L5_margin-12 L6_runway+5 liq+6 liq_rising+2
 21 SIP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   66.0             4  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+2 liq+2
 22 MWG  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    64.0           234  L1_cash+7 L1_value+35 L2_engine+3 L4_moat+5 L6_runway+5 dislocation+5 liq+8
 23 DMC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        63.5             0  L1_cash+1 L1_value+38 L2_engine+22 L4_moat+5 L6_runway+1
 24 PLX  COMPOUNDER CHEAP_QUALITY       nan               63.0           146  L1_cash+7 L1_value+38 L2_engine+6 L6_runway-2 dislocation+8 liq+8 liq_rising+2
 25 HPG  CYCLICAL   cmdty_CHEAP         LOWROIC_GROWTH    63.0           430  PB+3 cmdty_pctile+18 dislocation+4 liq+8 regime+30
 26 PGC  COMPOUNDER CHEAP_QUALITY       nan               62.0             1  L1_cash+10 L1_value+43 L2_engine+6 L4_moat+5 L6_runway-2 dislocation+2 liq_rising+2
 27 BWE  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    61.5 NARROW      2  L1_cash+7 L1_value+40 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+2
 28 PVP  COMPOUNDER CHEAP_QUALITY       nan               59.5            13  L1_cash+10 L1_value+36 L2_engine+6 L4_moat+5 L6_runway-2 liq+6 liq_rising+2
 29 GEG  POWER      PRE_INFLECTION_CHEA nan               59.0             3  PB+12 lifecycle+45 liq+2
 30 KHP  POWER      PRE_INFLECTION_CHEA nan               57.0             0  PB+12 lifecycle+45
 31 VNA  COMPOUNDER CHEAP_QUALITY       nan               56.0             0  L1_cash+7 L1_value+38 L2_engine+6 L4_moat+15 L5_margin-12 L6_runway-2 dislocation+8
 32 VGC  COMPOUNDER CHEAP_1lens         COMPOUNDER        55.5 NARROW     14  L1_value+16 L2_engine+22 L4_moat+5 L6_runway+1 L8_hybrid+5 dislocation+5 liq+6
 33 OIL  COMPOUNDER CHEAP_QUALITY       nan               55.5            20  L1_cash+7 L1_value+34 L2_engine+6 L6_runway-2 dislocation+8 liq+6
 34 PVD  COMPOUNDER CHEAP_QUALITY       nan               55.0            70  L1_cash+4 L1_value+35 L2_engine+6 L6_runway-2 dislocation+8 liq+8
 35 PVS  COMPOUNDER CHEAP_QUALITY       nan               55.0           110  L1_cash+1 L1_value+41 L2_engine+6 L6_runway-2 dislocation+5 liq+8

## Prioritized TOP-20 (by 8L composite)
  HAH(108), HSG(94), NKG(94), CTR(92), NNC(92), PTB(90), SCS(88), NCT(88), SMC(88), FPT(86), FMC(82), PVT(74), DHA(73), IDC(73), TCL(72), BMP(70), VNM(69), LIX(68), NTC(67), NTP(66)

## TOP-20 by route
  BANK (0): 
  CYCLICAL (3): HSG(94), NKG(94), SMC(88)
  SUGAR (0): 
  COMPOUNDER (17): HAH(108), CTR(92), NNC(92), PTB(90), SCS(88), NCT(88), FPT(86), FMC(82), PVT(74), DHA(73), IDC(73), TCL(72), BMP(70), VNM(69), LIX(68), NTC(67), NTP(66)

Caveat: composite is a PRIORITIZATION aid, not a buy signal. NEUTRAL state (FA/quality edge strongest in CRISIS/BEAR per fa-horizon study). Liquidity small names hard to deploy. SPECIAL_SITUATION (DGC/PAT) carry event risk not in score.