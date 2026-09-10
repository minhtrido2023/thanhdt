"""Robustness for the ac1_cs break: is it SELECTION (universe grew/changed) or REAL?

quant-research #11: when basket size changes, decompose kept-by-both vs added.
Here the universe grows 160 -> 450 names, so the raw cross-sectional median could move purely
from composition. Two controls:
  A) balanced cohort — only tickers with a valid annual ac1 in EVERY year 2009-2025
  B) wider break grid — is 2011 a real break or just the edge of my search window?
"""
import os
import numpy as np
import pandas as pd

D = os.path.dirname(os.path.abspath(__file__))
MIN_N = 100
p = pd.read_csv(os.path.join(D, "panel_ac_stats.csv"), parse_dates=["ym"])
p["year"] = p.ym.dt.year
agg = p.groupby(["year", "ticker"])[["n", "sx", "sy", "sxy", "sxx", "syy"]].sum().reset_index()
n, sx, sy, sxy, sxx, syy = (agg[c].to_numpy() for c in ["n", "sx", "sy", "sxy", "sxx", "syy"])
with np.errstate(invalid="ignore", divide="ignore"):
    den = np.sqrt((n * sxx - sx ** 2) * (n * syy - sy ** 2))
    agg["ac1"] = np.where((den > 0) & (n >= MIN_N), (n * sxy - sx * sy) / den, np.nan)
a = agg.dropna(subset=["ac1"])

YRS = list(range(2009, 2026))
cnt = a[a.year.isin(YRS)].groupby("ticker")["year"].nunique()
cohort = set(cnt[cnt == len(YRS)].index)
print(f"Balanced cohort: {len(cohort)} tickers present with valid ac1 in ALL {len(YRS)} years {YRS[0]}-{YRS[-1]}")

full = a.groupby("year")["ac1"].median()
bal = a[a.ticker.isin(cohort)].groupby("year")["ac1"].median()
nb = a[a.ticker.isin(cohort)].groupby("year")["ac1"].count()
cmp = pd.DataFrame({"ac1_cs_all": full, "ac1_cs_balanced": bal, "n_bal": nb,
                    "n_all": a.groupby("year")["ac1"].count()}).loc[2006:]
print("\n=== A) full universe vs BALANCED cohort ===")
print(cmp.round(4).to_string())

def break_search(y, x_year, lo, hi, minseg=3):
    y = np.asarray(y, float); xy = np.asarray(x_year)
    m = ~np.isnan(y); y, xy = y[m], xy[m]
    ssr0 = ((y - y.mean()) ** 2).sum()
    best = (None, np.inf, np.nan, np.nan)
    for b in range(lo, hi + 1):
        pre, post = y[xy < b], y[xy >= b]
        if pre.size < minseg or post.size < minseg: continue
        ssr = ((pre - pre.mean()) ** 2).sum() + ((post - post.mean()) ** 2).sum()
        if ssr < best[1]: best = (b, ssr, pre.mean(), post.mean())
    return best[0], 1 - best[1] / ssr0, best[2], best[3]

rng = np.random.default_rng(23)
print("\n=== B) wider break grid (start 2006 so 2011 is no longer the window edge) ===")
for label, s in [("ac1_cs_all", cmp["ac1_cs_all"]), ("ac1_cs_balanced", cmp["ac1_cs_balanced"])]:
    s = s.dropna()
    b, r2, mpre, mpost = break_search(s.to_numpy(), s.index.to_numpy(), 2009, 2022)
    v = s.to_numpy(); yy = s.index.to_numpy()
    cnt_p = sum(break_search(rng.permutation(v), yy, 2009, 2022)[1] >= r2 for _ in range(3000))
    print(f"{label:18s} N={len(s):2d} break={b} R2gain={r2:.3f} pre={mpre:.4f} post={mpost:.4f} p_perm={cnt_p/3000:.4f}")

# per-year share of tickers with ac1 > 0.05 (an economically-meaningful level of daily persistence)
sh = a.groupby("year")["ac1"].apply(lambda s: (s > 0.05).mean())
print("\n=== C) share of universe with ac1 > 0.05 (dose-response, not a single median) ===")
print(sh.loc[2006:].round(3).to_string())
