**Verdict: REFUTED, medium confidence. The centre of 17,673 is probably too HIGH.** The base case assumes the full 2,489 bn of construction-in-progress plus real-estate work-in-progress was paid for 100% from shareholders' equity. That is the most favourable value on the report's own funding sensitivity, and the report gives no evidence for it while there is evidence against it. The report's market prices (16,400, the 0.85× buy gate, sizing) were ignored.

**What I checked myself (all matched):**
- **Real-estate WIP:** the scanned KT25 note 9 (rendered page) shows 1,114,538,001,455 at year-end 2025 and 846,436,018,733 at the start of the year. Total inventory is 6,358.1 bn, which matches BQ `Inventory_P0` for 2025Q4.
- **Base value:** recomputing the residual-income formula from the locked assumptions gives 18,160 vs 18,162 reported.
- **Debt:** BQ shows short-term 5,763.1 + long-term 1,859.2 = **7,622 bn** at Q3/26, matching the figure cited in rev3.
- **KT25 note 9 says 2,447.7 bn of inventory is pledged as collateral for bank loans.**

**Too high:**
- **Funding of the projects (main objection).** With 7,622 bn of debt against 8,720 bn of parent equity, a leverage-neutral split is about 53% equity. The report's own 50% sensitivity gives 13,767 (−22%), and even 75% would be roughly −11% (my estimate). The report justifies 100% by saying "interest during construction is capitalised", but that argument points the other way: under VAS 16, capitalised interest means specific borrowings fund these assets. The capitalised-interest amount should be in the filings' construction-in-progress and borrowing notes, and the report never extracts it. That makes the gap quantifiable and well over the 5% threshold.
- **Real-estate WIP at book value with zero NPV.** The asset rose from 967 bn (2021) to 1,186 bn. Real-estate gross profit was only 24.7 bn in 2024 and 4.6 bn in 2025, on 2025 revenue of 21 bn — about 50 years of turnover at that pace. That is observed evidence that this capital earns well below the 13.5% cost of equity. Rev4 chose 1.0× book, above the roughly 0.70× that rev3 implied. The report shows this only as a −3% to −6% sensitivity.

**Too low:**
- If the land bank's fair value is above historical cost, the centre is understated; this is not quantified.
- The 647 bn of unused tax losses appear only in the good case.
- Rolling the window forward past Q4/26 raises the centre by +14% to +20% mechanically; the report discloses this.
- Bio-asset writedowns are unsupported, so leaving them out of the base is correct.

**Attacks that pass:**
- **Corporate income tax:** the tax notes reconcile. The 15% rate on feed and farming is the standard rate, not a time-limited incentive. Exemptions/reductions (4.8% of pre-tax profit) plus loss carryforward (2.8%) explain the 7.2% effective rate.
- **Bonus/welfare fund, share count, audit, related parties:** these are adequately sourced.
- **Flip from rev3:** it is driven by new audited data, not a reinterpretation, but the size chosen leans favourable.

<<<VERDICT_JSON>>>
{
  "case_topic": "DBC — DD rev4 (REPORT_rev4.md, centre 17,673 VND/share)",
  "mode": "DD_GENERAL",
  "verdict": "REFUTED",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; the report makes no fear-buy/§2.5 claim",
    "scandal_migration_risk": "pass — the only WARNING is 237.1 bn receivable from employees (~178 bn land-clearance advances for livestock projects, H1/26 note 7.1). Write-off sensitivity is −539 VND/share. No asset seizure or licence action is cited.",
    "optimistic_comp_sotp_bias": "fail — no peer comp is used, but the sum-of-parts book add-back sits at the most favourable end of two choices: (a) construction plus real-estate WIP (2,489 bn) counted as 100% equity-funded when parent equity is 8,720 bn and debt 7,622 bn (BQ Q3/26); the report's own 50% sensitivity is 13,767 (−22.1%). (b) Real-estate WIP 1,186 bn valued at 1.0× book with zero NPV while the segment earned 4.6–24.7 bn/yr gross profit in 2024–25 (2025 revenue 21.4 bn); rev3 implied about 0.70×.",
    "data_provenance": "pass — recomputed the base case 18,160 ≈ 18,162; KT25 note 9 real-estate WIP 1,114.54 / 846.44 bn read directly from the scanned page; BQ debt 7,622 bn and inventory 6,358.1 bn (2025Q4) match the filings and rev3. Minor: equity_parent_q3 8,720.41 vs series 2026Q3 8,721.41 (1 bn typo, immaterial). Report market prices ignored.",
    "liquidity_capacity_realism": "na — DD_GENERAL; the sizing/price-gate text was not judged (price-blind)",
    "confirmation_bias_flipflop": "pass (with caveat) — centres went 19,491 → 17,317 → 14,696 → 17,673. The +20.3% in rev4 comes from a real inconsistency flagged by the rev3 skeptic and backed by audited yearly real-estate WIP balances. However, the size was picked at the favourable end (book 1.0×, 100% equity funding) of the rev3 skeptic's +5.4…+28.9% range.",
    "exit_discipline_gap": "na — DD_GENERAL; milestone table in §9 is two-sided",
    "missing_items": "fail — (1) Capitalised borrowing cost and specific debt funding of construction/real-estate WIP (VAS 16 disclosure) not extracted; this is the evidence needed to set the funding share, which the report leaves at 100% with no basis. KT25 note 9 shows 2,447.7 bn of inventory pledged for loans. Effect: −11% (75% equity, estimate) to −22% (50%, roughly leverage-neutral 53%). Material and quantifiable ⇒ REFUTED. (2) Customer advances / commitments specific to real-estate projects and land-bank details for the 1,186 bn are absent. Effect: time-value haircut −3…−6%, or upside if land is above cost. (3) EPR recycling obligation unquantified (−1.5…−4.5%), flagged by the report. Present: audit opinion (EY 2025 unqualified, H1/26 review), share count 431.05 m at 30/9/26, bonus/welfare fund k=11.06%, tax incentive notes, NCI, related party Transeco."
  },
  "independent_verification": "Recomputed the base case from the locked assumptions: 18,160 vs 18,162 reported (match). Read KT25 note 9 from the scanned page: real-estate WIP 1,114,538,001,455 / 846,436,018,733 (match), total inventory 6,358.1 bn = BQ 2025Q4 Inventory_P0 (match), 2,447.7 bn of inventory pledged for loans (not mentioned in the report). BQ ticker_financial 2026Q3: StDebt 5,763.1 + LtDebt 1,859.2 = 7,622 bn (matches rev3 citation).",
  "killer_objection": "The base assumes zero debt funds the 2,489 bn of construction plus real-estate WIP, yet the group carries 7,622 bn of debt, capitalises borrowing costs (which under VAS 16 means specific borrowings fund these assets) and pledges 2,447.7 bn of inventory. A leverage-neutral funding share (~53%) gives about 13.8k (−22%), and the report offers no evidence that 100% is right.",
  "recommended_followups": [
    "Extract the capitalised borrowing cost and any specific loans for construction/real-estate projects from KT25 and H1/26 notes (construction-in-progress, borrowings 22.x, inventory); set the base funding share from that evidence, or from leverage-neutral D/(D+E) if no disclosure exists",
    "Extract real-estate customer advances (người mua trả tiền trước) and project-specific debt; net them against the 1,186 bn real-estate WIP add-back",
    "Justify the real-estate WIP at 1.0× book against the observed 2024–25 gross profit (≈0.4–2% of WIP), or put a time-to-realisation discount (e.g. 5-year realisation at Ke) into the base",
    "Upside side: look for land-bank location/area and acquisition cost to test whether book understates fair value",
    "Fix the equity_parent_q3 vs 2026Q3 series 1 bn inconsistency"
  ],
  "summary": "Rev4's arithmetic reproduces, and the change from rev3 rests on real audited real-estate WIP balances (checked against the KT25 page). But the 17,673 centre stacks two favourable choices with no evidence behind them. First, all 2,489 bn of construction plus real-estate WIP is treated as 100% equity-funded, which shrinks operating equity and lifts operating ROE, even though BQ shows 7,622 bn of debt against 8,720 bn of equity, borrowing costs are capitalised and 2,447.7 bn of inventory is pledged for loans; the report's own 50% case is −22%. Second, slow-selling real-estate WIP is held at full book with zero NPV despite very low segment returns. The tax, bonus/welfare-fund, share-count and audit items hold up. Upside risks (land bank above cost, tax-loss shield, window roll-forward) are smaller or already disclosed, so on balance the centre is biased too high by an amount above the 5% threshold. Market prices in the report were ignored."
}
<<<END_VERDICT>>>