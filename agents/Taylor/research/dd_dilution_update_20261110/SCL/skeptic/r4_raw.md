**Verdict: INCONCLUSIVE (medium).** The rev7 calculations check out against the source filings, and no quantifiable missing item moves the centre by more than 5% in either direction. The verdict can't be CONFIRMED because the base rests on perpetual access to ash/gypsum feedstock. That supply has no verifiable contract term (the report admits this in §1 #6 and §7), and its own scenarios cut the centre by 16% to 33%.

**Independent checks (both match):**
- **k = 16,703%.** Recomputed from the filing page image for H1/2026 note V.19.1 (`bn28_crop.png`). It shows phúc lợi 3,214 + khen thưởng 3,214, the bonus-fund reversal "(3.600.000.000)" and "Phát hành ESOP từ LNST 6.800.000.000". With 2024 and 2025 added: (14,54% + 15,00% + 20,57%) / 3 = 16,703%.
- **Tax shield = 4,142 tỷ/năm**, from 416,46 × 4,963% × 20,04%. Divided by 13,5% that is 30,7 tỷ, or ≈674 đ/cp before the liquidity discount and ≈644 after. This matches step C2 in the bridge.
- **Share count:** 32.407.875 + 5.508.940 (the 55,089 tỷ stock dividend) + 920.000 paid ESOP = 38.836.815, matching NQ 1191.

**Bias toward too LOW (the centre may be understated):**
- The tax shield uses the P&L interest rate of 4,96%. The same filing shows contract rates of 9,5–10,5% at BIDV and 10% from Cao Cường, so part of the interest is being capitalised into construction in progress. That capitalised interest is still tax-deductible later, through depreciation. Using a rate of about 9% would add roughly +2 to +4% to the centre (my estimate).
- The 2026 ESOP may not recur. If it doesn't, k falls to about 14,8%, which adds roughly +2%.

**Bias toward too HIGH (the centre may be overstated):**
- ESOP is costed at par value. At intrinsic value k would be about 18,9%, roughly −2,6%.
- The 920k-share paid ESOP isn't in k at all, and I couldn't find its issue price, so any discount handed to employees is unmeasured.
- The tax shield is treated as a perpetuity on the 30/9 debt level. The report's own base assumes the rights proceeds repay 75 tỷ to BIDV, and its own variant on post-repayment debt gives −116. The company's habit of repaying debt with new equity also argues for a shrinking shield, not a perpetual one.
- The Vincons receivable has a 0% loss in the base. The r3 loss axis gives about −74.

**Minor gap:** the report says remaining capex on the Vĩnh Tân line is "not disclosed". The same note gives a loan capped at 68,96% of the total investment, so a figure could be derived. The project is valued at book (NPV = 0), so the centre barely changes, but it matters for future funding needs.

I couldn't run the flip-flop check against the ledger: the permission check blocked opening `kb/dd_price_zones.json`, even for SCL's own rows. I worked from the report's own bridge instead. I ignored the market prices that appear in the report's text.

<<<VERDICT_JSON>>>
{
  "case_topic": "SCL DD rev7 (23/11/2026) — post-rights basis, centre 16.237 (CK 5 tỷ)",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "mode": "DD_GENERAL",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; the report makes no fear-buy/§2.5 claim",
    "scandal_migration_risk": "pass — no legal/regulatory WARNING items in the report; related-party loan from Cao Cường 28 tỷ @10% (V.17.2) and the NĐ 132 deductibility cap are disclosed; audit opinions clean",
    "optimistic_comp_sotp_bias": "pass (with caveat) — no comps; the five debt framings are shown openly (15.268…21.578). The base tax-shield convention chooses the lowest interest rate (P&L 4,96% vs contract 9,5–10,5% on the same page of the H1/2026 note) yet keeps the pre-repayment debt (416 vs 341 after repaying 75 tỷ). The two choices pull in opposite directions, net ≈ +2..+3% (estimate)",
    "data_provenance": "pass — k, the 3,6 tỷ reversal and the 6,8 tỷ ESOP traced to the H1/2026 V.19.1 image; DEBT/INT_Q3/TAX traced to Q3 codes 321+339/24/51; share count 32.407.875+5.508.940+920.000=38.836.815 matches; 'Vĩnh Tân capex không công bố' is not quite right (loan contract caps it at 68,96% of TMĐT)",
    "liquidity_capacity_realism": "na — no buy proposal; liquidity discount reuses ADV120 from r3 (flagged in §1 #8)",
    "confirmation_bias_flipflop": "pass — label unchanged; the −646 change is traceable to three sourced base fixes (k −1.274, shield +644, dividend payable −16), each fixing an item skeptic r3 named; not re-tuned. Ledger rows for the ticker were not read (permission denied); the report's own bridge was used",
    "exit_discipline_gap": "na — no buy proposal or sizing; two-sided milestones and HARD ABANDON carried over from rev6",
    "missing_items": "fail (unquantifiable, material) — (1) term/price/remaining life of the ash/gypsum feedstock from coal plants (Phả Lại, Vĩnh Tân) while terminal g=4% is perpetual; report's own scenarios −16%/−33%; not verifiable ⇒ INCONCLUSIVE. Non-material/quantified: ESOP at intrinsic value k≈18,9% (≈−2,6%, estimate); price of the 920k paid ESOP not checked; tax shield at contract rate (≈+2..+4%, estimate); Vincons expected loss on the r3 axis −74 (16.163); Vĩnh Tân TMĐT derivable from the loan contract (NPV0 ⇒ ≈0 on centre). Pass: share-count basis, KTPL/bonus/ESOP, related parties, audit FY2025 + H1/2026 review, dividend payable, one-off other income (net 1,515 variant)"
  },
  "independent_verification": "Read the H1/2026 V.19.1 image directly: 3.214.231.371 ×2, (3.600.000.000), 6.800.000.000 ESOP, 55.089.400.000 stock dividend — matching calc_rev7. Recomputed k = (6,582/45,27 + 3,985/26,57 + 13,229/64,30)/3 = 16,703% ✓; shield 416,46×4,963%×20,04% = 4,142 tỷ/yr → ≈644 đ/cp after CK ✓ (C2 +644); share count 38.836.815 ✓. Found contract rates 9,5–10,5% (BIDV) and 10% (Cao Cường) on the same filing page, versus the model's I_REAL 4,96%.",
  "killer_objection": "Valuation is a perpetual multiple (g=4%, RONIC=Ke) on a business whose core input is ash/gypsum from coal-fired plants. The supply-contract term and price are unverified (the 5F addendum suggests ~3-year auction cycles) and are in neither the base nor the probability weights; the report's own scenarios show −16% to −33%.",
  "recommended_followups": [
    "Find the ash/gypsum purchase contract with Phả Lại/Vĩnh Tân 4 (term, price, rebid mechanism) and the source plants' retirement schedules within the horizon; if the remaining term is < terminal horizon, put a finite feedstock life into the base",
    "Choose one consistent tax-shield convention: the real contract rate on debt including capitalised interest, and debt after the 75 tỷ repayment, since the base already assumes cover=1",
    "Find the issue price of the 920k paid ESOP (2026) and add the discount to intrinsic value into k",
    "Derive the Vĩnh Tân TMĐT from the loan contract (≤68,96%) instead of writing 'không công bố'",
    "Consider moving the r3 Vincons loss axis (expected −74) into the base instead of 0%"
  ],
  "summary": "Rev7 correctly fixes the items skeptic r3 named, and its sourced numbers check out: k 16,70% is recomputed exactly from H1/2026 note V.19.1, the tax shield gives +644 as stated, and the share count is consistent. Two-sided, there is a slight downward bias from the tax-shield interest rate (P&L 4,96% vs contract 9,5–10,5%, ≈+2..+4% estimate) and from treating ESOP-2026 as recurring; there is an upward bias from costing ESOP at par (≈−2,6%) and from a perpetual shield on debt that is being repaid. No quantifiable gap exceeds 5% of the centre. But the base assumes the ash/gypsum feedstock lasts forever at g=4% with no verifiable contract, and the report's own scenarios show −16%/−33%. That is a material, unquantifiable item, so the verdict is INCONCLUSIVE rather than CONFIRMED. Market prices in the report were ignored."
}
<<<END_VERDICT>>>