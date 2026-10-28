#!/usr/bin/env python3
"""Q1 + Q2 event-level trên 5.361 sự kiện LAG đã khoá — theo PREREG.md (md5 ba8a81f1…).

Cùng cache với nghiên cứu 10-21/10-22 (data/bq_cache, env phiên) để chân control tái hiện Y TB 4,551%.
Y = Close[e+25]/Open[e] − 1 (gộp, như các nghiên cứu trước). Cụm = mùa báo cáo (năm-quý Release).
Chạy: OMP_NUM_THREADS=1 BQ_LOCAL_CACHE=data/bq_cache /home/trido/thanhdt/wc_venv/bin/python lag_events.py
"""
import os, sys
import numpy as np
import pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
OUT = os.path.dirname(os.path.abspath(__file__))
EVF = f"{WC}/mike/agents/Taylor/research/lag_entry_window_width_20261021/exp_window_events.csv"
sys.path.insert(0, WC); os.chdir(WC)
sys.path.insert(0, OUT)
from simulate_holistic_nav import bq  # noqa: E402
from nav_overlay_stats import cluster_boot, holm  # noqa: E402

HOLD = 25
IRP_DIR = os.environ.get("IRP_DEP1M_DIR", "/tmp/irp_dep1m")
sys.path.insert(0, IRP_DIR); import idle_rate_proxy as irp  # noqa: E402

df = pd.read_csv(EVF, parse_dates=["release", "entry"])
N = len(df); assert N == 5361, N
df["Y"] = df["exA0"] / df["buyO0"] - 1
tks = ",".join(f"'{t}'" for t in sorted(df["ticker"].unique()))
px = bq(f"""SELECT t.ticker, t.time, t.Open, t.High, t.Low, t.Close FROM tav2_bq.ticker AS t
WHERE t.ticker IN ({tks}) AND t.time >= DATE '2012-10-01' AND t.Close > 0""")
px["time"] = pd.to_datetime(px["time"]); px = px.sort_values(["ticker", "time"])
by = {tk: g.reset_index(drop=True) for tk, g in px.groupby("ticker")}

rows = []
for _, r in df.iterrows():
    g = by[r["ticker"]]; t = g["time"].values
    k = int(np.searchsorted(t, np.datetime64(r["entry"]))); assert t[k] == np.datetime64(r["entry"])
    C, O, H, L = (g[c].values.astype(float) for c in ("Close", "Open", "High", "Low"))
    o = dict(VOL60=np.nan, RUN20=np.nan, DIST52=np.nan, GAP=np.nan, MAE=np.nan, open_chk=O[k] / r["buyO0"] - 1,
             exit_chk=(C[k + HOLD] / r["exA0"] - 1) if k + HOLD < len(C) else np.nan)
    o["MAE"] = L[k:min(k + HOLD, len(L) - 1) + 1].min() / O[k] - 1
    if k >= 61: o["VOL60"] = np.diff(np.log(C[k - 61:k])).std(ddof=1) * np.sqrt(250)
    if k >= 21: o["RUN20"] = C[k - 1] / C[k - 21] - 1
    if k >= 250: o["DIST52"] = C[k - 1] / H[k - 250:k].max() - 1
    R = C[k - 1]; o["GAP"] = O[k] / R - 1
    ex = r["exA0"]
    # R1 LIMIT2
    lim = R * 0.98; o["R1_st"], o["R1_px"] = "NOFILL", np.nan
    for j in range(3):
        if k + j < len(L) and L[k + j] <= lim:
            o["R1_st"], o["R1_px"] = "FILL", min(O[k + j], lim); break
    o["R2_st"] = "NOFILL" if o["GAP"] > 0.03 else "CONTROL"
    f = k + 1 if C[k] < R else k + 2
    o["R3_st"], o["R3_px"] = "FILL", O[f]
    o["exit_date"] = pd.Timestamp(t[k + HOLD]) if k + HOLD < len(t) else pd.NaT
    rows.append(o)
df = pd.concat([df, pd.DataFrame(rows)], axis=1)
_rate = np.asarray(irp.r_idle_series(df["entry"].dt.date, tier="dep1m"), float) / 100
df["IDLE"] = _rate * (df["exit_date"] - df["entry"]).dt.days / 365.0
df["season"] = df["release"].dt.year.astype(str) + "Q" + df["release"].dt.quarter.astype(str)
IS = (df["entry"].dt.year <= 2019).values; yrs = df["entry"].dt.year.values
print(f"[control] N={N} mã={df.ticker.nunique()} mùa={df.season.nunique()} | Y TB {df.Y.mean()*100:.3f}% (pin nghiên cứu 10-22: 4,551%) | "
      f"Open cache vs buyO0 |dev|>1bps: {(df.open_chk.abs()>1e-4).mean()*100:.2f}% | Close e+25 vs exA0 |dev|>1bps: {(df.exit_chk.abs()>1e-4).mean()*100:.2f}%")
print(f"[đặc trưng NaN] " + ", ".join(f"{c}={df[c].isna().sum()}" for c in ("VOL60", "RUN20", "DIST52", "GAP")))

# ---------------- Q1
print("\n[Q1 LAG-event] Δ = Y_biến_thể − Y_control (pp), CI cụm-mùa; không khớp ⇒ lãi nhàn rỗi (pin0=0 / pin1M=dep1m)")
top = df.Y.values >= np.quantile(df.Y.values, 2 / 3)
q1 = []
for rule in ("R1", "R2", "R3"):
    st = df[f"{rule}_st"].values
    for pin in ("pin0", "pin1M"):
        idle = np.zeros(N) if pin == "pin0" else df.IDLE.values
        yv = df.Y.values.copy()
        if rule != "R2":
            fill = st == "FILL"; yv[fill] = df.exA0.values[fill] / df[f"{rule}_px"].values[fill] - 1
        nof = st == "NOFILL"; yv[nof] = idle[nof]
        d = yv - df.Y.values
        est, ci, p, nc = cluster_boot(d, df.season.values)
        loyo = [d[yrs != y].mean() for y in np.unique(yrs)]
        impr = (1 - df[f"{rule}_px"].values / df.buyO0.values)[st == "FILL"] if rule != "R2" else np.array([np.nan])
        q1.append(dict(rule=rule, pin=pin, d=est, ci_lo=ci[0], ci_hi=ci[1], p=p, d_IS=d[IS].mean(), d_OOS=d[~IS].mean(),
                       loyo_min=min(loyo), loyo_max=max(loyo), nofill=nof.mean(), nofill_top=nof[top].mean(),
                       px_impr_bps=np.nanmean(impr) * 1e4, mean_Y_var=yv.mean()))
Q1 = pd.DataFrame(q1); Q1["holm"] = False
for pin in ("pin0", "pin1M"):
    m = Q1.pin == pin; Q1.loc[m, "holm"] = holm(Q1.loc[m, "p"].values)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
sh = Q1.copy()
for c in ("d", "ci_lo", "ci_hi", "d_IS", "d_OOS", "loyo_min", "loyo_max", "nofill", "nofill_top", "mean_Y_var"): sh[c] = (sh[c] * 100).round(3)
sh["px_impr_bps"] = sh["px_impr_bps"].round(1); sh["p"] = sh["p"].round(4)
print(sh.to_string(index=False))

# ---------------- Q2
cut = dict(VOL60=np.nanpercentile(df.loc[IS, "VOL60"], 80), RUN20=np.nanpercentile(df.loc[IS, "RUN20"], 80),
           DIST52=np.nanpercentile(df.loc[IS, "DIST52"], 20))
df["G_VOL"] = (df.VOL60 >= cut["VOL60"]).values; df["G_RUN"] = (df.RUN20 >= cut["RUN20"]).values
df["G_DEEP"] = (df.DIST52 <= cut["DIST52"]).values
df["HIT15"] = (df.MAE <= -0.15).astype(float)
print(f"\n[Q2 LAG-event] ngưỡng IS: VOL60≥{cut['VOL60']:.3f} RUN20≥{cut['RUN20']:.3f} DIST52≤{cut['DIST52']:.3f}")
q2 = []
for g in ("G_VOL", "G_RUN", "G_DEEP"):
    a = df[g].values.astype(bool)
    est, ci, p, nc = cluster_boot(df.HIT15.values, df.season.values, a, "diff")
    emae, cimae, _, _ = cluster_boot(df.MAE.values, df.season.values, a, "diff")
    ey, ciy, _, _ = cluster_boot(df.Y.values, df.season.values, a, "diff")
    loyo = [df.HIT15.values[a & (yrs != y)].mean() - df.HIT15.values[~a & (yrs != y)].mean() for y in np.unique(yrs)]
    h = df.HIT15.values
    q2.append(dict(group=g, n_grp=int(a.sum()), hit_grp=h[a].mean(), hit_rest=h[~a].mean(), d_hit=est, ci_lo=ci[0], ci_hi=ci[1], p=p,
                   d_IS=h[a & IS].mean() - h[~a & IS].mean(), d_OOS=h[a & ~IS].mean() - h[~a & ~IS].mean(),
                   loyo_min=min(loyo), loyo_max=max(loyo), mae_grp=df.MAE.values[a].mean(), mae_rest=df.MAE.values[~a].mean(),
                   d_mae=emae, d_mae_lo=cimae[0], d_mae_hi=cimae[1],
                   p5_grp=np.percentile(df.Y.values[a], 5), p5_rest=np.percentile(df.Y.values[~a], 5),
                   Y_grp=df.Y.values[a].mean(), Y_rest=df.Y.values[~a].mean(), dY=ey, dY_lo=ciy[0], dY_hi=ciy[1]))
Q2 = pd.DataFrame(q2); Q2["holm"] = holm(Q2.p.values)
Q2["c1"] = (Q2.d_hit > 0) & (Q2.ci_lo > 0); Q2["c2"] = (Q2.d_IS > 0) & (Q2.d_OOS > 0); Q2["c3"] = Q2.loyo_min > 0
sh = Q2.copy()
for c in sh.columns:
    if c not in ("group", "n_grp", "p", "holm", "c1", "c2", "c3"): sh[c] = (sh[c] * 100).round(2)
sh["p"] = sh["p"].round(4)
print(sh.to_string(index=False))
# P5 bootstrap Δ cho G_VOL (kết quả phụ PREREG §4)
a = df.G_VOL.values.astype(bool); us, ci_ = np.unique(df.season.values, return_inverse=True)
rng = np.random.default_rng(20261022); bs = []
for _ in range(2000):
    b = rng.integers(0, len(us), len(us)); w = np.bincount(b, minlength=len(us))[ci_].astype(int)
    y = np.repeat(df.Y.values, w); aa = np.repeat(a, w)
    bs.append(np.percentile(y[aa], 5) - np.percentile(y[~aa], 5))
print(f"[G_VOL] ΔP5 lợi suất = {(np.percentile(df.Y.values[a],5)-np.percentile(df.Y.values[~a],5))*100:.2f}pp CI95 cụm [{np.percentile(bs,2.5)*100:.2f}; {np.percentile(bs,97.5)*100:.2f}]")
inpit = None
df.to_csv(f"{OUT}/lag_events_features.csv", index=False, columns=["ticker", "release", "entry", "season", "Y", "MAE", "HIT15", "VOL60",
          "RUN20", "DIST52", "GAP", "G_VOL", "G_RUN", "G_DEEP", "R1_st", "R1_px", "R2_st", "R3_px"])
Q1.to_csv(f"{OUT}/q1_lag_events.csv", index=False); Q2.to_csv(f"{OUT}/q2_lag_events.csv", index=False)
print("[ghi] lag_events_features.csv, q1_lag_events.csv, q2_lag_events.csv")
