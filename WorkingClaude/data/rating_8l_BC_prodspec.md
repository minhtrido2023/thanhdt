# 8L-rating overlays B & C — prod-spec backtest (2014-01 → 2026-05)

Tests whether the **8L quality rating (1-5)** can improve the production paper-trade systems
(V1-V5) on the **canonical prod spec** (`run_5systems_prodspec.py`), the two ways flagged as the
cleanest direct uses of the rating in the existing book:

- **(B) distress-exclusion** — suppress a buy signal on a **rating-5** name (impaired: full-year
  loss or extreme real-leverage). Cut tail risk without touching the rest of the book.
- **(C) regime-conditional sizing** — weak-rating names (**rating ≥ 4**) keep full 10% weight in
  NEUTRAL/BULL/EX-BULL, but are **halved to 5% in BEAR/CRISIS (state ≤ 2)** via the simulator's
  `tier_weights_by_state` hook. Rating modulates SIZE only when the regime is risky.

## Method / integrity
- Rating computed **point-in-time** per ticker-quarter (`build_rating_8l_history.py`), stamped with
  `Release_Date` (no look-ahead), as-of merged onto the signal stream (buy-signal coverage **99.9%**).
  Port validated: latest-quarter rating matches the live `rating_8l.csv` snapshot **exactly** for all
  COMPOUNDER/CYCLICAL/INSURANCE/SECURITIES names tested.
- **Limitation (conservative):** BANK (ICB 8355) and POWER lenses are vnstock/current-only (no NPL/CAR
  history) → rated neutral **3** across all history → never excluded nor down-weighted. The overlay's
  effect is measured ONLY on names with a genuine historical fundamental read (COMPOUNDER / CYCLICAL /
  REALESTATE / INSURANCE / SECURITIES).
- Baseline reproduces the canonical control (V1 18.60% / V5 22.61%, window-dependent).

## Headline (full period 2014-01 → 2026-05)

| Sys | base CAGR/Sh/MaxDD | (B) exclude5 ΔCAGR | (C) regime_size ΔCAGR / Sh / MaxDD |
|----|----|----|----|
| V1 | 18.60% / 1.24 / −23.2 | **−0.59** | **+0.81** / 1.30 / **−19.4** |
| V2 | 22.03% / 1.65 / −16.9 | −0.49 | +0.51 / 1.71 / **−13.2** |
| V3 | 22.03% / 1.65 / −16.9 | −0.49 | +0.51 / 1.71 / −13.2 |
| V4 | 22.15% / 1.47 / −22.8 | −0.58 | +0.60 / 1.52 / **−19.6** |
| V5 | 22.61% / 1.39 / −20.7 | +0.29 | +0.97 / 1.44 / −19.8 |

## Verdict

### (B) distress-exclusion — **REJECT**
Slightly negative on V1-V4 (−0.5 to −0.6pp CAGR), Sharpe flat/down, MaxDD slightly **worse**. Only V5
marginally positive (+0.29pp, path-dependent). Per-year: the damage is concentrated in **2018 (−4 to
−5pp)** and **2023 (−1 to −1.5pp)** — hard-excluding rating-5 throws away names that were still good
**short-term momentum** trades. This reproduces the prior `redflag≥3`-exclusion finding: **the momentum
book resists hard FA exclusions; they remove winners.** A rating-5 name is impaired *fundamentally*,
but over a 45-day momentum hold it can still be the right trade.

### (C) regime-conditional sizing — **POSITIVE, worth advancing (with caveats)**
Improves **CAGR, Sharpe AND MaxDD on every system**. This is the **first FA overlay to improve the
prod-spec book on both return and risk** — EW5, the bank sub-model, and redflag-exclusion all FAILED
full-NAV (gate-not-ranker, capacity-bound). Mechanism is exactly the research thesis: **FA quality
matters in stress, is useless in bull** → so size DOWN junk only in BEAR/CRISIS.

**But read it honestly — two distinct components:**
1. **Return/Sharpe edge = small but robust across history.** Pre-selloff (2014→2025-08): V1 +0.33,
   V2 +0.16, V4 +0.26, V5 +0.80pp CAGR; Sharpe +0.03-0.05. Non-stress years are ~flat (confirms the
   `_W` tier-split is near-neutral outside stress); gains cluster in stress-dip years (2018, 2020,
   2021, 2025).
2. **MaxDD reduction (−3 to −4pp) = ONE recent episode.** The full-period max drawdown for every system
   is the **2025-09 → 2026-03 selloff** (ongoing). Pre-selloff MaxDD is **unchanged** (V1 −19.4→−19.4,
   V2 −13.0→−13.0, V4 −17.4→−17.3). So the headline DD win is the current bear — real and valuable
   (it's live OOS, helping *right now*), but **not yet confirmed across multiple independent bears**
   (in 2018/2020/2022 the state machine had already de-risked the book, leaving little for the overlay
   to trim).

**Caveats before deploy:**
- Quote the DD benefit as "**−3-4pp in the current 2025-26 bear**", NOT "robustly across cycles".
- V5 (Kelly) per-year deltas are path-dependent noise (2021 +19pp, 2025 −4pp swings) — trust V1-V4.
- Banks/power were neutral-3 (no historical lens); a live deployment using the real bank/power lenses
  could differ — re-test with the live lenses wired before committing.
- The `_W` tier split slightly reshuffles tier identity even outside stress (verified near-neutral, but
  a minor confound).
- TODO sensitivity: halving factor (0.05 vs 0.0/0.03/0.07), and `state≤2` vs `state==1`-only.

## Follow-up: (C) sensitivity sweep + bank/power lens (2026-06-05)

### ⚠️ The "sizing" mechanism is INERT — the real driver is selection priority
Swept the halving factor and the stress-state set (`run_prodspec_rating_C_sweep.py`):

| variant | V1 ΔCAGR | result |
|----|----|----|
| weak_size 0.0 / state≤2 | +0.81 | identical |
| weak_size 0.03 / state≤2 | +0.81 | identical |
| weak_size 0.05 / state≤2 | +0.81 | identical |
| weak_size 0.07 / state≤2 | +0.81 | identical |
| weak_size 0.05 / state==1 only | +0.81 | identical |
| **weak_size 0.10 / state≤2 (split only, NO weight change)** | **+0.81** | **identical** |

Every variant — including halving factor **0.10 (i.e. no weight change anywhere)** — gives the
**byte-identical** result. So the `tier_weights_by_state` lever does **nothing**. The entire effect
comes from the **tier split itself**.

**Mechanism (confirmed in `simulate_holistic_nav.py`):** the simulator selects its ≤12 positions by
`sort(-TIER_PRIORITY.get(play_type,0), -ta)` (lines 660/953). Renaming rating≥4 buys to `<tier>_W`
tiers — which are absent from the hardcoded `TIER_PRIORITY` map — drops them to **priority 0**, i.e. the
**bottom of the buy queue**. They are still in `allowed_tiers` so they can be bought, but only to fill
slots that no rating≤3 name claimed. So the real effect is:

> **Rating as a SOFT selection-priority gate** — fill the 12 slots with rating≤3 names first; let
> rating≥4 names fill only leftover capacity. **Global (all regimes), selection (not sizing),
> not regime-conditional.**

This also explains why it works where (B) failed: (B) HARD-excludes rating-5 (never bought) → loses the
cases where a weak-but-high-momentum name was the best available trade. The soft demotion keeps weak
names as last-resort fill (better than idle capital) while letting quality win the contested slots.
The per-year gains cluster in high-signal years (2021/2025 bulls) because the priority only **binds**
when >12 candidates compete for the slots.

### Bank/power lens robustness (ROE-rated point-in-time, not neutral-3)
Re-ran with banks/power rated by their real ROE history (`rating_8l_history_roe.pkl`) instead of
neutral-3. Verdict **holds**: V1 +1.03 (vs +0.81 neutral), V2 +0.71 (+0.53), V4 +0.70 (+0.61),
V5 +0.29 (+0.99, attenuated). Direction unchanged on V1/V2/V4; the neutral-3 simplification does NOT
distort the conclusion (if anything it slightly understated the gain on the BASE systems).

### Net reframed verdict (pre random-control)
- **The deployable artifact is a rating SOFT-PRIORITY gate** (demote rating≥4 to the back of the buy
  queue), +0.5–0.8pp CAGR / +0.05 Sharpe / −3–4pp MaxDD on V1-V4. NOT "regime-conditional sizing".

## RANDOM-DEMOTION CONTROL (2026-06-05) — splits the CAGR from the MaxDD effect
Demoted a RANDOM matched-count set of buy signals (21.9% = the rating≥4 share) to priority-0, 3 seeds,
vs the rating-based demotion (`run_prodspec_rating_C_sweep.py RANDOM_DEMOTE=1`):

| | rating-demote | random s1/s2/s3 | base |
|----|----|----|----|
| **V1 CAGR** | +0.81 | **+1.15 / +0.78 / −0.12** | — |
| **V1 MaxDD** | **−19.4** | −23.8 / −22.1 / −21.6 | −23.2 |
| **V2 CAGR** | +0.53 | +0.68 / +0.62 / −0.16 | — |
| **V2 MaxDD** | **−13.5** | −17.9 / −15.7 / −15.8 | −17.3 |
| **V4 CAGR** | +0.61 | +0.69 / +0.57 / −0.03 | — |
| **V4 MaxDD** | **−19.5** | −23.3 / −22.3 / −21.5 | −22.8 |

**The CAGR gain is NOT a rating effect.** Random demotion's CAGR deltas straddle the rating value
(random_s1 BEATS rating on V1/V2/V4). Demoting ~22% of buy signals to the back of the queue by ANY rule
bumps CAGR — it's a capacity/reshuffle artifact (tighter, different 12-name book), not rating quality.

**The MaxDD reduction IS a genuine rating effect.** Random demotion leaves MaxDD at ~baseline
(V1 −22.5 avg ≈ base −23.2; V4 −22.4 ≈ −22.8); only **rating** demotion cuts it −3 to −4pp (V1 −19.4,
V2 −13.5, V4 −19.5). The 8L rating specifically identifies the names that crater in the 2025-26 bear;
random names don't. Sharpe echoes this: rating-demote Sharpe ≥ every random seed on every system.

### FINAL VERDICT
- **(B) hard-exclude rating-5 → REJECT** (−0.5pp, removes momentum winners).
- **(C) regime sizing → the sizing lever is INERT** (weight 0.0–0.10 & state≤2/==1 all identical).
- **The genuine, deployable finding: 8L rating ≈ a DRAWDOWN GATE, not a return enhancer.** Demoting
  rating≥4 names to the back of the buy queue cuts MaxDD −3-4pp (V1/V2/V4) in the 2025-26 bear, an
  effect a random-demotion control CANNOT reproduce. The CAGR bump (+0.5-0.8pp) is a capacity artifact
  (random matches it) → do NOT sell it as alpha. This **confirms the standing thesis** ([[fa_layer_ic_audit_2026]],
  DT5G): FA/quality = a risk GATE (insurance), not a ranker.
- Caveats: DD benefit is one recent bear (needs more episodes); the gate fires via priority-0 (extreme)
  — a milder priority demotion is untested.

## REAL bank NPL lens (2026-06-05) — point-in-time, via vnstock
vnstock VCI `finance.ratio(period='quarter')` DOES carry historical NPL/coverage/ROE, **~2018→now**
(32 quarters, not back to 2014). `build_bank_npl_history.py` pulled all 18 banks (528 bank-quarters),
applied the live `rate_bank` logic (ROE base + NPL/coverage differentiator) per quarter, stamped each
with quarter-end+45d (no look-ahead), and merged into `rating_8l_history_banknpl.pkl` (banks 2018+ now
carry REAL ratings; latest matches the live snapshot exactly — VCB=1, CTG=1, STB/EIB/SSB=5). Pre-2018
banks fall back to neutral.

Re-running the rating demotion with real bank ratings vs the neutral-3 version:

| | banknpl: CAGR/Sh/MaxDD | neutral: CAGR/Sh/MaxDD | base MaxDD |
|----|----|----|----|
| V1 | +1.09 / 1.31 / −19.4 | +0.81 / 1.30 / −19.4 | −23.2 |
| V2 | +0.73 / 1.69 / −13.6 | +0.53 / 1.69 / −13.5 | −17.3 |
| V4 | +0.76 / 1.51 / −19.2 | +0.61 / 1.50 / −19.5 | −22.8 |
| V5 | +0.48 / 1.39 / −21.3 | +0.99 / 1.42 / −19.9 | −20.8 |

**Verdict holds with the real bank lens** — the drawdown-gate effect is preserved (V1/V2 identical DD,
V4 marginally better −19.2). Rating banks by real NPL instead of neutral-3 does not change the
conclusion (it slightly lifts CAGR on V1/V2/V4; V5 stays noisy). The 8L rating's value remains a
**drawdown gate, robust to how banks are scored**.

## (a)(b)(c) follow-ups (2026-06-05)

**(a) DD benefit is broad-based, not one episode** (episode-level drawdown of base vs rating-demote,
`analyze` on `_navs.csv`). Rating-demote cuts DD in MANY drawdowns: 2021-01 +0.7/+0.5pp, 2021-07
+1.9/+2.0pp, 2024-04→25 +0.9/+1.1pp, **2025-09→26-03 +4.1/+3.4pp** (V1/V4); it slightly HURT only in
the 2018 bear (−0.5/−1.1pp). Sign positive in most episodes, dominant in 2025-26 → genuine multi-episode
rating effect (corroborates the random-control: random cuts DD in none).

**(b) the demotion must be substantive — but priority-0 is NOT required.** Swept how hard rating≥4 is
pushed down the queue (`DEMOTE_PRIORITY`):

| level | V1 DD | V2 DD | V4 DD |
|----|----|----|----|
| base | −23.2 | −17.3 | −22.9 |
| **mild** (parent−0.5, within-tier tiebreak) | **−24.0** | −17.8 | −23.0 |
| **moderate** (parent−20, ~one tier band down) | **−19.4** | −14.2 | −19.6 |
| **extreme** (priority 0) | −19.4 | −14.2 | −19.2 |

Mild does **nothing** (DD even worsens) — a within-tier tiebreak can't beat `ta`, so rating≥4 high-`ta`
names still win slots. **Moderate ≈ extreme** — demoting rating≥4 by ~one tier band captures the FULL
DD benefit. → deployable as a moderate priority demotion; the rock-bottom priority-0 is unnecessary.

**(c) all lenses historical (bank real-NPL + power ROE) — verdict robust.** `rating_8l_history_full.pkl`
(bank=vnstock NPL 2018+, power=ROE-historical, no neutral-3 anywhere). Rating-demote (extreme):
V1 +0.89/DD−19.4, V2 +0.57/−14.2, V4 +0.62/−19.2, V5 +0.65/−20.1. The drawdown gate (−3-4pp V1/V4)
is preserved with power included; CAGR a touch below bank-only but DD intact. Conclusion unchanged.

## Files (updated)
- `build_rating_8l_history.py` → `data/rating_8l_history.pkl` (+ `_roe` via `BANK_POWER_MODE=roe`)
- `build_bank_npl_history.py` (vnstock) → `data/bank_rating_history.{pkl,csv}` → merged `rating_8l_history_banknpl.pkl`
- `run_prodspec_rating_BC.py`, `run_prodspec_rating_C_sweep.py` (sweep / RANDOM_DEMOTE / bank-npl)
- `data/rating_8l_C_sweep_{neutral,_roe,splitdiag,randctl,banknpl}.csv`, `analyze_rating_BC.py`

## Files
- `build_rating_8l_history.py` → `data/rating_8l_history.pkl` (+ `_roe` variant via `BANK_POWER_MODE=roe`)
- `run_prodspec_rating_BC.py` → `data/rating_8l_BC_prodspec.csv` + `_navs.csv`
- `run_prodspec_rating_C_sweep.py` → `data/rating_8l_C_sweep_{neutral,_roe,splitdiag}.csv`
- `analyze_rating_BC.py` (per-year + per-crisis breakdown)
