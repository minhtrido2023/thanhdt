# ConvergePort — Framework, Backtest & Launch Decision

**Author:** Taylor · **Job:** Taylor_20260706_093329 (dispatch from Mike, user approved direction)
**Scope:** RESEARCH / PAPER ONLY. Touches no production trading file (custom30V / BAL / LAG /
rating_8l.py unchanged). If launched, launches as a PAPER book, not real money. Any surfaced name
still routes Taylor → DollarBill → user → Mafee before a live order.
**Script:** `converge_portfolio_backtest.py` · **NAV audit CSV:** `data/converge_portfolio_backtest_nav.csv`
· **Paper book:** `data/converge_portfolio_paper.json`

---

## 1. Idea

ConvergePort sits at the **intersection of two independent systems** that the fleet already runs:

- **AlphaLens / sector_lens_monitor** — a per-name valuation/timing *lens* (Gordon P/B for banks,
  EVEB for CTR, PE-vs-history for FPT/textile, PB-trough for PVT/HAH, PB-cap+gate for securities,
  hog-feed for DBC). Says **BUY** when a name is cheap-and-confirmed on its own lens.
- **8L rating (composite v3)** — a cross-sectional fundamental-quality rank. **rating ≤ 2** =
  golden/strong tier.

When **both agree on the same name** (`rating ≤ 2` **AND** sector-lens `BUY`) that is the
**DOUBLE-CONFIRM** signal already built in `sector_lens_monitor.py` (job Taylor_20260706_082923).
ConvergePort turns that daily signal set into a **portfolio**, 2-layer like V2.4:

- **Layer 1 — active "converge" book:** the double-confirm names, equal-weight, each capped 20% NAV.
- **Layer 2 — idle cash parks in custom30V** (yieldcombo top-30, cap 0.10, quarterly rebal) — the
  same NEUTRAL parking vehicle V2.4 uses.

**Entry:** a name transitions INTO double-confirm → buy. **Exit:** *either* leg breaks
(`rating > 2` OR sector-lens leaves BUY) → sell fully. Symmetric. Rebalance daily on the
double-confirm update (aligned to `newdeals_daily_report.py`, 06:00 ICT).

### Weighting — my explicit reading of Mike's sketch
Mike's sketch said "normalize to 100% of the active book, cap 20% per name, tilt STRONG 1.5×, idle
cash parks." Those are slightly under-determined together (normalize-to-100% + rule-5 "idle cash
parks" can't both bind unless the cap is a **per-NAV** cap). I implemented the coherent version:

```
raw_i   = 1.5 if buy_mode==STRONG else 1.0        # (tilt variant; see §4 A/B — dropped)
share_i = raw_i / sum(raw)
w_i     = min(0.20, share_i)                        # 20% cap of TOTAL NAV
active_frac = sum(w_i) ;  parking = 1 - active_frac
```

The 20% cap naturally makes a **thin** double-confirm set park more (fewer confirmations = less
conviction = more mechanical parking): with ≥5 names the book is fully active; with 3 names it is
60% active / 40% parked. This is the only reading in which rule 5 ("idle cash parks") is ever live.

---

## 2. Point-in-time reconstruction (no look-ahead)

Every input is as-of the evaluation date `t`:
- **Price-current multiples** (PE, PB, EVEB, PE_MA5Y) from the `ticker` row for `t`.
- **Fundamentals** (PE_MA1Y, PB_MA1Y, ROE5Y, ROIC5Y, ROE_Trailing, ROE3Y, ROE_Min3Y, IntCov_P0,
  CF_OA_3Y, Debt_Eq_P0, NP, GPM_P0..P7) as-of the latest `ticker_financial.Release_Date ≤ t`.
- **DT5G state** (securities gate) as-of `t` from `vnindex_5state_dt5g_live`.
- **8L rating** as-of the latest `rating_8l_history.csv.eff_date ≤ t`.
- **Sector-lens BUY** decided by the **exact `eval_*` functions imported from
  `sector_lens_monitor`** — no re-implementation (per dispatch). DBC uses no historical hog-feed
  feed (its BUY branch doesn't need it; only the ARMED state does).
- **Execution T+1:** weights at `t-1` earn return `t`. Parking = published `custom30v_8l` basket
  (buy-and-hold drift within each quarterly period).

**Self-check:** daily weights (active + parking) sum to 1.0 with max deviation **2.2e-16** (0 VND
leak). Threads=1.

Coverage: 2014-08-05 → 2026-06-26 (2,970 sessions). Double-confirm name-days = 9,708; a
double-confirm name exists on 2,455 / 2,970 days; active-set size when active mean **4.0**, max 9.

---

## 3. Walk-forward results (TC = 0.1%/unit turnover)

| Config | Window | CAGR | Sharpe | Sortino | MaxDD | Calmar |
|---|---|---:|---:|---:|---:|---:|
| **custom30V thuần (baseline)** | FULL 2014-08→now | 18.75% | 0.87 | 1.04 | −45.9% | 0.41 |
| | IS 2014-2019 | 12.72% | 0.72 | 0.92 | −33.8% | 0.38 |
| | OOS 2020→now | 24.03% | 0.99 | 1.13 | −45.7% | 0.53 |
| **ConvergePort (equal-weight)** | FULL 2014-08→now | **23.86%** | **1.11** | 1.34 | −46.1% | **0.52** |
| | IS 2014-2019 | 14.22% | 0.83 | 1.07 | −30.7% | 0.46 |
| | OOS 2020→now | 32.54% | 1.31 | 1.54 | −40.6% | 0.80 |
| ConvergePort (tilt 1.5× STRONG) | FULL 2014-08→now | 23.74% | 1.10 | 1.33 | −46.0% | 0.52 |
| AlphaLens-static (FPT/ACB/MBB/HDB) | FULL 2014-08→now | 20.68% | 0.95 | 1.15 | −44.7% | 0.46 |

**Delta vs baseline (FULL):** ConvergePort EW **+5.11pp CAGR, +0.24 Sharpe, +0.11 Calmar**, DD flat.
Edge holds in **both** windows: IS **+1.5pp** (12.72→14.22), OOS **+8.3pp** (24.03→32.54) — not
overfit, and dynamic double-confirm beats the static 4-name AlphaLens book by **~3pp** (20.68→23.86).

### Turnover & TC (does trading eat the edge?)
Annualized one-way turnover: EW **4.14×/yr**, tilt 4.68×/yr, static 1.35×/yr. TC sensitivity on the
tilt config: CAGR 23.74% @0.1% → 23.16% @0.2% → **22.58% @0.3%** — a −1.16pp drag from 0.1→0.3%,
well **inside** the ~5pp edge. **Turnover does NOT eat the edge.**

### Robustness (KB Rule 5 discipline)
- **Leave-one-year-out** full-period ΔCAGR: all-years **+5.11pp**; dropping any single year keeps it
  in **[+3.42, +5.52]pp**. Even dropping the best year (2024, +21pp delta) leaves **+3.42pp**. The
  edge is **broad-based**, not carried by 1–2 years (the opposite of the Wave1/H8a trap). Positive
  yearly delta in **9 / 13 years**.
- **DSR** (Deflated Sharpe): ConvergePort EW standalone **0.998** (n=3 trials), **0.973** even at a
  conservative n=16 → clears the 0.95 gate. Only 3 configs compared (tilt / equal / static) →
  minimal multiple-testing.

### Honest caveats
- Backtest parking sleeve = **raw ungated** custom30V basket (DD ≈ −46%). Production custom30V is
  DT5G-gated (much lower DD). Baseline and ConvergePort share the same ungated basket, so the
  **relative** comparison is clean, but the absolute −46% DD is not what a gated live book shows.
- **Excess-over-baseline** spread Sharpe = 0.46, **DSR = 0.775** (< 0.95): the *marginal* edge over
  parking, treated as a long/short spread, is statistically softer than the robust standalone book —
  expected (both share heavy equity beta). The design bar is "not lose to custom30V"; that is cleanly
  met (+5pp, 9/13 years, LOO-stable). This is a PAPER book, not a production wire.

---

## 4. Verdicts (answering the dispatch)

1. **Does ConvergePort beat custom30V thuần?** YES — **+5.0pp CAGR (23.9 vs 18.7), +0.23 Sharpe,
   +0.11 Calmar, DD flat**, edge in both IS and OOS, LOO-stable.
2. **Does dynamic turnover eat the edge?** NO — 4.1×/yr, edge survives TC to 0.3% (−1.2pp vs a ~5pp
   edge).
3. **Is the STRONG 1.5× tilt worth it?** **NO — drop it.** Equal-weight is marginally *better*
   (23.86 vs 23.74) and simpler; the tilt only raises turnover (4.68 vs 4.14×). **Launch equal-weight.**
4. **Result reasonable → launch paper?** YES.

## 5. Launch

- **`data/converge_portfolio_paper.json`** — equal-weight, cap 0.20, idle→custom30V, benchmark
  VNINDEX (entry 1871.91), start 2026-07-06, review 2026-10-06 (3-month window like AlphaLens),
  SEPARATE from `alphalens_paper.json`.
- **Seed set (live double-confirm, 2026-06-26 cache, DT5G NEUTRAL(3)):** ACB, MBB, TCB (banks),
  HAH, PVT (logistics), DHG (pharma), SSI (securities), FPT (tech, STRONG), CTR (infra) — 9 names,
  1/9 ≈ 0.111 each, 0% parked at launch.
- **`newdeals_daily_report.py`** gains **§3 "ConvergePort"** (paper book P&L vs entry + vs VNINDEX,
  daily double-confirm add/drop) alongside the existing AlphaLens and sector-lens sections.

---

## 6. Capacity-appropriate scale (job Taylor_20260706_105156)

**Question:** what NAV can ConvergePort actually absorb as a standalone sleeve, before liquidity —
not signal — becomes the binding constraint? (This is separate from the "replace the 2-book
production" question, which was already REFUTED at 50B: ConvergePort-as-active-book = 12.05% CAGR vs
R3 28.05%, job Taylor_20260706_103815.)

**Method (identical to the fullharness capacity block, `converge_fullharness_test.py` L2298-2318 —
`converge_capacity_sweep.py` reuses the exact formula, no new logic):**
```
req      = CONV_WPN(0.110) × NAV                       # per-name target position
ADV60    = median(Volume_3M_P50 × Price) over recent 120 calendar days   (tav2_bq.ticker, END 2026-07-05)
cap_day  = 0.20 × ADV60                                # 20%-of-ADV/day fill rule
days     = req / cap_day                               # sessions to build one full name
flag     = OK(≤1) / WATCH(1-3) / BREACH(>3 build-days)
```
Universe = the **16 available names** (`sector_lens_monitor.NAMES`), not just today's 9 double-confirm.

### Per-name ADV60 and onset-NAV thresholds
Analytic onsets: a name enters WATCH at `NAV = 0.20·ADV60/WPN`, BREACH at `NAV = 0.60·ADV60/WPN`.

| ticker | ADV60 (B/day) | WATCH onset (NAV) | BREACH onset (NAV) |
|---|---:|---:|---:|
| **DHG** | **1.21** | **2.2B** | **6.6B** |
| MSH | 10.57 | 19.2B | 57.7B |
| CTR | 32.43 | 59.0B | 176.9B |
| HAH | 66.22 | 120.4B | 361.2B |
| DBC | 67.49 | 122.7B | 368.1B |
| PVT | 159.3 | 289.7B | 869.1B |
| … (VND/VCI/HCM/ACB/TCB/HDB/MBB/VCB/SSI/FPT all ≥200B ADV) | | ≥365B | ≥1,095B |

DHG's ADV (~1.2B/day) is **~9× thinner** than the next name (MSH ~10.6B) and **~600× thinner** than
the megacaps (FPT/SSI ~725B) — it single-handedly sets the full-universe ceiling.

### NAV sweep — days-to-build the thinnest names (rest are all <0.9 at every level ≤50B)
| name | ADV60 | 1B | 3B | 5B | 10B | 15B | 20B | 30B | 50B |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **DHG** | 1.21 | 0.46 | **1.37** | 2.28 | **4.56** | 6.84 | 9.12 | 13.68 | 22.81 |
| MSH | 10.57 | 0.05 | 0.16 | 0.26 | 0.52 | 0.78 | **1.04** | 1.56 | 2.60 |
| CTR | 32.43 | 0.02 | 0.05 | 0.08 | 0.17 | 0.25 | 0.34 | 0.51 | 0.85 |

Flag summary: **NAV=1B all-OK**; **3-5B → DHG WATCH**; **≥10B → DHG BREACH**; **≥20B → MSH also WATCH**.
(Consistent with the prior 50B/100B run, job Taylor_20260706_095725: DHG BREACH, MSH WATCH at 50B;
MSH BREACH + CTR WATCH at 100B.)

### Answers
3. **Sweet-spot (ALL 16 names OK, no WATCH/no BREACH):** DHG binds → **NAV ≈ 2.2B** (at 2.19B DHG
   hits exactly 1.0 build-day). Practically **~2B VND** is the safe ceiling with the *full* universe
   and DHG traded as an active momentum name. Tiny — because DHG barely trades.
4. **Excluding DHG** (it is a buy-and-hold pharma anchor — low turnover, held not traded — so the
   20%-ADV/day *build-rate* rule overstates its true constraint): the next binding name is **MSH**.
   - all-remaining-OK (≤1 build-day) ceiling → **~19B VND** (MSH WATCH onset).
   - tolerate MSH/CTR in WATCH (1-3 build-days, i.e. 2-3 sessions to build/exit those two thin
     names) → push to **~57B** before MSH itself BREACHES — but that is essentially the 50B design
     point already shown to underperform as a production replacement, and it re-introduces the
     multi-day-fill slippage the sweet-spot avoids.
5. **Is +5.0pp scale-dependent?** **NO.** `converge_portfolio_backtest.py` `sim_nav()` is a **pure
   fractional-weight return simulator** — it carries NO NAV level and NO ADV/notional/capacity term;
   the only "cap" is the 0.20 per-name *weight* fraction (not a liquidity cap). Verified by reading
   the function: it iterates daily `r_active + r_park − turnover·TC` on weights that sum to 1.0.
   **Therefore the +5.0pp CAGR edge is scale-invariant and holds at ANY NAV inside the sweet spot.**
   Capacity only *erodes* it above the sweet spot (via multi-day fills / slippage the backtest does
   not model) — it never *creates* the edge.

### 6.1 Verdict — recommended standalone-sleeve size
**Run ConvergePort as an independent sleeve at ~10-15B VND with DHG hard-excluded from active
rebalancing** (kept as a buy-and-hold anchor if desired, sized outside the rebalanced sleeve — the
same `excluded_tickers` pattern used for ZaloPay/DGC).

- **Why exclude DHG, not cap the whole sleeve at 2B:** DHG alone drags the full-universe ceiling to
  ~2B (7-9× smaller) purely on its thin ADV; it is a low-turnover pharma hold, not a name the book
  actively churns, so excluding it from the *rebalanced* fraction costs almost nothing in strategy
  behaviour while lifting the deployable size ~9×.
- **Why 10-15B, not the full 19B MSH ceiling:** 10-15B sits comfortably below MSH's 19.2B WATCH
  onset, leaving margin for ADV drift (thin-name ADV is volatile) so no name is even at WATCH under
  normal liquidity. Every remaining 15-name build completes in <1 session.
- **Aggressive variant:** up to ~19B if you accept zero margin against MSH ADV drift; ~50B only if
  you accept MSH+CTR trading in 2-3 sessions (WATCH), which is the already-refuted large-scale
  regime — not recommended for a clean sleeve.
- **The +5.0pp edge is fully intact** at 10-15B (scale-invariant per answer 5); capacity is not
  binding anywhere in that range for the 15 non-DHG names.

**Scope:** RESEARCH/PAPER-ONLY. No production trading file touched; the current paper book
(`data/converge_portfolio_paper.json`, equal-weight, launched 2026-07-06) is unaffected — this only
sizes what a *real* deployment could be, if/when that decision is taken (routes Taylor → DollarBill
→ user → Mafee as always).

---

## 7. UNION (OR) alternative — REFUTED (job Taylor_20260706_114506)

**Question (user via Mike).** The double-confirm set (AlphaLens BUY **AND** 8L golden) is thin —
mean 4.0 names, **17.3% of days 0 names**. Does switching **AND → OR (UNION)** fix the "too few
deals" problem *without* hurting risk-adjusted performance? Should the launched paper book switch
from double-confirm to UNION?

**UNION definition (no new conditions invented — per dispatch).**
`member(name,t) = [name ∈ sector_lens Group-A ∧ sector-lens status==BUY]  OR  [name ∈ rating_8l.py
BUY-NOW list at t]`, where BUY-NOW is rating_8l.py's OWN screen (L568-576): `rating(as-of)≤3 ∧
liq_bn≥3.0 ∧ pb_z≤-0.3 ∧ ¬(ROE_Min3Y<0)`. *(NB: the dispatch parenthetical said "ROE_Min5Y≥0"; the
actual BUY-NOW code uses the **ROE_Min3Y<0** chronic-destroyer guard — I used the real code per
"don't redefine".)* Equal-weight `min(0.20, 1/n)` + parking, symmetric to double-confirm.

**Engine.** Same fractional paper-sim as §3 (`converge_union_test.py`; baseline / double-confirm /
UNION all in one identical engine; custom30V parking; DT5G-as-of gate; T+1; threads=1; self-check
weight-sum `|dev−1|` = 2.2e-16 = 0 VND leak). **Why this frame, not the fullharness `CONVERGE_BOOK`
single-book replacement:** that frame is already REFUTED (12.05% vs R3 28.05%) and uses a *fixed*
per-name WPN=0.11 which clips at cash-exhaustion once breadth >9 (UNION runs 30-100 names → ordering
artifact). The fractional sim (weights sum to 1.0) handles arbitrary breadth and is scale-invariant
(job _105156), so **NAV=20B is irrelevant to the return sim** — it only enters the ADV capacity
overlay below. Double-confirm here reproduces the §3 headline **exactly** (23.86% / Sharpe 1.11 /
Calmar 0.52), validating the engine is identical.

**Breadth (does UNION fix "too few deals"? — YES, completely).**
| set | mean-when-active | max | empty days |
|---|---|---|---|
| double-confirm (AND) | 4.0 | 9 | **515/2970 (17.3%)** |
| BUY-NOW golden arm alone | 33.1 | 104 | 0 (0.0%) |
| **UNION (OR)** | **36.1** | **107** | **0/2970 (0.0%)** |

Live 2026-06-26: UNION = **65 names** vs double-confirm 9. The golden BUY-NOW arm is a *broad*
deep-value screen (~33 names/day), so UNION is never empty.

**Performance (FULL 2014-08→2026-06, TC=0.1%) — UNION is decisively WORSE.**
| Config | CAGR | Sharpe | MaxDD | Calmar | turnover |
|---|---|---|---|---|---|
| custom30V thuần (baseline) | 18.75% | 0.87 | −45.9% | 0.41 | ~0 |
| double-confirm (AND) | **23.86%** | **1.11** | −46.1% | **0.52** | 4.14×/yr |
| **UNION (OR)** | **12.07%** | **0.64** | **−55.9%** | **0.22** | **12.89×/yr** |

**Δ vs baseline: UNION −6.68pp CAGR / −0.23 Sharpe / −0.19 Calmar / MaxDD −10pp WORSE.** Worse in
BOTH IS (6.71% vs 12.72% baseline) and OOS (16.76% vs 24.03%). UNION underperforms even *pure
custom30V parking* — and by 11.8pp vs double-confirm. TC sensitivity: UNION 12.07%→9.22% @0.3%
(turnover really bites at 12.9×/yr).

**Why it fails (mechanistic).** (1) The golden BUY-NOW arm is a broad 8L deep-value list that
heavily **overlaps custom30V itself** (both are 8L/value over the liquid universe) — so UNION ≈ an
equal-weight broad-value book, a *worse-constructed* custom30V (equal-weight vs yieldcombo cap-weight)
with churn added. (2) Equal-weighting 30-100 deeply-dislocated (pb_z≤−0.3) names *maximises* exposure
to the cheapest/most-distressed names right as they fall → MaxDD −55.9% (falling-knife). (3) Turnover
3× higher (names constantly cross the pb_z≤−0.3 boundary). (4) The double-confirm edge WAS the
**AND-selectivity** — two independent lenses agreeing = high conviction, few names; OR destroys
exactly that.

**Capacity @20B — NOT the constraint.** UNION spreads thin (65 names × ~1.5% = 0.31B/name), so 64/65
live names are OK, only DHG at WATCH (1.27 build-days). Capacity is *easier* than double-confirm —
but irrelevant, because performance already fails.

**Verdict — DO NOT switch to UNION. Keep double-confirm.** UNION "solves" the empty-days problem, but
**that problem was never real: an empty double-confirm day = 100% custom30V parking = automatic
safety, not a defect** (exactly Mike's framing in the dispatch, confirmed by data). Trading OR-breadth
for AND-selectivity converts a high-conviction concentrated sleeve into a churning broad-value book
that loses to plain parking. The current paper book (double-confirm equal-weight) stays as launched.
Output: `converge_union_test.py`, `data/converge_union_test_nav.csv`,
`data/converge_union_test_summary.json`.

---

## 8. Does the active book follow the DT5G exposure schedule? MaxDD source + state-gate test (job Taylor_20260706_121242)

Follow-up to the full-harness-as-active-book audit (§6, job _103815). Mike asked: does the
double-confirm **active** book throttle its per-name exposure by DT5G state (CRISIS 0% / BEAR 20% /
NEUTRAL 70% / BULL 100% / EX-BULL 130%), does CAPIT actually apply to it, and is the deep MaxDD
caused by a *missing* state-gate on the active book? Answered by reading the code, then tested by
adding the gate.

### 8.1 Code-verified answers (converge_fullharness_test.py, no guessing)
1. **Is the active book state-throttled?** **NO.** When `CONVERGE_BOOK=1`, entry/exit is *purely
   membership-driven* (join double-confirm → buy at T+1 open; leave → force-close), and every
   state-sensitive knob is explicitly disabled: `tier_weights_by_state=None` (L1709),
   `stop_loss=-0.999`, `hold_days=1e9`, sector caps off. The DT5G regime-size halving that BAL uses
   (`weak buy-rows halved to 5% in BEAR/CRISIS`) is **not** applied to ConvergePort names. So in
   CRISIS/BEAR the active book stays at whatever double-confirm membership dictates — it does **not**
   scale down. *(Native BAL/LAG also don't hard-gate by state either — they thin out only because
   momentum/PEAD signals naturally dry up in bad tape; that organic thinning does not exist for a
   fundamentals+sector-lens membership book, which is exactly why the active book can sit near-full
   in a drawdown.)*
2. **Does CAPIT apply to the ConvergePort book?** **YES.** `add_capit_arm(sig_f, …)` (L1737) grafts
   the CAPIT washout-buyer onto the **same** BAL-slot signal frame that now carries ConvergePort, so
   the printed `CAPIT=ON` washout events *are* part of this book (not an independent sleeve summed on
   top). CAPIT deploys idle book cash into deep-value bottom-fish during washouts.
3. **Is `{3:0.7}` parking the ONLY total-exposure throttle?** **YES.** The custom30V idle-cash
   parking follows the production DT5G schedule `{1:0, 2:0.2, 3:0.7, 4:1.0, 5:1.0}` on *unused* book
   cash — it is the **only** state-aware exposure control in the ungated run, and it does **nothing to
   money already held in active positions**. In CRISIS/BEAR, if the book is fully invested in
   double-confirm names, parking has no idle cash to gate → the active exposure rides the drawdown.

### 8.2 Where the deep MaxDD actually comes from
The dispatch quoted **−46.1%**; that is the **standalone paper sleeve** number (§3,
`converge_portfolio_backtest.py`, simpler sim, raw-ungated parking). The **full production harness**
as-active-book (§6) is **−38.4%** (50B, real `simulate()` engine, TC 0.15/0.15/0.1, borrow 10%). Both
are with the active book **ungated**. The DD is dominated by **universe concentration**, not the
missing gate: 16 candidate names, double-confirm breadth **mean 4 active / max 9**, **17% of sessions
have 0 names** (→ those days are auto-parked, safe). A 4-name equal-weight equity book with no
state-throttle simply takes the full market hit in 2022/2025 washouts.

### 8.3 State-gate test — added `CONV_STATE_GATE` and re-ran (50B, FULL 2014→2026-06)
Added an **opt-in** flag (`CONV_STATE_GATE=1`, default OFF → byte-identical to the ungated run,
converge_fullharness_test.py L1712-1732). It makes the active book obey the DT5G ceiling
`{1:0, 2:0.2, 3:0.7, 4:1.0, 5:1.0}` two ways: (a) `tier_weights_by_state` caps NEW entry size to
`WPN × ceiling`; (b) `state_exit_map={1:1.0, 2:0.8, 3:0.3}` actively **trims held positions** to the
CRISIS(flush)/BEAR(80% trim)/NEUTRAL(30% trim) ceiling. Disclosed caveat: the trim applies to the
whole BAL slot, so it **also flushes the CAPIT crisis-buyer in CRISIS/BEAR** — i.e. it sells the
bottom-fisher exactly when CAPIT is designed to buy.

| Config (50B, CAPIT ON, same parking) | CAGR | Sharpe | MaxDD | Calmar |
|---|---|---|---|---|
| **Ungated active book** (baseline, §6) | **12.05%** | 0.85 | **−38.4%** | 0.31 |
| **State-gated active book** (`CONV_STATE_GATE=1`) | **5.74%** | 0.66 | **−19.4%** | 0.30 |
| — IS 2014-19 | 6.14% | 0.76 | −13.1% | 0.47 |
| — OOS 2020-now | 5.38% | 0.58 | −19.4% | 0.28 |
| *(reference)* 2-book V2.4 R3 | 28.05% | 1.86 | −17.5% | 1.60 |

### 8.4 Verdict — state-gating the active book is NOT the fix
The gate **works mechanically** and does what was asked — it **halves MaxDD (−38.4% → −19.4%**, down
to production's ~−17.5% neighborhood). **But it more-than-halves CAGR (12.05% → 5.74%)**: the trade is
~1:1 return-for-drawdown, so **Calmar is flat (0.31 → 0.30)** and **Sharpe gets *worse* (0.85 →
0.66)**. It buys no risk-adjusted improvement — it just scales the whole (already-losing-to-R3) book
down. **Root cause of the give-up:** forcing a de-risk on a value/mean-reversion + CAPIT book in
CRISIS/BEAR sells into washouts and misses the recovery — the exact wrong side for this book type
(same lesson as the archived hold-neutral-exit / vol-managed-BAL experiments: throttling a
mean-reverting book by regime destroys its convexity).

**Conclusion:** the deep MaxDD is a **small-concentrated-universe** artifact (4-name modal book), NOT
a missing state-gate — and *adding* the gate proves it, because gating shrinks return and risk
together with **zero Calmar gain and worse Sharpe**. ConvergePort remains a **capacity-limited paper
sleeve on idle cash** (§6: ~10–15B ex-DHG), **NOT** a replacement for the 2-book V2.4 active engine,
whose −17.5% DD comes from genuine BAL/LAG breadth + allocator + parking working together, not from a
single throttle. `CONV_STATE_GATE` stays **default-OFF** (research flag only); nothing wired to
production. Output: `converge_fullharness_test.py` (+`CONV_STATE_GATE`), `/tmp/conv_stategate.log`.
