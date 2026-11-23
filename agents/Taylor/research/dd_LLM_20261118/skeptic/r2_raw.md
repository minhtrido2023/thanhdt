**Verdict: REFUTED, medium confidence.** The balance-sheet arithmetic holds, but the base earnings line counts warranty cost twice. Fixing that alone moves the centre up by more than 5%. On the downside, two material risks are still left out of the base.

**What I re-checked against the filings (all matched):**
- I reran `calc_rev3.py` and its md5 hashes match the report. Net financial position (NFP) is 1,466.16, base pre-discount value 35,760, centre 28,834.
- Audited FY2025 P&L (p12): revenue 5,432.6, gross profit 380.3, so gross margin 7.0%. FY2024 margin was 1.74%.
- Retained earnings at 01/01/2026 are 618.28 on both the audited p44 table and the Q3/26 balance sheet.
- Parent-only equity at Q3/26 is 2,167.7 (total 2,101.5 less a minority interest of −66.25).

**Too LOW — the warranty double count (the killer objection):**
- Selling expense is 0 in both FY2024 and FY2025 (p12). So before the new accounting rule took effect in 2026, warranty accruals sat inside cost of goods sold. Their reversals went to other income (174.3 in 2025, 19.6 in 2024).
- That means the 4.5% historical median margin is already after warranty accruals. The model then:
  - subtracts warranty again as `flow_pct_rev × R × cash_share`;
  - never adds back the non-cash part of the accrual, even though it assumes 75% of warranty is non-cash and calls the policy systematic over-accrual (§2).
- Recomputed with the model's own functions, centre change by annual accrual rate (as % of revenue):

  | Annual accrual | Centre | Change |
  |---|---|---|
  | 0% (double count removed only) | 29,224 | +1.4% |
  | 1% | 30,919 | +7.2% |
  | 2% | 32,615 | +13.1% |
  | 3% | 34,310 | +19.0% |

- The accrual rate is unmeasured. But FY2025 implies at least 544.5 bn (closing 980.11 − opening 609.93 + reversal 174.27), which is about 10% of revenue. Even the 1% case crosses the 5% materiality line.

**Smaller upward error — the 12.8% welfare-fund rate is stale:**
- The report takes it from the 2024 profit distribution and cites TM36 to say 2025 profit has not been appropriated.
- But the Q3/26 balance sheet shows the 2025 distribution already happened. Retained earnings fell 273.2 and the development fund rose 242.3 (125.0 → 367.3). That leaves at most 30.9 for welfare, board bonus and any dividend, i.e. ≤6.3% of 492 bn.
- Effect is roughly +1.3% on the centre.

**Too HIGH — missing or unquantified items:**
- **Auditor-qualified items:** 370.5 at the subsidiaries plus 330.77 at the associates. They are left out of the base, and their sensitivity was never rerun under the rev3 model. A full write-down of the subsidiary items alone is roughly −11% of the centre.
- **Equitization settlement:** still not approved by the state after about 10 years. It could require payments to the state, and the report gives it no number or sensitivity at all.
- **Scenario weights:** 25/50/25 has no basis, and the report's own grid swings the centre from 19,422 to 35,390.

**Other attacks:**
- Data sources, comps and flip-flop all pass. The rev2 → rev3 move is driven by new filed evidence, and downward fixes (revenue down to 4,150, welfare fund) were applied alongside upward ones.
- I compared against rev2 through `REPORT.md`, not the price-zone ledger, which the brief forbids opening.
- I ignored the market price inside the report (33,300 and the 1.155× ratio).

<<<VERDICT_JSON>>>
{
  "case_topic": "LLM (Lilama, UPCoM) — DD rev3 2026-11-23, centre 28.834 đ/cp",
  "verdict": "REFUTED",
  "confidence": "medium",
  "mode": "DD_GENERAL",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; report makes no fear-buy/§2.5 claim",
    "scandal_migration_risk": "pass (with WARNING) — legal/regulatory items (qualified audit 2023–25, CPH settlement unapproved, HNX warning, 69-1 lawsuits/BIDV debt auction) are disclosed; no evidence of asset seizure at parent level found in cited filings; parent guarantee to 69-1 unverifiable (sensitivity 23.224–27.431 given)",
    "optimistic_comp_sotp_bias": "fail (direction UP, i.e. centre too LOW) — base NOPAT uses GPM median 4,5% which historically is AFTER warranty accrual (selling expense = 0 in FY2024/FY2025 [KT25 p12], reversals booked to other income 174,3/19,6), then deducts warranty again (flow_pct_rev×R×cash_share) and never adds back the 75% non-cash portion the report itself assumes. Recomputed via calc_rev3 functions: removing double-count only +1,4%; with non-cash add-back at accrual 1%/2%/3% of revenue: 30.919 (+7,2%) / 32.615 (+13,1%) / 34.310 (+19,0%). FY2025 implied accrual ≥544,5 bn (≈10% revenue). Separately scenario weights 25/50/25 unanchored (grid 19.422–35.390)",
    "data_provenance": "pass with one error — FY2025 P&L, equity roll, share count, NCI traced and match; welfare rate 12,8% is from 2024 distribution and the 'TM36: not yet appropriated' claim is stale: Q3/26 BS shows 2025 distribution done (retained lũy kế 618,3→345,1; ĐTPT 125,0→367,3) leaving ≤30,9 (≤6,3% of 492) for KTPL/BĐH/dividend ⇒ welfare deduction overstated, ~+1,3% on centre",
    "liquidity_capacity_realism": "na — sizing only stated as ≤2% NAV conditional; ADV ~0,45 bn/day disclosed with 11–22 session exit estimate (ước lượng); no fill claim made",
    "confirmation_bias_flipflop": "pass — rev2 24.599 → rev3 28.834 (+17,2%) driven by documented new evidence (9T/26 warranty roll-forward, Hamon note, KT25 notes read in full) and offset by evidence-based downward changes (revenue 4.500→4.150 TTM, welfare fund); compared via REPORT.md rev2 since brief forbids opening dd_price_zones.json",
    "exit_discipline_gap": "na — no position proposed at current level; two-sided change triggers listed in §9",
    "missing_items": "fail — (1) internal warranty double-count in NOPAT (quantified +7–19% at 1–3% accrual, see comp check); (2) auditor-qualified items (subs 370,5 + associates 330,77) not re-run under rev3 framework, full write-down of subs ≈ −11% on centre, associates further; only rev2-framework numbers cited; (3) CPH settlement (unapproved ~10 years, SOE 97,9% state) — possible remittance to state budget/adjustment of state capital: unquantified, no sensitivity; (4) land lease terms (TM26) not checked for expiry. Pass: share basis 79,726104m @30/09/26 code 411 + 31,7% stock dividend handled; capital raise sensitivity; audit opinion FY2025 present; one-offs 9T/26 excluded; related-party/guarantee absence searched (TM26/TM39)"
  },
  "independent_verification": "Re-ran calc_rev3.py (md5 f64e26de... matches): NFP 1.466,16, base 35.760, centre 28.834 reproduced. Read KT25 p12 image: revenue 5.432,6 / GP 380,3 (7,0%), FY2024 6.101,3 / 106,0 (1,74%), selling expense 0 both years, G&A 32,8/56,0, parent NPAT 492,0/92,7 — all match report. KT25 p44: 2024 distribution KTPL 11,352 + BĐH 0,546 on 92,695 = 12,8% (matches) plus 3,5% cash dividend 27,9. Q3/26 BS: retained 01/01 618,28 = KT25 closing (match); parent equity 2.167,7. Recomputed warranty-consistency fix with model functions (table above).",
  "killer_objection": "Base NOPAT counts warranty twice: historical GPM 4,5% is already net of warranty accruals (pre-TT99 accruals sat in COGS; reversals went to excluded other income), yet the model subtracts a separate warranty cash flow and gives no credit for the 75% non-cash share it assumes — at any accrual rate ≥1% of revenue the centre is >5% too low.",
  "recommended_followups": [
    "Recompute base/good NOPAT on a warranty-neutral margin: GPM ex-warranty-accrual minus cash_share × accrual (or keep GPM and drop flow_pct_rev + add back (1−c)×accrual); measure historical accrual/revenue from annual roll-forwards (FY2017–2025 audited notes) instead of assuming",
    "Replace welfare rate 12,8% with the 2025 actual appropriation from the 2026 AGM resolution / Q3 TM25 equity movement",
    "Rerun auditor-qualified-items sensitivity (subs 370,5; associates 330,77) inside the rev3 framework and report alongside the centre",
    "Quantify or bracket CPH settlement exposure (search MOC/MOF decisions, state-capital remittance obligations since 2016 conversion)",
    "Check TM26 land lease terms for expiry within horizon"
  ],
  "summary": "The arithmetic and sourcing of LLM rev3 largely hold up: I reproduced the model exactly and the FY2025 audited P&L, 2024 profit distribution, retained-earnings bridge and share count all match the filings. The verdict is still refuted on a two-sided basis. The decisive flaw pushes the centre too LOW: historical gross margins (the 4,5% base) are already after warranty accruals because before TT99 warranty sat in cost of goods sold (selling expense was zero in 2024 and 2025), yet the model deducts warranty again and ignores the non-cash share it itself assumes; fixing this adds about 7% at a 1%-of-revenue accrual and more at higher rates (FY2025 implies ~10%). The welfare-fund rate is also stale (2025 actual ≤6,3% vs 12,8% used, ~+1%). Pushing the other way, auditor-qualified subsidiary and associate balances (~700 bn) and the unapproved equitization settlement remain outside the base with no rev3 sensitivity, the former worth roughly −11% or more, and the 25/50/25 weights are unanchored. Market prices quoted in the report were ignored."
}
<<<END_VERDICT>>>