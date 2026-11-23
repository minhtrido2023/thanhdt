**Verdict: REFUTED (medium confidence).** The arithmetic reproduces exactly, but rev5's largest change, +1.406 đ/cp from adding the PV of 2027–28 earnings, ignores the working capital that PNJ's own revenue plan requires. Removing it cuts the centre by about 19%. Two more errors push the same way, and one possible error pushes the other way.

**What checks out.** Model r5 reruns to 7.395, with band 6.488/8.303, BVPS floor 12.586 and shortfall 1.077,5. The md5 hashes match the lock. Net inventory 16.626 in BQ (`ticker_financial`, 2026Q3) matches TM7. Revenue for 2024 (38,2) and 2025 (35,4) in BQ matches IRQ3 p9. IRQ3 p4 and p7 match the report: the 21.000 exchange liability, 80% → 16.500, a 7.100 loss provision, and the 8.000 raise split 60/20/20.

**Problems that make the centre too high:**
1. **Missing working capital for growth (attack 8, quantifiable).** The plan takes revenue from 39,1k (2026F) to 57,7k (2029F), up about 48%. In BQ, inventory/revenue was about 0,33–0,34 in 2023–24 and 0,45 in 2025. At 0,34, 2029 needs about 19,6k of inventory against 16,6k now, and 52% of today's stock is slow-moving diamonds. The raise funds only 1.600 of working capital, so the 1.300 of 2027–28 profit has to be retained to fund growth. It cannot also be counted as distributable. Defending this with "capex 9T is only 57,4" misses the point: for a jewellery retailer, inventory is the capital. Effect: −1.406 (−19%), giving a centre of about 5.989, possibly lower.
2. **O2 contradicts itself.** It is funded by "debt and/or cutting inventory" while keeping the same economics, which assumes 48% revenue growth. You cannot cut inventory and grow 48% at once.
3. **O3 (default/restructuring) gets zero base weight despite direct evidence.** PNJ has delayed payments to customers since 21/7. Cash fell from 3.700 to 770, and that already includes the chairman's 700 loan. The business needs 150/month, and up to 16.500 of exchanges are pending. Debt capacity of 8.000 is only assumed. If O2 really means O3 at q=0,5 with L=0, the centre falls about −19%; at q=1, about −38%.

**Problem that may make the centre too low:**
- The downside scenario (100% of customers exchanging) gets 10% weight. The other side gets no scenario, even though there is data for it: TM17's actual ratio implies a loss of about 3.867 instead of 7.071, and the historical exchange rate was 28,8%. This needs its own evidence basis, as the user's rule requires. The July run-rate (one month's exchanges ≈ all of 2025) does argue that 80% is plausible.

**Unquantified but material:** possible legal or regulatory action over the payment delays (Decree 390, lawsuits), the gold-bar licence term, the 500 of "vốn khác", the 50,7 board bonus fund set up in a loss year, the size of the ESOP, and the 773 deferred tax asset under O2/O3.

The market price 13.500 appears in the report itself; I ignored it.

<<<VERDICT_JSON>>>
{
  "case_topic": "PNJ — DD rev5 (center 7.395 đ/cp, zone 6.488–8.303, NON)",
  "mode": "DD_GENERAL",
  "verdict": "REFUTED",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; the report makes no §2/§2.5 fear-buy claim",
    "scandal_migration_risk": "fail — PNJ has delayed payments to customers since 21/7 due to liquidity problems [IRQ3 p2], and cash fell 3.700→770 even after the chairman's 700 loan [IRQ3 p4]. This is legal-entity risk (customer claims, consumer regulators, Decree 390), yet the report treats it only as an unverified WARNING and gives O3 zero base weight.",
    "optimistic_comp_sotp_bias": "fail — no comps are used, but the outcome tree is biased: (a) +PV of 2027–28 profit (1.020) double-counts capital that must be retained to fund working capital for the planned +48% revenue growth; (b) O2 keeps the plan's economics while financing 8.000 by cutting inventory, which contradicts that growth. In the other direction, there is a 100%-exchange stress scenario but no scenario below the 80% exchange rate (TM17 actual ratio ~3.867 vs 7.071).",
    "data_provenance": "pass — BVPS 12.586, shortfall 1.077,5, share count 511,72tr, IRQ3 p4/p7/p9 (21.000; 16.500; 7.100; 60/20/20; NPAT 0,1/1,2/1,6) all match source; inventory 16.626 and 2024/25 revenue match BQ. Scenario weights and N=2.500 are labelled (ước lượng).",
    "liquidity_capacity_realism": "na — sizing is 0% (NON); V3 is report-only",
    "confirmation_bias_flipflop": "pass with caveat — label stays NON, centre +76% across revisions (4.205→7.395) with no new business data; all three fixes answer skeptic r3. Fixes #1 and #3 are sound. Fix #4 (PV 2027–28) has the wrong justification ('capex only 57,4' ignores working capital). p was set after seeing the price (r4) and is now less decisive (+363/0,1).",
    "exit_discipline_gap": "na — no sizing or fear-buy claim; the report lists two-way triggers to change the call (§8)",
    "missing_items": "fail — (1) WORKING CAPITAL FOR GROWTH absent: plan revenue 39,1k→57,7k (2026F→2029F); BQ inventory/revenue 0,33–0,34 (2023–24), 0,45 (2025) ⇒ ~19,6k inventory needed vs 16,6k now (52% slow-moving diamond stock); the raise funds only 1.600 of working capital ⇒ 2027–28 profit (1.300) must be retained ⇒ the PV 1.020 add-on is not distributable: centre −1.406 (−19%) → ~5.989, possibly lower once extra working capital is deducted. (2) Debt capacity for O2 (8.000) unproven given payment delays, 770 cash, 150/month burn, up to 16.500 of pending exchanges; O3 at q≥0,5 ⇒ ≥−19%. Unquantified: Decree 390/lawsuits over payment delays, gold-bar licence term (GP not checked in rev5), 'vốn khác' 500, board bonus fund 50,7 in a loss year, ESOP size, recovery of the 773 deferred tax asset under O2/O3. Pass: capex commitments (none, 57,4), share-count basis 30/9, FY2025 audit unqualified + H1 review emphasis TM39, welfare fund 473 (already a liability), chairman loan 700."
  },
  "independent_verification": "Re-ran calc/model_r5.py: center 7.395, band 6.488/8.303, BVPS 12.586,3, shortfall 1.077,5, sens_no_2027_28 5.989 — match; md5 of assumptions/model match the lock. BQ ticker_financial PNJ: Inventory 2026Q3 = 16.626 (matches TM7 net); revenue 2024 = 38,23k, 2025 = 35,41k (match IRQ3 p9). IRQ3 text p4/p7 confirms 21.000 / 16.500 / 7.100 / 8.000 at 60/20/20.",
  "killer_objection": "Adding PV of 2027–28 profit (1.020, +1.406/share, 19% of the centre) assumes that profit can be paid out. But the plan grows revenue ~48% by 2029 in a business with inventory ≈0,34× revenue, while the raise funds only 1.600 of working capital — so that profit must be retained to reach N=1.600, and the centre should be ≤~5.989.",
  "recommended_followups": [
    "Model working capital explicitly: target inventory/revenue 2029 (0,34 pre-crisis vs 0,45 in 2025) × 57,7k, minus how much excess diamond stock can be cleared, minus the 1.600 from the raise ⇒ subtract the PV of the remaining working-capital need instead of adding PV of 2027–28 profit",
    "Rebuild O2: either borrowing (proving capacity: bank lines, covenants, collateral) or inventory cuts with lower growth — not both",
    "Give O3 a weight based on the liquidity evidence (payment delays, cash 770, 150/month burn), or state explicitly that q=0 is itself an unsupported assumption",
    "Add an upside scenario for an exchange rate below 80%, using the TM17 actual ratio, so the up/down scenarios are symmetric",
    "Check customer lawsuits / Decree 390 and the gold-bar licence term"
  ],
  "summary": "Rev5 fixes the O2 double penalty and the double-counted bridge interest correctly, and every source number traced (IRQ3, BCTC, BQ) matches; the model reruns exactly to 7.395. But the largest change (+1.406, PV of 2027–28 profit) rests on the false premise that recovery needs no capital: the plan takes revenue up ~48% by 2029 in a business with inventory ≈0,34× revenue, while the raise funds only 1.600 of working capital, so the 2027–28 profit must be retained and the centre should be ≤~5.989 (−19%). O2 also contradicts itself (financed by cutting inventory while keeping growth), and O3 gets zero weight despite direct evidence of a liquidity squeeze (customer payment delays, cash 770). In the other direction, there is no scenario for an exchange rate below 80%. Errors of >5% of the centre on both sides, with the larger push downward, mean the zone needs rebuilding; the NON label is unaffected."
}
<<<END_VERDICT>>>