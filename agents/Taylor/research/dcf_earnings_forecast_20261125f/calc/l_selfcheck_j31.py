# -*- coding: utf-8 -*-
"""l_selfcheck_j31.py — J3.1: tính lại số then chốt bằng đường code KHÁC (lặp tháng quý tự viết + scipy; lstsq-free cho KL2), so với artifact.
Chạy dưới env -u TZ và TZ=Asia/Ho_Chi_Minh; output phải byte-giống."""
import os, sys, hashlib
import numpy as np, pandas as pd
from scipy.stats import spearmanr
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."); J3 = os.path.join(F, "..", "dcf_earnings_forecast_20261125d"); ok_all = True
def chk(name, mine, art, tol):
    global ok_all; ok = abs(mine - art) <= tol; ok_all &= ok
    print(f"{'PASS' if ok else 'FAIL'} {name}: recompute={mine:.4f} artifact={art:.4f} tol={tol}")
# 0) panel đầu vào đúng V3.2 (md5 = ..e/out_panel/MD5_panel.txt) và ca ACG 2022-03 đã hết mc ảo trong panel đo
md5 = hashlib.md5(open(os.path.join(F, "in", "vp2.parquet"), "rb").read()).hexdigest(); ok = md5 == "a24678ff0a8b2166ac3328624cc0cd13"; ok_all &= ok
print(f"{'PASS' if ok else 'FAIL'} panel V3.2 md5={md5}")
for d in ("out_J3C", "out_CYC_CYC"):
    v = pd.read_parquet(os.path.join(F, d, "vp2.parquet"), columns=["ticker", "ym", "mc"]); x = v[(v.ticker == "ACG") & (v.ym.astype(str) == "2022-03")].mc.iloc[0] / 1e9
    chk(f"{d} ACG 2022-03 mc (tỷ, V3.2 = 9.018)", float(x), 9018.0, 1.0)
# 1) IC36 OOS trong CYC: D0 / C4 / EP — lặp tháng quý tự viết
v = pd.read_parquet(os.path.join(F, "out_CYC_CYC", "vp2.parquet"), columns=["ticker", "ym", "in_universe", "lv_D0", "lv_C4", "ep", "fwd36_h50"])
v["p"] = pd.PeriodIndex(v.ym, freq="M"); v = v[v.in_universe & (v.p >= pd.Period("2020-01", "M")) & (v.p <= pd.Period("2023-10", "M")) & v.p.dt.month.isin([3, 6, 9, 12])]
M = pd.read_csv(os.path.join(F, "out_CYC_CYC", "metrics2_C.csv"))
for mdl, col in (("D0", "lv_D0"), ("C4", "lv_C4"), ("EP", "ep")):
    out = []
    for p, s in v.groupby("p"):
        bm = np.log(np.nanmean(np.exp(s.fwd36_h50))); s = s[np.isfinite(s[col]) & np.isfinite(s.fwd36_h50)]
        if len(s) >= 30:
            out.append(spearmanr(s[col], s.fwd36_h50 - bm).correlation)
    art = M[(M.model == mdl) & (M.scope == "ALL") & (M.era == "OOS")].ic36.iloc[0]
    chk(f"CYC IC36 OOS {mdl} (n={len(out)})", float(np.mean(out)), art, 5e-3)
# 2) KL6: trong CYC, OOS E/P ≥ D0 (đọc từ metrics2) và số năm D0 > EP OOS từ dsr_cycle
d0, ep = (M[(M.model == m_) & (M.scope == "ALL") & (M.era == "OOS")].ic36.iloc[0] for m_ in ("D0", "EP")); ok = ep >= d0; ok_all &= ok
import json
by = json.load(open(os.path.join(F, "out_CYC_ALL", "dsr_cycle.json")))["CYC"]["D0-EP"]["by_year"]
print(f"{'PASS' if ok else 'FAIL'} KL6 CYC OOS EP {ep:.4f} >= D0 {d0:.4f}; D0>EP năm IS {sum(by[str(y)] > 0 for y in range(2014, 2020))}/6, OOS {sum(by[str(y)] > 0 for y in range(2020, 2024))}/4")
# 3) KL2: gap | ctrl4+nroe+nlv → u4 — phần dư hạng bằng phương trình chuẩn (np.linalg.solve) + scipy spearmanr, khác lstsq của k_kl2_check
g = pd.read_parquet(os.path.join(J3, "out_J3", "gapev.parquet")); K = pd.read_csv(os.path.join(F, "out_delta", "kl2_u4_ctrl.csv"))
ct = ["ep", "lsize", "roe_tc5", "mom", "nroe", "nlv"]
for era in ("IS", "OOS"):
    ics = []
    for _, s in g[g.era == era].groupby("qps"):
        s = s[np.isfinite(s[["gap", "u4"] + ct]).all(axis=1)]
        if len(s) < 30:
            continue
        X = np.column_stack([np.ones(len(s))] + [s[c].rank().values for c in ct]); y = s.gap.rank().values
        r = y - X @ np.linalg.solve(X.T @ X, X.T @ y); ics.append(spearmanr(r, s.u4).correlation)
    art = K[(K.era == era) & (K.ctrl == "ctrl4+nroe+nlv")].IC.iloc[0]
    chk(f"KL2 {era} IC(gap|ctrl4+nroe+nlv, u4)", float(np.mean(ics)), art, 5e-4)
print("ALL_PASS" if ok_all else "SOME_FAIL"); sys.exit(0 if ok_all else 1)
