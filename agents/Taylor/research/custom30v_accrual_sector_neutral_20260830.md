# custom30V accrual gate — sector-neutral standardization check (Việc 5)

Job Taylor_20260830_031841. Scope: REFINEMENT CHECK on the preliminary IC test
(`custom30v_cashflow_quality_selector_20260830.md`), per the limitation that doc's own §5 flagged
— "non-financial" pools steel/retail/tech which have very different natural accrual levels.
Question: does within-sector standardization make the accrual signal stronger/cleaner, or was
pooled-vs-sector a non-factor in the earlier NO-GO? No production code touched.

## 0. Panel — freshly pulled, NOT a byte-replication of the original doc

Re-queried `ticker_prune`, quarterly PIT (first trading day of Jan/Apr/Jul/Oct each quarter),
2014-01-01→2025-12-31, `PE>0`, full TTM NP/CFO (4 quarters non-null), `profit_2M` non-null,
excludes BANK(8355)/INSURANCE(8530-8579)/SECURITIES(8777)/REALESTATE(8633) — same construction the
original doc describes. Result: **48 quarters, 332 tickers**, median 143.5 names/quarter — close in
shape to the original (47 quarters, 307 tickers, median 142) but **not identical** (I don't have the
original SQL saved to reproduce the exact sampling day). Panel: `research/cfq_sector_panel_20260830.csv`.

**⚠️ Replication gap, disclosed not swept**: my pooled-panel IC numbers do not match the original
doc's:

| | original doc | this pull (pooled) |
|---|---|---|
| ey vs fwd2M | IC=0.0697 t=4.78 | IC=0.0316 t=1.88 |
| accrual (pooled) vs fwd2M | IC=0.0209 t=1.07 | IC=0.0452 t=2.68 |
| accrual vs ey (orthogonality) | IC=-0.1186 t=-8.13 | IC=-0.0730 t=-5.13 |

Direction of every sign is the same (ey positive, accrual weak-standalone-positive-in-both,
accrual strongly negatively correlated with ey in both) but magnitudes differ enough that this is
a genuinely different panel pull, not the same data re-touched. Likely cause: exact PIT sampling
day within the quarter (I used day≤7 of the quarter-start month; the original doc's script isn't
saved anywhere I could find to diff against). **Because of this gap, don't treat this doc's point
estimates as confirming/updating the original doc's numbers** — treat it as a self-contained A/B
test (pooled vs sector-neutral, both computed identically on the same fresh panel), which is valid
regardless of the panel-to-panel gap, but flag for follow-up: reconcile which panel construction
is right before this axis goes anywhere near a full backtest.

## 1. Sector classification used

BQ dictionary only says `ICB_Code` = "Industry Classification Benchmark", no code table available
in `bigquery_dictionary.json`. Used first digit of the 4-digit code (`ICB_Code // 1000`) as the
broadest available split — 9 buckets seen in the panel, of very uneven size. Grouped the 4 with
adequate density into their own bucket, lumped the rest into `OTHER`:

| sector_group | median names/quarter | min/quarter |
|---|---|---|
| 1 | 25.6 | 8 |
| 2 | 47.6 | 19 |
| 3 | 34.2 | 14 |
| 7 | 11.0 | 6 |
| OTHER (0,4,5,6,8,9 combined) | 26.1 | 10 |

Every (quarter, sector_group) cell has **n≥6** — no cell below the standard qcut-tercile minimum.
This is coarser than true GICS/ICB sub-industry (steel and cement both fall in "2", for instance)
but it's the finest split BQ's `ICB_Code` supports without a code lookup table, and it's dense
enough to standardize within.

## 2. Standalone IC and orthogonality — sector-neutral vs pooled

Accrual score = within-cell percentile rank of `accrual_ratio` (low=best cash-flow quality),
computed per (quarter, sector_group) instead of per quarter pooled.

```
                              IC       t       N (quarters)
accrual (pooled)            0.0452   2.68     48
accrual (sector-neutral)    0.0451   2.74     48

accrual vs ey (pooled)     -0.0730  -5.13     48
accrual vs ey (sector-neu) -0.0650  -4.81     48
```

**Standalone predictive power and orthogonality vs EY are essentially unchanged** by sector
neutralization — same IC, same t-stat magnitude, same conclusion (weak alone, real but negative
correlation with EY, i.e. the classic value-trap confound). Sector composition was NOT masking or
distorting the standalone signal.

## 3. Double-sort inside the cheap-EY bucket — where it matters

Same design as the original: top EY tercile (pooled) per quarter → split by accrual tercile within
that cheap bucket. Ran once with pooled accrual rank, once with sector-neutral accrual rank:

```
                    tercile0(best)  tercile1(mid)  tercile2(worst)   paired diff (0-2)   t     N
pooled                4.74            3.26           2.54              2.20pp          2.35   48
sector-neutral        5.58            1.98           2.89              2.69pp          3.17   48
```

**Sector-neutral standardization strengthens the double-sort spread**: +2.69pp/2M vs +2.20pp/2M
pooled, t=3.17 vs t=2.35 (both N=48 independent quarters). Middle tercile is still non-monotonic in
both versions (known small-N-per-cell tercile artifact, same note as the original doc) — the
best-vs-worst spread is the number that matters and it got *stronger*, not weaker, under
sector-neutral standardization.

**LOO-by-year robustness** (drop each of the 12 years, recompute mean paired diff): sector-neutral
stays in **2.42–3.35pp** across all 12 drops, never flips sign, tighter range than pooled's
1.91–2.93pp — no single year is driving the improvement.

## 4. Conclusion

**Sector-neutral standardization is a modest, real improvement, not a wash and not a reversal.**
Standalone IC/orthogonality (§2) barely move — pooling by "non-financial" wasn't hiding a
materially different standalone relationship. But the double-sort gate spread (§3, the actual
mechanism proposed for wiring — a GATE inside the cheap-EY bucket, not an additive leg) is both
larger (+2.69pp vs +2.20pp) and more significant (t=3.17 vs t=2.35) under sector-neutral
standardization, and it's robust across LOO-by-year.

**This is a GO for the sector-neutral variant to carry forward into a full backtest cycle**, same
class of caveat as the original: this is still one double-sort on one forward horizon (2M), on a
panel that itself doesn't byte-match the earlier pull (§0) — needs 1M/3M robustness, IS/OOS split,
pre-registered gate threshold, DSR/PBO, and quant-skeptic CONFIRMED before anything touches
`custom_basket.py`. Recommend the panel-reconciliation question (§0) get resolved in that same
cycle rather than as a separate detour — it's cheap to redo once, expensive to discover mid-backtest.

## 5. Honest limitations

- **Sector granularity is coarse** (4-digit ICB first-digit only, no lookup table available in this
  codebase) — steel and cement both land in bucket "2", which is exactly the kind of within-bucket
  heterogeneity the original doc's limitation was worried about. A true ICB sub-industry code table
  would let this run finer; didn't chase that down this round (scope = "is the direction worth it",
  not "build the definitive classifier").
- **OTHER bucket lumps 6 heterogeneous ICB-digit groups** (0,4,5,6,8,9) purely because each is too
  thin alone (median <10/quarter) — median 26/quarter combined is workable but this is a materially
  different sector concept from "one industry."
- Same N caveats as the original doc: 48 independent quarters, tercile-within-tercile-within-sector
  cells push per-cell N down further; robust to the LOO check run here but still a preliminary
  double-sort, not a backtest.
