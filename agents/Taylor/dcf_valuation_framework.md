# DCF Valuation Framework — 2-stage FCFE intrinsic value for VN non-financial equities

> Author: Taylor (quant). Job `Taylor_20260714_042622`. Status: **research / reference tool,
> NOT wired into production trading** (custom30V / BAL / LAG / rating_8l.py unchanged).
> Code: `dcf_valuation.py` (single-ticker API + CLI), `dcf_backtest.py` (calibration + walk-forward IC).

## 1. Purpose & where it fits

The 8L system values names **relatively**: P/E vs its own history, P/B vs Gordon, EV/EBITDA vs
sector. All of these answer "cheap **vs what it usually trades at / vs peers**" — they inherit
whatever premium the market has always paid. This DCF adds an **absolute** anchor: an estimate of
intrinsic value from the cash a business actually throws off to equity holders, discounted at a
VN-appropriate cost of equity. Before buying a discretionary name (AlphaLens / DC-book / sector
watchlist BUY), running the DCF answers a different question: *am I paying below or above what the
cash flows are worth on their own?* — reducing dependence on purely market-relative signals.

It is a **discretionary reference check** in the existing flow (Taylor validate → DollarBill plan
→ user approve → Mafee), **not** an automatic selector.

## 2. Scope — NON-FINANCIAL only

Excludes **BANK / INSURANCE / SECURITIES** (via the point-in-time 8L `route`; ICB fallback
8355 / 853x-857x / 877x). For financials, leverage *is* the product and FCFE-DCF is meaningless —
they keep their own Gordon-P/B models (`banking_/securities_/insurance_valuation_framework.md`).

## 3. The model (2-stage FCFE)

```
Fair value / share = [ Σ_{i=1..5} FCFE0·(1+g)^i / (1+r)^i
                       + FCFE0·(1+g)^5·(1+g_term)/(r − g_term) / (1+r)^5 ] / OShares
Margin of safety   = (fair_value − price) / fair_value          (price = unadjusted `Price`)
```

| Input | Value / source | Notes |
|---|---|---|
| **FCFE0** (base cash flow) | normalized 3Y-avg free cash flow to equity = `(CF_OA_3Y + CF_Invest_3Y)/3` | CF_OA / CF_Invest are **absolute VND** in `ticker_financial` (not ratios, despite the dictionary label). CF_Invest is negative (capex + net investing). Net borrowing assumed ~0 (stable capital structure). 3Y-avg smooths lumpy single-year capex. |
| **r** (cost of equity) | Big-4 12M deposit rate (as-of, `deposit_rate_vn.py`) **+ ERP 6.5%** | e.g. 2026-06: 6.8% + 6.5% = **13.3%** |
| **g** (stage-1, 5y) | `shrink·recency_blend(g1,g2,g3) + (1−shrink)·g_term`, clipped **[−10%, +25%]** | equal-weight blend of 3 trailing annual TTM-earnings growths; **shrink = 0.5** (see §4.1). |
| **g_term** (terminal) | trailing **5Y avg headline CPI** (as-of, `cpi_vn.py`) | 2026-06 ≈ **3.4%** |
| **OShares** | shares outstanding (`ticker_financial`) | per-share denominator |

**Gate (DCF returns "not computed" + reason otherwise):**
`CF_OA_3Y > 0` (reuse of the 8L golden-floor cash gate) **AND** `FCFE0 > 0` **AND** `OShares > 0`
**AND** `r − g_term > 0`. No DCF on firms burning free cash during a build-out (the
renewables/utility-buildout lesson) — a spurious negative or explosive value is worse than an
honest "can't value this with FCFE".

## 4. Empirical calibration (numbers chosen from data, not guessed)

### 4.1 Stage-1 growth: recency weighting — **the honest, surprising result**

Requirement was: test recency-weight schemes {equal, 50/30/20, 60/25/15, exp-decay} for predicting
**next-year** actual earnings growth vs an equal-weight 3Y baseline. Panel = one obs per
(ticker, calendar-year last release), non-financial, trailing 3 annual TTM-NP growths → realized
next-year TTM-NP growth. **n = 6,332 firm-years, 2009–2024, 892 tickers** (growths winsorized to [−90%, +200%]).

| window | scheme | rankIC | MAE | corr |
|---|---|---|---|---|
| IS ≤2019 (n=3283) | **equal 1/3** | **−0.104** | **0.623** | −0.137 |
| | 60/25/15 | −0.118 | 0.642 | −0.162 |
| OOS ≥2020 (n=3049) | **equal 1/3** | **−0.199** | **0.662** | −0.204 |
| | 60/25/15 | −0.221 | 0.700 | −0.226 |
| ALL (n=6332) | **equal 1/3** | **−0.151** | **0.641** | −0.171 |
| | 60/25/15 | −0.170 | 0.670 | −0.195 |

Reference (ALL): `g1_only` rankIC −0.134 / MAE 0.776; `mean(g1,g2,g3)` rankIC −0.151 / MAE 0.641.

**Finding: trailing earnings growth *mean-reverts hard*.** A company's own past growth has
**negative** rank correlation (−0.10 IS / −0.20 OOS / −0.15 ALL) with its next-year growth. Consequences measured:
- **Recency weighting does NOT help** — 50/30/20, 60/25/15, exp-decay and equal are within noise
  of each other; recency-tilt is marginally *worse* on MAE than a simple 3Y mean.
- **Multi-year averaging DOES help** — any 3-year average beats recent-quarter-only on MAE
  (~0.72 vs ~0.84, −14%). Stability, not recency, is what reduces error.
- **Heavy shrinkage toward a low anchor is MAE-optimal** — pushing the extrapolated growth toward
  the terminal/median anchor (~3%) monotonically reduces next-year MAE; the 1-year-ahead
  MAE-optimum is literally *full* shrink (k=0, i.e. "assume ~median growth").

**Design decision:** use **equal weights** (recency didn't earn its complexity) and **shrink 0.5**
toward terminal. k=0 is MAE-optimal but zeroes out all company differentiation (every firm becomes
the median), which defeats the purpose of a per-name valuation; **k=0.5 keeps half the
company-specific signal at a modest, documented accuracy cost.** This is a deliberate
interpretability-vs-accuracy trade, stated openly — not a hidden fudge. The hard cap [−10%, +25%]
is the "high-growth caveat": DCF must never extrapolate a hot recent number to infinity.

### 4.2 Equity risk premium — **6.5%**

Measured as the VNINDEX total-return premium over the Big-4 deposit rate:
VNINDEX price CAGR ≈ **11.5%** (2013-2026, cache start) + ~1.7% assumed dividend yield ≈ 13.2% TR,
minus Big-4 deposit avg ≈ 6.8% → **ERP ≈ 6.3–6.6%** across 2009/2012/2014 start windows. Central
estimate **6.5%**. (Damodaran-style VN mature-ERP + country-risk lands ~7–8% = upper bound;
6.5% is the direct empirical premium and is the pinned default.) *Caveat:* the cache's VNINDEX
history starts 2013 (a post-2012 recovery low), so the price CAGR carries endpoint sensitivity;
6.5% is a deliberately central, not aggressive, choice.

### 4.3 Terminal growth = 5Y-avg CPI

`cpi_vn.py` has clean monthly CPI 2011-01 → 2026-06 (Tier-1 real NSO for the last 13 months,
Tier-2 proxy before). Trailing-5Y average as-of 2026-06 ≈ **3.37%** (annual averages 2021-2025:
1.8 / 3.4 / 3.2 / 3.7 / 3.4%). Point-in-time by construction (sliced to `time ≤ asof`).

## 5. Sensitivity (know the tool's limits)

DCF is famously sensitive to r and terminal value. Measured on the demo names (as-of 2026-07-13):

| perturbation | CTR: FV (Δ%) → MoS | DHG: FV (Δ%) → MoS |
|---|---|---|
| base | 52,564 → −40.4% | 51,614 → −79.2% |
| r **−1%** | 58,591 (+11.5%) → −26.0% | 57,307 (+11.0%) → −61.4% |
| r **+1%** | 47,645 (−9.4%) → −54.9% | 46,962 (−9.0%) → −97.0% |
| g_stage1 **−2%** | 48,511 (−7.7%) → −52.1% | 47,510 (−8.0%) → −94.7% |
| g_stage1 **+2%** | 56,904 (+8.3%) → −29.7% | 56,023 (+8.5%) → −65.1% |

So a 1-percentage-point view on the discount rate moves intrinsic value ~±10%, ±2% growth ~±8% — the
margin-of-safety should be read with a **wide band**, not to the decimal. **But note the verdict is
robust to the whole ±1%r / ±2%g box: even at the most favorable corner (r−1%) both CTR and DHG stay
RICH** (−26% / −61%). Rule of thumb: distrust any MoS that *flips sign* inside that box — it is noise,
not signal. `dcf_valuation.py` prints the sensitivity grid on every single-name run.

## 6. Demo — 5 Group-A watchlist names (as-of 2026-07-13, r=13.30%, g_term=3.40%)

| Ticker | Sector | FCFE0 (B/yr) | g_stage1 | Fair value | Price | Margin of safety | DCF read | sector_lens (RELATIVE) |
|---|---|---|---|---|---|---|---|---|
| **MSH** | Textile | — | — | — | 31,750 | — | **no positive FCFE** (capex > CFO) | BUY/ACCUM · PE 5.70 cheap |
| **PVT** | Logistics (tanker) | — | — | — | 18,950 | — | **no positive FCFE** (fleet build-out) | BUY/ACCUM · PB 0.83 trough |
| **HAH** | Logistics (container) | — | — | — | 50,800 | — | **no positive FCFE** (ship build-out) | BUY/ACCUM · EVEB 4.21 cheap |
| **CTR** | Viettel-infra | 505 | +6.6% | 52,564 | 73,800 | **−40.4%** | **RICH** | BUY/ACCUM · EVEB 9.74 (<11 accum) |
| **DHG** | Pharma | 722 | +0.7% | 51,614 | 92,500 | **−79.2%** | **RICH** | BUY/ACCUM · PE 13.4 < MA5Y 15.05 |

**The DCF disagrees with the relative lens on all 5 — and that disagreement is exactly the point of an absolute lens:**
1. **3 of 5 (MSH / PVT / HAH) fall in the DCF blind spot** — capex-heavy expanders whose FCFE is currently
   negative (investing outflow > operating cash during build-out). The DCF correctly **abstains** rather than
   fabricate a value; the *right* tool for these is precisely what sector_lens uses (asset-based PB / EV-based
   EVEB, which handle reinvestment). This is a **coverage boundary, not a contradiction** — the two lenses cover
   different name types.
2. **CTR & DHG compute and both read RICH** despite being "cheap" on the relative lens — the **value-trap warning**:
   - **DHG is the archetype**: cheap vs its **own 5Y PE history** (13.4 vs 15.05) but ~80% above intrinsic on
     discounted cash flows, driven by **declining trailing earnings** (g2 −10.2%, g3 −16.6%) against a rich 92,500
     price. Relative-cheap, absolute-expensive — precisely what this lens is built to flag.
   - **CTR** is milder: EVEB 9.74 sits in sector_lens's *accumulate* band but *not* the `<9` *strong* band, and the
     DCF's −40% MoS agrees it is no longer a bargain in absolute terms after the run to 73,800.
3. **Level bias, use ranks not the line.** A conservative FCFE-DCF (all-investing netted out, growth shrunk toward
   CPI, ~13% VN discount rate) sits *below* the price the market pays for durable compounders — so a RICH reading is
   normal for quality names and the DCF's value is in **cross-sectional ranking / value-trap flags**, not an absolute
   buy/sell line. (Consistent with §5: the ranking is what Study B's +IC actually rewards.)

## 7. Walk-forward IC validation (does margin-of-safety predict forward return?)

`dcf_backtest.py` Study B: FV computed once per financial release (point-in-time), as-of merged onto
a monthly price panel, filtered to the **non-financial rating≤3** universe, cross-sectional Spearman
IC of MoS vs `profit_1M/2M/3M` per month, averaged, walk-forward IS(2014-19)/OOS(2020-26).

Panel: **51,529 rows · 144 months · 959 tickers.** FV releases older than ~15 months dropped as stale;
MoS distribution: mean −3.02, median +0.12, %cheap(MoS>0) 55%.

| window | profit_1M | profit_2M | profit_3M |
|---|---|---|---|
| **ALL 2014–2026** | +0.0444 (t=7.3, hit 72%) | +0.0584 (t=9.4, hit 79%) | +0.0690 (t=11.6, hit 86%) |
| **IS 2014–2019** | +0.0410 (t=4.5) | +0.0508 (t=5.4) | +0.0690 (t=7.5) |
| **OOS 2020–2026** | +0.0473 (t=5.8) | +0.0646 (t=7.9) | +0.0690 (t=8.9) |

Quintile monotonicity (profit_2M, 0=richest → 4=cheapest): **1.70 → 2.24 → 2.68 → 3.24 → 4.94** — clean monotone.

**Verdict: MoS carries a positive, monotone, IS/OOS-stable cross-sectional signal**, strengthening with horizon
(IC 0.044 → 0.069 from 1M → 3M) and — unusually — **OOS ≥ IS** (no overfit decay). The magnitude (~0.05–0.07) is
*modest*, consistent with a value lens: a real edge signal, **not** a stand-alone alpha. It corroborates the 8L thesis
that cheapness predicts — here from an *absolute* (cash-flow) angle, orthogonal to the relative lenses.

> **Run vintages:** `backtest_run.log` (the cache-build run) is authoritative (quintile 3 = 3.24). An earlier
> `/tmp/dcf_ic.log` shows quintile 3 = `inf` — a one-off `qcut` edge artifact; the IC/t figures match to ±0.001
> across both runs. Use `backtest_run.log`.

### 7.1 Robustness — is the IC an artifact of the hindsight-biased discount-rate input?

**The concern (Spyros / risk-auditor, 2026-07-14):** all 26 anchors in `deposit_rate_vn.py` were
calibrated retrospectively on ONE date (2026-06-19); they are **not truly point-in-time** for the
past. The Big-4 deposit series *does* vary materially over 2014-2026 (annual means 6.65→4.78→6.13,
**peak-trough spread 2.8pp, std 0.78pp**), so there is real room for hindsight to have crept into the
historical discount rate — most worrying for the IS 2014-19 number. Separately, the **terminal
growth** (5Y-avg CPI) is *100% proxy* for every as-of date before mid-2025 (the NSO real-print window
only reaches back ~13 months → `frac_real` = 0% pre-2025, ~22% at 2026-06; see §8 and the CLI's
`REAL NSO / PROXY` line).

**The test (`dcf_rate_robustness.py`):** re-run Study B's cross-sectional MoS IC with a **CONSTANT
discount rate** — the single window-mean deposit (5.97%) + ERP 6.5% = **r = 12.47% applied to every
as-of date** — versus the pinned time-varying result. Collapsing the whole series to one number
removes *all* date-level discount-rate information, hindsight included.

| window · target | pinned (time-varying) | **fixed r=12.47%** | Δ |
|---|---|---|---|
| ALL · 1M / 2M / 3M | +0.0444 / +0.0584 / +0.0690 | **+0.0441 / +0.0575 / +0.0680** | −0.0003 / −0.0009 / −0.0010 |
| IS 2014-19 · 1M / 2M / 3M | +0.0410 / +0.0508 / +0.0690 | **+0.0402 / +0.0486 / +0.0665** | −0.0008 / −0.0022 / −0.0025 |
| OOS 2020-26 · 1M / 2M / 3M | +0.0473 / +0.0646 / +0.0690 | **+0.0473 / +0.0649 / +0.0693** | +0.0000 / +0.0003 / +0.0003 |

*(panel 51,367 rows · 144 months · 952 tickers; 4,525 degenerate pre-2014 releases where the constant
low rate collides with the 2011 CPI spike, `g_term ≥ r`, were skipped — all outside the 2014+ eval window.)*

**Verdict: the IC is NOT sensitive to the deposit-rate hindsight.** Even the maximal perturbation —
one constant rate for twelve years — shifts the IC by **≤0.001 (ALL) / ≤0.0025 (IS) / ≤0.0003 (OOS)**,
inside month-to-month noise; the monotonicity and IS/OOS-stability are unchanged. **Why this is
expected, not luck:** the discount rate (and terminal growth) are **date-only** — identical across
every ticker within a given month — so they shift the *level* of every name's fair value on a date
by nearly the same factor, and Study B's IC is a **within-month cross-sectional rank** correlation,
which differences that common level out. Any hindsight in the *level* of the rate is largely
orthogonal to the cross-sectional MoS ranking the IC actually rewards. The same date-only argument
covers the CPI-proxy point (terminal growth being all-proxy pre-2025): it cannot manufacture
cross-sectional signal it doesn't carry.

**Honest residual caveat:** this shows the IC is robust to the discount-rate *level* being wrong; it
does **not** license treating the absolute MoS threshold as point-in-time-clean for the historical
period (consistent with §6.3 "use ranks, not the line"). The IS 2014-19 IC should still be read as
"stable under a large rate perturbation," not "computed from a verified historical rate series." Run:
`DCF_REFRESH=1 $DNA_PY dcf_rate_robustness.py` (writes its own `dcf_exp/fv_releases_fixedrate.parquet`,
never the pinned cache).

### 7.2 Orthogonality — is MoS an independent axis, or just 1/PE with more steps? (Pha 1)

**The concern (Taylor, round-table):** composite-as-selector failed before because the **1/PE dominant
factor absorbed everything** (KNOWLEDGE.md). Before any wire is considered, MoS must be shown to predict
forward return **after neutralizing** the relative value lenses. `dcf_orthogonality_test.py` reuses the
Study B panel (51,529 rows · 144 months · 959 tickers — FV not recomputed) and merges point-in-time
PE / PB / EV-EBITDA onto the same rows (98% / 98% / 96% coverage). **t-stat is on the MONTHLY IC series
(n≈144), a time-series t — NOT the 51k pooled rows** (Spyros: pooling inflates significance since
same-month obs aren't independent). Confirmed correct.

**Step 1 — cross-sectional rank-correlation rank(MoS) vs rank(value proxy)** (per month, averaged):

| pair | ALL | IS 2014-19 | OOS 2020-26 |
|---|---|---|---|
| MoS vs **1/PE** | +0.285 | +0.281 | +0.288 |
| MoS vs 1/PB | +0.334 | +0.334 | +0.334 |
| MoS vs 1/EVEB | +0.346 | +0.292 | +0.388 |

All **modest (0.28–0.39)** — MoS shares direction with the relative lenses but is **far from collinear**
(if MoS were just 1/PE relabeled the correlation would be >0.7). First evidence it is a distinct axis.

**Step 2 — residual IC** (neutralize MoS each month in rank space, IC of the residual vs forward return):

| neutralizer | window | profit_1M | profit_2M | profit_3M |
|---|---|---|---|---|
| **RAW MoS** (baseline) | IS | +0.0410 (t 4.5) | +0.0508 (t 5.4) | +0.0690 (t 7.5) |
| | OOS | +0.0473 (t 5.8) | +0.0646 (t 7.9) | +0.0690 (t 8.9) |
| **MoS ⟂ 1/PE** | IS | +0.0222 (t 2.5) | +0.0271 (t 3.0) | +0.0412 (t 4.4) |
| | OOS | +0.0252 (t 3.3) | +0.0367 (t 4.8) | +0.0373 (t 5.2) |
| **MoS ⟂ 1/PB** | IS | +0.0329 (t 4.1) | +0.0406 (t 4.7) | +0.0565 (t 6.2) |
| | OOS | +0.0332 (t 5.1) | +0.0486 (t 7.0) | +0.0508 (t 8.0) |
| **MoS ⟂ 1/EVEB** | IS | +0.0223 (t 2.6) | +0.0275 (t 3.2) | +0.0425 (t 4.7) |
| | OOS | +0.0170 (t 2.2) | +0.0265 (t 3.4) | +0.0294 (t 3.8) |
| **MoS ⟂ [1/PE,1/PB,1/EVEB]** | IS | +0.0121 (t 1.5) | +0.0133 (t 1.5) | +0.0261 (t 2.8) |
| | OOS | +0.0115 (t 1.7) | +0.0221 (t 2.9) | +0.0212 (t 3.2) |

**Verdict — MoS IS an independent information axis (GO for the axis; qualifies for Pha 2 consideration).**
- After neutralizing **1/PE alone**, MoS keeps **~55–60% of its raw IC and stays significant in BOTH
  IS and OOS at every horizon** (t 2.5–5.2). It is *not* 1/PE measured with a fancier tool — the failure
  mode that killed composite-as-selector does not repeat here.
- Even against **all three** relative value ratios jointly (the hardest test), the residual stays
  **positive and significant at 2M/3M in both windows** (3M: IS t 2.8, OOS t 3.2). Only the short-horizon
  1M/2M IS residual loses significance (t 1.5) — i.e. the incremental edge is **real but concentrated at
  the 2–3 month horizon**, consistent with the raw-MoS horizon-strengthening pattern (§7).
- **Honest magnitude caveat:** the residual is roughly **half** the raw MoS IC — a meaningful share of
  MoS's predictive power IS shared with the relative lenses. DCF is a **modest incremental axis, not a
  large new independent alpha**; strongest at 2–3M, weak at 1M once all three relatives are removed. This
  bounds how much weight Pha 2 (disciplined discretionary integration) should place on it.

**Interpretation rule set in advance (so the read is honest either way):** the other 8L lenses were
adopted *because* they showed a measured forward-return edge. This DCF is being held to the same
test, but with an explicit caveat: **if MoS shows a positive, IS/OOS-stable cross-sectional IC, it
is a genuine edge signal; if it does not, the DCF remains a useful interpretive / discipline tool
(an absolute sanity check on how much premium you are paying) but must NOT be sold as a measured
alpha source** — a distinction that matters for how much weight discretionary decisions give it.

## 8. Limitations (read before trusting a number)

- **FCFE proxy is coarse.** `CF_OA + CF_Invest` nets *all* investing (incl. securities buys/sells),
  not just maintenance capex — noisy for firms with large financial-investment lines. 3Y-avg tames
  but does not remove this.
- **Conservative level bias** — see §6.1; use ranks, not the absolute MoS threshold.
- **Growth is barely predictable** (§4.1) — the biggest single uncertainty; the shrink+cap is a
  guardrail, not a forecast.
- **ERP / terminal-rate sensitivity** — §5; a 1pp r view = ~10% value.
- **No look-ahead**, but the deposit/CPI series are calibrated retrospectively (proxy anchors, one
  calibration date) — a *hindsight* limitation distinct from look-ahead. Shown **not to affect the
  cross-sectional IC** (§7.1); still means the historical MoS *level* is not a clean point-in-time
  number. The CLI now prints the terminal-growth data provenance every run —
  `terminal g = X% (Y% REAL NSO / Z% PROXY)` — and emits a soft `⚠️` WARN when `frac_real < 15%`
  (the NSO real-print window only reaches back ~13 months, so any as-of date before mid-2025 is
  100% proxy). This surfaces *how much* of the terminal input is real vs interpolated at valuation time.
- **Not for financials, not for FCFE-negative build-outs** — gated out by design.

## 9. Reproduce

```bash
DNA_PY=/home/trido/thanhdt/wc_venv/bin/python
$DNA_PY dcf_valuation.py FPT --asof 2026-06-15        # single-name fair value + sensitivity
$DNA_PY dcf_backtest.py --calib                        # Study A (recency-weight calibration)
DCF_REFRESH=1 $DNA_PY dcf_backtest.py --ic             # Study B (walk-forward MoS IC; refresh FV cache)
DCF_REFRESH=1 $DNA_PY dcf_rate_robustness.py           # §7.1 fixed-discount-rate IC robustness probe
$DNA_PY dcf_orthogonality_test.py                      # §7.2 MoS vs 1/PE,1/PB,1/EVEB residual-IC (Pha 1)
```
FV cache: `mike/agents/Taylor/dcf_exp/fv_releases.parquet` (experiment namespace, §8 coding-guidelines).
