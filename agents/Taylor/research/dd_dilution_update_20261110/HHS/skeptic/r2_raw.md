**Verdict: INCONCLUSIVE (medium confidence).** The rev5 dilution maths is correct and I reproduced it. But I can't confirm the centre, for three reasons. The inherited centre of 13,969 can no longer be rebuilt from source. The DƯỚI ("below range") label rests entirely on the 0% holding-discount convention, which the user still hasn't ruled on. And the remaining cost to finish NC-II, open since r3, is still not quantified, and rev5 has dropped it from its own open list in §8.

**What I re-checked**
- **Rebuilt from inputs (V_pre 13,969, 431.99M shares, 259.19M rights shares at 10,000, liquidity discount 1.41%, 7% stock dividend):**
  - EX full coverage, k=1: **11,615**
  - EX "TCH only", k=0.8: **11,240**
  - EX "TCH only", k=1: **12,060**
  - EX with no rights issue: **13,055**

  All four match `calc_rev5_out.json` to the đồng. The stock-dividend count of 48.38M shares (7% × 691.18M) also ties to resolution item TT09.
- **TCH's 58.31% stake in HHS:** traces to 251,905,777 / 431,985,968 shares (`dd_HHS_20261101/GAPS_FILL.md:96`, from the 2025 audited report). It is correct, but `assumptions.json` gives no source for `tch_stake_hhs`.
- The correction to the partial-coverage formula (finding #2) and dropping k=0.946 in favour of k≥1 (finding #6) are both correct.

**Too HIGH**
- **NC-II completion cost (r3's open item G10):** still not quantified. Rev5 mentions it only in passing in §6 and has removed it from §8. HHS's value sits in the NC-II inventory surplus on a cost base of about 6,009.8 bn. A completion cost of just 10% of that, at HHS's ~51% economic share, is roughly −700 đ/share, which is above the 5% materiality line. It only pushes one way.
- **Centre can't be reproduced:** r3's `assumptions_r3.json` and `SUMMARY.json` are gone. The "three independent sources" for 13,969 are three copies of the same number, not a rebuild.
- **Weak evidence against the holding discount:** the report cites CRV's 153.7 bn cash dividend as support for 0%. But that dividend went to TCH, which holds CRV directly. It shows nothing about cash reaching HHS's shareholders. This matters because the 0% base adds +3,208 đ/share (step 8 of r3's bridge), about 23% of the centre.
- **I.14 at break-even (NPV0):** 2,591.9 bn goes into a project that has no building permit yet. The only cost of delay modelled is a 2pp × 3-year spread on the borrowed shortfall (−102 đ/share). This follows the fleet's V4 rule, but it treats the project as neutral even if it is delayed for years.
- **Liquidity discount:** 1.41% may be too low. The report itself notes that 5 bn is 48% of 60-day average daily value.

**Too LOW**
- Every reading of the NĐL share issue gives k≥1, because the issue price of 10,000 is below NĐL's unaudited book value of 11,210. Base k=1 is therefore conservative, by about +0.6%.
- The 30/09 balance of the group's 2,435.3 bn held-to-maturity deposits (01/01 figure) was not read. If enough is left, the shortfall can be self-funded and the −102 đ/share borrowing cost disappears.

**Missing-items checklist**

| Item | Result |
|---|---|
| Committed capex | Pass (I.14 included) |
| Share basis | Pass (30/09/2026, TM1.1) |
| Related parties | Pass (TM40 read) |
| One-off items in base year | Pass (2025Q2 excluded) |
| Audit opinion | Partial: FY2025 audit is clean, but the review status of the H1/2026 accounts isn't stated |
| Welfare/bonus fund | Inherited from r3 as "not disclosed", not searched again in rev5 |
| Real-estate sector items | **Fail**: NC-II completion cost |

Market prices in the report were ignored for this judgement.

<<<VERDICT_JSON>>>
{
  "case_topic": "HHS — DD rev5 dilution update (rights 60% @10.000 + 7% stock dividend), centre CUM 13.969 / EX 11.615",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — no fear-buy/§2.5 claim; report states HHS is not §2.5-eligible and is forensic-EXCLUDE",
    "scandal_migration_risk": "pass — legal/governance WARNINGs listed (NQ 10/NQ-HĐQT 20/11 written shareholder consultation with undisclosed content, 852 bn deposit-contract transfers TCH↔CRV/NĐL, 69 bn TCH loans not visible on cash-flow lines 33/34); no evidence of legal-entity/asset-level migration; HARD ABANDON triggers stated in §7",
    "optimistic_comp_sotp_bias": "fail (partial) — the headline depends on holding discount 0% vs 27% (r3 bridge step 8: +3.208 đ/cp ≈ 23% of centre); the only evidence offered for 0% is CRV's 153,7 bn cash dividend, which went to TCH (direct CRV holder), not to HHS — it does not support 0% for HHS holders. I.14 at NPV0 with no building permit and only a 2pp×3y spread on the shortfall is symmetric by convention but ignores the time cost of 2.591,9 bn sitting idle",
    "data_provenance": "fail (partial) — the load-bearing V_pre 13.969 cannot be rebuilt: assumptions_r3.json/SUMMARY.json are lost; the 'three independent sources' are copies of one number. tch_stake_hhs 0,5831 has no source field in assumptions.json (it does trace to BCTN25/Q3 TM22b: 251.905.777/431.985.968 cp). NĐL BV 11.210 unaudited (affects only the k>1 upside). The 30/09 HTM-deposit balance was not read",
    "liquidity_capacity_realism": "na — no sizing applied (EXCLUDE); report itself flags the 1,41% liquidity discount may be too low at 5 bn ≈ 48% of 60-day ADV",
    "confirmation_bias_flipflop": "pass — vs r4 the centre moves 0%; changes are mechanical corrections responding to skeptic r1 (#2 undercount fixed, #6 k=0,946 dropped) plus newly read sources (TM38/TM40/TM1.5, NQ 20/11); no re-interpretation of old facts toward a YES. dd_price_zones.json not opened (price-blind constraint)",
    "exit_discipline_gap": "na — no position proposed; abandon/HARD ABANDON triggers are still stated in §7",
    "missing_items": "fail — NC-II completion cost (r3 G10) still not quantified and dropped from the §8 open list (only a passing mention in §6); NC-II inventory cost base ~6.009,8 bn, value sits in its surplus ⇒ 10% completion cost ≈ −700 đ/cp (>5%), unquantifiable from available data ⇒ INCONCLUSIVE. Also: welfare fund inherited as 'not disclosed' without a new search; H1/2026 review status not stated; 30/09 HTM-deposit balance unread (affects shortfall financing, upside −102 đ/cp may not occur). Pass: committed capex I.14 in, share basis 30/09/2026 TM1.1, related parties TM40, one-off 2025Q2 excluded, FY2025 audit unqualified AASC"
  },
  "independent_verification": "Recomputed from inputs (V_pre 13.969, N0 431,99m, NR 259,19m @10.000, d5 1,41%, stock dividend 7%): EX full k=1 = 11.615, TCH-only k=0,8 = 11.240, TCH-only k=1 = 12.060, no issue = 13.055 — all match calc_rev5_out.json. Stock-dividend count 48,38m = 7% × 691,18m matches TT09. TCH 58,31% traced to 251.905.777 cp in BCTN25/Q3 TM22b (dd_HHS_20261101/GAPS_FILL.md:96).",
  "killer_objection": "The centre was inherited from an r3 grid that can no longer be reproduced (assumptions lost), and it still excludes NC-II completion costs (G10, open since r3, material and one-directional), while the DƯỚI label rests entirely on holding discount 0% (+3.208 đ/cp), whose only cited evidence (CRV dividend paid to TCH) does not show cash reaching HHS shareholders.",
  "recommended_followups": [
    "Quantify the remaining NC-II completion cost from HTK notes / project budget (G10) and put it in base or explicitly as a quantified sensitivity; restore it to the §8 open list",
    "Rebuild the r3 grid (or at least the central-parameter point 13.893) from source filings so V_pre is reproducible, and re-lock the assumptions",
    "Read the 30/09/2026 held-to-maturity deposit balance (Q3 HN appendix) to settle whether the 1.080,6 bn shortfall needs debt",
    "Add a source field for tch_stake_hhs in assumptions.json",
    "Correct the §2/§2.1 wording: the CRV→TCH dividend is not evidence for holding discount 0% at the HHS level; search for cash dividends CRV→HHS or HHS→shareholders",
    "User ruling on the holding-discount convention remains the decisive open item; re-run after the 14–25/12/2026 written shareholder consultation results"
  ],
  "summary": "The rev5 dilution maths is correct and reproducible (EX 11.615 / 11.240 / 12.060 / 13.055 all recomputed exactly), and the r1 findings on partial-coverage undercount and the k=0,946 error are properly fixed; k≥1 under every NĐL reading makes base k=1 mildly conservative (too-low side), as does the possibility that the shortfall is self-funded from unread held-to-maturity deposits. On the too-high side, three weaknesses keep this from CONFIRMED: the inherited centre 13.969 can no longer be rebuilt from source; the NC-II completion cost (G10) remains unquantified and has slipped off the open-items list despite plausibly exceeding 5% of centre; and the DƯỚI label depends wholly on a 0% holding discount whose cited evidence (CRV's dividend to TCH) does not actually bear on HHS shareholders. Market prices in the report were ignored for this judgement."
}
<<<END_VERDICT>>>