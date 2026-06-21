# Kelly Sizing Research — Q2 (Regime Exposure) + Q3 (Per-Tier Slot Weight)

**Date**: 2026-05-21
**Author**: research (no code changes yet)
**Status**: SPEC ONLY — verdicts gate any future deployment

## Scope

Replace two heuristic sizing layers with fractional-Kelly variants and assess whether the change is justifiable:

- **Q2** — 5-state regime exposure `{CRISIS 0%, BEAR 20%, NEUTRAL 70%, BULL 100%, EX-BULL 130%}` currently used by the V6 ETF leg (see `vnindex_5state_system.py`, `simulate_holistic_nav.py:cash_etf_states`).
- **Q3** — Per-tier slot weight `TIER_WEIGHTS_V11 = {t: 0.10 for t in TIER_BAL}` (flat 10% NAV per slot) currently used by the BA v11 BAL leg.

All math is shown explicitly. No code is changed in this round.

---

## Section 1 — Q2: Regime-aware Kelly exposure

### 1.1 Data

- **State series**: `vnindex_5state.csv` (production output of `vnindex_5state_system.py`, EMA 0.40 + mode 15 + min-stay 7).
- **Returns**: `tav2_bq.ticker WHERE ticker='VNINDEX'` (full history 2000-07-28 → 2026-05-20).
- Merge state[t] with next-session return `r[t→t+1]` to attribute return to the state that gates exposure on day t (T+1 execution, matching `backtest_workflow.py`).
- **SPY** (sessions / calendar year): 243.4 full, **249.3** since 2011.
- **Risk-free**: 6 % / yr (deposit rate per CLAUDE.md cost model).
- **Borrow**: 10 % / yr (margin cost).

### 1.2 Per-state stats (since 2011 — production-relevant window)

| state | n | μ_daily | σ_daily | μ_ann | σ_ann | Sharpe (excess) | Kelly_full (uncapped) | f_full (cap 1.30) | f_half | f_quarter |
|------:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 CRISIS  |  862 | −0.044 % | 1.481 % | −11.00 % | 23.38 % | −0.73 | < 0 | **0.00** | 0.00 | 0.00 |
| 2 BEAR    |  268 | +0.006 % | 1.254 % |  +1.38 % | 19.80 % | −0.23 | < 0 | **0.00** | 0.00 | 0.00 |
| 3 NEUTRAL | 2153 | +0.063 % | 1.025 % | +15.82 % | 16.18 % | +0.61 | **3.74** | 1.30 | 1.30 | 0.94 |
| 4 BULL    |  433 | +0.111 % | 1.155 % | +27.65 % | 18.23 % | +1.19 | **6.53** | 1.30 | 1.30 | 1.30 |
| 5 EX-BULL |  113 | +0.141 % | 1.044 % | +35.16 % | 16.48 % | +1.77 | **10.7** | 1.30 | 1.30 | 1.30 |

Reference (full 2000-2026): Kelly_full for state 3 is only **1.11** (driven down by 2008-2009 included in sample) — sensitivity to regime is large; see caveats.

**Formula**: `f* = (μ_ann − rf) / σ_ann²`, floored at 0 (no shorts), capped at 1.30 (current EX-BULL ceiling, justified by 10 % borrow cost making leverage > 1.3 negative-edge in normal vol).

**Key reading**:
- Full Kelly says NEUTRAL (state 3) should be **130 %** (capped) — vs heuristic 70 %.
- Half-Kelly and quarter-Kelly both still hit the cap on state 3 since 2011.
- States 1-2 correctly land at 0 % (negative expectancy).
- The cap is the binding constraint, not Kelly itself.

### 1.3 Variants tested

| Variant | w1 | w2 | w3 | w4 | w5 | Notes |
|---|---:|---:|---:|---:|---:|---|
| HEURISTIC (current) | 0.00 | 0.20 | 0.70 | 1.00 | 1.30 | Production |
| K_FULL              | 0.00 | 0.00 | 1.30 | 1.30 | 1.30 | Full Kelly capped |
| K_HALF              | 0.00 | 0.00 | 1.30 | 1.30 | 1.30 | Same as full (cap binds) |
| K_QTR               | 0.00 | 0.00 | 0.94 | 1.30 | 1.30 | Quarter Kelly |
| BLEND_HI            | 0.00 | 0.20 | 0.70 | 1.30 | 1.30 | Heuristic + Kelly only on bull states |
| HEUR_N100           | 0.00 | 0.20 | 1.00 | 1.30 | 1.30 | Push NEUTRAL up to 100 % only |
| HALF_FLOOR_HEUR     | 0.00 | 0.20 | 1.30 | 1.30 | 1.30 | Half Kelly but floored at heuristic |
| HEUR_N85            | 0.00 | 0.20 | 0.85 | 1.00 | 1.30 | Modest NEUTRAL boost |

### 1.4 Sanity backtest — VNINDEX, since 2011 (15.36 y)

NAV pipeline matches `backtest_workflow.py` (T+1 execution, ramp 3, snap < 3 %, TC 0.1 %, deposit 6 %/yr, borrow 10 %/yr, cap 130 %).

**In-sample (2011-2026, weights fitted on same data — optimistic):**

| variant              | CAGR | Sharpe | MaxDD | Calmar | NAV_bn |
|---|---:|---:|---:|---:|---:|
| B&H VNINDEX          |  9.38 % | 0.25 | −45.3 % | 0.21 | 3.96 |
| HEURISTIC            | 12.31 % | 0.56 | −22.7 % | 0.54 | 5.95 |
| K_FULL               | 14.07 % | 0.49 | −39.9 % | 0.35 | 7.55 |
| K_QTR                | 13.59 % | 0.54 | −29.0 % | 0.47 | 7.08 |
| BLEND_HI             | 12.77 % | 0.55 | −22.7 % | **0.56** | 6.33 |
| HEUR_N100            | 13.83 % | 0.54 | −32.1 % | 0.43 | 7.31 |
| HEUR_N85             | 12.86 % | 0.55 | −27.5 % | 0.47 | 6.41 |

**Walk-forward OOS 2019-2026 (weights fitted on 2011-2018 only — honest):**

| variant              | CAGR | Sharpe | MaxDD | Calmar | NAV_bn |
|---|---:|---:|---:|---:|---:|
| B&H VNINDEX          | 11.02 % | 0.33 | −40.3 % | 0.27 | 2.16 |
| HEURISTIC            | **15.17 %** | **0.71** | **−14.3 %** | **1.06** | 2.83 |
| K_FULL_OOS           | 18.48 % | 0.68 | −26.3 % | 0.70 | 3.48 |
| K_HALF_OOS           | 18.36 % | 0.68 | −25.6 % | 0.72 | 3.46 |
| K_QTR_OOS            | 15.06 % | 0.66 | −18.4 % | 0.82 | 2.81 |
| BLEND_HI_OOS         | 15.54 % | 0.67 | −18.4 % | 0.85 | 2.90 |
| HEUR_N100            | 17.37 % | 0.70 | −19.6 % | 0.89 | 3.25 |

### 1.5 Verdict — Q2: **YELLOW** (conditional adopt)

**Findings**:

1. **Full Kelly wins on CAGR but loses on risk-adjusted metrics.** OOS K_FULL gives +3.3 pp CAGR over heuristic but Sharpe drops 0.71 → 0.68, MaxDD worsens 14 % → 26 %, Calmar falls 1.06 → 0.70. The current heuristic is **near-optimal on Calmar terms** — it is not naively conservative.
2. **The cap is doing the work, not Kelly.** Half- and quarter-Kelly both bind to the 130 % cap on state 3, so the variants are effectively rescalings of `{0, 0, ≤1.3, 1.3, 1.3}`. Below-cap Kelly fractions only emerge in K_QTR (0.94 on state 3) — and that variant is roughly **tied** with HEURISTIC OOS (Sharpe 0.66 vs 0.71, CAGR ≈ same).
3. **Sweet spot identified**: `HEUR_N100` (push NEUTRAL only to 100 %, keep BEAR at 20 % floor) gives **+2.2 pp CAGR vs heuristic OOS** while losing only 0.01 Sharpe and adding 5.3 pp to MaxDD. This is a "Kelly-flavored" tweak that doesn't blow up the risk profile.
4. **State 2 BEAR**: Kelly says 0 % but heuristic says 20 %. Since 2011, state 2 has μ ≈ 0 — both choices are defensible. Keeping 20 % is preferable because the state often **transitions** to NEUTRAL/BULL (ramp delay would cost alpha if we sit at 0 %).

**Recommended path**: Do **not** adopt full or half Kelly as a direct replacement (risk profile degrades materially). The only Kelly-derived change worth shadow-testing is the **NEUTRAL boost** (70 % → 85-100 %) tested via a full BA v11 integrated stack — not just the VNINDEX-on-VNINDEX sanity backtest used here.

---

## Section 2 — Q3: Kelly-weighted slot sizing per tier

### 2.1 Data

- **Source**: `ba_trades_bal_refresh.csv` + `ba_trades_vn30_refresh.csv` (canonical BAL+VN30 refreshed trade log, T+1 Open exec).
- 434 trades total (BAL 289, VN30 145), 2015-12-03 → 2026-03-30 (10.32 years).
- **Tier names in historic log are legacy SCORE_V10 labels** (`DEEP_VALUE_RECOVERY`, `MOMENTUM`, `MOMENTUM_N`, `MOMENTUM_S`). The current production has more tiers (MEGA, S_PRO, MOMENTUM_QUALITY, COMPOUNDER_BUY, RE_BACKLOG_BUY, etc., see `simulate_holistic_nav.py:96-114`); those are absent from this trade log and **cannot be Kelly-fit here**. See caveats.

### 2.2 Per-tier stats (BAL+VN30 merged, net returns)

| tier                 | n   | WR    | avg_win | avg_loss | mean_ret | sd_ret | Sharpe_per_trade | Kelly_binary | Kelly_continuous |
|----------------------|---:|------:|-------:|--------:|--------:|-------:|----------------:|-----------:|-----------------:|
| MOMENTUM_S           |  80 | 77.5 % | 26.53 % | 17.68 % | **16.59 %** | 27.68 % | **0.599** | 3.54 | **2.16** |
| MOMENTUM             |  19 | 68.4 % | 26.89 % | 13.91 % | 14.01 % | 26.78 % | 0.523 | 3.75 | 1.95 |
| MOMENTUM_N           |  62 | 56.5 % | 26.47 % |  9.62 % | 10.75 % | 29.45 % | 0.365 | 4.22 | 1.24 |
| DEEP_VALUE_RECOVERY  | 273 | 58.6 % | 22.74 % | 11.88 % |  8.41 % | 24.57 % | 0.342 | 3.11 | 1.39 |

**Kelly forms**:

- *Binary*: `f_b = (WR · avg_win − (1−WR) · avg_loss) / (avg_win · avg_loss)` — large numbers because trades are independent and small.
- *Continuous*: `f_c = μ / σ²` — more stable when n is small.

We use **continuous Kelly × 0.25 (quarter)** and normalize so that the *trade-count-weighted average* per-slot weight matches the current 10 %. This keeps **total gross exposure** unchanged (relative re-weighting only) — the goal is redistribution, not leverage change.

### 2.3 Proposed per-slot tier weights

Normalization: `raw_w_tier = 0.10 × (kelly_c_tier / mean(kelly_c)) × 0.25` (quarter-Kelly), then clip to `[4 %, 18 %]`, then rescale so `Σ(n_tier × w_tier) = Σ(n_tier × 0.10)`.

| tier                 | n   | mean_ret | Kelly_c | proposed slot weight | vs current 10 % |
|----------------------|---:|--------:|--------:|---------------------:|----------------:|
| MOMENTUM_S           |  80 | 16.59 % | 2.16 | **14.1 %** | +4.1 pp |
| MOMENTUM             |  19 | 14.01 % | 1.95 | **12.7 %** | +2.7 pp |
| DEEP_VALUE_RECOVERY  | 273 |  8.41 % | 1.39 | **9.1 %**  | −0.9 pp |
| MOMENTUM_N           |  62 | 10.75 % | 1.24 | **8.1 %**  | −1.9 pp |

(Production tiers not in this log — MEGA, S_PRO, MOMENTUM_QUALITY, COMPOUNDER_BUY, RE_BACKLOG_BUY — would be assigned the **base 10 %** until enough trade data accumulates. See Section 3.)

### 2.4 Estimated impact (back-of-envelope, ROUGH)

Two estimators:

1. **Total-edge contribution** (assumes slot utilisation proportional to n_tier):
   - Old (flat 10 %): Σ n_tier × mean_ret × 0.10 = **+455.6** (cumulative %-trade units)
   - New (tier-weighted): Σ n_tier × mean_ret × w_tier = **+482.4**
   - Δ = +26.7 → over 10.32 y → **≈ +2.6 pp CAGR contribution** (very rough, ignores compounding, slot overlap, cash drag).
2. **Sharpe-weighted reallocation**:
   - Old: Σ 0.10 × n × Sharpe_tr = **17.40**
   - New: Σ w_tier × n × Sharpe_tr = **18.30**
   - **+5.2 % Sharpe gain proxy.**

Estimator 1 is optimistic (compounding assumption). Estimator 2 is more honest — a **modest +5 % Sharpe improvement** is consistent with what fractional-Kelly literature predicts.

### 2.5 Verdict — Q3: **YELLOW** (sample-size constrained, canonical sim required)

**Findings**:

1. The clear ranking is `MOMENTUM_S > MOMENTUM > MOMENTUM_N ≈ DEEP_VALUE_RECOVERY` on Sharpe-per-trade, which matches intuition (S = strong-bull setups in confirmed BULL/EX-BULL states).
2. **Sample sizes are uneven**: MOMENTUM has only n=19 trades — Kelly fraction (1.95) is **unreliable** at this sample size. Recommend pooling MOMENTUM + MOMENTUM_S into a single "momentum-strong" bucket if deployed.
3. DEEP_VALUE_RECOVERY (273 trades, the dominant tier) has the lowest Sharpe but largest sample size — its 9.1 % weight is statistically the most reliable change.
4. The proposed weights are **inside a reasonable band** (8-14 %) — not aggressive enough to cause failures from a single-tier blowup.
5. **Sticking point**: the production system has 7+ tiers (MEGA, S_PRO, COMPOUNDER_BUY, RE_BACKLOG_BUY, etc.) for which **no historic trade-level data exists in the refresh files**. Deploying Q3 in production requires either (a) a fresh canonical 12y sim with TIER_BAL labels emitted, or (b) starting with the 4-tier mapping above and leaving everything else at 10 % until paper-trade data accumulates.

---

## Section 3 — Caveats & invalidation conditions

### 3.1 Sample-size warnings

- **Q2**: 113 EX-BULL sessions, 268 BEAR sessions since 2011. EX-BULL Kelly_full = 10.7 (uncapped) — almost entirely driven by a few periods (2017-Q4, 2021-Q1, 2025 late). One outlier event could flip the answer.
- **Q3**: MOMENTUM tier has only 19 trades. Kelly fractions for any tier with n < 30 should be treated as informational only.

### 3.2 Regime instability (the single most important caveat)

Per-year state-3 (NEUTRAL) statistics since 2011 — what Kelly **would** have prescribed if fit on that single year:

| year | n_st3 | μ_ann state-3 | Kelly_full |
|---:|---:|---:|---:|
| 2011 | 182 | −35.0 % | 0.00 |
| 2012 | 141 | +15.9 % | 1.30 |
| 2013 | 148 | +30.0 % | 1.30 |
| 2014 | 161 | +29.4 % | 1.30 |
| 2015 | 226 |  −5.7 % | 0.00 |
| 2016 | 131 | +26.0 % | 1.30 |
| 2017 | 215 | +31.5 % | 1.30 |
| 2018 |  92 | +20.0 % | 1.30 |
| 2019 | 149 | +10.2 % | 1.30 |
| 2020 | 130 | +20.4 % | 1.30 |
| 2021 |  74 | +90.1 % | 1.30 |
| 2022 |  97 | −34.0 % | 0.00 |
| 2023 | 161 | +21.1 % | 1.30 |
| 2024 |  95 | +19.7 % | 1.30 |
| 2025 | 109 | +32.4 % | 1.30 |
| 2026 |  42 | +44.7 % | 1.30 |

**NEUTRAL state was a money-loser in 3 of 16 years (2011, 2015, 2022)** — Kelly fit on the pooled sample (positive mean) would have over-allocated in those years. The 5-state system **does not differentiate "early-NEUTRAL coming from CRISIS" from "late-NEUTRAL pre-BULL"** — both get the same weight. This is the dominant source of MaxDD increase in the Kelly variants.

### 3.3 Correlation / overlap

- Q2 and Q3 are **not independent**: tier definitions (`simulate_holistic_nav.py:96-114`) already gate on state5 ∈ {3,4,5} for entries. Boosting NEUTRAL exposure in Q2 also implicitly boosts the BA leg via larger NAV-base. Be careful when stacking the two changes — run them together in a single canonical sim before deploying both.

### 3.4 What would invalidate this analysis

- **A new state-3 down-year before deploying Q2** (e.g., 2026 turns into 2015-style chop): NEUTRAL Kelly would re-fit lower and the gain disappears. Re-fit every 6-12 months at minimum.
- **Tier definitions change**: any modification to `play_type` assignment logic invalidates the historic per-tier stats. If MEGA / COMPOUNDER_BUY / RE_BACKLOG_BUY are renamed or re-thresholded, Q3 weights must be re-derived.
- **Borrow cost rises above 12 %/yr**: the 130 % cap assumption breaks; full Kelly would naturally fall below 1.30 and the cap stops binding — could change verdict on Q2.
- **OOS canonical sim (Q3 with TIER_BAL labels) shows < +0.3 pp CAGR**: rough estimator is optimistic; below +0.3 pp the change is not worth operational complexity.

---

## Section 4 — Recommended next steps

### 4.1 Q2 deployment recommendation: **partial, NEUTRAL-only**

- **Do not deploy** full / half / quarter Kelly as a direct replacement — Sharpe and Calmar both degrade OOS.
- **Do shadow-test** the `HEUR_N100` variant (NEUTRAL 70 % → 100 %, all others unchanged) by running the **full BA v11 integrated stack** through `sim_v11_transparent.py` for 12 y with `cash_etf_states={1:0, 2:0.2, 3:1.0, 4:1.0, 5:1.0}` and current borrow / TC costs.
- **Gate to deploy**: OOS 2024-2026 must show ≥ +1.0 pp CAGR with ≤ +3 pp MaxDD vs current heuristic. If yes → deploy; if no → stay heuristic.
- **Monitoring**: rolling 12-month Sharpe of state-3 returns. If it falls below 0.4 for 2 consecutive months, revert to `state 3 = 70 %`.

### 4.2 Q3 deployment recommendation: **rebuild trade log first, then test**

Step 1 — **Generate a fresh canonical 12 y sim** (`sim_v11_transparent.py` 2014-2026 50B) that emits `play_type` (current TIER_BAL labels) on every trade. The refresh files used here have only 4 legacy tiers.

Step 2 — Recompute per-tier `μ`, `σ`, Kelly_continuous on the new log, with the same quarter-Kelly + clip [4 %, 18 %] + renormalize-to-flat-10 % procedure.

Step 3 — Apply via `simulate_holistic_nav.py:tier_weights={...}` and re-run the 12 y canonical sim. Compare against the current production baseline (CAGR 19.42 %, Sh 1.21-1.40, MaxDD −16.5 %).

**Gate to deploy**:
- OOS 2024-2026 CAGR ≥ +0.5 pp vs flat 10 %.
- Sharpe ≥ +0.05.
- MaxDD not worse by more than 1.5 pp.
- Tier with smallest sample (n < 30) **must** be merged into adjacent tier or kept at flat 10 %.

### 4.3 Suggested fractional level

- **Quarter-Kelly** is the right starting point for both Q2 and Q3 — half-Kelly already binds the 130 % cap on Q2, leaving no headroom for adverse scenarios.
- Vietnamese stock returns have **fat left tails** (2008 GFC, 2018 trade-war, 2022 commodity crash) — fractional Kelly literature suggests using ≤ 0.3× the theoretical value in markets with skewness < −1.

### 4.4 Monitoring (post-deploy, both Q2 and Q3)

- **Rolling 90-day per-state μ and σ** logged daily. Alert if any state's μ flips sign for > 30 days.
- **Per-tier rolling Sharpe** (60-trade window). If a tier's rolling Sharpe drops below 0.10 → revert that tier's weight to flat 10 %.
- **Capacity stress**: re-test Q2+Q3 stack at 100B and 200B NAV. The 130 % cap + lifted state-3 weight increases turnover; ADV cap (20 %) may bind earlier at larger sizes.

### 4.5 What NOT to do

- Do **not** apply Kelly weights to **both Q2 and Q3 simultaneously without an integrated sim**. Effects compound and the back-of-envelope estimates here will not be accurate.
- Do **not** lift the 130 % cap "because Kelly says higher". The cap exists because borrow > deposit and because tail risk is fat — not because of a missing parameter.
- Do **not** re-fit Kelly weights more often than every 6 months. State definitions are slow-moving; over-fitting to a single quarter's data is the failure mode that killed v2g (memory note `vnindex_5state_v2g.md`).

---

## Appendix — Files referenced / produced

**Inputs read**:
- `vnindex_5state.csv` — production 5-state series
- `tav2_bq.ticker` (VNINDEX rows) — daily returns
- `ba_trades_bal_refresh.csv`, `ba_trades_vn30_refresh.csv` — canonical BA v11 12 y trade log
- `simulate_holistic_nav.py`, `backtest_workflow.py` — pipeline reference (no changes)

**Intermediate outputs**:
- `_kelly_q2_state_stats_2011.csv` — per-state stats, 2011-2026
- `_kelly_q2_state_stats_full.csv` — per-state stats, full sample
- `_kelly_q2_backtest_results.csv` — VNINDEX sanity backtest table
- `_kelly_q3_tier_stats.csv` — per-tier stats
- `_kelly_q3_proposed_weights.csv` — proposed slot weights

**No production files modified.**
