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
(ticker, year), non-financial, trailing 3 annual TTM-NP growths → realized next-year TTM-NP growth
(n≈30k obs 2012-2026).

**Finding: trailing earnings growth *mean-reverts hard*.** A company's own past growth has
**negative** rank correlation (~−0.13) with its next-year growth. Consequences measured:
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

DCF is famously sensitive to r and terminal value. Measured on real names (fair value % change):
- **r ±1%** → fair value ≈ **∓9–12%** (e.g. FPT: r−1% +12%, r+1% −10%).
- **g_stage1 ±2%** → fair value ≈ **±8%**.

So a 1-percentage-point view on the discount rate moves intrinsic value ~10% — the margin-of-safety
should be read with a **wide band**, not to the decimal. `dcf_valuation.py` prints the sensitivity
grid on every single-name run.

## 6. Demo (as-of 2026-06-15, watchlist non-financials)

| Ticker | FCFE0 (B/yr) | g_stage1 | Fair value | Price | Margin of safety | Read |
|---|---|---|---|---|---|---|
| FPT | 6,335 | +11.7% | 53,909 | 73,600 | **−36.5%** | RICH |
| CTR | 505 | +6.6% | 52,475 | 86,900 | **−65.6%** | RICH |
| DHG | 722 | +0.7% | 51,530 | 94,000 | **−82.4%** | RICH |
| MSH | — | — | — | — | — | **no positive FCFE** (capex > CFO) |
| PVT | — | — | — | — | — | **no positive FCFE** (fleet build-out) |
| HAH | — | — | — | — | — | **no positive FCFE** (fleet build-out) |

**Two important, honest takeaways from the demo:**
1. **Nearly everything with a quality bid reads "RICH."** A conservative FCFE-DCF (all-investing
   netted out of cash flow, growth shrunk toward CPI, ~13% VN discount rate) sits *below* the price
   the market pays for durable compounders. The DCF's absolute level is therefore **conservative by
   construction** — its value is in **cross-sectional ranking** (which name is *least* rich, is the
   market premium unusually large right now), not as an absolute buy/sell line. This is consistent
   with sector_lens calling these names "expensive on relative metrics too" — the DCF agrees on
   *direction* but is harsher on *level*.
2. **Capital-intensive names (shipping/tankers/towers-in-buildout) are refused by the FCFE gate.**
   PVT, HAH, MSH have investing outflows exceeding operating cash — free cash flow to equity is
   negative during expansion, so a per-share DCF is not meaningful and the tool says so rather than
   manufacturing a number. For those, relative/asset-based lenses remain the right tool.

## 7. Walk-forward IC validation (does margin-of-safety predict forward return?)

`dcf_backtest.py` Study B: FV computed once per financial release (point-in-time), as-of merged onto
a monthly price panel, filtered to the **non-financial rating≤3** universe, cross-sectional Spearman
IC of MoS vs `profit_1M/2M/3M` per month, averaged, walk-forward IS(2014-19)/OOS(2020-26).

> **[IC RESULTS — filled from `dcf_exp/backtest_run.log` after the run completes]**

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
- **No look-ahead**, but the deposit/CPI series before ~2012 are proxies; IC window starts 2014.
- **Not for financials, not for FCFE-negative build-outs** — gated out by design.

## 9. Reproduce

```bash
DNA_PY=/home/trido/thanhdt/wc_venv/bin/python
$DNA_PY dcf_valuation.py FPT --asof 2026-06-15        # single-name fair value + sensitivity
$DNA_PY dcf_backtest.py --calib                        # Study A (recency-weight calibration)
DCF_REFRESH=1 $DNA_PY dcf_backtest.py --ic             # Study B (walk-forward MoS IC; refresh FV cache)
```
FV cache: `mike/agents/Taylor/dcf_exp/fv_releases.parquet` (experiment namespace, §8 coding-guidelines).
