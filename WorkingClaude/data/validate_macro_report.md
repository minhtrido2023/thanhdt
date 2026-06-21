# Macro Overlay — Robustness Validation

*Pure-index, real BQ, 1B. Baseline (no macro): Full +19.17%/Sh 1.25/DD -34.8%, Modern +14.49%/DD -18.7%.*

## A. One-at-a-time parameter sensitivity (Δ vs baseline)

| Param | Value | ΔFull CAGR | ΔModern CAGR | Full Sh | Full DD |
|---|---|---|---|---|---|
| vix_mult | 0.85 | +0.76pp | +0.24pp | 1.39 | -34.7% |
| vix_mult | 1.0 ←base | +0.49pp | +0.05pp | 1.34 | -34.7% |
| vix_mult | 1.15 | +0.44pp | -0.00pp | 1.34 | -34.7% |
| spx_mult | 0.85 | +0.66pp | +0.45pp | 1.36 | -34.7% |
| spx_mult | 1.0 ←base | +0.49pp | +0.05pp | 1.34 | -34.7% |
| spx_mult | 1.15 | +0.66pp | +0.27pp | 1.35 | -34.7% |
| sbv_mult | 0.7 | +0.49pp | +0.05pp | 1.34 | -34.7% |
| sbv_mult | 1.0 ←base | +0.49pp | +0.05pp | 1.34 | -34.7% |
| sbv_mult | 1.3 | +0.49pp | +0.05pp | 1.34 | -34.7% |
| refi_lag | 5 ←base | +0.49pp | +0.05pp | 1.34 | -34.7% |
| refi_lag | 21 | +0.63pp | +0.22pp | 1.35 | -34.7% |
| refi_lag | 63 | +0.39pp | -0.45pp | 1.29 | -34.7% |
| ez_confirm | 5 | +0.38pp | -0.05pp | 1.34 | -34.7% |
| ez_confirm | 10 ←base | +0.49pp | +0.05pp | 1.34 | -34.7% |
| ez_confirm | 15 | +0.56pp | +0.05pp | 1.35 | -34.7% |
| ez_confirm | 20 | +0.58pp | +0.05pp | 1.35 | -34.7% |
| ez_price_lb | 5 | +0.30pp | +0.04pp | 1.33 | -34.7% |
| ez_price_lb | 10 ←base | +0.49pp | +0.05pp | 1.34 | -34.7% |
| ez_price_lb | 20 | +0.24pp | -0.13pp | 1.33 | -34.7% |
| bull_bypass | True ←base | +0.49pp | +0.05pp | 1.34 | -34.7% |
| bull_bypass | False | -0.67pp | -0.95pp | 1.30 | -34.7% |

*ΔFull range [-0.67, +0.76]pp, all mixed; ΔModern range [-0.95, +0.45]pp. Plateau (not spike) ⇒ sensitive.*

## B. Leave-one-year-out — modern alpha attribution

Macro modern alpha (all years) = **+0.05pp**. Drop each year, recompute modern-window alpha; a big drop = that year drives the alpha.

| Excluded year | Modern alpha w/o it | Δ vs all-years |
|---|---|---|
| 2014 | -0.24pp | -0.29pp |
| 2015 | +0.05pp | +0.00pp |
| 2016 | +0.05pp | +0.00pp |
| 2017 | +0.05pp | +0.00pp |
| 2018 | +0.05pp | +0.00pp |
| 2019 | +0.05pp | +0.00pp |
| 2020 | +0.05pp | +0.00pp |
| 2021 | +0.05pp | +0.00pp |
| 2022 | +0.05pp | +0.00pp |
| 2023 | +0.05pp | +0.00pp |
| 2024 | +0.05pp | +0.00pp |
| 2025 | +0.05pp | +0.00pp |
| 2026 | +0.05pp | +0.00pp |

*Most alpha-carrying year: dropping **2014** leaves -0.24pp (vs +0.05pp all-years). If alpha stays positive after dropping the biggest contributor, it is NOT a single-event artifact.*
