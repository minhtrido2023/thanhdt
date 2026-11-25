**Verdict: REFUTED (medium confidence).** The HHS rev9 centre of 13,969 VND per share rests on two choices that contradict the fleet's own documents. Each one moves the centre by more than 5%.

**What I re-checked:**
- **EX value (after the rights issue):** recomputed by hand to 11,615 ✓. The cum/ex relationship also holds: 1.712 × 11,615 − 6,000 × (1 − 1.41%) ≈ 13,969 ✓.
- **BigQuery `ticker_financial`:** OShares 431,985,968 ✓, and 2025Q2 net profit of 3,507.1 bn matches the excluded one-off ✓.
- **Not checked:** CRV is not in BigQuery, so the 52% gross margin could not be verified. I did not re-run `calc_rev9.py` because it writes an output file and this role is read-only.

**Two contradictions that could flip the verdict:**

1. **The holding discount base of 0% is presented as a measured centre, but the user's decision file says it is not.**
   - `kb/projects/ck-hhs-reference-range-20261124.md:13` describes 0% as "NOT a measured centre; a discount of 0 is an upper bound favourable to HHS".
   - `assumptions_rev9.json` justifies it as "median −3.24% ≈ 0".
   - The base therefore sits at the favourable edge of the band. The current-month reading of 19.7% gives a centre 16.8% lower, and rev9 gives no independent evidence for preferring 0 over it.
   - The other direction also needs a basis: using the −3.24% premium as-is would raise the centre by about 3%.
2. **The 52% margin conflicts with the fleet's own competitive-moat review.**
   - The base uses an after-tax surplus of 0.7016, which equals a 52% gross margin on the NC-II project.
   - `ADDENDUM_5F_r1.md` §2–3 classifies exactly that margin as the WIDE-moat case. It concludes the moat is not durable, so under rule 3c the margin should revert to the sector average (peer average 37.7%; direct Hai Phong competitor TCH 29.9%).
   - rev9 says the moat is NONE and that the D4 rule does not apply, but only discusses terminal value and RONIC, not the margin.
   - The effect: +1,083 VND per share according to REPORT_r3, or by my estimate about −1,632 VND (−11.7%) at the peer average and about −16% at TCH's level.
   - There is a real counter-argument: 52% was observed on the very project being valued, on land bought at historical cost. But no document reconciles it with rule 3c, and the Q3 margin was not reviewed (the reviewed H1 figures cut parent-company profit by 34%).

**Missing items (attack 8):**
- The mandatory social-housing obligation and the city inspectorate conclusion KL 08/KL-TTTP have no figure, and neither does the remaining NC-II completion cost (which only pushes the centre down).
- The source files for the core assumptions (`assumptions_r3.json`/`SUMMARY.json`) are lost; those values now survive only as constants in the code.
- NĐL's book value is unaudited.
- The board resolution NQ 10 has not been published, so the dilution could change.
- The remaining I.14 funding gap of 1,803 bn could mean further dilution.

The report quotes market prices; I ignored them when judging the model.

<<<VERDICT_JSON>>>
{
  "case_topic": "HHS — DD rev9 (recheck round 3, 25/11/2026): CUM centre 13,969 VND/share, EX 11,615, holding discount base 0%",
  "mode": "DD_GENERAL",
  "verdict": "REFUTED",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; the report makes no fear-buy/§2.5 claim",
    "scandal_migration_risk": "pass — the legal items in the report (KL 08/KL-TTTP NƠXH Pruksa, TB 2124 7.87 bn, the 852 bn deposit-contract transfers TCH↔CRV/NĐL, NQ 10 content not yet published) are all listed as WARNING in §5; I found no sign in the documents I read of a move to legal-entity level/core assets. The NƠXH price-adjustment risk under KL 08 remains unquantified (see missing_items)",
    "optimistic_comp_sotp_bias": "fail — (1) Holding discount base 0%: ck-hhs-reference-range-20261124.md:13 says 0% is 'NOT a measured centre; discount = 0 is an upper bound favourable to HHS', while assumptions_rev9 justifies it as 'median −3.24% ≈ 0'; the base is placed at the favourable edge of the band with no independent basis preferring it over the current-month reading of 19.7% (−16.8% to the centre). (2) The old-inventory surplus s_obs 0.7016 (NC-II gross margin 52.05%) is exactly the WIDE mapping in ADDENDUM_5F_r1 §3 (E[s] 70.6%); the same document concludes moat_durable=false ⇒ rule 3c: margin reverts to the sector average 37.7% (TCH 29.9%). rev9 §4 only discusses D4/terminal value and does not reconcile the margin. Effect: +1,083 VND/share per REPORT_r3:22, or about −1,632 VND (−11.7%) by my estimate if s is brought to the peer average",
    "data_provenance": "fail (partial) — assumptions_rev9.sources states that the original assumptions_r3.json/SUMMARY.json are LOST from disk; the core inputs (G_OBS 51.9–52.2%, BLK 6,009.8, CPBH 10%, scenario weights) now survive only as constants in hhs_r3.py. The CRV margin cannot be checked in BQ (CRV not in ticker_financial); the Q3/2026 margin is unreviewed (H1 review cut parent NPAT −34%, REPORT.md:25). NĐL book value 11,210 is unaudited. What matched: OShares and NP 2025Q2 against BQ; the EX formula",
    "liquidity_capacity_realism": "na — the report makes no sizing claim (EXCLUDE; V8 does not apply); only the 1.41% liquidity discount for 5 bn is inherited",
    "confirmation_bias_flipflop": "pass with caveat — the history in the report itself: v1 11,900 → r2 10,387 → 5F 8,393–9,700 → r3/rev6 13,969 → rev7 10,805 → rev9 13,969; the r3 report itself says the swings come 'from conventions, not new data'. The rev9 change comes from a new measurement (v5 N=12, median moving from +26.63% to −3.24% within a day), which is new information, but the parameter itself is unstable (N 13→12 flipped the median 1.5→−3.2). The 7 attack is not one of 'wanting a YES' (EXCLUDE is kept), but the centre returning exactly to the rev6 headline needs to be noted",
    "exit_discipline_gap": "na — no sizing/entry claim (forensic EXCLUDE)",
    "missing_items": "fail — (a) mandatory social-housing obligation / NƠXH price adjustment under KL 08/KL-TTTP: report D3 says 'needs verification, no figure yet' — potentially material, unquantifiable ⇒ INCONCLUSIVE on its own; (b) remaining NC-II completion cost (G10) base 0, which REPORT_r3:75 itself calls a 'one-sided downside risk not yet quantified'; (c) the I.14 shortfall of 1,803.2 bn has no funding structure — if raised as equity, a further dilution not in the EX case; (d) NQ 10 content (shareholder written consultation 14–25/12) could change the dilution; (e) mix HH1–HH4: the report's own scenario probabilities (0.30/0.15/0.05) give an expected value of ≈ −1.35% of centre (my calc), below the 5% threshold. Passed: share-count basis (431.99M shares at 30/09/2026, BCTC Q3 TM1.1 = BQ), welfare fund (6.46 bn, already a liability), audit FY2025 AASC unqualified, one-off 3,507 bn excluded from V_short, minority interest 48.85% excluded, deferred tax on PPA (STEP_AT ×0.8)",
    "symmetry": "{too_high_checked: 8, too_low_checked: 9, too_low_items: ['v5 median −3.24% is a PREMIUM, rounding to 0 drops about +2.8% (has a basis)', 'Ke low end 12.3%: +2.05% (quantified, not in base — appropriate)', 'k_sensitivity 1.0205/1.025: EX +≈0.7%, small', 'audited PPA covers HH1–HH4 above the model ⇒ s_hh +0.16 scenario upside not in base', 'BĐSĐT at 100% of book (could be above book)', 'consolidated inventory 17,961 bn (BQ 2026Q3) vs BLK 6,009.8 + I.14 1,329: the remainder is valued at book/backlog m — possible surplus left out, could not verify without the inventory note', 'I.14 NPV0 symmetric ±15% (no upside credited — consistent with 3c)', 'backlog m 33.5% net vs observed project margin of 52% gross — not too strict', 'the cost discount (1−pv(y)) on BLK is correct for time value, not an excess haircut'] — 9 ≥ 8; the only too-low item with a measurable basis is −3.24% (+~3%), which does not offset the two too-high contradictions"
  },
  "independent_verification": "(1) Recomputed EX by hand: (13,969×431.986M + (1−0.014097)×2,591.9 bn)/691.18M/1.07 = 11,615 ✓; cum/ex identity 1.712×11,615 − 6,000×0.9859 = 13,969 ✓. (2) BQ ticker_financial HHS: OShares 431,985,968 ✓; NP 2025Q2 3,507.1 bn ✓ (one-off); consolidated 2026Q3 GPM 11.95% on revenue 1,903.8 bn (post-PPA, consistent with the model working on the ex-PPA basis). (3) Recomputed the sensitivity to s: BLK 6,009.8×Δs 0.346×pv(3.25@13.5%) 0.663×0.5115/431.99M ≈ −1,632 VND/share (−11.7%). (4) Recomputed the expected HH1–HH4 effect from the report's own probabilities ≈ −1.35%. Not re-run: calc_rev9.py (writes calc_rev9_out.json — this role is read-only); calc_rev9_out.json has an mtime of 12:30, later than run1/run2 at 10:40, but its contents match the report. The 52% CRV margin could not be verified (CRV not in BQ)",
  "killer_objection": "The two parameters that drive the centre are both set at the favourable end and contradict the fleet's own documents: holding discount 0% is stated by the user's decision file to be 'NOT a measured centre, a favourable upper bound' (vs the current reading of 19.7% ⇒ −16.8%), and the 52% margin is the WIDE-moat mapping while the report itself assigns moat NONE and rule 3c requires reverting to the sector average (−8…−12%). Neither has been reconciled",
  "recommended_followups": [
    "Pick the holding-discount base with an explicit basis and say why it is preferred over the current reading of 19.7%, or report the centre as a range 11,593–13,969 rather than a single point",
    "Reconcile s_obs 0.7016 with ADDENDUM_5F_r1 rule 3c: either argue explicitly that 'an existing land bank at historical cost ≠ a moat' (with evidence of the remaining NC-II product mix), or bring s to the peer average 37.7% / TCH 29.9% and report the gap",
    "Quantify the social-housing obligation + NƠXH price adjustment under KL 08 and the NC-II completion cost (G10) from the BCTC notes/project documents",
    "Rebuild the core assumptions file (assumptions_r3.json) from the hhs_r3.py constants with per-line sources, because the original file is lost",
    "Verify the NC-II gross margin of 52% against CRV's own reviewed/audited BCTC (not available in BQ)",
    "Rebuild the dilution case once NQ 10 is published and the I.14 shortfall funding structure (1,803 bn) is known"
  ],
  "summary": "The rev9 calculation is internally consistent: I recomputed the EX value and the cum/ex identity by hand, and the share count and the 3,507 bn one-off match BigQuery. The r sensitivity is low and explained correctly. But the centre of 13,969 depends on two choices at the favourable end that contradict the fleet's own documents. First, the 0% holding discount is presented as '≈ the v5 median', while the user's decision file calls 0% 'not a measured centre, a favourable upper bound'. The current reading of 19.7% gives a centre 16.8% lower, and nothing explains the preference. Second, the 52% margin on old inventory is the WIDE-moat case in the 5F review, while the report itself assigns moat NONE and rule 3c requires reverting to the sector average (about −8…−12%). Also missing: the social-housing obligation, the NC-II completion cost, the lost r3 source files, and a possible further dilution from the I.14 shortfall. Upward-side checks were run in equal or greater number; only the −3.24% premium (+~3%) has a real basis, and it does not offset the two contradictions. The report quotes market prices; I ignored them when judging the model."
}
<<<END_VERDICT>>>