# custom30V accrual — panel reconciliation (Bước 1, job Taylor_20260830_035832)

Resolves the gap flagged by job `Taylor_20260830_031841`'s own §0 disclosure: IC(EY) 0.0316 (t=1.88,
sector-neutral pull) vs original doc's IC(EY) 0.0697 (t=4.78, `custom30v_cashflow_quality_selector_20260830.md`).
Same sign, materially different magnitude, on the same-looking "47-quarter" panel.

## Root cause: a BQ WHERE-clause bug in the ORIGINAL panel query, not vintage drift

Recovered the original query from the session transcript that produced `cfq_panel_20260830.csv`
(job `Taylor_20260829_173455` — the script itself was never saved to disk, only the CSV artifact):

```sql
WHERE EXTRACT(DAYOFYEAR FROM time) BETWEEN 1 AND 7   -- ~first trading day per quarter start month proxy
  AND MOD(EXTRACT(MONTH FROM time), 3) = 1
  AND time >= "2014-01-01" AND time <= "2025-12-31"
  ...
```

**Bug**: `DAYOFYEAR` resets to 1 every January 1st. `DAYOFYEAR BETWEEN 1 AND 7` is satisfied **only
in the first week of January**, regardless of which month is otherwise being filtered — April 1st has
`DAYOFYEAR≈91`, July 1st ≈182, October 1st ≈274, none of which ever land in `[1,7]`. ANDing this with
`MOD(month,3)=1` (intended to select Jan/Apr/Jul/Oct) doesn't broaden the window — it collapses to the
**intersection**, which is just January's first week, every year. Q2/Q3/Q4 are silently excluded
entirely. The inline comment ("first trading day per quarter start month proxy") states the intended
behavior; the code does not implement it.

**Verified directly against the saved CSV**, not just re-derived from the query text:

```
research/cfq_panel_20260830.csv — groupby(year, month):
  2014-01: 293 rows   2015-01: 315   2016-01: 382   ...   2025-01: 645
  (12 distinct year-buckets, ALL month=1, min date 2014-01-02, max date 2025-01-07)
rows per (ticker, year): median 4, max 4 — i.e. ~4 trading days/year (Jan 2–7 window), not 4 quarters
```

So the original doc's "**47 quarters**" is actually **~47 distinct trading DAYS, all within the first
week of January, across 12 years** (12×4 − 1 dropped for TTM lookback ≈ 47) — mislabeled as
independent quarters. Two compounding statistical problems, not one:

1. **N is not 47 independent events.** The ~4 daily snapshots within the same first week of a given
   January are nearly-identical cross-sections (same universe, prices/fundamentals barely moved
   day-to-day) — effectively ~12 independent year-events, not 47. The t-stats reported in the
   original doc (t=4.78 for EY, t=2.59 for the double-sort) are computed against an inflated N and are
   **overstated**.
2. **Sample is January-only, not quarterly.** Vietnamese year-start/Tet-adjacent trading (many
   companies also publish annual reports and Q4 preliminary results in this window) is a distinct
   seasonal regime, not a representative draw from all four quarters. The original doc's numbers
   describe "what EY/accrual predict in the first week of January," not "what they predict in a
   typical quarter" — a materially narrower and non-representative claim than what was stated.

## The sector-neutral job's panel (`pull_sector_panel.sql`, job `_031841`) is the correct construction

```sql
WHERE EXTRACT(MONTH FROM t.time) IN (1,4,7,10)
  AND EXTRACT(DAY FROM t.time) <= 7
  ...
```
— filters on calendar day-of-month (not day-of-year), correctly yielding the first week of *each*
quarter-start month. Verified against `cfq_sector_panel_20260830.csv`: **all 4 months (1,4,7,10)
present every year, 2014–2025, 48 distinct (year,quarter) cells** — a genuine quarterly panel. It also
already deduplicates to one row per (ticker, quarter) via `ROW_NUMBER() ... rn=1`, which the original
query never did (hence the 4 near-duplicate rows/ticker/quarter found in the original CSV).

**This is a real code bug in the original panel, not a BQ-vintage drift artifact** (the class of gap
the R3/EY-score registry note previously accepted as immaterial) — per the dispatch's own decision
rule, this means the flawed panel/numbers must not be carried forward, and the corrected
(sector-neutral job's) panel is the one to trust.

## What this does and doesn't change

- **Original doc's headline IC(EY)=0.0697 and double-sort +2.05pp/2M are unreliable** — built on an
  inflated-N, January-only sample. Superseded by the sector-neutral job's properly-constructed
  numbers (IC(EY) pooled=0.0316 t=1.88, sector-neutral accrual IC=0.0451 t=2.74, double-sort
  sector-neutral +2.69pp/2M t=3.17 on N=48 genuinely-independent quarters).
- **Does not overturn the double-sort GATE finding itself** — the correctly-constructed panel
  (job `_031841`) independently re-ran the double-sort on real quarterly data and still found a
  significant, LOO-robust spread (2.42–3.35pp across all 12 year-drops, sector-neutral). The
  direction and gate-not-tilt design implication survive; only the magnitude/significance claimed by
  the *original* preliminary doc do not.
- **Does not affect the full-backtest engine result already on record** (`custom30v_accrual_gate_20260830`,
  job `_014429`, POOLED gate, NO-GO) — that harness computes PIT accrual directly from
  `ticker_financial` per rebalance date inside `custom_basket_ag.py`, independent of either buggy or
  fixed exploratory CSV panel. The panel bug is confined to the ad-hoc preliminary-IC-test scripts.

**Verdict: gap explained, root cause is a code bug (day-of-year vs day-of-month confusion), corrected
panel identified and already in use for the sector-neutral proxy work. Proceeding to Bước 2 (full
backtest cycle for the sector-neutral gate variant) on that basis** — no further panel work needed
before wiring the sector-neutral gate into the existing `custom_basket_ag.py` harness.

## Follow-up (not blocking, logged for hygiene)

- `cfq_panel_20260830.csv` should not be reused for any future IC test without regenerating from a
  corrected query — it is a Jan-only sample mislabeled as quarterly.
- No `kb/data_registry/` entry exists for either panel (both are one-off exploratory pulls under
  `agents/Taylor/research/`, not a registered canonical source) — no registry correction needed, but
  worth noting for anyone who greps for "cfq_panel" later.
