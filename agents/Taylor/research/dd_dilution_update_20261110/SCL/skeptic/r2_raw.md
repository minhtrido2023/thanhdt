**Verdict: INCONCLUSIVE, medium confidence.** I could not fault the arithmetic or the share count in rev6, and I checked several of its key numbers against the original filings. What it leaves unanswered is the ash-supply contract at Phả Lại thermal plant, which the existing business depends on and not just the new project. That risk is material and cannot be quantified from the sources available.

**What I checked myself:**
- **Q3/2026 balance sheet (page 2):** borrowings are 259.737 + 156.724 = 416.46 bn VND. The welfare/bonus fund balance (line 323) is 6.3295 bn and 9-month profit after tax (line 420b) is 94.362 bn. Charter capital of 388.368 bn gives 38,836,815 shares. All of these match `calc_rev6.py`.
- **Share count:** from 1/1 to 30/9, charter capital rose by 64.289 bn. That equals the 55.089 bn stock dividend plus the 9.2 bn paid ESOP (920k shares). Retained earnings from earlier periods are 7.365 bn, which equals the expected 0.565 bn plus 6.8 bn. So the free ESOP-2 (680,000 shares) had not been issued by 30/9, and adding it to the share count is correct.
- **Welfare/bonus funds at 10%:** this matches resolution NQ 486 (as shown in section V.19.1 of the reviewed H1 report: 3.214 + 3.214 bn). The 3-year average of 16.1% also recomputes correctly.

**Where the centre could be too high:**
- **Phả Lại ash contract (main objection):** the report only models losing the source as an impairment on the new project, which cuts the centre by 2,000–4,000 VND/share. The core business (processing fly ash and making lightweight bricks at Chí Linh) also relies on that ash. The contract's term and price are not in any filing, and the cost of re-bidding is not in the model.
- **Vincons receivable:** 67.89 bn with no provision, roughly 1,490 VND/share, or 8.8% of the centre if fully lost. Rev4 had a loss sensitivity for it; rev6 dropped it.
- **Other income:** a 4.76 bn one-off item (recovery of a written-off debt) stays inside trailing earnings. I estimate this lifts the centre by about 3%.
- **Welfare/bonus rate:** the base uses 10%, the lowest of the last three years. The 3-year average would lower the centre by 6.9%. This is disclosed and backed by the latest AGM resolution, so I don't count it as an error.

**Where the centre could be too low:**
- **Debt-valuation method (debt at face value):** it capitalises the added-back interest at the cost of equity and also applies the reinvestment haircut to it. My estimate is that this understates the centre by about 4–6%, which matches the 6.1% gap to the r3 method.
- **Interest rate:** the 4.96% in the model, from annualised Q3 interest, is low next to the 9.5% on the Vĩnh Tân project loan. A low rate shrinks the added-back interest, which also pushes the centre down.

These upward and downward biases roughly cancel. None of them is a clearly wrong number above 5%. The 21,339 → 16,883 move from r4 is backed by filings and by the 22/11 terminal-value rule, not by reinterpreting old facts.

The report's text includes market prices; I ignored them, as required. I did not open `kb/dd_price_zones.json`.

<<<VERDICT_JSON>>>
{
  "case_topic": "SCL — DD rev6 (23/11/2026), post-rights basis 45.516.815 cp, centre 16.883 (CK 5 tỷ)",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; report makes no fear-buy/§2.5 claim",
    "scandal_migration_risk": "pass — WARNING items present (related-party loan Cao Cường 28 tỷ @10% confirmed in H1 V.18(3) image, Vincons concentration, dilution); no sanction/prosecution cited; nothing contradicting found in sources read",
    "optimistic_comp_sotp_bias": "pass (two-sided) — no comps; frame choice shown across 3 debt frames (16.558/16.883/17.918). Headline par-debt frame applies Ke + (1−g/ROE) retention to the interest add-back stream ⇒ est. ~4–6% DOWNWARD bias (ước lượng); KTPL base 10% is the most favourable of 3 years (3Y avg 16,1% ⇒ −6,9%) ⇒ UPWARD lean; disclosed, roughly offsetting",
    "data_provenance": "pass — debt 259,737+156,724, KTPL 6,3295 (mã 323), NPAT 9T 94,362 (420b), vốn góp 388,368 tỷ all match Q3 BS image; KTPL 3,214+3,214 and ESOP 6,8 tỷ match H1 V.19.1 image; I_REAL 4,96% is annualised Q3 interest on period-end debt (understates vs 9,5% Vĩnh Tân loan — flagged, not refuting)",
    "liquidity_capacity_realism": "na — no buy proposal; CK at 5 tỷ = 213% ADV120 disclosed as out-of-range extrapolation",
    "confirmation_bias_flipflop": "pass — r4 21.339 → rev6 16.883 bridged one axis at a time; each step tied to new filing evidence (NQ 486, H1 V.19.1, LCTT/V.9) or the 22/11 D4 rule; controls reproduce r4 and skeptic-r1 figures. Did not open dd_price_zones.json per brief",
    "exit_discipline_gap": "na — no entry; two-sided milestones and HARD ABANDON carried forward",
    "missing_items": "fail (unquantifiable, material) — (1) the Phả Lại ash/gypsum supply contract (term, price, re-bid) feeds the CORE Chí Linh business, but the report models it only as a CIP impairment (−2.000…−4.000); the effect on core margin is unmodelled and unknowable from the sources; (2) Vincons receivable 67,89 tỷ (≈1.490 đ/cp = 8,8% of centre at full loss, ước lượng) unprovisioned and no sensitivity in rev6 (r3/r4 had one); (3) one-off other income 4,76 tỷ kept in TTM (≈+3% centre, ước lượng). Pass: share basis (verified), committed capex Phả Lại 72 tỷ (growth, NPV0), welfare fund, related party, audit FY2025 unqualified + H1 review, land to 2059"
  },
  "independent_verification": "Read Q3/2026 consolidated BS image (q3_03.png) and H1 V.19.1 (bn28_crop.png). Debt 416,46 / KTPL 6,3295 / NPAT 9T 94,362 / shares 38.836.815 match exactly. Equity rollforward ΔVốn góp 64,289 = stock div 55,089 + ESOP-paid 9,2; 420a 7,365 = 0,565 + 6,8 ⇒ ESOP-2 680k cp not yet issued at 30/9 — independently confirms the B3 share count.",
  "killer_objection": "The core business depends on ash from Phả Lại thermal plant under contracts that reference cases suggest run about 3 years. The report confines the loss-of-source risk to a CIP write-off, while the core margin's exposure to re-bidding the contract (term and price) cannot be verified and is absent from the model. It could move the centre more than the −2.000…−4.000 scenario.",
  "recommended_followups": [
    "Obtain the ash/gypsum purchase contract with Phả Lại thermal plant (term, price, re-bid date), or annual-report/AGM disclosure of it; model the core-margin effect, not just CIP impairment",
    "Restore the Vincons receivable loss sensitivity (0/20/50/100%) that r3/r4 carried",
    "Strip the 4,76 tỷ other income (debt recovery) from TTM earnings or show its effect",
    "Show a WACC/unlevered-cost variant of the par-debt frame (or drop the retention haircut on the interest add-back) to size the frame's downward bias",
    "Check Q4 interest per average debt vs 4,96%, and the remaining capex of the Vĩnh Tân line under the 68,96% project loan"
  ],
  "summary": "Rev6's numbers trace to the original filings. I checked debt, the welfare fund, 9-month profit, the share count and the ESOP-2 status against the BCTC images, and the equity rollforward confirms the 680k free ESOP shares are still pending. The bridge from r4 is driven by sourced filings and a stated rule, not by reinterpreting old facts. Two-sided review: the par-debt frame leans low (est. 4–6%) and the 10% welfare rate, one-off other income and the dropped Vincons sensitivity lean high. These roughly offset. What stops a CONFIRMED is a missing item: the Phả Lại ash supply contract, which the core business depends on, is unverified and its effect on core margin is unmodelled (the report confines it to a CIP impairment). That item is material and cannot be quantified from the sources, hence INCONCLUSIVE. The report's market-price text was ignored."
}
<<<END_VERDICT>>>