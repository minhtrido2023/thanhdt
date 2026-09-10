# -*- coding: utf-8 -*-
"""VONG 5 — phan ra o cap RO GROSS (chinh cai selector doi), tach khoi tang park/ADV cua NAV.
Nguon: basketret_<leg>.csv do basket_probe.py sinh (cache GHIM, da kiem tra tai lap byte-identical)."""
import numpy as np, pandas as pd
L = ["ctrl", "L1b", "P1d", "P2d", "P1r1", "P1r2", "P2r1", "P2r2"]
R = {t: pd.read_csv(f"basketret_{t}.csv", index_col=0, parse_dates=[0])["ret"] for t in L}
idx = R["ctrl"].index; yrs = (idx[-1] - idx[0]).days / 365.25
def m(t):
    s = R[t]; lv = (1 + s).cumprod()
    return dict(level=float(lv.iloc[-1]), cagr=100 * (float(lv.iloc[-1]) ** (1 / yrs) - 1),
                maxdd=100 * float((lv / lv.cummax() - 1).min()), vol=100 * s.std() * np.sqrt(252),
                sharpe=s.mean() / s.std() * np.sqrt(252))
T = pd.DataFrame({t: m(t) for t in L}).T
T["d_cagr"] = T.cagr - T.loc["ctrl", "cagr"]; T["d_maxdd"] = T.maxdd - T.loc["ctrl", "maxdd"]
print("=== RO GROSS (khong tien mat, khong park sizing, khong phi) ==="); print(T.round(3).to_string())
T.to_csv("gross_metrics.csv")
tot = T.loc["L1b", "d_cagr"]
for lab, a, b in [("CHINH mode=top", T.loc["P1d", "d_cagr"], T.loc["P2d", "d_cagr"]),
                  ("PHU  mode=random", (T.loc["P1r1", "d_cagr"] + T.loc["P1r2", "d_cagr"]) / 2,
                                       (T.loc["P2r1", "d_cagr"] + T.loc["P2r2", "d_cagr"]) / 2)]:
    print(f"\n{lab}: TONG {tot:+.3f}pp = dP1 {a:+.3f} ({100*a/tot:+.1f}%) + dP2 {b:+.3f} "
          f"({100*b/tot:+.1f}%) + tuongtac {tot-a-b:+.3f} ({100*(tot-a-b)/tot:+.1f}%)")
# block bootstrap chung tren log-return gross
lg = {t: np.log1p(R[t].values) for t in L}
n = len(idx); B, BL = 4000, 63; rng = np.random.default_rng(20260910); nb = int(np.ceil(n / BL))
o = {k: [] for k in ["TOT", "dP1", "dP2", "inter"]}
for _ in range(B):
    st = rng.integers(0, n, nb); ii = np.concatenate([(np.arange(s, s + BL) % n) for s in st])[:n]
    f = lambda t: (lg[t][ii].sum() - lg["ctrl"][ii].sum()) / yrs * 100
    t_, a, b = f("L1b"), f("P1d"), f("P2d")
    o["TOT"].append(t_); o["dP1"].append(a); o["dP2"].append(b); o["inter"].append(t_ - a - b)
O = pd.DataFrame(o)
print("\n=== block bootstrap CHUNG tren RO GROSS (L=63, B=4000; pp/nam, log-return) ===")
print(pd.DataFrame({"diem": O.mean(), "p2.5": O.quantile(.025), "p50": O.median(),
                    "p97.5": O.quantile(.975), "P(>0)": (O > 0).mean()}).round(3).to_string())
print(f"\n  P(dP1 < 0) = {float((O.dP1 < 0).mean()):.3f}   P(dP2 > dP1) = {float((O.dP2 > O.dP1).mean()):.3f}")
