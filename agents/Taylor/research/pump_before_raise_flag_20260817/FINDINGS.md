# Pre-raise high-momentum issuers — threshold, sector, beta

Job `Taylor_20260817_101337`, 2026-08-17. Follow-up to `serial_capital_raiser_20260817` (`ec3fd8d2`).
Design locked at **`4835d3f2` before any outcome below was computed**. Selfcheck **55/55 PASS**,
identical under `env -u TZ`, `TZ=UTC` and `TZ=America/Chicago`.

**Vocabulary (PREREG §0).** The construct is a *pre-raise high-momentum issuer* — a statistical
condition on realised excess return before an ex-date. Nothing here identifies intent, and no
company named below is characterised as having done anything improper. High momentum before a raise
is exactly what a company with genuinely improving results also looks like; separating the two is
the problem, not the assumption.

---

## Answer first

| Question asked | Answer |
|---|---|
| Is there a pre-trend threshold T that flags raises which then underperform at 1 year? | **No. `NO-FLAG`.** All seven thresholds fail the preregistered gap test; every CI spans zero, every Holm-adjusted p = 1.000. Flagged and unflagged raises both return ≈ −7% to −9%. |
| Does the same threshold work at 2–3 years? | **Yes, strongly** — up to **−33pp at 3Y**, monotone in T, significant at all seven thresholds, and it survives the IS/OOS split. But 3Y was preregistered as *context*, not as the decision horizon, so this is a **hypothesis for a fresh prereg, not a validated flag**. |
| Do securities firms raise more often? | **Yes, clearly** — 2.54 raises per brokerage vs 1.99 elsewhere; 73% have ≥2 vs 49%. And they raise after **roughly double** the run-up (+83% vs +42%). |
| Do securities firms then underperform more? | **No.** −6.1% vs −7.7% for everyone else — gap +1.6pp, CI spans zero. Below the verdict floor either way (66 events / 26 tickers). |
| Does beta predict post-raise underperformance? | **Yes, monotonically**, and the canonical `risk_rating` bin independently agrees. β>1.2 costs **−13.5pp** vs β≤1.2 [−21.8, −5.5]. But it is **insignificant out of sample** and 2010 carries half the effect ⇒ under this fleet's standing bar, **not deployable as a return predictor**. |
| Is "high pre-trend AND high beta" the dangerous cell? | **Cannot be answered.** n = 8 events / 7 tickers. Declared underpowered in advance; no verdict. |

**Nothing is proposed for wiring as a return predictor.** `FLAG_SPEC.md` specifies the flag as an
**informational disclosure** only, which is what `due_diligence.py` already is by design.

---

## 1. Sample

Inherited unchanged from the prior program: `exright_date` anchor, `universe_pit` PIT gate on the
anchor date itself, horizons counted in the ticker's **own** sessions, `PE`/`PB`/`ROIC` read as
stored. Selfcheck CC5 asserts this program's event keys are byte-identical to that panel's 2,953.

| Population | Events | Tickers |
|---|---:|---:|
| Mục 1 primary — RIGHTS ∪ PRIVATE_PLACEMENT, with pre-trend and 1Y outcome | **590** | **312** |
| Mục 1 sensitivity — RAISE_SET (adds AUCTION) | 608 | 321 |
| Mục 3 — same subtypes, 1Y outcome (a beta test needs no pre-trend) | 646 | 336 |
| Mục 2 — all ISS events, for frequency | 2,953 | 578 |

New fields, all point-in-time and asserted so by selfcheck: fundamentals from the last session
**strictly before** the ex-date (0/2,953 violations); a 250-session beta computed on `[t0−250, t0−1]`
only; `risk_rating` from a quarter **strictly before** the event's own quarter (0/2,263 violations).

**Reproduced before producing anything new** (CC1/CC2): pooled BHAR_250 over RAISE_SET
**−7.7425%, n=712**; pre-trend **+45.5400%**; far placebo **+30.2121%** — the prior program's three
published numbers, to 5 decimal places.

---

## 2. Mục 1 — the threshold does not separate anything at one year

`suspected = pretrend_250 > T`. Gap = mean BHAR_250(suspected) − mean BHAR_250(rest); block
bootstrap on anchor year-month, Holm across the seven grid points.

| T | n susp / rest | tickers susp / rest | BHAR susp | BHAR rest | **gap** | 95% CI | Holm p | FPR |
|---:|---:|---:|---:|---:|---:|---|---:|---:|
| 15% | 312 / 278 | 205 / 199 | −7.35% | −7.53% | **+0.18pp** | [−8.84, +9.98] | 1.000 | 28.8% |
| 20% | 297 / 293 | 197 / 206 | −8.42% | −6.44% | −1.98pp | [−10.91, +7.97] | 1.000 | 27.8% |
| 25% | 271 / 319 | 181 / 214 | −7.99% | −6.97% | −1.02pp | [−10.41, +9.67] | 1.000 | 29.1% |
| 30% | 251 / 339 | 171 / 224 | −8.47% | −6.67% | −1.79pp | [−10.98, +9.06] | 1.000 | 29.3% |
| 40% | 213 / 377 | 154 / 235 | −8.98% | −6.56% | −2.41pp | [−12.38, +9.81] | 1.000 | 29.4% |
| 50% | 190 / 400 | 137 / 244 | −8.08% | −7.13% | −0.96pp | [−11.72, +12.52] | 1.000 | 30.1% |
| 60% | 171 / 419 | 129 / 251 | −9.57% | −6.57% | −3.00pp | [−13.96, +11.26] | 1.000 | 29.9% |

Every T clears the power floor. Every T clears the false-positive requirement (28–30% vs a 40%
ceiling; 26.7–28.3% using within-year medians instead). **No T clears the gap requirement** — not
one CI excludes zero, and the largest gap (−3.0pp) is well short of the −5pp bar. Per PREREG §2
step 5 the verdict is **`NO-FLAG`**, and the same holds on the RAISE_SET sensitivity (gaps −0.3pp to
−3.6pp, all Holm p = 1.000).

Read plainly: **among companies that raise cash, how much they ran up first tells you essentially
nothing about the next twelve months.** The run-up matters for whether they underperform *the
market* — the prior program established that, and both legs here do underperform by ~7–9% — but it
does not sort the population.

The false-positive rate is worth stating in its own right. At every threshold, **≈29% of flagged
raises have both above-median trailing ROIC and a Piotroski score above 4.** Roughly three in ten
names the flag fires on look like healthy companies raising after a genuinely good run. That is the
irreducible ambiguity the dispatch asked about, quantified: this design cannot separate a deliberate
run-up from an earned one, and the flag would be wrong about a third of the time even if the returns
had cooperated.

### 2.1 At two and three years the same threshold is strongly informative

The 500/750-session gaps were preregistered as *context*. Their CIs are a deviation (D-2) added
because a bare point estimate invites exactly the over-reading this program exists to prevent.

| T | gap 2Y | 95% CI | Holm p | gap 3Y | 95% CI | Holm p |
|---:|---:|---|---:|---:|---|---:|
| 15% | −13.48pp | [−25.5, −2.2] | .027 | −26.40pp | [−43.1, −10.7] | .001 |
| 25% | −14.57pp | [−25.7, −4.2] | .027 | −27.69pp | [−42.3, −13.7] | .001 |
| 40% | −18.91pp | [−29.8, −8.4] | .004 | −29.74pp | [−43.0, −16.7] | <.001 |
| 50% | −21.84pp | [−32.0, −12.0] | <.001 | −32.63pp | [−45.6, −19.6] | <.001 |
| 60% | −23.54pp | [−33.8, −13.7] | <.001 | **−33.12pp** | [−46.9, −19.7] | <.001 |

Significant at all seven thresholds after Holm, and **monotone in T** — a higher bar flags a smaller,
worse group, which is what a real ordering looks like and what noise generally does not do. At
T = 60% the 3Y gap survives the split: **IS −39.4pp** [−57.8, −20.5] p<.001 (101 vs 254 events),
**OOS −20.0pp** [−35.2, −5.0] p=.011 (59 vs 99). The 2Y version likewise (IS −26.8pp p<.001, OOS
−19.1pp p=.025).

This is coherent with the prior program's independent finding that the 3-year horizon was the one
holding in both halves while the 1-year did not, and with its pre-trend-quartile table where damage
concentrated at long horizons in the biggest-run-up quartile. Two caveats keep it a hypothesis
rather than a result: the horizon was not the preregistered decision variable, and a 3Y outcome
requires 750 forward sessions, so that sample stops at 2023 and is 69% pre-2020 (vs 60% at 1Y).

**What to do with it:** a separate preregistration in which 3Y is the primary horizon, with the
holding-period question answered honestly first — a 3-year abnormal return is not something this
book's machinery trades. It is a *risk-marker* horizon, not an entry signal.

### 2.2 Why the 1Y verdict was not rescued

At the least-bad T (60%) the 1Y gap is **+1.1pp in-sample and −9.1pp out-of-sample** — a sign flip,
with both halves insignificant — and 2010 alone carries **55.7%** of the flagged group's mean
(dropping 2010 moves it from −9.57% to −5.04%). Both preregistered kill conditions fire. Even had a
T squeaked through the gap test, PREREG §2 would have labelled it IS-ONLY.

---

## 3. Mục 2 — securities firms raise far more often, but do not fall further afterwards

Securities = **ICB 8777, Investment Services** (32 tickers: SSI, HCM, SHS, MBS, VND, BSI, FTS, CTS,
AGR, ORS, EVS, …). Verified by inspecting membership, and asserted disjoint from Banks (8355) by
selfcheck. Codes whose membership did not clearly match their ICB name are printed as
`ICB <code> (unverified label)` rather than guessed.

**Frequency — the user's intuition is confirmed, and it is the sharpest sector result here:**

| | Securities (8777) | All other sectors |
|---|---:|---:|
| Cash raises per company | **2.54** | 1.99 |
| Companies with ≥2 raises | **73.1%** | 49.1% |
| Companies with ≥3 raises | **38.5%** | 24.7% |
| All ISS events per company | **6.53** | 5.03 |
| Companies with ≥2 ISS | **90.6%** | 75.6% |
| Mean pre-raise 1Y excess return | **+82.95%** | +41.69% |

Brokerages raise capital half again as often as everyone else, and they do it after roughly
**double** the run-up. That combination is exactly the pattern the dispatch described, and it is
real in the data. It also has an unremarkable explanation available: brokerage earnings are
levered to market activity, so their share prices rise *because* the market rose, and margin-lending
capacity is regulatory-capital-constrained, so a rising market is simultaneously when the stock is
up and when more equity is genuinely needed. This design cannot choose between the two readings.

**Outcome — the pattern does not carry a penalty:**

| Cut | n events / tickers | BHAR_250 | gap vs rest | 95% CI | p |
|---|---:|---:|---:|---|---:|
| Securities, cash raises | 66 / 26 | −6.11% | +1.58pp | [−10.65, +14.30] | .81 |
| Securities, all ISS | 209 / 32 | +2.53% | +5.10pp | [−2.73, +13.98] | .21 |

Both are **below the preregistered verdict floor** (100 events / 60 tickers) — 26 brokerages is
simply too few companies. Reported as descriptive, no verdict. What can be said is that there is no
sign of *worse* outcomes; if anything the point estimate leans the other way.

**Sector table, cash raises** (`•` = below verdict floor):

| ICB | Sector | events / tickers | raises per ticker | ≥2 raises | BHAR_250 | 95% CI |
|---:|---|---:|---:|---:|---:|---|
| 8633 | Real Estate Holding & Development | 124 / 51 • | 2.43 | 58.8% | −2.56% | [−11.8, +7.5] |
| 2357 | **Heavy Construction** | **119 / 64** | 1.86 | 54.7% | **−23.65%** | **[−31.2, −13.9]** |
| 8777 | Investment Services | 66 / 26 • | 2.54 | 73.1% | −6.11% | [−17.4, +6.0] |
| 2353 | Building Materials & Fixtures | 50 / 27 • | 1.85 | 51.9% | −13.25% | [−39.0, +29.8] |
| 8355 | Banks | 41 / 17 • | 2.41 | 52.9% | +3.57% | [−6.2, +14.6] |

**The one sector clearing the verdict floor is Heavy Construction, and it is the worst by a wide
margin** — −23.7% at one year, CI comfortably clear of zero, on 119 events across 64 companies. That
was not something the dispatch asked about and it has not been through the stability checks the
other results here have, so it is flagged as the most interesting unplanned observation in this
program, not as a finding.

**Top-20 companies by ISS count, 2010–2026** (all ISS, including stock dividends and bonuses, which
raise no cash):

VIC 69 (4 cash) · CII 34 (0) · FPT 34 (0) · NVL 33 (5) · DXG 31 (**10**) · KDH 29 (6) · SSI 26 (4) ·
MBB 26 (7) · TNG 24 (1) · HBC 24 (3) · MSN 22 (6) · NLG 21 (4) · HUT 19 (**8**) · GMD 18 (3) ·
DIG 18 (5) · HSG 17 (1) · SHI 17 (**7**) · SHB 17 (4) · HDG 17 (1) · MWG 17 (1)

The list is dominated by real estate (VIC, NVL, DXG, KDH, NLG, DIG, HDG) and construction/
infrastructure (CII, HBC, HUT) rather than by brokerages — SSI is the only 8777 name in it. Total
ISS count is a poor proxy for cash raising: FPT and CII appear near the top with **zero** cash
raises between them, because stock dividends and bonuses are near-universal among large VN names.

---

## 4. Mục 3 — beta orders post-raise returns, and two independent measures agree

Primary beta is a 250-session OLS coefficient vs VNINDEX on `[t0−250, t0−1]` (coverage 93.8%,
median 0.98). **Deviation D-B1, declared in the prereg before any outcome:** `tav2_bq.risk_rating.Beta`
cannot carry the dispatched 1.2/1.8 cut points — it is an integer **1–5 bin** (SSI reads 5.0 in
every recent quarter) and is NULL on 84.4% of table rows. Applying "≤1.2" to it would silently have
meant "bin 1 only".

| Bin | n / tickers | mean β | BHAR_250 | 95% CI | Holm p | mean pre-trend |
|---|---:|---:|---:|---|---:|---:|
| low (β ≤ 1.2) | 410 / 257 | 0.70 | **−2.72%** | [−9.7, +4.7] | .445 | +50.1% |
| mid (1.2 < β ≤ 1.8) | 205 / 137 | 1.45 | **−15.95%** | [−21.1, −10.1] | <.001 | +39.9% |
| high (β > 1.8) • | 31 / 24 | 1.98 | **−18.24%** | [−27.0, −8.0] | .001 | +87.8% |

Monotone decreasing, and high−low = **−15.5pp** [−27.6, −3.0], p = .018 ⇒ **ordering detected** by
the preregistered criterion. The dispatched `high` bin holds only 31 events and is **below the power
floor**, so the powered version of the same ordering merges the two preregistered upper bins:

> **β > 1.2 vs β ≤ 1.2: −13.5pp** [−21.8, −5.5], p = .001 — 236 events / 146 tickers vs 410 / 257.

**Independent corroboration.** The canonical `risk_rating` bin, a different measure built by someone
else on a different method, reproduces the ordering on its own scale: bins 1–2 **+2.4%**, bin 3
**−1.6%**, bins 4–5 **−12.3%** [−17.5, −6.7]. Its correlation with the computed coefficient is
+0.55, and mean computed beta rises monotonically across its bins (0.75 → 0.92 → 1.35). Two
constructions, one ordering.

**What beta is not a proxy for here.** Pre-trend is *not* monotone across the bins (+50%, +40%,
+88%), so this is not the Mục 1 result restated. And the high-beta group is not the small illiquid
tail — it is the **most** liquid (median ADV60 **19.9bn** vs 3.6bn for low beta), the **most**
profitable on trailing ROIC (0.349 vs 0.285), and 45% brokerages by count. High beta here means
large, liquid, market-sensitive names.

**Why it still does not clear the bar.** IS −16.6pp [−26.7, −6.8] p=.001; **OOS −8.4pp [−22.2, +4.2]
p=.20**. No sign flip, but the out-of-sample half is insignificant, and 2010 carries **50.1%** of the
high-beta leg. Under `Edge rớt OOS = loại` this is a risk marker, not a return predictor.

**Combined cut (`pre-trend > 60%` AND `β > 1.8`): 8 events, 7 tickers.** Declared underpowered in
advance; mean −16.2%, gap −8.7pp [−27.7, +11.9], p=.36. **No verdict, and it is not in `FLAG_SPEC`
as a recommendation.** The two conditions barely co-occur — which is itself informative: the
dangerous-sounding intersection is largely hypothetical in this sample.

---

## 5. What this licenses

**Supported:**
- Securities firms raise external capital markedly more often than other sectors, after markedly
  larger run-ups. Frequency and pre-trend, not outcome.
- Post-raise abnormal returns are ordered by beta, monotonically, with two independent beta
  measures agreeing — in-sample.
- The pre-trend threshold is informative at 2–3 years, monotone in T, robust across IS/OOS.
- ≈29% of any pre-trend-flagged raise cohort consists of companies with healthy ROIC and F-score.

**Not supported, and specifically not claimed:**
- **No 1-year flag.** The preregistered question returns `NO-FLAG` at every threshold tested.
- **No claim that any company timed a raise deliberately.** Pre-trend, sector and beta are all
  consistent with earned run-ups; the dispatch's own concern — separating intent from performance —
  remains unresolved and is not resolvable with this design.
- **No sector verdict for securities.** 26 companies is below the floor set in advance.
- **No deployable beta screen.** OOS insignificant, half the effect from 2010.
- **No combined "most dangerous group" claim.** n=8.
- **No causal reading of the long-horizon gaps.** The prior program's +45.5% pre-trend and +30.2%
  far placebo mean post-event underperformance still cannot be separated from reversal.
- **No announcement-window analysis** — `public_date` stays `WEAK_UNVERIFIED_VINTAGE` until a second
  `corporate_action` vintage (≈2026-09-12).
- **DSR/PBO not computed**, deliberately: nothing was selected for deployment. They become mandatory
  if anyone proposes wiring the 3Y version as a screen.

## 6. Limits

1. **N trials = 11** declared in advance (7 thresholds + 3 beta bins + 1 combined), Holm applied
   within each family. The D-2 long-horizon CIs add two further families of 7, Holm-adjusted
   separately and never pooled with the primary.
2. **Reversal confound**, inherited and dominant — see prior program §2.1.
3. **No market cap.** `OShares` is restated, not point-in-time; every size statement rests on ADV.
4. **The 3Y sample ends in 2023** by construction and is 69% pre-2020.
5. **The FPR definition is the dispatch's**, and it is a *proxy for* genuineness, not a measurement
   of it. A company can have strong trailing ROIC and still have had a run-up detached from it.
6. **One `corporate_action` vintage**; amendment rate unmeasured.
7. **Heavy Construction's −23.7%** is an unplanned observation that has had none of the stability
   checks applied to the preregistered results. Treat as a lead, not a finding.

## 7. Reproducing

```bash
cd mike/agents/Taylor/research/pump_before_raise_flag_20260817
python3 build_extras.py                          # read-only BQ pull -> out/extras.csv  (~14s)
python3 analyze.py                               # executes PREREG                      (~10s)
python3 selfcheck_pump_flag.py                   # 55 tests, offline
python3 selfcheck_pump_flag.py --rerun-foreign-tz # same 55 under unset/UTC/Chicago TZ
```

Machine-readable: `out/results.json`, `out/extras.csv`, `out/selfcheck.json`, `out/sql/extras.sql`.
Deviations from the locked design: `DEVIATIONS.md`. Flag specification: `FLAG_SPEC.md`.
