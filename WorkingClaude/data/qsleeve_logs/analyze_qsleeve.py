#!/usr/bin/env python
"""Q-SLEEVE family analysis — job Taylor_20260712_080114 (plan_quality_sleeve_20260712.md).
Reads the _exp_qsleeve* CSVs, computes window metrics + per-year LOO vs control + gate table.
Usage: python analyze_qsleeve.py [tags...]   (default: ctrl q8neu q12neu qf8neu)
"""
import sys, os, glob, math
import numpy as np, pandas as pd

DATA = "/home/trido/thanhdt/WorkingClaude/data"

def find_csv(tag):
    g = glob.glob(f"{DATA}/v23_golive_audit_2014_now_*_exp_qsleeve_{tag}.csv")
    assert len(g) == 1, f"{tag}: expected 1 csv, got {g}"
    return g[0]

def load_nav(path):
    df = pd.read_csv(path, low_memory=False)
    d = df[df["combined_nav"].notna() & df["ymd"].notna()].copy()
    d["ymd"] = pd.to_datetime(d["ymd"], errors="coerce")
    d = d.dropna(subset=["ymd"]).sort_values("ymd")
    return d.groupby("ymd")["combined_nav"].last().astype(float)

def metrics(nav):
    nav = nav.dropna()
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1 / yrs) - 1
    r = np.diff(np.log(nav.values))
    ann = len(r) / yrs
    sh = r.mean() / r.std(ddof=1) * math.sqrt(ann)
    dd = (nav / nav.cummax() - 1).min()
    cal = cagr / abs(dd) if dd < 0 else float("nan")
    return cagr * 100, sh, dd * 100, cal

def peryear(nav):
    out = {}
    for y in range(nav.index[0].year, nav.index[-1].year + 1):
        ny = nav[nav.index.year == y]
        if len(ny) < 5: continue
        out[y] = ny.iloc[-1] / ny.iloc[0] - 1
    return out

def loo_cagr(py, skip=()):
    """Geometric chain of yearly returns excluding `skip` years."""
    ys = [y for y in py if y not in skip]
    if not ys: return float("nan")
    g = 1.0
    for y in ys: g *= (1 + py[y])
    return (g ** (1 / len(ys)) - 1) * 100

def main():
    tags = sys.argv[1:] or ["ctrl", "q8neu", "q12neu", "qf8neu"]
    navs, pys = {}, {}
    print("=== Window metrics (CAGR% / Sharpe / MaxDD% / Calmar) ===")
    print(f"{'tag':10s} {'FULL':>26s} {'IS 2014-19':>26s} {'OOS 2020+':>26s}")
    for t in tags:
        nav = load_nav(find_csv(t)); navs[t] = nav; pys[t] = peryear(nav)
        rows = []
        for w in (nav, nav[nav.index <= "2019-12-31"], nav[nav.index >= "2020-01-01"]):
            c, s, d, k = metrics(w)
            rows.append(f"{c:6.2f}/{s:4.2f}/{d:6.1f}/{k:4.2f}")
        print(f"{t:10s} {rows[0]:>26s} {rows[1]:>26s} {rows[2]:>26s}")
    if "ctrl" not in navs: return
    print("\n=== Per-year return % (trial − ctrl in pp) ===")
    years = sorted(pys["ctrl"])
    hdr = "year  " + "".join(f"{t:>12s}" for t in tags)
    print(hdr)
    for y in years:
        line = f"{y}  "
        for t in tags:
            v = pys[t].get(y)
            if t == "ctrl":
                line += f"{v*100:11.1f}%"
            else:
                dv = (v - pys["ctrl"][y]) * 100 if v is not None else float("nan")
                line += f"{dv:+11.2f}p"
        print(line)
    print("\n=== Per-year LOO: delta CAGR (trial − ctrl, pp) khi bỏ từng năm ===")
    for t in tags:
        if t == "ctrl": continue
        deltas = {}
        for y in years:
            deltas[y] = loo_cagr(pys[t], (y,)) - loo_cagr(pys["ctrl"], (y,))
        deltas["ex20+21"] = loo_cagr(pys[t], (2020, 2021)) - loo_cagr(pys["ctrl"], (2020, 2021))
        neg = [k for k, v in deltas.items() if v < 0]
        print(f"{t}: " + "  ".join(f"{k}:{v:+.2f}" for k, v in deltas.items()))
        print(f"   -> LOO âm tại: {neg if neg else 'KHÔNG (pass)'}")

if __name__ == "__main__":
    main()
