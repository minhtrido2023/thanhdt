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
