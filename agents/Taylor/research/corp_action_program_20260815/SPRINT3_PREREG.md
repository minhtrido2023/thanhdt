# SPRINT 3 — PRE-REGISTRATION (stock dividend and bonus shares)

> Locked on 2026-08-15 before computing any Sprint 3 outcome. Base ledger: Sprint 1 commit
> `f8cb4596`; cash-dividend methods/corrections: `2a9b951a`…`fdae3fe6`. This file is immutable
> after its commit. Every departure or extra trial goes to `SPRINT3_DEVIATIONS.md`.

## 0. Inherited gate and scope

- Allowed: ex-date mechanics and post-event outcomes anchored to `exright_date`; descriptive
  outcomes around an AIS date that is explicitly recorded or unambiguously linked.
- Forbidden: announcement studies; treating `public_date`/`known_date` as point-in-time;
  reading `ticker.Price` on an ex-date row; using a later AIS date as information available at
  ex-date; wiring a rule to production.
- Studied subtypes are `STOCK_DIVIDEND` and `BONUS`, retained separately. Rights, ESOP,
  placements and conversions are contamination, not observations in this sprint.

## 1. Questions and confirmatory hypotheses

**E1 — post-ex performance (primary).** After the exchange mechanically adjusts nominal price,
is benchmark-adjusted total return from the ex-date close to T+20 different from zero?

- H0-E1: mean `BHAR_EX_20 = 0`.
- H1-E1: mean `BHAR_EX_20 != 0`.
- The STOCK_DIVIDEND–BONUS contrast is secondary; no direction is predicted.

**E2 — nominal-price/liquidity channel.** Is the change in liquidity after ex-date associated
with the distribution ratio, after separating the mechanical fall in nominal price?

- H0-E2: mean `DLOG_ADTV_EX = 0` and its coefficient on `log(1+ratio)` is zero.
- H1-E2: at least one differs from zero. This is a descriptive microstructure hypothesis, not
  an alpha hypothesis.

**A1 — supply arrival at AIS (co-primary but separate family).** For events with a high-quality
AIS link, is benchmark-adjusted return from AIS T-1 close through T+20 different from zero?

- H0-A1: mean `BHAR_AIS_20 = 0`.
- H1-A1: mean `BHAR_AIS_20 != 0`.
- AIS results describe realised supply arrival. They do not establish a strategy unless the AIS
  date is independently proven known before a feasible trade; that proof is outside Sprint 3.

Null results and sign disagreements between IS/OOS will be reported without relabelling.

## 2. Population and fixed dates

Source: `out/event_ledger.csv.gz`, `actionable = 1`, subtype in the two studied labels,
`exright_date` in 2014-01-01…2026-06-30, positive usable `exercise_ratio`, and an exact trading
session on the anchor date with `Close > 0` and `Volume > 0`.

- **P-CORE:** in `universe_pit` on the exact ex-date; primary ex-date population.
- **P-WIDE:** has valid price but no universe restriction; robustness only.
- Events sharing `(ticker, exright_date, subtype)` are economically deduplicated first. If stock
  dividend and bonus occur for the same ticker/ex-date, keep one combined mechanical event with
  `ratio_total = sum(ratio)` and a `MIXED_STOCK_DISTRIBUTION` label; it is excluded from the
  subtype contrast but retained in the overall primary.
- Ratio must satisfy `0 < ratio_total <= 2.0`. Above 200% is reported and excluded as an extreme
  terms/data-quality stratum, not silently winsorised.
- IS = 2014–2019; OOS = 2020–2026-06-30. Horizon-specific N requires the terminal session.

## 3. AIS linkage — fixed, conservative and auditable

For each deduplicated ex event, define one AIS anchor using these tiers in order:

1. **Tier A:** the issuance row has `listing_date`; use it if it is after ex-date, within 365
   calendar days, and it is an exact trading session or resolves to the first trading session on
   or after the recorded date (record both dates and lag).
2. **Tier B:** otherwise find `ADDITIONAL_LISTING.effective_date` for the same ticker in
   `[ex+7, ex+365]`. Accept only when exactly one candidate exists and its `shares_delta` matches
   issuance `issue_volumn` within max(2%, 1,000 shares). If issue volume is missing, Tier B is
   not accepted.
3. **Cross-check:** when both the issuance `listing_date` and an AIS row exist, report date and
   volume agreement. A disagreement over 5 calendar days or 2% volume downgrades the link to
   `CONFLICT`; it is excluded from confirmatory AIS analysis.
4. Multiple candidate AIS rows, missing required dates, or an AIS anchor outside 365 days are
   `UNLINKED/AMBIGUOUS` and excluded, with counts and samples published.

No nearest-date fallback is allowed. The 365-day ceiling is fixed before measuring returns.

## 4. Contamination exclusions

For each horizon, exclude another actionable price-adjusting event (`DIV`, stock dividend,
bonus or rights) for the same ticker in `[anchor-21, anchor+W]` calendar days, except the rows
forming the focal combined event. `W=21` for 20-session outcomes and `W=90` for 60-session
outcomes. Around AIS, additionally exclude another AIS/issuance within ±21 calendar days.

Exclude known broken raw-price tickers `DNN`, `BCB`, `PTX` from nominal-price checks. Adjusted
return outcomes do not use `Price` on the anchor row. No exclusion is based on realised return.

## 5. Fixed outcomes

Let `C_k` be adjusted `Close`, `P_k` raw `Price`, and `V_k` volume at session offset k. The
benchmark is the equal-weighted point-in-time universe return used and validated in Sprint 2.

### 5.1 Ex-date family

- **Primary:** `BHAR_EX_20 = C_20/C_0 - 1 - EW(0,20)`.
- Secondary horizons: 5, 10 and 60 sessions.
- Mechanical check: `AR_EX = C_0/C_-1 - 1 - EW(-1,0)`.
- Theoretical raw reference: `P_ref = P_-1/(1+ratio_total)`. Reconstruct raw ex price only as
  `P_hat_0 = C_0 * (P_+1/C_+1)` after requiring the `Price/Close` ratio to be stable over T+1…T+3
  within 0.1%. Report `P_hat_0/P_ref-1`; never read `Price_0` for inference.
- Liquidity: `ADTV_pre = median(P*V)` on T-60…T-6 and `ADTV_post = median(P*V)` on T+6…T+60;
  `DLOG_ADTV_EX = log(ADTV_post)-log(ADTV_pre)`. Also report volume and zero-volume-session
  changes. The gap prevents the adjustment week dominating the long-run liquidity measure.

### 5.2 AIS family

- **Primary:** `BHAR_AIS_20 = C_20/C_-1 - 1 - EW(-1,20)` on Tier A/B non-conflict links.
- Secondary: AIS 5 and 60 sessions; abnormal volume T0 and mean T0…T+5 versus T-60…T-6.
- Supply intensity: linked `issue_volumn / shares_total_after`, if both positive; missing values
  remain missing. No backfilled shares assumption.

## 6. Controls, inference and multiplicity

- Report N events, N tickers, N event months, mean, median, p10/p25/p75/p90, share positive and
  month-block-bootstrap 95% CI. Bootstrap: 10,000 draws, seed `20260815`.
- Primary ex and AIS tests form two distinct confirmatory families. Within the four ex horizons
  and three AIS horizons, Holm-adjust p-values; primary claims require adjusted p < 0.05.
- Two-way clustered OLS by ticker and event month:
  `outcome ~ log(1+ratio) + subtype + log(ADV60) + momentum_6m_skip1m + rvol60 + year FE`.
  Add PIT market cap only if coverage >=80%. Current ICB may be descriptive FE only and must be
  labelled as non-PIT.
- Matched-control robustness: one control per event, selected without future outcomes from
  universe members on the anchor date, same ICB level 1 and calendar month, nearest standardized
  pre-event `log(ADV60), momentum, rvol60, log(mcap_PIT)`. Caliper 0.5 on each available feature;
  no replacement within an event month. Fewer than 200 events or 60 tickers means insufficient N.

## 7. Mandatory robustness and failure gates

1. IS/OOS and per-year leave-one-out.
2. STOCK_DIVIDEND and BONUS separately; combined same-day events separately.
3. Above/below median ratio and liquidity, subject to the N floor.
4. Winsorised 1% and 1%-trimmed mean.
5. Placebo window T-40…T-20 and pretrend T-21…T-1 for ex-date outcomes.
6. P-WIDE and matched-control estimates.
7. AIS Tier A only versus A+B; link conflicts and unlinked events reported.
8. Exclude events whose reconstructed adjustment-factor error exceeds 1%.

Fail closed:

- If fewer than 80% of mechanical-check events match the theoretical factor within 1%, the raw
  nominal-price module becomes `DESCRIPTIVE ONLY` and cannot support a causal claim.
- If AIS confirmatory N <200 events or <60 tickers, AIS is a descriptive case series only.
- A nonzero primary with a same-sign significant pretrend/placebo, unstable IS/OOS sign, or a
  single-year contribution above 40% cannot be labelled causal or alpha.
- Any after-cost screen is forbidden in Sprint 3 unless the date entitlement and trade timing
  are specified in a later preregistration. Sprint 3 can conclude only `DESCRIPTIVE ONLY`,
  `RISK/DUE-DILIGENCE`, or `RESEARCH CANDIDATE`; never production-ready alpha.

## 8. Declared deliverables

`SPRINT3_STOCK_DISTRIBUTION.md`, `SPRINT3_DEVIATIONS.md`, a reproducible event/AIS panel,
linkage audit and samples, machine-readable results, plots, and an independent selfcheck. No
BigQuery write, scheduler, production code or live trading rule.
