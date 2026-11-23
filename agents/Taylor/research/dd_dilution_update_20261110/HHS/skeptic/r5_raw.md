## HHS DD rev7: REFUTED (medium confidence)

I recomputed the CUM centre and it is right. The rev7 EX base is not: it contradicts its own locked assumptions file, and it applies the holding discount (CK holding) on a rule it does not follow elsewhere in the report.

**Recomputed:**
- **CUM centre:** the share of NAV that takes the discount is 85.06% (from calc output), and 14,169 × (1 − 0.2663 × 0.8506) = 10,959 before the liquidity cut. That matches the calc. After the 1.41% liquidity cut (d5) it is 10,805, also a match.
- **EX centre:** with k = 0.734 the formula gives 8,846; with k = 1 it gives 9,767. Both match the report.
- **Integrity:** md5 hashes of assumptions, calc, output, run1 = run2, and the CK source file all match the lock file.
- **Median 26.63%:** the six values sorted are VIC −245, PAN 18.6, CII 24.1, SNZ 29.2, IPA 42.0, GEX 51.3. The middle pair averages to 26.65%, so the median is correct.

**Weak points:**
1. **EX base k conflicts with the lock file.** `assumptions.json` sets `"k_base": 1.0`, and rev5 #6 showed every reading gives k ≥ 1 (NĐL issues shares at 10,000, below its 11,210 book value). The report headline instead uses k = 1 − h = 0.734 as the EX base. That cuts the EX centre by 921 đ/cp (−9.4%) with no independent basis. Rule V4 requires one for a downward adjustment.
2. **The discount scope is applied two ways.** The measured CK is defined on the whole holding (1 − MV/SOTP, with book items inside SOTP). In CUM, the report spares HHS's own assets (OTHER and the auto unit), which pushes the centre up; applying the discount to the whole NAV gives 10,249 (−5.1%). In EX, it does apply the discount to new cash, which pushes the centre down. It needs one rule for both.
3. **Arbitrary choices move the centre by more than 5%.**
   - Coverage threshold: at ≥70% the median is 18.6%, which puts the CUM centre near 11,760 (+8.8%). At ≥60% the median is 26.6%.
   - Peer set: IPA is not a controlling holding but sits in the base. The structurally comparable controlling group (N = 5, 24.06%) is relegated to a sensitivity row; it gives 11,110 (+2.8%).
   - The bootstrap 5–95% band on the median is −110% to +42%, so the parameter is barely pinned down.
   - Anchoring risk: the measured median almost exactly equals the earlier unsourced 27%.
4. **Pushes the centre too high:**
   - No cash dividends flow from CRV to HHS, and HHS sits in a stacked chain (TCH → HHS → CRV). Both point to the high end of the range. On the liquid-coverage measure (N = 3) the discount is 42%, which gives 8,975 (−16.9%).
   - The NQ 10 shareholder poll (14–25/12/2026) has not published its content.
   - Unfunded I.14 capital of 1,803.2 bn is assumed to be debt at NPV0.
5. **Pushes the centre too low:** the measured CK already includes the holding's own illiquidity, and the model still subtracts the 1.41% liquidity cut on top. That is about +1.4%, not material.
6. **Missing items:** most of the checklist passes. Not found in rev7 or its assumptions: land-use or licence term for NC-II and I.14. Also unquantified: NC-II completion cost (G10 = 0) and the NQ 10 content.

The report quotes market prices (9,700; TERP 9,171). I ignored them.

<<<VERDICT_JSON>>>
{
  "case_topic": "HHS — DD rev7 (CK holding đo được 26,63% thay 0%/27% không nguồn)",
  "mode": "DD_GENERAL",
  "verdict": "REFUTED",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL, the report makes no fear-buy/§2.5 claim",
    "scandal_migration_risk": "pass — WARNINGs TB 2124/TB-TTCP (7,87 tỷ, not material) and KL 08/KL-TTTP Pruksa NƠXH restored in §4; the 852 tỷ TCH↔CRV/NĐL deposit-contract transfer is listed; nothing shows a migration to the legal entity or core assets",
    "optimistic_comp_sotp_bias": "fail (two-sided) — the CK parameter comes from N=6 with a bootstrap 5–95% of the median of −110%…+42%; a ≥70% coverage threshold gives a median of 18,6% (tâm ≈11.760, +8,8%); IPA (non-controlling financial holding) sits in the base while the structurally closer controlling group N=5 (24,06%, tâm 11.110) is only a sensitivity; the liquid-coverage measure N=3 is 42% (tâm 8.975, −16,9%). The measured median ≈ the earlier unsourced 27% ⇒ anchoring risk on the threshold choice",
    "data_provenance": "fail — assumptions.json (locked, md5 3afcd113…) sets k_base = 1.0, but the REPORT names EX BASE k = 1−h = 0,734 (8.846 vs 9.767, −9,4%). rev5 #6 showed every reading gives k ≥ 1 (NĐL issues @10.000 < BV 11.210); V4 requires an independent basis to go below NPV0 and the report gives none. Separately, all md5s/asserts and CUM figures match",
    "liquidity_capacity_realism": "na — no sizing (HHS EXCLUDE forensic_flags, V8 not applied)",
    "confirmation_bias_flipflop": "pass with note — 0%→26,63% is driven by NEW data (CK measurement job Taylor_20261123_120407), not a reinterpretation; the report keeps the 0% row for comparison. Note: the result coincides with the earlier 27% expectation ⇒ needs a check that the 60% threshold was not picked after the fact",
    "exit_discipline_gap": "na — no position/sizing claim (EXCLUDE)",
    "missing_items": "pass (partial) — present: share base 431,986tr cp @30/09/2026 (BCTC Q3 TM1.1), quyền 5:3 + CP dividend 7%, commitment of 2.591,9 tỷ + 1.803,2 tỷ unfunded (scenario), welfare fund 6,46 tỷ, related parties, audit FY2025 AASC unqualified (Q3 not reviewed), one-off 3.507 tỷ. Not found in rev7/assumptions: land-use/licence term for NC-II/I.14 within the horizon; NC-II completion cost G10 = 0 (not disclosed, unquantifiable); NQ 10 content (14–25/12) unknown — unquantifiable"
  },
  "independent_verification": "Recomputed CUM: 14.169×(1−0,2663×0,8506)=10.959 pre → ×(1−0,014097)=10.805 ✓. EX: (10.805×431,986tr + 0,985903×0,7337×2.591,9 tỷ)/691,178tr/1,07 = 8.846 ✓; k=1 → 9.767 ✓. Median N=6 from the per-holding table (18,6/24,1/29,2/42,0) = 26,65% ✓. md5 of assumptions/calc/out/run1=run2/ck calc_out match LOCK ✓.",
  "killer_objection": "The CK scope rule is applied to suit each line: CUM excludes HHS's own assets from CK (pushes up; full-NAV per the measurement's definition = 10.249, −5,1%), while EX applies CK to the rights cash (pushes down, k=0,734 vs k_base=1,0 in locked assumptions, −9,4%). Either way, the base centre is not built on a single consistent rule, and the parameter itself has a bootstrap CI covering −110…+42%.",
  "recommended_followups": [
    "Pick one CK scope rule (CRV-only or whole NAV per the measurement's definition) and apply it the same way to CUM and EX; sync k_base in assumptions.json with the headline",
    "Pre-register the coverage threshold and the peer set (controlling vs all) before rerunning; report tâm at the 50/60/70% thresholds",
    "Remove the double count of d5 (1,41%) when CK already includes the holding's own liquidity, or justify keeping it",
    "Add land-use term / licence for NC-II and I.14 within the horizon",
    "Rerun dilution after the shareholder poll 14–25/12/2026 (NQ 10)"
  ],
  "summary": "Rev7's mechanics are clean: the calc reproduces, the md5s match the lock, and the CUM tâm 10.805 and EX 8.846/9.767 recompute exactly. The issues are in the modelling choices. (1) The EX base uses k=0,734 while the locked assumptions say k_base=1,0, and rev5 had shown k≥1; that is −9,4% on the EX centre with no V4 basis. (2) The CK scope rule is applied inconsistently: OTHER/auto are spared in CUM, while CK is applied to the new cash in EX. (3) The parameter is fragile: N=6, bootstrap CI −110…+42%, and a coverage threshold or peer-set choice moves the centre +2,8…+8,8% (cheap side) or −5,1…−16,9% (expensive side). CUM 10.805 is defensible as one point in a wide band, but it is not a base resting on a consistent rule. Market prices in the report were ignored."
}
<<<END_VERDICT>>>