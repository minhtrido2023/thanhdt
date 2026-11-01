# -*- coding: utf-8 -*-
"""Tiện ích dùng chung: nạp panel, lợi suất kỳ hạn, IC, bootstrap khối theo năm."""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "out")


def load_panel():
    p = pd.read_parquet(os.path.join(DATA, "panel_monthly.parquet"))
    return p.sort_values(["t", "ticker"]).reset_index(drop=True)


def month_close(px=None):
    """Close điều chỉnh tại mỗi cuối tháng (phiên cuối ≤ t trong 10 ngày)."""
    if px is None:
        px = pd.read_parquet(os.path.join(DATA, "px_daily.parquet"))
    vn = px[px.ticker == "VNINDEX"].time
    me = pd.DatetimeIndex(vn.groupby(vn.dt.to_period("M")).max().values)
    px = px.sort_values("time")
    grid = pd.DataFrame({"t": np.repeat(me, 1)})
    out = []
    for tk, g in px.groupby("ticker"):
        g = g[["time", "Close"]].dropna()
        if len(g) == 0:
            continue
        m = pd.merge_asof(grid, g, left_on="t", right_on="time", direction="backward")
        m = m[(m.t - m.time).dt.days <= 10]
        m["ticker"] = tk
        out.append(m[["t", "ticker", "Close"]])
    return pd.concat(out, ignore_index=True), me


def add_fwd(p, mc, me, hs=(3, 6, 12)):
    piv = mc.pivot(index="t", columns="ticker", values="Close").reindex(me)
    piv.index.name = "t"
    piv.columns.name = "ticker"
    for h in hs:
        fwd = piv.shift(-h) / piv - 1.0
        s = fwd.stack().rename(f"fwd{h}").reset_index()
        p = p.merge(s, on=["t", "ticker"], how="left")
    return p


def spearman(a, b):
    a = pd.Series(a).rank()
    b = pd.Series(b).rank()
    return float(np.corrcoef(a, b)[0, 1])


def ic_by_date(df, x, y, min_n=30):
    out = []
    for t, g in df.groupby("t"):
        g = g[[x, y]].dropna()
        if len(g) >= min_n:
            out.append((t, spearman(g[x], g[y]), len(g)))
    return pd.DataFrame(out, columns=["t", "ic", "n"])


def ic_summary(ics, h_months):
    """TB IC + t Newey-West lag h-1 + IS/OOS + CI bootstrap khối NĂM."""
    s = ics.set_index("t").ic.dropna()
    if len(s) < 6:
        return {}
    m = s.mean()
    L = max(h_months - 1, 0)
    e = s - m
    n = len(e)
    gamma0 = (e * e).sum() / n
    nw = gamma0
    for l in range(1, L + 1):
        w = 1 - l / (L + 1)
        nw += 2 * w * (e.values[l:] * e.values[:-l]).sum() / n
    se = np.sqrt(max(nw, 1e-12) / n)
    yrs = s.groupby(s.index.year)
    ylist = list(yrs.groups.keys())
    rng = np.random.default_rng(1)
    bs = []
    for _ in range(2000):
        pick = rng.choice(ylist, len(ylist), replace=True)
        bs.append(np.mean(np.concatenate([s[s.index.year == y].values for y in pick])))
    is_ = s[s.index.year <= 2019].mean()
    oos = s[s.index.year >= 2020].mean()
    return {"ic": m, "t_nw": m / se, "ci_lo": np.percentile(bs, 2.5), "ci_hi": np.percentile(bs, 97.5),
            "ic_is": is_, "ic_oos": oos, "n_dates": n, "n_years": len(ylist)}
