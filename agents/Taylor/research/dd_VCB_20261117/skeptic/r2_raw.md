**Verdict: REFUTED (medium confidence).** The arithmetic holds up. The weak spot is an item the report dismissed without real evidence: profit that leaves equity every year and never reaches shareholders. There is also a lopsided choice of base inputs that pushes the centre up. The report understates the risk of the centre being too high, and it also hides some upside.

**What I re-checked:** I rebuilt the base chain by hand from the locked inputs and it matches.
- Core PPOP: (49.620 − 3.171) × 4/3 = 61.932, divided by average loans 1.744.809, gives **3,549%**.
- Leverage: 1.744.809 / ((253.669 + 224.516) / 2) = **7,298**.
- Normalised credit cost: provisions 2017–25 of 62.659, minus the 20.070 rise in provision balances, gives 42.588 = 0,49%. Adding 0,12% maintenance gives **0,62%**.
- ROE 17,1% → P/B 1,558 → **47.300**.

**Reasons the centre may be too HIGH:**
1. **Profit that never reaches equity (attack 8, quantifiable).** The audited 2025 equity roll-forward doesn't close. 196.113 + net profit 35.178 − cash dividend (2.515–3.760, from BQ `Dividend_1Y` = 450đ) should be about 227.500–228.800. Actual equity is 224.487, so **3.000–4.300 bn (9–12% of profit) is missing**. That is consistent with the bonus/welfare fund appropriation state-owned banks book at year-end.
   - The 9M/26 gap is only about 120 bn. That fits an appropriation not yet booked, so the 9-month check the report relied on for item 11 looks at the wrong window.
   - If the drain recurs, shareholder ROE falls to 15,0–15,6% and the base to **37.600–40.400 (−15% to −21%)**.
   - I could not confirm what the gap is made of. The audited PDF is a scanned image and the statement of changes in equity (B05) was not read.
2. **Lopsided base inputs.** The base takes its margin from the current period (9M/26, 3,55%) but its credit cost from long history (0,62%). That 0,62% is below every 2026 reading: 9M annualised is 0,70%, and Q3 annualised is about 1,37% (6.184 × 4 / ~1,8 trillion).
   - Using 9M/26 for both inputs gives 45.000 (−5%).
   - Using the Q3 run-rate for both gives about 35.500 (−25%).
3. **NII/loans jumped 3,76% → 4,37%** while banks were under orders to cut lending rates. The report never explains the driver, yet that margin is what lifts the centre +15,7%.

**Reasons the centre may be too LOW:**
- The Q3 PPOP run-rate is about 3,87%, above the base 3,55%.
- g = 7% has no source and implies a 59% payout. VCB's real cash payout is about 11% (3.760 / 35.178). The two-stage model at 51.700 shows the single-stage Gordon formula probably undervalues compounding retained earnings.
- g at 8% gives 50.400. The cash-dividend deduction was correctly removed in rev2.

**Other attacks:**
- **Flip-flop:** mostly justified. The credit-cost series is genuinely new, audited input. The margin change partly re-reads the same 9M/26 data that rev 1 called a "NIM peak".
- **Data sources:** pass, with caveats. CAR is from press only; CET1 and LDR under TT22 are absent and flagged.
- **Price-blind:** the report contains the price 52.100. I ignored it.

<<<VERDICT_JSON>>>
{
  "case_topic": "VCB — DD rev2 (BCTC Q3/2026), P/B-ROE valuation, weighted centre 44.900 / band 38.900–53.100",
  "mode": "DD_GENERAL",
  "verdict": "REFUTED",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; the report makes no fear-buy/§2.5 claim",
    "scandal_migration_risk": "pass — the WARNING items (KTNN restatement +29bn equity, branch inspections, VCBNeo unverified) are listed; no asset seizure, licence or contract event; VCBNeo is quantified only as an illustrative sensitivity, which is the honest treatment",
    "optimistic_comp_sotp_bias": "fail (asymmetric input selection) — base margin taken from the current period (9M/26 core 3,55%) but base CC from long history (0,62%), which is below every 2026 reading (9M annualised 0,70%; Q3 annualised ≈1,37% = 6.184×4/≈1,8tn). Consistent 9M pair ⇒ ≈45.000 (−5%); consistent Q3 pair (margin ≈3,87%, CC ≈1,37%) ⇒ ≈35.500 (−25%). The NII/loans jump 3,76%→4,37% during a lending-rate-cut directive is unexplained. Opposite direction: g=7% has no source and implies 59% payout vs actual cash payout ≈11%; the two-stage model gives 51.700, so single-stage Gordon may undervalue retention",
    "data_provenance": "pass with caveats — base chain traced to the locked JSON and recomputed by hand; historical series read from scans (not re-read by me, PDFs have no text layer); CAR 11,14% press only; CET1/LDR TT22 absent and flagged; g=7% has no source (±6% effect from g 6/8%)",
    "liquidity_capacity_realism": "na — no sizing claim beyond the 2–4% NAV frame; ADV 175bn/day makes capacity non-binding",
    "confirmation_bias_flipflop": "pass with caveat — only VCB's own rev1/rev2 compared (ledger not opened); 38.800→44.900 driven mainly by a genuinely new audited 9-year CC series; but switching the margin from 'midpoint' to '9M core, not peak' re-reads the same 9M/26 data rev1 called a NIM peak",
    "exit_discipline_gap": "na — not a fear-buy; two-sided conditions for changing the view are listed in §9",
    "missing_items": "fail — (1) bonus/welfare fund and other non-equity profit draws: audited 2025 equity roll 196.113 + NP 35.178 − cash dividend 2.515…3.760 (BQ Dividend_1Y 450đ) vs actual 224.487 ⇒ 3.000–4.300bn/yr (9–12% of NP) leaves equity; rev2 item 11 dismissed it using a 9M window (9M/26 gap ≈120bn, consistent with a year-end appropriation not yet booked). If recurring, shareholder ROE 15,0–15,6% ⇒ base 37.600–40.400 (−15…−21%), material >5%; composition (B05) not read. (2) CET1, LDR TT22, Pillar 3 absent — flagged, sensitivity −12%. (3) VCBNeo unquantified — flagged, −2…−8%. (4) Possible VAMC/special-bond provisions inside the 2017–19 credit-provision line could distort the 0,49% loss rate either way — not checked. Pass: audit opinion (EY 2025 unqualified), latest audited FY present, one-off 3.171 removed, share count 8.355,7m at 30/09 with pending bonus/placement noted, NPL/group 2/coverage present"
  },
  "independent_verification": "Recomputed by hand from the locked JSON: core PPOP (49.619,9−3.171,3)×4/3=61.931,5; avg loans 1.744.809 ⇒ margin 3,549% ✓; lev 1.744.809/239.092=7,298 ✓; CC loss rate (62.658,7−20.070,4)/Σavg loans ⇒ 0,49% + maintenance 1,49%×0,09/1,09=0,12% ⇒ 0,62% ✓; ROE 17,1% ⇒ P/B 1,558 ⇒ 47.300 ✓. Independent check: 2025 audited equity roll-forward does NOT reconcile — 3,0–4,3k bn unexplained after the BQ-verified 450đ cash dividend",
  "killer_objection": "The model treats 100% of net profit as accruing to shareholders' book value, yet the audited 2025 equity roll-forward shows ≈9–12% of profit leaving equity (most likely the bonus/welfare fund). Rev2 dismissed this using a 9-month window where the appropriation has not yet been booked; if recurring, the base falls 15–21% to ≈37.600–40.400, below the 9M-consistent pair, and the band's top half is unsupported",
  "recommended_followups": [
    "Read B05 / the equity note of the audited 2025 and 2024 statements (OCR the scans): split the 2025 equity gap into bonus/welfare fund, FX translation and other; model the recurring part as a haircut to ROE",
    "Use one consistent period for margin and credit cost in the base, or justify why the 2026 margin persists while the 2026 credit cost reverts to history; explain the NII/loans jump 3,76%→4,37% (deposit mix/KBNN, interest recoveries, repricing)",
    "Separate Q3/2026 provisions (6.184bn) into coverage build vs realised loss, including the 2.997bn TPDN part",
    "Give g a source tied to retention × ROE under the CAR constraint, or switch the base to the two-stage model already computed",
    "Check whether 2017–19 credit-provision expense includes VAMC special-bond provisions and whether the provision balances used in the loss-rate calculation match"
  ],
  "summary": "Rev2's arithmetic reproduces exactly and its new 9-year audited credit-cost series is a genuine improvement over rev1's unsourced 0,8%. But the base still has two problems. First, a missing non-equity claim: the audited 2025 equity roll-forward loses ≈3–4,3k bn (9–12% of profit) after the BQ-verified cash dividend, most plausibly the bonus/welfare fund, which rev2 dismissed using the wrong (9-month) window; if recurring, the base falls 15–21%. Second, asymmetric input selection: the margin comes from 2026 while credit cost comes from long history and is below every 2026 reading, including a Q3 run-rate near 1,37%. In the other direction, the unsourced g=7% and the implied 59% payout conflict with VCB's ≈11% cash payout, and the two-stage model (51.700) suggests some upside is understated. The welfare-fund item is quantifiable and material, so the verdict is REFUTED until B05 is read and the base inputs are made consistent."
}
<<<END_VERDICT>>>