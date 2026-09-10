# -*- coding: utf-8 -*-
"""VONG 5 — do DO KHONG CHAC CHAN cua chinh phep phan ra (PREREG §1).
Block bootstrap CHUNG chi so (cung block cho moi chan) => dP1, dP2, tuong tac va cac ty le %TONG
duoc resample NHAT QUAN. Khong phai mot 'trial' moi: chi la sai so cua con so da bao cao."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from dsr_pbo_annex import load_nav, daily_logret

_D = ("/home/trido/thanhdt/WorkingClaude/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge"
      "_etfliqcustompitg_wtnamecap_advprice_univpit")
p = lambda t: f"{_D}_exp_c30vpb{t.lower()}.csv"
nav = {t: load_nav(p(t)) for t in ["ctrl", "L1b", "P1d", "P2d", "P1r1", "P1r2", "P2r1", "P2r2"]}
lr = lambda t: pd.Series(daily_logret(nav[t]), index=nav[t].index[1:])
rc = lr("ctrl")
yrs = (nav["ctrl"].index[-1] - nav["ctrl"].index[0]).days / 365.25
D = {t: (lr(t) - rc).dropna().values for t in nav if t != "ctrl"}
n = len(D["L1b"]); L, Bn = 63, 4000
rng = np.random.default_rng(20260910); nb = int(np.ceil(n / L))
out = {k: [] for k in ["TOT", "dP1", "dP2", "inter", "dP1r", "dP2r", "interR"]}
for b in range(Bn):
    st = rng.integers(0, n, nb)
    idx = np.concatenate([(np.arange(s, s + L) % n) for s in st])[:n]
    f = lambda t: D[t][idx].sum() / yrs * 100
    tot, d1, d2 = f("L1b"), f("P1d"), f("P2d")
    d1r, d2r = (f("P1r1") + f("P1r2")) / 2, (f("P2r1") + f("P2r2")) / 2
    out["TOT"].append(tot); out["dP1"].append(d1); out["dP2"].append(d2); out["inter"].append(tot - d1 - d2)
    out["dP1r"].append(d1r); out["dP2r"].append(d2r); out["interR"].append(tot - d1r - d2r)
O = pd.DataFrame(out)
print("=== BOOTSTRAP CHUNG (block 63 phien, B=4000, cung chi so cho moi chan) — pp/nam ===")
print(pd.DataFrame({"diem": O.mean(), "p2.5": O.quantile(.025), "p50": O.median(),
                    "p97.5": O.quantile(.975), "P(>0)": (O > 0).mean()}).round(3).to_string())
print("\n=== TY LE %TONG (chi tinh tren cac lan bootstrap co TONG > 0.5pp de ty le co nghia) ===")
m = O.TOT > 0.5
for a, b_, lab in [("dP1", "dP2", "CHINH mode=top"), ("dP1r", "dP2r", "PHU mode=random")]:
    s1 = 100 * O.loc[m, a] / O.loc[m, "TOT"]; s2 = 100 * O.loc[m, b_] / O.loc[m, "TOT"]
    si = 100 - s1 - s2
    print(f"  {lab:16s} n={int(m.sum())}/{Bn}  "
          f"%P1 med {s1.median():6.1f} CI[{s1.quantile(.025):7.1f},{s1.quantile(.975):6.1f}]  "
          f"%P2 med {s2.median():6.1f} CI[{s2.quantile(.025):7.1f},{s2.quantile(.975):6.1f}]  "
          f"%tuongtac med {si.median():6.1f}")
print("\n=== P(dP2 > dP1) — cau hoi (Y) manh hon (X) hay khong ===")
print(f"  mode=top    : {float((O.dP2 > O.dP1).mean()):.3f}")
print(f"  mode=random : {float((O.dP2r > O.dP1r).mean()):.3f}")
