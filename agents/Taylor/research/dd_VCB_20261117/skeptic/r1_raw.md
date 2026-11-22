**Verdict: REFUTED, medium confidence.** The arithmetic is sound and BVPS checks out against BQ. What fails is the assumption that sets the centre: a 0,8% "normalised" credit cost is applied to both ROE anchors with no evidence behind it, and moving it by 20bp shifts the centre by more than 5%. Most corrections in the review rounds so far pushed the number down. The user's rule needs the same evidence for downward changes as for upward ones.

**What I checked**
- **BVPS matches.** BQ `ticker_financial` VCB 2026Q3 BVPS is 30.370, against the report's 30.359 (0,04% off). End-2025 BVPS 26.875 × 8.355,7m shares = 224.560, against the report's 224.516. Share count 8.355.675.094 matches.
- **2025 profit matches.** BQ net profit for the four 2025 quarters sums to 35.177.
- **The 13,2% anchor recomputes correctly:** (47.211,8 − 0,8% × 1.561.362) × 0,8 / 210.300 = 13,21%. The logic is right, but the inputs are unverified (see below).

**Where the centre could be too low**
1. **The 0,8% credit cost has no source.** The report's own figures are 0,47% (loan credit cost, 9 months of 2026, annualised) and roughly 0,2% charged to profit in 2025 (my estimate: 47.212 PPOP minus roughly 44.000 pre-tax profit). No VCB credit-cost history is given. At 0,6% the two anchors become 14,4% and 17,2%, the midpoint is about 15,8%, and the centre is about 41.100 (+16%).
2. **The cash-dividend haircut is wrongly made mandatory.** §4 says all price zones must drop by about 2.850 VND after the cash-dividend ex-date. BQ `Dividend_1Y` shows VCB pays 450 VND/share in cash, and the 20.331 bn payout equals a 24,3% ratio, which fits a stock dividend. A stock dividend changes no value. The −8% should be conditional, not an order.
3. **Small items:** the model uses a 20% tax rate while the actual rate is 18,3%. The planned private placement of up to 6,5% would add value if priced above book; it is mentioned but not modelled.

**Where the centre could be too high**
1. **CBBank, the transfer bank VCB was required to take over, is not quantified at all.** It is excluded from consolidation and from CAR. If that exemption ends, or VCB has to put in capital, losses flow straight into profit and CAR. This is material and cannot be sized from what the report has.
2. **Capital ratios rest on one press source.** CAR of about 11,1–11,6% is not checked against the Pillar 3 disclosure, and CET1 and the regulatory LDR are missing. The D-SIB scenario already gives 31.800 (−10%).
3. **Early-stage credit stress is shown but not modelled.** Group-2 loans are up 85% against loans up 8,5%; groups 3–4 rose about 4× (1.063 → 4.229 bn). Guarantees are up 2,37× (about 55% of equity), and construction lending rose 72% in 2025. None of this feeds the model.

**Where the numbers come from**
- The 2025 audited inputs (PPOP 47.211,8, end-2024 loans, end-2024 equity 196.112,9) came from a dispatch message, not read from the PDF. The PDF is a scan and `pdftotext` isn't installed, so I couldn't render it either.
- The guarantee and construction-lending figures were never re-checked against `src/`.
- The share-issuance details come from press reports, not the original AGM resolution.

**Flip-flop between revisions:** the centre moved from 42.035 (round 1, ROE 16%) to 35.497 (round 3, ROE 14,6%). The only new input was the unverified 2025 audited figures. The cut came mainly from adding a 13,2% anchor and taking a midpoint, which the report itself calls "phán đoán" (judgement).

I did not open `dd_price_zones.json` or look up any price. The report's own market price (52.100), its P/B tables and its implied-ROE/Ke lines were ignored when judging the model.

<<<VERDICT_JSON>>>
{
  "case_topic": "VCB — DD định giá sau BCTC Q3/2026 (REPORT r4, tâm 35.500 @ Ke 13,5%, ROE 14,6%)",
  "mode": "DD_GENERAL",
  "verdict": "REFUTED",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; report makes no fear-buy/§2.5 claim",
    "scandal_migration_risk": "pass (with WARNING) — legal items are branch-level inspection findings and a small KTNN restatement (+29 bn equity, +46,9 bn PPOP 2025); no criminal case. The open legal/regulatory risk is the CBBank exemption from consolidation and CAR, which is unquantified (counted under missing_items)",
    "optimistic_comp_sotp_bias": "fail (two-sided) — no comps or SOTP; single-stage Gordon. The load-bearing input is a normalised credit cost of 0,8% applied to BOTH ROE anchors (13,2% and 16,0%) with no history or source, while the report's own realised loan credit cost is 0,47% (9M26) and roughly 0,2% charged to profit in 2025 (estimate). At 0,6%: anchors 14,4% / 17,2%, midpoint about 15,8%, centre about 41.100 (+16%). The downward adjustment lacks an independent basis (user rule 02/11, 03/11)",
    "data_provenance": "fail (partial) — BVPS and 2025 profit match BQ. But the 2025 audited inputs behind the 13,2% anchor and bear case (PPOP 47.211,8; loans end-2024 1.449.198,9; equity end-2024 196.112,9) were taken from a Mike dispatch and are self-declared 'chưa render lại từ PDF'. The guarantee ×2,37 and construction-lending +72% figures are also not re-checked. The share actions rely on press only; the AGM resolution was not checked",
    "liquidity_capacity_realism": "na — no sizing claim; ADV 175 bn/session is ample for the fleet's scale",
    "confirmation_bias_flipflop": "fail (toward conservative) — centre 42.035 (r1, ROE 16%) → 35.497 (r3/r4, ROE 14,6%). The only new input was the unverified 2025 audited figures; the cut came mainly from adding a 13,2% anchor (built on the same unsourced CC 0,8%) and a midpoint the report itself calls 'phán đoán'. dd_price_zones.json not opened, per the task's blind constraint",
    "exit_discipline_gap": "na — no position or sizing claim; §9 does give two-sided change-of-view triggers",
    "missing_items": "fail — (1) CBBank / 'NH TNHH MTV Ngoại thương Công nghệ số' (compulsory-transfer bank): size, accumulated losses and support commitments absent; if the consolidation/CAR exemption lapses, losses hit profit and CAR — material, unquantifiable ⇒ at least INCONCLUSIVE. (2) CET1, regulatory LDR (TT22) and Pillar 3 CAR absent (single press source); D-SIB sensitivity −10%. (3) Dividend form unresolved, yet the report orders an unconditional −2.850 VND (−8%) post-ex-date cut; BQ Dividend_1Y = 450 VND cash history and the 24,3% ratio point to a stock dividend (no value change) ⇒ an overstated downside. (4) Group-2 +85%, groups 3–4 ×4, guarantees ×2,37 and construction lending +72% are not modelled (disclosed as WARNING). (5) The bonus/welfare fund draw on retained earnings is not discussed; on BQ the 9M26 equity gap is mostly explained by the 450 VND cash dividend ⇒ small. Capex, licence and land-bank items: na for a bank"
  },
  "independent_verification": "BQ tav2_bq.ticker_financial VCB: 2026Q3 BVPS 30.370 vs report 30.359 (Δ0,04%) ✓; 2025Q4 BVPS × 8.355,7m shares = 224.560 vs 224.516 ✓; OShares 8.355.675.094 ✓; NP 2025 four-quarter sum 35.177 ✓; Dividend_1Y 450 VND (cash about 4,5%/yr). Recomputed ROE 2025 at CC 0,8% = 13,21% ✓ (logic right, inputs unverified). Could not render the scanned PDFs (pdftotext not installed)",
  "killer_objection": "The centre rests on a 0,8% credit cost applied to both ROE anchors with no evidence, while VCB's realised loan credit cost is 0,47% (9M26) and about 0,2% charged to profit in 2025. At 0,6% the centre is about 41.100 (+16%). The headline is a judgement-driven downward haircut, not a measured one",
  "recommended_followups": [
    "Build a 10-year VCB credit-cost series (provision charge / average loans, from the audited filings), set the normalisation level on that evidence, and print the centre at CC 0,5 / 0,6 / 0,8%",
    "Re-render the 2025 audited inputs (PPOP, loans end-2024, equity end-2024) and the guarantee / construction-lending figures directly from src/ (OCR) before using them",
    "Pull the 2026 AGM resolution: dividend form (cash or stock) and share-issuance ratios; make the −2.850 VND post-ex-date cut conditional on a cash dividend",
    "Quantify CBBank: equity/accumulated losses, VCB support commitments, legal status of the consolidation/CAR exemption",
    "Get Pillar 3 CAR/CET1 and the TT22 regulatory LDR at 30/06 or 30/09/2026"
  ],
  "summary": "The arithmetic is correct and BVPS (30.359) matches BQ (30.370). But the centre of 35.500 hinges on an unsourced 0,8% credit cost applied to both ROE anchors, while VCB's realised figures are 0,47% (9M26) and about 0,2% in 2025. A 0,6% assumption gives about 41.100 (+16%), so the downward haircut lacks the independent evidence the user's two-sided rule requires, and the r1→r3 cut (42.035→35.497) came from reinterpretation, not new filings. On the high side, the CBBank transfer-bank obligation is unquantified, CAR/CET1/LDR rest on one press source, and the early credit stress (group-2 +85%, guarantees ×2,37) is not modelled. The unconditional −8% post-dividend cut also conflicts with VCB's cash-dividend history (450 VND), which points to a stock dividend. Fix the credit-cost basis with history, verify the 2025 inputs from the PDF, confirm the dividend form from the AGM resolution and size CBBank before treating any centre as final."
}
<<<END_VERDICT>>>