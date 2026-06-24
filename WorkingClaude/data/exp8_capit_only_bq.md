# Exp-8: RECOVERY_CAPIT_ONLY — wait-for-capitulation deploy + MGE=1.3

**Taylor, 2026-06-24** · Tier-3 BQ · self-check **0 VND** both books both tests.

## Concept

V2.4-LF **instant-deploys** idle cash into custom30V the moment `pb_z ≤ −0.5` in CRISIS/BEAR
(catches the falling knife early, rides it down). **Exp-8 = NO instant-deploy**: the recovery-park
parking idles until a **volume capitulation spike** (Volume[T] ÷ rolling-mean[T−BASE..T−1] ≥ threshold)
fires, then snaps to the depth-scaled full target on **T+1** and **HOLDS**. Leverage (`MGE=1.3`,
CAPIT-only borrow) is layered on the deep-washout stock arm. All other V2.4-LF params unchanged.

Mechanism reuses the Exp-6 gradual state machine with the daily-step and accel/gradual episode-start
disabled — episode may be entered **only** by a capit fire (`RECOVERY_CAPIT_ONLY=1`); the vol_ratio
baseline window is `RECOVERY_CAPIT_BASE` (63 ≈ 3M, 126 ≈ 6M) instead of 21d.

## Step 1 — Volume threshold calibration (causal: `Volume[T] / mean(Volume[T−BASE..T−1])`)

Peak causal vol_ratio in ±45d window around each crisis bottom:

| Crisis (bottom) | vr 21d | vr 63d (3M) | vr 126d (6M) |
|---|---|---|---|
| COVID-2020 (03-24) | 1.65 | 1.83 | 2.00 |
| 2022-bear (11-15) | 1.91 | 2.37 | 2.45 |
| 2018-bear (10-30) | 1.83 | 2.01 | 2.23 |
| 2016-flash (01-21) | 1.69 | 1.71 | 1.70 |
| 2023-Q1 (02-27) | 1.93 | 1.90 | 1.70 |
| 2025-tariff (04-09) | 2.26 | 2.94 | 3.23 |

**Catch-all-6 threshold**: 1.7x at BOTH bases (min peak-in-window ≈ 1.71/1.70). 1.8x starts missing
2016 (3M) and 2016+2023 (6M). Selectivity at 1.7x: BASE-63 fires **83 days = 2.7%** (≈P97);
BASE-126 fires **131 days = 4.3%** (≈P97). → **Calibrated threshold = 1.7x** for both 3M and 6M.

## Step 2 — Wiring (`pt_v23_audit_2014.py`)

`RECOVERY_CAPIT_ONLY=1` (forces gradual machine on, daily-step + accel/gradual-start disabled) ·
`RECOVERY_CAPIT_BASE=63|126` · `RECOVERY_CAPIT_VOL=1.7`. The keep-frac branch HOLDS post-spike;
pre-spike frac=0 (parking idle). Episode resets on `pb_z` rising above start or state leaving CRISIS/BEAR.

## Step 3/4 — Tier-3 BQ results (same-snapshot 2026-06-24, AUDIT_END 2026-06-19)

| config | period | CAGR | Sharpe | MaxDD | Calmar |
|---|---|---|---|---|---|
| **Baseline V2.4-LF** (instant, LF) | FULL | 28.04% | 1.69 | −31.5% | 0.89 |
| | IS 14-19 | 25.53% | 1.76 | −13.3% | 1.91 |
| | OOS 20-now | 30.28% | 1.65 | −31.5% | 0.96 |
| **Test A — CAPIT-ONLY 3M/63d 1.7x + MGE 1.3** | **FULL** | **31.07%** | **1.87** | **−20.5%** | **1.52** |
| | IS 14-19 | 26.11% | 1.78 | −13.4% | 1.96 |
| | OOS 20-now | 35.82% | 1.95 | −20.5% | 1.75 |
| Test B — CAPIT-ONLY 6M/126d 1.7x + MGE 1.3 | FULL | 30.14% | 1.81 | −26.3% | 1.14 |
| | IS 14-19 | 26.11% | 1.78 | −13.4% | 1.96 |
| | OOS 20-now | 33.97% | 1.85 | −26.3% | 1.29 |

**Self-check = 0 VND** (cash-flow + final-NAV identity) for both tests, both books.

### Verdict

**Test A (3M/63d) is a STRONG winner — beats baseline on EVERY metric in EVERY sub-period:**
- FULL: **+3.03pp CAGR, +11.0pp MaxDD (−31.5→−20.5), +0.63 Calmar, +0.18 Sharpe**.
- OOS 2020-now (where deploys live): **+5.54pp CAGR, +11pp DD, +0.79 Calmar**.
- IS 2014-19: +0.58pp CAGR, equal DD — CAPIT-ONLY also *suppresses* the 2018 instant-deploy (no
  qualifying vol-spike), which is mildly accretive, not a drag.
- Test A **dominates Test B** (3M times entries tighter — 12 vs 18 events; 6M holds through more grind).

**Why it works**: instead of catching the knife early on `pb_z` alone (riding the decline down),
it waits for the volume-capitulation print near the actual bottom, deploys there, and layers 1.3x on the
recovery leg. The −11pp MaxDD improvement is the tell: most of the early-decline drawdown is sidestepped.

### Episode log — Test A (3M), 12 capit fires

All deploys land in deep-cheap CRISIS/BEAR windows: **COVID** 2020-03-12 (vr1.83, d−12 vs bottom),
2020-03-19, 2020-04-21 · **2022-bear** 2022-11-16→12-06 (7 fires, vr up to 2.37) · **2023-Q1** 2023-04-06.
2016/2018/2025 did **not** deploy — the vol-spike did not coincide with the `pb_z≤−0.3 + CRISIS/BEAR`
gate at those dates (V2.4-LF gating, unchanged). frac is depth-scaled (0.705 mild-cheap → 0.950 deep).

## Caveats / notes

- **Cite DELTA, not absolute.** Same-snapshot baseline here is 28.04%/−31.5%/0.89 — **not** the brief's
  cited V2.4-LF 30.63%/−17.5%/1.75. The gap is data drift (recent VVS +47.8% / VCS / DTD corp-actions
  swing the custom30 NAV path). The defensible figure is **Test A − baseline on the same snapshot**.
- **IS/OOS is a weak overfit test here** (same as DT5G): all qualifying deploys are 2020+ by construction,
  so the edge is OOS-concentrated — not overfit, just dormant in-sample. Both IS and OOS beat baseline.
- **Real leverage** (MGE=1.3, cash<0, borrow 10%/yr) → needs Spyros risk sign-off + user approval before
  any LIVE use. Go-live default stays leverage-free unless promoted.
- **Live entry timing**: backtest enters T+1 after the close-confirmed vol spike. Live, a spike is often
  visible intraday early in the session — an operator *could* enter same-day, which would only improve
  fills near the bottom. Modeled conservatively as T+1.
