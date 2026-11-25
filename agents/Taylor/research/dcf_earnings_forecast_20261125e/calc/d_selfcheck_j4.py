# -*- coding: utf-8 -*-
"""d_selfcheck_j4.py — PRELOCK_J4 §5: tính lại số then chốt bằng đường code KHÁC.
(1) IC36 OOS P1 & M4 & EP (ALL) bằng vòng lặp tháng quý + scipy spearmanr; ΔIC36(M4−P1) dấu/độ lớn
(2) φ P1 bằng numpy.linalg.lstsq trên mẫu fit dựng lại bằng groupby/shift (khác merge của b_cycle_models)
(3) LOO: tính lại S1 cho 300 dòng ngẫu nhiên bằng lọc tường minh peer ≠ i
(4) PIT: known ≤ time mọi dòng sig_rows; (5) V3.2 không còn mc ảo ở ACG/ABI/TCB
Chạy dưới env -u TZ và TZ=Asia/Ho_Chi_Minh; output phải byte-giống."""
import os, sys, json
import numpy as np, pandas as pd
from scipy.stats import spearmanr
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."); ok_all = True
def chk(name, mine, art, tol):
    global ok_all; ok = abs(mine - art) <= tol; ok_all &= ok
    print(f"{'PASS' if ok else 'FAIL'} {name}: recompute={mine:.4f} artifact={art:.4f} tol={tol}")
# (1)
v = pd.read_parquet(os.path.join(D, "out_ALL", "vp2.parquet"), columns=["ticker", "ym", "in_universe", "lv_P1", "lv_M4", "ep", "fwd36_h50"])
v["p"] = pd.PeriodIndex(v.ym, freq="M"); v = v[v.in_universe & (v.p >= pd.Period("2020-01", "M")) & (v.p <= pd.Period("2023-10", "M")) & v.p.dt.month.isin([3, 6, 9, 12])]
res = {"lv_P1": [], "lv_M4": [], "ep": []}
for p, s in v.groupby("p"):
    bm = np.log(np.nanmean(np.exp(s.fwd36_h50)))
    for c in res:
        q = s[np.isfinite(s[c]) & np.isfinite(s.fwd36_h50)]
        if len(q) >= 30:
            res[c].append(spearmanr(q[c], q.fwd36_h50 - bm).correlation)
M = pd.read_csv(os.path.join(D, "out_ALL", "metrics2_J4.csv")); M = M[(M.scope == "ALL") & (M.era == "OOS")].set_index("model").ic36
for c, mname in (("lv_P1", "P1"), ("lv_M4", "M4"), ("ep", "EP")):
    chk(f"IC36 OOS {mname}", float(np.mean(res[c])), float(M[mname]), 5e-3)
dm = float(np.mean(res["lv_M4"]) - np.mean(res["lv_P1"])); V = json.load(open(os.path.join(D, "out_ALL", "J4_verdict.json")))
chk("dIC36 OOS M4-P1", dm, V["verdict"]["M4"]["OOS_dP1"], 2e-3)
chk("dIC36 OOS EP-P1 (EP>P1)", float(np.mean(res["ep"]) - np.mean(res["lv_P1"])), -V["P1_ref"]["OOS"]["EP"][0], 5e-3)
print("n_dates_OOS", len(res["lv_P1"]))
# (2)
vp = pd.read_parquet(os.path.join(D, "out_panel", "vp2.parquet"), columns=["ticker", "quarter", "known", "time", "roe", "roe_tc5", "in_universe"])
f = vp.sort_values("time").groupby(["ticker", "quarter"], as_index=False).first()
_pi = pd.PeriodIndex(f.quarter, freq="Q"); f["qn"] = _pi.year * 4 + _pi.quarter; f = f.sort_values(["ticker", "qn"])
idx = f.set_index(["ticker", "qn"])
def fut(h, col):
    k = list(zip(f.ticker, f.qn + h)); return idx.reindex(k)[col].values
f["r4"], f["k4"], f["r8"], f["k8"] = fut(4, "roe"), fut(4, "known"), fut(8, "roe"), fut(8, "known")
tc = f.roe_tc5.clip(-0.1, 0.4); f["g"] = (f.roe - tc).clip(-0.3, 0.3); f["y"] = ((f.r4 + f.r8) / 2 - tc).clip(-0.3, 0.3)
cut = pd.Timestamp("2020-01-01")
s = f[f.in_universe & f.known.dt.year.between(2014, 2019) & (pd.to_datetime(f.k4) < cut) & (pd.to_datetime(f.k8) < cut) & f.y.notna() & f.g.notna()]
phi = float(np.linalg.lstsq(s[["g"]].values, s.y.values, rcond=None)[0][0])
fitj = json.load(open(os.path.join(D, "out_ALL", "fit.json")))
chk("phi P1 (lstsq)", phi, fitj["coef"]["P1"][0], 1e-3); print("n_fit_recompute", len(s), "artifact", fitj["n_fit_rows"])
# (3)
sg = pd.read_parquet(os.path.join(D, "out_panel", "sig_rows.parquet"))
cand = sg[sg.S1.notna() & sg.icb.notna()].sample(300, random_state=20261125); bad = 0
for r in cand.itertuples():
    peers = sg[(sg.ym == r.ym) & (sg.icb == r.icb) & (sg.ticker != r.ticker) & sg.x1.notna()]
    if len(peers) < 5 or abs(np.median(peers.x1) - r.S1) > 1e-12:
        bad += 1
chk("LOO S1 mismatches (300 dòng)", float(bad), 0.0, 0.0)
# (4)
chk("PIT violations sig_rows", float((sg.known > sg.time).sum()), 0.0, 0.0)
# (5)
mf = json.load(open(os.path.join(D, "out_panel", "mc_fix32.json"))); cs = {(c["ticker"], c["ym"]): c for c in mf["cases"]}
for k in (("ACG", "2022-03"), ("ABI", "2025-07"), ("TCB", "2024-05")):
    c = cs[k]; chk(f"mc V3.2 {k[0]} {k[1]} |log(mc32/mc_old)|<0.1", float(abs(np.log(c["mc_v32_ty"] / c["mc_old_ty"])) < 0.1), 1.0, 0.0)
print("ALL_PASS" if ok_all else "SOME_FAIL"); sys.exit(0 if ok_all else 1)
