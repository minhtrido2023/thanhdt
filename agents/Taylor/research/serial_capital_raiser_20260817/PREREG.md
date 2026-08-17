# PREREG — serial capital raising: long-run returns and cross-sectional valuation discount

Job `Taylor_20260817_075412`. **Committed BEFORE any outcome number was computed.** Anything not
written here and later reported is a deviation and goes in `DEVIATIONS.md` with a reason.

Predecessor: `corp_action_program_20260815` Sprints 1–4 (event ledger, taxonomy, cash-dividend and
issuance event studies). This program does **not** rebuild the taxonomy — it reuses the audited
`issue_method_code → subtype` map (`ca_lib.ISS_SUBTYPE_BY_METHOD_CODE`) verbatim, expressed in SQL
exactly as `sprint4_build.py` did.

---

## 0. What is being asked, and why the answer cannot be Sprint 4's

Sprint 4 measured the **event window** around a single issuance (T+5/T+20/T+60) and found a NULL for
pooled ESOP/private placement, and a null preregistered primary for rights. That is an
event-driven, short-horizon question.

Two different questions here:

- **Q1 — long-run.** Does the short-horizon null persist, revert, or turn into drift at 1/2/3 years
  after an issuance?
- **Q2 — cross-sectional.** Holding valuation and sector fixed, are companies that raise capital
  *repeatedly* priced **cheaper** (an implicit stigma discount) — and if so, do they earn more or
  less than equally-cheap non-raisers?

Q2 is the user's actual question: *"cùng PE/PB, công ty hay huy động vốn có bị discount không?"*
Answering it requires a panel, not an event study, and it requires the valuation and the return
legs to be reported **together** — a cheaper multiple alone is not a discount if the forward return
is correspondingly worse.

## 1. Data sources — locked, registry-checked

`kb/data_registry/` consulted before choosing each source (§9 `coding_guidelines`).

| Source | Status in registry | Use here |
|---|---|---|
| `tav2_bq.corporate_action` | CANONICAL (bẫy PIT đã ghi) | issuance events; **only `exright_date` anchors** |
| `tav2_bq.ticker` `Close` | CANONICAL | returns (adjusted series) |
| `tav2_bq.ticker` `PE`,`PB` | **CANONICAL — already PIT on raw `Price`** | valuation. **NEVER multiplied by `Price/Close`** |
| `tav2_bq.ticker` `Price`,`Volume` | CANONICAL | ADV size control (`Price×Volume`, bẫy (7)) |
| `tav2_bq.ticker` `ROE_Trailing`,`Debt_Eq_P0`,`Revenue_YoY_P0`,`ICB_Code` | CANONICAL | controls |
| `tav2_mike.universe_pit` | CANONICAL, per-day | universe gate, PIT join per day |
| `ticker.profit_2W/1M/2M/3M` (+ `_center_*`) | forward-looking | **FORBIDDEN** — not read, not as filter, not as variable |
| `ticker_financial.OShares` | **TRAP — restated, not PIT** | **NOT USED.** Size control is ADV, not market cap |
| `corporate_action.public_date` | `WEAK_UNVERIFIED_VINTAGE` | **NOT USED** — no announcement study |
| `corporate_action.effective_date` | drifts up to ~7 weeks from ex | not used as anchor |

Consequences accepted in advance:

- **No market-cap control.** `OShares` is restated (registry: HAH 2026-02-02 carried a share count
  created 2026-05-27). `ADV60` is the size proxy. This is a real omitted-variable limitation and
  will be stated in the conclusion, not discovered later.
- **No announcement study.** Still forbidden until a second vintage of `corporate_action` exists
  (ledger C1, due ≈2026-09-12).
- **`Price/Close` mixing is banned in both directions**: valuation columns stay as stored; return
  series stays on `Close`. No expression mixes the two bases.

## 2. Event construction (shared by Q1 and Q2)

One economic event = `(ticker, exright_date, subtype)` after collapsing vendor multi-component rows.

- Filter: `event_code='ISS'`, `event_status='executed'`, `exright_date IS NOT NULL`.
- Dedup key: `(ticker, exright_date, issue_method_code, exercise_ratio, issue_volumn, total_value)`;
  survivor = `public_date DESC, id DESC`. Identical to Sprint 4's `RAW` CTE. Rationale for keeping
  distinct same-day rows with different terms: ledger A1/A2 — same-day, same-value rows are real
  separate tranches, and naive dedup destroys data.
- Subtype from `issue_method_code` only. `UNKNOWN` never enters any sample (ledger A4/T7c).

**RAISE_SET (primary, locked):** `RIGHTS`, `PRIVATE_PLACEMENT`, `AUCTION`.
These are the subtypes where external cash actually enters the company from investors.
Excluded from the primary and why:

- `STOCK_DIVIDEND`, `BONUS` — no capital raised; pure accounting split. Including them would answer
  a different question (dilution/split frequency, not capital raising).
- `ESOP` — compensation, not a capital raise.
- `CONVERTIBLE` — conversion of a pre-existing instrument; the cash arrived earlier.
- `MERGER` — share issue as acquisition consideration.

**Pre-registered robustness variants, declared now so neither can be a post-hoc pick:**

- **V-WIDE** = RAISE_SET ∪ {`ESOP`, `CONVERTIBLE`} — "anything that puts new shares in third-party
  hands".
- **V-ALL** = every ISS subtype except `UNKNOWN` — the dispatch's literal wording (`event_code='ISS'`).

The primary is **RAISE_SET**. V-WIDE and V-ALL are reported for every headline number. If the three
disagree in sign, the verdict is DESCRIPTIVE regardless of any single p-value.

## 3. Q1 — long-run BHAR after an issuance

**Anchor** `t0` = `exright_date`, required to be a real trading session of that ticker with
`Close > 0`. Entry convention: **close of the ex-date**. Entitlement declared explicitly (ledger
E4): a buyer at that close does **not** receive the right, and the mechanical ex-adjustment has
already happened. No arithmetic on this outcome will be presented as describing any other trade.

**Universe gate** `in_universe = TRUE` in `universe_pit` on `t0` (PIT, per-day join).

**Outcome**

```
BHAR_h = (Close_{t0+h} / Close_{t0} - 1) - (VNINDEX_{t0+h} / VNINDEX_{t0} - 1)
```

`h` counted in **the ticker's own trading sessions** (session index, not calendar days) so a
suspension does not silently shorten the window. VNINDEX leg read from `ticker` where
`ticker='VNINDEX'`, same `Close` basis. Missing `t0+h` ⇒ event drops out (NaN), never borrows a
neighbouring session (ledger E3).

**Horizons** `h ∈ {250, 500, 750}` sessions ≈ 1Y / 2Y / 3Y.

**Primary hypothesis H1:** pooled RAISE_SET `BHAR_250 = 0`.
Primary horizon is **250** — chosen a priori for maximum sample retention. 500 and 750 are
secondary. **A "long-run underperformance" claim requires the primary to reject Holm-corrected AND
at least one longer horizon to agree in sign.** One isolated significant horizon is not a finding.

**Multiplicity:** Holm across `{250, 500, 750}` within each reported family.

**Inference:** month-block bootstrap on `YYYY-MM` of `t0`, 10,000 resamples, seed `20260817`
(reused estimator `boot()` from `sprint3_analyze.py`). Also report median and share-positive: a
skewed mean with a negative median is not evidence of a typical outcome (Sprint 4 rights lesson).

**N is declared as events / distinct tickers / distinct anchor months.** Subgroup floor **N = 200
events**, same floor Sprint 4 locked. Below floor ⇒ descriptive only, no verdict.

**Splits:** IS = `t0 < 2020-01-01`; OOS = `t0 ≥ 2020-01-01`. An edge present only in IS is rejected.

**Falsification tests (all pre-committed):**

1. **Placebo** — identical estimator anchored at `t0 − 250` sessions. A significant placebo means the
   pipeline or the selection, not the event, produces the number (Sprint 2 lesson E2).
2. **Pre-trend** — `BHAR` over `[t0−250, t0−1]`. Issuers are known to time raises after run-ups;
   a large pre-trend reframes any post-event number as reversal, not issuance effect.
3. **Leave-one-year-out** on the primary. Sign flip ⇒ not temporally stable ⇒ downgrade.
4. **Subtype disagreement** — RIGHTS vs PP vs AUCTION reported separately even below the N floor,
   flagged as such.

## 4. Q2 — cross-sectional valuation discount

**Panel** month-end snapshots, `2010-01-31 → 2026-05-31`. Start 2010 so the 3-year lookback window
sits inside dense `corporate_action` coverage (raise events/yr: 2007=457, 2008=219, 2009=221).
Row = `(ticker, month_end)` with `in_universe = TRUE` on that date and a real session.

**Raiser state at `t` (PIT by construction — only past ex-dates)**

```
n_raise_3y(i,t) = # events, subtype in RAISE_SET, exright_date in (t - 1095 days, t]
serial(i,t)     = 1 if n_raise_3y >= 2
occasional(i,t) = 1 if n_raise_3y == 1
baseline        = n_raise_3y == 0
```

**Valuation on the YIELD scale**, not on PE/PB directly:

```
ey = 1/PE   (rows with PE > 0)
by = 1/PB   (rows with PB > 0)
```

Rationale, locked: PE is unbounded and heavy-tailed, and negative-earnings names (52/797 tickers
per registry) make a PE mean meaningless; yields are the production convention (`rating_8l`
composite v3 = ey + cfy + ps). **Cheaper ⇒ HIGHER `ey`. A discount predicts a POSITIVE `serial`
coefficient.** `ln(PE)` on the `PE>0` subset is reported as a secondary for readability only.

**Test Q2a — is there a discount?** Pooled OLS

```
ey_it = a + b1*serial_it + b2*occasional_it + controls_it + month_FE + sector_FE + e_it
```

- controls: `ln(ADV60)`, `ROE_Trailing`, `Debt_Eq_P0`, `Revenue_YoY_P0`.
- `sector_FE` = `ICB_Code`; `month_FE` = `YYYY-MM`. Month FE absorbs the regime — a raiser wave that
  coincides with a cheap market cannot masquerade as a raiser discount.
- SE **two-way clustered on ticker and month** (Cameron-Gelbach-Miller, same `meat()` estimator as
  `sprint3_analyze.twoway_ols`). Clustering on ticker is mandatory: `serial` is persistent within a
  firm, so event-level SEs would be badly understated.
- `b1` reported in yield points **and** translated to a % multiple gap at the sample median PE/PB.
- Repeated with `by`. **Holm across `{ey, by}`.**

**Test Q2b — is the cheapness earned or is it compensation?** Value-matched, monthly-rebalanced
portfolio spread:

1. Each month `t`, among rows with valid `ey`, form **`ey` quintiles**.
2. Within each quintile: EW portfolio of `serial` names, EW portfolio of `baseline` names.
   A quintile contributes only if **both** legs have `>= 3` names.
3. `spread_{q,t}` = next-month return of serial leg − baseline leg (from `Close`).
4. `spread_t` = mean over contributing quintiles. This is a **monthly, non-overlapping** series, so
   there is no overlapping-window inference problem to hand-wave about.
5. Test `mean(spread_t) = 0` with Newey-West (lag 6) **and** month-block bootstrap. IS/OOS split.
   Cumulative compounded spread reported for the 12/24/36-month reading.

Same procedure repeated with `by` quintiles.

**Locked decision matrix — the verdict is a table lookup, not a judgement call after the fact:**

| Q2a `serial` coefficient | Q2b spread | Verdict | Meaning |
|---|---|---|---|
| positive (cheaper), Holm p<0.05 | not significantly positive | **NULL / RISK** | the discount is compensation — market is right, no alpha |
| positive (cheaper), Holm p<0.05 | significantly positive | **ALPHA candidate** | stigma discount; requires DSR/PBO + quant-skeptic before any further step |
| not significant | anything | **DESCRIPTIVE** | no measurable discount |
| negative (richer) | anything | **DESCRIPTIVE / RISK** | the premise of the question is not supported |

**Falsification for Q2 (pre-committed):**

1. **Shuffle placebo** — reassign `serial` labels randomly within `(month, sector)` cells, rerun
   Q2a. A significant coefficient under shuffling means the FE/clustering structure is broken.
2. **Occasional-raiser monotonicity** — if a genuine stigma exists, `b1(serial) > b2(occasional) > 0`
   is expected. Non-monotonicity is reported, not smoothed over.
3. **Look-ahead probe** — recompute `n_raise_3y` using a window shifted 6 months into the FUTURE
   `(t, t+180]`. If the "discount" is as strong or stronger with future events, the result is
   picking up a firm characteristic, not information available at `t`.
4. **Subsample by regime** — split on DT5G-era macro states is *not* attempted (regime tables cover a
   shorter span and would confound the test); month FE is the regime control, and this is stated as a
   limitation rather than papered over with a shorter sample.

## 5. Multiple-testing accounting (§`coding_guidelines` mult-testing discipline)

Declared trial count for this program:

- Q1: 3 horizons × 3 raise-set variants = 9, plus 3 subtype cuts = **12 estimates**.
- Q2a: 2 valuation measures × 3 raise-set variants = **6 estimates**.
- Q2b: 2 sort variables × 3 raise-set variants = **6 estimates**.
- **N_trials = 24.** Holm applied within family as specified above.

**DSR/PBO are NOT computed and NOT required here** — deliberately, with the reason stated: no
strategy configuration is being selected and nothing is proposed for wiring. DSR/PBO are the gate
for *choosing a config to deploy*; this program produces a descriptive answer to a research
question. If Q2 lands on **ALPHA candidate**, that is where the program stops and DSR/PBO +
quant-skeptic become mandatory *before* anything further. Declaring that boundary now prevents the
usual drift from "we measured something" to "we should trade it".

## 6. Self-check obligation — and one declared deviation

There is **no NAV simulation and no execution** in this program: Q2b is a return-spread series, not
a capital path, so the standard `self-check 0 VND` has nothing to reconcile. Declaring this in
advance rather than discovering it later. The equivalent discipline actually applied:

`selfcheck_serial.py` must assert, on real data, at minimum:

1. `Close`/`Price` bases are never mixed in one expression; no `profit_*` column appears anywhere in
   the build SQL or the analysis (grep-based assertion over the source files themselves).
2. Session-index arithmetic: `BHAR` at `h` uses exactly the `h`-th following session of that ticker;
   a fabricated gap must produce NaN, not a borrowed price.
3. Event dedup is lossless in lineage: every raw `id` in scope appears in exactly one output event.
4. `n_raise_3y` counts only events with `exright_date <= t` (no future leakage) — asserted by
   constructing a synthetic event after `t` and checking the count does not move.
5. Universe gate is per-day: a ticker `in_universe` on one date but not another must be present in
   the first snapshot and absent in the second.
6. Two-way clustered SE reduces to the one-way value when the second cluster is a singleton per row.
7. Independent recompute of the primary Q1 number and the primary Q2a coefficient from the dumped
   CSVs by a **separate code path** from the one that produced them, matching to 1e-9.
8. Bootstrap reproducibility: same seed ⇒ identical CI to the last digit.
9. Timezone: date logic runs identically under `env -u TZ` and under a foreign `TZ` (§16).

Any FAIL is fixed, or the affected number is not reported. The first hypothesis on a FAIL is *"my
test is wrong"* (ledger E1), not *"the code is wrong"* — but the test is only edited with the reason
written down.

## 7. Scope boundary

- Files only under `agents/Taylor/research/serial_capital_raiser_20260817/`.
- **No** production wiring, **no** cron, **no** change to `trading_rules.json`, **no** table or view
  created, **no** other agent dispatched.
- Read-only BigQuery.
