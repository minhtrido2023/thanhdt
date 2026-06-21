# -*- coding: utf-8 -*-
"""wf_basket_size_cap.py — walk-forward IS/OOS + per-year check for the C+D basket configs.
Reads the audit CSV DAILY combined_nav for each config (NO backtest re-run) and computes
Full / IS(2014-2019) / OOS(2020-now) CAGR-Sharpe-MaxDD-Calmar, plus per-year CAGR.
Goal: confirm the (30,0.15) / (40,0.12) edge vs prod (30,0.10) is NOT one-year/overfit."""
import sys, numpy as np, pandas as pd

NAV = sys.argv[1] if len(sys.argv) > 1 else "500"
PRE = "data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap"
CONFIGS = {  # label -> filename tag
    "(30,0.10) PROD": "",            # untagged baseline file
    "(30,0.12)": "_n30_cap12",
    "(30,0.15)": "_n30_cap15",
    "(40,0.12)": "_n40_cap12",
    "(40,0.15)": "_n40_cap15",
}
IS_END = "2019-12-31"; OOS_START = "2020-01-01"


def load_nav(tag):
    f = f"{PRE}{tag}_nav{NAV}B.csv"
    A = pd.read_csv(f, low_memory=False)
    d = A[A.record_type == "DAILY"][["ymd", "combined_nav"]].copy()
    d["ymd"] = pd.to_datetime(d["ymd"]); d = d.dropna().set_index("ymd")["combined_nav"].astype(float)
    return d


def metrics(nav):
    nav = nav.dropna()
    if len(nav) < 30: return dict(cagr=np.nan, sharpe=np.nan, maxdd=np.nan, calmar=np.nan)
    days = (nav.index[-1] - nav.index[0]).days
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (365.25 / days) - 1
    r = nav.pct_change().dropna()
    sharpe = r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else np.nan
    dd = (nav / nav.cummax() - 1).min()
    calmar = cagr / abs(dd) if dd < 0 else np.nan
    return dict(cagr=cagr * 100, sharpe=sharpe, maxdd=dd * 100, calmar=calmar)


navs = {lbl: load_nav(tag) for lbl, tag in CONFIGS.items()}
print(f"================ WALK-FORWARD NAV={NAV}B ================")
hdr = f"{'config':<16}" + "".join(f"{w:>26}" for w in ["FULL", "IS 2014-19", "OOS 2020-now"])
print(hdr)
print(f"{'':16}" + "  CAGR  Sh   MaxDD  Cal " * 3)
for lbl, nav in navs.items():
    parts = []
    for win in [nav, nav[:IS_END], nav[OOS_START:]]:
        m = metrics(win)
        parts.append(f"{m['cagr']:6.2f} {m['sharpe']:.2f} {m['maxdd']:6.1f} {m['calmar']:.2f}")
    print(f"{lbl:<16}" + "  ".join(parts))

print(f"\n================ PER-YEAR CAGR (%) NAV={NAV}B ================")
years = sorted({d.year for d in navs["(30,0.10) PROD"].index})
print(f"{'year':<6}" + "".join(f"{l.replace(' PROD',''):>13}" for l in CONFIGS))
for y in years:
    row = f"{y:<6}"
    for lbl, nav in navs.items():
        sub = nav[(nav.index.year == y)]
        if len(sub) > 2:
            yr = (sub.iloc[-1] / sub.iloc[0] - 1) * 100
            row += f"{yr:>13.1f}"
        else:
            row += f"{'-':>13}"
    print(row)

print(f"\n================ Δ PER-YEAR vs (30,0.10) PROD [pp] NAV={NAV}B ================")
base = navs["(30,0.10) PROD"]
print(f"{'year':<6}" + "".join(f"{l.replace(' PROD',''):>13}" for l in CONFIGS if l != "(30,0.10) PROD"))
for y in years:
    bsub = base[base.index.year == y]
    if len(bsub) <= 2: continue
    byr = bsub.iloc[-1] / bsub.iloc[0] - 1
    row = f"{y:<6}"
    for lbl, nav in navs.items():
        if lbl == "(30,0.10) PROD": continue
        sub = nav[nav.index.year == y]
        yr = sub.iloc[-1] / sub.iloc[0] - 1 if len(sub) > 2 else np.nan
        row += f"{(yr - byr) * 100:>13.2f}"
    print(row)
