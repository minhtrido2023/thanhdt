**Verdict: INCONCLUSIVE (medium confidence).** The model's arithmetic holds up: I recomputed net cash and the centre from the source numbers and both match exactly. But the mine life of about 14 years, which carries the valuation, rests only on press reserve figures and an inferred extraction rate. No licence register, approval decision or FY2025 audited report was read. The report admits this itself.

I ignored the market prices and peer P/Es written into the report, as the blind rule requires. Per the brief I also did not open `kb/dd_price_zones.json`, so the flip-flop check compares only against this folder's own r1 draft.

**What I checked independently**
- Net cash: 812.584 − 107.466 − 61.748 − 51.54 − 67.06 − 35.93 = **488.84 bn VND**, an exact match. The pre-discount centre of **52,732** also reproduces from `model/dcf_vlb.py`.
- Stone conversion: 9-month revenue 1,233.9 bn ÷ about 222,000 VND/m³ ≈ 5.56m m³ sold. Against 9.95m tonnes from the environmental fee, that gives 1.79 t/m³, which is the density of crushed stone. So the fee is charged on product sold, and the 2.6 t/m³ conversion to in-place rock is plausible. The extraction-rate method is internally consistent; the reserve figure behind it is what's unverified.

**Too HIGH (centre may be overstated)**
- The base case uses 330 bn operating profit, flat plus 2% a year for 14 years. That is above the report's own normalised figure (median 301 bn) and its ~290 bn for 2025. Using 290 bn moves the centre −4.7%; g = 0 moves it −3.4%. Profit is at a peak about 2.7× the 2017–2023 median.
- The good case assumes higher volume and a longer life (16 years) at the same time. With fixed reserves, more volume shortens life. Capping it at 14 years: −1.5%.
- At the Q3 run-rate, life is about 13 years, not 14: −1.3%.
- The base case counts all of Tân Cang 1 (about 28% of reserves), part of whose area expired in 2/2025.

**Too LOW (centre may be understated)**
- The 329 bn offset is a claim on the state but is discounted at the 13.5% equity rate. At 7% its value rises from 119.4 to 169.8 bn, about +1.5% on the centre.
- The ~57 bn left over at end of mine life is counted at zero.
- Environmental deposits exceed the restoration provision by 22.7 bn (about +485 VND/share), not counted.
- The 12.4% fund-deduction alternative gives +2.2%.

The upward and downward adjustments roughly cancel. None is above 5% on its own. There is no one-sided bias.

**Attack 8 (missing items)**
- Not read: the FY2025 audited report and its opinion. This matters because the licence-fee calculation already reversed once (topped up in 2022, then found overpaid in 2026).
- No licence table: licence numbers, expiry dates, capacity and mining floor depth for each mine are absent.
- No approval decisions for the licence fee, so the remaining obligation, or a new one if reserves are re-approved, is unknown.
- Committed capex or land compensation needed to reach the remaining reserves is not checked. The 2026 AGM resolution was read, but only for dividends.
- Passed: share count (46.72m, Q3 p22), welfare/bonus fund (14.84%), related parties (no sales, p23), no borrowing, 20.5 bn of deposits pledged.

All the gaps are material but cannot be put into numbers, so the rule gives INCONCLUSIVE.

**Changes since r1:** the centre fell from 61,798 to 51,163. Each step traces to a scanned page (fund deduction, offset rate, receivables, mine life), so new evidence drove the change, not reinterpretation. Attacks 1, 5 and 7 are `na` in this mode.

<<<VERDICT_JSON>>>
{
  "case_topic": "VLB: DD investor report 22/11/2026 (r2), finite-mine-life DCF + licence-fee offset right + real net cash",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "mode": "DD_GENERAL",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; the report makes no fear-buy/§2.5 claim (r2 §9 says explicitly it is not fear-state)",
    "scandal_migration_risk": "pass — the report lists the WARNING items it knows of: the Government Inspectorate's review of the Soklu licences, State Audit recommendations on land, and the 2022→2026 licence-fee reversal. No asset seizure or licence revocation appears in the cited material. The Soklu review only touches mines the report already treats as probably idle. Caveat: all of this is from the press; no original documents were read",
    "optimistic_comp_sotp_bias": "pass — peers are shown for comparison only and do not drive the centre. The DCF has no terminal value; new mines are valued at NPV 0. Two internal biases (base profit 330 bn above the report's own normalised 301 / 2025's ~290; good case pairs higher volume with longer life) are offset by understated items (offset discounted at 13.5% instead of ~7%, 22.7 bn excess deposits, the 57 bn end-of-life balance at zero). Each is <5% of centre and they roughly cancel",
    "data_provenance": "fail (partial) — balance sheet, cash-flow and offset figures trace to Q3/H1 statement pages and recompute correctly. But the load-bearing reserves (35.59/22.7/22.65 m m³) come only from stockbiz (press). Licence term per mine and the remaining licence-fee obligation have no source. The audited FY2025 report was not read; LNST 301.44 comes from the AGM resolution. The report labels all of these as estimates/unverified, which is honest but leaves them untraced",
    "liquidity_capacity_realism": "na — no sizing claim in the report beyond a 2.98% liquidity discount (Q = 5 bn), computed mechanically from ADV and a Corwin-Schultz spread",
    "confirmation_bias_flipflop": "pass — r1→r2 in the same folder: centre 61,798 → 51,163. Each step traces to a scanned page (fund deduction Q3 p22 23d; offset sub-line H1 p30/Q3 p19; receivables 2,762,480 VND Q3 p2; mine life made consistent). The change came from evidence, not reinterpretation. Per the brief, kb/dd_price_zones.json was not opened",
    "exit_discipline_gap": "na — DD_GENERAL, no position sizing proposed; two-sided change triggers with dates are present (§10)",
    "missing_items": "fail (unquantifiable) — ABSENT: (1) audited FY2025 report: audit opinion/emphasis on licence fees, notes on licences; (2) licence register: licence numbers, expiry dates, capacity and mining floor for TP1/TT2/TC1, plus the TC1 area inside a valid licence (TC1 ≈28% of reserves; −3 years of life = −8.7% of base value); (3) licence-fee approval decisions: remaining obligation, plus possible new obligations if reserves are re-approved; (4) committed capex/land compensation from board/AGM resolutions needed to reach the remaining reserves (the 2026 AGM resolution was read for dividends only). PASS: share count 46.72m (Q3 p22 23c), welfare fund 14.84% deducted, related parties (no sales, p23 VI.1b), no borrowing, 20.5 bn pledged deposits, restoration provision vs deposits. All absent items are material but cannot be quantified from the available material ⇒ INCONCLUSIVE"
  },
  "independent_verification": "Recomputed net cash from the Q3 balance sheet: 812.584 − 107.466 − 61.748 − 51.54 (76.938 × (1 − 33.0%)) − 67.06 net working capital − 35.93 interim fund accrual (565.97 − 11,345 × 46.7206m) = 488.84 bn — exact match. Re-ran dcf_vlb.py: pre-discount centre 52,732 — exact match. Checked density from the environmental fee: 9.95m tonnes ÷ ~5.56m m³ sold (1,233.9 bn ÷ 221,986 VND/m³) = 1.79 t/m³, consistent with crushed stone ⇒ the extraction rate of ~5.1m m³/yr in-place rock is plausible. Sensitivities: base profit 290 bn −4.7%; g = 0 −3.4%; good-case life 14 −1.5%; base life 13 −1.3%; offset discounted at 7% ≈ +1.5%; excess deposits +485 VND/share",
  "killer_objection": "The ~14-year mine life, which drives about 75% of the centre's value, rests on press reserve figures (stockbiz) and an inferred extraction rate, with no licence register or audited FY2025 report. Part of Tân Cang 1 (≈28% of reserves) has expired and is fully counted in the base case. At the Q3 run-rate the life is ~13 years. If the licences or mining floor depth are tighter than the press says, the centre could fall much further than the ±5% sensitivities shown.",
  "recommended_followups": [
    "Download the audited FY2025 statements (A&C): read the audit opinion, the notes on mining licences and licence fees, and the 2025 interest income to separate core operating profit",
    "Find the licence register for TP1/TT2/TC1 (licence number, expiry date, capacity, mining floor) and confirm what share of TC1's 22.65m m³ sits inside a valid licence",
    "Find the licence-fee approval decisions: the remaining obligation and the rate R, to judge the risk of reversal or new obligations",
    "Check the 2026 AGM resolution and board resolutions for any investment plan or land compensation needed for the remaining reserves",
    "Fix the good case: either cut life to ≤14 years or drop the volume-growth assumption (with fixed reserves, more volume means a shorter life)",
    "Consider discounting the offset at a near-sovereign rate (≈7%) instead of Ke 13.5%, and say whether the leftover balance can be refunded"
  ],
  "summary": "The VLB r2 report is arithmetically correct: net cash of 488.84 bn and the pre-discount centre of 52,732 reproduce exactly from the statements and the model, and the r1→r2 corrections each trace to scanned pages. Two-sided, the base profit of 330 bn sits above the report's own normalised figure, and the good case pairs more volume with a longer life. Against that, the offset is discounted at too high a rate and the excess deposits are not counted. Each of these is under 5% and they roughly cancel, so there is no one-sided bias. The decisive weakness is attack 8 (missing items): mine life and reserves, which carry most of the value, come only from the press. There is no licence register, no licence-fee approval decision and no audited FY2025 report, and part of Tân Cang 1 has expired yet is fully counted in the base case. These gaps are material but cannot be quantified, so the verdict is INCONCLUSIVE rather than CONFIRMED. The market prices in the report were ignored when judging the model."
}
<<<END_VERDICT>>>