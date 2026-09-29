"""BRIDGE metric: is the cross-sectional MOMENTUM environment structurally weaker, or cyclical?

Daily AC(1) is a microstructure measure — it is NOT the same thing as the 6-12M cross-sectional
momentum that BAL/SIGNAL_V11 harvests. This file measures the momentum environment DIRECTLY:
per month-end t (causal, no look-ahead in the predictor), Spearman IC between
  predictor  = 6-1 momentum (return from t-7 to t-1 month-end; skips the most recent month)
  outcome    = forward 3-month return (t -> t+3)
across universe_pit members. Also 12-1 momentum and 1M short-term reversal for contrast.
Aggregated to calendar-year means, then the SAME break test as structural.py.
"""
import os
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

D = os.path.dirname(os.path.abspath(__file__))
MIN_XS = 30           # min names in a cross-section
MIN_DAYS = 10         # min trading days in the month-end month

p = pd.read_csv(os.path.join(D, "monthly_panel.csv"), parse_dates=["ym", "asof"])
p = p[p.ndays >= MIN_DAYS].sort_values(["ticker", "ym"])
w = p.pivot(index="ym", columns="ticker", values="close_me").sort_index()
print(f"panel {w.shape[0]} months x {w.shape[1]} tickers, {w.index.min().date()} -> {w.index.max().date()}")

mom6 = w.shift(1) / w.shift(7) - 1      # 6-1: t-7 -> t-1  (all data <= t-1)
mom12 = w.shift(1) / w.shift(13) - 1    # 12-1
rev1 = w / w.shift(1) - 1               # last month return (short-term reversal probe)
fwd3 = w.shift(-3) / w - 1              # outcome t -> t+3 (NOT used as a filter, only as outcome)

rows = []
for t in w.index:
    for name, pred in [("mom6", mom6), ("mom12", mom12), ("rev1", rev1)]:
        x, y = pred.loc[t], fwd3.loc[t]
        m = x.notna() & y.notna()
        if m.sum() < MIN_XS:
            continue
        ic, _ = spearmanr(x[m], y[m])
        rows.append({"ym": t, "signal": name, "ic": ic, "n": int(m.sum())})
ic = pd.DataFrame(rows)
ic["year"] = ic.ym.dt.year
ic.to_csv(os.path.join(D, "momentum_ic_monthly.csv"), index=False)

tab = ic.pivot_table(index="year", columns="signal", values="ic", aggfunc="mean")
cnt = ic[ic.signal == "mom6"].groupby("year")["n"].mean().rename("n_xs")
nm = ic[ic.signal == "mom6"].groupby("year")["ic"].count().rename("n_months")
out = tab.join(cnt).join(nm)
print("\n=== Annual mean cross-sectional IC (predictor causal, outcome fwd-3M) ===")
print(out.round(4).to_string())
out.to_csv(os.path.join(D, "momentum_ic_annual.csv"))

def break_search(y, xy, lo, hi, minseg=3):
    y = np.asarray(y, float); xy = np.asarray(xy)
    m = ~np.isnan(y); y, xy = y[m], xy[m]
    ssr0 = ((y - y.mean()) ** 2).sum()
    best = (None, np.inf, np.nan, np.nan)
    for b in range(lo, hi + 1):
        pre, post = y[xy < b], y[xy >= b]
        if pre.size < minseg or post.size < minseg: continue
        s = ((pre - pre.mean()) ** 2).sum() + ((post - post.mean()) ** 2).sum()
        if s < best[1]: best = (b, s, pre.mean(), post.mean())
    return best[0], 1 - best[1] / ssr0, best[2], best[3]

rng = np.random.default_rng(31)
print("\n=== Break test on the annual IC series (grid 2010-2022) ===")
for sig in ["mom6", "mom12", "rev1"]:
    s = out[sig].dropna()
    s = s[(s.index >= 2007) & (s.index <= 2026)]
    b, r2, mpre, mpost = break_search(s.to_numpy(), s.index.to_numpy(), 2010, 2022)
    v, yy = s.to_numpy(), s.index.to_numpy()
    pp = sum(break_search(rng.permutation(v), yy, 2010, 2022)[1] >= r2 for _ in range(3000)) / 3000
    print(f"{sig:6s} N={len(s):2d} break={b} R2gain={r2:.3f} pre={mpre:+.4f} post={mpost:+.4f} p_perm={pp:.4f}")

print("\n=== Era means (IC) + fraction of months with IC>0 ===")
for lo, hi in [(2007, 2009), (2010, 2014), (2015, 2019), (2020, 2023), (2024, 2026)]:
    sub = ic[(ic.year >= lo) & (ic.year <= hi)]
    line = f"{lo}-{hi}: "
    for sig in ["mom6", "mom12", "rev1"]:
        s = sub[sub.signal == sig]["ic"]
        line += f"{sig} mean={s.mean():+.4f} hit={np.mean(s > 0):.2f} (nM={len(s)})  "
    print(line)
