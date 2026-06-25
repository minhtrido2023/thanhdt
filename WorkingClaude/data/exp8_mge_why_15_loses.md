# Exp-8 — WHY MGE=1.5 loses 1.03pp OOS CAGR vs 1.3 (the gap ≠ borrow drag)

**Taylor, 2026-06-25** · decomposed from the frozen MGE-sweep audit CSVs (`..._mge1{20,30,40,50}cap_capitonly63cv17.csv`), same-snapshot `AUDIT_END=2026-06-19`, NAV 50B, self-check 0 VND.

## The question (user via Mike)
MGE=1.5 loses **1.03pp OOS CAGR** vs 1.3 (35.85→34.82). Pure borrow drag should be only ≈0.26%/yr
(3 episodes × 60 sess / 1386 OOS sess × 0.2× NAV × 10%/yr). Actual is ~4× that. Why?

## Answer: the premise is wrong — there is essentially NO borrow. The gap is a position-SIZING tilt, not a financing cost.

### Fact 1 — leverage almost never fires; actual borrow interest ≈ 0
- **Combined gross exposure never reaches 100%** in the entire 2014→2026 backtest: max gross **0.995 (MGE 1.3) / 0.966 (MGE 1.5)**. The book is cash-covered virtually always.
- Actual borrow interest charged in OOS: **1.3 = 0 VND (0 borrow-days); 1.5 = 2.73M VND total (only 2 borrow-days in 6.5 yrs, max borrow 6.76B in ONE book while the other held cash) = 0.0002 %/yr.**
- ⇒ The 0.26%/yr estimate assumes a 0.2× borrow runs continuously over the deploy windows. It does not — the marginal CAPIT size is funded from **otherwise-idle cash**, not margin. Real carry is ~1000× smaller than the estimate. So the gap cannot be borrow drag; it is ~5000× the borrow actually paid.

### Fact 2 — what MGE actually is here: a SIZE-CAP multiplier on the deep-washout recovery arm
`MGE_CAPIT_ONLY` raises the per-arm gross cap to MGE, adding `(MGE−1)×size` headroom to the CAPIT sleeve.
Because spare cash exists (gross<100%), MGE=1.5 simply **deploys a bigger CAPIT recovery position out of cash**, displacing idle cash / other holdings — a composition tilt, not >100% financing.
Evidence (1.5 minus 1.3 stock holdings): **+13–14B in Aug–Sep 2020, +25/+23B in Feb–Mar 2021** (bigger arm in the up-leg), then **−25/−24/−17B in Sep–Nov 2021** (the position unwinds into the give-back).

### Fact 3 — the gap is the net return of that extra tilt: gain-then-larger-giveback (volatility/path drag), compounded
Per-year contribution to the 1.5-vs-1.3 gap (Δlog NAV ratio, pp; negative = 1.5 loses ground):

| 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026-H1 |
|---|---|---|---|---|---|---|
| +0.25 | **−2.31** | −0.47 | +0.06 | −0.25 | −0.56 | **−1.63** |

navratio (1.5/1.3, OOS-normalised): 1.000 → **+1.59% by 2021-03-31** → **−2.03% by 2021-12-31** → −4.79% by 2026-06-19.

- **2021 is the killer (−2.31pp).** The bigger COVID-recovery arm rode the rally to **+1.59%** by Mar-2021, then **gave it ALL back and more (−2.03%)** through the H2-2021 reversal/chop. Same names, bigger size → both legs amplified; an up-then-deeper-down path has **negative geometric return** even with zero financing cost. That NAV deficit then compounds for the remaining ~5 OOS years.
- **2026-H1 (−1.63pp)** is the same mechanism in the current washout (bigger arm into a still-volatile recovery).
- It is **lumpy and episode-bound** (concentrated in 2 recovery cycles), the opposite of the smooth, flat bleed a 10%/yr carry would produce — direct visual proof it is composition/path, not carry.

### The four hypotheses, scored
1. **Leveraged arm worse in sub-periods — YES, primary driver.** Net-loses across 2021/2022/2024/2025/2026 recovery cycles; only wins 2020/2023. The extra size is a tilt into volatile washout names that mean-revert after the bounce.
2. **Compounding × volatility in recovery — YES.** The 2021 +1.59%→−2.03% swing is textbook variance drag amplified by bigger size; the resulting deficit compounds geometrically over 6.5 OOS yrs → ~1pp/yr CAGR, with no reason to equal an arithmetic carry figure.
3. **Capacity/liquidity at 50B, gross 150% — NO.** Gross never approaches 150% (max 0.966); book is cash-covered. No 150%-gross liquidity/capacity problem. (Single-name concentration in the arm is modestly higher with more size, a second-order risk, not the driver.)
4. **CAPIT_STOP early exit — MINOR.** 1.5 fired 36 stops vs 34 (1.3); 334 vs 350 distinct OOS CAPIT holding-ids. A small path artifact of the different fills, not a systematic early-cut. Hold mechanism is unchanged (60-session).

## Verdict
The 1.03pp OOS CAGR loss going 1.3→1.5 is **NOT borrow drag** (real carry ≈ 0.0002%/yr — the book never actually levers, gross<100% throughout). It is the **negative geometric/path return of a LARGER deep-washout recovery tilt** that gains the bounce then gives back more in the reversal, concentrated in 2021 (−2.31pp) and 2026-H1 (−1.63pp) and compounded over the OOS window. MGE here behaves as an **arm-size multiplier funded by cash**, not a financing lever — which is also why MaxDD pins flat at −20.5% (no real >100% tail). Confirms MGE=1.3 as the sizing sweet spot: past it you buy MORE of a tilt that has negative path-return, for ~zero financing benefit.
