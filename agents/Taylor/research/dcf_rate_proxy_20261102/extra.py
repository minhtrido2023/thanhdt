# -*- coding: utf-8 -*-
"""NGOÀI PREREG (mô tả): độ nhạy FV hôm nay theo dịch r; ERP hiệu chuẩn theo cửa sổ khác; hình r* vs proxy."""
import os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import analysis as A0           # noqa: E402
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt  # noqa: E402
OUT = A0.OUT
p = A0.load_panel(); last = (p.m == p.m.max()).values
f0 = A0.fv(p, 0.1225, 0.055)[last]; px = p.Price.values[last]
rows = []
for dr in (-1.0, 1.0, 2.0, 2.89):
    for g_follow in (0.0, 1.0):
        f = A0.fv(p, 0.1225 + dr / 100, 0.055 + g_follow * dr / 100)[last]
        ok = np.isfinite(f) & (f > 0) & np.isfinite(f0) & (f0 > 0)
        rows.append({"dr_pp": dr, "gT_follows": g_follow, "FV_med_vs_a": float(np.median(f[ok] / f0[ok]) - 1),
                     "pct_RE": float(((f[ok] - px[ok]) / f[ok] > 0).mean())})
S = pd.DataFrame(rows); S.to_csv(os.path.join(OUT, "sens_today_ngoai_prereg.csv"), index=False); print(S.round(4).to_string(index=False))
M = pd.read_csv(os.path.join(OUT, "monthly_series.csv"), index_col=0); M.index = pd.PeriodIndex(M.index, freq="M")
W = M.loc["2014-01":"2026-10"]
erp = [{"window": w, "erp_gb10": 12.25 - W.loc[w[0]:w[1], "gb10"].mean(), "r_today": 12.25 - W.loc[w[0]:w[1], "gb10"].mean() + W.at[pd.Period("2026-10"), "gb10"]}
       for w in (("2014-01", "2026-10"), ("2016-07", "2026-10"), ("2019-01", "2026-10"), ("2021-01", "2026-10"))]
E = pd.DataFrame(erp); E["window"] = E.window.map(lambda w: f"{w[0]}..{w[1]}"); E.to_csv(os.path.join(OUT, "erp_window_ngoai_prereg.csv"), index=False); print(E.round(3).to_string(index=False))
fig, ax = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
t = W.index.to_timestamp()
ax[0].plot(t, W.rstar, label="r* thị trường (median P/FV=1, g_T 5,5%)", color="k"); ax[0].axhline(12.25, ls="--", color="grey", label="r hằng 12,25%")
ax[0].plot(t, W.ey + 5, label="EY VNINDEX + 5pp", color="tab:purple", alpha=.7); ax[0].legend(fontsize=8); ax[0].set_ylabel("%")
for k, c in (("gb10", "tab:blue"), ("te_ib3m", "tab:orange"), ("dep1m", "tab:green"), ("dep12", "tab:red"), ("sbv_lo", "tab:brown")):
    ax[1].plot(t, W[k], label=k, color=c, lw=1.2)
ax[1].legend(fontsize=8, ncol=5); ax[1].set_ylabel("%/năm")
for a in ax:
    for s, e in (("2021-12", "2022-12"), ("2022-12", "2023-12"), ("2025-12", "2026-10")):
        a.axvspan(pd.Period(s).to_timestamp(), pd.Period(e).to_timestamp(), color="grey", alpha=.08)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "rstar_vs_proxies.png"), dpi=110)
