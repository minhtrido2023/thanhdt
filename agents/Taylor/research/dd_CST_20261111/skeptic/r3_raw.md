**Verdict: REFUTED (medium confidence).** The single point that moves rev 3 most is the +1.459 đ/cp for paying out the 130,66 bn VND of retained profit, and its key premise contradicts the audited 2025 accounts.

**What I checked against the source**
- **Equity note 17 (KT25 tr.30, image p33) matches the report.** LNST 2024 130,02; 2025 82,749. The 2025 distribution was 164,155 bn: development fund 39,006 (23,76%), bonus-and-welfare fund 81,988 (49,95%), managers' bonus 0,315, dividend 42,847 (26,10%). Retained profit at year-end was 213,41, so the undistributed remainder is 213,41 − 82,75 = 130,66. These match.
- **Share count is 42.846.773.** The dividend of 1.000 đ/cp equals 42,847 bn, consistent with charter capital of 428,47 bn.
- **The model arithmetic reproduces.** Base case: 0,045×951,16 + 21,79×6,739 = 189,7 bn, about 4.429 đ/cp. Payout value: 0,4785 × 3.049 = 1.459. Weighted centre: 0,3×3.622 + 0,45×5.887 + 0,25×9.143 = 6.022.

**Why the centre could be too high**
1. **The "fund already deducted" claim (§2b) fails on the note-17 arithmetic.** The 2025 fund percentages were applied to the 164,155 bn tranche, not to the full 294,82 bn pool. The 130,66 bn is what was left untouched, not a post-fund residual. That tranche also included about 34,1 bn of older accumulated profit, and half of it (49,95%) went to the bonus-and-welfare fund. So the precedent is that accumulated profit gets split by the same percentages when it is distributed.
   - If ~50% goes to the fund, the payout is worth about +730 instead of +1.459. That is −729 đ/cp, or −12% of the centre: quantifiable and material.
   - The only support for "dividend only, no fund" is a press article from 04/2025. The 2026 AGM then did not pay the money as promised. The extraordinary AGM (20–30/12) has not voted, and the rate is unpublished.
2. **The rev 2 → rev 3 jump (+32%) is not driven by new information.** The audited accounts, board resolution 40 and the 04/2025 article were all available to rev 2, which itself wrote "payout rate and fund share not yet published". Rev 3 moved the item into the base without any new primary document.
3. **The pessimistic case may be too kind.** The fund deduction is modelled as proportional to profit. If the fund actually behaves like a near-fixed amount tied to wages (2022: 55,9 bn on profit of 106,6), the bear case could fall to about zero. That is about −350 đ/cp after weighting (my estimate).

**Why the centre could be too low**
4. **TKV restructuring is only a warning, with no scenario.** The restructuring plan is due 27/11/2026. Book value is about 22.400–24.000 đ/cp, while the model values the 951 bn of book equity at a coefficient of 0,045, i.e. about 1.000 đ/cp. Any state divestment, merger or share swap priced against valuation or book would land far above the centre. The probability can't be quantified, but the effect is material.
5. **The 8% borrowing cost on the payout may be too harsh.** It is charged for 19 years even though the report says TKV's cost-plus price may cover financing costs. If the cost is passed through or the cash is idle, the payout is worth +1.951 to about +2.770, which is +8% to +22% on the centre.

**Smaller points**
- §2 still shows rev 2 sensitivities (7.787 / 4.389 / 1.243) next to the rev 3 figures in §8d (9.246 / 5.848 / 2.702); each pair differs by exactly 1.459. This is an internal inconsistency.
- The Khe Chàm II site (42,31 bn environmental deposit) has no licence term or closure plan in the report.
- The 1.020 bn of remaining expansion spend is an estimate, and the 2026 fund figure of 52,76 is a balance-sheet residual rather than a disclosed amount.

I did not look up any market price. The 14.100 price in the report's own text was ignored when judging the model.

<<<VERDICT_JSON>>>
{
  "case_topic": "CST (Than Cao Sơn – TKV) DD REPORT_rev3 — centre 6.022 / 5.837 đ/cp",
  "mode": "DD_GENERAL",
  "verdict": "REFUTED",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; report makes no fear-buy/§2.5 claim",
    "scandal_migration_risk": "pass (with gap) — no lawsuit/penalty in the sources read; but the TKV restructuring plan (due 27/11/2026) is only a WARNING with no scenario, even though a divestment/swap could move value toward book (~22.4–24k đ/cp)",
    "optimistic_comp_sotp_bias": "pass — no comps; finite residual-income model reproduces (base 4.429+1.459=5.887; centre 6.022). The 8%/yr borrowing haircut on the payout (19 years) is an estimate tilted toward cheap",
    "data_provenance": "fail — the load-bearing claim 'the 130,66 bn already had funds deducted in 2025, no further bonus-and-welfare deduction' contradicts equity note 17 (KT25 tr.30): the percentages 23,76/49,95/0,19/26,10% were applied to the 164,155 tranche (which included ~34,1 bn of older accumulated profit, ~50% of it to the fund); the 130,66 is the untouched remainder. The only support is a 04/2025 press article. The 2026 fund figure of 52,76 is a residual, not disclosed",
    "liquidity_capacity_realism": "na — no position sizing proposed (§9 'không đề xuất vị thế')",
    "confirmation_bias_flipflop": "fail — rev2→rev3 +32% (4.563→6.022) driven by moving the +1.459 from sensitivity into the base; no new primary document (audited accounts, board resolution 40 and the 04/2025 article were all available to rev2, which itself wrote 'tỷ lệ chia và phần KTPL từ khoản này chưa công bố'); the extraordinary AGM has not voted. Ledger kb/dd_price_zones.json not opened per the brief's blind constraint — compared via REPORT.md/REPORT_rev2.md",
    "exit_discipline_gap": "na — no sizing/entry claim; §10 does give two-sided re-lock triggers",
    "missing_items": "fail — (1) bonus-and-welfare fund deduction on the 130,66 bn payout: quantifiable, −729 đ/cp (−12% of centre) if 49,95% applies; (2) TKV restructuring/divestment/swap scenario: material, unquantifiable, upside direction; (3) Khe Chàm II licence term/rehab plan (42,31 bn deposit) absent; (4) remaining expansion capex still an estimate (~1.020 bn), shown as display only; (5) TKV fund-allocation rules/ND 167 not read in primary text. Passed: share count 42.846.773 (dividend 42,847 bn / 1.000 đ), audit opinion unqualified FY2025, mine horizon 08/2045, environmental deposit included as compliance outflow"
  },
  "independent_verification": "Read KT25 note 17 image (img_kt25/p33.png): LN2024 130,020; LN2025 82,749; 2025 distribution 164,155 = 39,006+81,988+0,315+42,847 with stated % 23,76/49,95/0,19/26,10; year-end retained 213,41 ⇒ undistributed 130,66 — all match the report. Recomputed (1,135)^-19=0,0902, annuity 6,739, base value 189,7 bn/42,847M = 4.429 đ, payout factor 0,4785×3.049=1.459, weighted centre 6.022 — match. Same note shows the 2025 distribution included ~34,1 bn of older accumulated profit split by the same percentages, which contradicts the report's 'already deducted' premise.",
  "killer_objection": "The +1.459 in the base assumes the 130,66 bn goes 100% to dividends because it 'already had funds deducted'; the audited equity note shows the opposite precedent (accumulated profit entering a distribution in 2025 was split ~50% to the bonus-and-welfare fund), and the AGM has not voted — at a 49,95% fund rate the centre falls to ~5.290 (−12%). Counterweight: the borrowing haircut and the missing TKV-divestment scenario bias toward cheap.",
  "recommended_followups": [
    "Wait for / obtain the extraordinary AGM resolution (20–30/12/2026) and TKV letter 7788/TKV-KSNB: the exact split of the 130,66 bn between dividend and bonus-and-welfare fund; keep +1.459 as sensitivity until then (or base ~+730 at a 49,95% fund rate)",
    "Read the primary text of ND 167/2024 and TKV's fund-allocation rules (cap on the bonus-and-welfare fund by months of wages vs % of profit) — decides α and the shape of the bear case",
    "Add an explicit TKV-restructuring scenario (divestment/swap priced against valuation/book) as a two-sided sensitivity",
    "Re-justify the 8%/yr × 19-year borrowing cost on the payout given the cost-plus pricing mechanism",
    "Fix the stale rev2 sensitivity numbers in §2 (7.787/4.389/1.243) to rev3 values; add the Khe Chàm II licence term"
  ],
  "summary": "Rev 3's figures trace correctly to the audited 2025 equity note (verified from the page image) and the model arithmetic reproduces exactly (centre 6.022). But the main rev 3 change — adding +1.459 đ/cp for paying out the 130,66 bn of accumulated profit — rests on the premise that this amount 'already had bonus-and-welfare deductions in 2025'. The audited equity note shows the 2025 percentages were applied to the 164,155 bn tranche only. That tranche itself included older accumulated profit, about half of which went to the fund. If the same split applies, the item is worth ~+730, not +1.459 (−12% of centre). The rev2→rev3 upward move is a re-interpretation of information already available, with only press support, before the AGM has voted. In the other direction, the model may undervalue: it charges an estimated 19-year borrowing cost on the payout and has no TKV-restructuring scenario, under which book value (~22–24k đ/cp vs a 0,045 coefficient in the model) could be crystallised. Verdict REFUTED on provenance of a load-bearing, quantifiable item; the true centre band is roughly 5.300–7.600 depending on the payout split and funding, before any restructuring scenario."
}
<<<END_VERDICT>>>