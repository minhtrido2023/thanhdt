# Serial capital raising in VN equities — long-run returns and the valuation-discount question

Job `Taylor_20260817_075412`, 2026-08-17. Design locked at commit `eccab390` **before** any outcome
number was produced. Selfcheck **28/28 PASS**, identical under `env -u TZ` and `TZ=America/Chicago`.

---

## The user's question, answered first

> *"Cùng PE/PB, công ty hay huy động vốn có bị discount không?"*

**No — and the sign is the opposite of the premise.** Companies that raised external capital ≥2
times in the trailing 3 years are **not** priced cheaper on earnings; they carry a **~17–19% HIGHER
PE** than same-month, same-sector peers after controlling for liquidity, profitability, leverage and
Piotroski score. On book value they are marginally cheaper, but that gap is not statistically
distinguishable from zero once the same controls are applied.

And there is no hidden discount being missed: **at matched valuation they still underperform** by
roughly **0.8–0.9% per month (~10%/yr)**. So the cheapness that does exist on book value is
compensation, not opportunity.

**Verdict: RISK / DESCRIPTIVE.** No alpha candidate. Nothing is proposed for wiring — see §6 for why
the effect fails this fleet's own deployment bar even though it is statistically real in-sample.

---

## 1. Samples — N declared as independent companies, not rows

| Panel | Rows / events | Distinct tickers | Distinct months |
|---|---:|---:|---:|
| Q1 event panel (all ISS, universe-gated) | 2,953 events | 578 | 198 |
| Q1 primary RAISE_SET (rights + private placement + auction) | 758 events | **368** | 181 |
| Q2 monthly panel (2010-01 → 2026-05) | 64,068 firm-months | 895 | 197 |
| Q2 serial raisers (≥2 raises / 3Y) | 14.7% of rows | **391** | — |
| Q2 serial raisers, ADV ≥ 2bn slice | — | **295–308** | — |

Definitions, locked in advance: **RAISE_SET = RIGHTS ∪ PRIVATE_PLACEMENT ∪ AUCTION** — the subtypes
where external cash actually enters the company. Stock dividends and bonus issues raise no capital
and were excluded from the primary by design; ESOP and convertibles enter only the declared V-WIDE
variant. This choice turns out to carry the entire result (§4).

Universe gate is `tav2_mike.universe_pit` `in_universe = TRUE` **on the anchor date itself** (per-day
PIT join, asserted by selfcheck T5). `PE`/`PB` are read **as stored** — already on the raw `Price`
basis and therefore already point-in-time — and are never rescaled by `Price/Close` (registry
`valuation_pe_pb_pcf_ps.md` bẫy (4); asserted by T1c). `OShares` is not read at all: it is restated,
not point-in-time, so the size control is ADV, not market cap.

---

## 2. Q1 — long-run BHAR after an issuance

Anchor = `exright_date`, entry at that session's close. Horizons counted in the ticker's **own**
sessions (T2c: median 250 index sessions for h=250, so nothing silently shortened).

**Pooled RAISE_SET, buy-and-hold abnormal return vs VNINDEX:**

| Horizon | N events | mean BHAR | 95% month-block CI | Holm p | median | share positive |
|---:|---:|---:|---:|---:|---:|---:|
| **250 (≈1Y, primary)** | **712** | **−7.74%** | **[−13.18%, −1.77%]** | **.0138** | −18.66% | 31.2% |
| 500 (≈2Y) | 674 | −18.18% | [−24.67%, −10.78%] | <.0001 | −33.98% | 27.2% |
| 750 (≈3Y) | 634 | −22.03% | [−30.44%, −12.46%] | <.0001 | −38.14% | 26.7% |

Unlike Sprint 4's rights result, **mean and median agree in direction here** and only ~27–31% of
events are positive, so this is not a skew artifact of a few winners.

**By subtype at the primary horizon** (floor N=200 events; below-floor cuts shown but carry no
verdict):

| Subtype | N | tickers | BHAR_250 | 95% CI | p | |
|---|---:|---:|---:|---|---:|---|
| RIGHTS | 420 | 277 | −9.67% | [−16.53%, −1.72%] | .020 | above floor |
| PRIVATE_PLACEMENT | 315 | 201 | −4.73% | [−12.18%, +3.90%] | .270 | above floor, null |
| AUCTION | 23 | 21 | −13.03% | [−24.76%, +1.04%] | .070 | **below floor** |
| ESOP | 555 | 233 | −0.25% | [−5.36%, +5.13%] | .915 | above floor, null |
| STOCK_DIVIDEND | 1,003 | 346 | −0.75% | [−5.17%, +3.57%] | .719 | above floor, null |
| BONUS | 427 | 230 | −2.90% | [−8.46%, +2.82%] | .302 | above floor, null |
| CONVERTIBLE | 164 | 46 | +7.61% | [−0.80%, +16.33%] | .077 | **below floor** |
| MERGER | 46 | 39 | +1.79% | [−8.54%, +12.30%] | .759 | **below floor** |

Only **rights issues** clear the floor with a significant negative. ESOP, stock dividend and bonus
are flat — consistent with Sprint 4's short-window nulls and with the economics: those events raise
no external capital.

### 2.1 The confound that matters most — issuers raise after a run-up

Both preregistered falsification tests fired, and they change how the table above must be read:

| Test | Window | Result |
|---|---|---|
| Pre-trend | [t0−250, t0] | **+45.54%** CI [+33.53%, +58.43%] |
| Far placebo | [t0−500, t0−250] | **+30.21%** CI [+20.71%, +40.78%] |

Firms that raise external capital have already beaten the index by ~30% two-to-one years out and
another ~46% in the year immediately before the ex-date. A significant far placebo is exactly the
condition PREREG §3 said would force a downgrade: **the post-event underperformance cannot be
separated from reversal of the pre-event run-up by this design.**

Conditioning on the run-up (post-hoc, deviation R1) shows how much of the effect is reversal:

| Pre-trend quartile | mean pre-trend | N | BHAR_250 | BHAR_500 | BHAR_750 |
|---|---:|---:|---:|---:|---:|
| Q0 (worst) | −36.2% | 152 | −5.78% ns | −5.92% ns | +4.92% ns |
| Q1 | +3.1% | 152 | −5.58% ns | −8.86% ns | −14.21% ns |
| Q2 | +41.8% | 152 | −7.90% ns | −10.67% ns | −18.07% * |
| Q3 (biggest run-up) | **+186.1%** | 152 | −10.38% ns | **−34.43%** * | **−43.51%** * |

The long-horizon damage is concentrated in the names that had run up most — the signature of
reversal. But it does not vanish: pooling all ISS events and regressing `BHAR_250` on a
cash-raise dummy alongside the pre-trend, `ln(ADV)`, realised vol and year fixed effects (SE
two-way clustered ticker × month, n=2,548) leaves

```
is_raise  = −5.49%  (t = −2.17)      pretrend = −3.28%  (t = −2.36)
```

so **being a cash raise costs ~5.5pp at 1Y incremental to the run-up it followed**, not the headline
−7.74%.

### 2.2 Temporal stability — the 1Y number does not survive, the 3Y number does

| Horizon | IS (t0 < 2020) | OOS (t0 ≥ 2020) |
|---:|---|---|
| 250 | −9.94% CI[−16.12%,−2.76%] p=.008, n=450 | **−3.97% CI[−13.50%,+7.08%] p=.44, n=262** |
| 500 | −20.52% CI[−27.84%,−12.40%] p<.0001 | −13.47% CI[−25.46%,+1.99%] p=.076, n=224 |
| 750 | −21.27% CI[−32.46%,−7.89%] p=.002 | **−23.89% CI[−32.47%,−14.57%] p<.0001, n=184** |

Leave-one-year-out on the primary: no sign flip, but **2010 alone carries 67.4% of the effect**
(n=129, mean −28.81%); dropping 2010 leaves −3.08%. Combined with the insignificant OOS, the **1Y
result is not robust**. The 3-year horizon is the one that holds in both halves.

---

## 3. Q2a — is there a valuation discount? No: a PE premium

Within-(month × sector) regression of earnings yield `ey = 1/PE` on raiser state plus `ln(ADV60)`,
`ROIC_Trailing`, `NPM_P0`, `FSCORE`, `Debt_Eq_P0`. SE two-way clustered on ticker and month.
**A discount would show as a POSITIVE serial coefficient (higher yield = cheaper).**

| Spec | n | cells | serial coef | t | p | occasional coef | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| **ey, RAISE_SET (primary)** | 49,911 | 6,522 | **−0.01350** | **−3.36** | **.0008** | −0.00408 | −1.24 |
| by, RAISE_SET | 54,891 | 6,815 | +0.04439 | +0.85 | .393 | +0.07794 | +2.08 |
| ey, V-WIDE | 49,911 | 6,522 | −0.00821 | −2.33 | .020 | −0.00494 | −1.55 |
| by, V-WIDE | 54,891 | 6,815 | −0.01531 | −0.34 | .738 | +0.03524 | +0.88 |
| ey, V-ALL | 49,911 | 6,522 | +0.00030 | +0.08 | .936 | +0.00084 | +0.23 |
| by, V-ALL | 54,891 | 6,815 | −0.07310 | −1.63 | .103 | +0.06029 | +1.31 |

Holm over the primary family {ey, by}: **ey p=.0015**, by p=.393.

**Magnitude.** Sample median `ey` = 0.0907 (PE 11.03). A −0.01350 shift implies **PE 12.95 vs
11.03 = +17.5%**. On the investable slice (ADV ≥ 2bn) the coefficient is −0.01286 (t=−2.58, p=.0098)
against a median PE of 12.45 → **PE 14.82 vs 12.45 = +19.1%**. The premium survives the liquidity
floor.

**Falsification results:**

- **Shuffle placebo** (serial labels permuted within month × sector): t = −0.75 (ey), −0.24 (by).
  The FE/clustering machinery does not manufacture a coefficient.
- **Look-ahead probe** (replace past raises with raises in the *next* 180 days): ey coefficient
  −0.00106, t=−0.31 — future raising does **not** predict a high PE, so the premium is tied to
  raises that have already happened, not to a permanent firm type. On book yield the future probe is
  strongly negative (−0.129, t=−4.19), i.e. firms raise **after** their book multiple is rich —
  market timing, and a further reason not to read PB cheapness as a discount.
- **Monotonicity** fails: on book yield the *occasional* raiser looks cheap (+0.078, t=+2.08) while
  the *serial* raiser does not (+0.044, t=+0.85). A genuine escalating stigma would order these the
  other way.
- **IS/OOS** on `ey`: −0.01465 (t=−2.40) and −0.00923 (t=−1.93). Same sign, OOS marginal.
- **Winsorised** (1/99 by month) and raw agree in sign and significance.

### 3.1 Why PE is high while PB is low — the denominator, not the market

Medians on the ADV ≥ 2bn slice:

| Group | rows | PE | PB | ROIC_Trailing | NPM_P0 | FSCORE | Debt/Eq |
|---|---:|---:|---:|---:|---:|---:|---:|
| none (0 raises) | 23,515 | 11.34 | 1.315 | **0.326** | 0.098 | 5.0 | 1.073 |
| occasional (1) | 9,422 | 13.00 | 1.222 | 0.272 | 0.089 | 4.0 | 1.199 |
| **serial (≥2)** | 6,260 | 12.71 | 1.216 | **0.211** | 0.092 | 4.0 | 1.237 |

Serial raisers have **35% lower trailing ROIC** (0.211 vs 0.326), a lower F-score and more leverage.
That configuration produces a *low* PB and a *high* PE at the same time, because the earnings
denominator is the thing that fell. **The most defensible reading of the PE gap is depressed and
diluted earnings power, not a premium the market chose to pay.** Either way it is the opposite of the
discount the question asked about.

---

## 4. Q2b — value-matched forward returns: the cheapness is compensation

Monthly rebalanced, equal-weight, **within** valuation quintile: serial leg minus non-raiser leg,
both legs ≥3 names. One observation per month ⇒ non-overlapping by construction.

| Sort | Variant | months | spread /mo | NW t (lag 6) | boot p | annualised | IS t | OOS t |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| ey | **RAISE_SET** | 197 | **−0.886%** | **−3.98** | <.001 | **−10.55%** | −3.96 | −1.86 |
| by | RAISE_SET | 197 | −1.137% | −5.60 | <.001 | −13.20% | −4.40 | −3.61 |
| ey | V-WIDE | 197 | −0.462% | −2.76 | .005 | −5.72% | −2.95 | −1.03 |
| by | V-WIDE | 197 | −0.632% | −4.03 | <.001 | −7.57% | −3.61 | −1.99 |
| ey | V-ALL | 197 | −0.254% | −1.55 | .150 | −3.37% | −2.03 | −0.13 |
| by | V-ALL | 197 | −0.290% | −1.74 | .081 | −3.74% | −2.70 | +0.61 |

**Unmatched levels** (what each leg actually earned, no valuation matching):

| Variant | ADV floor | serial /mo | non-raiser /mo | spread t | median PE serial vs base | median PB serial vs base |
|---|---|---:|---:|---:|---|---|
| RAISE_SET | none | +0.061% | +1.152% | −5.00 | 11.62 vs 10.63 | 1.06 vs 1.16 |
| RAISE_SET | ≥2bn | **−0.153%** | **+1.024%** | −4.72 | 13.37 vs 12.00 | 1.22 vs 1.32 |
| V-WIDE | ≥2bn | +0.357% | +0.971% | −3.27 | 12.90 vs 11.93 | 1.29 vs 1.26 |
| V-ALL | ≥2bn | +0.623% | +0.678% | −0.28 | 12.66 vs 12.45 | 1.32 vs 1.22 |

Serial raisers earned **roughly zero to slightly negative** per month over 16 years while non-raisers
compounded at ~1%/month. The gap is not a valuation artifact — it survives matching.

### 4.1 Where it weakens: size matching plus the liquidity floor

Sixteen specifications, crossing sort variable × size matching × the production ADV ≥ 2bn gate. **All
sixteen are negative in sign, in both IS and OOS.** But the most demanding cells lose significance:

| Spec | spread /mo | NW t | boot p | annualised | IS t | OOS t |
|---|---:|---:|---:|---:|---:|---:|
| ey, RAISE_SET, size-matched, ADV≥2bn | −0.896% | −2.24 | .012 | −11.28% | −1.96 | **−1.20** |
| by, RAISE_SET, size-matched, ADV≥2bn | −0.410% | **−1.04** | **.273** | −6.23% | −1.06 | −0.27 |
| ey, V-WIDE, size-matched, ADV≥2bn | −0.450% | −1.72 | .074 | −5.87% | −1.28 | −1.36 |
| by, V-WIDE, size-matched, ADV≥2bn | −0.271% | −0.96 | .300 | −3.89% | −0.45 | −1.42 |

In the slice this book can actually trade, once size is also matched, the effect is **directionally
consistent but statistically marginal, and insignificant out of sample.**

---

## 5. Decision-matrix lookup — the verdict was fixed in advance

PREREG §4 committed the mapping. The primary Q2a `serial` coefficient is **negative (richer, not
cheaper)**, which lands on:

> *negative (richer) → **DESCRIPTIVE / RISK** — the premise of the question is not supported.*

Two further preregistered rules bind and both point the same way:

1. **Sign consistency across the three raise-set variants.** PREREG: *"If the three disagree in
   sign, the verdict is DESCRIPTIVE regardless of any single p-value."* On `ey` they read −0.01350
   (RAISE_SET), −0.00821 (V-WIDE), **+0.00030** (V-ALL). The literal `event_code='ISS'` definition
   from the dispatch gives essentially zero. The result is specific to the cash-raise definition.
   That is economically coherent — stock dividends and bonuses are ubiquitous and raise no capital —
   but by the rule as written it caps the headline at DESCRIPTIVE.
2. **`Edge rớt OOS = loại`.** Q1's primary horizon fails OOS; Q2b's investable, size-matched spread
   fails OOS. Neither survives the fleet's standing bar.

**Final verdict: RISK / DESCRIPTIVE. Not an alpha candidate.**

---

## 6. What this does and does not license

**Supported by these numbers:**

- Repeated external capital raising is a **negative marker**, not a source of cheapness. Serial
  raisers are structurally less profitable (ROIC 0.211 vs 0.326), more levered, and their forward
  returns are worse at matched valuation in all 16 specifications tested.
- **Rights issues** are the one subtype with a floor-clearing negative long-run BHAR (−9.67% at 1Y,
  N=420/277 tickers). ESOP, stock dividend and bonus are flat — Sprint 4's null extends to the long
  horizon for those.
- A cheap **PB** on a serial raiser should not be read as a value opportunity: the same names carry a
  high PE, weak profitability, and negative matched-valuation forward returns.

**NOT supported, and specifically not claimed:**

- **No causal claim that issuing capital destroys value.** The far placebo (+30.2%) and pre-trend
  (+45.5%) mean the long-run BHAR cannot be disentangled from reversal of the pre-raise run-up. The
  incremental cash-raise effect after conditioning is −5.5pp at 1Y, not −7.7pp, and even that is a
  regression coefficient, not an experiment.
- **No tradable edge.** The investable, size-matched spread is insignificant OOS. Nothing here is a
  screen to wire.
- **No market-cap-based inference.** `OShares` is restated and was not used, so every size statement
  rests on ADV. A genuine omitted-variable limitation, declared in PREREG §1, not discovered late.
- **No announcement-window claim.** `public_date` is `WEAK_UNVERIFIED_VINTAGE`; announcement studies
  stay blocked until a second `corporate_action` vintage exists (ledger C1, ≈2026-09-12).
- **DSR/PBO were not computed** — deliberately, per PREREG §5: no configuration was selected for
  deployment. If anyone later wants to turn the `ey`-sorted spread into a screen, that is where
  DSR/PBO and a quant-skeptic gate become mandatory, and the OOS failure above must be resolved
  first.

## 7. Known limits

1. **Reversal confound (dominant).** §2.1. The clean version of Q1 would match each issuer to a
   non-issuer on prior 12-month return; that is a design change, not a robustness tweak, and was not
   preregistered.
2. **No market cap.** ADV is a liquidity proxy, not size. A small-cap tilt inside the serial group
   cannot be fully excluded — though size-tercile matching (R2) leaves the `ey` spread intact.
3. **Delisting returns unobserved.** Forward returns require a consecutive month-end; the gap rate is
   0.0078% of rows (5 rows of 64,068), so this is negligible here, but the return of a name that
   vanished is missing rather than set to −100%.
4. **Q2a is an association, not a decomposition.** It cannot separate "market applies a discount/
   premium" from "the accounting denominator moved". §3.1 argues the latter dominates; that argument
   rests on the ROIC/PB pattern, not on a formal test.
5. **`n_all_3y` covers ~48% of firm-months** (stock dividends are near-universal), so V-ALL is close
   to a coin-flip split and has little power by construction. Its null is uninformative, not
   evidence against the primary.
6. **One vintage of `corporate_action`.** Amendment rate still unmeasured; anchoring on
   `exright_date` avoids the worst exposure but does not eliminate it.

## 8. Reproducing

```bash
cd mike/agents/Taylor/research/serial_capital_raiser_20260817
python3 build.py             # read-only BQ pulls -> out/   (~53s, ~0.7 GB scanned)
python3 analyze.py           # preregistered estimates      (~2.5 min)
python3 robust.py            # post-hoc robustness (R1-R4)  (~37s)
python3 selfcheck_serial.py  # 28 tests; --offline skips the 2 BQ ones
```

Machine-readable: `out/results.json` (preregistered), `out/robust.json` (post-hoc),
`out/selfcheck.json`, `out/q1_bhar.csv`, `out/q2_panel.csv`, `out/sql/*.sql` (every query as issued).
Design committed before outcomes at `eccab390`.
