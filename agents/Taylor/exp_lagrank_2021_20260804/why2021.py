# -*- coding: utf-8 -*-
"""Why does 2021 hurt at 1B but HELP at 50B? + drop-worst-year placebo (job Taylor_20260804_061252).

Two things the rebuttal needs and the original report did not have:

(1) PLACEBO for the "excise a year" move. Dropping the single worst year mechanically raises the
    t-stat of any series, even under a pure null. So print the t-stat after dropping EACH year in
    turn: if ex-2021 t is merely the maximum of a wide, overlapping spread, the improvement is the
    arithmetic of deleting the worst 8% of the sample, not evidence about 2021.

(2) MECHANISM. The original report attributed the 2021 loss to "selection quality" (the ranking
    picked the wrong names). Test that directly with engine artefacts: entry-fill LAG capacity in
    2021 (how many entries, how fast they filled, how much cash sat idle) for FIFO vs treatment.
    signal date is encoded in holding_id = TICKER_YYYYMMDD_seq -> fill delay is measurable.

Usage: python why2021.py
"""
import numpy as np
import pandas as pd

ANN = 252.0
PRE = ("/home/trido/thanhdt/WorkingClaude/data/v23_golive_audit_2014_now_matpostbull_shrink0_"
       "edge_etfliqcustompitg_wtnamecap_advprice_exp_")
LEGS = ["A_dnpr_w0", "A_surprise_w0", "A_pahl3_w0", "A_fill_w0", "A_blend_w0",
        "B_surprise_w5", "B_pahl3_w5", "B_blend_w5", "B_dnpr_w5", "B_fill_w5"]


def paths(scale):
    suf = "_1B_univpit_nav1B.csv" if scale == "1B" else "_50B_univpit.csv"
    base = "L0_ctrl1B_univpit_nav1B.csv" if scale == "1B" else "L0_ctrl50B_univpit.csv"
    return PRE + base, {l: PRE + l + suf for l in LEGS}


def daily(path):
    df = pd.read_csv(path, low_memory=False)
    d = df[df["record_type"] == "DAILY"].copy()
    d["date"] = pd.to_datetime(d["ymd"])
    return d.sort_values("date").set_index("date")["combined_nav"].astype(float)


# ---------------------------------------------------------------- (1) placebo
print("=== (1) PLACEBO — t-stat of the daily difference series after dropping EACH year ===")
print("    (if ex-2021 is just the max of a wide spread, the gain is deletion arithmetic)\n")
for scale in ("1B", "50B"):
    bp, lp = paths(scale)
    b = daily(bp)
    print(f"  NAV {scale}")
    hdr = None
    for lab in ("B_surprise_w5", "A_blend_w0", "B_pahl3_w5"):
        t = daily(lp[lab])
        idx = b.index.intersection(t.index)
        d = pd.Series(np.diff(np.log(t.loc[idx].values)) - np.diff(np.log(b.loc[idx].values)),
                      index=idx[1:])
        yrs = sorted(set(d.index.year))
        ts = {}
        for y in yrs:
            s = d[d.index.year != y]
            ts[y] = s.mean() / (s.std(ddof=1) / np.sqrt(len(s)))
        t_all = d.mean() / (d.std(ddof=1) / np.sqrt(len(d)))
        if hdr is None:
            hdr = "    " + f"{'leg':<15} {'t(all)':>7} " + " ".join(f"{y:>6}" for y in yrs)
            print(hdr)
        row = " ".join(f"{ts[y]:6.2f}" for y in yrs)
        best = max(ts, key=lambda y: ts[y])
        print(f"    {lab:<15} {t_all:7.2f} {row}   best-drop={best} "
              f"(t {ts[best]:.2f}) | spread {min(ts.values()):.2f}..{max(ts.values()):.2f}")
    print()

# ---------------------------------------------------------------- (2) mechanism
print("=== (2) MECHANISM — LAG entry capacity & fill delay per year, FIFO vs treatment ===")


def lag_entries(path):
    df = pd.read_csv(path, low_memory=False)
    tx = df[(df["record_type"] == "TX") & df["play_type"].astype(str).str.startswith("LAG_")].copy()
    buys = tx[tx["action"].astype(str).str.lower() == "buy"].copy()
    buys["ymd"] = pd.to_datetime(buys["ymd"])
    sig = buys["holding_id"].astype(str).str.split("_").str[1]
    buys["sig_date"] = pd.to_datetime(sig, format="%Y%m%d", errors="coerce")
    first = buys.sort_values("ymd").groupby("holding_id").first()
    first["delay"] = (first["ymd"] - first["sig_date"]).dt.days
    first["year"] = first["ymd"].dt.year
    # realised P&L per closed holding, from the audit's own cash amounts
    amt = tx.groupby("holding_id")[["buy_amount", "sell_amount"]].sum()
    first = first.join(amt, rsuffix="_tot")
    first["ret%"] = np.where(first["buy_amount_tot"] > 0,
                             (first["sell_amount_tot"] / first["buy_amount_tot"] - 1) * 100, np.nan)
    return first


for scale in ("1B", "50B"):
    bp, lp = paths(scale)
    fb = lag_entries(bp)
    ft = lag_entries(lp["B_surprise_w5"])
    fw = lag_entries(lp["A_surprise_w0"])
    print(f"\n  NAV {scale} — FIFO vs B_surprise_w5 (reserve) vs A_surprise_w0 (reorder only)")
    print(f"    {'year':<6} {'N_FIFO':>7} {'N_w5':>6} {'N_w0':>6} | "
          f"{'delay_FIFO':>10} {'delay_w5':>9} {'delay_w0':>9} | "
          f"{'ret%_FIFO':>10} {'ret%_w5':>8} {'ret%_w0':>8}")
    for y in range(2014, 2027):
        a, b_, c = fb[fb.year == y], ft[ft.year == y], fw[fw.year == y]
        if len(a) == 0:
            continue
        print(f"    {y:<6} {len(a):7d} {len(b_):6d} {len(c):6d} | "
              f"{a['delay'].mean():10.2f} {b_['delay'].mean():9.2f} {c['delay'].mean():9.2f} | "
              f"{a['ret%'].median():10.1f} {b_['ret%'].median():8.1f} {c['ret%'].median():8.1f}")
