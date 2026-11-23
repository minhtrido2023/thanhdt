**Verdict: INCONCLUSIVE (medium confidence).** The figures rev5 does use check out against the filings. The open problem is what it leaves out: the base never values about 176 bn VND of assets on the balance sheet, which is roughly 13% of the centre before the liquidity discount (CK), and whether they belong in the valuation can't be settled from the sources in the folder. The report shows the 27,700 price; I ignored it when judging the model.

**What I re-checked against the Q3/2026 page images and BQ**
- **Welfare-fund (KTPL) rate, p30:** 13,979,344,350 / 69,896,721,750 = 20.0%. The 69.897 bn is Q3/2026 profit alone, and it matches BQ `NP_P0` for 2026Q3.
- **Balance sheet, p4–6:** cash 171.22, loans 110.03 + 196.34 and dividend payable 70.36 give net debt 205.51, which matches the model. CIP is 407.04. Long-term investments 398.05 equal the sum of `INV_BOOK`. "Phải trả dài hạn khác" 298.97 equals the 146.99 deposits plus the 151.99 NQ 76 balance.
- **Revenue and cost of sales, p31:** land lease and management fees bring 21.33 bn revenue in Q3 against 13.67 bn cost.

**Could the centre be too high?**
- **Non-cash share of profit (`nc` axis):** the axis is 0/10/20% with a 10% mean, and that weight is the analyst's own judgement. Deferred revenue of 762.16 bn (codes 319 + 337) spread over at most 27 years releases at least 28.2 bn a year, about 22.6 bn after tax, or ≈17% of N0. Under the model's own "capex = 1.0× depreciation" framework, the margin on that revenue doesn't reduce it. Moving the mean to 17% costs about −1,180 đ/share, ≈ −4.5% (estimate, by linear scaling of the capex sensitivity). If the average remaining lease is shorter than 27 years, the effect is larger.
- **Capex:** BQ investing cash outflow was about 202 bn in 2025 and 309 bn in the first nine months of 2026, against depreciation of about 90 bn a year. The report acknowledges this as its widest axis (±6,482).

**Could it be too low?**
- **Inventory of 118.0 bn** (unchanged since the start of the year) and **supplier prepayments of 72.6 bn** (+58.4 in nine months) appear nowhere in `val()` or in any revision. House-and-land revenue is only about 1.3 bn a quarter, so the inventory may be land or resettlement stock rather than operating working capital. The prepayment jump may be project capex, which the report's own "new project = book value" rule would add at cost. Together that is up to about +3,650 đ/share before the CK, depending on what the items actually are.
- **Operating cash flow runs about 1.8× profit:** 248 vs 141 bn in 2025, and 263 vs 133 bn in the first nine months of 2026. That points to recurring upfront rent receipts, which the model never credits; it only deducts non-cash revenue.

**Other attacks**
- **Legal (scandal migration):** pass. The SNZ (parent company) case and the ~14 bn tax arrears stay at WARNING and in the HARD ABANDON triggers.
- **Comps/SOTP:** pass. There are no peer comps. One minor point: the associates (Bình Thuận 80, An Bình 24.5) are carried at cost with no impairment check.
- **Flip-flop:** pass. All three rev5 changes come from pages flagged by skeptic r3.
- **Attacks 1, 5 and 7** are `na`: the report makes no fear-buy claim and proposes no order.

<<<VERDICT_JSON>>>
{
  "case_topic": "SZL (Sonadezi Long Thành) — DD REV5 23/11/2026, REPORT_rev5.md",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — report does not claim fear-buy/§2.5 qualification (explicitly states sổ-rule not met)",
    "scandal_migration_risk": "pass — SNZ BKS-head prosecution and ~14 bn tax arrears (≈290 đ/cp, ~1%) stated as WARNING with HARD ABANDON (a) covering migration to SZL legal entity/IZ assets; no contrary filing evidence in src",
    "optimistic_comp_sotp_bias": "pass — no peer/M&A comp; SOTP = SZC/SZB stakes net of 20% CGT with holdco 0% base (10%/25% sensitivities shown), unlisted 113.25 at book; minor: associates Bình Thuận 80 + An Bình 24.5 at cost without impairment check",
    "data_provenance": "pass — recomputed from page images: KTPL 13.979/69.897=20.0% (p30; 69.897 = Q3 NP, matches BQ NP_P0 2026Q3); cash 171.22, loans 110.03+196.34, div payable 70.36 → net debt 205.51 = model; CIP 407.04; LT investments 398.05 = Σ INV_BOOK; 338 = 146.99+151.99. Labelled estimates: DC 78.7, nc weights, Long Phước 920 (press), FY2025 audit opinion and ex-date unverified — all flagged in §8",
    "liquidity_capacity_realism": "na — no order proposed; CK computed only for labels",
    "confirmation_bias_flipflop": "pass — rev4b→rev5 +331 = three filing-anchored items (NQ76 via equity statement p29, KTPL p30, Tân Đức TM11 p24), all raised by skeptic r3; the Tân Đức +1,391 offsetting KTPL −1,766 comes from a skeptic-identified asset, not reinterpretation; control reproduces rev4b 25,852",
    "exit_discipline_gap": "na — no sizing/entry claim; still lists two-way milestones + HARD ABANDON (a)(b)(c)",
    "missing_items": "fail (unquantifiable but material) — (1) inventory 118.03 bn (unchanged YoY; house-and-land revenue only 1.3 bn/q ⇒ possibly land/resettlement stock, not operating WC) and supplier prepayments 72.61 bn (+58.4 in 9M, possibly project capex) absent from val() and never discussed in any revision: up to (118+58)/48.2 ≈ +3,650 đ/cp pre-CK (~13% of centre), direction UP, nature unverified; (2) deferred revenue 762.16 (319+337) handled only by an [UL] nc axis 0/10/20%, mean 10%: straight-line over ≤27 years gives ≥28.2 bn/yr ⇒ ≥17% of N0 after tax (margin irrelevant when capex=1.0×D&A offsets D&A) ⇒ ≈ −1,180 đ (−4.5%, estimate), larger if the average remaining lease is <27 years, direction DOWN; (3) BQ CF_OA ≈1.8× NP (2025: 248 vs 141; 9M/2026: 263 vs 133) ⇒ recurring upfront receipts never credited, direction UP, while CF_Invest 202 (2025) / 309 (9M/2026) ≫ D&A ~90, direction DOWN — capex/receipts not reconciled against the same cash-flow data; (4) FY2025 audit opinion, ex-date of the 70% bonus, Long Phước total investment 920, licence 2053 — still open (flagged); (5) SNZ related-party balances/guarantees not checked; tax ~14 bn ≈1% immaterial"
  },
  "independent_verification": "Read page images q3_p04/p05/p06/p30/p31 directly: KTPL 20.0%, Q3 NP 69.897 (= BQ), net debt 205.51, CIP 407.04, LT investments 398.05, deferred revenue 762.16, KTPL fund 23.96 — all match the model. Separately extracted inventory 118.03 and supplier prepayments 72.61 from p04 — the model does not use them. BQ szl_cf_hist: CF_OA/NP ≈1.8× in 2025 and 9M/2026.",
  "killer_objection": "The base omits ~176 bn of balance-sheet assets (inventory 118 + supplier prepayments 72.6, ≈13% of centre) while deducting an analyst-chosen non-cash share (10%) below its own straight-line floor (17%). Both errors are larger than the whole rev4b→rev5 bridge (+331), and they push in opposite directions — so neither the label nor the centre is anchored on these items.",
  "recommended_followups": [
    "Read the TM V.7 inventory note and TM V.4 supplier-prepayment note (Q3/2026): split land/resettlement/project vs operating working capital; apply the 'book value / NPV 0' rule to the non-operating part",
    "Read the TM V.19 deferred-revenue note: 9M amortisation vs new receipts; re-anchor the nc axis on actual amortisation instead of [UL] 0/10/20",
    "Reconcile capex and upfront receipts on the same cash-flow series (CF_OA, CF_Invest by year) to replace the 1.0×D&A assumption with a split of maintenance vs growth vs NPV-0 projects",
    "Fetch the FY2025 audited report (opinion) and the HOSE/VSD notice for the ex-date of the 70% bonus"
  ],
  "summary": "Rev5 fixes all three skeptic-r3 errors correctly, and the load-bearing figures I re-checked against the page images (KTPL 20.0%, net debt 205.51, CIP, LT investments, deferred revenue) all match. The model still omits balance-sheet items a sector analyst would value: inventory 118 bn and supplier prepayments 72.6 bn (up to ~+13% of centre, nature unverified). The non-cash-profit deduction uses a 10% mean below its own straight-line floor of 17% (≈ −4.5%). Cash flow runs ~1.8× profit while capex is ≫ depreciation, and those two pull in opposite directions without being reconciled. Because the material omissions cannot be quantified from the sources in the folder, the verdict is INCONCLUSIVE, not CONFIRMED. The report shows the 27,700 price; it was ignored in this judgement."
}
<<<END_VERDICT>>>