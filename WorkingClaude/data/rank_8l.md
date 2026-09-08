# 8L composite ranking — route-aware score (snapshot ~2026-05-29, market state NEUTRAL)
scored 140 tickers | weights encode: cheapness + engine/runway + cash-machine + moat + dislocation; banks=NPL-gate+PB/ROE; cyclicals=trough+dislocation+PB

  # tkr  route      verdict             engine           score     5F   liqB  components
  1 HAH  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆      108.4            34  L1_cash+13 L1_value+36 L2_engine+22 L3_cash+10 L4_moat+10 L6_runway+8 dislocation+8 liq+6
  2 HSG  CYCLICAL   TROUGH_BUY          nan               94.0            24  PB+10 cmdty_pctile+18 dislocation+15 liq+6 regime+45
  3 NKG  CYCLICAL   TROUGH_BUY          nan               94.0            16  PB+10 cmdty_pctile+18 dislocation+15 liq+6 regime+45
  4 CTR  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        91.9            21  L1_cash+4 L1_value+36 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+5 liq+6
  5 NNC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        91.4 NARROW      2  L1_cash+7 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+8 dislocation+8
  6 PTB  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       89.9             3  L1_cash+4 L1_value+40 L2_engine+22 L3_cash+10 L4_moat+5 L6_runway+1 dislocation+8 liq+2 liq_rising+2
  7 FPT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        88.9 NARROW    453  L1_cash+1 L1_value+39 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq+8
  8 SCS  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        88.4 NARROW      5  L1_cash+7 L1_value+34 L2_engine+22 L4_moat+15 L6_runway+5 dislocation+5 liq+4
  9 SMC  CYCLICAL   TROUGH_BUY          nan               88.0             2  PB+10 cmdty_pctile+18 dislocation+15 regime+45
 10 NCT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        87.9 NARROW      2  L1_value+43 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+2 liq+2
 11 FMC  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH◆   82.4             0  L1_cash+13 L1_value+42 L2_engine+3 L3_cash+10 L4_moat+5 L6_runway+8 dislocation+5
 12 PVT  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    74.9            96  L1_cash+10 L1_value+38 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+5 liq+8 liq_rising+2
 13 IDC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   73.0 NARROW     35  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+15 L8_pbfloor+2 dislocation+8 liq+6
 14 DHA  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        72.9 NARROW      2  L1_value+37 L2_engine+22 L4_moat+10 L6_runway+1 dislocation+5 liq_rising+2
 15 VNM  COMPOUNDER CHEAP_QUALITY       -                 71.7   WIDE    232  L1_cash+4 L1_value+42 L2_engine+6 L4_moat+12 L6_runway+1 dislocation+2 liq+8 moat5f_dur+0
 16 BMP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        70.4 NARROW     12  L1_cash+1 L1_value+32 L2_engine+22 L4_moat+15 L5_margin-12 L6_runway+5 dislocation+5 liq+6
 17 NTP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        69.9 NARROW     10  L1_value+39 L2_engine+22 L4_moat+10 L5_margin-12 L6_runway+5 dislocation+2 liq+6 liq_rising+2
 18 LIX  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        69.9             0  L1_value+27 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq_rising+2
 19 TCL  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        69.4             0  L1_value+34 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+2
 20 NTC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   69.0 NARROW      1  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+5 liq_rising+2
 21 SIP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   66.0             4  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+2 liq+2
 22 BWE  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    64.9 NARROW      3  L1_cash+7 L1_value+40 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+2 liq+2 liq_rising+2
 23 DMC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        63.9             0  L1_cash+1 L1_value+39 L2_engine+22 L4_moat+5 L6_runway+1
 24 MWG  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    63.9           247  L1_cash+7 L1_value+35 L2_engine+3 L4_moat+5 L6_runway+5 dislocation+5 liq+8
 25 HPG  CYCLICAL   cmdty_CHEAP         LOWROIC_GROWTH    63.0           423  PB+3 cmdty_pctile+18 dislocation+4 liq+8 regime+30
 26 PLX  COMPOUNDER CHEAP_QUALITY       nan               62.9           153  L1_cash+7 L1_value+38 L2_engine+6 L6_runway-2 dislocation+8 liq+8 liq_rising+2
 27 PGC  COMPOUNDER CHEAP_QUALITY       nan               61.9             1  L1_cash+10 L1_value+43 L2_engine+6 L4_moat+5 L6_runway-2 dislocation+2 liq_rising+2
 28 GEG  POWER      PRE_INFLECTION_CHEA nan               59.0             3  PB+12 lifecycle+45 liq+2
 29 PVP  COMPOUNDER CHEAP_QUALITY       nan               57.9            11  L1_cash+10 L1_value+37 L2_engine+6 L4_moat+5 L6_runway-2 liq+6
 30 KHP  POWER      PRE_INFLECTION_CHEA nan               57.0             0  PB+12 lifecycle+45
 31 VGC  COMPOUNDER CHEAP_1lens         COMPOUNDER        55.9 NARROW     15  L1_value+16 L2_engine+22 L4_moat+5 L6_runway+1 L8_hybrid+5 dislocation+5 liq+6
 32 OIL  COMPOUNDER CHEAP_QUALITY       nan               55.4            19  L1_cash+7 L1_value+34 L2_engine+6 L6_runway-2 dislocation+8 liq+6
 33 DTD  COMPOUNDER VALUE_TRAP          COMPOUNDER ASSE   55.0 NARROW      2  L2_engine+22 L4_moat+10 L6_runway+5 L8_backlog+10 L8_pbfloor+8 L8_trap-10 dislocation+8 liq_rising+2
 34 PVD  COMPOUNDER CHEAP_QUALITY       nan               54.9            70  L1_cash+4 L1_value+35 L2_engine+6 L6_runway-2 dislocation+8 liq+8
 35 PVS  COMPOUNDER CHEAP_QUALITY       nan               54.9           111  L1_cash+1 L1_value+41 L2_engine+6 L6_runway-2 dislocation+5 liq+8

## Prioritized TOP-20 (by 8L composite)
  HAH(108), HSG(94), NKG(94), CTR(92), NNC(91), PTB(90), FPT(89), SCS(88), SMC(88), NCT(88), FMC(82), PVT(75), IDC(73), DHA(73), VNM(72), BMP(70), NTP(70), LIX(70), TCL(69), NTC(69)

## TOP-20 by route
  BANK (0): 
  CYCLICAL (3): HSG(94), NKG(94), SMC(88)
  SUGAR (0): 
  COMPOUNDER (17): HAH(108), CTR(92), NNC(91), PTB(90), FPT(89), SCS(88), NCT(88), FMC(82), PVT(75), IDC(73), DHA(73), VNM(72), BMP(70), NTP(70), LIX(70), TCL(69), NTC(69)

Caveat: composite is a PRIORITIZATION aid, not a buy signal. NEUTRAL state (FA/quality edge strongest in CRISIS/BEAR per fa-horizon study). Liquidity small names hard to deploy. SPECIAL_SITUATION (DGC/PAT) carry event risk not in score.