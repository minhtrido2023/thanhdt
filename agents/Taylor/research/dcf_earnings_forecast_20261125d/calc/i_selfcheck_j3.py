# -*- coding: utf-8 -*-
"""i_selfcheck_j3.py — tính lại 4 số then chốt J3 bằng đường code KHÁC (scipy spearmanr / groupby thuần / lặp ngày tự viết), so với artifact.
Chạy: env -u TZ ... và TZ=Asia/Ho_Chi_Minh ...; output phải byte-giống."""
import os, sys
import numpy as np, pandas as pd
from scipy.stats import spearmanr
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."); ok_all = True
def chk(name, mine, art, tol):
    global ok_all; ok = abs(mine - art) <= tol; ok_all &= ok
    print(f"{'PASS' if ok else 'FAIL'} {name}: recompute={mine:.4f} artifact={art:.4f} tol={tol}")
# 1) B1null OOS: IC(nlv, cu) — scipy spearmanr theo quý (≥30), TB đều
g = pd.read_parquet(os.path.join(D, "out_J3", "gapev.parquet")); g = g[g.era == "OOS"]
ics = []
for _, s in g.groupby("qps"):
    s = s[np.isfinite(s[["nlv", "cu"]]).all(axis=1)]
    if len(s) >= 30:
        ics.append(spearmanr(s.nlv, s.cu).correlation)
R = pd.read_csv(os.path.join(D, "out_J3", "B_results.csv")); a = R[(R.era == "OOS") & (R.test == "B1null") & (R.x == "nlv") & (R.y == "cu")].IC.iloc[0]
chk("B1null OOS IC(nlv,cu)", float(np.mean(ics)), a, 5e-4)
# 2) A' OOS CYC_HI: thiên lệch trung vị D0imp ở PEAK / TROUGH — từ fc.parquet của b_forecast (đường J2) + đặc trưng chu kỳ, không dùng fc_cy
fc = pd.read_parquet(os.path.join(D, "out_J3", "fc.parquet")); fc = fc[(fc.h == 1) & fc.common & (fc.era == "OOS")]
cf = pd.read_parquet(os.path.join(D, "out_CY", "cyc_features.parquet"))[["ticker", "qps", "grp", "phase"]]
m = fc.merge(cf.rename(columns={"qps": "qp"}), on=["ticker", "qp"], how="left")
A2 = pd.read_csv(os.path.join(D, "out_CY", "A2_grp_phase.csv"))
for ph in ("PEAK", "TROUGH"):
    mine = float(m[(m.grp == "CYC_HI") & (m.phase == ph)].e_D0imp.median())
    art = A2[(A2.era == "OOS") & (A2.grp == "CYC_HI") & (A2.phase == ph)].bias_D0imp.iloc[0]
    chk(f"A' OOS CYC_HI {ph} bias D0imp", mine, art, 1e-6)
# 3) C' CYC: IC36 OOS của D0 — lặp tháng quý tự viết (excess = fwd36_h50 − log TB đều exp trên universe đã che), so metrics2
v = pd.read_parquet(os.path.join(D, "out_CYC_CYC", "vp2.parquet"), columns=["ticker", "ym", "in_universe", "lv_D0", "fwd36_h50"])
v["p"] = pd.PeriodIndex(v.ym, freq="M"); v = v[v.in_universe & (v.p >= pd.Period("2020-01", "M")) & (v.p <= pd.Period("2023-10", "M")) & v.p.dt.month.isin([3, 6, 9, 12])]
out = []
for p, s in v.groupby("p"):
    bm = np.log(np.nanmean(np.exp(s.fwd36_h50))); s = s[np.isfinite(s.lv_D0) & np.isfinite(s.fwd36_h50)]
    if len(s) >= 30:
        out.append(spearmanr(s.lv_D0, s.fwd36_h50 - bm).correlation)
M = pd.read_csv(os.path.join(D, "out_CYC_CYC", "metrics2_C.csv")); art = M[(M.model == "D0") & (M.scope == "ALL") & (M.era == "OOS")].ic36.iloc[0]
chk("C' CYC IC36 OOS D0", float(np.mean(out)), art, 5e-3)
print("n_dates_C3", len(out))
print("ALL_PASS" if ok_all else "SOME_FAIL"); sys.exit(0 if ok_all else 1)
