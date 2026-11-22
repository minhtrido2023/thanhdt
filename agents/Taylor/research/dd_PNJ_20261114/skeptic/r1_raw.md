The verdict is **REFUTED**: the PNJ valuation block contradicts itself, and the NON conclusion stands. I checked the main numbers against BigQuery and re-ran the report's model.

**Independent checks (all match):**
- Re-running `calc/model_r2.py` reproduces the report's figures: 6,366, 7,635, 14,368, 3,267 and estimated end-2026 book value per share 12,586.
- BigQuery `ticker_financial` matches the report's company numbers:
  - Profit after tax: Q4/25 1,218.1; Q1/26 1,467.4; Q2/26 −282.9; Q3/26 −256.9.
  - Shares outstanding: 511.72 million.
  - Operating cash flow: Q4/25 −1,695.0; Q3/26 −2,874.1. The trailing-twelve-month figure of −2,579.5 also adds up.

**Fatal flaw (centre too HIGH): the share count does not fit the model's own value.**
- The base case puts the post-raise company at F ≈ 6,759 bn VND (6,366 × 1,061.72m shares), and says the 8,000 bn raised goes entirely to the trade-in buy-backs.
- Dividing by 550m new shares means new investors pay at least 14,545 per share for stock the model values at 6,366.
- If investors pay what the model says the shares are worth, existing holders get (F − 8,000)/511.72:
  - base, g = 5%: **−2,425 per share** (about zero, worth only option value)
  - base, g = 0%: **208**
  - weak case: **−8,855**
  - good case: 14,177
- So the 6,370–7,640 range only holds if new investors overpay. On the model's own logic the base case is close to zero for existing holders, or the raise fails. That gap is far above the 5% threshold. The report's own fact supports this: at book value of about 12,590, 550m shares raise only about 6,923 bn, short of 8,000.

**Centre too LOW (weaker, but real):**
- It capitalises the 2029 plan year forever, at a 2.8% net margin, while the plan still shows revenue growing about 14% a year. The report admits this but leaves it out of the range.
- Excess inventory (cost 18,855 vs 15,881 at the start of the year) could free up cash, and none of that is counted.
- The 2026 plan itself is management's crisis plan; nothing shows whether it is conservative or optimistic.

**Missing items:**
- The cost of 100% of customers redeeming instead of the planned 80% is about 1,768 bn. That is about 26% of base F, is quantifiable, and is not in the range.
- The FY2025 audited statements were "not read".
- The gold-bar licence status under Decrees 232 and 390 was not checked.
- Not checked: share-count history (the BQ share count jumped from 341m to 511.7m in Q1/2026), ESOP, welfare fund, guarantees, and customer lawsuits over delayed buy-back payments.
- The `src/` folder of source PDFs is not on disk, so none of the figures from the filings could be traced. Only the BigQuery figures were confirmed.

I set aside the market prices in the report's own text (§0, §6, §8) and judged the model only. Following the brief, I did not open `kb/dd_price_zones.json`.

<<<VERDICT_JSON>>>
{
  "case_topic": "PNJ — DD r2 14/11/2026 (Q3/2026 financials, trade-in buy-back crisis, 550m-share private placement), keep-excluded NON verdict + valuation block",
  "mode": "DD_GENERAL",
  "verdict": "REFUTED",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; the report makes no fear-buy/§2.5 claim (verdict is keep-excluded NON)",
    "scandal_migration_risk": "pass — the report itself documents migration into the economics (21,058 bn trade-in obligation, bank loans −606.5, CFO of finance resigned 06/11, chairwoman's unsecured 700 bn loan) and lists what has not migrated yet (legal entity, audit, licence). Remaining gaps: the link to a board member's brother is from the press only, not checked against company disclosures; the gold-bar licence under Decrees 232/390 was not checked",
    "optimistic_comp_sotp_bias": "fail — no peer comps (admitted), but the core flaw is in the residual-income/Gordon model: base F ≈ 6,759 bn (6,366 × 1,061.72m shares) while 8,000 bn of new money is fully absorbed by trade-in obligations; dividing by 550m new shares implies investors pay ≥14,545 for shares the model values at 6,366. If the raise happens at model value, existing holders get (F−8,000)/511.72 = −2,425 (base g5), 208 (base g0), −8,855 (weak case). The 6,370–7,640 centre is materially too HIGH. Pushing the other way: capitalising 2029 forever at a 2.8% net margin while revenue still grows ~14%/yr is too LOW (the report admits this but leaves it out)",
    "data_provenance": "fail (partial) — BQ figures match my recompute (profit Q4/25 1,218.1, Q1 1,467.4, Q2 −282.9, Q3 −256.9; shares 511.72m; operating cash flow Q4/25 −1,695.0, Q3/26 −2,874.1; TTM −2,579.5). But the src/ folder cited for every filing figure is NOT on disk ⇒ the 21,057.9 trade-in obligation, 7,071 provision, bank loans by lender, equity 13,182.3, 2027–29 plan and 550m-share filing cannot be traced locally. ROE 10% / equity 15.8k and g 5% are estimates; the note-17 contradiction (6,104 / 6,783 vs balance 821.4) is still open",
    "liquidity_capacity_realism": "na — no sizing proposal; NON verdict",
    "confirmation_bias_flipflop": "pass (limited) — the NON verdict has been consistent 28/09 → r1 → r2; the move from r1 to r2 (dropping the 800/6% weak case, dropping the weights, adding g=0) was driven by the previous skeptic review, not new information, and every change pushed the centre UP; the replacement weak case (plan delayed 1 year) is no better grounded than the one dropped. As the brief required, I did not open dd_price_zones.json, so I could not compare against the ledger rows",
    "exit_discipline_gap": "na — no entry/sizing; the report does set two-sided milestones (Q4/2026 results, placement before 31/12/2027, FY2026 audit, Q1/2027)",
    "missing_items": "fail — (1) the extra loss if 100% of customers redeem instead of 80% (~1,768 bn ≈ 26% of base F) is quantifiable and left out of the centre; (2) the FY2025 audited statements were not read (audit opinion for the latest year missing); (3) gold-bar licence status under Decrees 232/390 not checked (24K segment ≈17% of Q3 revenue; material, not quantifiable); (4) share-count history/ESOP not checked: BQ shares jumped from 341.1m to 511.7m in Q1/2026 with no explanation in the report; (5) welfare/bonus fund, guarantees/related-party flows beyond the chairwoman's loan, customer lawsuits over delayed payment, and recoverability of the 773 bn deferred tax asset not assessed; (6) committed capex: pass (9-month capex 57.4 bn, store count shrinking)"
  },
  "independent_verification": "Re-ran calc/model_r2.py: reproduced 6,366 / 7,635 / 14,368 / 3,267 and estimated book value per share 12,586 (=(13,182.31−6,741.66)/511.72). BQ ticker_financial PNJ: profit Q4/25–Q3/26, shares 511.72m, operating cash flow Q4/25 −1,695.0 and Q3/26 −2,874.1 all match the report. Fair-value consistency check: base F ≈ 6,759 bn < the 8,000 bn raise ⇒ existing holders ≈ 0.",
  "killer_objection": "The valuation divides post-raise firm value by 511.72m + 550m shares while assuming the full 8,000 bn goes to settling obligations. Base F (~6.76k bn) is below the cash new investors must put in, so the 6,370–7,640 per-share range exists only if new investors overpay ~2.3× the model's own value; under a consistent issue price, existing holders' base-case value is ~0 (−2,425 at g5, 208 at g0).",
  "recommended_followups": [
    "Rebuild the valuation with an internally consistent issue price: existing-holder value = (F − raise)/511.72, or solve P = F/(511.72 + raise/P); show the case where the raise fails/falls short (6,923 bn at book value ~12,590)",
    "Put the extra loss if 100% of customers redeem (~1,768 bn) into the range as a scenario, not just a side note",
    "Restore src/ (BCTC Q3 HN, PwC H1 review, EGM 21/10 documents) to disk so the 21,058 / 7,071 / bank loans / plan figures can be traced",
    "Read the audit opinion in the FY2025 audited statements; check the gold-bar licence under Decrees 232/390; explain the share-count jump 341m → 511.7m in Q1/2026 (bonus issue/ESOP)",
    "Too-low side: add a scenario where the net margin returns to 6.4–7.9% after 2029 (N ≈ 3.7–4.6k) and value any cash freed from excess inventory, with evidence",
    "Run the price-blind pass the report itself says is still owed (new session, lock assumptions + md5 before seeing any price)"
  ],
  "summary": "The NON (keep-excluded) verdict holds up, and the BQ figures (quarterly profit, shares, operating cash flow) match my recompute. The valuation block does not. The model says post-raise PNJ is worth ~6.76k bn in the base case, yet requires 8,000 bn of new money that goes entirely to trade-in obligations. Dividing by 550m new shares assumes new investors pay ≥14,545 per share for something the model values at 6,366. With a consistent issue price, existing holders' value is ~0 in the base case. So the 6,370–7,640 range is materially too HIGH. On the other side, capitalising the 2029 plan year (net margin 2.8%) forever and ignoring cash freed from excess inventory biases it LOW. Missing items: the extra loss if 100% of customers redeem (~26% of F) is outside the centre; the FY2025 audit, the gold-bar licence and the share-count history were not checked. The source PDFs (src/) are not on disk, so every figure taken from the filings is untraceable."
}
<<<END_VERDICT>>>