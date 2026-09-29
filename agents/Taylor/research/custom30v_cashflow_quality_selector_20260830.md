# custom30V selector — cash-flow-quality axis + banking asset-quality lens: preliminary IC test

Job Taylor_20260829_173455 (Việc 4, weekend R&D). Scope: DESIGN + preliminary IC test only — no
change to `custom_basket.py` or any production selector. Answers "is this direction worth a full
backtest cycle", per [[project-custom30v-selector-roadmap]].

## 0. Prior art already covers most of this — read before re-deriving

This roadmap item is NOT starting from zero. 2026-07-14→07-15 already ran an extensive research
chain on exactly these three axes, on `custom_basket.py`'s `BASKET_SELECT` modes:

- **`yieldcombo`** (pre-cutover) = rank(1/PE)+rank(1/PCF), pool-wide.
- **`eyfin`** → **`eyonly` (= current production, "v4final")**: 1/PCF dropped entirely because a
  bank's PCF reflects deposit/loan balance-sheet flow, not core-operations cash — not the same
  economic quantity as a manufacturer's PCF (user's premise, 2026-07-14). Confirmed: BANK-route
  IC for 1/PE = +0.181 (t=3.79), stronger than pb_z or 1/PCF inside the route itself.
- **`eyrisk`** (job Taylor_20260715_025346, `agents/Taylor/eyrisk_exp/`): earnings yield DISCOUNTED
  by a continuous ROE-quality floor, `ey_adj = (1/PE) × clip(0.5+5·ROE_Min5Y, 0.5, 1.0)` — the
  closest existing analog to "make EY quality-aware." **Result: NO-GO.** Anchor (plain eyonly)
  CAGR 27.03% / Calmar 1.58 beat both scope=all (26.75% / 1.50) and scope=fin-only (26.64% / 1.56).
  Discounting earnings by a quality multiplier made the basket **worse**, not better.
- **`v3route`/`v3route2`/`v3route3`** (job Taylor_20260714_112932/121717): route the three
  financial ICB routes (BANK/INSURANCE/SECURITIES) to `rating_8l`'s own `value_score_v2`
  (P/B-vs-ROE, Gordon-style) instead of the pool-wide EY/CFY composite, i.e. exactly "(c)
  sector-lens-referenced ranking" for financials. **NO-GO** — quant-skeptic REFUTED v3route
  (absolute-vs-percentile scale mismatch cutting cross-route); v3route2 over-corrected the
  opposite way; v3route3 (the scale-matched reference arm) still underperformed the pool-wide
  eyonly baseline in the composite-selector backtest (-2..-15pp region reported in that chain).
- **`banking_valuation_framework.md`** (job Taylor_20260630_051434) already built and validated the
  banking asset-quality lens: **NPL/CAR/CASA/NIM are NOT in BQ** (`ticker_financial`); the working
  proxy is **`ROE_Min3Y` as a "never-destroyed-equity" floor** (a bad-debt blowup crushes ROE, so a
  high 3Y-minimum ≈ clean asset quality), paired with Gordon justified-P/B
  `(ROE5Y−0.05)/0.08` for value. Real NPL/CAR only exist via `bank_lens_v3.py` (vnstock), which is
  **currently BLOCKED-STALE** (vnstock lib deprecated 2025-08-31, 100% KeyError — Taylor finding
  2026-08-28, not fixed). `Debt_Eq`, `CF_OA*`, `ROIC*` are confirmed **meaningless for banks** —
  directly relevant to why any CFO-based axis (this doc's §1) must exclude financials by
  construction, not as an afterthought.

**Net: (b) and (c) already have a considered, tested answer** — don't re-run v3route or the
banking lens from scratch. What's actually NEW and worth testing this round is **(a) a genuine
cash-flow-quality axis distinct from what `eyrisk` tried** (ROE-discount ≠ accrual/cash-quality),
and whether it's additive-tilt-worthy or gate-worthy given the `eyrisk` lesson that discounts on
the EY score underperform plain eyonly.

## 1. Metric candidates found in `bigquery_dictionary.json` / `ticker_financial`

⚠️ **Dictionary correction, worth fixing in `bigquery_schema.md`**: the schema doc's column-group
line says `CF_OA_P0–P4` = "operating/assets" (a ratio). The actual dictionary entry says
**`CF_OA_P0` = "Operating cashflow, raw VND ... NOT a ratio over assets despite the name"**
(verified: HPG 2026Q1 CF_OA_P0 = 6.82e12, same order of magnitude as NP_P0). Only **`CF_OA_3Y`/
`CF_OA_5Y`** are true assets-scaled ratios (sums). This inconsistency is exploitable-by-mistake —
anyone building a cash-flow-quality ratio from `CF_OA_P0` assuming it's pre-scaled will silently
divide by assets twice. Flagging as a `data_registry` follow-up, not fixing schema.md in this job.

Candidates evaluated:
| Metric | Formula (available columns) | Note |
|---|---|---|
| **Accrual ratio (Sloan-style, no-assets variant)** | `(TTM_NP − TTM_CFO) / \|TTM_NP\|` where `TTM_X = X_P0+X_P1+X_P2+X_P3` | **Used below.** Low = cash-backed earnings (good); high = earnings run ahead of cash (accrual-heavy, easier to manipulate). Needs `TTM_NP > 0` (ratio undefined/unstable for loss-makers). |
| CFO/NP (cash conversion) | `TTM_CFO / TTM_NP` | Equivalent monotone transform of the above; not run separately. |
| ROA-based accrual (Sloan original) | `ROA_P0 − CF_OA_P0/totalAsset_P0` | Needs an extra `ticker_financial` join for `totalAsset_P0` (not in `ticker`/`ticker_prune`) — deferred, no-assets variant above is a fair proxy and avoids the join. |
| Beneish M-score component (DSRI, days-sales-in-receivables) | needs `AR_P0`, `Revenue_P0` (both in `ticker_financial` only) | Not tested this round — flagged for a future pass if the accrual-ratio result is promoted. |

## 2. IC test — quarterly panel, non-financial routes only, PIT, no look-ahead

**Method**: `ticker_prune`, quarterly-sampled (first-month-of-quarter snapshot),
2014-01-01→2025-12-31, `PE>0`, full TTM NP/CFO available, `profit_2M` (training-only column, used
here for research exactly as `coding_guidelines.md` §quant-research permits — not a live filter).
**Excludes BANK(8355)/INSURANCE(8530–8579)/SECURITIES(8777)/REALESTATE(8633)** by construction —
same routing rationale as `rating_8l.py`/`eyonly`, since CFO is not economically comparable for
those routes. Panel: 47 quarters, 307 distinct tickers, median 142 names/quarter.
N = **47 independent quarters** (not row count), per guideline.

```
ey vs fwd2M:                            mean IC = 0.0697  t = 4.78   (68% of quarters positive)
-accrual vs fwd2M (standalone):         mean IC = 0.0209  t = 1.07   (57% of quarters positive)
-accrual vs ey (orthogonality check):   mean IC = -0.1186 t = -8.13  (only 23% of quarters positive)
```

**Reading**:
1. **Standalone, accrual-quality is weak** — IC 0.02, t≈1.07, not significant on its own. It is
   NOT a replacement for 1/PE and would not clear the bar as a stand-alone score leg.
2. **It is NOT redundant with 1/PE — it's *negatively* correlated with it**, strongly and
   consistently (t=-8.13, only 23% of quarters positive). Economically: names that look cheap on
   1/PE skew toward *worse* cash-flow quality (higher accruals). This is the classic "value trap"
   confound, not noise — and it means accrual quality is exactly the kind of orthogonal-but-weak
   signal that works as a **filter on the cheap bucket**, not as an additive score (adding a weak,
   negatively-correlated leg to a linear composite mostly just dilutes the strong EY leg — this is
   very likely why `eyrisk`'s ROE-discount approach, which multiplies the EY score directly by a
   quality factor, came back NO-GO).

## 3. Double-sort: accrual as a GATE inside the cheap-EY bucket (not an additive tilt)

Per quarter: top EY tercile (cheapest third by 1/PE) → split by accrual tercile within that
cheap bucket. Mean forward 2M return by accrual tercile (0 = lowest accrual/best quality, 2 =
worst):

```
tercile 0 (best cash-flow quality):   +9.14%
tercile 1 (middle):                   +5.63%
tercile 2 (worst cash-flow quality):  +7.09%
paired diff (best − worst): mean = +2.05pp/2M, t = 2.59, p = 0.013, N = 47 quarters
```

Middle tercile is non-monotonic (a known small-N-per-cell tercile artifact, not unusual with ~47
names/cheap-bucket/quarter) — but the **best-vs-worst spread is real and significant** (p=0.013 on
independent-quarter N, not row count). **Within names that already pass the 1/PE cheapness bar,
the best-cash-flow-quality third earns ~2pp/2M more than the worst-quality third.**

## 4. Design implication — GATE/tiebreak, not a new composite leg

Same shape as the system's one validated quality mechanism (`rating_8l`'s golden floor:
`ROE_Min3Y≥0 ∧ CF_OA_3Y>0`, a binary gate, explicitly NOT a return-tilt) and the opposite of the
one that failed (`eyrisk`'s continuous discount multiplied into the score). Proposed next step (NOT
run this round — first full backtest cycle, not wired):
- **Gate, not composite leg**: within the eyonly top-30 selection, either (a) exclude the worst
  accrual tercile/quartile before ranking by 1/PE, or (b) use accrual rank as a tiebreak among
  near-equal 1/PE scores (same pattern as the existing `BASKET_DY_TIEBREAK` mechanism already in
  `custom_basket.py` for `eyonly`).
- **Scope**: non-financial routes only (BANK/INSURANCE/SECURITIES/REALESTATE excluded from the
  gate, same as this test) — CFO is not a comparable quantity there; those routes already have
  their own lens (`banking_valuation_framework.md`, §0 above) and should NOT get a CFO-based
  filter bolted on.
- **Full backtest required before any wiring**: this is one double-sort on one forward horizon
  (2M) — needs (i) 1M/3M robustness, (ii) IS/OOS split, (iii) a real gate threshold pre-registered
  (not tuned to this result), (iv) DSR/PBO, (v) quant-skeptic CONFIRMED, per
  `coding_guidelines.md` §quant-research and the standing custom30V backtest bar. This doc's job
  is only "is the direction worth that cycle" — answer: **yes for (a) as a gate, no for (a) as an
  additive score; (b)/(c) already have a settled NO-GO/proxy answer from 07-14, don't re-open**.

## 5. Risks / limitations (honest, not swept)

- **Data-snooping structure**: the accrual-ratio idea and its threshold weren't pre-registered
  before seeing this panel — this is a *preliminary* IC test to decide whether to invest in a
  properly pre-registered backtest, not a result to wire. Flagged explicitly, per the dispatch's
  own framing.
- **N=47 quarters is not large** for a tercile-within-tercile double sort (median ~142 names/quarter
  → ~47/cheap-bucket/quarter → ~15-16/accrual-tercile-cell). Robust to outliers via rank-based
  qcut, but a full run needs a wider window check and per-year LOO before trusting the point
  estimate.
- **`ttm_np>0` filter drops loss-makers from the accrual leg** (ratio undefined/unstable at
  NP≈0) — 0.13% of rows in this panel, immaterial here, but the full design must define what
  a loss-making cheap-EY name gets (neutral pass-through, like `rating_8l`'s missing-data
  convention) rather than silently excluding it from the universe.
- **Sector/route composition within "non-financial"** is not itself homogeneous (steel vs retail vs
  tech have very different natural accrual levels) — this test pools them; a full backtest should
  check whether the accrual-quality edge survives within-sector, not just pool-wide (same lens the
  fleet already applies per `feedback-finance-domain-grounding-not-pure-statistics`).
- Panel artifact: `research/cfq_panel_20260830.csv` (6,329 rows, BQ-pulled 2026-08-30, `ticker_prune`).
