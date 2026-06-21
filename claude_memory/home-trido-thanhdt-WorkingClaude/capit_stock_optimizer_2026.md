---
name: capit-stock-optimizer-2026
description: "Capitulation stock selection optimization — feature IC analysis + before/after comparison ([REDACTED]11). Key finding: strict quality gate is most important, RSI added as secondary sort."
metadata: 
  node_type: memory
  type: project
  originSessionId: 169175c2-e4bb-43b4-990e-5ab581fd0038
---

## Capacity constraint (capit_liquidity_audit.py, [REDACTED]11)
- Tier 0+1 avg **2 stocks/event**, avg **50% fill at 10B** — structurally thin
- Only 6 unique tickers in 9 events 2018-2022: SAB(7x), VSC(4x), SCS(3x), BMP(2x), VCS, SIP
- Best bounces: VSC +31.2%, SCS +20.4%, BMP +52.1% (small mid-caps, liq 3-7B/day)
- Tier 0-2 expansion fills 79% but delta fwd60d NEGATIVE (-4 to -12pp in 2022 grind)
- **Rule: size capit sleeve 8-10B max; never force-fill with Tier 2+; hold cash if T0+1 < 5 picks**
- Tier 2 fallback only when T0+1 = 0 picks (emergency); Tier 3 watchlist only
- Updated crisis_capitulation_signal.py: now shows capacity table (deploy Xb → fills Y%), Tier 2 fallback

## Context
Ran feature IC analysis on 45,973 CRISIS-period stock-days (ticker_prune, profit_3M=T+60).
Before/after comparison: 11 washout events 2018-2023.

## Feature ICs (Spearman, directional, CRISIS washout breadth<=30%)
- pb_z: +0.398 (strongest)
- D_RSI: +0.382 (nearly equal)
- PC_6M: +0.218, D_CMB: +0.203, ID_LO_3Y: +0.200
- ROIC5Y: -0.041 (near zero — quality is risk filter, not bounce predictor)
- Pattern_Median_Profit_3Y: **-0.298 (NEGATIVE — "known bouncers" are priced in, avoid)**
- D_CMF: -0.227, D_MFI: -0.234 (negative — high money flow = already bought)

## Before/After event comparison (11 events)
- OLD (strict quality + pb_z<-1): med +8.7%, **win 91%**, P10 +7.8% ← BASELINE WINS
- BASE (relaxed quality + pb_z): same median but win drops to 73%, P10 -7.6%
- NEW composite (pbz+RSI+3Ylow): med +2.7%, win 55% ← WORSE (too few events to validate)
- CONCLUSION: strict quality gate is the critical factor for 91% win rate

## Crisis_capitulation_signal.py update ([REDACTED]11, conservative)
Changes made:
1. **NEW Tier 0**: quality_strict + golden + D_RSI<=0.35 (triple confirm)
2. **Sort within tier**: pb_z ASC → D_RSI ASC → ID_LO_3Y ASC (RSI as secondary)
3. **Sector exclusion**: ICB 86xx (BDS), 87xx (securities), 33xx (mining) — all negative IC
4. **near_lo3y flag**: ID_LO_3Y < 500 sessions shown as informational column
5. **Kept unchanged**: strict quality gate (ROE_Min5Y>=12%, ROIC5Y>=10%, FSCORE>=6) + golden (pb_z<-1)

**Why:** The choice not to REPLACE golden with composite is backed by data:
- 11-event test shows relaxing quality gate drops win from 91% → 55%
- Composite adds noise in grinding bear (2022: OLD +8.5% vs NEW -2.4%)
- RSI as secondary sort (not primary) = free improvement with no downside

## Most frequent best bouncers in CRISIS (historical top-5 Q5)
HBC(31), VGC(31), KSB(25), TNG(25), NLG(20), CTR(19), VNM(17), IJC(15), HAH(13), NT2(11)

## Sector analysis (quality-gated CRISIS)
- Best: ICB 95 (+5.5%, 69% win)
- Worst: ICB 87 (-21%, 23% win), 86 (-7.6%), 33 (-15.3%)

## Why: Strict quality gate is key
The quality filter prevents holding stocks through extended crises.
In grinding scenarios (2022), technically oversold stocks keep falling.
Quality + historically-cheap (pb_z<-1) = stocks that survived prior cycles at cheaper valuations.

**How to apply:** Do NOT soften the quality threshold when signal is dormant.
Do NOT select stocks based on Pattern_Median_Profit_3Y.
Sector exclusion is low cost, [REDACTED] apply.
