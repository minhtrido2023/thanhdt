# Pre-register — Stage 7 (continuous vs discrete LAG gate), job Taylor_20260723_135623

Written BEFORE running any NAV. Extends prior-job PREREGISTER.md.

## Hypotheses under test
- H-cont: a CONTINUOUS market-feature gate/sizing beats the discrete DT5G half-size
  gate (prior winner c4: mult 0.5 if dt5g in {1,2} else 1.0) on walk-forward risk-adjusted
  terms AND is robust (IS not negative, LOO flat, DSR>0.95).
- Prior (from Q2 univariate): breadth best predicts LAG drift LEVEL but its IS IC is
  NEGATIVE (−0.049) while OOS is +0.212 → I EXPECT breadth-based continuous gates to look
  strong OOS but fail IS (regime-carry), i.e. NOT beat c4 on robustness. Recording this
  prediction so a positive OOS result is not mistaken for a robust edge.

## Candidate sizing multipliers (mult in (0,1], applied to POS_PCT at entry)
Frozen list (N_trials for DSR = 7 incl. baseline):
1. baseline            : mult=1
2. disc_c4 (prior win) : 0.5 if dt5g_state in {1,2} else 1
3. cont_breadth        : 0.5 if breadth < 0.40 else 1        (CAPIT oversold level, fixed)
4. cont_liq            : 0.5 if liq_ratio < 1.0 else 1
5. cont_roc            : 0.5 if roc20 < -8 else 1             (fast-decline price gate)
6. cont_combo          : 0.5 if (breadth<0.40 or roc20<-8) else 1
7. cont_smooth_breadth : clip(0.40 + breadth, 0.40, 1.0)     (smooth, no threshold pick)

## Decision rule (unchanged discipline from prior job)
- PASS to recommend-as-candidate only if: CAGR give-up ≤ ~0.5pp vs baseline, Sharpe &
  Calmar improve, **IS Sharpe NOT lower than baseline** (robustness), OOS improves,
  LOO-by-year edge does not come from 1-2 years, DSR>0.95.
- Report the fresh-drawdown question explicitly: does the gate fire in 2026 H1 (unlike
  DT5G c4 which stayed dormant)? At what CAGR cost?
- Fail any of the above → REJECT, do not wire, keep c4/c5 as the standing candidate.
- Self-check 0 VND (min NAV positive, no negative cash) required for every variant.

## Frozen params
Engine = lag_common.simulate_nav (canonical LAG spec). Events = lag_events_cont.pkl.
IS=2014-19, OOS=2020-26. sr0 for DSR from N_trials=7.
