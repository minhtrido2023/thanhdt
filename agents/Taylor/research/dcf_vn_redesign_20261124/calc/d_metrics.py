# -*- coding: utf-8 -*-
"""d_metrics.py — đo tiêu chí (1) cắt giá 36T, (2a-2d) tầm nhìn, cho mọi biến thể. Seed 20261124.
In: ../out/vp.parquet. Out: ../out/metrics.csv, cases.csv, events_<v>.csv, never_cross_<v>.csv"""
import os, sys, json
import numpy as np, pandas as pd
from scipy.stats import spearmanr, rankdata
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out")
SEED = 20261124; B_ALL = int(os.environ.get("B_ALL", "300"))
vp = pd.read_parquet(os.path.join(OUT, "vp.parquet")).sort_values(["ticker", "ym"]).reset_index(drop=True)
vp["ymp"] = pd.PeriodIndex(vp.ym, freq="M"); vp["mi"] = vp.ymp.dt.year * 12 + vp.ymp.dt.month
VARS = [c[3:] for c in vp.columns if c.startswith("lv_")]
only = os.environ.get("ONLY"); VARS = [v for v in VARS if (not only or v in only.split(","))]
# lợi suất vượt trội so universe EW cùng tháng
for N in (12, 24, 36):
    m = vp[vp.in_universe & vp[f"fwd{N}"].notna()].groupby("ym")[f"fwd{N}"].apply(lambda x: np.log(np.mean(np.exp(x))))
    vp[f"ex{N}"] = vp[f"fwd{N}"] - vp.ym.map(m)
ERA = {"IS": ("2014-01", "2019-12"), "OOS": ("2020-01", "2099-12")}

def crossing(df, col):
    """cho mỗi dòng: số tháng tới lần đổi dấu kế tiếp của log V/P (NaN nếu không có)."""
    out = np.full(len(df), np.nan)
    for tk, g in df.groupby("ticker", sort=False):
        s = np.sign(g[col].values); mi = g.mi.values; n = len(s); nxt = np.full(n, np.nan)
        last_mi = None; last_sign = None
        # duyệt ngược: nd[i] = mi của tháng gần nhất phía sau có dấu khác s[i]
        next_diff = {1.0: np.nan, -1.0: np.nan}   # mi gần nhất phía sau mang dấu +1 / -1
        for i in range(n - 1, -1, -1):
            if np.isnan(s[i]) or s[i] == 0:
                continue
            nxt[i] = next_diff[-s[i]] - mi[i] if not np.isnan(next_diff[-s[i]]) else np.nan
            next_diff[s[i]] = mi[i]
        out[g.index.values] = nxt
    return out

def boot_ic(d, col, ycol, B, rng):
    """IC hạng trung bình theo ngày + CI bootstrap cụm mã."""
    groups = [(g[col].values, g[ycol].values, g.ticker.values) for _, g in d.groupby("ym") if len(g) >= 30]
    if not groups:
        return np.nan, np.nan, np.nan, 0
    ics = [spearmanr(x, y)[0] for x, y, _ in groups]; pt = float(np.mean(ics))
    tks = np.unique(np.concatenate([t for _, _, t in groups])); code = {t: i for i, t in enumerate(tks)}
    gi = [np.array([code[t] for t in tt]) for _, _, tt in groups]
    bs = []
    for _ in range(B):
        w = np.bincount(rng.integers(0, len(tks), len(tks)), minlength=len(tks))
        v = []
        for (x, y, _), ii in zip(groups, gi):
            rep = np.repeat(np.arange(len(ii)), w[ii])
            if len(rep) >= 20:
                v.append(np.corrcoef(rankdata(x[rep]), rankdata(y[rep]))[0, 1])
        bs.append(np.mean(v))
    return pt, float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)), len(groups)

rows = []; case_rows = []
for v in VARS:
    col = f"lv_{v}"; rng = np.random.default_rng(SEED)
    d = vp[vp[col].notna()].copy().reset_index(drop=True)
    d["nx"] = crossing(d, col)
    d["has36"] = d.fwd36.notna()
    d["lVadj"] = d[col] + np.log(d.Close)
    rec = {"variant": v}
    for era, (a, b) in ERA.items():
        u = d[d.in_universe & (d.ym >= a) & (d.ym <= b)]
        f = u[u.has36]
        cr = (f.nx <= 36)
        rec[f"{era}_n36"] = len(f); rec[f"{era}_ntk"] = f.ticker.nunique()
        rec[f"{era}_medVP"] = float(np.exp(u[col].median())); rec[f"{era}_iqr"] = float(u[col].quantile(.75) - u[col].quantile(.25))
        rec[f"{era}_cross36"] = cr.mean()
        rec[f"{era}_cross36_exp"] = cr[f[col] < 0].mean(); rec[f"{era}_cross36_chp"] = cr[f[col] > 0].mean()
        rec[f"{era}_share_exp"] = (f[col] < 0).mean()
        for N in (12, 24, 36):
            q = u[u.ymp.dt.month.isin([3, 6, 9, 12]) & u[f"ex{N}"].notna()]
            ic, lo, hi, nd = boot_ic(q, col, f"ex{N}", B_ALL if N == 36 else 0, rng) if N == 36 else (
                float(np.mean([spearmanr(g[col], g[f"ex{N}"])[0] for _, g in q.groupby("ym") if len(g) >= 30] or [np.nan])), np.nan, np.nan, 0)
            rec[f"{era}_ic{N}"] = ic
            if N == 36:
                rec[f"{era}_ic36_lo"] = lo; rec[f"{era}_ic36_hi"] = hi; rec[f"{era}_ic36_ndates"] = nd
        q = u[u.ymp.dt.month.isin([3, 6, 9, 12]) & u.ex36.notna()]
        if len(q) > 100:
            x = q[col].values; y = q.ex36.values
            rec[f"{era}_beta36"] = float(np.cov(x, y)[0, 1] / np.var(x))
            rec[f"{era}_gapratio36"] = float(np.median(np.abs(x - q.fwd36.values)) / np.median(np.abs(x)))   # |log(V0/P36)|/|log(V0/P0)|
        # (2c) sự kiện cắt lên / cắt xuống, re-arm 36 tháng
        ev = []
        for tk, g in d.groupby("ticker", sort=False):
            s = (g[col].values >= 0); mi = g.mi.values; iu = g.in_universe.values; ym = g.ym.values
            last = {True: -999, False: -999}
            for i in range(6, len(g)):
                if s[i] != s[i - 1] and (s[i - 6:i] == (not s[i])).all() and (mi[i] - mi[i - 6] == 6) and iu[i] and a <= ym[i] <= b:
                    if mi[i] - last[s[i]] >= 36:
                        last[s[i]] = mi[i]
                        ev.append((tk, ym[i], "up" if s[i] else "down", g.ex12.values[i], g.ex24.values[i], g.ex36.values[i]))
        ev = pd.DataFrame(ev, columns=["ticker", "ym", "dir", "ex12", "ex24", "ex36"])
        if os.environ.get("SAVE_EVENTS"):
            ev.to_csv(os.path.join(OUT, f"events_{v}_{era}.csv"), index=False)
        for dr in ("up", "down"):
            e = ev[ev.dir == dr]
            rec[f"{era}_ev_{dr}_n"] = len(e)
            for N in (12, 36):
                rec[f"{era}_ev_{dr}_ex{N}"] = e[f"ex{N}"].mean(); rec[f"{era}_ev_{dr}_n{N}"] = int(e[f"ex{N}"].notna().sum())
    # % mã không bao giờ cắt (>=60 tháng in_universe từ 2014)
    u = d[(d.ym >= "2014-01")]
    cnt = u[u.in_universe].groupby("ticker").size(); elig = cnt[cnt >= 60].index
    g = u[u.ticker.isin(elig)].groupby("ticker")[col].agg(lambda x: (np.sign(x) > 0).mean())
    rec["never_cross"] = float(((g == 0) | (g == 1)).mean()); rec["never_cross_n"] = len(g)
    rec["always_exp"] = float((g == 0).mean()); rec["always_chp"] = float((g == 1).mean())
    if os.environ.get("SAVE_EVENTS"):
        g.rename("share_months_V_gt_P").to_csv(os.path.join(OUT, f"side_share_{v}.csv"))
    # bám giá: corr quý Δlog V vs Δlog P
    qd = d[d.in_universe & d.ymp.dt.month.isin([3, 6, 9, 12]) & (d.ym >= "2014-01")].copy()
    qd["dV"] = qd.groupby("ticker").lVadj.diff(); qd["dP"] = np.log(qd.Close).groupby(qd.ticker).diff()
    qd = qd.dropna(subset=["dV", "dP"])
    rec["corr_dV_dP"] = float(np.corrcoef(qd.dV, qd.dP)[0, 1]); rec["sd_dV_over_dP"] = float(qd.dV.std() / qd.dP.std())
    rows.append(rec)
    # (2d) 4 ca
    def share(tk, a, b, sign):
        x = d[(d.ticker == tk) & (d.ym >= a) & (d.ym <= b)][col]
        return (np.nan if len(x) == 0 else float(((x > 0) if sign > 0 else (x < 0)).mean())), len(x)
    def vadj(tk, ym):
        x = d[(d.ticker == tk) & (d.ym == ym)].lVadj
        return float(np.exp(x.iloc[0])) if len(x) else np.nan
    c1, n1 = share("VCS", "2015-01", "2015-12", 1); c2, n2 = share("DGC", "2016-01", "2016-12", 1)
    c3, n3 = share("VNM", "2011-01", "2011-12", 1); c4, n4 = share("VNM", "2015-07", "2016-12", -1)
    h = [vadj("HPG", y) for y in ("2018-12", "2019-06", "2019-12", "2020-06")]; c5s, n5 = share("HPG", "2019-01", "2019-12", 1)
    hp = bool(h[2] > h[0] and h[3] > h[1] and (c5s or 0) > 0)
    score = sum([c1 >= .5 if c1 == c1 else False, c2 >= .5 if c2 == c2 else False, c3 >= .5 if c3 == c3 else False, c4 >= .5 if c4 == c4 else False, hp])
    case_rows.append({"variant": v, "VCS_2015_shareV>P": c1, "DGC_2016_shareV>P": c2, "VNM_2011_shareV>P": c3, "VNM_1507_1612_shareV<P": c4,
                      "HPG_V_1812": h[0], "HPG_V_1906": h[1], "HPG_V_1912": h[2], "HPG_V_2006": h[3], "HPG_2019_shareV>P": c5s,
                      "HPG_pass": hp, "score5": int(score), "n_obs": f"{n1}/{n2}/{n3}/{n4}/{n5}"})
    print(v, {k: (round(x, 3) if isinstance(x, float) else x) for k, x in rec.items() if k in (
        "IS_cross36", "IS_cross36_exp", "IS_cross36_chp", "OOS_cross36", "OOS_cross36_exp", "OOS_cross36_chp", "never_cross", "IS_ic36", "OOS_ic36")}, "cases", score, flush=True)
sfx = os.environ.get("SFX", "")
pd.DataFrame(rows).to_csv(os.path.join(OUT, f"metrics{sfx}.csv"), index=False)
pd.DataFrame(case_rows).to_csv(os.path.join(OUT, f"cases{sfx}.csv"), index=False)
