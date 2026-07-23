# LAG deep-dive #2 — rating-by-regime + continuous vs discrete gate
Job Taylor_20260723_135623 · 2026-07-23 · Taylor (quant) · R&D only, wires nothing.
Continues job Taylor_20260723_131958. Same LAG-only engine (`lag_common.py`), same
5,389 PIT-attributed events. Scripts: `stage4_rating_by_regime.py`,
`stage5_build_cont_features.py`, `stage6_cont_univariate.py`, `stage7_cont_vs_disc.py`.
Pre-register: `PREREGISTER_stage7.md`.

---
## Q1 — Does RATING discrimination (≤3 vs ≥4) depend on regime? **User hypothesis REFUTED.**
User guessed: rating separates returns mainly in NEUTRAL, loses meaning in BULL+ (everything rises).
Data says the opposite point-estimate, and — more importantly — rating barely discriminates in ANY regime.

RATING GAP (avg post_ret rating≤3 minus rating≥4), Welch t:

| regime | N | gap (pp) | t | p |
|---|---|---|---|---|
| DT5G 1 BEAR | 1087 | **−0.03** | −0.03 | 0.98 |
| DT5G 3 NEUTRAL | 2826 | +0.66 | 1.02 | 0.31 |
| DT5G 4 BULL | 1059 | **+1.53** | 1.31 | 0.19 |
| DT5G≥4 bull+ | 1169 | +1.83 | 1.61 | 0.11 |
| ALL | 5389 | +0.79 | 1.62 | 0.11 |
| **dd −10..−5 (early-drawdown)** | 1203 | **+2.44** | **2.30** | **0.022** |
| dd≤−20 (deep) | 501 | −1.93 | −1.08 | 0.28 |

Per-rating means confirm it: in **NEUTRAL** the profile is FLAT (r1 4.28 / r3 4.34 / r4 3.41 / r5 4.24 —
rating hardly matters); in **BULL** it's the *most* monotone (r2 11.0 > r3 8.4 > r4 6.7). So the user's
"rating only works in neutral" is doubly wrong: neutral is where rating discriminates *least*.

**But the honest headline is: no per-regime gap is statistically significant** (all p>0.10 except the
early-drawdown bucket). Rating is a **binary quality/safety gate, not a regime-conditional return tilt**
— consistent with the standing KB position. → **No basis for a "rating-gate only in NEUTRAL" rule.**
The single significant effect (early-drawdown dd −10..−5, +2.44pp) is one bucket out of many (multiple-
testing fragile) and, notably, is roughly where the market sits *now* — worth remembering, not wiring.

---
## Q2 — Is DT5G "too coarse"? Continuous features vs the discrete gate. **Continuous does NOT win.**

**Which continuous feature predicts LAG drift LEVEL** (Spearman IC, full / IS / OOS):

| feature | IC_full | IC_IS(≤19) | IC_OOS(≥20) |
|---|---|---|---|
| **breadth** (% >MA200) | **+0.143** | **−0.049** | **+0.212** |
| liq_ratio (vol/LT-avg) | +0.104 | +0.007 | +0.145 |
| roc5 | +0.094 | +0.025 | +0.126 |
| dd3m/6m/12m (drawdown) | ~0.00 | ~ | ~ | ← drawdown per se does NOT predict LAG drift |

Breadth is the best single predictor of the drift level — **but its IS IC is NEGATIVE and flips to +0.212
OOS**: the whole "healthy-market → fatter LAG drift" relationship is a **post-2020 phenomenon**. Same for
liquidity. Multivariate OLS: breadth dominates (std-β +5.17, t +12.2) but that fit is OOS-driven.
Surprise-IC (the *ranking*) is stable ~0.09–0.13 across every feature bucket → as in job #1, what moves is
the **LEVEL, not the ranking**.

**Within-NEUTRAL(3) heterogeneity (user's sharpest point) is REAL but OOS-only.** Splitting the 2,826
NEUTRAL entries by breadth: low-breadth-neutral +3.02 vs high-breadth-neutral +5.20 (gap **+2.19, t 3.54,
p<0.001**) — "bear-leaning" vs "bull-leaning" neutral genuinely differ. BUT IS gap −0.72 / OOS gap +5.33:
sign flips in-sample. dd6m splits NEUTRAL the *wrong* way (deeper dd → HIGHER drift, gap −2.61) — cutting
drawdowns would cut the good rebound trades (job #1's lesson).

**NAV backtest — continuous sizing gates vs discrete DT5G c4** (LAG-only, POS×mult; DSR N=7):

| variant | CAGR | Sharpe | MaxDD | Calmar | IS_Sharpe | OOS_Sharpe | DSR |
|---|---|---|---|---|---|---|---|
| baseline | 17.07 | 1.23 | −16.7 | 1.02 | 0.90 | 1.50 | 0.998 |
| **disc_c4 (DT5G≤2 half)** | **16.63** | **1.33** | **−15.0** | **1.11** | **1.03↑** | **1.57** | 0.999 |
| cont_breadth (<0.40 half) | 16.12 | 1.23 | −16.7 | 0.97 | **0.82↓** | 1.57 | 0.998 |
| cont_liq (<1.0 half) | 15.02 | 1.30 | −14.7 | 1.02 | 1.00 | 1.53 | 0.999 |
| cont_roc (roc20<−8 half) | 16.56 | 1.26 | −16.7 | 0.99 | 0.96 | 1.51 | 0.999 |
| cont_combo (breadth\|roc) | 15.98 | 1.25 | −16.7 | 0.96 | **0.87↓** | 1.56 | 0.999 |
| cont_smooth_breadth | 16.28 | 1.25 | −16.7 | 0.97 | 0.90 | 1.54 | 0.999 |
| hybrid c4+roc | 16.04 | 1.30 | −15.0 | 1.07 | 1.03 | 1.52 | 0.999 |

**disc_c4 wins outright**: highest Sharpe (1.33), best Calmar, only −0.44pp CAGR, and it **improves BOTH
IS (0.90→1.03) and OOS**. Every breadth-based continuous gate **fails IS** (IS_Sharpe drops below baseline)
— the OOS gain is the predicted regime-carry. cont_liq costs −2.05pp. The hybrid costs more CAGR without
beating c4's Sharpe. **→ The coarse discrete DT5G gate is MORE robust than any continuous market-health
signal for LAG**, because the continuous signals are 2020+-fitted.

The one IS-stable continuous gate is **roc20<−8 (fast-decline)**: −0.51pp CAGR, IS_Sharpe 0.96, fires only
on genuine fast sell-offs (2014/2018/2022/2023/2025). It is a *cheaper fresh-drawdown gate* than job #1's
below-MA200/neg-6m cuts (those cost ~1.5pp) — but its Sharpe gain is below c4's, so it's an optional
insurance overlay, not a replacement.

---
## Q3 — Current market state (2026-07-23) on the 4 dimensions, and the LAG read

| dimension | value | pctile (2014+ daily) | read |
|---|---|---|---|
| **a. Drawdown from peak** | −11.9% (3m=6m=12m) | dd6m 19% | moderate; **not** deep crisis (≠ ≤−20%) |
| **c. Decline speed** roc5/10/20 | −5.8 / −7.7 / **−8.8%** | **3–5%** | **very fast** — bottom 5% of history |
| **b. Liquidity** vol/LT-avg | 0.87× | 31% | thin, below long-term average |
| **d. Breadth** %>MA200 | 30.5% | 12% (Q1) | weak, bottom quintile (stale from 06-10 → real likely lower) |
| (RSI) | 0.30 | 4% | oversold |

**LAG read for these exact conditions:**
- Breadth-Q1 historical LAG drift = **+0.24%**; analog events (breadth~0.30 & dd6m~−12%): N=372, avg
  post_ret **+0.70%, WR 46%** — the earnings-drift **LEVEL is compressed to ~zero** (vs +4.5% normal).
- BUT surprise-IC within the analog set = **+0.128 (p=0.014)** — the signal still **ranks names** (selection
  intact, even sharp), exactly the mild-drawdown/falling bucket that job #1 found strongest-IC.
- roc20 = −8.79 **< −8 → the fast-decline gate fires NOW** (DT5G, still NEUTRAL(3), does not).

**→ The user is right about the LEVEL**: in this low-breadth, fast-falling, thin-liquidity tape the LAG
premium is thin (~0–0.7% avg, coin-flip WR), so lagged/earnings-drift names offer little *return* edge
here vs defensive blue-chips on a risk-adjusted basis. **The user is not right that the signal is dead** —
it still discriminates; the correct response is **size down, keep selecting on surprise**, not abandon.
This is not deep crisis (where IC genuinely dies). TRC additionally rating-fails (prior work) → both the
level lens and the quality lens argue small/cautious. **Decision stays with Mike/user.**

---
## Bottom line / recommendation (vs job #1)
- **Standing candidate UNCHANGED = disc_c4/c5** (half-size LAG in DT5G bear/low-neutral). This deep-dive
  *strengthens* it: it survives a direct challenge from continuous features and beats all of them on
  robustness. Route to quant-skeptic before any wiring; frame as risk-sizing insurance, not a return
  booster.
- **New, honest addition for the fresh-drawdown gap** (DT5G is slow, misses tape like now): the
  **roc20<−8 fast-decline overlay** is the cheapest IS-stable way to also act on sharp sell-offs
  (−0.5pp CAGR vs the −1.5pp of MA200/6m cuts). Optional insurance for the user to weigh; it fires today.
- **Do NOT** build a breadth/liquidity continuous gate (OOS-fitted, fails IS) and **do NOT** add a
  regime-conditional rating gate (Q1: no significant per-regime discrimination). Rating stays a binary
  quality gate.
- Nothing wired. TRC remains HOLD. All variants self-check 0 VND (min NAV +49.6–49.9B, no negative cash).
