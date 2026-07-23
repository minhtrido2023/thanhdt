# LAG (PEAD) weakness — regime vs quality decomposition + gate design
Job Taylor_20260723_131958 · 2026-07-23 · Taylor (quant) · R&D only, wires nothing.

Engine: standalone LAG-only NAV ledger (canonical spec NP_R≥15 ∧ prior_n_good≥4 ∧
pa_HL3≥5, entry T+5, hold 25d, MAX_POS 12, POS 8%). 5,389 admitted signals, 550
filled trades, 2014-2026. All regime/rating/surprise attributed **point-in-time at
entry**. Scripts: `lag_common.py`, `stage1_decomp_ic.py`, `stage2_gates.py`,
`stage3_loo_dsr.py`. LAG-only ≠ blended V2.4 (27%); this isolates the sleeve.

## Q1 — where is the weakness
LAG-only full-period: CAGR 16.03% / Sharpe 1.16 / MaxDD −18.3% / Calmar 0.88.
Per-year realized trades are fine through 2025 (2025 WR 75%, avg +8.9%). **The decline
is specifically 2026-H1 entries**: event-level avg post_ret **−0.82%, WR 30%** (vs
historical ~+4.5% / ~55%). Weak prior years: 2019 (+0.77%), 2022 (+0.01%, bear) — both
low-return market years. So "recent weakness" = the 2026 falling-market window.

## Q2 — CORE TEST: does surprise lose meaning in bad markets? **NO.**
IC(surprise, post_ret) by regime at entry (Spearman, t-stat):

| regime bucket | N | avg post_ret | IC_surprise | t |
|---|---|---|---|---|
| DT5G BEAR(1) | 1087 | **+1.96%** | **+0.125** | +4.16 |
| DT5G NEUTRAL(3) | 2826 | +4.07% | +0.079 | +4.21 |
| DT5G BULL(4) | 1059 | **+6.78%** | +0.034 | +1.12 |
| DT5G EX-BULL(5) | 110 | +19.16% | +0.067 | +0.70 |
| VNI dd −20..−10 (mild) | 1155 | +3.44% | **+0.173** | +5.95 |
| VNI dd ≤ −20 (deep crisis) | 501 | +4.53% | **−0.026** | −0.58 |
| VNI 6m −10..0 (falling) | 862 | +3.49% | **+0.154** | +4.58 |

**Two facts that split the user's hypothesis:**
1. **Surprise IC is PRESERVED and even STRONGEST in bad-but-not-crisis regimes** (BEAR
   0.125, mild-drawdown 0.173, falling-6m 0.154) — vs WEAKEST in BULL (0.034, n.s.).
   Top-minus-bottom-surprise return spread is also *largest* in BEAR (+4.90pp vs +2.78pp
   in BULL). The signal still ranks names — arguably better — when the market is fearful.
2. **What collapses is the LEVEL, not the ranking**: average post_ret drops from +6.78%
   (BULL) to +1.96% (BEAR). Risk-off compresses the *whole* earnings-drift premium
   (every name's beta drags), independent of whether surprise still discriminates.

→ User's "NĐT sợ giảm hơn sợ tăng" is **right about the LEVEL** (the premium compresses
in fear) but **wrong about the signal** ("surprise không có ý nghĩa" — it still works,
even sharper). The ONE place surprise genuinely dies is **deep crisis (dd ≤ −20%)**:
IC −0.026, insignificant — everything correlates to 1, idiosyncratic earnings drown.

## Q4 — 2026 decline: regime vs quality attribution (numbers)
2026 entries N=287, avg −0.82%. Gap vs 2023-25 (+4.60%) = ~5.4pp.
- **rating-fail % is NOT elevated**: 39% in 2026 vs 36-41% historically → the book did
  **not** suddenly pick worse-quality names.
- Split 2026 by rating: pass (≤3) **+0.38%**, fail (>3) **−2.69%**. Gating rating>3 lifts
  2026 from −0.82% → +0.38% = **~1.2pp recovered ≈ 22% of the gap = QUALITY component.**
- The remaining ~4.2pp (**~78% = REGIME**): even the clean rating≤3 book made only +0.38%
  vs +4.5-5% historically. Split 2026 by DT5G: state-3 entries **−3.15%**, state-4 +1.76%
  — the book kept buying full-size while the market fell, because **DT5G still labeled it
  NEUTRAL(3)/BULL(4)** (DT5G is slow by design; 25-session commit).

**Verdict: 2026 LAG decline ≈ 78% regime (market-level compression) + 22% quality tail.**
User's regime-dominant intuition confirmed; quality is a real but secondary contributor.

## Q3 — gate backtests (same engine; full + IS 2014-19 / OOS 2020-26; DSR; LOO)

| variant | CAGR | Sharpe | MaxDD | Calmar | IS_Sharpe | OOS_Sharpe | OOS_Calmar |
|---|---|---|---|---|---|---|---|
| **a BASELINE** | 16.03% | 1.16 | −18.3% | 0.88 | 0.95 | 1.34 | 1.13 |
| b rating≤3 | 15.94% | 1.19 | −17.2% | 0.93 | **0.80↓** | 1.49 | 1.35 |
| c1 half<MA200 | 14.28% | 1.16 | −15.5% | 0.92 | 0.83 | 1.43 | 1.40 |
| c2 half neg-6m | 14.67% | 1.16 | −15.4% | 0.95 | 0.84 | 1.42 | 1.42 |
| **c4 half DT5G≤2** | **15.86%** | **1.30** | **−15.1%** | **1.05** | **1.08↑** | 1.47 | 1.41 |
| c5 half DT5G≤1 | 15.79% | 1.26 | −16.8% | 0.94 | **1.08↑** | 1.41 | 1.41 |
| d rating≤3 + half<MA200 | 14.19% | 1.18 | −15.3% | 0.93 | **0.67↓↓** | 1.57 | 1.65 |

**Winner = c4/c5: proportional sizing — HALF-size LAG entries in DT5G BEAR/low-neutral,
full size otherwise.**
- CAGR-neutral (−0.17pp), Sharpe 1.16→1.30, MaxDD −18.3→−15.1%, Calmar 0.88→1.05.
- **Improves BOTH IS (Sharpe 0.95→1.08) and OOS** — not an OOS-only artifact.
- **DSR 0.999** (N_trials=10, sr0=0.028) > baseline 0.994 > 0.95 gate ✓.
- **LOO-by-year robust**: edge flat (~−0.17pp CAGR every year, no single year carries it).
- self-check: min NAV +49.9B, no negative cash, 0-VND-clean.
- Economic story (not data-mined): size down where the drift *premium is demonstrably
  thin* (BEAR level +1.96% vs BULL +6.78%), keep full where it pays. Keeps the strong-IC
  BEAR *selection* but at reduced size — appropriate since the level, not the ranking, is
  what's weak there.

**Rejected:**
- **rating≤3 (b)**: CAGR-neutral, helps OOS DD, but **IS-NEGATIVE** (Sharpe 0.95→0.80) →
  benefit is 2020+-only, not robust. Trims the 2026 rating>3 tail (~1.2pp) but weak
  standalone.
- **price-trend cuts (c1/c2)**: robustly **COST ~1.5pp CAGR every year** (LOO −1 to −2pp
  all years) because they also cut BEAR-rebound trades (best-IC bucket). Justified only
  under a pure drawdown-minimization mandate, not as return-neutral improvers.
- **combo d**: best OOS but worst IS (Sharpe 0.67) → overfit-flavored. NO.

## Critical tension to surface (do NOT paper over)
The winner **c4/c5 would NOT have prevented the 2026 loss** — 2026 entries were DT5G
state 3/4, so the gate never fired. DT5G is slow by design and lagged the falling market.
- To catch *fresh* drawdowns like 2026 you need a faster **price** gate (below-MA200 /
  neg-6m) — but those robustly cost ~1.5pp CAGR/yr. Genuine tradeoff.
- The 78%-regime part of the 2026 decline is **level compression no name-gate can fix**;
  the honest lever there is *sizing to regime*, and DT5G's slowness limits how early that
  can act.

## Current regime (2026-07-23) & TRC read
VNINDEX: dd −11.9% from 1y peak, below MA200 (−4.1%), 6m −9.6%, RSI 0.30 (oversold),
DT5G still **NEUTRAL(3)**. This is the **mild-drawdown / falling-6m bucket = historically
the STRONGEST surprise-IC regime (0.173 / 0.154) but with a COMPRESSED level.** So the
correct stance now: LAG surprise *selection remains valid, even sharper — but size down*
(the level is thin). c4/c5 wouldn't auto-fire (DT5G=3); a price-trend overlay would say
half-size. TRC additionally rating-fails (prior job) → both lenses argue small/cautious.
Decision stays with Mike/user.

## Recommendation
1. **Candidate to route to quant-skeptic before any wiring: c4/c5** (DT5G-proportional
   half-sizing) — robust risk-adjusted improvement, CAGR-neutral, passes DSR/IS-OOS/LOO.
   Frame as **insurance / risk-sizing, not a return booster**, and note it does not fix
   fresh-drawdown weakness (DT5G slow).
2. Optional separate insurance option for user to weigh: a faster **price-trend half-size**
   overlay that DOES catch fresh drawdowns but costs ~1.5pp CAGR/yr — pure DD-vs-return
   trade, user's call.
3. **Do NOT** deploy a blanket rating≤3 LAG gate as a return fix (IS-negative). The 8L
   rating≤3 filter already exists elsewhere as a binary quality gate; adding it to LAG
   only trims a modest tail and hurts in-sample.
4. Next step if pursued: re-run inside blended V2.4 (BAL+LAG) to size the production
   impact — this decomposition is on the isolated LAG sleeve.
