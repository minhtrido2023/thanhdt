**Verdict: CONFIRMED, medium confidence.** The rev4 centre of 51,652 đ/cp holds up. I found one model inconsistency that pushes the centre too high, by about 2.5% (estimate). That is below the 5% materiality bar and does not change the label. The price figures inside the report (74,100, P/E) were ignored; I judged only the model and the facts.

**Re-checked against the filings, all matched:**
- **Welfare/bonus fund 3.51%.** `ocr_h1/p52.txt` shows 379,579,000,000 VND (187,753 provisional + 191,826 top-up). The report's 394.0 / 11,212.5 = 3.514%, which matches.
- **FY2025 receivable provision.** `k58.txt` shows a net release of only (436,554,383,396). So Q4/25 re-provisioned 1,194.4 bn and the r2/rev3 error was real. rev4 fixes it with new evidence from the filing, not to move the number.
- **Share count.** 2,412,949,756 shares matches the post-bonus charter capital of 24,129.5 bn (`k48.txt`).
- **Net cash.** The bridge sums to 39,654.7 bn, with the 5,491.7 bn dividend payable and the 1,409.5 bn minority interest deducted. The 19,740 đ/cp figure excludes the 3,300 bn site-restoration provision (ARO), which is deducted separately.

**Where it could be too high:**
- **The Q4/25 add-back is inconsistent with the regression.** From `np_hist_gas.csv`, Q4 profit has been below the Q1–Q3 average in every year since 2020: 0.82, 0.88, 0.84, 0.92, 0.73 and 0.41 (2025).
  - The 2016–2025 regression keeps the year-end charges of every year except 2025.
  - The residual term (RES) then adds the whole Q4/25 charge back (+955.5 bn) as a one-off.
  - Meanwhile PVPower receivables doubled, from 4,003 to 8,870 bn. A recurring year-end provision is plausible, so the +1,555 đ/cp from the rev4 fix rests on an unproven one-off assumption.
- **PVComBank deposit.** 1,783.6 bn at a related-party restructured bank is held at full book value (about 739 đ/cp).

**Where it could be too low:**
- The 3.51% welfare rate rests on a single year, 2025. If that year's top-up was one-off, the rate is overstated (worth up to +1,215 đ/cp).
- The ARO is deducted in full and undiscounted (+976 đ/cp if spent in 10 years).
- The deduction for lower depreciation (−747 đ/cp) may be too harsh.

**Missing items checklist:** no absent material item. Committed capex of 21.2 trillion VND, the ARO, share basis, welfare fund, related parties, audit opinion and contract expiries are all present. The biggest unknown is the 12/2026 expiry of the old-field gas contracts. It is shown only as a sensitivity (−1,995 to −7,980 đ/cp, not in the centre), and its 22% share of volume rests on an unverified estimate of 8 bn m³.

<<<VERDICT_JSON>>>
{
  "case_topic": "GAS (PV GAS) — DD rev4 23/11/2026, centre 51.652 đ/cp after 5bn liquidity discount",
  "verdict": "CONFIRMED",
  "confidence": "medium",
  "mode": "DD_GENERAL",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; the report makes no fear-buy/§2.5 claim",
    "scandal_migration_risk": "pass — legal WARNINGs (free float 4,24% due 31/12/2026, Chair/CEO dismissed 07/2026 for an unverified reason) are disclosed and kept out of the centre; nothing in the cited filings points to asset/licence/legal-entity risk",
    "optimistic_comp_sotp_bias": "pass (minor fail toward HIGH) — no comp is used; the SOTP bridge recomputes exactly (net cash 39.654,7 = 15.540,6+35.269,9+7−1.551,2−2.710,4−5.491,7−1.409,5). Weakness: the 2016–2025 regression keeps every year's year-end charges except 2025, yet RES adds the whole Q4/25 provision back (+955,5 bn) as a one-off, although Q4/(avg Q1–Q3) has been <1 for 6 straight years (0,82/0,88/0,84/0,92/0,73/0,41) and PVPower receivables doubled 4.003→8.870 ⇒ centre biased up by an estimated ~+1.300 đ/cp (~2,5%, below the 5% bar)",
    "data_provenance": "pass — 379.579.000.000 (ocr_h1/p52), (436.554.383.396) (k58), 24.129,5 bn charter capital / 2.412.949.756 shares (k48) all match; the 8 bn m³ dry-gas volume is labelled an estimate; a few items are explicitly marked unverifiable (contract renewal, Lô B IRR, the 540,7 bn dividend gap)",
    "liquidity_capacity_realism": "na — no position proposed (above-zone label), max 2% NAV if LAG buys mechanically; median ADV 113 bn vs 5 bn order size",
    "confirmation_bias_flipflop": "pass — centre 50.146 → 50.651 → 51.652 driven by errors found in the filings (FY2025 provision 436,6 vs 1.631 9M figure, welfare fund 1,91%→3,51%), confirmed by OCR; label unchanged; price-zone ledger not opened per the blind rule",
    "exit_discipline_gap": "na — DD_GENERAL with no sizing claim; the report still states HARD ABANDON (delisting / 4-quarter profit < 9.500 bn at Brent ≥ 80)",
    "missing_items": "pass — committed capex 21.238,7 bn (TM35, growth, NPV 0 + ±5% sensitivity), mandatory ARO 3.300 deducted 100%, share basis verified, welfare fund verified, PVPower/PVN/PVComBank related parties quantified, FY2025 audit clean (Deloitte 28/02/2026), base-year one-offs reviewed, gas contracts expiring 12/2026 shown as sensitivity. Nothing material absent; residual: PVComBank deposit 1.783,6 bn at par (~739 đ/cp), the 12/2026 expiry is a sensitivity not a probability (−1.995…−7.980)"
  },
  "independent_verification": "Re-read OCR: welfare fund 379,579 bn (p52) ⇒ 394,0/11.212,5 = 3,514% matches; FY2025 receivable provision net release 436,55 bn (k58) matches ⇒ Q4/25 re-provision 1.194,4 matches; charter capital 24.129,5 bn ⇒ 2.412.949.756 shares matches assumptions_r4.json; net-cash bridge re-summed = 39.654,7 matches; Q4 seasonality recomputed from np_hist_gas.csv ⇒ found the fit/RES inconsistency",
  "killer_objection": "The Q4/25 add-back (+955,5 bn into RES, ≈+1.555 đ/cp combined with the regression point) assumes year-end provisioning is a one-off, while 6/6 years since 2020 had weak Q4s and PVPower receivables doubled to 8.870 bn — if the charge recurs, the centre is ~2–3% too high; on the other side, the 12/2026 gas-contract expiry (~22% of volume, estimated) is the largest unquantified risk and could cut 4–15%",
  "recommended_followups": [
    "Make the regression and RES consistent: either adjust year-end provisioning for every year 2016–2025 (TM in each audited FS), or do not add back Q4/25 — report both",
    "Collect Q4 provision / CP QLDN for 2020–2024 to test whether the year-end charge is recurring",
    "Check whether the 3,51% welfare rate repeats in 2024 (prior year's AGM resolution) instead of relying on one year",
    "Follow the renewal of contracts Lô 05.2/05.3/05-1b/c and NCS–NT2 after 12/2026; replace the 8 bn m³ estimate with a primary figure (annual report)",
    "Consider a haircut on the PVComBank deposit as a sensitivity"
  ],
  "summary": "The rev4 model and facts are well traced: the two rev4 fixes (welfare fund 3,51%, FY2025 receivable provision 436,6) match the original OCR, and the share count and net-cash bridge recompute exactly. The fix is driven by an error found in the filings, not by price. The remaining weakness, toward HIGH, is an inconsistency between the 2016–2025 regression (which keeps year-end charges) and RES (which adds back the whole Q4/25 charge as a one-off) despite a recurring weak-Q4 pattern and a doubling of PVPower receivables — an estimated +2,5% to the centre, below the materiality bar and not enough to change the label. On the other side, the welfare rate taken from a single year, the undiscounted ARO and the depreciation deduction may make the centre slightly too low. The largest risk, the 12/2026 gas-contract expiry, is disclosed as a sensitivity, not absent. Medium confidence because the recurrence of Q4 provisioning was not checked across prior years."
}
<<<END_VERDICT>>>