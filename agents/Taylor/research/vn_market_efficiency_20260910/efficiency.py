"""VN market-efficiency gauge — monthly, CAUSAL (trailing windows only).

Metrics (all computed at each month-end T using ONLY data <= T):
  VR(q) Lo-MacKinlay q=2,5,10 on trailing 250 trading days (+ hetero-robust z*)
  Hurst (DFA-1) on trailing 500 trading days
  AC(1) VNINDEX on trailing 250 trading days
  AC(1) cross-sectional median across universe_pit members, trailing 12 calendar months

NOT a trading signal. Diagnostic/context only.
"""
import os
import numpy as np
import pandas as pd

D = os.path.dirname(os.path.abspath(__file__))
W_VR = 250      # ~1 trading year
W_H = 500       # ~2 trading years (DFA needs more points)
MIN_N_TICKER = 100   # min daily obs per ticker in the 12M window


# ---------- Lo-MacKinlay variance ratio ----------
def variance_ratio(r, q):
    """r: 1-D array of log returns. Returns (VR, z_star) with heteroskedasticity-robust z."""
    r = np.asarray(r, float)
    T = r.size
    if T < q * 5:
        return np.nan, np.nan
    mu = r.mean()
    d = r - mu
    sig_a = (d ** 2).sum() / (T - 1)
    if sig_a <= 0:
        return np.nan, np.nan
    # overlapping q-period sums
    csum = np.concatenate([[0.0], np.cumsum(r)])
    qsum = csum[q:] - csum[:-q]                    # length T-q+1
    m = q * (T - q + 1) * (1.0 - q / T)
    sig_c = ((qsum - q * mu) ** 2).sum() / m
    vr = sig_c / sig_a
    # hetero-robust variance of VR (Lo-MacKinlay 1988 eq. 4.5.3)
    denom = ((d ** 2).sum()) ** 2
    theta = 0.0
    for j in range(1, q):
        num = ((d[j:] ** 2) * (d[:-j] ** 2)).sum()
        delta = num / denom          # Lo-MacKinlay (1988) eq 4.5.2 — no leading T
        theta += (2.0 * (q - j) / q) ** 2 * delta
    z = (vr - 1.0) / np.sqrt(theta) if theta > 0 else np.nan
    return vr, z


# ---------- DFA-1 Hurst ----------
def hurst_dfa(r):
    r = np.asarray(r, float)
    n = r.size
    if n < 200:
        return np.nan
    y = np.cumsum(r - r.mean())
    scales = np.unique(np.floor(np.logspace(np.log10(10), np.log10(n // 4), 12)).astype(int))
    scales = scales[scales >= 8]
    F = []
    used = []
    for s in scales:
        nseg = n // s
        if nseg < 4:
            continue
        seg = y[:nseg * s].reshape(nseg, s)
        x = np.arange(s)
        # detrend each segment with a linear fit
        X = np.vstack([x, np.ones(s)]).T
        coef, *_ = np.linalg.lstsq(X, seg.T, rcond=None)
        resid = seg.T - X @ coef
        f = np.sqrt((resid ** 2).mean())
        if f > 0:
            F.append(f)
            used.append(s)
    if len(F) < 4:
        return np.nan
    slope = np.polyfit(np.log(used), np.log(F), 1)[0]
    return slope


# ---------- load ----------
vni = pd.read_csv(os.path.join(D, "vnindex_daily.csv"), parse_dates=["time"]).sort_values("time")
vni["lr"] = np.log(vni["Close"]).diff()
vni = vni.dropna(subset=["lr"]).reset_index(drop=True)
print(f"VNINDEX daily returns: {len(vni):,} obs {vni.time.min().date()} -> {vni.time.max().date()}")

# month-end = last trading day of each calendar month
vni["ym"] = vni["time"].values.astype("datetime64[M]")
month_end_idx = vni.groupby("ym").tail(1).index.to_numpy()

rows = []
lr = vni["lr"].to_numpy()
for i in month_end_idx:
    ym = vni.loc[i, "ym"]
    asof = vni.loc[i, "time"]
    w = lr[max(0, i - W_VR + 1): i + 1]
    wh = lr[max(0, i - W_H + 1): i + 1]
    rec = {"ym": ym, "asof": asof, "n_vr": w.size, "n_h": wh.size}
    if w.size >= W_VR:
        for q in (2, 5, 10):
            v, z = variance_ratio(w, q)
            rec[f"vr{q}"] = v
            rec[f"vr{q}_z"] = z
        rec["ac1_idx"] = pd.Series(w).autocorr(1)
        rec["vol_ann"] = w.std(ddof=1) * np.sqrt(250)
    if wh.size >= W_H:
        rec["hurst"] = hurst_dfa(wh)
    rows.append(rec)
idx = pd.DataFrame(rows)

# ---------- cross-sectional AC(1) from sufficient statistics ----------
p = pd.read_csv(os.path.join(D, "panel_ac_stats.csv"), parse_dates=["ym"])
p = p.sort_values(["ticker", "ym"])
cols = ["n", "sx", "sy", "sxy", "sxx", "syy"]
# trailing 12 CALENDAR months per ticker -> reindex to a full monthly grid so gaps count as zeros
grid = pd.MultiIndex.from_product(
    [sorted(p["ticker"].unique()), pd.date_range(p.ym.min(), p.ym.max(), freq="MS")],
    names=["ticker", "ym"])
pf = p.set_index(["ticker", "ym"]).reindex(grid).fillna(0.0).reset_index()
roll = pf.groupby("ticker")[cols].rolling(12, min_periods=12).sum().reset_index(level=0)
roll["ym"] = pf["ym"].to_numpy()
n, sx, sy, sxy, sxx, syy = (roll[c].to_numpy() for c in cols)
with np.errstate(invalid="ignore", divide="ignore"):
    num = n * sxy - sx * sy
    den = np.sqrt((n * sxx - sx ** 2) * (n * syy - sy ** 2))
    roll["ac1"] = np.where((den > 0) & (n >= MIN_N_TICKER), num / den, np.nan)
cs = (roll.dropna(subset=["ac1"])
          .groupby("ym")["ac1"]
          .agg(ac1_cs_median="median", ac1_cs_mean="mean",
               ac1_cs_q25=lambda s: s.quantile(.25),
               ac1_cs_q75=lambda s: s.quantile(.75),
               n_tickers="count")
          .reset_index())

out = idx.merge(cs, on="ym", how="left")
out.to_csv(os.path.join(D, "efficiency_monthly.csv"), index=False)
print(f"efficiency_monthly.csv: {len(out)} months, {out.ym.min().date()} -> {out.ym.max().date()}")
print(out.dropna(subset=["vr2"]).tail(6)[
    ["ym", "vr2", "vr2_z", "vr5", "vr10", "hurst", "ac1_idx", "ac1_cs_median", "n_tickers"]].to_string(index=False))
