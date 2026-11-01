# -*- coding: utf-8 -*-
"""Vấn đề 2 — beta VN. PREREG §4. Ra: data/beta_panel.parquet (mọi biến thể tại cuối quý) + out/t2_*.csv"""
import os
import numpy as np
import pandas as pd
from common import DATA, OUT
import engine as E

P = print
px = pd.read_parquet(os.path.join(DATA, "px_daily.parquet"))
px = px[px.time >= "2008-01-01"]
# kiểm nối 2012→2013 (Close 2 nguồn cùng gốc điều chỉnh?)
for tk in ("VNM", "FPT", "VNINDEX"):
    g = px[(px.ticker == tk) & (px.time.between("2012-12-20", "2013-01-10"))][["time", "Close"]]
    P(tk, g.Close.round(1).tolist())
C = px.pivot(index="time", columns="ticker", values="Close").sort_index()
VOL = px.pivot(index="time", columns="ticker", values="Volume").reindex(C.index)
C = C[C.index.isin(px[px.ticker == "VNINDEX"].time)]       # lịch phiên = VNINDEX
VOL = VOL.reindex(C.index)
u = E.load_universe()
pan = pd.read_parquet(os.path.join(DATA, "panel_monthly.parquet"))
icb = pan.groupby("ticker").ICB_Code.last()
isfin = pan.groupby("ticker").is_fin.last()

def rets(freq):
    if freq == "d":
        c = C
    elif freq == "w":
        c = C.resample("W-FRI").last()
    else:
        c = C.resample("ME").last()
    c = c.where(c > 0)
    r = np.log(c / c.shift(1))
    if freq == "d":
        r = r.where(r.abs() <= 0.4)          # lỗi dữ liệu (biên độ tối đa UPCOM 15%, ngày đầu niêm yết 40%)
    return r

R = {f: rets(f) for f in ("d", "w", "m")}
PER_YEAR = {"d": 250, "w": 52, "m": 12}
QE = pd.date_range("2013-12-31", "2026-09-30", freq="QE")   # beta tới 2026Q3 cho tác động live; truth chỉ có tới 2025Q3
WINDOWS = (1, 2, 3, 5)


def ols(Y, x):
    """Y (n,k) có NaN, x (n,) ⇒ beta, se, nobs từng cột."""
    X = np.where(np.isnan(Y), np.nan, x[:, None])
    xm = np.nanmean(X, 0)
    ym = np.nanmean(Y, 0)
    dx = X - xm
    dy = Y - ym
    sxx = np.nansum(dx * dx, 0)
    b = np.nansum(dx * dy, 0) / sxx
    n = np.sum(~np.isnan(Y), 0)
    res = dy - b * dx
    s2 = np.nansum(res * res, 0) / np.maximum(n - 2, 1)
    se = np.sqrt(s2 / sxx)
    return b, se, n


def dimson(Y, xs):
    """Hồi quy bội Y lên các cột xs (list mảng), từng mã; beta = tổng hệ số."""
    Xf = np.column_stack(xs)
    out = np.full(Y.shape[1], np.nan)
    for j in range(Y.shape[1]):
        y = Y[:, j]
        m = ~np.isnan(y) & ~np.isnan(Xf).any(1)
        if m.sum() < 20:
            continue
        A = np.column_stack([np.ones(m.sum()), Xf[m]])
        coef = np.linalg.lstsq(A, y[m], rcond=None)[0]
        out[j] = coef[1:].sum()
    return out


def window_slice(Rf, T, years):
    lo = T - pd.DateOffset(years=years)
    return Rf[(Rf.index > lo) & (Rf.index <= T)]


rows = []
for T in QE:
    ud = u.time[u.time <= T].max()
    tks = sorted(set(u.ticker[u.time == ud]) & set(C.columns))
    for f in ("d", "w", "m"):
        Rf = R[f]
        for W in WINDOWS:
            S = window_slice(Rf, T, W)
            if f == "d":
                full = len(S)
            else:
                full = PER_YEAR[f] * W
            for bench in ("VNINDEX", "VN30"):
                if bench not in S.columns:
                    continue
                x = S[bench].values
                if np.isnan(x).mean() > 0.2:
                    continue
                Y = S[tks].values
                b, se, n = ols(Y, x)
                okn = n >= 0.7 * full
                rec = pd.DataFrame({"T": T, "ticker": tks, "freq": f, "win": W, "bench": bench,
                                    "ols": b, "se": se, "nobs": n})
                rec = rec[okn]
                if len(rec) < 20:
                    continue
                cs_mean = rec.ols.mean()
                cs_var = rec.ols.var()
                w = cs_var / (cs_var + rec.se ** 2)
                rec["vasicek"] = w * rec.ols + (1 - w) * cs_mean
                rec["blume"] = 0.67 * rec.ols + 0.33
                if f in ("d", "w"):
                    keep = [tks.index(t) for t in rec.ticker]
                    xl = np.concatenate([[np.nan], x[:-1]])
                    xf = np.concatenate([x[1:], [np.nan]])
                    rec["dimson"] = dimson(Y[:, keep], [xl, x, xf])
                if f == "d":
                    bl, _, _ = ols(Y[:, keep], xl)
                    bf, _, _ = ols(Y[:, keep], xf)
                    rho = pd.Series(x).autocorr(1)
                    rec["sw"] = (bl + rec.ols.values + bf) / (1 + 2 * rho)
                rows.append(rec)
    P("T", T.date(), "done")
B = pd.concat(rows, ignore_index=True)

# --------------- sự thật: 12T kế tiếp — Dimson tuần (lag 0,1) vs VNINDEX; phụ: OLS ngày
truth = []
for T in QE:
    S = R["w"][(R["w"].index > T) & (R["w"].index <= T + pd.DateOffset(years=1))]
    Sd = R["d"][(R["d"].index > T) & (R["d"].index <= T + pd.DateOffset(years=1))]
    tks = sorted(B.ticker[B["T"] == T].unique())
    x = S["VNINDEX"].values
    xl = np.concatenate([[np.nan], x[:-1]])
    Y = S[tks].values
    tw = dimson(Y, [xl, x])
    td, _, nd = ols(Sd[tks].values, Sd["VNINDEX"].values)
    down = (S["VNINDEX"] < 0).values
    dsum = np.nansum(Y[down], 0)
    nn = np.sum(~np.isnan(Y), 0)
    truth.append(pd.DataFrame({"T": T, "ticker": tks, "beta_true_w": tw, "beta_true_d": td,
                               "down_sum": np.where(nn >= 40, dsum, np.nan), "nw": nn}))
TR = pd.concat(truth, ignore_index=True)
TR.loc[TR.nw < 40, ["beta_true_w", "beta_true_d"]] = np.nan
B.to_parquet(os.path.join(DATA, "beta_panel.parquet"))
TR.to_parquet(os.path.join(DATA, "beta_truth.parquet"))
P("beta rows", len(B), "truth rows", len(TR))
