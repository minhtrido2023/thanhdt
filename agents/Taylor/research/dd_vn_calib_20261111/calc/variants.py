# -*- coding: utf-8 -*-
"""variants.py — (e) chẩn đoán thành phần: tính lại FV từ thành phần đã lưu trong panel
(base FCFE, g_raw, gT_unc, osh) bằng đúng D._fv_per_share của engine, thay TỪNG tham số.
KHÔNG đổi dcf_valuation.py. Không tham số nào dùng giá làm đầu vào (giá chỉ dùng để CHẤM).

Lưới khai trước (PRELOCK): r {10.25,11.25,12.25,13.25} x gT cap {4.5,5.5,6.5} x shrink {.25,.5,.75}
x base {fcfe3y, fcfe5y}  = 72 trial. Thêm (khai NGOÀI prelock, đếm vào N trials): base earning-power
{np_ttm, blend 50/50 fcfe3y+np_ttm} x cùng lưới r/gT/shrink = 72 trial nữa => N=144.
Chọn trên IS (as-of 2016-2019) rồi đo OOS (2020+). Run: $DNA_PYEXE variants.py
"""
import os, sys, json, itertools
import numpy as np, pandas as pd
WC = "/home/trido/thanhdt/WorkingClaude"
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out")
sys.path.insert(0, WC)
import dcf_valuation as D
D.pin_oshares_source_fin(__file__)
os.chdir(HERE)

p = pd.read_parquet(os.path.join(OUT, "panel.parquet"))
p = p[p["ok"] & (p["rating"] <= 3)].copy().reset_index(drop=True)
fin = D._load_financials()
# NP TTM PIT (dòng fin mới nhất có time <= asof) — cùng dòng engine dùng
fin_by = {t: g for t, g in fin.groupby("ticker")}
npt = []
for r in p.itertuples():
    g = fin_by[r.ticker]; last = g[g["time"] <= r.asof].iloc[-1]
    assert pd.Timestamp(last["time"]) <= r.asof
    npt.append(np.nansum([last[c] for c in ("NP_P0", "NP_P1", "NP_P2", "NP_P3")]))
p["np_ttm"] = npt
BASES = {"fcfe3y": p.base_fcfe.values,
         "fcfe5y": ((p.cfoa5 + p.cfinv5) / 5.0).values,
         "np_ttm": p.np_ttm.values,
         "blend": 0.5 * p.base_fcfe.values + 0.5 * p.np_ttm.values}
gclamp = np.clip(p.g_raw.values, D.G_EXPLICIT_FLOOR, D.G_EXPLICIT_CAP)
P0 = p.P0.values; osh = p.osh.values
IS = (p["asof"].dt.year <= 2019).values
f36 = (p["full36"] == True).values
y36 = np.log(p.PN36.values / P0)
f60 = (p["full60"] == True).values


def fv_vec(base, r, cap, shrink):
    gT = np.minimum(p.gT_unc.values, cap)
    gT = np.where(r <= gT, r - 0.01, gT)
    gexp = gT + shrink * (gclamp - gT)
    out = np.full(len(p), np.nan)
    for i in range(len(p)):
        if base[i] > 0 and osh[i] > 0:
            out[i] = D._fv_per_share(base[i], gexp[i], gT[i], r, osh[i])
    return out


def metrics(fv, m):
    ok = m & np.isfinite(fv) & (fv > 0)
    lr = np.log(fv[ok] / P0[ok])
    o = {"n": int(ok.sum()), "med_FVP": float(np.exp(np.median(lr))), "sd_log": float(np.std(lr)),
         "iqr_log": float(np.subtract(*np.percentile(lr, [75, 25])))}
    k = ok & f36
    gap0 = np.abs(np.log(P0[k] / fv[k])); gapN = np.abs(np.log(p.PN36.values[k] / fv[k]))
    o["gap_ratio_36"] = float(np.median(gapN) / np.median(gap0))
    o["beta_36"] = float(np.polyfit(np.log(fv[k] / P0[k]), y36[k], 1)[0])
    o["rankcorr_36"] = float(pd.Series(np.log(fv[k] / P0[k])).rank().corr(pd.Series(y36[k]).rank()))
    k6 = ok & f60
    t60 = p.touch60.values  # touch đã tính theo FV gốc => tính lại theo FV mới bên dưới
    o["n36"] = int(k.sum())
    return o


# chạm-tâm 60m phải tính lại theo FV mới: cần min đường giá trong 60m => lưu tỉ lệ min/P0 1 lần
import duckdb
px = duckdb.connect().execute(f"""SELECT ticker, CAST(time AS DATE) AS time, Close FROM read_parquet('{WC}/data/bq_cache/ticker/*.parquet')
    WHERE time >= DATE '2016-01-01' AND Close > 0""").df()
px["time"] = pd.to_datetime(px["time"]); pxb = {t: g for t, g in px.groupby("ticker")}
minr60 = np.full(len(p), np.nan)
for i, r in enumerate(p.itertuples()):
    if r.full60 != True: continue
    g = pxb[r.ticker]; c0 = g[g.time == r.asof].Close.iloc[0]
    seg = g[(g.time >= r.asof) & (g.time <= r.asof + pd.DateOffset(months=60))]
    minr60[i] = seg.Close.min() / c0


def touch_metrics(fv, m):
    k = m & f60 & np.isfinite(fv) & (fv > 0)
    t = P0[k] * minr60[k] <= fv[k]
    need = fv[k] < P0[k]; deep = fv[k] < 0.7 * P0[k]
    return {"touch60": float(t.mean()), "touch60_FVltP": float(t[need].mean()) if need.any() else np.nan,
            "touch60_FVlt0.7P": float(t[deep].mean()) if deep.any() else np.nan, "frac_FVlt0.7P": float(deep.mean())}


rows = []
grid = itertools.product(BASES, (0.1025, 0.1125, 0.1225, 0.1325), (0.045, 0.055, 0.065), (0.25, 0.5, 0.75))
for b, r, cap, sh in grid:
    fv = fv_vec(BASES[b], r, cap, sh)
    for lab, m in (("IS", IS), ("OOS", ~IS), ("ALL", np.ones(len(p), bool))):
        o = {"base": b, "r": r, "gTcap": cap, "shrink": sh, "split": lab}
        o.update(metrics(fv, m)); o.update(touch_metrics(fv, m)); rows.append(o)
res = pd.DataFrame(rows)
# kiểm tra: biến thể production (fcfe3y, 12.25, 5.5, 0.5) phải khớp FV engine
fv_prod = fv_vec(BASES["fcfe3y"], 0.1225, 0.055, 0.5)
dev = np.nanmax(np.abs(fv_prod / p.FV.values - 1))
print("control vs engine max rel dev:", dev); assert dev < 1e-9
res.to_csv(os.path.join(OUT, "variants.csv"), index=False)
print("N trials =", len(res) // 3)
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200)
isr = res[res.split == "IS"].copy()
isr["k3_pass"] = (isr.gap_ratio_36 < 1) & (isr.beta_36 > 0)
isr["lvl"] = np.abs(np.log(isr.med_FVP))
print(isr.groupby("base")[["med_FVP", "sd_log", "iqr_log", "gap_ratio_36", "beta_36", "rankcorr_36", "touch60_FVltP"]].median().round(3))
# một-tham-số-một-lần quanh production
base = dict(base="fcfe3y", r=0.1225, gTcap=0.055, shrink=0.5)
for k, vals in (("r", (0.1025, 0.1125, 0.1225, 0.1325)), ("gTcap", (0.045, 0.055, 0.065)), ("shrink", (0.25, 0.5, 0.75)), ("base", tuple(BASES))):
    for v in vals:
        q = dict(base); q[k] = v
        sel = res[(res.base == q["base"]) & np.isclose(res.r, q["r"]) & np.isclose(res.gTcap, q["gTcap"]) & np.isclose(res.shrink, q["shrink"])]
        print(k, v, sel[["split", "med_FVP", "iqr_log", "gap_ratio_36", "beta_36", "touch60", "touch60_FVltP"]].round(3).to_dict("records"))
best = isr[isr.k3_pass].sort_values(["lvl", "iqr_log"]).head(8)
print("IS best (K3 pass, |log medFVP| nhỏ nhất):\n", best[["base", "r", "gTcap", "shrink", "med_FVP", "iqr_log", "gap_ratio_36", "beta_36", "touch60_FVltP"]].round(3))
