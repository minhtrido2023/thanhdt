The model reproduces exactly from its source numbers, but its headline still rests on one unaudited input. Verdict: **INCONCLUSIVE (medium confidence).**

**What checks out**
- I rebuilt the core formula myself from the BCTC numbers and the TMĐT figures. The central-parameter value comes out at 15.894,9 đ before trading cost, the same as the model output's "tham so trung tam 15.894,9".
- C for NC-II = 6.010,1 matches.
- k matches for all three projects: NC-II 0,918, GR 0,172, H2 2,958.
- Margins match: audited FY25 is 42,7% and FY24 is 42,7%; 6T FY26 is 51,9%.
- The share count of 1.003.312.808 is dated (business registration 16/09/2026). The FY25 audit opinion is clean. The 20,21 tỷ tax penalty is small.

**Where the centre could be too high**
- **Margin g (decisive):** the base uses 51,9% from the 6T FY26 statements, which have not been reviewed by the auditor. Both audited years show 42,7%. Using 42,7% gives 13.642 đ (−14%). The argument that 51,9% reflects NC-II's whole-project margin is reasonable but it is an inference.
- **H2's k = 2,96:** the report itself flags this as an anomaly but keeps it in the base. Capping k at 1,0 gives −296 đ; k = 0,3 gives about −400 đ (−2,5%).
- **TMĐT used as cost-to-complete:** TMĐT may include VAT and contingency. The ±25% axis is symmetric, so it cannot catch a bias in one direction. A 15% cut to remaining spend gives −229 đ.

**Where the centre could be too low**
- **Backlog cost:** the "exact" form is consistent with the measured k and gives +578 đ (+3,6%). The base picks the conservative form without any separate evidence.
- **NC-II cash timing:** the model assumes all cash for unsold units arrives at completion in 11/2030. Off-plan sales collect as they go. This is material but has no data behind it.
- **Investment property:** it is held at book value, 1.438 tỷ.

**Process note:** the files the report cites (`assumptions_r3b.json`, the output files, the image evidence) were deleted from the working tree on 19/11. I recovered them from git commit `fc5bd02d9`.

**Next step:** the auditor's review report for 6T FY26 should now be out (around 14/11). It decides between 51,9% and 42,7%, and that choice decides the label.

<<<VERDICT_JSON>>>
{
  "case_topic": "TCH — DD redo r3b (REPORT_r3b.md, 09/11/2026), centre 15.864 đ/cp",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; the report makes no fear-buy/§2.5 claim (it states FLOOR_FAIL CF_OA_3Y −771,7 tỷ ⇒ not eligible for the sleeve)",
    "scandal_migration_risk": "pass — WARNING items are listed: UBCKNN penalty 1357/QĐ-XPHC 12/2024 (295 tr) and Hải Phòng tax decision 1020/QĐ-XPHC 03/04/2026 (20,21 tỷ, ~20 đ/cp); both administrative; related-party dealings now disclosed (GAPS.md §2, §9); FY25 audit AASC unqualified, no emphasis paragraph; no sign of asset seizure or licence loss",
    "optimistic_comp_sotp_bias": "fail (partial) — no comps used, but the load-bearing input is g = 51,9% from 6T FY26 (not reviewed) while both audited years FY24/FY25 are 42,7% (I recomputed: 1−275,27/480,49 = 42,71%; 1−2.235,88/3.899,17 = 42,66%); g 42,7% ⇒ 13.642 (−14%), label flips to TRONG. The ±25% F axis is symmetric, so the P10–P90 band does not cover this scenario and the band understates uncertainty. Disclosed, but the base still uses the favourable number",
    "data_provenance": "pass with caveat — numbers trace to notes_read.md (TM9(*), TM25, TM34, TM1.5) and BCTN25; however assumptions_r3b.json / tch_r3b_out.* / evidence png were deleted from the working tree on 19/11 (commit 14ad1c925) and are only recoverable from git fc5bd02d9 — the citations in REPORT §8 currently point to non-existent files",
    "liquidity_capacity_realism": "na — the report proposes no position size",
    "confirmation_bias_flipflop": "pass (with note) — lineage r2 13.768 TRONG → r3 16.244 DƯỚI → r3b 15.864 DƯỚI; the r2→r3 jump came from the user ruling holding discount = 0% (ERRATA), and r3→r3b moved DOWN after the skeptic fix; this is not re-reading the same data more favourably. Did not open kb/dd_price_zones.json per the blind constraint",
    "exit_discipline_gap": "na — no entry/sizing proposed; ERRATA says excluded from candidates because of FLOOR_FAIL",
    "missing_items": "fail (each item <5% of centre, but they do not net to zero) — (1) H2 k=2,958 kept in base despite the self-flagged anomaly ('xong thô', HTK only 25% of TMĐT): k=1 ⇒ −294 đ, k=0,3 ⇒ −399 đ (−2,5%); (2) TMĐT possibly includes VAT + contingency: a one-sided bias the symmetric axis does not catch, F −15% ⇒ −229 đ (−1,4%); (3) NC-II backlog (NMTT 3.099) discounted at y=1 while the high-rise blocks HH1–HH4 are still at basement stage (SHS 08/08) ⇒ ~−180 đ; (4) social-housing/infrastructure obligations of NC-II inside TMĐT not checked (unquantified); upward: (5) the 'exact' form consistent with measured k ⇒ +570 đ (+3,6%), the base picks the conservative form without separate evidence; (6) NC-II cash assumed in a lump at 11/2030 although off-plan sales collect progressively (material upside, unquantified); (7) investment property 1.438 tỷ at book. Present and OK: share count 1.003.312.808 (business reg. 16/09/2026, bonus 10:1 done 10/09), no debt, FY25 audit unqualified, related parties intra-group, tax penalty 20 tỷ, new land at book NPV0, KTPL fund not yet appropriated (small)"
  },
  "independent_verification": "Rebuilt nav() independently from BCTC numbers (EQ_ME 12.159,11; HTK by project TM9(*); NMTT 5.599,8; TMĐT BCTN25; r 13,5%): central-parameter 15.894,9 đ pre-CK — exact match with tch_r3b_out 'tham so trung tam 15.894,9'. C_NC-II 6.010,1 ✓; k NC-II 0,918 / GR 0,172 / H2 2,958 ✓; k=0 y by project 14.371 ✓ (report 14.412 grid mean); g audited 42,7% ✓; g 6T 51,9% ✓.",
  "killer_objection": "The DƯỚI label depends on one 6T FY26 number (51,9%) that has not been reviewed by the auditor, while two audited years both show 42,7% (centre 13.642, label TRONG). The ±25% axis and the narrow P10–P90 band hide this risk because the g scenario is outside the band.",
  "recommended_followups": [
    "Pull AASC's review report for 6T FY26 (due around mid-11/2026) — check whether the property margin stays at ~51,9% after review; this decides g",
    "Compare TMĐT for H2 and NC-II with the internal budget used to accrue cost of sales (TM 2.25): VAT, contingency, social-housing/infrastructure obligations",
    "Find the handover schedule for NC-II's backlog (low-rise vs HH1–HH4) to set y for the NMTT 3.099 tỷ",
    "Choose the base form (conservative vs exact) on evidence, not by default; the +570 đ gap needs the same evidentiary standard as downward adjustments",
    "Restore assumptions_r3b.json / outputs / evidence png to the tree or update the citations to the git commit"
  ],
  "summary": "The r3b model is mechanically sound and reproducible: I rebuilt the core formula from the BCTC and TMĐT numbers and got exactly 15.894,9 đ (central parameters, before trading cost), and every k and margin input matches its source. Nothing quantifiable above 5% is missing. Small adjustments run both ways: downward from H2's k (−2,5%), possible VAT/contingency in TMĐT (−1,4%) and backlog timing (−1%); upward from the exact form (+3,6%), NC-II collection timing and investment property. These roughly cancel. The decisive weak point is the margin input. The base uses 51,9% from unreviewed 6T FY26 statements while both audited years show 42,7%, which would give a 14% lower centre and flip the label. The P10–P90 band leaves this scenario out. I am not refuting the centre, but the label cannot be confirmed until AASC's review report for 6T FY26 confirms the margin."
}
<<<END_VERDICT>>>