# -*- coding: utf-8 -*-
"""Case diagnostic VNM + panel PIT (PREREG §6). KHÔNG fit theo mã — chỉ hiển thị + reverse-DCF."""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common import DATA, OUT
import engine as E

P = print
pd.set_option("display.width", 250)
p = pd.read_parquet(os.path.join(DATA, "panel_monthly.parquet"))
m, base = E.base_valid(p)
p["ok"] = m & p.Price.notna()
p["base"] = base
REQ = ["VNM", "FPT", "MWG", "PNJ", "DGC", "GAS", "REE", "CTR", "DHG"]
# tiêu chí PIT khai trước
d = p[(p.t >= "2014-01-01")]
nT = d.t.nunique()
cov = d.groupby("ticker").t.nunique() / nT
okr = d.groupby("ticker").ok.mean()
nonfin = ~d.groupby("ticker").is_fin.max()
t0 = d[d.t == d.t.min()].copy()
t0["mcap"] = t0.Price * t0.OShares
top30 = set(t0[~t0.is_fin].nlargest(30, "mcap").ticker)
sel = sorted(t for t in top30 if cov.get(t, 0) >= 0.9 and okr.get(t, 0) >= 0.8 and nonfin.get(t, False))
P("panel PIT theo tiêu chí:", sel)
panel = sel + [t for t in REQ if t not in sel]
lab = {t: ("tiêu chí" if t in sel else "ngoài tiêu chí") for t in panel}
f = pd.read_parquet(os.path.join(DATA, "fv_variants.parquet"))
V0, VS0 = "V0 hiện tại (s.5 N5 gT5.5 r hằng)", "G s=0"
r = 0.1225
# đề xuất level: s=0 + gT 4,5% (Gordon một tầng) — tính trực tiếp, cùng công thức fv_path
gp = 0.045
f["FV_de_xuat"] = f.base * (1 + gp) / (r - gp) / f.OShares
F = f.base / f.OShares
f["g_impl_1stage"] = (r * f.Price - F) / (f.Price + F)           # P = F(1+g)/(r−g)
# r ngầm định với đường tăng trưởng V0
def r_impl(row):
    gT = 0.055
    graw = gT if np.isnan(row.g_raw) else row.g_raw
    ge = gT + 0.5 * (np.clip(graw, -0.02, 0.20) - gT)
    lo, hi = gT + 0.002, 0.60
    for _ in range(60):
        mid = (lo + hi) / 2
        v = E.fv_path(np.array([row.base]), np.full((1, 5), ge), gT, mid, np.array([row.OShares]))[0]
        lo, hi = (mid, hi) if v > row.Price else (lo, mid)
    return (lo + hi) / 2
c = f[f.ticker.isin(panel)].copy()
rs = []
for rw in c.itertuples():
    if np.isfinite(getattr(rw, "base")) and rw.base > 0 and rw.OShares > 0 and rw.Price > 0:
        rs.append(r_impl(rw))
    else:
        rs.append(np.nan)
c["r_impl_V0"] = rs
c = c.rename(columns={V0: "FV_V0", VS0: "FV_s0"})
cols = ["t", "ticker", "Price", "FV_V0", "FV_s0", "FV_de_xuat", "g_impl_1stage", "r_impl_V0", "g_raw", "beta_b1"]
c[cols].to_csv(os.path.join(OUT, "t4_case_panel.csv"), index=False)
rows = []
for tk in panel:
    g = c[c.ticker == tk]
    g = g[np.isfinite(g.FV_V0)]
    if len(g) == 0:
        rows.append({"ticker": tk, "nhóm": lab[tk], "n_tháng": 0})
        continue
    lr0 = np.log(g.Price / g.FV_V0)
    lr1 = np.log(g.Price / g.FV_de_xuat)
    last = g.iloc[-1]
    rows.append({"ticker": tk, "nhóm": lab[tk], "n_tháng": len(g), "P/FV_V0_med": np.exp(lr0.median()),
                 "P/FV_dexuat_med": np.exp(lr1.median()), "P/FV_dexuat_p10": np.exp(lr1.quantile(.1)),
                 "P/FV_dexuat_p90": np.exp(lr1.quantile(.9)), "g_impl_med": g.g_impl_1stage.median(),
                 "r_impl_V0_med": g.r_impl_V0.median(), "last_t": last.t.date(), "last_P": last.Price,
                 "last_FV_V0": last.FV_V0, "last_FV_dexuat": last.FV_de_xuat, "last_g_impl": last.g_impl_1stage,
                 "last_r_impl": last.r_impl_V0})
S = pd.DataFrame(rows)
S.to_csv(os.path.join(OUT, "t4_case_summary.csv"), index=False)
P(S.round(3).to_string(index=False))
# VNM theo năm
v = c[c.ticker == "VNM"].copy()
v["yr"] = v.t.dt.year
vy = v.groupby("yr").agg(P=("Price", "median"), FV_V0=("FV_V0", "median"), FV_dexuat=("FV_de_xuat", "median"),
                         g_impl=("g_impl_1stage", "median"), r_impl=("r_impl_V0", "median"), g_raw=("g_raw", "median"))
P("=== VNM theo năm (trung vị tháng)"); P(vy.round(3).to_string())
vy.to_csv(os.path.join(OUT, "t4_vnm_by_year.csv"))
# hình
n = len(panel)
cols_ = 4
fig, ax = plt.subplots(int(np.ceil(n / cols_)), cols_, figsize=(18, 3.2 * np.ceil(n / cols_)), squeeze=False)
for i, tk in enumerate(panel):
    a = ax[i // cols_][i % cols_]
    g = c[c.ticker == tk]
    a.plot(g.t, g.Price, color="black", lw=1.2, label="Giá (thô)")
    a.plot(g.t, g.FV_V0, color="#d62728", lw=1, label="FV hiện tại")
    a.plot(g.t, g.FV_de_xuat, color="#1f77b4", lw=1, label="FV đề xuất (s=0, gT 4,5%)")
    a.set_title(f"{tk} ({lab[tk]})", fontsize=9)
    a.set_yscale("log")
    a.tick_params(labelsize=7)
    if i == 0:
        a.legend(fontsize=7)
for j in range(n, ax.size):
    ax.flat[j].axis("off")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "t4_case_panel.png"), dpi=90)
P("png:", os.path.join(OUT, "t4_case_panel.png"))
