**Verdict: INCONCLUSIVE (medium confidence).** The dilution maths is correct and I reproduced it. But the DƯỚI label rests on a convention the user has not yet ruled on, and two material items are still open in the report.

**What I checked myself**
- **Share counts:** 431.99M × 5:3 = 259.19M new shares, which matches the 259,191,580 in TT08. Then 691.18M × 1.07 = 739.56M. Correct.
- **EX centre:** (13,969 × 431.99M + (1 − 0.0141) × 2,591.9bn) / 691.18M / 1.07 = **11,615**. This matches the report. Without the 1.41% liquidity discount on the cash it would be 11,664, so the convention changes the centre by only 0.4%.

**Where the centre could be too HIGH**
1. **The holding discount is load-bearing and unresolved.** With 0% holding discount the EX centre is 11,615 (DƯỚI). With 27% it is 8,808 (TRONG), a −24% swing. The r3 errata says about 85% of the r3 move up to 13,969 comes from this one convention. The report flags it honestly, but the label cannot be called confirmed until the user decides.
2. **Losses in the "TCH only" scenario are under-counted.** The model scales the cash going into NĐL by the coverage rate. In reality HHS is committed to putting the full 2,591.9bn into NĐL and borrows to cover the gap. At k = 0.8 that hides about 216bn of loss, roughly −290 đ/share (−2.4%). That is below the 5% materiality line, so it is not a refutation.
3. **Missing item: further capital calls.** Lot I.14 costs 6,223bn in total. The 2.6tn raise plus NĐL's 1.82tn charter capital do not cover it, and the rest is "vốn tự có + vay". The report does not consider another equity call or debt build-up in NĐL before handovers start in 2028. This is material but I could not quantify it.
4. **Missing item: Q3/2026 subsequent-events notes.** The report says itself it has not read them. Nor has it checked whether the 100bn loan from TCH was drawn (it relies on the earlier skeptic for that).

**Where the centre could be too LOW**
- **The k = 0.946 downside has no real basis.** Line 68 of `calc/dilution_calc.py` assumes only HHS's 2.6tn goes into NĐL. But if HHS really ends at 75.41% rather than the self-computed 79.8%, others must buy about 25.9M more NĐL shares at the same 10,000, still below the 11,210 book value. On that reading HHS gains about +53bn, which is k ≈ 1.02, not a −141bn loss. The effect is small (−1.6%), but presenting it as the "downside with a basis" is wrong.

**Provenance gaps**
- NĐL's book value of 11,210 comes from a self-prepared, unaudited statement at 31/12/2025.
- TCH's direct 38.19% stake and the TCH loan status are taken from the earlier skeptic, not checked by the author.

**Price-blind note**
- The report contains market prices (9,990, the TERP of 9,346, DNSE fills). I ignored them.
- I did not open `kb/dd_price_zones.json`, so the flip-flop check against earlier rows is marked `na`.
- r3 itself records the centre drifting by convention (11,900 → 10,387 → 8,393–9,700 → 13,969), not because of new data.

<<<VERDICT_JSON>>>
{
  "case_topic": "HHS — r4 dilution update (60% rights issue at 10,000 + 7% stock dividend), DD_GENERAL",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — the report makes no fear-buy/§2.5 QUALIFY claim; it says itself that HHS does not qualify under §2.5 and is excluded by forensic_flags",
    "scandal_migration_risk": "pass (partial) — no legal/regulatory WARNING found in the report; it does flag a related-party governance WARNING (TCH→HHS loan of up to 100bn; raise proceeds flow into NĐL inside the TCH/CRV group; the board allocates unsold shares). It has not scanned news outside the company website for 01–10/11, so this is incomplete",
    "optimistic_comp_sotp_bias": "pass/minor fail — no comps used. k=1 follows rule 20 (NPV 0). But the 'downside with a basis' k=0.946 (calc line 68) assumes NĐL post-money = eq0 + 2.6tn only, which is inconsistent with HHS ending at 75.41%. If others subscribe ~25.9M shares at 10,000 < BV 11,210, HHS gains ~+53bn (k≈1.02), not −141bn. Effect −1.6% of centre, not material",
    "data_provenance": "partial fail — share count, price and proceeds trace to NQ ĐHĐCĐ 01/2026 TT08/TT09 and NQ HĐQT 07 (PDFs in src_hhs). NĐL BV 11,210 comes from a self-prepared, unaudited BCTC at 31/12/2025. TCH's 38.19% stake and the TCH loan not being drawn at Q3 are 'per skeptic', not self-checked. V_pre 13,969 is inherited from r3 and not re-derived here",
    "liquidity_capacity_realism": "na — the report proposes no position size; HHS is EXCLUDED from candidate plans",
    "confirmation_bias_flipflop": "na — the brief forbids opening price-zone ledgers. For the record, r3 itself logs centre drift by convention: 11,900 → 10,387 → 8,393–9,700 → 13,969 (or 10,761 with holding discount), driven by conventions, not new data. r4 is a mechanical transform of r3",
    "exit_discipline_gap": "na — not a fear-buy/sizing claim; still lists added HARD ABANDON triggers (NĐL issues to others at a lower price; proceeds not going into NĐL)",
    "missing_items": "fail (unquantifiable but material) — (1) the remaining funding for lot I.14 (total 6,223bn; the 2.6tn raise does not cover it): no further dilution or NĐL debt build-up modelled before 2028; (2) Q3/2026 subsequent-events notes not read; (3) offer validity/distribution deadline unknown. Quantifiable but below 5%: the TCH-only scenario applies k to c×cash instead of the full 2,591.9bn committed, so at k=0.8 a loss of ~216bn ≈ −290 đ/share (−2.4%) is hidden. Present and pass: share-count basis (431.99M → 691.18M → 739.56M, dated sources), audit/BV source flagged, related-party flows flagged"
  },
  "independent_verification": "Recomputed EX centre: (13,969×431.99M + 0.9859×2,591.9bn)/691.18M/1.07 = 11,615, matching the report (11,664 without the liquidity discount on cash). Share counts 259.19M = 0.6×431.99M and 739.56M = 1.07×691.18M match TT08/TT09. Re-derived the k from the 75.41% stake: implies ~25.9M NĐL shares issued to others ⇒ k≈1.02, contradicting the report's k=0.946.",
  "killer_objection": "The DƯỚI label depends entirely on a 0% holding discount, which is still awaiting the user's ruling. At 27%, the EX centre drops to 8,808 (−24%) and the label flips to TRONG. The dilution maths is right, but it carries an unresolved convention.",
  "recommended_followups": [
    "Get the user's ruling on holding discount 0% vs 27% before any ledger entry; until then record both centres (11,615 / 8,808)",
    "Fix the k=0.946 derivation: either model the extra NĐL subscribers explicitly or drop it as 'downside with a basis' (on the 75.41% reading it implies k≈1.02)",
    "In the c<1 scenarios apply k to the full 2,591.9bn committed into NĐL plus the cost of the borrowed shortfall",
    "Model the remaining funding for lot I.14 (6,223bn total) and the chance of another NĐL/HHS capital call before 2028",
    "Render and read the Q3/2026 subsequent-events notes and confirm the TCH 100bn loan status yourself"
  ],
  "summary": "The r4 dilution maths is correct and reproducible (centre 11,615, share counts tie to TT08/TT09). But the DƯỚI label rests on a 0% holding discount that the user has not ruled on; at 27% the centre falls 24% and the label becomes TRONG. Too-high risks: losses in partial-coverage scenarios are under-counted (~−2.4% at k=0.8), no further capital call for lot I.14 is modelled, and the Q3 subsequent-events notes are unread. Too-low: the k=0.946 'downside with a basis' is built on an internally inconsistent post-money assumption and should be ~1.02. No quantifiable missing item exceeds 5% of centre, so the report is not refuted, but it cannot be confirmed while the holding-discount convention and those items are open. Market prices in the report were ignored."
}
<<<END_VERDICT>>>