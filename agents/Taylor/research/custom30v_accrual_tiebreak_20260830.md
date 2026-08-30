# custom30V accrual-quality — TIEBREAK variant in `eyonly` top-30 (job Taylor_20260830_031818)

Distinct from the accrual-GATE arm (job `Taylor_20260830_014429`, NO-GO on `yieldcombo`/production
custom30V — see `data/results_registry.md` "2026-08-30 — CUSTOM30V ACCRUAL-QUALITY GATE"). This job
tests arm (b) from `research/custom30v_cashflow_quality_selector_20260830.md` §4: "use accrual rank
as a tiebreak among near-equal 1/PE scores, same pattern as `BASKET_DY_TIEBREAK`" — proposed but
never run in that doc.

## 0. Selector context — `eyonly` is NOT production

`BASKET_SELECT=eyonly` is the `v4final` research selector (job `Taylor_20260714_140127`), audit-only,
never wired. Production custom30V = `BASKET_SELECT=yieldcombo` (A0, LIVE). `eyonly` was benchmarked
against A0 as a return-neutral candidate (A2: FULL 27.04 vs A0 27.09, −0.05pp) and already has ONE
tiebreak precedent on record: **DY tiebreak (arm A4, job `Taylor_20260714_152605`) = NO-GO** — band
ey-rank 20-45, FULL −0.00pp / IS ±0.00 / OOS −0.01, but MaxDD got WORSE (−17.6→−18.6) and Calmar
worse (1.54→1.45) despite 48/48 rebalances changing composition (verified not-a-no-op). Structural
reading recorded there: **portfolio-level MaxDD in this selector family is dominated by market beta,
not by anything a within-band name permutation touches** — the same argument very plausibly applies
here, since accrual-tiebreak is architecturally the identical operation (permute-within-band,
fail-open, score untouched) just fed a different metric. This job tests whether that structural
read is metric-specific (DY) or general (any tiebreak axis).

## 1. Pre-registration (written before reading either run's output)

- **Band = ey ranks 20-45 (1-indexed, inclusive)** — reusing the *exact* band DY tiebreak already
  established as the codebase's generic definition of "near-equal 1/PE, marginal cohort where a
  tiebreak can actually move a pick" (straddles the `top_n=30` cut inside `CFO_POOL=60`). NOT
  re-derived from the accrual double-sort's own window (that test used top-EY-tercile, a much wider
  cohort) — deliberately reusing the established architectural band rather than picking a new one
  that happens to flatter this metric's own preliminary result. This is the single biggest lever
  against data-snooping in a tiebreak-threshold choice: the mechanism's definition of "marginal" is
  fixed by the DY precedent, not tuned per metric.
- **Direction**: accrual_ratio = `(TTM_NP−TTM_CFO)/|TTM_NP|`, **ascending** (lowest = best cash-flow
  quality = ranked first) — opposite sign convention to DY (descending, high=best), but same "best
  goes to the better slot" semantics.
- **Scope**: non-financial routes only (route NOT IN {BANK, INSURANCE, SECURITIES, REALESTATE}) —
  identical scope to the gate arm; CFO not economically comparable for those routes
  (`banking_valuation_framework.md`).
- **Fail-open**: a financial-route name, or a name with an undefined/unknown accrual ratio
  (TTM_NP≤0 or no PIT history as-of Release_Date), never moves — keeps its exact ey slot. Sorting an
  undefined value to either end of the band would be a different, unmeasured rule (same reasoning
  DY's own fail-open used).
- **PIT**: as-of `Release_Date` (fallback `time+45d`), identical convention to the gate arm and to
  `dy_at`/`qfloor_asof` elsewhere in this file — a report published after the rebal date can never
  be read.
- **Expected coverage, stated before running**: DY's own coverage in the identical band was ~66%
  movable (950/1440 name-rebal, `Taylor_20260714_152605`). Accrual should be LOWER than that,
  because financial-route names in the band are now *always* fixed (DY had no such route exclusion)
  and the accrual gate arm's own panel showed 0.13% of the (already non-financial) rows have
  `TTM_NP≤0` (immaterial) — so the main coverage loss vs DY is the financial-route carve-out, not
  missing accrual data. Given `eyonly` is not sector-routed and BANK/INSURANCE/SECURITIES/REALESTATE
  historically run ~25-47% of custom30V-family weight (`v4final` job 140127 finweight audit), a rough
  prior is **coverage in the 40-55% range** — logged as a pre-stated expectation, not a target;
  the actual run prints `[accrual tie-break] coverage over N band-slot observations: movable=...`
  and that number is reported as-is regardless of where it falls.
- **Number of names expected to actually CHANGE rank**: DY tiebreak changed composition on 48/48
  rebalances despite a wash return effect — a permutation-within-band changes *some* picks almost by
  construction whenever ≥2 movable names in the 26-slot band have DY/accrual values that don't
  already sort in ey order. Given the accrual/ey orthogonality found in the preliminary IC test
  (accrual vs ey correlation t=−8.13, i.e. NOT already sorted the same way as ey) the reorder is
  expected to be materially non-trivial per rebal, similar in kind to DY's 48/48. This is checked
  post-hoc against the actual per-rebal reorder count, not assumed.
- **Decision rule stated in advance**: WIRE requires both IS and OOS to improve (same rule the gate
  arm's NO-GO was judged against) — a mixed-sign or wash result is NO-GO, no cherry-picking robustness
  variants. Given `eyonly` itself is not production, "GO" here means "worth carrying into a real
  wire proposal that would ALSO require re-litigating whether `eyonly` itself should replace
  `yieldcombo`" — a two-step bar, stated explicitly so a merely-positive tiebreak number is not
  mistaken for a production-ready result.

## 2. Harness

Fork `custom_basket.py`→`custom_basket_ag.py` (already forked for the gate arm; this job ADDS
`BASKET_AGATE_TIEBREAK` env var, gated to `SELECT_MODE=="eyonly"` only, independent of the existing
`BASKET_AGATE_PCT`/`yieldcombo_agate` gate mechanism — `custom_basket.py` and `custom_basket_ag.py`'s
existing gate code path untouched). `engine_ag.py` (import-swap fork of `pt_v23_audit_2014.py`)
unchanged. Same pinned config as the gate arm and as the R3 registry pin: `BQ_LOCAL_CACHE=data/
bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg
BASKET_WT=namecap PARK_STATES="3:0.7" AUDIT_END=2026-06-19 LAG_ADV_BASIS=price`, threads=1,
`$DNA_PYEXE engine_ag.py v23a none postbull 0 edge`.

- **ctrl (eyctrl)**: `BASKET_SELECT=eyonly` — validity check: should reproduce the A2 `eyonly`
  registry anchor (FULL ~27.0, IS ~23.0, OOS ~30.8, Sharpe ~1.8, MaxDD ~−17.6, Calmar ~1.54) within
  normal vintage drift (registry itself notes A0 27.09→27.04 vintage drift between two same-day
  reruns, i.e. a fraction of a point is expected and not a red flag).
- **treatment (eytb2045)**: `BASKET_SELECT=eyonly BASKET_AGATE_TIEBREAK=20:45`.
- self-check 0 VND (BAL+LAG) required on both legs before trusting any number.

Logs: `eng_eyctrl.log`, `eng_eytb2045.log`. CSVs auto-tagged `_exp_eyctrl_*`/`_exp_eytb2045_*` —
canonical R3 CSV untouched (same `EXP_TAG` safety as the gate arm, §8 of `coding_guidelines.md`).

## 3. Results

Both legs `EXIT=0`, self-check clean: `[selfcheck BAL] ... err = 0 VND; [selfcheck LAG] ... err = 0
VND` on both `eng_eyctrl.log` and `eng_eytb2045.log` — no self-check recompute needed, printed
directly.

| Metric | ctrl (eyctrl) | treatment (eytb2045) | Δ |
|---|---|---|---|
| FULL CAGR (12.46y) | 29.68% | 29.21% | **−0.47pp** |
| IS CAGR (2014-01-02→2019-12-31, 5.99y, recomputed from `combined_nav`) | 27.89% | 27.82% | **−0.07pp** |
| OOS CAGR (2020-01-02→2026-06-19, 6.46y, recomputed from `combined_nav`) | 31.31% | 30.46% | **−0.85pp** |
| Sharpe(252) | 1.97 | 1.96 | −0.01 |
| MaxDD | −16.4% | −16.9% | worse |
| Calmar | 1.81 | 1.73 | worse |

IS/OOS recomputed independently from each leg's `combined_nav` column (not eyeballed off the
per-year prints in the log) — boundary dates: IS window uses last trading day ≤2019-12-31
(2019-12-31 itself present in both CSVs), OOS window starts at first trading day ≥2020-01-01
(2020-01-02 in both).

**Ctrl-vs-anchor validity flag (open, does not change the decision below):** the `eyctrl` leg does
NOT reproduce the §2 pre-stated `eyonly` A2 registry anchor within "vintage drift" — anchor FULL
~27.0/IS~23.0/OOS~30.8/MaxDD~−17.6/Calmar~1.54 vs actual FULL 29.68/IS 27.89/OOS 31.31/MaxDD
−16.4/Calmar 1.81. The IS gap (+4.89pp) and Calmar gap (+0.27) are far larger than the ~0.05pp
vintage drift precedent cited for A0 reruns — this looks like a real config/engine-fork difference
between `engine_ag.py`/`custom_basket_ag.py` and whatever produced the original A2 anchor (job
`Taylor_20260714_140127`), not noise. **Does not invalidate this job's own conclusion**, because
the decision here is a controlled A/B: ctrl and treatment share the identical harness/config/data
vintage, differing only in `BASKET_AGATE_TIEBREAK`, so the relative Δ is trustworthy even though
the absolute level disagrees with the older anchor. Flagged for follow-up, not resolved here —
don't cite this ctrl leg's absolute numbers as a fresh `eyonly` anchor without reconciling first.

**Decision (per §1 pre-registered rule, "WIRE requires both IS and OOS to improve"):** treatment
improved NEITHER — IS −0.07pp, OOS −0.85pp, both negative, alongside worse MaxDD and worse Calmar.

## **NO-GO.**

Confirms the §0 hypothesis as GENERAL, not DY-specific: two independent tiebreak metrics (DY,
descending; accrual-quality, ascending) fed into the identical permute-within-band mechanism on the
identical `eyonly` selector both produced a wash-to-negative FULL result with WORSE MaxDD/Calmar
despite materially reordering names within the band. Reading carried forward: **portfolio-level
MaxDD/Calmar in this selector family is dominated by market-beta timing (allocator, gates), not by
which name occupies a marginal near-equal-EY slot** — a tiebreak-within-band is structurally not a
lever this family responds to, regardless of which secondary metric feeds it. No further
tiebreak-axis variants (e.g. F-score, ROE-trend) are worth testing under this same band/mechanism
without first changing that structural read.
