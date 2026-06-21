---
name: T+1 Intraday Buy-Point Results (2026-05-17, UPDATED with full coverage)
description: Layer 3 — does buy POINT within T+1 day matter? With expanded intraday coverage (335 tickers, vnstock bulk fetch): YES, +1.2-1.3pp CAGR alpha by avoiding ATO. Deploy "wait 15+ min before market BUY".
type: project
originSessionId: df3c1340-40c2-46c7-b6dc-247737308843
---

# T+1 Intraday Buy-Point — Results (2026-05-17, expanded coverage)

**Question**: Given the realistic T+1 day constraint, does buying at a specific
intraday point (ATO/Open vs 09:15 vs 11:15 vs VWAP vs ATC) deliver material
CAGR alpha over the canonical BQ.Open-based T+1 fill?

**Answer**: 🟢 **YES — asymmetric rule**:
- **BUY at T+1 14:45 ATC** (with liquidity gate / hybrid for non-TOP tickers)
- **SELL at T+1 09:00 OPEN/ATO** (already canonical, optimal — do not change)

Combined: **+1.81 to +2.11pp CAGR / +0.09-0.11 Sharpe / unchanged MaxDD** on
2.5y v11 stack. Phase 5 sell-curve revealed every later sell-slot LOSES alpha
(-7.61pp in 2026 BEAR if selling at ATC instead of OPEN); the current canonical
"sell at next-day Open" was correct already.

## Update history

- **2026-05-17 v1** (98-ticker intraday cache, 30% trade coverage):
  Per-trade alpha +0.82pp for T1115_LIM but NAV alpha only +0.18pp → declared NULL
- **2026-05-17 v2** (335-ticker cache via vnstock bulk fetch, ~99% trade
  coverage): NAV alpha +1.2-1.3pp across 11:15 / VWAP / Open-LIM → ADOPT.
  Initial recommendation was T1115_MKT.
- **2026-05-17 v3** Phase 3 full intraday curve (16 slots × 4 sub-periods):
  optimal is **14:45 ATC** (+1.81pp full, +0.74pp BEAR); morning slots reverse
  sign in BEAR. v3 supersedes v2's T1115_MKT recommendation.
- **2026-05-17 v4 (current)** Phase 4 (liquidity gate) + Phase 5 (sell-curve):
  - **Liquidity check**: only 11.3% of ticker-sessions have ATC volume to fill
    a 1.25B VND position within 20% of bar volume. ATC works cleanly only for
    T1_TOP tickers (ADV ≥ 50B/day = 87/335 universe).
  - **ATC REALISTIC (gated → fallback to OPEN)** actually OUTPERFORMS optimistic
    ATC: +2.11pp vs +1.81pp full, +1.26pp vs +0.74pp BEAR. The gated-out trades
    (thin-book tickers) had WORSE ATC fills, so excluding them helps.
  - **HYBRID (ATC for T1_TOP, T1115 for non-TOP)**: +1.75pp full, +1.25pp BEAR.
    Operationally cleaner (no partial-fill risk).
  - **Sell-side curve (Phase 5)**: every later sell-slot LOSES alpha. ATC sell
    in 2026 BEAR is -7.61pp/yr. **Current canonical T+1 Open sell IS optimal**
    — no sell-side change needed.

## Scripts

- `layer3_t1_buypoint_diagnostic.py` — per-trade alpha analysis on real BA-v11 trades
- `layer3_t1_buypoint_navsim.py` — full NAV sim head-to-head
- `layer3_fetch_intraday_expand.py` — vnstock bulk-fetcher for BAL universe (one-time)
- `simulate_holistic_nav.py` — extended with `entry_alt_prices` + `entry_fill_mode` params
- `data/bal_universe_2024_25.csv` — 333-ticker BAL universe seed list
- `intraday_full.pkl` — now 335 tickers × ~10k bars each (Sep 2023 → May 2026)

## Setup

- Window: 2023-09-15 → 2026-05-12 (intraday data limit; 2.5y)
- Stack: v11 = v10 score + SV_TIGHT Fresh-Q + P3 overheat + 50/50 BAL+VN30 + V6 ETF
- 4 fill modes (T+1 day, exit logic unchanged):
  - **OPEN**: BQ.Open (canonical baseline; reflects ATO 09:00 match)
  - **T1115_MKT**: market order at 11:15 (close of 11:15 bar)
  - **T1115_LIM**: limit @ p_open (continuous-bar opening price); fills when
    intraday touches that level pre-11:15, else fallback to OPEN. p_lim = p_open
    (conservative — limit-buys fill at limit price, not below).
  - **VWAP**: full-session volume-weighted average

## Phase 1 — per-trade alpha diagnostic (n=79)

(Per-trade ROI alpha vs OPEN, after fees/slippage adjusted)

| Mode | ALL | TOP30 | OTHER | BAL | VN30 | 2024 | 2025 | 2026 BEAR | WIN | LOSS |
|---|---|---|---|---|---|---|---|---|---|---|
| **T1115_LIM** | +0.69pp | +0.77 | +0.64 | +0.72 | +0.61 | +0.31 | +0.78 | +0.77 | +0.69 | +0.66 |
| T1115_MKT | +0.48pp | +0.54 | +0.39 | +0.53 | +0.33 | +0.42 | +0.78 | +0.52 | +0.80 | +0.53 |
| VWAP | +0.15pp | +0.09 | +0.19 | +0.16 | +0.14 | -0.16 | +0.21 | +0.25 | +0.04 | +0.49 |
| ATC | +0.19pp | +0.21 | +0.18 | +0.09 | +0.49 | -0.03 | +0.09 | +0.53 | +0.02 | +0.76 |
| DAY_LOW oracle | +2.14pp | — | — | — | — | — | — | — | — | — |

T1115_LIM has the strongest per-trade alpha; all positive 10 / 10 slices. Note
this Phase 1 LIM used the lookahead `min(p_1115, p_open)` formula — Phase 2
uses the conservative `p_lim = p_open` (yet still delivers +1.24pp at NAV level).

## Phase 2 — full NAV sim (50B v11, 2.5y) — 4 modes head-to-head

| Variant | CAGR | Sharpe | MaxDD | Calmar | Wealth | vs OPEN |
|---|---|---|---|---|---|---|
| OPEN (baseline) | 19.01% | 1.17 | -16.1% | 1.18 | 1.59× | +0.00pp |
| T1115_MKT | 20.28% | 1.24 | -16.1% | 1.26 | 1.63× | +1.27pp |
| T1115_LIM (p_open fill) | 20.25% | 1.24 | -16.1% | 1.26 | 1.63× | +1.24pp |
| VWAP | 20.22% | 1.23 | -16.1% | 1.26 | 1.63× | +1.20pp |

All three alt modes give +1.2 to +1.3pp CAGR alpha; identical Sharpe (+0.07) and
MaxDD (unchanged at -16.1%). Calmar lifts uniformly from 1.18 to 1.26.

## Phase 3 — full intraday alpha curve (16 slots × 4 periods)

Tested every 15-min bar from 09:15 to 14:45. Script: `layer3_t1_buypoint_curve.py`.

### FULL 2.5y alpha (vs OPEN baseline 19.01% CAGR / 1.17 Sh):

```
Slot         Alpha    Sharpe   Calmar
09:15      +1.34pp     1.24     1.27
09:30      +1.21pp     1.24     1.26
09:45      +0.83pp     1.22     1.24   ← curve trough
10:00      +0.77pp     1.21     1.23   ← curve trough
10:15      +1.09pp     1.23     1.25
10:30      +1.17pp     1.23     1.26
10:45      +1.24pp     1.24     1.26
11:00      +1.33pp     1.24     1.27
11:15      +1.27pp     1.24     1.26
13:00      +1.34pp     1.24     1.27
13:15      +1.11pp     1.23     1.25
13:30      +1.29pp     1.24     1.26
14:00      +1.17pp     1.23     1.25
14:15      +1.79pp     1.26     1.29
14:30      -0.03pp     1.16     1.18   ← DATA GAP (only 4,467 sessions)
14:45 ATC  +1.81pp     1.26     1.29   ← OPTIMAL
```

Pattern: U-shape — high at open, dip 09:45-10:00, plateau through mid-day,
strong rise into close. Best slot = 14:45 ATC (+1.81pp).

### Sub-period robustness — DISPOSITIVE

```
Slot       2024     2025      2026 BEAR
09:15    +0.77    +3.89      -1.03  ❌ reverses sign in bear
09:30    +0.76    +3.65      -1.42  ❌
09:45    +0.79    +2.16      -1.00  ❌
10:00    +0.79    +2.26      -1.54  ❌
11:00    +0.69    +4.14      -1.35  ❌
11:15    +0.61    +3.92      -1.08  ❌
13:00    +0.73    +3.58      -0.28  ⚠ small negative
13:30    +0.57    +3.91      -0.78  ❌
14:00    +0.73    +3.68      -1.61  ❌
14:15    +0.78    +4.59      +0.61  ✅
14:45    +0.79    +4.58      +0.74  ✅ ROBUST + best alpha
```

**Only afternoon slots (14:15+) maintain positive alpha across all 3 sub-periods.**

In 2026 BEAR (4-month sub-window): morning slots LOSE -1.0 to -1.6pp.
Mechanism: in bear markets, panic-sell pressure pushes morning prices LOWER
than ATO match — so morning continuous-market fills are EXPENSIVE vs ATO,
not cheap. Afternoon settles after selling exhaustion → cheaper.

## Root cause — ATO auction spike

The almost-identical alpha across three otherwise distinct modes (09:15-ish
limit, 11:15 mkt, VWAP) reveals a single source: **BQ.Open is the ATO 09:00
auction match price, which is systematically worse than the continuous-market
price 15+ min later.**

Vietnamese HOSE ATO mechanics:
- Pre-open phase: orders accumulate (ATO type or limit)
- 09:00 match: single auction clearing price, often consuming aggressive market
  orders against thin liquidity → spike print
- 09:15 onwards: continuous matching settles the spike

Retail trades using "market on open" (placed pre-09:00) fill at the auction
spike → systematic disadvantage. Waiting 15 min or longer for continuous
matching to normalize captures ~1.2-1.3pp/yr of alpha for a 45-day-hold
strategy with the BA-v11 turnover profile.

## Decision

Per `t1_intraday_research_plan.md` decision rule, applied at the OPTIMAL slot:
- CAGR alpha ≥ +0.50pp: **+1.81pp full / +0.74pp BEAR** ✓ (14:45 ATC)
- Sharpe ≥ baseline: **+0.09** ✓ (14:45 ATC)
- MaxDD ≤ -2pp worse: **0pp** ✓ (identical -16.1%)
- Robust across sub-periods: **only 14:15 and 14:45 pass this gate** ✓

🟢 **ADOPT — T+1 14:45 ATC market order** as production entry.

Operationally: place "Match On Close" (MOC) or "Match At Close" market order
during 14:30-14:45 ATC period. All Vietnamese brokers support this order type.

If MOC unavailable: 14:15 fallback is nearly identical (+1.79pp full, +0.61pp BEAR).

## Deployment

### Live engine `recommend_holistic.py`

Update the "💡 Execution checklist for tomorrow (T+1 entry)" output text:
- OLD: "buy at T+1 ATO (09:00) market on open"
- NEW (v3): "T+1 14:45 ATC market BUY (Match On Close). Avoid morning fills —
  +1.81pp/yr alpha at ATC vs T+1 Open; works in bull AND bear regimes
  (morning slots LOSE 1.0-1.6pp in bear)."

Fallback if MOC order unavailable: 14:15 market order (+1.79pp / +0.61pp BEAR).

### Sim engine `simulate_holistic_nav.py`

Already extended (2026-05-17) with optional `entry_alt_prices` + `entry_fill_mode`
params. Default behavior remains BQ.Open (no change to existing backtests).
Production canonical sims can optionally use intraday alt prices going forward.

### Updated production baseline (v11, realistic T+1, 2.5y)

| Metric | OPEN (legacy) | ATC OPTIMISTIC | **ATC REALISTIC (gated)** | HYBRID |
|---|---|---|---|---|
| CAGR | 19.01% | 20.82% | **21.13%** | 20.77% |
| Sharpe | 1.17 | 1.26 | **1.28** | 1.26 |
| MaxDD | -16.1% | -16.1% | -16.1% | -16.1% |
| Calmar | 1.18 | 1.29 | **1.31** | 1.29 |

| Sub-period | OPEN | ATC OPT | **ATC REAL** | HYBRID |
|---|---|---|---|---|
| 2024 | 11.94 | +0.79 | +0.22 | +0.24 |
| 2025 | 45.62 | +4.58 | **+6.06** | +4.84 |
| **2026 BEAR** | 4.07 | +0.74 | **+1.26** | +1.25 |

Production baseline going forward (HYBRID recommended for operational simplicity):
**+1.75pp CAGR / +0.09 Sharpe** at zero operational cost.

### Phase 5 — sell-side curve (asymmetric finding)

Selling LATER loses alpha at every slot. Best sell time = OPEN (T+1 09:00 ATO).

```
Scenario A: BUY=OPEN, vary SELL slot vs OPEN/OPEN baseline 19.01%
  Sell @ 09:15  -0.80pp  ←  least bad late
  Sell @ 11:15  -1.65pp
  Sell @ 13:30  -1.80pp
  Sell @ 14:45  -1.74pp  (FULL); -7.61pp (2026 BEAR ← catastrophic)
```

Combined optimum:
```
BUY=ATC + SELL=OPEN (current canonical SELL):  +1.81pp full / +0.74pp BEAR
BUY=ATC + SELL=ATC                          :  +0.16pp full / -6.34pp BEAR
```

**Mechanism — opposite-sign drifts**:
- Morning: retail MOO buy interest → ATO premium → BUY late / SELL early
- Afternoon: sellers exhaust buyers (esp. bear) → afternoon drifts down → BUY (cheap) / DON'T SELL (no buyers)

Current `simulate_holistic_nav.py` already sells at T+1 Open via the
`pending_exits` mechanism — **no sell-side change needed**. Phase 5 confirmed
this default is already optimal.

## Caveats

1. **2.5y window** (intraday data starts 2023-09-11). Bull-biased; not tested
   in pre-2020 or 2008/2018 deep bear. The mechanism (ATO spike) should
   generalize — auction microstructure is regime-independent — but magnitude
   may differ.
2. **n=79 alpha events** in Phase 1. SE ≈ 0.20pp on per-trade alpha. The
   Phase 2 NAV result is more robust because it uses 114-115 trade portfolio
   path with full sizing/cash dynamics.
3. **Alpha is sensitive to ATO market order proportion**. If your broker
   uses LO (limit) at 09:00 instead of MOO, the ATO spike disadvantage may
   already be partially avoided → alpha lower for you.
4. **Real-world LIM execution risk**: gap-up days where intraday never
   touches your limit (placed at expected open or yesterday's close) → order
   stays un[REDACTED] all session, trade missed. Fallback strategy needed.
   T1115_MKT avoids this — [REDACTED] fills.

## Future work

- **Phase 3 (live shadow)**: Run paper-trade comparison BQ.Open vs T1115_MKT
  on next ~30 BA-system entries to confirm +~1pp alpha in real fills.
- **Pre-market depth**: If we can pull HOSE order-book data showing ATO
  imbalance, may be able to predict which days will spike worst → conditional
  delay.
- **More fill points**: test 10:00, 10:30, 13:30, 14:00, 14:30 to map the
  full intraday alpha curve; choose minimum-variance time slot.
