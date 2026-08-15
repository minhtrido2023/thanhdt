# SPRINT 4 — PRE-REGISTRATION (rights, ESOP, private placement)

> Locked 2026-08-15 before any Sprint 4 outcome. Base ledger commit `f8cb4596`; inherited
> methods through Sprint 3 commit `b4e111b2`. This file is immutable after commit. Deviations
> and additional trials go to `SPRINT4_DEVIATIONS.md`.

## 0. Scope and inherited gate

- Subtypes: `RIGHTS`, `ESOP`, `PRIVATE_PLACEMENT`, always retained separately.
- Rights are price-adjusting at `exright_date`; ESOP/private placement are not. Therefore an
  ex-date/TERP study is allowed only for rights.
- ESOP/private placement are studied only at a high-quality additional-listing/supply-arrival
  anchor. Their `exright_date` is not treated as announcement or a tradable known date.
- Announcement studies and use of `public_date`/`known_date` remain forbidden. No production,
  strategy optimisation or BigQuery write is allowed.

## 1. Economic quantities

- `issue_price = total_value / issue_volumn`, requiring both positive.
- Rights ratio `q = exercise_ratio`, requiring `0 < q <= 5`.
- Cum raw price is `P_-1`, never `ticker.Price` on the ex-date row.
- `TERP = (P_-1 + q * issue_price)/(1+q)` and theoretical adjustment factor
  `f_terp = TERP/P_-1`.
- AIS dilution intensity is `shares_delta/shares_total_after` from the linked AIS row. If AIS
  shares are missing, use `issue_volumn/shares_total_after` only when the two volumes match
  within max(2%, 1,000 shares). No current-share-count proxy.
- Issue discount at rights ex-date is `1 - issue_price/P_-1`. For ESOP/private placement it is
  `1 - issue_price/P_AIS_-1`, explicitly descriptive because issue pricing predates AIS.

Values outside `0 < issue_price <= 5*P_anchor`, negative/nonpositive volume, dilution outside
`(0,1]`, or missing terms are excluded from term/dose-response modules and counted. They may
remain in pure event-time returns if anchor and price are valid.

## 2. Populations

Date range: anchors in 2014-01-01…2026-06-30. An exact anchor trading session is required,
except a recorded AIS/listing date may map to the first trading session on or after that date;
the calendar lag is retained and must be <=5 days.

- **R-CORE:** executed actionable rights, exact ex session, `Volume_0>0`, in `universe_pit` on
  exact ex-date, valid positive q and issue price, and no contamination.
- **R-WIDE:** same without universe membership; robustness only.
- **AIS-CORE:** ESOP/private placement/rights with accepted AIS link, exact/resolved trading
  anchor, in universe on the AIS trading date, valid prices and no contamination. Rights AIS is
  a separate subgroup, not pooled into the ESOP/placement primary contrast.

Economic duplicates are collapsed using the canonical ledger components. Same ticker/subtype/
ex-date components sum issue volume and total value; if terms imply different issue prices by
more than 1%, label `MIXED_TERMS` and exclude from TERP/dose-response while retaining event
returns. ESOP rows with the same ticker/listing date are combined to avoid double-counting one
supply arrival.

IS = 2014–2019; OOS = 2020+. All subgroup claims require >=200 events and >=60 tickers.

## 3. AIS linkage

Use Sprint 3's locked conservative hierarchy:

1. Tier A: issuance `listing_date`, after the issuance reference date and within 365 days.
2. Tier B: exactly one AIS row within 7…365 days whose `shares_delta` matches `issue_volumn`
   within max(2%, 1,000 shares).
3. If both sources exist, dates must agree within 5 calendar days and volumes within the same
   tolerance. Otherwise `CONFLICT`, excluded from confirmatory AIS analysis.
4. Multiple candidates, no valid trading anchor, >5-day market-date mapping or >365-day lag are
   excluded and reported. No nearest-date fallback.

## 4. Contamination

- Rights ex-date: exclude another actionable price-adjusting event on the same ticker in
  `[ex-21, ex+21]` calendar days, exempting only components of the focal rights event.
- AIS: exclude another AIS/issuance or any price-adjusting event within ±21 calendar days.
- For 60-session outcomes, extend the forward contamination window to +90 calendar days.
- Exclude DNN/BCB/PTX from raw-price validation. No realised-return exclusion.

## 5. Confirmatory questions and outcomes

Benchmark is the equal-weighted PIT universe total-return series validated in Sprint 2.

### R1 — rights after ex-date

- **Primary:** `BHAR_RIGHTS_EX_20 = C_20/C_0 - 1 - EW(0,20)`.
- Secondary: 5 and 60 sessions.
- H0: primary mean is zero; two-sided alternative.
- TERP microstructure: reconstruct `P_hat_0=C_0*(P_+1/C_+1)` only if `Price/Close` is stable
  over T+1…T+3 within 0.1%; report `P_hat_0/TERP-1`. Validate observed factor against
  `P_-1/TERP`; if <80% match within 1%, fail the TERP module closed to descriptive-only.

### A1 — supply arrival at AIS

- **Primary:** `BHAR_AIS_20 = C_20/C_-1 - 1 - EW(-1,20)`.
- Secondary: 5 and 60 sessions, abnormal volume T0 and mean T0…T+5.
- Primary family contains ESOP and private placement pooled only for the overall supply-arrival
  test; subtype estimates and their contrast are secondary. Rights AIS is reported separately.
- H0: pooled ESOP/private-placement primary mean is zero; two-sided alternative.

### D1 — dilution and discount gradients

Two-way clustered regressions by ticker and event month:

`BHAR_AIS_20 ~ dilution + discount + subtype + log(ADV60) + momentum + rvol60 + year FE`.

PIT market cap is included only if coverage >=80%; otherwise omitted and disclosed. Current ICB
may be a descriptive FE only. Continuous terms are winsorised at predeclared 1/99 percentiles;
raw coefficients are also reported.

## 6. Inference and trials

- Month-block bootstrap, 10,000 draws, seed `20260815`; report N events/tickers/months, mean,
  median, p10/p25/p75/p90, positive share and 95% CI.
- Rights ex family: 3 horizons, Holm correction.
- ESOP/private-placement AIS family: 3 horizons, Holm correction.
- Rights AIS is an explicitly secondary third family and cannot upgrade the verdict.
- Effect/dose-response claims require the declared clustered regression and matching robustness.

## 7. Mandatory robustness

1. IS/OOS and leave-one-year-out for each primary.
2. ESOP vs private placement; rights AIS separately.
3. Below/above median dilution and discount, subject to N floor.
4. Winsorised 1% and 1%-trimmed means.
5. Placebo T-40…T-20 and pretrend T-21…T-1 at each valid anchor.
6. R-WIDE for rights.
7. Tier A only vs A+B; conflict/unlinked counts and samples.
8. One-to-one matched control for rights ex and pooled AIS: same current ICB level 1/month,
  caliper 0.5 on standardized pre-event log(ADV60), momentum and rvol60, no replacement within
  event month; controls with a price-adjusting event ±21 days are removed.

## 8. Failure gates and labels

- Significant pretrend/placebo, IS/OOS instability, matched-control null, or one year carrying
  >40% of the effect prevents causal/alpha interpretation.
- If valid issue-price coverage or AIS linkage leaves fewer than 200 events/60 tickers for a
  subtype, label that subtype `DESCRIPTIVE ONLY`.
- AIS dates are not assumed known early enough to trade. No cost screen or strategy is allowed.
- Final labels are limited to `DESCRIPTIVE ONLY`, `RISK/DUE-DILIGENCE`, or `RESEARCH CANDIDATE`.
  Sprint 4 cannot wire a production rule.

## 9. Deliverables

Reproducible event/AIS panels, TERP and linkage audit, `SPRINT4_ISSUANCE.md`, deviations ledger,
machine-readable results, plots and independent selfcheck.
