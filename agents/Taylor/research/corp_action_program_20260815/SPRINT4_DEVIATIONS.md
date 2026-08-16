# Sprint 4 deviations and trial ledger

The preregistration is immutable at commit `03962aaf`.

## D1 — no PIT market-cap control

Point-in-time shares outstanding was not materialized for this panel. Current/restated shares
were not substituted. Regressions and matching use pre-event ADV, momentum and volatility plus
current ICB level 1. The missing PIT size control caps interpretation at descriptive/risk level.

## D2 — Tier B AIS fallback not materialized

The AIS panel uses issuance `listing_date` (Tier A) and cross-checks against AIS rows. Issuances
without listing date were not recovered through the volume-matched Tier B fallback. This is a
conservative coverage loss, not a date substitution. The report therefore describes its AIS
population as Tier-A only.

## D3 — far baseline is an extra diagnostic

`T-250..T-230` was measured for comparability with Sprints 2–3 but was not declared in Sprint 4.
It is excluded from both Holm families and cannot upgrade any finding.

## D4 — rights matched-control N below floor

Only 132 rights events found a unique within-month control after the locked caliper and control
contamination filters, below the 200-event floor. The estimate is still reported, but is an
underpowered diagnostic rather than a robustness pass.

## Trial ledger

- Rights ex-date family: 3 horizons, Holm-adjusted.
- Pooled ESOP/private-placement AIS family: 3 horizons, Holm-adjusted.
- Declared secondary diagnostics: IS/OOS, subtype and rights-AIS splits, TERP validation,
  placebo, pretrend, leave-one-year-out, R-WIDE, matched controls, dilution/discount regression.
- Extra: far baseline only (D3).

No horizon, filter, caliper or subgroup threshold was changed after outcomes were observed.
