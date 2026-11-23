**Verdict: CONFIRMED, medium confidence.** Rev6 puts a size on the high-rise margin risk that r3 flagged and the base centre of 13,969 holds up. One justification is overstated, though: the PPA is not an independent valuation. That wording should be fixed. I ignored every market price in the report (9,700 and the TERP).

**What I re-checked myself**
- I re-ran `rev6/calc/calc_rev6.py`. Its output md5 `4e593e33…` is byte-identical to `run1.txt`.
- The re-run reproduces the base (14,169 before the liquidity discount, 13,969 after), the probability-weighted 13,784, the w=30%/s_hh=−0.20 stress at 12,708, and the skeptic's −0.54 shift at 11,663.
- I recomputed these by hand and they match:
  - S_OBS = 0.8 × (0.5205 − 0.1) / 0.4795 = 0.7016.
  - STEP_AT (after-tax step-up left over from the PPA) = 2,020.76 / 0.2 × 0.8 = 8,083.0.
  - Model surplus = 4,216.5 + 961.3 + 817.0 = 5,994.6, which is 74.2% of the PPA step-up.
  - Book value per share = 9,152.94 / 431.99 = 21,188.
- The comparison against the PPA is consistent: the model strips the step-up (`CRV_COST = CRV_FV − STEP_AT`) and applies s to a historical-cost base (the observed margin is "ex-PPA 52.2%").

**Where the centre could be too high**
- **The PPA is not "the only independent source".** The fleet's own files say otherwise:
  - The PPA is an intra-group fair-value measurement and produced the 3,488.7 bn remeasurement gain (`dd_HHS_20261101/REPORT.md:94,217`).
  - The fleet's own brief records "không định giá độc lập" (no independent valuation) (`BRIEF_v2_investor.md:6`).
  - The valuation report is unpublished and has no per-project breakdown (G8).
  - It therefore supports the total, but it cannot settle how much value sits in the high-rise HH1–HH4 lots. It also cannot justify putting 50% probability on "HH earns at least s_obs".
- **The w anchor is biased low.** The 3.75% figure is a share of land area. High-rise lots are dense: about 2,494 units sit on 18,494 m². Their share of cost, and especially of land-use fees, should be well above their share of area.
  - A realistic w is about 10–30%, which gives −2% to −9% (13,642 down to 12,708).
  - The −1.3% only reflects the report's own probability choices.
  - None of this changes the base, because V4 still has no independent evidence for a cut.
- **Two inspection conclusions from v2 disappeared from the WARNING list in r3, rev5 and rev6:** TB 2124/TB-TTCP (CRV, 7.87 bn provisionally collected) and KL 08/KL-TTTP (Pruksa social housing). The 7.87 bn is immaterial; the social-housing finding has no figure.

**Where the centre could be too low**
- The PPA implies about 2,088 bn more after-tax surplus than the model uses. That is roughly +2,470 đ/share undiscounted, or +17%, and rev6 deliberately does not use it to raise the centre.
- `CRV_COST` assumes the entire deferred tax liability comes from the PPA. Any part that doesn't means the centre is understated.
- Setting k = 1 is conservative, worth at most about +1%.

**The biggest open variable is not a model error.** The holding-discount choice (0% vs 27%) moves the centre about 23% and changes the label. The user still has to decide it, and the report shows both versions side by side without merging them.

<<<VERDICT_JSON>>>
{
  "case_topic": "HHS — DD rev6 (dilution update rights 5:3 @10.000 + 7% stock div; HH1–HH4 high-rise margin split), REPORT_rev6.md, skeptic round 4",
  "mode": "DD_GENERAL",
  "verdict": "CONFIRMED",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; no fear-buy/§2.5 claim (HHS in forensic EXCLUDE, no sizing)",
    "scandal_migration_risk": "pass with gap — WARNINGs carried: 60% rights issue, NQ 10/NQ-HĐQT 20/11/2026 written poll 14–25/12 (content unpublished, redo trigger), 852,0 bn TCH↔CRV/NĐL deposit-contract transfer. Gap: inspection conclusions TB 2124/TB-TTCP (CRV 7,87 bn) and KL 08/KL-TTTP (Pruksa NƠXH) listed in dd_HHS_20261101 BRIEF_v2 no longer appear in r3/rev5/rev6 WARNING lists; no evidence of asset seizure/licence loss",
    "optimistic_comp_sotp_bias": "pass with caveat — no comps used upward; PPA used only defensively (not to raise centre, which it would by ~+17%). Caveat: the 50% probability mass on 'HH ≥ s_obs' and w anchored on land-AREA share 3,75% are self-set and lean favourable; high-rise lots carry far more GFA/land-fee per m², plausible w 10–30% ⇒ −2,3%…−9,0% (calc hh_split), still <P10 label flip and base unchanged under V4",
    "data_provenance": "pass with correction — all model inputs trace to hhs_r3.py constants (BCTC Q3/2026 HN, KT25 TM), md5-pinned; KTPL 6,458 bn mã 323 correctly treated as liability already in EQ_ME. Correction: §2.1 calls the PPA 'nguồn độc lập duy nhất' — fleet's own files record it as intra-group, 'không định giá độc lập', source of 3.488,7 bn remeasurement gain, valuation report unpublished; it is an audited-accepted management FV, not an independent valuation",
    "liquidity_capacity_realism": "na — no sizing while EXCLUDE; CK 1,41% inherited, report flags 5 bn = 48% ADV60 (display only)",
    "confirmation_bias_flipflop": "pass — compared only to HHS's own rev5/r3 and skeptic r1–r3; centre 13.969 unchanged, rev6 changes are responses to skeptic r3 items (grid reproduction, HH split, KTPL search), not reinterpretation; skeptic's −10%/−17,7% reproduced exactly rather than argued away",
    "exit_discipline_gap": "na — no entry/sizing claim; two-sided milestones + HARD ABANDON (rev5 §7) stated",
    "missing_items": "pass (minor gaps) — committed capex: I.14 2.591,9 + unfunded 1.803,2 bn present (growth, NPV0/scenario); share basis 431.985.968 @30/09/2026 TM1.1; dilution + 7% bonus modelled; welfare fund found (6,46 bn, ≤15 đ/cp); related-party 852 bn + TCH loans (repaid) present; audit FY2025 unqualified AASC, Q3 unreviewed flagged; one-off 3.507 bn excluded; real-estate land bank/commitments present; VietinBank pledge of HH lots secured CRV 390 bn loan now repaid. Absent: HH1–HH4 cost share/total investment (unpublished — bounded by ladder, ≤−9% at w 30%, plausible ≤−4,5% at w≤15%); NƠXH/inspection obligations (unquantified, likely small); remaining NC-II completion budget (G10, NPV0 per V4)"
  },
  "independent_verification": "Re-ran rev6/calc/calc_rev6.py: output md5 4e593e3391a9ec15b54a3fb0585d258b identical to run1.txt; base 14.169 pre-CK / 13.969 post (P10 12.422, P90 15.564, n=405), prob-weighted 13.784 (−1,33%), stress w30/s−0,2 12.708, skeptic −0,54 11.663 — all match report. Hand recompute: S_OBS 0,7016; STEP_AT 2.020,76/0,2×0,8 = 8.083,0; model surplus 4.216,5+961,3+817,0 = 5.994,6 = 74,2% of PPA; BVPS 21.188 — match. Confirmed model strips PPA step-up (CRV_COST = CRV_FV − STEP_AT) and s_obs is ex-PPA margin, so the PPA comparison is like-for-like.",
  "killer_objection": "The argument that keeps the base unchanged leans on the PPA as the 'only independent source', but that PPA is an intra-group fair value (no independent valuation, unpublished, generated the 3.488,7 bn gain) and gives no per-project split; if HH1–HH4 is 15–30% of NC-II carrying cost at NPV0-or-worse margin, the centre is 3,5–9% lower than shown — not a label flip, but the −1,3% weighted figure understates it.",
  "recommended_followups": [
    "Reword §2.1: PPA = audited-accepted management/intra-group FV, not an independent valuation; keep it as a total-level consistency check only",
    "Re-anchor w on value/GFA (land-use fee per lot, buildable GFA) instead of land-area share; show w 10–30% as the plausible band alongside the −1,3%",
    "Restore inspection items TB 2124/TB-TTCP and KL 08/KL-TTTP (Pruksa NƠXH) to the WARNING list with current status",
    "Obtain CRV standalone audited FS 2025 (per-project book values) to back out HH1–HH4 carrying cost (G8 path noted but not done)",
    "User decision on holding discount 0% vs 27% remains the dominant (~23%) open variable; re-label after it, and after the 14–25/12/2026 poll content is published"
  ],
  "summary": "Rev6 closes the r3 INCONCLUSIVE: it reproduces the skeptic's whole-block shifts exactly, splits the high-rise HH1–HH4 part with a w × s_hh ladder, and its calc re-runs byte-identically. Recomputed S_OBS, the PPA step-up (8.083 bn), the model/PPA ratio (74,2%) and book value per share all match. The PPA cross-check is like-for-like because the model strips the step-up and uses an ex-PPA margin. On the expensive side, the report overstates the PPA as an 'independent source' when it is an intra-group fair value, and anchors w on land area, which understates the high-rise share; a plausible w of 10–30% gives −2% to −9%, not −1,3%. This does not flip any label or justify a base cut under V4. On the cheap side, the PPA implies roughly +17% that the model deliberately leaves out, and k=1 is conservative (≈+1%). Two inspection WARNINGs (TB 2124, KL 08 Pruksa NƠXH) dropped out of the list and should be restored. The holding discount 0% vs 27% remains the dominant open variable and is the user's call. Market prices in the report were ignored."
}
<<<END_VERDICT>>>