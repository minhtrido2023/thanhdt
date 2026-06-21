# EW5 full-NAV prodspec validation (2026-05-29)

Full 5-system prod-spec NAV (max_pos=12, sector cap {8:4}, hold 45d, stop −20%, T+1 open,
TC, liquidity caps, ETF parking, LAGGED book, overheat+SV_TIGHT filters, ensemble switch).
Baseline = canonical `ba_v11_unified_12y_sig.pkl` (fa_ratings 7-axis). EW5 = `ba_v11_ew5_sig.pkl`
(fa_ratings_ew5, drop health+valuation). Identical pipeline except the FA tier table.
Period 2014-01-01 → 2026-05-15, 50B/system.

| System            | CAGR base | CAGR EW5 |   ΔCAGR | Sharpe b→e | MaxDD base | MaxDD EW5 |
|-------------------|----------:|---------:|--------:|-----------:|-----------:|----------:|
| V1 V11+TQ34b      |   16.13%  |  15.65%  | **−0.48** | 1.14→1.13 |  −18.97%  |  −20.01% |
| V2 V12+TQ34b      |   18.53%  |  18.84%  | **+0.31** | 1.47→1.49 |  −16.41%  |  −16.24% |
| V3 V12+LIVE       |   18.53%  |  18.84%  | **+0.31** | 1.47→1.49 |  −16.42%  |  −16.24% |
| V4 V121_ENS+TQ34b |   20.58%  |  19.75%  | **−0.83** | 1.45→1.44 |  −18.55%  |  −17.64% |
| V5 V4+KellyQ2     |   21.99%  |  21.32%  | **−0.67** | 1.41→1.40 |  −18.41%  |  −18.41% |

VNI B&H: 11.42% / Sharpe 0.68 / DD −45.26% (both runs identical, control OK).

## Verdict: EW5 is NOT a deploy win — roughly NEUTRAL, mildly negative for flagships.
- CAGR: V1 −0.48, V4 −0.83, V5 −0.67 (flagships DOWN); V2/V3 +0.31 (marginal, within noise).
- Sharpe: flat everywhere (±0.02). DD: better V2/V3/V4, worse V1 — mixed.
- Net across 5 systems ≈ −0.27pp avg CAGR. No clear improvement.

## Why the signal-level test (+2.7-3pp) did NOT survive full NAV
The BA book is CAPACITY-CONSTRAINED (max 12 positions, sector cap 4 for financials). FA tier
is a GATE (C/D for MEGA/MOMENTUM) + E-exclusion, NOT the ranker — `ta` (technical score) ranks
which 12 names fill the book. EW5 reshuffles tiers, but the top-`ta` momentum names that
actually fill the 12 slots are largely the same regardless of FA-rank quality. The signal-level
test counted all ~10k BA-core signals equal-weight unlimited-capital; the portfolio realizes
only ~12-at-a-time by ta priority → the signal-pool mean improvement doesn't reach the book.

## Meta-lesson (3rd confirmation today)
Validation must climb ALL tiers, each more conservative: standalone IC → signal-level integrated
→ full capacity-constrained NAV. EW5 passed the first two, failed the third. Same pattern as the
bank sub-model (IC win → BA-core loss). The 7-axis FA layer is already well-fit for its gated,
capacity-bound role; "cleaner" rankings don't move the realized book.
