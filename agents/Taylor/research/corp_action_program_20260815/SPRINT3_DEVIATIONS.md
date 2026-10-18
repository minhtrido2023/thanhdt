# Sprint 3 deviations and trial ledger

The pre-registration is immutable at commit `40d91b74`. These decisions were made after it.

## D1 — PIT market cap omitted

The Sprint 3 extraction did not materialize a point-in-time shares-outstanding field for the
stock-distribution sample. Consequently market cap was not silently proxied with a current or
restated field: it was omitted from both regressions and matching. Matching used the three
available pre-outcome features (`ADV60`, 6-month momentum, `rvol60`) and current ICB level 1.
This weakens confound control and caps every verdict at `RISK/DUE-DILIGENCE`.

## D2 — control contamination enforced locally

Candidate ranking used no future outcome, but the BigQuery candidate extract did not apply the
event-free condition. Before assignment, the analyzer removed any candidate with an actionable
price-adjusting event within ±21 calendar days using the canonical Sprint 1 ledger. Greedy
assignment then enforced no replacement within each event month. This implements the intended
rule at a different layer; it does not change the estimand.

## D3 — far-baseline diagnostic is an extra trial

After the pretrend/placebo were computed, the analyzer also measured the same 20-session outcome
roughly one trading year earlier (`T-250..T-230`). This is not confirmatory and is not included in
the two Holm families. It is reported because it is +1.890% [1.014%, 2.775%], showing persistent
selection of prior outperformers and further weakening causal interpretation.

## D4 — no matched-control AIS estimator

The matched-control extract was anchored at ex-date, not AIS. AIS retains the point-in-time EW
benchmark, linkage audit, IS/OOS and Tier-A-only tests, but no individual-stock matched control.
Therefore even its Holm-significant 5/20-session association cannot be labelled causal.

## Executed trial ledger

- Confirmatory ex family: 4 horizons, Holm-adjusted.
- Confirmatory AIS family: 3 horizons, Holm-adjusted.
- Declared diagnostics: IS/OOS, subtype, mixed events, ratio/liquidity regression, liquidity
  change, placebo, pretrend, leave-one-year-out, P-WIDE, matched ex control, AIS Tier A.
- Additional post-registration diagnostic: far baseline (D3), explicitly excluded from claims.

No threshold, horizon, subgroup or matching caliper was changed after inspecting outcomes.
