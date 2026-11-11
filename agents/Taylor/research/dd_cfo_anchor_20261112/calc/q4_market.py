# -*- coding: utf-8 -*-
"""q4_market.py — kiểm luận điểm "thị trường VN định giá theo LN + chất lượng LN" (PRELOCK §Q4, mô tả).
Chéo mã tại as-of Q4 mỗi năm 2016–2025, toàn panel phi tài chính (mọi rating). Không dùng nhãn tương lai.
(i)  log MC0 ~ M1..M5 (log-log, chủ yếu đo quy mô) + bản chuẩn hoá theo tổng tài sản (đo bội số).
(ii) thưởng P/E cho tercile CFO3/NI3 cao vs thấp, FE ngành + log1p(g) + ROE; CI bootstrap cụm mã.
Run: $DNA_PYEXE -W ignore q4_market.py -> ../out/q4_market.json
"""
import os, sys, json
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out")
sys.path.insert(0, HERE)
import bases as Bm
SEED = 20261112; B = 1000
p, E1, E2, V, M0, A = Bm.build()
d = pd.DataFrame({"tk": p.ticker.values, "yr": p["asof"].dt.year.values, "qq": p["asof"].dt.quarter.values,
                  "grp": p.grp.values, "MC": p.MC0.values, "NIn": p.NI_norm.values, "NI3": A["NI3"],
                  "CFO3": A["CFO3"], "CPX3": A["CPX3"], "TA": E2.totalAsset_P0.values,
                  "g": p.g_exp.values, "roe": p.roe.values})
d = d[(d.qq == 4) & np.isfinite(d.MC) & (d.MC > 0) & (d.TA > 0)].copy()
d["FCFE3"] = (d.CFO3 - d.CPX3) / 3; d["CFOa"] = d.CFO3 / 3


def ols(y, Xs, fe=None):
    X = np.column_stack([np.ones(len(y))] + Xs)
    if fe is not None:
        D = pd.get_dummies(fe, drop_first=True).values.astype(float)
        X = np.column_stack([X, D])
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    e = y - X @ b
    return b, 1 - (e @ e) / ((y - y.mean()) @ (y - y.mean()))


def wins(s):
    lo, hi = np.nanpercentile(s, [1, 99]); return np.clip(s, lo, hi)


out = {"i_loglog": {}, "i_scaled": {}, "ii_pe_premium": {}}
for yr, g in d.groupby("yr"):
    c = g[(g.NIn > 0) & (g.CFOa > 0) & (g.FCFE3 > 0)]
    if len(c) >= 30:
        y = np.log(c.MC.values); ln = np.log(c.NIn.values)
        rq = np.clip(c.CFO3 / c.NI3.where(c.NI3 > 0), -1, 3).fillna(0).values
        mods = {"M1_logNI": [ln], "M2_logNI+CFO/NI": [ln, rq], "M3_logCFO": [np.log(c.CFOa.values)],
                "M4_logFCFE": [np.log(c.FCFE3.values)], "M5_logNI+logFCFE": [ln, np.log(c.FCFE3.values)]}
        out["i_loglog"][int(yr)] = {"n": len(c), **{k: round(ols(y, v)[1], 4) for k, v in mods.items()},
                                    **{k + "|FE": round(ols(y, v, c.grp.values)[1], 4) for k, v in mods.items()}}
    s = g[np.isfinite(g.NIn) & np.isfinite(g.CFOa) & np.isfinite(g.CPX3)]
    if len(s) >= 30:
        y = np.log(s.MC.values / s.TA.values)
        ni = wins(s.NIn.values / s.TA.values); cf = wins(s.CFOa.values / s.TA.values)
        cx = wins((s.CPX3.values / 3) / s.TA.values); fc = wins(s.FCFE3.values / s.TA.values)
        mods = {"S1_NI": [ni], "S2_NI+CFO": [ni, cf], "S3_NI+FCFE": [ni, fc], "S4_FCFE": [fc], "S5_CFO": [cf],
                "S6_NI+CFO+CPX": [ni, cf, cx]}
        o = {"n": len(s)}
        for k, v in mods.items():
            for fe in (None, "FE"):
                b, r2 = ols(y, v, s.grp.values if fe else None)
                o[k + ("|FE" if fe else "")] = round(r2, 4)
                if k == "S6_NI+CFO+CPX" and fe:
                    o["coef_S6FE"] = {"NI": round(b[1], 3), "CFO": round(b[2], 3), "CPX": round(b[3], 3)}
                if k == "S2_NI+CFO" and fe:
                    o["coef_S2FE"] = {"NI": round(b[1], 3), "CFO": round(b[2], 3)}
        out["i_scaled"][int(yr)] = o


def period_mean(dct, keys, yrs):
    return {k: round(float(np.mean([dct[y][k] for y in yrs if y in dct])), 4) for k in keys}


for name in ("i_loglog", "i_scaled"):
    keys = [k for k in next(iter(out[name].values())) if k not in ("n", "coef_S6FE", "coef_S2FE")]
    out[name + "_avg"] = {"2016_19": period_mean(out[name], keys, range(2016, 2020)),
                          "2020_25": period_mean(out[name], keys, range(2020, 2026))}

# (ii) thưởng P/E theo chất lượng
e = d[(d.NIn > 0) & (d.NI3 > 0) & np.isfinite(d.CFO3) & np.isfinite(d.roe) & np.isfinite(d.g)].copy()
e["q"] = e.CFO3 / e.NI3
e["ter"] = e.groupby("yr").q.transform(lambda s: pd.qcut(s.rank(method="first"), 3, labels=False))
e["lpe"] = np.log(e.MC / e.NIn)
e["roe_c"] = np.clip(e.roe, -0.2, 0.6); e["lg"] = np.log1p(e.g)


def prem(sub):
    y = sub.lpe.values
    X = [(sub.ter == 2).astype(float).values, (sub.ter == 0).astype(float).values, sub.lg.values, sub.roe_c.values]
    fe = sub.grp.astype(str) + "|" + sub.yr.astype(str)
    b, _ = ols(y, X, fe.values)
    return b[1] - b[2]   # cao − thấp


def boot(sub):
    tks = sub.tk.unique(); gi = sub.groupby("tk").indices
    rng = np.random.default_rng(SEED); bs = []
    for _ in range(B):
        pick = rng.choice(tks, len(tks))
        ss = sub.iloc[np.concatenate([gi[t] for t in pick])]
        try:
            bs.append(prem(ss))
        except Exception:
            pass
    return [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)]


for lab, yrs in (("2016_19", range(2016, 2020)), ("2020_25", range(2020, 2026))):
    sub = e[e.yr.isin(yrs)].reset_index(drop=True)
    out["ii_pe_premium"][lab] = {"n": len(sub), "n_tk": int(sub.tk.nunique()), "hi_minus_lo_logPE": round(prem(sub), 4),
                                 "ci_tk": boot(sub),
                                 "median_PE_by_tercile": {int(t): round(float(np.exp(sub[sub.ter == t].lpe.median())), 2) for t in (0, 1, 2)}}
by = {}
for yr, sub in e.groupby("yr"):
    sub = sub.reset_index(drop=True)
    if len(sub) >= 40:
        by[int(yr)] = {"n": len(sub), "hi_minus_lo": round(prem(sub), 4)}
out["ii_pe_premium"]["by_year"] = by
json.dump(out, open(os.path.join(OUT, "q4_market.json"), "w"), indent=1)
print(json.dumps({k: out[k] for k in ("i_loglog_avg", "i_scaled_avg")}, indent=1))
print(json.dumps(out["ii_pe_premium"], indent=1))
for y in sorted(out["i_scaled"]):
    print(y, out["i_scaled"][y].get("coef_S6FE"), out["i_scaled"][y].get("coef_S2FE"))
