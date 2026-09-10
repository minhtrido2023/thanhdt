"""BUOC 3 — join efficiency + momentum-environment + ecology; 1 chart + 1 table."""
import os
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = os.path.dirname(os.path.abspath(__file__))
ann = pd.read_csv(os.path.join(D, "efficiency_annual.csv"))
icy = pd.read_csv(os.path.join(D, "momentum_ic_annual.csv"))
eco = pd.read_csv(os.path.join(D, "ecology_monthly.csv"), parse_dates=["ym"])
eco["year"] = eco.ym.dt.year
ecoy = eco.groupby("year").agg(foreign_share=("foreign_share", "mean"),
                               net_fx_ty=("net_foreign_vnd", lambda s: s.sum() / 1e9),
                               turnover_real_ty=("turnover_real_vnd", lambda s: s.mean() / 1e9)).reset_index()

t = (ann[["year", "vr2", "vr2_z", "vr5", "vr10", "hurst", "ac1_idx", "ac1_cs", "n_tickers", "vol_ann"]]
     .merge(icy[["year", "mom6", "mom12", "rev1"]], on="year", how="left")
     .merge(ecoy, on="year", how="left"))
t.to_csv(os.path.join(D, "amh_gauge_annual.csv"), index=False)
print("=== TABLE: amh_gauge_annual.csv ===")
print(t.round(4).to_string(index=False))

print("\n=== Descriptive co-movement (NOT a test — N is tiny, say so out loud) ===")
sub = t.dropna(subset=["foreign_share", "mom6"])
r, p = spearmanr(sub.foreign_share, sub.mom6)
print(f"foreign_share vs mom6 IC : rho={r:+.3f} p={p:.3f}  N={len(sub)} years (2018-2026) — descriptive only")
sub2 = t.dropna(subset=["ac1_cs", "mom6"])
r2, p2 = spearmanr(sub2.ac1_cs, sub2.mom6)
print(f"ac1_cs      vs mom6 IC : rho={r2:+.3f} p={p2:.3f}  N={len(sub2)} years — descriptive only")
sub3 = t.dropna(subset=["vol_ann", "mom6"])
r3, p3 = spearmanr(sub3.vol_ann, sub3.mom6)
print(f"vol_ann     vs mom6 IC : rho={r3:+.3f} p={p3:.3f}  N={len(sub3)} years — descriptive only")

# ---------------- chart ----------------
mon = pd.read_csv(os.path.join(D, "efficiency_monthly.csv"), parse_dates=["ym"])
mon = mon[mon.ym >= "2008-01-01"]
icm = pd.read_csv(os.path.join(D, "momentum_ic_monthly.csv"), parse_dates=["ym"])
icm = icm[icm.signal == "mom6"].set_index("ym")["ic"].rolling(12, min_periods=9).mean()

INK, MUTED, GRID = "#22303F", "#7A8896", "#E3E7EB"
A, B, C = "#2F6F9F", "#C1666B", "#6A9E5E"
fig, ax = plt.subplots(4, 1, figsize=(11, 12.5), sharex=True,
                       gridspec_kw={"height_ratios": [1, 1, 1, 1], "hspace": 0.22})
for a in ax:
    a.grid(True, color=GRID, lw=.7); a.set_axisbelow(True)
    for s in ("top", "right"): a.spines[s].set_visible(False)
    for s in ("left", "bottom"): a.spines[s].set_color(GRID)
    a.tick_params(colors=MUTED, labelsize=9)
    a.axvspan(pd.Timestamp("2010-01-01"), pd.Timestamp("2011-01-01"), color="#F2C14E", alpha=.18, lw=0)

ax[0].plot(mon.ym, mon.ac1_cs_median, color=A, lw=1.5)
ax[0].axhline(0, color=MUTED, lw=.8, ls="--")
ax[0].set_ylabel("AC(1) cross-sec\nmedian (12M)", color=INK, fontsize=9)
ax[0].set_title("VN market-efficiency gauge — CAUSAL trailing windows, monthly (diagnostic, NOT a trading signal)",
                color=INK, fontsize=12, loc="left", pad=12)
ax[0].annotate("structural break 2010\n(p_perm=0.0007, balanced cohort)", xy=(pd.Timestamp("2010-07-01"), 0.16),
               xytext=(pd.Timestamp("2012-06-01"), 0.19), fontsize=8.5, color=INK,
               arrowprops=dict(arrowstyle="->", color=MUTED, lw=.9))

ax[1].plot(mon.ym, mon.vr2, color=A, lw=1.3, label="VR(2)")
ax[1].plot(mon.ym, mon.vr10, color=C, lw=1.1, label="VR(10)")
ax[1].axhline(1, color=MUTED, lw=.8, ls="--")
ax[1].set_ylabel("Variance ratio\n(VNINDEX, 250d)", color=INK, fontsize=9)
ax[1].legend(frameon=False, fontsize=8.5, loc="upper right", labelcolor=INK, ncol=2)

ax[2].plot(mon.ym, mon.hurst, color=A, lw=1.3)
ax[2].axhline(.5, color=MUTED, lw=.8, ls="--")
ax[2].set_ylabel("Hurst (DFA, 500d)", color=INK, fontsize=9)

ax[3].plot(icm.index, icm.values, color=B, lw=1.7)
ax[3].axhline(0, color=MUTED, lw=.8, ls="--")
ax[3].set_ylabel("mom(6-1) IC vs fwd-3M\n12M mean", color=INK, fontsize=9)
ax[3].annotate("NO structural break (p_perm=0.22) — cyclical:\ntroughs 2008-10, 2014, 2020-23; back positive 2024/2026",
               xy=(pd.Timestamp("2021-06-01"), -0.05), xytext=(pd.Timestamp("2012-01-01"), -0.115),
               fontsize=8.5, color=INK, arrowprops=dict(arrowstyle="->", color=MUTED, lw=.9))
ax[3].set_xlabel("")
fig.text(.5, .045, "Source: tav2_bq.ticker + tav2_mike.universe_pit (BQ, asof 2026-09-10). "
                   "Shaded = located structural break. Estimators self-checked against iid / AR(1)±0.2 / DFA controls.",
         ha="center", color=MUTED, fontsize=8)
fig.savefig(os.path.join(D, "vn_efficiency_gauge.png"), dpi=150, bbox_inches="tight", facecolor="white")
print("\nchart -> vn_efficiency_gauge.png")
