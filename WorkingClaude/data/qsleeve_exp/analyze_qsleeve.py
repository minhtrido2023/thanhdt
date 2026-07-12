# -*- coding: utf-8 -*-
"""Q-SLEEVE family analysis (job Taylor_20260712_080114, plan_quality_sleeve_20260712.md).
Windows + per-year LOO gate table for trials vs contemporaneous control.
Reads the _exp_qsleeve_* audit CSVs (DAILY rows -> combined_nav)."""
import sys
import numpy as np
import pandas as pd

BASE = "data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_"
RUNS = {
    "control": "wtnamecap_exp_qsleeve_control",
    "q8neu":   "wtew_n8_cap10_exp_qsleeve_q8neu",
    "q12neu":  "wtew_n12_cap10_exp_qsleeve_q12neu",
    "qf8neu":  "wtew_n8_cap10_exp_qsleeve_qf8neu",
}
# optional extra runs passed as name:pathsuffix args
for a in sys.argv[1:]:
    k, v = a.split(":", 1)
    RUNS[k] = v


def load_nav(suffix):
    df = pd.read_csv(BASE + suffix + ".csv", low_memory=False)
    d = df[(df.record_type == "DAILY") & df.combined_nav.notna()].copy()
    d["ymd"] = pd.to_datetime(d["ymd"])
    return d.groupby("ymd")["combined_nav"].last().astype(float).sort_index()


def stats(nav):
    nav = nav.dropna()
    if len(nav) < 30:
        return dict(cagr=np.nan, sharpe=np.nan, maxdd=np.nan, calmar=np.nan)
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1 / yrs) - 1
    r = np.log(nav / nav.shift()).dropna()
    spy = len(r) / yrs  # actual sessions/year
    sharpe = r.mean() / r.std() * np.sqrt(spy) if r.std() > 0 else np.nan
    dd = (nav / nav.cummax() - 1).min()
    calmar = cagr / abs(dd) if dd < 0 else np.nan
    return dict(cagr=cagr * 100, sharpe=sharpe, maxdd=dd * 100, calmar=calmar)


def rechain_excl_year(nav, y):
    """Re-chain daily returns excluding calendar year y."""
    r = nav.pct_change().dropna()
    r = r[r.index.year != y]
    return 1000.0 * (1 + r).cumprod()


def yearly_ret(nav):
    out = {}
    for y in sorted(set(nav.index.year)):
        ny = nav[nav.index.year == y]
        if len(ny) >= 5:
            out[y] = (ny.iloc[-1] / ny.iloc[0] - 1) * 100
    return out


navs = {k: load_nav(v) for k, v in RUNS.items()}
ctl = navs["control"]

WINDOWS = {
    "FULL":    lambda s: s,
    "IS14-19": lambda s: s[s.index <= "2019-12-31"],
    "OOS20+":  lambda s: s[s.index >= "2020-01-01"],
    "OOSex21": lambda s: rechain_excl_year(s[s.index >= "2020-01-01"], 2021),
    "2022+":   lambda s: s[s.index >= "2022-01-01"],
    "2024+":   lambda s: s[s.index >= "2024-01-01"],
}

print("=" * 110)
hdr = f"{'run':10s}" + "".join(f"{w:>26s}" for w in WINDOWS)
print(hdr)
print(f"{'':10s}" + f"{'CAGR/Sharpe/MaxDD/Calmar':>26s}" * len(WINDOWS))
for k, nav in navs.items():
    row = f"{k:10s}"
    for w, fn in WINDOWS.items():
        st = stats(fn(nav))
        row += f"{st['cagr']:7.2f}/{st['sharpe']:4.2f}/{st['maxdd']:6.1f}/{st['calmar']:5.2f}"
    print(row)

print("\n--- per-year LOO: delta FULL-CAGR (trial - control) when year y is EXCLUDED from both ---")
years = sorted(set(ctl.index.year))
print(f"{'drop-year':>10s}" + "".join(f"{k:>10s}" for k in navs if k != "control"))
for y in years:
    c = stats(rechain_excl_year(ctl, y))["cagr"]
    row = f"{y:>10d}"
    for k, nav in navs.items():
        if k == "control":
            continue
        t = stats(rechain_excl_year(nav, y))["cagr"]
        row += f"{t - c:+10.2f}"
    print(row)
c_all = stats(ctl)["cagr"]
row = f"{'(none)':>10s}"
for k, nav in navs.items():
    if k == "control":
        continue
    row += f"{stats(nav)['cagr'] - c_all:+10.2f}"
print(row)

print("\n--- yearly returns (pp) ---")
yr_ctl = yearly_ret(ctl)
print(f"{'year':>6s}{'control':>9s}" + "".join(f"{k:>9s}" for k in navs if k != "control"))
for y in years:
    row = f"{y:>6d}{yr_ctl.get(y, float('nan')):>9.1f}"
    for k, nav in navs.items():
        if k == "control":
            continue
        row += f"{yearly_ret(nav).get(y, float('nan')):>9.1f}"
    print(row)
