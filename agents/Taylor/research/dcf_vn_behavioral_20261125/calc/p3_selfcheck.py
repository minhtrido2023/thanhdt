# -*- coding: utf-8 -*-
"""p3_selfcheck.py — tự kiểm ĐỘC LẬP pilot (không import p1/p2). In PASS/FAIL; exit≠0 nếu có FAIL."""
import os, sys, json, glob
import numpy as np, pandas as pd, duckdb
WC = "/home/trido/thanhdt/WorkingClaude"; HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out")
V3 = f"{WC}/wt-dcf-v3-20261125/agents/Taylor/research/dcf_vn_redesign_20261125c"
ft = pd.read_parquet(f"{OUT}/feat.parquet"); res = json.load(open(f"{OUT}/pilot_results.json")); ok = True
def chk(name, cond, info=""):
    global ok; ok &= bool(cond); print(("PASS" if cond else "FAIL"), name, info)
c = duckdb.connect()
# 1) tính lại hi52/cgo/mom/rev1 bằng đường khác (vòng lặp thuần, từng mã) cho 4 mã × mọi tháng
pan = pd.read_parquet(f"{V3}/out_F/vp2.parquet", columns=["ticker", "ym", "N", "in_universe", "fwd12_h50", "lv_ENS2", "ep"])
pre = pd.read_csv(f"{V3}/out/px_pre2013_d.csv", parse_dates=["time"])
for tk in ["VNM", "HPG", "DGC", "VCS"]:
    a = c.execute(f"SELECT CAST(time AS DATE) AS time, Close, Volume FROM read_parquet('{WC}/data/bq_cache/ticker/*.parquet') WHERE ticker='{tk}' AND Close>0 ORDER BY time").df()
    a["time"] = pd.to_datetime(a.time); b = pre[(pre.ticker == tk) & (pre.time < a.time.min()) & (pre.Close > 0)][["time", "Close", "Volume"]]
    x = pd.concat([b, a]).sort_values("time").reset_index(drop=True); x["ym"] = x.time.dt.to_period("M").astype(str)
    nmap = pan[pan.ticker == tk].set_index("ym").N; x["N"] = x.ym.map(nmap); x["N"] = x.N.ffill().bfill()
    cl = x.Close.tolist(); vol = x.Volume.fillna(0).tolist(); N = x.N.tolist(); rp = cl[0]; out = {}
    for i in range(len(x)):
        if i > 0:
            t = min(max(vol[i] / N[i], 0), 1); rp = (1 - t) * rp + t * cl[i]
        hi = max(cl[max(0, i - 251):i + 1]) if i + 1 >= 120 else np.nan
        out[x.ym[i]] = (np.log(cl[i] / hi), np.log(cl[i] / rp) if i >= 250 else np.nan,
                        np.log(cl[i - 21] / cl[i - 252]) if i >= 252 else np.nan, np.log(cl[i] / cl[i - 21]) if i >= 21 else np.nan)
    f = ft[ft.ticker == tk].set_index("ym"); mx = 0.0; n = 0
    for ym, v in out.items():
        for j, col in enumerate(["hi52", "cgo", "mom", "rev1"]):
            w = f.at[ym, col]
            if np.isfinite(v[j]) or np.isfinite(w):
                mx = max(mx, abs(v[j] - w)) if (np.isfinite(v[j]) and np.isfinite(w)) else 9.9; n += 1
    chk(f"feat_recompute_{tk}", mx < 1e-9, f"n={n} max|Δ|={mx:.2e}")
# 2) PIT: cắt dữ liệu sau 2019-12-31 ⇒ đặc trưng tháng 2019-12 không đổi (VNM)
x2 = x  # VCS ở vòng cuối
xt = x2[x2.time <= "2019-12-31"]; cl = xt.Close.values
chk("pit_truncate_hi52_VCS_2019-12", abs(np.log(cl[-1] / cl[-252:].max()) - ft[(ft.ticker == "VCS") & (ft.ym == "2019-12")].hi52.iloc[0]) < 1e-9)
# 3) IC tính lại từ file dự báo bằng scipy; hiệu F−F0 khớp JSON
from scipy.stats import spearmanr
for h in (12, 24):
    P = pd.read_parquet(f"{OUT}/pilot_pred_h{h}.parquet")
    for era in ("IS", "OOS"):
        E = P[P.era == era]; d = [spearmanr(g.p_F, g.ydm)[0] - spearmanr(g.p_F0, g.ydm)[0] for _, g in E.groupby("mi")]
        chk(f"dIC_F_F0_h{h}_{era}", abs(np.mean(d) - res[f"h{h}"][era]["dic"]["F-F0"]["mean"]) < 1e-9, f"{np.mean(d):+.4f}")
        chk(f"ydm_zero_mean_h{h}_{era}", abs(E.groupby("mi").ydm.mean()).max() < 1e-9)
# 4) không rò nhãn: hệ số đóng băng h=12 chỉ dùng tháng ≤ 2018-12 (72 tháng từ 2013-01)
chk("frozen_months_h12", res["h12"]["n_coef_months_frozen"] == 72, str(res["h12"]["n_coef_months_frozen"]))
chk("frozen_months_h24", res["h24"]["n_coef_months_frozen"] == 60, str(res["h24"]["n_coef_months_frozen"]))
# 5) hệ số đóng băng F h=12 tái lập độc lập (OLS từng tháng, trung bình)
P = pan[pan.in_universe].merge(ft, on=["ticker", "ym"]).dropna(subset=["mom", "rev1", "ep", "lv_ENS2", "hi52", "cgo"])
fs = ["mom", "rev1", "ep", "lv_ENS2", "hi52", "cgo"]
for f in fs: P["r_" + f] = P.groupby("ym")[f].rank(pct=True) - 0.5
P = P.dropna(subset=["fwd12_h50"]); bs = []
for ym, g in P.groupby("ym"):
    if not ("2013-01" <= ym <= "2018-12") or len(g) < 30: continue
    y = g.fwd12_h50 - g.fwd12_h50.mean(); y = y.clip(y.quantile(0.01), y.quantile(0.99))
    import numpy.linalg as la
    bs.append(la.lstsq(g[["r_" + f for f in fs]].values, y.values, rcond=None)[0])
chk("coef_frozen_F_h12", np.abs(np.mean(bs, axis=0) - np.array(res["h12"]["coef_frozen"]["F"])).max() < 1e-9, str(np.round(np.mean(bs, axis=0), 3)))
# 6) không dùng cột cấm
src = open(os.path.join(HERE, "p1_features.py")).read() + open(os.path.join(HERE, "p2_pilot.py")).read()
chk("no_profit_cols", "profit_2W" not in src and "profit_1M" not in src and "bq_cache/ticker_prune" not in src)
print("ALL PASS" if ok else "HAS FAIL"); sys.exit(0 if ok else 1)
