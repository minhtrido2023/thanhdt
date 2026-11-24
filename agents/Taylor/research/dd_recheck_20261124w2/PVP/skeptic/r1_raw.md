**Verdict: INCONCLUSIVE (medium confidence).** The math reproduces exactly. Two problems remain. First, the D3 dry-dock sensitivity is one-sided and probably double-counts. Second, a material share-count/financing item is still unchecked.

**What I verified independently**
- I re-ran `calc_recheck.py` against the restored r3 tree. Output md5 is `91f4475b…`, the same as run1/run2. That rerun rewrote `calc_recheck_out.json` with identical content.
- Summing the parts by hand: 1.016,2 + 37,01 + 711,95 + 1.340,45 − 232,9 − 220,7 = 2.652,0 bn ÷ 103,70M shares = **25.573 đ/cp**. This matches `center_param_pre`.
- The D3 annual figure checks: 53,1 × 4/3 = 70,8. The scrap unit checks: (23.685,8 − 23.566,5) × (1 − 1,98%) ≈ **117 đ/cp per $1M**.
- FSO is not double-counted. Fleet EBITDA = transport gross profit 292,9 + depreciation of Era/Pride (`model.py:19`), which excludes FSO.

**Findings**
1. **D3 likely double-counts, so the −7% is too harsh.**
   - The 9T/25 transport gross profit was pre-TT99. The repair accrual was still running through cost of sales then; that is the 53,1 bn LCTT line the report itself uses.
   - So the 2025 base (~380–390) that the 400 "cơ sở" level sits on already contains a dry-dock-like charge.
   - Only the "tốt" branch (550 ≈ the 9T/26 run-rate) truly lacks dry-dock cost. The right adjustment is about 0,275 × (−7%) ≈ **−2%**, not −3,5%/−7% across the whole grid.
   - The report's claim that dry-dock is "not in EBITDA 300/400/550" is only right for 550.
2. **Scrap is asymmetric (too low).**
   - The base sets scrap = 0, which is a downward haircut with no independent evidence.
   - Each tanker's scrap value is certainly positive. At 117 đ per $1M, even a few $M per vessel offsets the D3 effect.
   - The recheck quantified only the downside (dry-dock) and left scrap unquantified.
3. **Missing item, unquantifiable but material: the ship purchase and financing.**
   - Press dated 12/09/2026 says an extraordinary AGM was set for **23/10/2026** (record date 28/9). The agenda was the investment policy and feasibility study for "**tàu dầu thô Aframax số 3**". Price, age, funding source and any share issuance were not disclosed.
   - The report has not checked again since 05/11. It is unclear whether "ship #3" is one of the two ships in the model (56,5 + 59,5) or a new one.
   - An equity issuance below intrinsic value would dilute `SH = 103.702.452`.
4. **Provenance gap.** HTM 1.015,9 bn was read from a scanned image and the 3 source PDFs are not in git, so it cannot be re-read. Net cash (1.016 bn) is about 40% of SOTP value.
5. **Minor.**
   - The 13,5% base r sits above the upper end of the Ke band (13,4%); the effect is +40 đ.
   - The 10-year corporate-cost deduction against a 4–8 year fleet life tilts the centre down.
   - The 2026 welfare/bonus fund is not deducted (small).

The market price quoted in the report (18.000) and in the search result was ignored.

<<<VERDICT_JSON>>>
{
  "case_topic": "PVP — recheck REPORT_r3 theo B5/E15/E16 (24/11/2026, dd_recheck_20261124w2)",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; report makes no fear-buy/§2.5 claim",
    "scandal_migration_risk": "pass — report lists legal as WARNING only (no prosecution, semi-annual review clean per r3 §5); no contrary legal news surfaced in my one search. Legal sweep after 05/11 is itself listed as open (item 5)",
    "optimistic_comp_sotp_bias": "pass with caveat — no comp used. SOTP recomputed by hand: parts sum 2.652,0 bn / 103,70M sh = 25.573 = center_param_pre. Grid reproduces (md5 91f4475b). FSO is not double-counted (fleet EBITDA = transport GP + depreciation of Era/Pride only, model.py:19). Bias is two-sided: scrap=0 (too low) vs dry-dock outside base (too high)",
    "data_provenance": "partial fail — HTM 1.015,87 bn (≈half of net cash 1.016 bn, ~40% of SOTP) read from a CĐKT scan; 3 source PDFs not in git, cannot re-read. D3 basis (LCTT line 03 = 53,1 bn attributed to repair accrual) is labelled inference by the report itself. Share count 103.702.452 [Q3 p13] and dividend 103,70 bn reconcile (1.000 đ/cp)",
    "liquidity_capacity_realism": "na — no fear-buy sizing claim; 2% NAV stated, 5 bn liquidity discount 1,98% carried from r3",
    "confirmation_bias_flipflop": "pass — centre unchanged vs r3 (23.099); r2→r3 bridge is explicit step by step (22.823 → 23.566 pre-discount). Price-zone ledger not opened, per the brief's blind constraint",
    "exit_discipline_gap": "na — no fear-buy claim; r3 §6 already lists HARD ABANDON (share issuance below book, adverse PVTrans related-party flows)",
    "missing_items": "fail (INCONCLUSIVE-grade) — (1) Extraordinary AGM 23/10/2026 (press 12/09, record date 28/9) to approve 'tàu Aframax số 3': price/age/funding/share issuance undisclosed; report has not re-checked since 05/11; unclear whether ship #3 is inside the model's 116M USD or a new ship. Issuance below intrinsic value would dilute SH: material, unquantifiable. (2) Future dry-dock spend after TT99: quantifiable, but the correct effect is ≈ −2% (tốt branch only), not −7% — under the 5% threshold. (3) 2026 welfare/bonus fund not deducted: small. Pass: audit (semi-annual review clean), FSO 2036 appendix (variant 22.489), related party 63,3% (WARNING), share-count basis 30/09/2026",
    "symmetry": "{too_high_checked: 5, too_low_checked: 6, too_low_items: ['scrap=0 with no evidence: +117 đ/cp per $1M, unquantified while dry-dock was quantified', 'D3 double-count: base 400 anchored to pre-TT99 2025 EBITDA that already includes the 53,1 bn/9T accrual ⇒ correct D3 ≈ 0,275×(−7%) ≈ −2%', 'corporate cost 10 years vs fleet life 4–8 years (−2.128 đ/cp in r3, [UL])', 'ship NPV −30% in bad branch ignores 70% debt cost < Ke (r3 admits magnitude [UL])', 'base r 13,5% > top of Ke band 13,4% (+40 đ)', 'liquidity discount at 5 bn (1,98%) vs actual sleeve 0,18%'] ; too_high: D3 dry-dock, AGM/issuance, HTM provenance, tốt EBITDA 550 = cycle peak, welfare fund}"
  },
  "independent_verification": "Re-ran calc_recheck.py against the restored r3 tree: output md5 91f4475b… identical to run1/run2. Hand-summed SOTP parts = 25.573 đ/cp, matching center_param_pre. Checked 53,1×4/3 = 70,8 and the scrap unit 117 đ/$1M. One web check: press 12/09/2026 confirms an extraordinary AGM on 23/10/2026 about Aframax ship #3, with no funding/issuance details",
  "killer_objection": "The AGM on the Aframax #3 purchase (23/10/2026) has not been followed up since 05/11. If the purchase is funded by share issuance, or ship #3 is outside the model's 116M USD, the share-count basis and the 'ship NPV = 0' branch (the label's main driver) change. Not quantifiable from the documents in hand",
  "recommended_followups": [
    "Pull the minutes/resolutions of PVP's 23/10/2026 extraordinary AGM (or postponed date ≤30/11): which ship, value, funding structure, any issuance",
    "Reconcile ship #3 against the 56,5 + 59,5M USD in assumptions_r3.json",
    "Rework D3: apply future dry-dock cost only to branches anchored on post-TT99 EBITDA (tốt 550); state clearly that 300/400 are anchored to pre-TT99 levels",
    "Quantify scrap (LDT per vessel × scrap price) alongside D3 instead of only a unit sensitivity",
    "Recover the Q3/2026 balance-sheet PDF to re-read HTM 1.015,87 bn"
  ],
  "summary": "The recheck is mechanically sound. The 270-cell grid, the r table and the D3 table reproduce exactly (md5 91f4475b), and a hand-summed SOTP matches the model. Low r sensitivity is real (short cash flows, net cash ~40% of value). D3 is the main 'too high' finding, but the report probably overstates it: base EBITDA of 400 is anchored to pre-TT99 2025 levels that already include the repair accrual, so the right adjustment is ≈ −2%, not −7%. Meanwhile scrap = 0 is a downward haircut with no basis and was never quantified, so the two directions roughly offset. Not CONFIRMED because of one material, unquantifiable missing item: the 23/10/2026 extraordinary AGM on buying Aframax ship #3 (funding/issuance undisclosed, not re-checked since 05/11). Also, HTM 1.016 bn cannot be traced back to its source PDF."
}
<<<END_VERDICT>>>

Sources:
- [doanhnhan.baophapluat.vn — PVP calls an extraordinary AGM to buy Aframax ship #3](https://doanhnhan.baophapluat.vn/van-tai-dau-khi-thai-binh-duong-pvp-trieu-tap-dhdcd-bat-thuong-muon-mua-them-tau-aframax-thu-3.html)