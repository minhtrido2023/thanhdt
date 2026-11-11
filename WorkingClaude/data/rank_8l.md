# 8L composite ranking — route-aware score (snapshot ~2026-05-29, market state NEUTRAL)
scored 140 tickers | weights encode: cheapness + engine/runway + cash-machine + moat + dislocation; banks=NPL-gate+PB/ROE; cyclicals=trough+dislocation+PB

  # tkr  route      verdict             engine           score     5F   liqB  components
  1 CTR  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        99.0            11  L1_cash+7 L1_value+38 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+8 liq+6
  2 NNC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        94.5 NARROW      2  L1_cash+7 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+8 dislocation+8 liq+2 liq_rising+2
  3 NCT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        94.5 NARROW      1  L1_cash+7 L1_value+43 L2_engine+22 L4_moat+15 L6_runway+8 dislocation+2 liq_rising+2
  4 PTB  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       93.0             3  L1_cash+10 L1_value+40 L2_engine+22 L3_cash+10 L4_moat+5 L6_runway+1 dislocation+8 liq+2
  5 FPT  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        91.5 NARROW    423  L1_cash+1 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq+8 liq_rising+2
  6 HAH  COMPOUNDER CHEAP_QUALITY       COMPOUNDER◆       90.0            33  L1_cash+13 L1_value+32 L2_engine+22 L3_cash+10 L4_moat+10 L5_margin-12 L6_runway+8 dislocation+5 liq+6
  7 SCS  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        89.5 NARROW      7  L1_cash+7 L1_value+34 L2_engine+22 L4_moat+15 L6_runway+5 dislocation+5 liq+4 liq_rising+2
  8 SMC  CYCLICAL   TROUGH_BUY          nan               87.6             1  PB+6 cmdty_pctile+20 dislocation+15 liq_rising+2 regime+45
  9 TCL  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        86.5             0  L1_cash+10 L1_value+40 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+2 liq_rising+2
 10 VGC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        84.5 NARROW     31  L1_cash+4 L1_value+39 L2_engine+22 L4_moat+5 L6_runway+1 L8_hybrid+5 dislocation+5 liq+6 liq_rising+2
 11 FMC  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH◆   81.5             1  L1_cash+13 L1_value+43 L2_engine+3 L3_cash+10 L4_moat+5 L6_runway+8 dislocation+2 liq_rising+2
 12 LIX  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        78.0             1  L1_value+36 L2_engine+22 L4_moat+10 L6_runway+5 dislocation+8 liq_rising+2
 13 NKG  CYCLICAL   cmdty_CHEAP         nan               77.6            81  PB+10 cmdty_pctile+20 dislocation+8 liq+8 liq_rising+2 regime+30
 14 VNM  COMPOUNDER CHEAP_QUALITY       -                 75.3   WIDE    124  L1_cash+4 L1_value+43 L2_engine+6 L4_moat+12 L6_runway+1 dislocation+5 liq+8 moat5f_dur+1
 15 PVT  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    75.0           130  L1_cash+10 L1_value+40 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+5 liq+8
 16 HSG  CYCLICAL   cmdty_CHEAP         nan               71.6            42  PB+10 cmdty_pctile+20 dislocation+4 liq+6 liq_rising+2 regime+30
 17 DHA  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        71.5 NARROW      1  L1_value+41 L2_engine+22 L4_moat+10 L6_runway+1 dislocation+2
 18 KTS  SUGAR      TREND_DIP_BUY       nan               70.2             0  PB+8 cmdty_trend+10 dip+10 regime+40 roe+2
 19 IDC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   70.0 NARROW     38  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+15 L8_pbfloor+2 dislocation+5 liq+6
 20 SIP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER ASSE   70.0             5  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 dislocation+2 liq+4 liq_rising+2
 21 GAS  COMPOUNDER CHEAP_QUALITY       -                 68.5            86  L1_cash+4 L1_value+36 L2_engine+6 L4_moat+10 L6_runway+1 dislocation+8 liq+8
 22 DMC  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        68.0             0  L1_value+42 L2_engine+22 L4_moat+5 L6_runway+1 dislocation+2
 23 NTP  COMPOUNDER CHEAP_QUALITY       COMPOUNDER        66.5 NARROW      9  L1_cash+4 L1_value+38 L2_engine+22 L4_moat+10 L5_margin-12 L6_runway+5 liq+4
 24 HPG  CYCLICAL   cmdty_CHEAP         LOWROIC_GROWTH    64.6           433  PB+3 cmdty_pctile+20 dislocation+4 liq+8 regime+30
 25 BWE  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    64.5 NARROW      3  L1_cash+7 L1_value+42 L2_engine+3 L4_moat+5 L6_runway+8 liq+2 liq_rising+2
 26 PVP  COMPOUNDER CHEAP_QUALITY       nan               63.0            24  L1_cash+10 L1_value+38 L2_engine+6 L4_moat+5 L6_runway-2 dislocation+5 liq+6
 27 PGD  COMPOUNDER CHEAP_QUALITY       nan               62.0             0  L1_cash+7 L1_value+40 L2_engine+6 L4_moat+10 L6_runway-2 dislocation+5
 28 PHP  COMPOUNDER CHEAP_QUALITY       LOWROIC_GROWTH    61.0            22  L1_cash+1 L1_value+38 L2_engine+3 L4_moat+5 L6_runway+8 dislocation+2 liq+6 liq_rising+2
 29 PVS  COMPOUNDER CHEAP_QUALITY       nan               61.0            80  L1_cash+4 L1_value+42 L2_engine+6 L6_runway-2 dislocation+8 liq+8
 30 SLS  SUGAR      TREND_UP            nan               60.2 NARROW      0  PB+8 cmdty_trend+10 dip+6 regime+28 roe+8
 31 PGC  COMPOUNDER CHEAP_QUALITY       nan               59.5             1  L1_cash+10 L1_value+43 L2_engine+6 L4_moat+5 L6_runway-2 dislocation+2
 32 GEG  POWER      PRE_INFLECTION_CHEA nan               59.0             3  PB+12 lifecycle+45 liq+2
 33 BMP  COMPOUNDER CHEAP_1lens         COMPOUNDER        57.5 NARROW     10  L1_cash+4 L1_value+15 L2_engine+22 L4_moat+15 L5_margin-12 L6_runway+5 dislocation+5 liq+6 liq_rising+2
 34 KHP  POWER      PRE_INFLECTION_CHEA nan               57.0             0  PB+12 lifecycle+45
 35 NTC  COMPOUNDER VALUE_TRAP          COMPOUNDER ASSE   56.0 NARROW      1  L2_engine+22 L4_moat+15 L6_runway+5 L8_backlog+20 L8_trap-10 dislocation+2 liq_rising+2

## Prioritized TOP-20 (by 8L composite)
  CTR(99), NNC(94), NCT(94), PTB(93), FPT(92), HAH(90), SCS(90), SMC(88), TCL(86), VGC(84), FMC(82), LIX(78), NKG(78), VNM(75), PVT(75), HSG(72), DHA(72), KTS(70), IDC(70), SIP(70)

## TOP-20 by route
  BANK (0): 
  CYCLICAL (3): SMC(88), NKG(78), HSG(72)
  SUGAR (1): KTS(70)
  COMPOUNDER (16): CTR(99), NNC(94), NCT(94), PTB(93), FPT(92), HAH(90), SCS(90), TCL(86), VGC(84), FMC(82), LIX(78), VNM(75), PVT(75), DHA(72), IDC(70), SIP(70)

Caveat: composite is a PRIORITIZATION aid, not a buy signal. NEUTRAL state (FA/quality edge strongest in CRISIS/BEAR per fa-horizon study). Liquidity small names hard to deploy. SPECIAL_SITUATION (DGC/PAT) carry event risk not in score.