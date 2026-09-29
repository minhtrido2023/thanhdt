# PREREG — LAG edge-health exit-keyed A/B (ONE leg)

**Job** `Taylor_20260910_142406` · Taylor · written 2026-09-10 **BEFORE any backtest leg ran**
**User approval** 2026-09-10 21:23 ICT, topic 1547589883999158363.

## Question (single, fixed)

Of the **+0.60pp** CAGR published for the edge-conditional allocator (tilt `w_LAG` 0.65 when
trailing-12M LAG edge `mean12 >= 4%`, else 0.50), how much survives when the `mean12` series is
keyed on the **exit** date (= the date the return becomes knowable) instead of the **entry** date?

This is **measuring a known bias**, not searching for an edge.

## The defect (restated from `research/bal_edge_gate_20260910/CONCLUSION_*.md` §2)

`edge_health_monitor.py::lag_edge_health()` enters T+5 after release and exits **25 sessions**
later, but writes the trailing-12M stats indexed on **entry**. `pt_v23_audit_2014.py:2057-2059`
reindexes that entry-keyed series over 2014-2026 with `ffill`, so on historical day `d` the gate
reads a value requiring data from `d+25` sessions. Measured lag: **32-45 calendar days**
(median 35).

**LIVE IS NOT AFFECTED** — the file only ever holds completed events, so the last row is ~5 weeks
old and the allocator ffills a stale-but-real value. Nothing here is a proposal to change the live
gate.

## Legs — exactly two (+1 inertness proof). No grid, no variants.

| leg | what changes |
|---|---|
| `ctrl` | pin R3, production engine, unchanged |
| `inert` | research engine copy, exit-key switch OFF — must be **byte-identical** to `ctrl` |
| `exitkey` | research engine copy, gate reads `mean12_av` indexed on `exit` |

Environment verbatim from job `Taylor_20260910_131906` / `research/lag_repin_20260803/run_repin.sh`:
`BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate`, `BQ_CACHE_THREADS=1`, `NAV_TOTAL_B=50`,
`ETF_LIQ=custompitg`, `BASKET_WT=namecap`, `BASKET_SELECT=yieldcombo`, `PARK_STATES=3:0.7`,
`AUDIT_END=2026-06-19`, `$DNA_PYEXE`, argv `v23a none postbull 0 edge`, `EXP_TAG` on every leg.

**Hard gate:** `ctrl` must reproduce md5 `7d053e6201c9d107685ff4d1dd9d2d2a` and self-check 0 VND on
both books. If it does not — **STOP and report**, run nothing further.

**Treatment differs in ONE thing.** The `(entry, ret)` pairs are copied VERBATIM from
`data/lag_edge_health.csv`; only the date axis of the trailing-12M window changes
(`build_exitkey_series.py`). No cohort rebuild, so no cohort-drift confound.

## N — independent events, not rows

The two series disagree on the gate (`>=4%` vs `<4%`) in **367 of 3,109 sessions (11.8%)** on the
allocator's axis, in **16 contiguous runs**. Sessions are serially dependent by construction (the
series is a trailing 12M mean, and `w_LAG` is band-rebalanced, not daily). So:

**N = 16 disagreement runs.** Not 367, not 3,109. With N=16 a sign test is possible in principle;
it is not planned, because the deliverable is a *magnitude* (how much of +0.60pp survives), not a
significance claim about a new effect.

## Declared in advance

- **Expected direction: unknown.** Both "most of +0.60pp disappears" and "most of it survives" are
  valid outcomes and will be reported in full, unedited, either way.
- **Noise floor must be stated with the number.** A comparable content-free perturbation of this
  same harness moved CAGR by **+0.40pp** (calendar placebo, job `Taylor_20260910_131906` §5) and
  ~0.385pp was measured in the 2026-08-23 margin study. If |Δ| lands inside that band, the finding
  is **"not distinguishable from harness path-divergence noise"** — it must NOT be quoted as a
  point estimate.
- **No threshold grid.** `EDGE_THR=4.0` is the production constant and stays fixed. Zero free
  parameters in this job.
- **Stopping rule:** one treatment leg. If another direction looks attractive, WRITE IT DOWN and
  stop — do not run it under this job.
- **Nothing is wired.** No production `.py` is edited; `data/lag_edge_health.csv` is never touched.
  `git status` must be clean on all production files at the end.
- **Registry:** if the published +0.60pp needs qualifying, this job PROPOSES wording only. It does
  not edit `data/results_registry.md`.

## Success criterion

There is none — this is a measurement, not a proposal. The deliverable is (a) pp surviving,
(b) whether that is distinguishable from harness noise, (c) proposed registry wording.
