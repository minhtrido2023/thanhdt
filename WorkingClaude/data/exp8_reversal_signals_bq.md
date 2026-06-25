# Exp-8 REVISED — Reversal-signal triggers (A vol / B RSI-reversal / C RSI-divergence) + MGE 1.3

**Taylor, 2026-06-24** · Tier-3 BQ · self-check **0 VND** all runs · answers Mike `exp8-revised` + user follow-up Q1/Q2/Q3.

> **Correction:** my first pass executed the *superseded* `exp8-capit-only-task` (vol 3M/6M only). This doc
> delivers the **revised** task: Signal A (vol) / B (RSI oversold-reversal) / C (RSI bullish-divergence),
> Test A / A∨B / A∨B∨C, plus the 1.6x sensitivity (Q2) and the 2011→now event-by-event validation (Q1).

## Signals (all causal; gate unchanged = CRISIS/BEAR state ∧ pb_z ≤ −0.5 ∧ postbull-clear)

- **A — Vol spike**: `Volume_VNINDEX[T] / mean(Volume[T−63..T−1]) ≥ thr` (3M baseline).
- **B — RSI oversold-reversal**: `D_RSI_VNINDEX < 0.30` for ≥3 consecutive days AND turning up (`RSI[T] > RSI[T−3] + 0.02`).
- **C — RSI bullish-divergence**: in a 10-day window `Close[T]` is a new low but `RSI[T] > RSI@prior-in-window-Close-low`.

ANY enabled signal firing inside the gate → T+1 full (depth-scaled) deploy + MGE 1.3 on the CAPIT arm, then HOLD (idempotent).

## Q1 — Event-by-event validation, 14 deep CRISIS/BEAR episodes (pb_z≤−0.5), 2011→now

Δ = signal-A(1.7x) fire − VNINDEX bottom, calendar days (negative = fired **before** bottom):

| episode | bottom | A@1.7x fire (Δ) | A@1.6x | B (RSI-rev) | C (div) |
|---|---|---|---|---|---|
| 2011-05-25→06-03 | 2011-05-25 | 06-03 (+9 late) | 05-26 | 05-26 | — |
| 2011-07-18→2012-01-18 | 2012-01-06 | 2011-08-30 (**−129 early**) | 08-30 | 08-16 | 07-22 |
| 2012-03-15→09-21 | 2012-08-28 | 2012-03-15 (**−166 early**) | 03-15 | — | 05-24 |
| 2013-02-21→08-09 | 2013-03-05 | 02-21 (−12) | 02-21 | — | — |
| 2020-02-07→05-12 (COVID) | 2020-03-24 | **2020-03-12 (−12 ✓)** | 03-09 | **03-25 (+1 ✓)** | 02-26 |
| 2022-09-06→2023-01-17 | 2022-11-15 | 2022-12-01 (+16 late) | 12-01 | — | 11-07 |
| 2025-04-09→05-05 (tariff) | 2025-04-09 | — (gate closed) | — | — | — |
| *(7 small episodes: 2012-11, 2019-11, 2020-06/08/10, 2023-03/04)* | | no in-gate fire | | | |

**Read:** Signal A timing is **inconsistent** — excellent at COVID/2013 (−12d), but **fires 4–5 months too early in
slow grinds** (2011–12: −129/−166d = deploys at episode start, rides down), and **late** in 2022 (+16d). Signal **B
is rare & precise** (lands AT the bottom: COVID +1d) but only fires in 4/14 episodes. **C is early/noisy.** The
gate filters most noise — selectivity 2011→now (fires total / outside-gate FP): A@1.7x 175/77%, A@1.6x 252/79%,
**B 14/43%** (most selective), C 56/79%.

## Q2 + Q3 — Tier-3 BQ performance (same-snapshot 2026-06-24, all 0 VND)

| config | FULL CAGR | Sharpe | MaxDD | Calmar | OOS CAGR | OOS Cal | vs A_1.7x |
|---|---|---|---|---|---|---|---|
| Baseline V2.4-LF | 28.04% | 1.69 | −31.5% | 0.89 | 30.28% | 0.96 | — |
| **A — vol 1.7x (WINNER)** | **31.07%** | **1.87** | **−20.5%** | **1.52** | 35.82% | 1.75 | — |
| **A — vol 1.6x (Q2)** | 30.14% | 1.81 | −26.3% | 1.15 | 33.97% | 1.29 | **−0.93pp, −5.8pp DD** |
| **A∨B — +RSI-reversal (Q3)** | 31.07% | 1.87 | −20.5% | 1.52 | 35.82% | 1.75 | **±0.00 (neutral)** |
| **A∨B∨C — full combo (Q3)** | 29.54% | 1.77 | −29.7% | 0.99 | 32.78% | 1.10 | **−1.53pp, −9.2pp DD** |

### Answers

**Q2 — 1.6x is WORSE, keep 1.7x.** 1.6x fires ~3 days earlier into the COVID crash (2020-03-09 vs 03-12) plus
extra early prints → deploys leveraged before the bottom → −0.93pp CAGR and DD −20.5→−26.3. (Resolves the
P97 confusion: exp6's "1.6x = P97" is for the **21d** baseline; for the **63d** baseline P97 ≈ 1.7x. Empirically
1.7x dominates — waiting for the stronger print avoids early-deploy drawdown.)

**Q3 — B is redundant (+0.00pp), C is harmful (−1.53pp).**
- **Signal B** opens **no new episode** in 2014–2026: its COVID fires (2020-03-25→04-01) land inside the episode
  Signal A already opened on 03-12 → idempotent. B's standalone value (catching crises where vol does NOT spike
  but RSI reverses) only appears in **2011–2013** (pre-harness), so the 2014+ backtest can't reward it. Not harmful,
  just dormant here — defensible to keep as a **free secondary trigger** for a future no-volume crisis.
- **Signal C is actively harmful**: it fires **too early** (2020-02-26 *pre-crash*; 2022-11-07 a week before A),
  deploying 1.3x leverage before the bottom → rides the crash down → DD −20.5→−29.7, −1.53pp CAGR. It defeats
  the entire wait-for-capitulation thesis. **Reject Signal C.**

## Verdict

**Signal A (vol 1.7x / 3M) alone is the winner — the RSI signals do not improve it.** B is neutral (subsumed by A
in-window; keep only as cheap insurance for a no-volume crisis), C is harmful (early leveraged entry). The
recommended config is **A-only, 1.7x, 3M, MGE 1.3** = the Exp-8 Test A: **31.07% / −20.5% / Cal 1.52**, beating
V2.4-LF by **+3.03pp CAGR / +11pp MaxDD / +0.63 Calmar** (same-snapshot), 0 VND.

## Caveats
- **Cite DELTA** vs same-snapshot baseline (28.04%), not the brief's 30.63%/−17.5% (data drift: VVS/VCS/DTD corp-actions).
- **A's early-fire risk** (2011–12 slow grinds, −129/−166d) is *invisible to the 2014+ harness*. In a future
  slow L-shaped crisis A could deploy leveraged too early. Flag for Spyros — this is the main residual risk of the lever.
- Real leverage (MGE 1.3) → Spyros sign-off + user approval before LIVE; go-live default stays leverage-free unless promoted.
- IS/OOS is a weak overfit test here (deploys are all OOS by construction, like DT5G); A beats baseline in both IS and OOS.

---

## Exp-8 v2 — refined Signal C as a CONFIRM (user idea + DT5G `D_RSI_BullDvg`) — 2026-06-25 (Tier-3 BQ, 0 VND)

User insight: C is *early* but flags "bottom approaching" — so use it as a **leading arm**, with A as the
capitulation **confirm** (never deploy on C alone). Refined C per the DT5G `_BullDvg` pattern (filter.json):
**RSI rising vs 3M ago AND price flat/up ≤6% vs 3M ago, after a genuine 3M washout (rolling-63d RSI min <0.40)
and not yet recovered (RSI<0.60)**. Deploy = (A or B) fires AND C armed within last K sessions.

| config | CAGR | Sharpe | MaxDD | Calmar | vs A-only |
|---|---|---|---|---|---|
| A-only 1.7x (prior winner) | 31.07% | 1.87 | −20.5% | 1.52 | — |
| **A ∧ C-confirm K=30** | **31.31%** | 1.91 | −20.6% | 1.52 | **+0.24pp, =DD** |
| **A ∧ C-confirm K=40** | **31.81%** | 1.92 | −20.6% | 1.54 | **+0.74pp, =DD** |

**Why it helps (not hurts like standalone-C v1):** C-confirm SUPPRESSED the premature 2022 deploys —
A-only fired 2022-11-16→12-06 (7 prints, riding the late-Nov chop with leverage); A∧C deployed only at the
C-confirmed 2022-12-06 → higher return at equal DD. COVID deploys preserved (03-12/03-19/04-21). And
event-by-event 2011+ it FIXES Signal A's worst failure: 2012 slow-grind A-only −166d (deploy at episode start)
→ A∧C-armed **−4d** (deploy at the actual bottom). That 2012 fix is pre-harness (invisible to 2014+ CAGR) but
is the exact out-of-sample tail risk flagged for Spyros — now closed at zero in-sample cost.

**Verdict:** 🟢 **A ∧ C-confirm (refined BullDvg arm) supersedes A-only as the recommended lever config** —
slightly higher return, identical DD (−20.6%), self-check 0 VND, AND removes the slow-grind early-fire risk.
K=30 conservative default (31.31%); K=40 edges higher (31.81%) but don't over-tune K to 2-3 episodes. Reverses
the v1 "Signal C harmful" finding — that was C-as-standalone-trigger with a crude 10d divergence; the refined
BullDvg arm in a confirm role is the right use. **Real leverage MGE 1.3 → still needs Spyros + user before LIVE.**
