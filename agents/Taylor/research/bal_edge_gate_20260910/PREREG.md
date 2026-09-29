# PREREG — BAL edge-gate (AMH #1), job `Taylor_20260910_131906`

**Written 2026-09-10, BEFORE any backtest leg was run.** Steps 1 and 2 of this job were already
complete when this was written (their results are cited below as design inputs); step 4 had not
been started. Commit/mtime of this file predates every `*.log` in this directory.

## 0. What steps 1-2 already killed (so this prereg does not re-propose them)

- **A LAG-symmetric realized-trade gate on BAL is structurally impossible.** BAL is a BULL-only
  book (every `TIER_BAL` buy tier requires `state5 IN (4,5)` in `signal_v11_sql.py`); DT5G has
  zero BULL/EXBULL sessions in 2014/2015/2016/2019/2022/2023. Its cohort arrives in 10 episodes,
  with gaps up to 25 months. Read causally at the open of each signal episode, a trailing-12M
  `mean12` gate sees `n12_av = 0` in 3 of 6 clusters (staleness 819 and 688 days) and, where it
  does see something, ranks the episodes backwards. Not a tuning problem.
- **A fwd-1M "fast" IC does not buy the 3 months back.** Median wall-clock lead over the
  production fwd-3M verdict is 1 month against a 2-month mechanical floor from publication lag
  alone — i.e. −1 month in signal-month terms — at a cost of 30% unconfirmed alarms (8/27) and
  3 missed real alarms.

## 1. Hypothesis (H1)

When the production momentum edge verdict is **FLIPPED**, BAL's momentum book earns less per unit
of exposure, so cutting BAL exposure while that verdict is active improves the *risk* profile of
the combined book (MaxDD, Calmar) without materially changing CAGR.

## 2. Gate definition — every threshold inherited, zero free parameters

- **Series:** `mom_200` / scope `ALL`, monthly cross-sectional Spearman IC vs `fwd_3m`, from
  `data/edge_panel.csv` — the exact series `edge_health_monitor.py` already publishes daily.
- **Verdict:** production `edge_health_monitor.classify()` → `FLIPPED` requires
  `|t| >= T_SIG (2.0)`, `sign(recent12) != sign(full)`, `|recent12| >= MAG_MIN (0.015)`.
  `T_SIG` and `MAG_MIN` are pre-existing production constants (set 2026-06, not by me).
- **One causality change vs production:** the `full` reference mean is EXPANDING to the evaluation
  date, not full-sample. Production's full-sample comparison is fine for reading a dashboard today
  but peeks at the future when dating a historical alarm.
- **Availability clock:** the verdict for signal month `m` is applied from month `m+3` onward.
  No exception, no interpolation.
- **I am NOT choosing a numeric threshold.** LAG's `mean12 >= 4%` came from its own 2026-06-10
  edge-cycle study (trough = 3rd pctile, 5/5 troughs recovered >= +3.9% within 6M). No equivalent
  study exists for BAL, so picking a number here would be a grid search wearing a prereg's clothes.
  The pre-committed threshold is the production verdict label itself.

## 3. Action when the gate is active — ONE axis, declared now

**Cut BAL slot count `MAX_POS_V11` 12 → 6** on gate-active sessions. Everything else byte-identical.

Why this and not "nới parking custom30V": bull-parking is a separately-measured feature already
judged non-robust (+0.49pp CAGR / −0.03 Sharpe @50B, default OFF; `results_registry.md` explicitly
warns not to lower a threshold to deploy it). Using it as the gate's action would confound the
gate with a mechanism that has its own open verdict. Slot count is the same shape as the existing
EXBULL momentum suppression (fewer momentum positions in a hostile phase), single-axis, reversible.

12 → 6 is the natural halving, matching the LAG gate's own 0.65 → 0.50 fallback-to-neutral shape.

## 4. N — independent events, stated before the result

**N = 4.** The gate is active during exactly 4 DT5G BULL/EXBULL episodes 2014-2026:

| episode | window | sessions | gate-active |
|---|---|---|---|
| 6  | 2020-10-06 → 2021-02-18 | 92 | 100% |
| 8  | 2021-03-05 → 2021-07-23 | 98 | 40% |
| 14 | 2024-01-24 → 2024-05-13 | 70 | 100% |
| 20 | 2026-01-28 → 2026-02-12 | 12 | 100% |

213 gate-active BULL sessions out of 482 BULL sessions total, across 13 calendar years.

**Declared consequence, before running anything: walk-forward IS(2014-19)/OOS(2020+) cannot
adjudicate this rule — the IS window contains ZERO gate-active episodes.** All 4 events are in
OOS. I will still report the IS/OOS split (it must show IS Δ ≈ 0 by construction; if it does not,
that is a harness bug, not an edge), but per `quant-research` skill §5 the small-N substitute is
the governing test: **leave-one-episode-out + per-year LOO**, and I am declaring that substitution
here rather than presenting IS/OOS as if it decided anything.

With N=4, a sign test cannot reach p<0.05 even if all 4 go the same way (p = 0.125). **No p-value
in this study can pass a conventional bar. Any GO would have to rest on causal mechanism +
dose-response shape, not on significance.**

## 5. Expectation, declared before the result

- **ΔCAGR ≈ 0**, and I will not treat a positive ΔCAGR as support. The objective is surviving a bad
  edge phase, not earning more. This mirrors the standing AMH caveat: the only AMH-inspired
  directional signal ever tested in this fleet (ecology mood) was REFUTED walk-forward.
- Success would look like: **MaxDD improves, Calmar improves, CAGR loss ≤ ~1pp, and the direction
  holds in ≥3 of 4 leave-one-episode-out refits and ≥10 of 13 per-year LOO refits.**
- Failure looks like: CAGR loss > 1pp, or MaxDD not improving, or the sign flipping when any single
  episode is dropped.

## 6. Legs to run

Pinned environment, identical to the R3 pin (`research/lag_repin_20260803/run_repin.sh`):
`BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate`, `BQ_CACHE_THREADS=1`, `NAV_TOTAL_B=50`,
`ETF_LIQ=custompitg`, `BASKET_WT=namecap`, `BASKET_SELECT=yieldcombo`, `PARK_STATES=3:0.7`,
`AUDIT_END=2026-06-19`, `$DNA_PYEXE`, `pt_v23_audit_2014.py v23a none postbull 0 edge`, `EXP_TAG`
set on every leg so no canonical CSV is ever the target (`coding_guidelines.md` §8).

| leg | config | purpose |
|---|---|---|
| `ctrl` | production, untouched | must reproduce the pin **28,86% / 1,90 / −17,8% / 1,62 / 1.178,01B** |
| `g6`   | **pre-committed**: slots 12→6 while gate active | the decision leg |
| `g8`, `g10`, `g4`, `g0` | slots 12→8 / 10 / 4 / 0 | dose-response ladder ONLY (§10). Reported for shape; **not eligible to be selected** |
| `plac` | same rule, gate signal replaced by a fixed calendar mask of equal length/placement | separates "the gate knows something" from "less exposure in 2020-21 and 2024" |

**N_trials = 6 configs compared.** Per `quant-research` §13, DSR/PBO are required only if a
specific config is recommended for wire; the pre-committed config is fixed in advance, so a
"wire `g6`" recommendation would still need DSR/PBO — I will run them in that case and say so.

## 7. Stopping rule

If `g6` fails any of the §5 success conditions, the answer is **NO-GO** and I will not go looking
through the ladder for a variant that passes. The ladder exists to check monotonic shape; a
non-monotonic ladder is itself evidence against the rule.

## 8. Production untouched

No production file is edited. The treatment engine is a `sed`-generated copy of
`pt_v23_audit_2014.py` differing by exactly the documented gate lines. `git status` on production
files verified clean before and after.
