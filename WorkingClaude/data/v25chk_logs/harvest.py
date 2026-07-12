"""Harvest V2.5 lever LOO/DSR runs — job Taylor_20260712_054553.
Run AFTER data/v25chk_logs/ALL_DONE exists:  python3 data/v25chk_logs/harvest.py
"""
import os, sys, glob
import numpy as np, pandas as pd
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from dsr_pbo_annex import load_nav, daily_logret, moments, dsr, expected_max_sr

W = "/home/trido/thanhdt/WorkingClaude"
TAGS = ["v25chk_LF", "v25chk_LEV", "v25chk_LOO2020", "v25chk_LOO2022",
        "v25chk_LOO2023", "v25chk_LEVnocap"]

def find_csv(tag):
    g = glob.glob(os.path.join(W, "data", f"*_{tag}.csv"))
    assert len(g) == 1, (tag, g)
    return g[0]

def metrics(s, a=None, b=None):
    if a: s = s[s.index >= a]
    if b: s = s[s.index <= b]
    r = np.log(s / s.shift(1)).dropna()
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1
    spy = len(r) / yrs
    sh = r.mean() / r.std() * np.sqrt(spy)
    dd = (s / s.cummax() - 1).min()
    return cagr * 100, sh, dd * 100, (cagr / abs(dd)) if dd else np.nan

navs = {}
print("=" * 100)
print(f"{'run':18s} {'FULL CAGR':>9s} {'Sharpe':>7s} {'MaxDD':>7s} {'Calmar':>7s} | {'IS CAGR':>8s} | {'OOS CAGR':>8s} {'OOS DD':>7s}")
for t in TAGS:
    try:
        s = load_nav(find_csv(t)); navs[t] = s
        f = metrics(s); i = metrics(s, None, "2019-12-31"); o = metrics(s, "2020-01-01")
        print(f"{t:18s} {f[0]:9.2f} {f[1]:7.2f} {f[2]:7.1f} {f[3]:7.2f} | {i[0]:8.2f} | {o[0]:8.2f} {o[2]:7.1f}")
    except Exception as e:
        print(f"{t:18s} MISSING/ERR: {e}")

if "v25chk_LF" in navs and "v25chk_LEV" in navs:
    lf, lev = navs["v25chk_LF"], navs["v25chk_LEV"]
    print("\n--- LEVER EDGE (LEV - LF), pp CAGR ---")
    base_full = metrics(lf)[0]; base_oos = metrics(lf, "2020-01-01")[0]
    for t in ["v25chk_LEV", "v25chk_LOO2020", "v25chk_LOO2022", "v25chk_LOO2023", "v25chk_LEVnocap"]:
        if t not in navs: continue
        d_full = metrics(navs[t])[0] - base_full
        d_oos = metrics(navs[t], "2020-01-01")[0] - base_oos
        d_cal = metrics(navs[t])[3] - metrics(lf)[3]
        print(f"{t:18s} dCAGR_full {d_full:+6.2f}pp  dCAGR_oos {d_oos:+6.2f}pp  dCalmar {d_cal:+5.2f}")

    # DSR on the EXCESS series (lever mechanism itself) and on LEV absolute
    idx = lf.index.intersection(lev.index)
    ex = np.log(lev.reindex(idx) / lev.reindex(idx).shift(1)) - np.log(lf.reindex(idx) / lf.reindex(idx).shift(1))
    ex = ex.dropna()
    T = len(ex); spy = T / ((idx[-1] - idx[0]).days / 365.25)
    sr_ex, g3, g4 = moments(ex.values)  # moments() returns per-obs SR directly
    nz = (ex.abs() > 1e-12).sum()
    for N in (3, 7, 20):
        var_sr = 1.0 / T  # null: zero-skill SR variance ~ 1/T per obs
        sr0 = expected_max_sr(var_sr, N)
        p, _ = dsr(sr_ex, sr0, g3, g4, T)
        print(f"DSR(excess lever series) N={N:2d}: SR_daily={sr_ex:.4f} (ann~{sr_ex*np.sqrt(spy):.2f}) "
              f"nonzero_days={nz}/{T}  DSR={p:.4f}" + ("  <<< RED FLAG (<0.95)" if p < 0.95 else ""))
    rl = np.asarray(daily_logret(lev)); Tl = len(rl)
    sr_lev, g3l, g4l = moments(rl)
    for N in (7, 20):
        p, _ = dsr(sr_lev, expected_max_sr(1.0 / Tl, N), g3l, g4l, Tl)
        print(f"DSR(LEV absolute)     N={N:2d}: SR_ann~{sr_lev*np.sqrt(252):.2f}  DSR={p:.4f}")
print("=" * 100)
print("Self-check reminder: grep 'self-check' data/v25chk_logs/*.log — must be 0 VND all runs")
