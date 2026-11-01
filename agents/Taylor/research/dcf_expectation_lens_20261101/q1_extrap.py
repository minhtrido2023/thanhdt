# -*- coding: utf-8 -*-
"""Q1 — thị trường ngoại suy cửa sổ tăng trưởng nào? Fama-MacBeth theo tháng (PREREG §2 Q1)."""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
P = print
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)

WIN = ["gQ2", "g1", "g2", "g3", "g5", "acc", "accS", "rg1", "rg2"]


def rk(s):
    r = s.rank(pct=True)
    return r - 0.5


def nw_t(x, L=12):
    x = pd.Series(x).dropna().values
    n = len(x)
    if n < 8:
        return np.nan
    m = x.mean()
    e = x - m
    g = (e * e).sum() / n
    for l in range(1, L + 1):
        g += 2 * (1 - l / (L + 1)) * (e[l:] * e[:-l]).sum() / n
    return m / np.sqrt(max(g, 1e-18) / n)


def load():
    p = pd.read_parquet(os.path.join(HERE, "data", "mpanel.parquet"))
    p = p[(p.t >= "2014-01-01")].copy()
    p["logPE"] = np.log(p.PE.where((p.PE > 0) & (p.PE < 200)))
    p["logPCF"] = np.log(p.PCF.where((p.PCF > 0) & (p.PCF < 500)))
    p["logEV"] = np.log(p.EVEB.where((p.EVEB > 0) & (p.EVEB < 200)))
    p["size"] = np.log(p.tv3.where(p.tv3 > 0))
    p["roe"] = p.ROE_Trailing
    return p


def fm(p, y, xs, min_n=40):
    rows = []
    for t, g in p.groupby("t"):
        g = g[[y] + xs].dropna()
        if len(g) < min_n:
            continue
        X = np.column_stack([np.ones(len(g))] + [rk(g[x]).values for x in xs])
        Y = g[y].values
        b, *_ = np.linalg.lstsq(X, Y, rcond=None)
        res = Y - X @ b
        r2 = 1 - res.var() / Y.var() if Y.var() > 0 else np.nan
        rows.append([t, r2, len(g)] + list(b[1:]))
    return pd.DataFrame(rows, columns=["t", "r2", "n"] + xs)


def summ(d, xs):
    out = {}
    for per, m in (("ALL", slice(None)), ("IS", d.t.dt.year <= 2019), ("OOS", d.t.dt.year >= 2020)):
        dd = d[m]
        out[f"R2_{per}"] = dd.r2.mean()
        for x in xs:
            out[f"{x}_b_{per}"] = dd[x].mean()
            out[f"{x}_t_{per}"] = nw_t(dd[x])
    out["n_months"] = len(d)
    out["n_med"] = d.n.median()
    return out


def main():
    p = load()
    res = []
    for y in ["logPE", "logPCF", "logEV", "f1", "f2"]:
        for w in WIN:
            s = summ(fm(p, y, [w]), [w])
            res.append({"y": y, "x": w, "R2_IS": s["R2_IS"], "R2_OOS": s["R2_OOS"], "b_IS": s[f"{w}_b_IS"],
                        "t_IS": s[f"{w}_t_IS"], "b_OOS": s[f"{w}_b_OOS"], "t_OOS": s[f"{w}_t_OOS"],
                        "months": s["n_months"], "n_med": s["n_med"]})
    r = pd.DataFrame(res)
    r.to_csv(os.path.join(OUT, "q1_univariate.csv"), index=False)
    P("=== Q1a đơn biến (hệ số trên hạng −0,5..0,5 ⇒ = chênh top−bottom) ===")
    P(r.round(3).to_string(index=False))
    J = ["gQ2", "g1", "g2", "g3", "g5"]
    for y in ["logPE", "f1", "f2"]:
        for ctrl in ([], ["roe", "size"]):
            xs = J + ctrl
            s = summ(fm(p, y, xs), xs)
            P(f"\n=== Q1b chung y={y} ctrl={ctrl}: R2 IS {s['R2_IS']:.3f} OOS {s['R2_OOS']:.3f} tháng {s['n_months']} ===")
            P("   " + "  ".join(f"{x}: b {s[f'{x}_b_IS']:+.3f}/{s[f'{x}_b_OOS']:+.3f} t {s[f'{x}_t_IS']:+.1f}/{s[f'{x}_t_OOS']:+.1f}"
                              for x in xs))
    # Q1c — LSV định lượng: chênh log PE top−bottom quintile g vs chênh tăng trưởng tương lai thật
    P("\n=== Q1c chênh top−bottom QUINTILE (trung bình theo tháng; f = tăng trưởng đối xứng tương lai/năm) ===")
    rows = []
    for w in ["gQ2", "g1", "g2", "g3", "g5", "acc"]:
        for per, m in (("IS", p.t.dt.year <= 2019), ("OOS", p.t.dt.year >= 2020)):
            acc = []
            for t, g in p[m].groupby("t"):
                g = g[[w, "logPE", "f1", "f2", w]].dropna(subset=[w, "logPE"])
                g = g.loc[:, ~g.columns.duplicated()]
                if len(g) < 50:
                    continue
                qn = pd.qcut(g[w].rank(method="first"), 5, labels=False)
                top, bot = g[qn == 4], g[qn == 0]
                acc.append([top[w].median() - bot[w].median(), top.logPE.median() - bot.logPE.median(),
                            top.f1.median() - bot.f1.median(), top.f2.median() - bot.f2.median()])
            a = np.nanmean(np.array(acc), axis=0)
            rows.append({"x": w, "per": per, "d_past_g": a[0], "d_logPE": a[1], "PE_ratio": np.exp(a[1]),
                         "d_f1": a[2], "d_f2_per_yr": a[3], "implied_dg_2y_per_yr": a[1] / 2})
    q = pd.DataFrame(rows)
    q.to_csv(os.path.join(OUT, "q1_lsv_quintile.csv"), index=False)
    P(q.round(3).to_string(index=False))
    P("\n(implied_dg_2y_per_yr ≈ Δlog PE / 2: mức tăng trưởng/năm TRONG 2 NĂM mà chênh PE hàm ý, xấp xỉ bậc 1)")


if __name__ == "__main__":
    main()
