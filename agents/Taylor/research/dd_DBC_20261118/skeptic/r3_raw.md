**Verdict: REFUTED, medium confidence.** The error makes the centre too low. Rev3 takes historical real-estate profit out of the numerator, but leaves the real-estate work-in-progress (about 1,186 bn) inside operating equity.

**Too low (the error that decides the verdict)**
- The rev1 report (§ balance sheet, notes TM 8) records about 1,186 bn of real-estate WIP inside inventory at 30/6/2026. Rev3 has no line for it.
- In the model that WIP stays in E_op = equity minus construction in progress (CIP) = 7,418 bn, so it is priced at (ROE×(1−k) − g)/(r − g) ≈ 0.70× book. Its own earnings were removed, and it earns nothing in the denominator, which pulls ROE_op down.
- My estimate if it is booked at book value like CIP (net present value = 0): base 15,119 → 15,936 (**+5.4%**). If it is also taken out of the ROE denominator, the upper bound is 19,489 (**+28.9%**). Both are estimates, because the historical share of real-estate WIP is not known.
- This breaks the two-sided rule. The downward fix (B1) went in without its balance-sheet counterpart.
- One more small push upward: subtracting gross profit without the real-estate selling and admin costs removes slightly too much profit. The report admits this itself.

**Too high (still open)**
- **Tax incentive end date (B5):** the report estimates about −13% but did not run it. This is material and unverified.
- **Biological-asset (hog) writedown:** rev1 put it at 94–188 bn (−1.5% to −3%). Rev3 dropped it from its sensitivities.
- **Environmental compliance capex for existing farms:** unverified. The 50–150 bn sensitivity range is an assumption with no source.
- **Unpriced CIP capex:** the capex still needed to finish the CIP projects is not disclosed and not counted.

**Independent check**
- BigQuery `NP_P0` for 2023Q2, 2025Q1, 2025Q4 and 2026Q3 matches the assumptions file. Equity for 2026Q3 is 8,721.4 bn, which matches.
- The quarterly sums match the audited annual figures the report cites: 2023 = 25.01, 2024 = 769.08, 2025 = 1,506.77.
- Recomputed: real-estate run-rate 2.635 bn/quarter (report 2.64), total real-estate profit removed 474.4 bn (report 474.3), base 15,119 (report 15,123 — rounding).
- I could not read the source PDFs, because no PDF library is installed. The 1,186 bn comes from rev1's citation, not from my own reading of the filing.

Market prices in the report were ignored, and I did not open the price-zone ledger.

<<<VERDICT_JSON>>>
{
  "case_topic": "DBC — DD rev3 (centre 14,696, zone [7,284; 21,857])",
  "mode": "DD_GENERAL",
  "verdict": "REFUTED",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; the report makes no fear-buy/§2.5 claim",
    "scandal_migration_risk": "pass — legal is WARNING only: 237.1 bn receivable from employees (land clearance/advances; −539 đ/share if fully lost, not in base), Transeco 20 bn; EY 2025 audit unqualified, H1/26 review clean; no signal of asset seizure or licence loss. Note: the 237.1 bn land-clearance advance may tie to the real-estate project, whose value is unverified",
    "optimistic_comp_sotp_bias": "fail (direction: too LOW) — residual-income model with no SOTP: about 1,186 bn of real-estate WIP (rev1 §balance sheet, TM 8, at 30/6/26) stays inside E_op = 7,418 bn and is priced at ≈0.70× book, while the earnings of that segment were removed from historical ROE (B1). Booking it at NPV=0 like CIP: base 15,119→15,936 (+5.4%, estimate); also removing it from the ROE denominator: up to 19,489 (+28.9%, upper bound, estimate — historical share unknown). Also, subtracting gross profit without the segment's selling/admin cost removes slightly too much (report §10.2 admits this)",
    "data_provenance": "pass with reservation — quarterly NP, equity and real-estate gross profit all trace to BQ or cited notes (KT22/23/25, Q3/26 section VI); BQ quarterly sums match audited figures; CIP between year-ends is interpolated (labelled estimate); the 1,186 bn real-estate WIP figure is from the 30/6 note and rev3 does not update or use it; liquidity discount 2% reuses the rev1 ADV",
    "liquidity_capacity_realism": "na — the report proposes no purchase; the 2% discount is an estimate (sensitivity 0–5%)",
    "confirmation_bias_flipflop": "pass with note — 19,491 → 17,317 → 14,696; each cut is backed by new filings (KT22–25 audited reports, real-estate gross profit), not reinterpretation. But all three revisions only go down: the balance-sheet counterpart of the real-estate exclusion was not applied, which goes against the rule (02/11, 03/11) that adjustments in either direction need the same evidential basis. kb/dd_price_zones.json not opened (blind constraint); comparison uses only the rev1/rev2 centres cited in the report",
    "exit_discipline_gap": "na — not a fear-buy; §9 already sets two-sided pre-declared milestones plus the mechanical window-slide effect",
    "missing_items": "fail — (1) real-estate WIP about 1,186 bn absent from the model as a separate asset: +5.4% to +28.9% (estimate) ⇒ quantifiable and >5% ⇒ REFUTED; (2) CIT incentive end date (B5) not run, report estimates about −13% — material, unverified; (3) biological-asset/hog writedown 94–188 bn (rev1) dropped from rev3: −1.5% to −3%; (4) compliance capex/environmental permits for existing farms unverified, 50–150 bn sensitivity is unsourced; (5) committed capex to finish CIP undisclosed and uncounted. Passed: audit opinion FY2025 + H1/26 review; share count 431.05m (charter capital, TM25.1, 30/9/26, after 12% stock dividend); welfare-fund deduction k=11.06% from filings; NCI immaterial; 2022Q4 corrected to audited figure"
  },
  "independent_verification": "BQ ticker_financial DBC: NP_P0 2023Q2=326.82, 2025Q1=508.26, 2025Q4=148.581, 2026Q3=200.169; equity 2026Q3=8,721.4 — match the assumptions file. Quarterly sums 2023=25.007, 2024=769.083, 2025=1,506.768 = cited audited figures. Recomputed real-estate run-rate 2.635 bn/quarter (report 2.64), real-estate profit removed 474.4 bn (474.3), base 15,119 (15,123, rounding). Could NOT read the PDFs directly (no PDF library) — the 1,186 bn real-estate WIP is taken from rev1's citation",
  "killer_objection": "Rev3 strips the real-estate segment's profit from historical ROE but keeps its capital (about 1,186 bn real-estate WIP) inside operating equity, valued at 0.70× book and dragging ROE_op down — the centre is understated by +5% to +29% (estimate), the opposite direction to the main rev3 change; meanwhile the CIT incentive item (−13%, estimate) is still unrun, so the net direction is not settled",
  "recommended_followups": [
    "Read TM 8 (inventory/WIP) in Q3/26 and KT22–KT25: real-estate WIP balance per year-end, project name, land-use status, any impairment; treat it like CIP (book/NPV=0, removed from the ROE denominator using historical shares) and rerun calc",
    "Link the 237.1 bn employee land-clearance advance to the real-estate project (if it is part of land clearance for that project, include it in the real-estate asset, not only as a WARNING)",
    "Run the CIT incentive item (B5) in calc: find the incentive terms per entity and expiry year, apply the tax path to normalised ROE",
    "Put back the biological-asset writedown sensitivity 94–188 bn from rev1",
    "Check environmental permits (2020 Environmental Protection Law) for existing farms; if there is an upgrade obligation, quantify it as compliance capex (cash outflow)",
    "Install a PDF reader (pypdf/pdftotext) so the skeptic can verify the original notes directly"
  ],
  "summary": "Rev3's numbers reproduce (BQ NP and equity, real-estate gross profit, run-rate, base 15,119≈15,123), and the real-estate profit exclusion is backed by new audited filings. But the model is internally inconsistent: it removes the segment's profit and keeps its capital — about 1,186 bn of real-estate WIP inside operating equity, priced at ≈0.70× book and lowering ROE_op. Fixing only that raises the centre by +5.4% to +28.9% (estimate), above the 5% threshold, so the verdict is REFUTED in the 'too low' direction. In the other direction, the CIT incentive end date (about −13%, estimate, unrun), the biological-asset writedown (−1.5% to −3%) and environmental compliance capex are still unverified, so the corrected centre could move either way. The real-estate asset must be priced and B5 run before a centre can be accepted. Market prices in the report were ignored."
}
<<<END_VERDICT>>>