---
name: bal-exbull-momentum-suppression-2026
description: BAL momentum IC inverts in EX-BULL (state5==5); suppressing momentum buys there = validated V2.3 win
metadata: 
  node_type: memory
  type: project
  originSessionId: e388f0eb-36db-4ac3-be7d-416a3f69f5f0
---

BAL/LAG deep-dive Finding #1 ([REDACTED]12), kickoff angle #1 = per-term IC attribution on `ta`.

**Diagnosis**: composite `ta` IC by DT5G state (clean LEAD fwd20, ticker_prune, liq≥1e9, 2014+): momentum block works in BULL(+0.030)/NEUTRAL(+0.059) but **INVERTS hard in EX-BULL state5==5: IC_mom −0.307**, value block stays +0.076. Structural across **3/3** EX-BULL episodes (2020 −0.11 / 2021 −0.48 / 2025 −0.14 — the only state-5 windows in DT5G history). Tier buckets in EX-BULL are monotone-inverted: ta 140-155 → fwd20 −6%/win24%; ta<70 → +5.1%/54%.

**Root cause of the 2025-08 grind START**: book's MEGA/MOMENTUM/MOMENTUM_S/S_PRO tiers fire in `state5 IN (4,5)`. Aug-Sep 2025 = 27 days EX-BULL → book bought peak momentum into euphoria top, then reversed = start of −11.8%/294d grind. Existing `overheat` guard needs VNINDEX>1.30×MA200 which NEVER fired then (index only 1.15-1.28×MA200).

**Fix** (validated faithful 2-ledger engine, real TC, 50B; `workspace/pt_v22_exbull_test.py`): in state5==5 route momentum tiers {MEGA,MOMENTUM,MOMENTUM_S,MOMENTUM_QUALITY,MOMENTUM_A,S_PRO}→AVOID_exbull; keep value tiers (DEEP_VALUE_RECOVERY/COMPOUNDER_BUY/RE_BACKLOG_BUY, +IC in EX-BULL). Removes-only → capacity-safe + causal. Result V2.2+capit: FULL 25.77→**26.09%** (DD −20.1→−20.3), **2025+ 18.30→19.85%, DD −18.7→−17.4, Sh 1.04→1.13**. BAL-leg alone: FULL MaxDD **−25.4→−20.6pp**, 2025+ CAGR 2.59→8.36%. Caveat: no-capit base FULL dips slightly (2021 price gains forgone) but production=+capit nets positive.

**⚠️ CORRECTION ([REDACTED]11, combined backtest):** the standalone "+1.5pp/2025+ 18.30→19.85%" win was a **STATE-SOURCE ARTIFACT**. The standalone test (pt_v22_exbull_test.py) triggered on `sig_b.state5` = base `vnindex_5state` (192 EXBULL days across 2017-2024) NOT the production dt5g (59 days, 2020/21/25 only; overlap just 36). On the CORRECT dt5g trigger the fix is **negligible**: BAL-leg FULL 19.01→19.05%, 2025+ 2.59→2.54%, portfolio +0.02pp. The IC inversion is real but only 59 days, few NEW entries (45d holds), and the LAG allocator already cuts BAL to 35% in EXBULL → subsumes it. **Verdict: EXBULL fix = harmless free insurance for future genuine euphoria, NOT a return driver.** The real win is the LAG allocator [[lag-bal-state-conditional-allocator-2026]]. Lesson: signal SQL joins base `vnindex_5state` (per CLAUDE.md trap), engine sizing uses dt5g — [REDACTED] trigger regime logic on dt5g.

**NOT yet deployed live** (needs user OK). Deploy = mirror overheat guard in `pt_v22_dt5g.py` after ~line 220, triggering on dt5g `state`. Dormant today (DT5G live = NEUTRAL).

**Finding #2 (angle #2, same session) — NEUTRAL grind persistence is NOT momentum-selection-fixable** (`workspace/bal_lag_finding2_neutral_grind.md`): momentum-of-momentum gate works pooled (NEUTRAL trail120<0 → IC 0.07→−0.01) but stayed POSITIVE through 2025-08+ grind → didn't flag it. The grind = EW quality universe absolutely declined while index rose on megacaps (VIC). Decisive test: VIC +16.2% fwd20 but avg `ta`=89 (ta≥140 only 1% of days); 0 of top-20 grind winners (VIC/energy BSR/GAS/PVD/OIL/VVS, all ta 50-130) were buyable at ta≥140. Momentum gradient FLAT in NEUTRAL (ta125≈155, can't lower without diluting to noise) but STEEP in BULL (can't raise). ⇒ momentum book structurally can't hold megacap/cyclical leaders. Redirect = orthogonal CYCLICAL/ENERGY or megacap-participation sleeve (NOT generic value Book C which co-fell), future session. See [[bal-lag-selection-deepdive-kickoff]], [[v4-faithful-reproduction-2026]], [[edge-health-monitor-amh1-2026]], [[cyclical-commodity-framework-2026]], [[oil-gas-chain-8l-2026]].


**GO-LIVE [REDACTED]12 session (user-approved khi mom_200 FLIPPED 12M trên edge-health): wired vào pt_v22_dt5g.py (V2.3A live) — mp4: state==5 & EXB_MOM {MEGA,MOMENTUM,MOMENTUM_S,MOMENTUM_QUALITY,MOMENTUM_A,S_PRO} → AVOID_exbull, đặt sau overheat guard. Deploy lúc state=NEUTRAL → zero hiệu ứng tức thời, chỉ chặn entry momentum ở EX-BULL tương lai.**
