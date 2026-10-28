#!/usr/bin/env python3
"""Phân loại phản ứng giá quanh công bố cho candidate LAG — event study theo PREREG.md (md5 0af5bd9d…).

Tập sự kiện = research/lag_entry_window_width_20261021/exp_window_events.csv (5.361 dòng, không dựng lại).
Chỉ bộ lọc LOẠI BỎ, 14 trials. Thống kê cụm theo mùa báo cáo (năm-quý của Release_Date).
Chạy (threads=1): OMP_NUM_THREADS=1 /home/trido/thanhdt/wc_venv/bin/python reaction_study.py
"""
import os, sys, itertools
import numpy as np
import pandas as pd
from scipy.stats import norm

WC = "/home/trido/thanhdt/WorkingClaude"
OUT = os.path.dirname(os.path.abspath(__file__))
EVF = f"{WC}/mike/agents/Taylor/research/lag_entry_window_width_20261021/exp_window_events.csv"
sys.path.insert(0, WC); os.chdir(WC)
from simulate_holistic_nav import bq  # noqa: E402

HOLD, ENTRY_OFF, TAU = 25, 5, 0.03
SEED, NB = 20261022, 2000
IRP_DIR = os.environ.get("IRP_DEP1M_DIR", "/tmp/irp_dep1m")  # idle_rate_proxy.py @aaed41eec (tier dep1m)

df = pd.read_csv(EVF, parse_dates=["release", "entry"])
N = len(df)
assert N == 5361, N
df["Y"] = df["exA0"] / df["buyO0"] - 1

# ---------------- panel giá (adj) + VNINDEX gốc
tks = ",".join(f"'{t}'" for t in sorted(df["ticker"].unique()) + ["VNINDEX"])
px = bq(f"""SELECT t.ticker, t.time, t.Open, t.High, t.Close, t.Volume
FROM tav2_bq.ticker AS t WHERE t.ticker IN ({tks}) AND t.time >= DATE '2012-10-01' AND t.Close > 0""")
px["time"] = pd.to_datetime(px["time"]); px = px.sort_values(["ticker", "time"]).reset_index(drop=True)
vni = px[px["ticker"] == "VNINDEX"].set_index("time")["Close"]
by = {tk: g.reset_index(drop=True) for tk, g in px[px["ticker"] != "VNINDEX"].groupby("ticker")}
print(f"[panel] {len(px):,} dòng; VNINDEX {len(vni)} phiên {vni.index.min().date()}→{vni.index.max().date()}")


def vr(a, b):
    """lợi suất VNINDEX từ close ngày a tới close ngày b (gần nhất ≤)."""
    va = vni.asof(a); vb = vni.asof(b)
    return vb / va - 1


feat = []
for _, r in df.iterrows():
    g = by[r["ticker"]]; t = g["time"].values
    e = int(np.searchsorted(t, np.datetime64(r["entry"])))
    assert t[e] == np.datetime64(r["entry"])
    d0 = int(np.searchsorted(t, np.datetime64(r["release"])))       # phiên đầu ≥ Release
    C, O, H, V = g["Close"].values, g["Open"].values, g["High"].values, g["Volume"].values.astype(float)
    o = dict(REACT=np.nan, GAP=np.nan, AVOL=np.nan, PRERUN=np.nan, DIST52=np.nan, PEAK=np.nan, Y_ex=np.nan)
    tt = pd.to_datetime(t)
    if d0 >= 1 and d0 <= e - 1:
        o["REACT"] = (C[e - 1] / C[d0 - 1] - 1) - vr(tt[d0 - 1], tt[e - 1])
        o["GAP"] = O[d0] / C[d0 - 1] - 1
        o["PEAK"] = max((C[j] / C[d0 - 1] - 1) - vr(tt[d0 - 1], tt[j]) for j in range(d0, e))
    if d0 >= 20:
        m = V[d0 - 20:d0].mean()
        o["AVOL"] = V[d0] / m if m > 0 else np.nan
    if d0 >= 21:
        o["PRERUN"] = (C[d0 - 1] / C[d0 - 21] - 1) - vr(tt[d0 - 21], tt[d0 - 1])
    if e >= 250:
        o["DIST52"] = C[e - 1] / H[e - 250:e].max() - 1
    if e + HOLD < len(C):
        o["Y_ex"] = r["Y"] - vr(tt[e - 1], tt[e + HOLD])
    o["gap_d0_e"] = e - d0
    o["exit_date"] = tt[e + HOLD] if e + HOLD < len(C) else pd.NaT
    feat.append(o)
df = pd.concat([df, pd.DataFrame(feat)], axis=1)

sys.path.insert(0, IRP_DIR); import idle_rate_proxy as irp  # noqa: E402
assert "dep1m" in irp.TIERS
_rate = irp.r_idle_series(df["entry"].dt.date, tier="dep1m") / 100
df["IDLE"] = _rate * (df["exit_date"] - df["entry"]).dt.days / 365.0   # pin1M: lãi 1M trả cho tiền nằm im cả kỳ

# lớp 3 dạng (ngưỡng 5% chốt trong PREREG)
cls = np.full(N, "FLAT", dtype=object)
R, P = df["REACT"].values, df["PEAK"].values
cls[R >= 0.05] = "UP_FULL"
cls[(R <= -0.05)] = "DOWN"
utd = (P >= 0.05) & (R <= P - 0.05) & (R < 0.05)
cls[utd] = "UP_THEN_DOWN"
cls[np.isnan(R)] = "NA"
df["CLASS"] = cls

# Y_live: W3·Luật A·ANCH cơ sở Open (sao y event_ret_open của harness 10-21)
def event_ret_open(W):
    out = np.zeros(N); filled = np.zeros(N, bool)
    for k in range(W):
        O_, L_, f_ = df[f"Or{k}"].values, df[f"Lr{k}"].values, df[f"f{k}"].values
        c = df[f"ref{k}"].values * (1 + TAU)
        can = ~df[f"lock{k}"].values & (L_ <= c + 1e-9)
        b = np.where(O_ <= c, O_, c) / f_
        new = can & ~filled
        out[new] = df["exA0"].values[new] / b[new] - 1; filled |= new
    return out
df["Y_live"] = event_ret_open(3)

# universe_pit (độ nhạy): in_universe tại phiên e−1, ruleset mới nhất
try:
    up = bq(f"""SELECT u.ticker, u.time, u.in_universe FROM tav2_mike.universe_pit AS u
    WHERE u.ruleset_version = (SELECT MAX(ruleset_version) FROM tav2_mike.universe_pit)
    AND u.ticker IN ({tks})""")
    up["time"] = pd.to_datetime(up["time"])
    upk = {(a, b): c for a, b, c in zip(up["ticker"], up["time"], up["in_universe"])}
    prev = []
    for _, r in df.iterrows():
        t = by[r["ticker"]]["time"].values
        e = int(np.searchsorted(t, np.datetime64(r["entry"])))
        prev.append(upk.get((r["ticker"], pd.Timestamp(t[e - 1]))))
    df["in_pit"] = prev
except Exception as ex:  # noqa: BLE001
    print(f"[universe_pit] KHÔNG đọc được: {ex}")
    df["in_pit"] = None

# ---------------- cụm
df["season"] = df["release"].dt.year.astype(str) + "Q" + df["release"].dt.quarter.astype(str)
IS = (df["entry"].dt.year <= 2019).values
yrs = df["entry"].dt.year.values
FEATS = ["REACT", "GAP", "AVOL", "PRERUN", "DIST52"]
cuts = {f: np.nanpercentile(df.loc[IS, f], [100 / 3, 200 / 3]) for f in FEATS}
cfgs = []
for f in FEATS:
    x = df[f].values
    cfgs.append((f"{f}:loại_THẤP", ~np.isnan(x) & (x <= cuts[f][0])))
    cfgs.append((f"{f}:loại_CAO", ~np.isnan(x) & (x >= cuts[f][1])))
for c in ("UP_FULL", "UP_THEN_DOWN", "DOWN", "FLAT"):
    cfgs.append((f"CLASS:loại_{c}", (df["CLASS"] == c).values))
assert len(cfgs) == 14


def make_boot(mask=None):
    sub = np.ones(N, bool) if mask is None else mask
    s = df.loc[sub, "season"].values
    us, ci = np.unique(s, return_inverse=True)
    rng = np.random.default_rng(SEED)
    return sub, ci, len(us), [rng.integers(0, len(us), len(us)) for _ in range(NB)]


def delta_stats(y, excl, boot):
    sub, ci, ns, B = boot
    y, ex = y[sub], excl[sub]
    sE = np.bincount(ci, weights=y * ex, minlength=ns); nE = np.bincount(ci, weights=ex.astype(float), minlength=ns)
    sK = np.bincount(ci, weights=y * ~ex, minlength=ns); nK = np.bincount(ci, weights=(~ex).astype(float), minlength=ns)
    d = sE.sum() / nE.sum() - sK.sum() / nK.sum()
    bs = np.array([sE[b].sum() / max(nE[b].sum(), 1) - sK[b].sum() / max(nK[b].sum(), 1) for b in B])
    p = 2 * min((bs >= 0).mean(), (bs <= 0).mean())
    return d, np.percentile(bs, [2.5, 97.5]), min(p, 1.0)


full = make_boot()
print(f"\n[N] sự kiện={N} | mã={df['ticker'].nunique()} | ngày công bố={df['release'].nunique()} | "
      f"mùa (N độc lập)={full[2]} | IS {IS.sum()} / OOS {(~IS).sum()}")
print(f"[đặc trưng NaN] " + ", ".join(f"{f}={df[f].isna().sum()}" for f in FEATS))
print(f"[cắt tercile IS] " + "; ".join(f"{f}=[{cuts[f][0]:.4f},{cuts[f][1]:.4f}]" for f in FEATS))
print(f"[lớp] {df['CLASS'].value_counts().to_dict()}")
print(f"[d0→e] phân bố số phiên: {df['gap_d0_e'].value_counts().sort_index().to_dict()}")
print(f"[Y] mean toàn bộ {df['Y'].mean()*100:.3f}% | Y_live {df['Y_live'].mean()*100:.3f}% | Y_ex {np.nanmean(df['Y_ex'])*100:.3f}%")

# mô tả: Y theo tercile mỗi đặc trưng + theo lớp
print("\n[mô tả] mean Y (%) theo tercile (cắt IS) | n")
for f in FEATS:
    x = df[f].values
    b = np.where(np.isnan(x), -1, np.digitize(x, cuts[f]))
    print(f"  {f:<7}" + "  ".join(f"T{k+1}: {df['Y'].values[b==k].mean()*100:6.2f} (n={int((b==k).sum())})" for k in range(3)))
for c in ("UP_FULL", "UP_THEN_DOWN", "DOWN", "FLAT", "NA"):
    m = (df["CLASS"] == c).values
    if m.any():
        print(f"  CLASS {c:<13} Y={df['Y'].values[m].mean()*100:6.2f}%  Y_live={df['Y_live'].values[m].mean()*100:6.2f}%  "
              f"Y_ex={np.nanmean(df['Y_ex'].values[m])*100:6.2f}%  n={m.sum()}")

# ---------------- bảng chính
season = df["season"].values
seas_u = np.unique(season)
rows = []
for name, ex in cfgs:
    y = df["Y"].values
    d, ci, p = delta_stats(y, ex, full)
    dIS = y[ex & IS].mean() - y[~ex & IS].mean(); dOOS = y[ex & ~IS].mean() - y[~ex & ~IS].mean()
    loyo = [y[ex & (yrs != k)].mean() - y[~ex & (yrs != k)].mean() for k in np.unique(yrs)]
    # capacity: % mùa mà bộ lọc loại >50% candidate
    frac_s = pd.Series(ex).groupby(season).mean()
    # độ nhạy
    dl, cil, _ = delta_stats(df["Y_live"].values, ex, full)
    yx = df["Y_ex"].values; okx = ~np.isnan(yx)
    dx = yx[ex & okx].mean() - yx[~ex & okx].mean()
    pit = (df["in_pit"] == True).values  # noqa: E712
    dp = y[ex & pit].mean() - y[~ex & pit].mean() if pit.any() else np.nan
    rows.append(dict(cfg=name, n_excl=int(ex.sum()), pct_excl=ex.mean(), mean_excl=y[ex].mean(), mean_kept=y[~ex].mean(),
                     delta=d, ci_lo=ci[0], ci_hi=ci[1], p=p, d_IS=dIS, d_OOS=dOOS, loyo_min=min(loyo), loyo_max=max(loyo),
                     seasons_gt50=(frac_s > 0.5).mean(), d_live=dl, d_live_ci_lo=cil[0], d_live_ci_hi=cil[1], d_ex=dx, d_pit=dp))
T = pd.DataFrame(rows)
# Holm
order = np.argsort(T["p"].values); m = len(T); holm = np.zeros(m, bool); stop = False
for i, j in enumerate(order):
    if not stop and T["p"].values[j] <= 0.05 / (m - i):
        holm[j] = True
    else:
        stop = True
T["holm"] = holm
T["c1"] = (T["delta"] < 0) & (T["ci_hi"] < 0)
T["c2"] = (T["d_IS"] < 0) & (T["d_OOS"] < 0)
T["c3"] = T["loyo_max"] < 0
T["idle_excl"] = [df["IDLE"].values[ex].mean() for _, ex in cfgs]
T["c5"] = T["mean_excl"] < T["idle_excl"]

# DSR + PBO trên lợi ích theo mùa: b_s = mean(Y giữ lại) − mean(Y toàn bộ) trong mùa s
Ys = pd.Series(df["Y"].values)
allm = Ys.groupby(season).mean()
B = pd.DataFrame({name: Ys[~ex].groupby(season[~ex]).mean().reindex(seas_u) - allm.reindex(seas_u) for name, ex in cfgs})
B = B.fillna(0.0)
SR = B.mean() / B.std(ddof=1)
best = T.loc[T["delta"].idxmin(), "cfg"]
x = B[best].values; Tn = len(x); sr = SR[best]
from scipy.stats import skew, kurtosis
g3, g4 = skew(x), kurtosis(x, fisher=False)
emc = 0.5772156649
sr0 = np.sqrt(SR.var(ddof=1)) * ((1 - emc) * norm.ppf(1 - 1 / m) + emc * norm.ppf(1 - 1 / (m * np.e)))
dsr = norm.cdf((sr - sr0) * np.sqrt(Tn - 1) / np.sqrt(1 - g3 * sr + (g4 - 1) / 4 * sr ** 2))
# PBO CSCV: metric = mean(Y giữ lại) theo khối mùa
K = pd.DataFrame({name: Ys[~ex].groupby(season[~ex]).mean().reindex(seas_u) for name, ex in cfgs}).fillna(0.0)
blocks = np.array_split(np.arange(len(seas_u)), 10)
lam = []
for comb in itertools.combinations(range(10), 5):
    isx = np.concatenate([blocks[i] for i in comb]); oosx = np.concatenate([blocks[i] for i in range(10) if i not in comb])
    bi = K.iloc[isx].mean().values.argmax()
    oo = K.iloc[oosx].mean().values
    w = (oo < oo[bi]).sum() / (m - 1)  # hạng tương đối OOS của cấu hình IS-best (0=tệ nhất, 1=tốt nhất)
    w = min(max(w, 1e-6), 1 - 1e-6)
    lam.append(np.log(w / (1 - w)))
pbo = float((np.array(lam) <= 0).mean())

pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
show = T.copy()
for c in ("pct_excl", "mean_excl", "mean_kept", "delta", "ci_lo", "ci_hi", "d_IS", "d_OOS", "loyo_min", "loyo_max",
          "seasons_gt50", "idle_excl", "d_live", "d_live_ci_lo", "d_live_ci_hi", "d_ex", "d_pit"):
    show[c] = (show[c] * 100).round(2)
show["p"] = show["p"].round(4)
print("\n[BẢNG CHÍNH] Δ = mean(Y|loại) − mean(Y|giữ), đơn vị pp; CI cụm-mùa; tiêu chí PREREG §7")
print(show.to_string(index=False))
print(f"\n[DSR] cấu hình Δ âm nhất = {best}: SR/mùa={sr:.3f}, SR0={sr0:.3f}, T={Tn}, skew={g3:.2f}, kurt={g4:.2f} → DSR={dsr:.3f}")
print(f"[PBO] CSCV S=10 (252 tổ hợp), 14 cấu hình → PBO={pbo:.3f}")
print(f"[idle pin1M] TB lãi nhàn rỗi dep1m trên kỳ nắm: {df['IDLE'].mean()*100:.3f}% (ĐO, idle_rate_proxy dep1m PIT)")
pit_ok = (df["in_pit"] == True).sum(); pit_na = df["in_pit"].isna().sum()  # noqa: E712
print(f"[universe_pit] in_universe tại e−1: {pit_ok} / {N} (thiếu dòng {pit_na})")
T.to_csv(f"{OUT}/filter_grid.csv", index=False)
df[["ticker", "release", "entry", "season", "Y", "Y_live", "Y_ex", "REACT", "GAP", "AVOL", "PRERUN", "DIST52", "PEAK",
    "CLASS", "in_pit"]].to_csv(f"{OUT}/event_features.csv", index=False)
