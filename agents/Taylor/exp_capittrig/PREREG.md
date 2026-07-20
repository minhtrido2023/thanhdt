# PREREG — CAPIT trigger + state-conditional sizing (job Taylor_20260720_170234)

Written BEFORE any result inspected. Multiple-testing discipline per 2026-07-05 standard.

## Ground truth verified in code (pt_v23_audit_2014.py, NOT assumed)

- `WASHOUT_GATE = 0.30` — **hard-coded module constant, line 577**, NOT env-configurable.
  Sweeping it requires a patched copy; production untouched.
- Breadth definition (line 929): `AVG(CASE WHEN p.D_RSI<0.3 THEN 1 ELSE 0 END)` over
  `tav2_bq.ticker_prune` where `Close_T1>0`, grouped by day. **NB the two 0.3's are
  different things**: per-stock RSI cut vs cross-sectional share threshold.
- Event clustering: washout days with `>=30` calendar-day gap start a new event; `d0` =
  FIRST day of cluster. Fill at T+1 open → causal, no look-ahead in the trigger itself.
- `capit_base(state, dd52w, vn_cooling)` (line 580):
  CRISIS(1)=1.0 · NEUTRAL(3)=0.75 · BULL(4)/EXBULL(5)=0.5 ·
  BEAR(2)= 0.5 if (dd52w > -25 OR vn_cooling) else 0.0 · fallback 0.5
- `grind` halver: any washout day 20–90 sessions back → `size *= 0.5`.
- Maturity multiplier (`ew2d`/`postbull`/`smooth`/`gate15`) applied on top.

**Prior-testing status**: `MATURITY` variants and the postbull/ew2d gates WERE tuned on the
audit events (code comments state "In-sample ... NOT walk-forward validated"). The
`WASHOUT_GATE=0.30` level and the `capit_base` state table carry **no such comment and no
registry entry** — treating them as un-swept is consistent with the code, and I flag that
`ew2d`/`postbull` thresholds are already admitted in-sample (so the sizing stack is *not*
a clean slate; it has absorbed prior researcher degrees of freedom).

## Design — why NOT a per-event comparison

Changing the gate changes the event SET itself (N=14 at 0.30). Comparing event sets of
different size/composition is not a fair test. Instead: **dose-response over all observed
days** — for every trading day 2014→2026 measure breadth (causal) and forward return.
If the CAPIT thesis ("buy when breadth washes out") is real, forward return must rise
monotonically with oversold breadth, and the 0.30 level should sit near where the
relationship turns on. This uses ~3000 days, not 14 events.

**Honest N**: forward-60d windows overlap → effective independent N ≈ 3000/60 ≈ 50.
All significance via **stationary block bootstrap (block=60 sessions)**, never i.i.d. t-stats.

## Response variables (fixed now)

- Primary: `fwd60_ew` = forward 60-session equal-weight return of `ticker_prune` (matches
  CAPIT_HOLD=60 and equal-weight basket construction).
- Secondary: `fwd60_vni` (VNINDEX) as a megacap-lens robustness check.
- Selection is NOT modelled — 5 prior jobs established name-selection is noise, so a
  market/EW proxy is the appropriate stand-in for the timing decision.

## Pre-registered trials — N_trials = 14 total

**Q1 — gate level (5 trials)**: breadth thresholds {0.20, 0.25, **0.30 baseline**, 0.35, 0.40}.
**Q2 — breadth metric (4 trials)**: {D_RSI<0.3 (baseline), %below MA200, %at-52w-low-decile,
composite = D_RSI<0.3 gate ∧ VNINDEX dd52w ≤ −10%}.
**Q3 — state sizing (3 trials)**: {current table (baseline), forward-return-implied table,
adding dd52w-depth term}.
**Q4 — confirmatory timing (2 trials)**: {fire at first touch (baseline), wait for breadth to
turn down ≥2 consecutive sessions from its cluster peak}.

No knob outside this list will be swept. If I want a 15th, it gets reported as an
exploratory addendum, not folded into a GO claim.

## GO / NO-GO criteria (fixed now, per question)

**Q1 GO** requires ALL:
1. Dose-response monotone: mean `fwd60_ew` non-decreasing across breadth quintiles
   (Spearman ρ > 0, block-bootstrap 90% CI excludes 0).
2. Some non-baseline threshold beats 0.30 on mean `fwd60_ew` by ≥ **3pp** AND the
   block-bootstrap 90% CI of the *difference* excludes 0.
3. The winner holds in BOTH IS (2014–19) and OOS (2020+) — same sign, no reversal.
4. Winner is not a lone-year artifact: per-year leave-one-out keeps the improvement > 0.

**Q2 GO**: an alternative metric raises mean `fwd60_ew` at its own matched fire-rate by
≥3pp with CI excluding 0, AND reduces false-positive rate (fires followed by negative
fwd60) vs baseline, AND holds IS+OOS.

**Q3 GO**: forward returns conditioned on state at fire-time show ordering that
*contradicts* the current 1.0/0.75/0.5 table by more than a monotone rescaling — i.e. a
rank inversion, not just a level shift. A level shift alone = NO-GO (it's leverage, not
information).

**Q4 GO**: confirmatory wait raises mean `fwd60_ew` by ≥3pp with CI excluding 0 AND does
not drop more than 2 of the 14 historical events (a filter that removes half the events
is a different strategy, not a timing refinement).

**Any question failing any of its clauses → NO-GO for that question.** INCONCLUSIVE
reserved for: correct sign but CI spanning 0 with < 6 effective independent observations.

## Self-check applicability

This is a dose-response / conditional-return study on observed data — **no NAV path is
simulated, so "self-check 0 VND" does not apply** (same posture as the 4 prior CAPIT jobs).
If any question reaches GO, the follow-up NAV backtest WILL carry the 0-VND self-check
before any wire proposal.

## Boundary

R&D only. No edit to `pt_v23_audit_2014.py` / `golive_recommend_v23.py`. Any GO routes
through quant-skeptic + user sign-off before wiring.
