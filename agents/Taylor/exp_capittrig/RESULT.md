# RESULT — CAPIT trigger + state-conditional sizing (job Taylor_20260720_170234)

**Verdict: Q1 NO-GO · Q2 NO-GO · Q3 INCONCLUSIVE · Q4 NO-GO. Nothing to wire.**
The trigger as built (`WASHOUT_GATE=0.30`, D_RSI<0.3 breadth, fire at first touch) is
**vindicated, not improved on**. Production is not sitting on an un-tuned parameter — it
is sitting on a plateau, which is the good case.

Prereg: `PREREG.md` (written before results). N_trials declared = 14. Scripts:
`build_data.py`, `analyze.py`. Panel: 3054 sessions 2014-01-02→2026-06-15, ~1,270 names.
**Self-check 0 VND: N/A** — no NAV path simulated (dose-response/conditional-return study),
same posture as the 4 prior CAPIT jobs. Any future wire proposal gets the full NAV audit.

## Ground truth re-verified in code (dispatch asked; several assumptions were off)

| Item | Reality |
|---|---|
| `WASHOUT_GATE` | `0.30` **hard-coded constant, line 577** — NOT env-configurable |
| breadth | `AVG(D_RSI<0.3)` over `ticker_prune`, `Close_T1>0` (line 929) |
| clustering | new event when gap ≥ **30 calendar days**; `d0` = first day of cluster |
| `capit_base` | CRISIS 1.0 · NEUTRAL 0.75 · BULL/EXBULL 0.5 · BEAR 0.5 if (dd52w>−25 ∨ cooling) else 0.0 |
| production MATURITY | **`postbull` with hard-block** (`pt_v23_audit_2014.py v23a none postbull 0 edge`) — *not* the dd52w ramps `smooth`/`gate15` |

Two corrections to the dispatch's framing:
- The two `0.3`s are **different things** (per-stock RSI cut vs cross-sectional share) — easy
  to conflate when reasoning about "the 30% gate".
- "Both parameters never backtested" is **half right**. `WASHOUT_GATE` and `capit_base` carry
  no tuning record. But `ew2d`/`postbull` thresholds are *self-admittedly* in-sample (code
  comment: "thresholds set on the audit events; NOT walk-forward validated"). So the sizing
  stack is **not a clean slate** — it has already absorbed researcher degrees of freedom, and
  anything I add sits on top of that.

## Q1 — Is 30% the right breadth threshold? **NO-GO (both clauses fail)**

Dose-response over all 2,994 usable days, forward-60-session equal-weight `ticker_prune` return:

| breadth quintile | n | mean fwd60 | CI90 |
|---|---|---|---|
| Q1 [0.000,0.004] | 601 | +4.00% | [−2.00, +9.36] |
| Q2 [0.004,0.011] | 597 | +6.27% | [+3.23, +9.83] |
| Q3 [0.011,0.025] | 598 | +4.86% | [+2.12, +8.01] |
| Q4 [0.025,0.060] | 599 | +3.11% | [+0.90, +5.42] |
| Q5 [0.060,0.836] | 599 | +4.02% | [+0.69, +7.04] |

**Spearman ρ = −0.0695, CI90 [−0.184, +0.066].** Clause 1 (monotone, ρ>0, CI excludes 0)
**FAILS** — there is no dose-response. Breadth is *not* a continuous predictor.

Threshold sweep (event-level, production clustering). Unconditional baseline = **+4.45%**:

| thr | fire days | events | event mean fwd60 | win | Δ vs 0.30 (CI90) |
|---|---|---|---|---|---|
| 0.20 | 149 | 29 | +6.83% | 79% | −1.14% [−6.52,+4.56] |
| 0.25 | 106 | 26 | +7.09% | 81% | −0.89% [−6.18,+4.92] |
| **0.30** | **81** | **18** | **+7.98%** | **83%** | — *(production)* |
| 0.35 | 68 | 14 | +7.86% | 79% | −0.12% [−7.39,+6.96] |
| 0.40 | 54 | 12 | +8.03% | 83% | +0.05% [−7.18,+7.01] |

Clause 2 (some threshold beats 0.30 by ≥3pp, CI excluding 0) **FAILS** — best alternative is
**+0.05pp** and every CI spans 0.

**The useful positive result.** Finer tail bins (exploratory addendum, flagged as such in the
prereg) show why: the effect is **a pure deep-tail step, not a gradient**.

| breadth | n | mean fwd60 |
|---|---|---|
| [0.00,0.02) | 1619 | +5.15% |
| [0.02,0.05) | 642 | +3.77% |
| [0.05,0.10) | 389 | +1.52% |
| [0.10,0.20) | 195 | +3.78% |
| [0.20,0.30) | 68 | +5.78% |
| **[0.30,1.01)** | **81** | **+10.39%** |

Nothing below 0.30 carries information; the payoff appears only in the top 2.7% of days.
**0.30 sits at the knee of a flat plateau (0.30/0.35/0.40 all ≈ +8%)** — the safest place a
threshold can be, because it is insensitive to its own exact value. Going lower (0.20/0.25)
measurably dilutes. This is the answer to "is 30% optimal": it is not *provably* optimal, but
it is provably **not a lucky pick**, and there is no better one to be had.

## Q2 — Is D_RSI<0.3 the best breadth metric? **NO-GO**

Matched fire-rate (81 days) against the production metric:

| metric | events | event mean | false-pos | Δ vs prod |
|---|---|---|---|---|
| **bd_rsi30** (prod) | 18 | +7.98% | 17% | — |
| %below MA200 | 4 | +11.00% | 25% | +3.02pp but **n=4** |
| %near 1M-low | 31 | +4.53% | 32% | −3.45pp |
| composite (rsi30 ∧ dd52w≤−10%) | 16 | +8.86% | **12%** | +0.88pp |

- `%below MA200` clears the 3pp bar on paper but produces **4 events in 12 years** — cannot be
  IS/OOS split, cannot have a CI. Fails the stated criteria; reporting it as a win would be
  the exact n-too-small error the standard exists to prevent.
- The **composite is directionally the most interesting** (best false-positive rate 12% vs 17%,
  highest mean among adequately-sampled variants) but **+0.88pp is far under the 3pp bar**.
  Logged as an idea, not a recommendation.
- No false-positive problem was found in the current metric. 83% of fires are followed by a
  positive 60-session return; the sector-specific-selloff worry the dispatch raised does not
  show up in the data.

## Q3 — Is the state→size table calibrated? **INCONCLUSIVE (deliberately not GO)**

Forward returns on all oversold days (breadth ≥ 0.10) vs the current size table:

| state | n days | mean fwd60 | CI90 | current size |
|---|---|---|---|---|
| CRISIS | 109 | +7.57% | [+1.30,+12.60] | **1.00** |
| BEAR | 60 | **−4.39%** | [−11.05,+2.55] | 0.50 |
| NEUTRAL | 138 | +6.68% | [+3.21,+10.03] | 0.75 |
| BULL | 35 | +12.57% | [+3.84,+20.31] | **0.50** |
| EXBULL | 2 | +24.33% | n/a | 0.50 |

Empirical rank EXBULL > BULL > CRISIS > NEUTRAL > BEAR vs size rank CRISIS > NEUTRAL > BEAR >
BULL > EXBULL. **My pre-registered GO criterion (a rank inversion, not a level shift) is
literally satisfied.** I am still not calling it GO, and that is a judgment call I want on
record: at the *event* level BULL has **n=2** and EXBULL **n=0**. Sizing BULL washouts up on
two observations is precisely the Wave1/H8a-tiebreaker reshuffle-luck failure. A criterion met
by a sample that cannot support it is a criterion that was written too loosely, not a result.

**dd52w depth — the one genuinely robust signal found, and still not wireable.** Among
oversold days, deeper prior drawdown predicts higher forward return, cleanly monotone:

| dd52w | n | mean fwd60 |
|---|---|---|
| ≤ −25% | 71 | +11.30% |
| −25..−15% | 78 | +8.28% |
| −15..−8% | 87 | +5.14% |
| −8..0% | 108 | +0.70% |

Robust where it can be tested: IS ρ=−0.248 / OOS ρ=−0.309 (same direction, similar size), and
it survives **within** state (CRISIS −0.581, NEUTRAL −0.407, BEAR −0.253) so it is not a state
proxy. **But at the decision-relevant event level it collapses**: among the 16 events
production actually deploys, deep-vs-shallow gap = +8.46% [+2.69,+14.35] full-sample, yet
**IS gap +0.26% (n_shallow=1) vs OOS gap +10.85%** — entirely an OOS phenomenon, unvalidatable
walk-forward. The phenomenon is real at day level; the number of CAPIT *decisions* it would
change is too small to prove it. → INCONCLUSIVE.

**Production's existing guards are already doing this work.** Applying the real production
chain to the 18 clusters, the two catastrophic events are both already neutralised:
- `2022-04-19` CRISIS, dd −8.0%, ret2y +83% → **postbull HARD-BLOCK**, size 0 (would have been
  −23.94% at full 1.00 size — by far the worst event).
- `2022-09-28` BEAR, dd −25.2% → **BEAR guard zeroes it**, size 0 (−22.09%).

Size-weighted mean fwd60 under production = **+11.59%**. Adding a continuous depth multiplier
on top = +12.85% (+1.26pp) — real but inside the noise, and OOS-only per above.

## Q4 — Wait for confirmation before firing? **NO-GO**

Waiting for breadth to roll over (2 consecutive declining sessions) fires all 18 events, mean
delay 5.9 calendar days: **+7.30% vs +7.98% at first touch, diff −0.68% [−5.69,+4.72]**.
Waiting costs the first days of the rebound and buys nothing. **Fire at first touch is correct.**

## Robustness — per-year leave-one-out (production gate)

All-event mean +7.98%. Dropping any single **positive** year leaves +6.73%..+8.35% — no year
carries the edge. The only large mover is dropping **2022** → +12.33% (that year: 3 events,
−13.79%), i.e. the edge is *dragged down* by one bad year, not propped up by one good one.
That is the opposite of the usual overfitting signature and argues the trigger is sound.

## Methodological note — a bug in my own first pass (worth recording)

The first run reported every CI as a collapsed point (`CI90=[mean,mean]`) for series with
n≤60. Cause: stationary block bootstrap with `block=60` and `N≤60` — the wrapped resample
`arange(s, s+60) % N` is just a **rotation of the entire array**, so every replicate has an
identical mean. Silent, and it looked like implausibly tight significance rather than an
error. Fixed by capping `block = min(block, N//4)`. **Any bootstrap CI in prior CAPIT jobs
using block ≥ N deserves the same check** — flagging for whoever revisits those.

## Bottom line for the fleet

Five prior jobs closed selection/exit/sizing-by-name. This job closes **trigger level, trigger
metric, and entry timing**. The remaining open item is not a parameter — it is that CAPIT's
edge rests on **~16 events in 12 years**, and no amount of re-slicing 16 events will produce a
statistically defensible refinement. The mechanism is sound (deep-tail breadth step, +8% mean
/ 83% win vs +4.45% unconditional, no single-year dependence); it is simply already at the
resolution limit of its own sample.

**Recommendation: stop parameter-tuning CAPIT.** Further edge, if any, has to come from a
source that generates more events, not from re-cutting these. Two honest leads, both under
the bar today and neither proposed for wiring: the dd52w-depth continuous multiplier and the
`dd52w≤−10%` composite gate (best false-positive rate observed, 12% vs 17%).

## Boundary respected

No production file touched. `pt_v23_audit_2014.py` / `golive_recommend_v23.py` unmodified —
verified read-only. Nothing here is proposed for wiring, so no quant-skeptic run was
triggered; a GO would have required one plus user sign-off before any change.

## Unreconciled minor discrepancy

I count **18 raw washout clusters** / **16 deployed** after postbull + BEAR guard, vs **14** in
the project record. The residual 2 are likely basket-emptiness or anomaly-gate exclusions I did
not replicate (I did not run the full basket builder). Flagging rather than papering over — it
does not affect any conclusion above (all are NO-GO/INCONCLUSIVE), but anyone quoting an event
count should reconcile it first.
