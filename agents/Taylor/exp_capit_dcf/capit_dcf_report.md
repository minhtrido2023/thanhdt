# CAPIT basket selection — DCF secondary filter/tiebreaker (R&D)

Events: 16 | pool-rows: 73 | K=5 slots | primary horizon 6M

## DCF coverage on CAPIT pools
- computable (ok): 62/73 = 84.9%
  - N/A: normalized 3y FCFE <= 0 (capex > CFO, heavy reinvestment) — no positive FCFE — 7
  - N/A: CF_OA_3Y <= 0 (operating cash gate fails) — DCF not meaningful — 4
- of computable: RICH(MoS<0) 27 | CHEAP 35

## Per-event basket forward return (equal-weight, %)
```
variant      BASE   HARD   SOFT  HARD-BASE  SOFT-BASE
event                                                
2014-05-09  40.69  40.69  40.69       0.00       0.00
2015-08-25   5.97  -1.40   5.97      -7.37       0.00
2016-01-19  44.85  49.37  44.85       4.52       0.00
2018-05-29  27.09  27.09  27.09       0.00       0.00
2018-07-06  17.53  17.53  17.53       0.00       0.00
2020-02-04  11.86  20.88  11.86       9.02       0.00
2020-03-12  44.46  43.55  43.55      -0.91      -0.91
2020-07-28  45.27  45.27  45.27       0.00       0.00
2022-04-20 -10.74 -10.74 -10.74       0.00       0.00
2022-06-16 -11.26 -11.26 -11.26       0.00       0.00
2023-10-31  41.75  41.75  41.75       0.00       0.00
2024-04-19  11.33  11.33  11.33       0.00       0.00
2024-08-06   0.83   0.83   0.83       0.00       0.00
2025-04-04   7.81   8.14   7.81       0.33       0.00
2025-10-21  12.71  12.71  12.71       0.00       0.00
2026-03-10    NaN    NaN    NaN        NaN        NaN
```

## Pooled summary (mean of per-event basket returns)

**2M**
```
FULL         n=16 BASE=   6.58% HARD=   6.53% SOFT=   6.48%  | dHARD=-0.04pp dSOFT=-0.10pp
IS 2014-19   n= 5 BASE=  11.55% HARD=  10.67% SOFT=  11.55%  | dHARD=-0.88pp dSOFT=+0.00pp
OOS 2020+    n=11 BASE=   4.32% HARD=   4.65% SOFT=   4.18%  | dHARD=+0.34pp dSOFT=-0.14pp
```

**6M**
```
FULL         n=16 BASE=  19.34% HARD=  19.72% SOFT=  19.28%  | dHARD=+0.37pp dSOFT=-0.06pp
IS 2014-19   n= 5 BASE=  27.23% HARD=  26.66% SOFT=  27.23%  | dHARD=-0.57pp dSOFT=+0.00pp
OOS 2020+    n=11 BASE=  15.40% HARD=  16.25% SOFT=  15.31%  | dHARD=+0.84pp dSOFT=-0.09pp
```

**12M**
```
FULL         n=16 BASE=  29.68% HARD=  33.18% SOFT=  32.49%  | dHARD=+3.51pp dSOFT=+2.81pp
IS 2014-19   n= 5 BASE=  29.70% HARD=  27.88% SOFT=  29.70%  | dHARD=-1.82pp dSOFT=+0.00pp
OOS 2020+    n=11 BASE=  29.67% HARD=  36.13% SOFT=  34.04%  | dHARD=+6.47pp dSOFT=+4.37pp
```

## Bite
- HARD differs from BASE on 5/16 events
- SOFT differs from BASE on 1/16 events
- HARD: n_diff=5 mean_delta=+1.12pp t=0.41 wins=3/5
- SOFT: n_diff=1 — no testable sample

## Name-level: is DCF MoS informative INSIDE a CAPIT pool?
- Spearman(MoS, fwd6M) = +0.207 on n=58 computable names
- mean fwd6M: RICH +9.74% (n=24) | CHEAP +22.76% (n=34)
- mean fwd6M of DCF-N/A names: +32.67% (n=10) — sanity check that N/A-as-pass is not silently harmful
---

## CRITICAL — event-clustered inference reverses the naive name-level spread

The pooled `CHEAP +22.8% vs RICH +9.7%` (n=58) above is **not valid inference**: names inside one
washout basket are near-perfectly correlated (same market rebound), so the effective sample is the
16 EVENTS, not 58 names. Recomputed WITHIN each event (the only comparison free of event-composition
bias), on the 10 events that contain both a CHEAP and a RICH name:

```
event       n_cheap n_rich  spread(CHEAP-RICH, pp)
2014-05-09        2      1   +30.81
2015-08-25        4      3   -37.34
2016-01-19        2      1   -11.54
2020-02-04        3      1   +36.08
2020-03-12        5      1   +12.83
2022-04-20        1      4   -40.90
2022-06-16        1      2   -26.09
2024-04-19        2      4    -4.83
2024-08-06        1      3   -16.40
2025-04-04        2      2    -7.89
mean -6.53pp | median -9.71pp | wins 3/10 | t=-0.78 | sign-test p=0.34
```

The within-event spread is **NEGATIVE** — i.e. inside a CAPIT pool, DCF-RICH names did marginally
BETTER, not worse. The naive +13pp pooled gap was a Simpson's-paradox artifact (events with a higher
share of DCF-cheap names happened to be the events with the largest market-wide rebound).

## Mechanism — why a second value filter cannot bite here

Pool size at the 16 events: median 4, range 2-7. **11/16 events have pool <= K=5 slots.**
The existing quality gate (ROE_Min5Y>=0.12 AND ROIC5Y>=0.10 AND FSCORE>=6 AND ADV>=2B) plus
pb_z<-1 already leaves fewer candidates than there are slots. Trace of every event where HARD bites:

```
2015-08-25 pool=7 dropped VNM  -> SHRINK 5->4 (no replacement)
2016-01-19 pool=4 dropped VNM  -> SHRINK 4->3 (no replacement)
2020-02-04 pool=4 dropped SAB  -> SHRINK 4->3 (no replacement)
2020-03-12 pool=6 dropped SAB  -> substituted CVT   <-- the ONLY true substitution in 12 years
2025-04-04 pool=5 dropped CTR,TNG -> SHRINK 5->3 (no replacement)
```

4 of 5 bites are pure **basket shrinkage**: the filter trades diversification for concentration
without upgrading a name. That is a risk INCREASE at the moment of maximum uncertainty (a washout),
paid for an edge that measures as zero. This is a structural argument independent of the statistics
-- widening the pool, not filtering it, is the only place a DCF signal could add anything.

## On the motivating cases (SAB / DHC)

- **SAB** is the intuition behind the request (pb_z-cheap, DCF-rich -34%). It appears at 2 events
  (2020-02-04, 2020-03-12); excluding it helped once and the other bite-events cut the other way.
  n=2 is an anecdote, not a base rate.
- **DHC** (pb_z rank 7, DCF cheap +54.7%, dropped only for lack of slots) is a **slot-cap** question,
  not a DCF question. Nothing in this study addresses whether K should be >5; that is a separate,
  cleanly testable ask if the user wants it.

## Why no full pt_v23 NAV backtest was run

Pre-registered plan called for it. It was NOT run, deliberately: the variants differ from BASE on
only 5/16 events (SOFT: 1/16), the event-level delta is t=0.41 / n_diff=5, and the underlying
name-level signal is negative under correct clustering. A full NAV run would return a CAGR/Sharpe
number, but that number would be one noise realization driven by 4 shrinkage events -- reporting it
would manufacture false precision and invite selecting the variant that happened to land well.
DSR is likewise not reported: no variant reached the selection stage, so there is nothing to deflate.
Stating this explicitly rather than producing an unfalsifiable number.

## VERDICT

**NO-GO for both (a) HARD FILTER and (b) SOFT TIEBREAKER. Not even PAPER-FIRST.**

- (a) HARD: no measurable edge (t=0.41 on 5 bites); mechanically converts to basket shrinkage 4/5
  times -> strictly increases concentration risk. NO-GO.
- (b) SOFT: bites 1/16 events -> a no-op that adds a code path and a data dependency for nothing. NO-GO.
- (c) BASE (pb_z only): retained.

Paper-trading is not recommended either -- paper cannot resolve this. At ~1.3 CAPIT fires/year, the
5 bite-events took 12 years to accumulate; a paper period would generate 0-1 observations.

**Confirmed sound (no change needed):** treating DCF N/A as pass-through was the right call and is
now measured -- the 10 N/A names returned +32.7% fwd-6M, the best of the three groups. Auto-rejecting
them (PVT/SIP-type capex-heavy infra) would have been the single most damaging variant.

**The one real finding worth keeping:** the CAPIT pool is slot-constrained, not selection-constrained
(11/16 events have fewer candidates than slots). Any future work on CAPIT basket quality should
target pool BREADTH (universe/quality-gate width, or K), not adding filters on top.
