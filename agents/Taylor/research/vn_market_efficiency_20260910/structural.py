"""Structural-vs-cyclical test on NON-OVERLAPPING annual efficiency statistics.

The monthly series in efficiency_monthly.csv uses 250d rolling windows -> heavily overlapping,
so its month-to-month t-stats are meaningless. Here each calendar year contributes ONE
independent-ish observation, giving N=19 usable years (2008-2026) instead of 226 fake ones.

Test 1: single least-squares break search (Bai-Perron style, one break) per metric.
Test 2: does the level shift SURVIVE controlling for the cycle? Regress metric on
        [post-break dummy, log realized vol, |index 1y return|]. If the dummy dies once vol is
        controlled for -> the decline is a CYCLE artifact. If it survives -> structural.
"""
import os
import numpy as np
import pandas as pd
from efficiency import variance_ratio, hurst_dfa

D = os.path.dirname(os.path.abspath(__file__))
MIN_N_TICKER = 100
START = 2008   # VN universe crosses ~100 names in 2008 (CLAUDE.md / ticker_prune note)

vni = pd.read_csv(os.path.join(D, "vnindex_daily.csv"), parse_dates=["time"]).sort_values("time")
vni["lr"] = np.log(vni["Close"]).diff()
vni = vni.dropna(subset=["lr"])
vni["year"] = vni.time.dt.year

rows = []
for y, g in vni.groupby("year"):
    r = g["lr"].to_numpy()
    if r.size < 150:
        continue
    rec = {"year": y, "ndays": r.size}
    for q in (2, 5, 10):
        rec[f"vr{q}"], rec[f"vr{q}_z"] = variance_ratio(r, q)
    rec["ac1_idx"] = pd.Series(r).autocorr(1)
    rec["hurst"] = hurst_dfa(r)
    rec["vol_ann"] = r.std(ddof=1) * np.sqrt(250)
    rec["abs_ret_1y"] = abs(r.sum())
    rows.append(rec)
ann = pd.DataFrame(rows)

# annual cross-sectional AC(1): per-ticker corr WITHIN the calendar year, then cross-sec median
p = pd.read_csv(os.path.join(D, "panel_ac_stats.csv"), parse_dates=["ym"])
p["year"] = p.ym.dt.year
agg = p.groupby(["year", "ticker"])[["n", "sx", "sy", "sxy", "sxx", "syy"]].sum().reset_index()
n, sx, sy, sxy, sxx, syy = (agg[c].to_numpy() for c in ["n", "sx", "sy", "sxy", "sxx", "syy"])
with np.errstate(invalid="ignore", divide="ignore"):
    den = np.sqrt((n * sxx - sx ** 2) * (n * syy - sy ** 2))
    agg["ac1"] = np.where((den > 0) & (n >= MIN_N_TICKER), (n * sxy - sx * sy) / den, np.nan)
cs = (agg.dropna(subset=["ac1"]).groupby("year")
        .agg(ac1_cs=("ac1", "median"), n_tickers=("ac1", "count")).reset_index())
ann = ann.merge(cs, on="year", how="left")
ann = ann[ann.year >= START].reset_index(drop=True)
ann.to_csv(os.path.join(D, "efficiency_annual.csv"), index=False)
print("=== Annual (non-overlapping) efficiency stats ===")
print(ann[["year", "ndays", "vr2", "vr2_z", "vr5", "vr10", "hurst", "ac1_idx", "ac1_cs",
           "n_tickers", "vol_ann"]].round(4).to_string(index=False))


def break_search(y, x_year, lo=2011, hi=2022):
    """Single least-squares break: mean shift. Returns (best_year, ssr_ratio, mu_pre, mu_post)."""
    y = np.asarray(y, float)
    m = ~np.isnan(y)
    y, xy = y[m], np.asarray(x_year)[m]
    ssr0 = ((y - y.mean()) ** 2).sum()
    best = (None, np.inf, np.nan, np.nan)
    for b in range(lo, hi + 1):
        pre, post = y[xy < b], y[xy >= b]
        if pre.size < 3 or post.size < 3:
            continue
        ssr = ((pre - pre.mean()) ** 2).sum() + ((post - post.mean()) ** 2).sum()
        if ssr < best[1]:
            best = (b, ssr, pre.mean(), post.mean())
    return best[0], 1 - best[1] / ssr0, best[2], best[3], ssr0, best[1]


def ols(X, y):
    X = np.asarray(X, float); y = np.asarray(y, float)
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ b
    dof = len(y) - X.shape[1]
    s2 = (res ** 2).sum() / dof
    cov = s2 * np.linalg.pinv(X.T @ X)
    se = np.sqrt(np.diag(cov))
    return b, b / se, dof


print("\n=== Test 1: single break search (grid 2011-2022, N years = %d) ===" % len(ann))
print(f"{'metric':10s} {'break':>6s} {'R2gain':>7s} {'pre':>9s} {'post':>9s} {'p_perm':>8s}")
rng = np.random.default_rng(11)
breaks = {}
for met in ["vr2", "vr5", "vr10", "ac1_idx", "ac1_cs", "hurst"]:
    b, r2, mpre, mpost, ssr0, ssrb = break_search(ann[met], ann.year)
    # permutation test: shuffle the years, re-run the SAME break search -> how often do we get
    # an R2 gain this large by chance? (guards against "any 19-point series has a best break")
    v = ann[met].dropna().to_numpy()
    cnt = 0
    for _ in range(2000):
        vp = rng.permutation(v)
        _, r2p, *_ = break_search(vp, ann.year.to_numpy()[:len(vp)])
        cnt += (r2p >= r2)
    breaks[met] = b
    print(f"{met:10s} {b:>6d} {r2:>7.3f} {mpre:>9.4f} {mpost:>9.4f} {cnt/2000:>8.3f}")

print("\n=== Test 2: does the shift survive controlling for the cycle? ===")
print("model: metric ~ 1 + post_dummy + log(vol_ann) + |1y index return|")
print(f"{'metric':10s} {'break':>6s} {'b_post':>9s} {'t_post':>7s} {'t_logvol':>9s} {'t_absret':>9s}")
for met in ["vr2", "ac1_idx", "ac1_cs", "hurst"]:
    d = ann[["year", met, "vol_ann", "abs_ret_1y"]].dropna()
    post = (d.year >= breaks[met]).astype(float).to_numpy()
    X = np.column_stack([np.ones(len(d)), post, np.log(d.vol_ann.to_numpy()), d.abs_ret_1y.to_numpy()])
    b, t, dof = ols(X, d[met].to_numpy())
    print(f"{met:10s} {breaks[met]:>6d} {b[1]:>9.4f} {t[1]:>7.2f} {t[2]:>9.2f} {t[3]:>9.2f}   (dof={dof})")

print("\n=== Test 3: is the recent (2024-2026) level back inside the PRE-break range? ===")
for met in ["vr2", "ac1_idx", "ac1_cs", "hurst"]:
    b = breaks[met]
    pre = ann.loc[ann.year < b, met].dropna()
    post = ann.loc[(ann.year >= b) & (ann.year <= 2023), met].dropna()
    recent = ann.loc[ann.year >= 2024, met].dropna()
    print(f"{met:10s} pre({ann.year.min()}-{b-1}) [{pre.min():.4f},{pre.max():.4f}] med={pre.median():.4f} | "
          f"post({b}-2023) med={post.median():.4f} | recent(2024-26) {list(recent.round(4))}")
