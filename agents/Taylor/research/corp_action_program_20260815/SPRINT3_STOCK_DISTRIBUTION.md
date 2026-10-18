# Sprint 3 — stock dividends and bonus shares

## Executive verdict

**Ex-date: DESCRIPTIVE ONLY. AIS: RISK / DUE-DILIGENCE. No alpha candidate.**

The primary ex-date outcome is statistically null after multiplicity correction and does not
replicate out of sample. Short-run AIS returns are negative in the full sample, but the OOS
T+20 confidence interval contains zero and AIS lacks an individual-stock matched control.
Positive pretrend/placebo and persistent prior outperformance rule out a causal reading.

## Sample and lineage

- 1,914 stock-distribution ex events have an exact price session; 862 events / 333 tickers pass
  P-CORE, ratio ≤200%, trading and contamination filters.
- Components are 1,277 stock-dividend rows, 514 bonus rows and 123 same-day mixed events before
  P-CORE filtering. SQL totals match the canonical ledger ratios on 100% of observations.
- 2 events above 200% are excluded and disclosed.
- AIS audit: 1,899 Tier-A links, 2 Tier-B links, 13 unlinked, and 242 cross-source conflicts.
  After P-CORE, conflict/overlap and price coverage, AIS confirmatory N is 736 events / 317 tickers
  (721 observations have T+20).

## Ex-date results

| horizon | N | mean BHAR | 95% month-block CI | raw p | Holm p |
|---:|---:|---:|---:|---:|---:|
| 5 | 862 | -0.508% | [-0.892%, -0.131%] | .0074 | .0296 |
| 10 | 862 | -0.537% | [-1.094%, +0.005%] | .0520 | .1356 |
| **20 primary** | **862** | **-0.575%** | **[-1.337%, +0.175%]** | **.1364** | **.1364** |
| 60 | 832 | -1.485% | [-2.926%, -0.038%] | .0452 | .1356 |

The T+20 median is -1.583% and 43.9% of events are positive, but the mean CI contains zero.
The one-to-one matched-control estimate is -0.410% on 611 events, CI
[-1.463%, +0.581%], also null. Ratio has no association with T+20 return in the declared
two-way-clustered regression (`t=-0.28`).

Stability rejects a general effect:

- IS 2014–2019: -1.159%, CI [-2.612%, +0.300%].
- OOS 2020+: -0.299%, CI [-1.176%, +0.537%].
- Stock dividend: -0.342%, CI [-1.271%, +0.577%].
- Bonus: -1.705%, CI [-3.164%, -0.228%], but N=192 is below the locked 200-event floor and
  therefore cannot support a subgroup claim.
- Mixed events: N=51, also below the floor.
- Leave-one-year-out does not flip the overall sign but still demonstrates
  material time variation.

## Selection diagnostics

- Placebo T-40…T-20: **+1.084%**, CI [+0.218%, +2.063%].
- Pretrend T-21…T-1: **+2.161%**, CI [+1.394%, +2.944%].
- Extra far baseline T-250…T-230: **+1.890%**, CI [+1.014%, +2.775%].

The event firms were already outperforming before the event, followed by relative cooling.
Neither the ex-date estimate nor the short negative drift can be called the causal effect of the
distribution.

## Nominal price and liquidity

The raw-price reconstruction gate passes: among 785 stable `Price/Close` ratios, **98.7%** match
the theoretical `(1+ratio)` factor within ±1%. Reconstructed ex-date prices close on average
2.408% above the mechanical reference, CI [+2.140%, +2.702%]. This remains a descriptive
microstructure result because the exchange sets the reference price.

Median trading value changes by `DLOG_ADTV=-0.104`, approximately a 9.9% decline, CI on log
change [-0.198, -0.008]. This does not support the simple story that a lower nominal price
automatically improves liquidity. More importantly, the coefficient on distribution ratio is
null (`t=-0.11`), so the aggregate decline is not evidence of a dose-response mechanism.

## Additional-listing (AIS) results

| horizon | N | mean BHAR | 95% month-block CI | Holm p |
|---:|---:|---:|---:|---:|
| 5 | 735 | -0.492% | [-0.885%, -0.092%] | .0396 |
| **20** | **721** | **-0.988%** | **[-1.787%, -0.202%]** | **.0396** |
| 60 | 703 | +0.609% | [-0.885%, +2.273%] | .4562 |

The association is short-lived: T+60 is null. T+20 is -1.321% in IS but -0.834% with CI
[-1.829%, +0.194%] in OOS. Tier-A-only is similar (-0.965%), which supports linkage robustness,
not causality. AIS date availability/tradability was not proven point-in-time and no AIS matched
control was run; the correct label is `RISK / DUE-DILIGENCE`.

## Limitations and permitted use

- Announcement reaction remains forbidden because `public_date` is not proven PIT.
- Current ICB and no PIT market cap leave residual confounding; see `SPRINT3_DEVIATIONS.md`.
- The adjusted series is fit for total-return comparisons, but the raw adjustment factor fails
  its own validation gate.
- No cost screen is run because entitlement and feasible trade timing differ between ex and AIS.
- The results may support an analyst warning that supply-arrival windows deserve scrutiny. They
  do not support buying/selling automatically, production wiring or a live gate.

## Reproducibility

Run `sprint3_build.py` (read-only BigQuery), then `sprint3_analyze.py`, `sprint3_plots.py`, and
`selfcheck_sprint3.py`. Machine-readable results and panels are under `out3/`. The design was
committed before outcomes in `40d91b74`.
