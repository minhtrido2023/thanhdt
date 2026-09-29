# -*- coding: utf-8 -*-
"""exp_dc3book_c1_stateswap_20260825.py — R&D: backtest C1 (state-conditional
BULL-only LAG->DC swap) for real, with turnover cost + IS/OOS split.

Job Taylor_20260825_153800 (dispatch from Mike), Giai doan 3 Phan 1. RESEARCH
ONLY. Does NOT modify production code/CSV. Reuses loaders from
exp_dc3book_20260825.py (phase-2 script, same folder) by import.

METHOD
------
Two dollar buckets: V_bal, V_slot. V_bal always earns r_BAL(t) (production
book-level NAV tracker, nav_bal_ref pct-change). V_slot earns r_LAG(t) when
state != BULL, r_DC(t) when state == BULL (DC built fresh via ConvergePort's
own loaders, state-gated parking @0.80 NEUTRAL only -- same convention as
phase-2 Part A/C1 estimate).

Target weight w_lag_tgt(t) is read from the REAL production allocator column
(golive-audit CSV) -- NOT hardcoded. State != BULL -> unchanged from V2.4
(w_slot_tgt = w_lag_tgt(t), slot content = LAG). State == BULL -> w_slot_tgt
still = w_lag_tgt(t) (same target weight the real allocator used that day),
but slot CONTENT swaps to DC. This isolates the effect of "swap what fills
the LAG-target's dollar bucket in BULL", exactly the C1 question -- it does
NOT also re-tune the weight itself (that would confound with the ma-tran
factor-rotation idea, C3, which is explicitly out of scope this round).

Turnover cost: every time the target regime for V_slot flips (LAG<->DC,
driven purely by state crossing into/out of BULL), charge TC=0.1% per side
(0.2% round-trip) on V_slot's FULL dollar value the day of the flip. This is
a conservative (worst-case) assumption -- full liquidation + full rebuild,
no partial overlap credit between LAG's PEAD longs and DC's double-confirm
bank/securities names (they are genuinely different tickers, so full
turnover is the realistic assumption, not merely conservative padding).

Band rebalance: same +-10pp band convention as phase-2 Part A, applied to
(V_bal, V_slot) around (1-w_lag_tgt(t), w_lag_tgt(t)) -- keeps the two-bucket
mechanic comparable to Part A's three-bucket one. This remains a
simplification of the real allocator's 3-session ramp (documented, not
hidden -- see phase-2 SUMMARY.md caveats, same caveat applies here).

Self-check: 0 VND leak (bucket weights sum to 1.0 every day by construction,
verified numerically each day).
"""
import os
import sys

import numpy as np
import pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
OUTDIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, OUTDIR)

import exp_dc3book_20260825 as base  # noqa: E402  (reuse phase-2 loaders)

GOLIVE_CSV = base.GOLIVE_CSV
TC = base.TC              # 0.1% per side, CLAUDE.md standard
BAND = base.BAND           # +-10pp
IS_END = base.IS_END
OOS_START = base.OOS_START
BULL_STATE = 4              # state coding: 1 CRISIS,2 BEAR,3 NEUTRAL,4 BULL,5 EXBULL


def load_bal_lag_wtgt():
    """r_BAL(t), r_LAG(t), state(t), w_lag_tgt(t) from the production CSV."""
    usecols = ["record_type", "ymd", "state", "nav_bal_ref", "nav_lag_ref", "w_lag_tgt"]
    df = pd.read_csv(GOLIVE_CSV, usecols=usecols)
    df = df[df["record_type"] == "DAILY"].copy()
    df["ymd"] = pd.to_datetime(df["ymd"])
    df = df.sort_values("ymd").reset_index(drop=True)
    df["r_bal"] = df["nav_bal_ref"].pct_change()
    df["r_lag"] = df["nav_lag_ref"].pct_change()
    return df[["ymd", "state", "r_bal", "r_lag", "w_lag_tgt"]]


def sim_c1_stateswap(dates, r_bal, r_lag, r_dc, state, w_lag_tgt):
    """Two-bucket sim: V_bal always r_bal; V_slot = r_lag outside BULL,
    r_dc inside BULL, with turnover cost on regime flip + band rebalance
    against w_lag_tgt(t). Returns daily portfolio return series + counters
    + self-check leak."""
    n = len(dates)
    w0 = w_lag_tgt[1] if np.isfinite(w_lag_tgt[1]) else w_lag_tgt[np.isfinite(w_lag_tgt)][0]
    V_bal = 1.0 - w0
    V_slot = w0
    regime = "DC" if (np.isfinite(state[1]) and int(state[1]) == BULL_STATE) else "LAG"
    port_ret = np.zeros(n)
    n_flip = 0
    n_rebal = 0
    turnover_cost_total = 0.0
    rebal_cost_total = 0.0
    max_leak = 0.0
    flip_dates = []
    for i in range(1, n):
        rb = r_bal[i] if np.isfinite(r_bal[i]) else 0.0
        rl = r_lag[i] if np.isfinite(r_lag[i]) else 0.0
        rd = r_dc[i] if np.isfinite(r_dc[i]) else 0.0
        st = state[i]
        wt = w_lag_tgt[i] if np.isfinite(w_lag_tgt[i]) else w_lag_tgt[i - 1]

        prev_total = V_bal + V_slot
        target_regime = "DC" if (np.isfinite(st) and int(st) == BULL_STATE) else "LAG"
        flip_cost = 0.0
        if target_regime != regime:
            flip_cost = V_slot * TC * 2.0  # round-trip: sell old book, buy new book
            turnover_cost_total += flip_cost
            regime = target_regime
            n_flip += 1
            flip_dates.append(dates[i])

        r_slot = rd if regime == "DC" else rl
        V_bal = V_bal * (1.0 + rb)
        V_slot = (V_slot - flip_cost) * (1.0 + r_slot)
        total = V_bal + V_slot
        port_ret[i] = total / prev_total - 1.0

        w_slot = V_slot / total if total > 0 else 0.0
        w_slot_tgt = wt if np.isfinite(wt) else w_slot
        rebal_cost = 0.0
        if abs(w_slot - w_slot_tgt) > BAND:
            moved = abs(V_slot - total * w_slot_tgt)
            rebal_cost = moved * TC  # one-way $ moved, TC charged once (matches Part A convention)
            rebal_cost_total += rebal_cost
            total_after = total - rebal_cost
            V_bal = (1.0 - w_slot_tgt) * total_after
            V_slot = w_slot_tgt * total_after
            port_ret[i] -= rebal_cost / prev_total
            n_rebal += 1

        leak = abs((V_bal + V_slot) / (total - rebal_cost) - 1.0) if (total - rebal_cost) > 0 else 0.0
        max_leak = max(max_leak, leak)

    return (pd.Series(port_ret, index=dates), n_flip, n_rebal,
            turnover_cost_total, rebal_cost_total, max_leak, flip_dates)


def main():
    print("Loading BAL/LAG production daily returns + real w_lag_tgt(t) ...")
    bl = load_bal_lag_wtgt()
    bl = bl[bl["ymd"] >= pd.Timestamp("2014-08-05")].reset_index(drop=True)
    calendar = pd.DatetimeIndex(bl["ymd"])
    print(f"Calendar: {calendar[0].date()} -> {calendar[-1].date()} ({len(calendar)} sessions)")

    print("Building DC book returns (reusing converge_portfolio_backtest loaders, "
          "same convention as phase-2 Part A: state-gated park @0.80 NEUTRAL only) ...")
    r_dc_full, active_frac, n_active_days = base.build_dc_returns(calendar)

    r_bal = bl["r_bal"].values
    r_lag = bl["r_lag"].values
    r_dc = r_dc_full.reindex(calendar).values
    state = bl["state"].values
    w_lag_tgt = bl["w_lag_tgt"].values

    n_bull_days = int((state == BULL_STATE).sum())
    print(f"BULL-state days in window: {n_bull_days}/{len(calendar)} ({n_bull_days/len(calendar)*100:.1f}%)")

    print("Simulating C1 (state-conditional BULL-only LAG->DC swap, real w_lag_tgt(t), "
          "turnover cost on regime flip, +-10pp band) ...")
    (port_c1, n_flip, n_rebal, turnover_cost_total, rebal_cost_total,
     max_leak, flip_dates) = sim_c1_stateswap(calendar, r_bal, r_lag, r_dc, state, w_lag_tgt)

    # ---- baseline: real production combined_nav return, SAME window ----
    usecols = ["record_type", "ymd", "combined_nav"]
    prod = pd.read_csv(GOLIVE_CSV, usecols=usecols)
    prod = prod[prod["record_type"] == "DAILY"].copy()
    prod["ymd"] = pd.to_datetime(prod["ymd"])
    prod = prod.sort_values("ymd").set_index("ymd")
    prod_ret_full = prod["combined_nav"].pct_change()
    baseline_2book = prod_ret_full.reindex(calendar)

    # ---- also load phase-2 static 3-book (1/3-1/3-1/3) for reference ----
    static_csv = os.path.join(OUTDIR, "exp_dc3book_nav_3book_dc33.csv")
    static3 = pd.read_csv(static_csv, parse_dates=["date"]).set_index("date")
    static3_ret = static3["port_3book_dc33"].reindex(calendar)

    print("\n" + "=" * 96)
    print("RESULTS — C1 (state-conditional BULL-only LAG->DC swap) vs V2.4 baseline vs static 3-book")
    print("=" * 96)
    rows = []
    rows += base.window_report("baseline_2book_prod_SAMEWINDOW", baseline_2book)
    rows += base.window_report("exp_c1_stateswap_bull_only", port_c1)
    rows += base.window_report("exp_3book_dc33_static_REF", static3_ret)
    hdr = f"{'config':<34}{'window':<12}{'CAGR%':>8}{'Sharpe':>8}{'Sortino':>9}{'MaxDD%':>9}{'Calmar':>8}{'N':>7}"
    print(hdr)
    for r in rows:
        print(f"{r[0]:<34}{r[1]:<12}{r[2]:>7.2f}{r[3]:>8.2f}{r[4]:>9.2f}{r[5]:>8.1f}{r[6]:>8.2f}{r[7]:>7d}")

    yrs = (calendar[-1] - calendar[0]).days / 365.25
    print(f"\nself-check: max weight-leak = {max_leak:.2e} (bucket weights sum to 1.0 by construction)")
    print(f"state flips (regime LAG<->DC transitions): {n_flip} ({n_flip/yrs:.2f}/yr)")
    print(f"  turnover cost total (2-sided, on flip days): {turnover_cost_total*100:.4f}% cumulative "
          f"(annualized drag ~{turnover_cost_total/yrs*100:.4f}pp/yr)")
    print(f"band rebalance events (+-10pp): {n_rebal} ({n_rebal/yrs:.2f}/yr), "
          f"rebalance cost total: {rebal_cost_total*100:.4f}% cumulative")
    print(f"flip dates: {[d.date().isoformat() for d in flip_dates]}")

    # ---- decompose: how much of the CAGR delta is turnover cost vs BULL-swap benefit ----
    cagr_baseline = [r for r in rows if r[0] == "baseline_2book_prod_SAMEWINDOW" and r[1] == "FULL"][0][2]
    cagr_c1 = [r for r in rows if r[0] == "exp_c1_stateswap_bull_only" and r[1] == "FULL"][0][2]
    print(f"\nCAGR delta vs baseline (net of turnover cost, FULL window): {cagr_c1 - cagr_baseline:+.2f}pp")

    out = pd.DataFrame({
        "date": calendar, "state": state, "w_lag_tgt": w_lag_tgt,
        "r_bal": r_bal, "r_lag": r_lag, "r_dc": r_dc,
        "port_c1_stateswap": port_c1.values,
        "baseline_2book_prod": baseline_2book.values,
    })
    outcsv = os.path.join(OUTDIR, "exp_dc3book_c1_stateswap_univpit.csv")
    out.to_csv(outcsv, index=False)
    print(f"\nwrote {outcsv}")

    summary_csv = os.path.join(OUTDIR, "exp_dc3book_c1_stateswap_metrics.csv")
    import csv as _csv
    with open(summary_csv, "w", newline="") as f:
        w = _csv.writer(f)
        w.writerow(["config", "window", "cagr_pct", "sharpe", "sortino", "maxdd_pct", "calmar", "n_days"])
        w.writerows(rows)
    print(f"wrote {summary_csv}")


if __name__ == "__main__":
    main()
