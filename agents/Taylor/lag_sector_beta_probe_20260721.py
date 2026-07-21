# -*- coding: utf-8 -*-
"""
lag_sector_beta_probe_20260721.py — job Taylor_20260721_133858 (phần 2)

Phần 1 (lag_sector_split_20260721.py) cho kết quả NGƯỢC giả thuyết user ở mức
trung bình (BROKER excess +6.3% vs MANUF +2.1%), nhưng IC(surprise) của BROKER
≈ 0 (không có ý nghĩa) trong khi MANUF +0.136 (p<1e-4) — tức "xổ số" đúng ở
chỗ ĐỘ LỚN surprise không dự báo được, sai ở chỗ mức edge trung bình.

Script này kiểm tra xem edge trung bình của BROKER có phải là ARTEFACT BETA
(cổ phiếu CTCK beta cao, mẫu 2020+ toàn thị trường tăng => vượt VNINDEX một
cách cơ học) hay là alpha thật:
  A. clustered SE theo quý (event CTCK tương quan cực mạnh — cùng ngày ra BCTC,
     cùng cửa sổ thị trường => N=342 hiệu dụng thấp hơn nhiều)
  B. tách theo chiều thị trường trong CHÍNH cửa sổ nắm giữ (bench up/down)
  C. beta-adjusted excess: post_ret - beta_tk * bench_ret
  D. per-year leave-one-out
"""
import os, sys
import numpy as np, pandas as pd
from scipy import stats

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)
os.environ.pop("BQ_LOCAL_CACHE", None)
from simulate_holistic_nav import bq

df = pd.read_csv("mike/agents/Taylor/data_lag_sector_split_20260721.csv",
                 parse_dates=["Release_Date"])
df["yr"] = df["Release_Date"].dt.year


def stat(x):
    x = np.asarray(x, float)
    t = stats.ttest_1samp(x, 0)
    return len(x), x.mean(), t.statistic, t.pvalue, (x > 0).mean() * 100


# ── A. clustered SE theo quý sự kiện ─────────────────────────────────────
print("=" * 92)
print("A. CLUSTERED SE theo quý phát hành (event CTCK tương quan chéo rất mạnh)")
print("=" * 92)
df["cl"] = df["Release_Date"].dt.to_period("Q").astype(str)
for g in ["BROKER", "MANUF", "OTHER"]:
    s = df[df["grp"] == g]
    # cluster-robust SE cho trung bình: var = sum_c (sum_i e_i)^2 / n^2 (CR0)
    e = s["excess"] - s["excess"].mean()
    gs = e.groupby(s["cl"]).sum()
    n, G = len(s), s["cl"].nunique()
    se_cl = np.sqrt((gs ** 2).sum()) / n * np.sqrt(G / max(G - 1, 1))
    se_iid = s["excess"].std(ddof=1) / np.sqrt(n)
    m = s["excess"].mean()
    print(f"  {g:7s} N={n:5d} clusters={G:3d}  mean={m:+.2f}%  "
          f"SE_iid={se_iid:.2f} (t={m/se_iid:.2f})   "
          f"SE_cluster={se_cl:.2f} (t={m/se_cl:.2f}, p={2*(1-stats.t.cdf(abs(m/se_cl), G-1)):.4f})")
    # trung bình theo cluster (mỗi quý 1 quan sát)
    cm = s.groupby("cl")["excess"].mean()
    t = stats.ttest_1samp(cm, 0)
    print(f"          -> trung bình-theo-quý: {cm.mean():+.2f}%  t={t.statistic:.2f} "
          f"p={t.pvalue:.4f}  quý dương {(cm>0).mean()*100:.0f}%")

# ── B. chiều thị trường trong cửa sổ nắm giữ ─────────────────────────────
print("\n" + "=" * 92)
print("B. EXCESS THEO CHIỀU THỊ TRƯỜNG (bench_ret của chính cửa sổ T+5->T+30)")
print("=" * 92)
for g in ["BROKER", "MANUF", "OTHER"]:
    s = df[df["grp"] == g]
    for lbl, m in [("bench UP  ", s["bench_ret"] > 0), ("bench DOWN", s["bench_ret"] <= 0)]:
        n, mu, t, p, w = stat(s[m]["excess"])
        print(f"  {g:7s} {lbl} N={n:5d}  excess={mu:+.2f}%  t={t:+.2f}  p={p:.4f}  win={w:.1f}%")
    # slope: excess ~ bench_ret  (nếu >0 => còn beta dư, không phải alpha)
    sl = stats.linregress(s["bench_ret"], s["excess"])
    print(f"          -> hồi quy excess ~ bench: slope={sl.slope:+.3f} "
          f"(p={sl.pvalue:.4f}) => beta ngầm ≈ {1+sl.slope:.2f}; alpha={sl.intercept:+.2f}%\n")

# ── C. beta-adjusted excess ──────────────────────────────────────────────
print("=" * 92)
print("C. BETA-ADJUSTED: alpha = post_ret - beta_tk * bench_ret (beta 2Y rolling, causal)")
print("=" * 92)
tks = sorted(df["ticker"].unique())
px = bq(f"""SELECT t.time, t.ticker, t.Close, t.VNINDEX
FROM tav2_bq.ticker AS t
WHERE t.ticker IN ({','.join(chr(39)+x+chr(39) for x in tks)})
  AND t.time >= '2011-01-01' AND t.Close IS NOT NULL AND t.VNINDEX IS NOT NULL""")
px["time"] = pd.to_datetime(px["time"])
px = px.sort_values(["ticker", "time"])
px["r"] = px.groupby("ticker")["Close"].pct_change()
px["rm"] = px.groupby("ticker")["VNINDEX"].pct_change()
px = px[px["r"].notna() & px["rm"].notna() & (px["r"].abs() < 0.5)]

betas = {}
for tk, sub in px.groupby("ticker"):
    betas[tk] = sub.set_index("time")[["r", "rm"]]


def beta_at(tk, dt, win=500):
    s = betas.get(tk)
    if s is None:
        return np.nan
    h = s.loc[:pd.Timestamp(dt)].tail(win)          # causal: chỉ dữ liệu TRƯỚC release
    if len(h) < 120 or h["rm"].var() == 0:
        return np.nan
    return h["r"].cov(h["rm"]) / h["rm"].var()


df["beta"] = [beta_at(t, d) for t, d in zip(df["ticker"], df["Release_Date"])]
print(f"  beta trung vị: " + "  ".join(
    f"{g}={df[df['grp']==g]['beta'].median():.2f}" for g in ["BROKER", "MANUF", "OTHER"]))
d2 = df[df["beta"].notna()].copy()
d2["alpha"] = d2["post_ret"] - d2["beta"] * d2["bench_ret"]
print(f"  (N có beta = {len(d2)}/{len(df)})")
for g in ["BROKER", "MANUF", "OTHER"]:
    s = d2[d2["grp"] == g]
    n, mu, t, p, w = stat(s["alpha"])
    cm = s.groupby(s["Release_Date"].dt.to_period("Q").astype(str))["alpha"].mean()
    tc = stats.ttest_1samp(cm, 0)
    print(f"  {g:7s} N={n:5d}  alpha_beta-adj={mu:+.2f}%  t_iid={t:+.2f}  p={p:.4f}  "
          f"win={w:.1f}%   | theo-quý: {cm.mean():+.2f}% t={tc.statistic:+.2f} p={tc.pvalue:.4f}")

# ── D. per-year ──────────────────────────────────────────────────────────
print("\n" + "=" * 92)
print("D. PER-YEAR (BROKER) + leave-one-out")
print("=" * 92)
s = df[df["grp"] == "BROKER"]
for y, sub in s.groupby("yr"):
    n, mu, t, p, w = stat(sub["excess"])
    print(f"   {y}  N={n:3d}  excess={mu:+7.2f}%  win={w:5.1f}%")
print("  -- LOO (bỏ 1 năm) --")
for y in sorted(s["yr"].unique()):
    r = s[s["yr"] != y]["excess"]
    print(f"   bỏ {y}: mean={r.mean():+.2f}%  (full {s['excess'].mean():+.2f}%)")

d2.to_csv("mike/agents/Taylor/data_lag_sector_beta_20260721.csv", index=False)
print("\n[saved] mike/agents/Taylor/data_lag_sector_beta_20260721.csv")
