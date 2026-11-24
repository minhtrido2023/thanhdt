**Verdict: INCONCLUSIVE (medium confidence).** The recheck's arithmetic holds up. What fails is its claim that the new rules "only need mechanical confirmation." It inherits an unresolved load-bearing assumption, leaves out one material obligation, and applies the "base = book value" rule in one direction only.

**What I checked myself**
- I re-ran `calc/calc_recheck.py` with the project venv. The output is byte-identical to `run1.txt` (md5 `354ddca1…`).
- I evaluated `value()` by hand at the central parameters, before the liquidity discount: 53,826 VND/share at r 13.5% and 57,151 at 12.3%. That is +6.2%, against +6.02% in the report, so the result is consistent.
- V_ngắn: the four quarterly net profits from BQ for 2025Q3 add to 365.8 + 284.6 + 351.4 + 323.4 = 1,325.3 bn VND. That gives 40,547 VND/share, which matches the report.
- The report quotes a market price. I ignored it.

**How the centre breaks down (central point, VND/share)**

| Component | VND/share |
|---|---|
| Operating core at P/E 1/r | 21,605 |
| Net financial assets | 16,336 |
| 937 ha of unleased land | 13,137 |
| Recovery of costs already spent on that land | 6,488 |
| Credit loss | −1,255 |
| Future tax | −1,915 |

**Places the centre could be too HIGH**
1. **Land value rests on an estimate.** About 36% of the centre depends on a net value of 12 bn VND/ha ("toàn phần", after compensation, infrastructure and tax). Its only basis is "ước lượng" (an estimate) in the 01/11 report, and no source backs it. The ×0.75–1.25 axis is a guess around a guess.
2. **Land rent owed to the State (G16) is not in the model.** The core valuation excludes the land segment, and the 15,077 bn of deferred revenue only bears tax. Any annual rent on land already leased therefore sits nowhere. At ~100 bn VND/year, the present value is about −3,000 VND/share (−5.6%). It is not quantified, so it is material but open.
3. **Area already leased in the first nine months of 2026 is counted twice.** Deferred revenue rose by +1,701.8 bn in that period. At gross land prices this implies roughly 60 ha, or about −1,000 VND/share. The report admits the bias runs downward but keeps it out of the centre.
4. **Credit exposure:** 6,016 bn VND of non-bank credit (116% of parent equity) with borrowers unidentified (G1/G2). The model puts 60% weight on zero loss.
5. **Smaller items:**
   - The book assets (396.8 bn) come from scanned images and were never checked against text.
   - The insider advance of 643.7 bn ("to find and buy land") is in the base at full recovery.
   - The Q3 consolidated statements are unreviewed.
   - The gross-margin normalisation (−1,228) is left out of the base.

**Places the centre could be too LOW**
1. **Asymmetric book-value rule (the strongest objection).** The 643.7 bn insider advance went into the base under "base = sổ sách" (base = book value). Deductible VAT of 890.5 bn, a cleaner asset, stayed out (+3,123 VND/share, +5.7% net of the DTL) only because the notes weren't read.
2. **Non-controlling interest:** the balance-sheet share is 9.9%, but the model's centre is 20% (+1,735, +3.2%).
3. **Growth on new land:** setting RONIC = Ke on the core removes utility and service income from tenants on the 937 ha. That income needs little capex because infrastructure is already netted out of the per-ha value. Not quantified.
4. **Discount rate:** the base r of 13.5% sits above the top of the Ke band (13.4%). Effect +0.47%, immaterial.

Netting the items the report quantified but left out (+4,858 up, −2,228 down) suggests the centre leans about 4.8% too low. That is just under the 5% trigger, so it does not on its own count as REFUTED.

<<<VERDICT_JSON>>>
{
  "case_topic": "SIP — DD recheck 24/11/2026 (r3 model re-run under B5/E15/E16 rules; centre 54,466 VND/share unchanged)",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — no fear-buy/§2.5 claim in the report",
    "scandal_migration_risk": "fail (unquantified) — the report itself flags a WARNING: non-bank credit of 6,016 bn = 116% of parent equity, borrowers unidentified (G1/G2), plus a 643.7 bn advance to employees 'to find and buy land' (TM7). The recheck checks no legal/related-party status ('quick check 24/11: no new facts' with no source cited)",
    "optimistic_comp_sotp_bias": "fail (partial) — the land leg (13,137 + 6,488 VND/share recovered cost ≈ 36% of centre) rests on 12 bn VND/ha net ('toàn phần'), which REPORT_v1/investor_report 01/11 label only as an 'estimate' (110–120 USD/m² after compensation/infrastructure/tax), no transaction source; the ×0.75–1.25 axis is a guess around a guess. Recomputed SOTP: core 21,605 + financials 16,336 + land 13,137 + recovered cost 6,488 − credit 1,255 − future tax 1,915 ≈ 54.4k, consistent",
    "data_provenance": "fail (partial) — book assets 396.8 bn from scanned images, not checked against text (assumptions_r3 states this outright); Q3 consolidated statements unreviewed; 242.112943m share count has no date/source in the recheck; 12 bn/ha unsourced. Positive: BQ NP TTM 1,325.3 recomputed and matching; the run reproduces byte-identically",
    "liquidity_capacity_realism": "na — no position proposed (rule 4 not met); 2% NAV is only conditional 'if the user considers it'",
    "confirmation_bias_flipflop": "pass — r2 54,230 → r3 54,466: the cumulative bridge (6 steps, each tied to a numbered correction, from model_r3_out.txt) explains the whole change; recheck 0%. dd_price_zones.json not opened per the blind constraint",
    "exit_discipline_gap": "na — no buy recommendation",
    "missing_items": "fail (unquantified, material) — (1) land rent paid to the State (G16) is in neither the core (land segment excluded) nor the deferred revenue (tax only); PV at ~100 bn/yr ≈ −3,000 VND/share (−5.6%), unknown; (2) related-party identity of 6,016 bn of credit + 643.7 bn advance (G1/G2); (3) ha leased in 9M26 counted twice (deferred revenue +1,701.8 bn ⇒ ~60 ha ⇒ ≈ −900…−1,000) left out of the centre despite a known downward bias; (4) AGM/board committed capex for the last 12 months not cited (mitigation: 12 bn/ha is defined net of infrastructure, and the 3,262.8 bn of accrued infrastructure for leased land is already deducted); (5) share count/ESOP/stock dividend basis not given. Pass: welfare fund (KTPL) on core, land and deferred revenue; FY2025 EY unqualified opinion; land bank 937.1 ha (AR25)",
    "symmetry": "{too_high_checked: 9, too_low_checked: 9, too_low_items: ['deductible VAT 890.5 − DTL 123.7 excluded (+3,123, +5.7%) while the 643.7 advance is in the base at book: asymmetric use of the base=book rule', 'NCI on subsidiaries: centre 20% vs balance sheet 9.9% (+1,735, +3.2%)', 'RONIC=Ke on the core removes utility/service income from new tenants on 937 ha, which needs little capex since infra is netted in 12 bn/ha (unquantified)', 'base r 13.5% sits above the Ke band top 13.4% (+254, immaterial)', 'credit-loss axis 0/10/30% with no independent basis since EY made no provision (−1,255 could be too heavy; can go either way)', 'taxdef ×1.2 axis vs no deferred tax asset (pass, symmetric)', 'D3 environmental infra for 937 ha flagged as possibly missing although 12 bn/ha is defined net of infra (centre need not fall)', 'recovery of 60% removed from the axis (pass, up-consistent)', 'gross-margin normalisation −1,228 checked; not a too-low item'] — m = n"
  },
  "independent_verification": "Re-ran calc_recheck.py (wc_venv): md5 354ddca1… identical to run1.txt. Hand-evaluated value() at central parameters before the liquidity discount: 53,826 @13.5%, 57,151 @12.3% (+6.2% vs report +6.02%, consistent). Recomputed V_ngắn from v6_bq.csv: 365.8+284.6+351.4+323.4 = 1,325.3 bn / 13.5% / 242.113m shares = 40,547 ✓. Did not re-check balance-sheet figures (cash 400.8, deposits 7,187.6, credit 6,016) against the PDF (scan, no text layer).",
  "killer_objection": "The recheck declares 'only mechanical confirmation is needed', but its centre rests on (a) a net land value of 12 bn/ha with no source (~36% of centre) and (b) a book-value rule applied one way: insider advances go in at book (+826), deductible VAT stays out (+3,123); meanwhile land rent to the State (G16) is missing from every component of the model. Netting the quantified items left out of the centre, the centre leans about +4.8% too LOW, yet the unquantified G16 could pull it ~5% too HIGH. Neither direction is resolved.",
  "recommended_followups": [
    "Read the land-lease and land-rent notes (G16): annual rent vs one-off payment for the areas already sub-leased; if annual, deduct the PV in the base",
    "Read the VAT/DTL notes: if deductible VAT is recoverable against output VAT from land leasing, put it in the base consistently with the base=book rule (or take the 643.7 advance out of the base as well)",
    "Get the ha leased in 9M26 (G12) from the Q3 statements/announcements and deduct it from 937.1 ha in the base, not just as a sensitivity",
    "Find a transaction or audited-margin source for 12 bn/ha net (recent sub-lease margins of Phước Đông/Lộc An), or widen the axis",
    "Identify the borrowers G1/G2 and check related-party status before keeping 60% weight on zero loss",
    "Record the share-count basis (date + source) and any stock-dividend/ESOP plans"
  ],
  "summary": "The SIP recheck reproduces exactly (identical md5; the r 12.3–14.5% sensitivity is consistent when recomputed by hand), so the narrow claim 'centre unchanged under the new discount-rate rules' is right. As a DD, however, the centre is not well enough founded to be called confirmed. Too-high side: land value at 12 bn/ha rests only on an estimate (~36% of centre), land rent to the State (G16) is not in the model (could be ~−5%), double-counted 9M26 leased area is left in the centre although the bias is known, and 6,016 bn of credit has unidentified borrowers. Too-low side: deductible VAT (+5.7%) is left out while the insider advance is in the base under the same 'book value' rule, balance-sheet NCI 9.9% vs 20% in the model (+3.2%), and RONIC=Ke ignores service income from new tenants. Net quantified leaning is about +4.8% too low, but the unquantified G16 points the other way; hence INCONCLUSIVE, naming G16, the 12 bn/ha source and VAT as the items to settle. The market price in the report was ignored."
}
<<<END_VERDICT>>>