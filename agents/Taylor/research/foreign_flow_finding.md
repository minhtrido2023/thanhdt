# Foreign-flow (VNDirect finfo) as a lead signal for VNINDEX declines — NO-GO

Job `Taylor_20260723_082112`. Data: VNDirect finfo `/v4/foreigns` (Winston-verified source).
INDEX (VNINDEX, `type=INDEX`, HOSE) 2018-08-30→2026-07-23 (1,966 rows, FRESH to today);
VN30F front-month chained (`type=FU`, HNX) 2018-08→2025-12 (1,826 rows, **STALE** — feed stops
2025-12-18, cannot cover current episode). Method mirrors the VN30F-basis IC job
(`Taylor_20260723_073030`): Spearman IC full-history + episode overlays.
Scripts: `research/fetch_foreign_flow.py`, `research/analyze_foreign_flow.py`.

## IC (Spearman), INDEX, full 2018-2026 (n=1965)
| signal | fwd5 | fwd10 | fwd20 |
|---|---|---|---|
| nv (daily level) | +0.062 (p.01) | +0.008 | −0.027 |
| cum5/10/20 (N-day accum) | +0.04 / −0.03 / −0.06 | −0.04 / −0.09 / −0.10 | **−0.08 / −0.13 / −0.13** |
| nv_z20 (daily z-score) | **+0.111** (p.00) | +0.086 | +0.063 |

**Signs are inconsistent across constructions** (level ~0, accumulation NEGATIVE, z-score POSITIVE)
— hallmark of coincidence leakage + noise, not a coherent structural lead. Accumulation being
negative means "more foreign buying over past N days → LOWER future returns" (momentum-chasing /
mean-reversion artifact), the opposite of a "foreign selling warns of decline" thesis.

- Coincidence: Spearman(netVal_t, ret_t) = **+0.184** (p=2e-16) — flow is strongly SAME-DAY, i.e.
  largely re-encodes price info already in the system.
- The one apparently-real signal, nv_z20 fwd5 +0.111, **survives** controlling for same-day ret0
  (partial +0.100, p=1e-5) → a genuine but tiny **fwd5-only** within-week co-movement, decays by
  fwd20. Wrong horizon/direction for drawdown early-warning.

## Structural outflow makes level/accum signals useless for timing
Foreign is NET SELL on **61%** of all days (2024-26: **70%**, mean **−466 bn/day**). It's always-on,
not a timing event. **Apr01→May18 2026: VNI RALLIED +13.2% to its peak while foreigners net-sold
−22,553 bn (−22.5 tn VND), selling on 84% of those days.** A "foreign selling" rule would have
exited the entire final rally leg.

## Current episode — foreign flow gave NO early warning (the decisive test)
nvz (daily sell-surprise) at the pivots:
- **05-18 peak**: nvz **+0.36** (mild BUY surprise — foreigners NOT distinctively selling at the top)
- **07-17 accel-down pivot**: nvz −0.34 (unremarkable)
- **07-20** (VNI −44 pts): nvz **+0.35** (foreign net-BUY surprise ON the crash day)
- **07-22** (VNI −62 pts): nvz −1.63 — the only sell-surprise, but AFTER two crash days (lagging)

The −617 bn on 05-18 was milder than many surrounding days (−3504 on 04-15, −3174 on 05-22). It did
NOT distinguish the peak. Same conclusion as the VN30F-basis job: the current selloff is
**domestic / cash-led**, foreigners were near-zero to net-buyers on the worst days.

## As an explicit decline-warning: ZERO discrimination
Signal = foreign sell-surprise nvz<−1.5 (n=128): fwd20 mean **+0.45%** vs unconditional +0.64%;
**P(fwd20<0 | signal) = 0.41 = unconditional 0.41**. nvz<−2.0 (n=55): fwd20 **+0.99%** (foreign
panic-selling precedes RECOVERIES — contrarian). No threshold separates declines from base rate.

## Independence & verdict
Not an independent channel — strongly coincident with price (+0.184), same domestic-led read as the
basis job. **NO-GO** — 5th signal killed today (basis IC~0, breadth-momentum wrong-sign, rate-signal
= existing Pillar-A, foreign flow now). DT5G production unchanged. The residual +0.10 fwd5 z-score
co-movement is real but too weak, fwd5-only, and useless for the drawdown-warning use case; not worth
routing to quant-skeptic.
