# -*- coding: utf-8 -*-
"""Vấn đề 3 — tăng trưởng/giai đoạn. PREREG §5 (a)(b)(c)."""
import os
import numpy as np
import pandas as pd
from common import DATA, OUT, spearman
import engine as E

P = print
pd.set_option("display.width", 250)
ri = pd.read_parquet(os.path.join(DATA, "row_inputs.parquet"))
pan = pd.read_parquet(os.path.join(DATA, "panel_monthly.parquet"))
finflag = pan.groupby("ticker").is_fin.last()
icb = pan.groupby("ticker").ICB_Code.last()
# năm tài chính = dòng Q4 (TTM = cả năm). Chỉ phi tài chính.
fy = ri[ri.quarter.str.endswith("Q4")].copy()
fy["fy"] = fy.quarter.str[:4].astype(int)
fy = fy[~fy.ticker.map(finflag).fillna(True).astype(bool)]
fy = fy.sort_values(["ticker", "fy"]).drop_duplicates(["ticker", "fy"], keep="last")
fy = fy[fy.fy >= 2005]
# vốn hoá tại ngày công bố Q4: Price thô × OShares (TRAP restate — chỉ dùng chia tam phân)
px = pd.read_parquet(os.path.join(DATA, "px_daily.parquet"))[["ticker", "time", "Close"]]
W = fy.pivot(index="ticker", columns="fy", values="ttm_np")
FC = fy.pivot(index="ticker", columns="fy", values="ttm_fcfe")
ROE = fy.pivot(index="ticker", columns="fy", values="ROE5Y")
OSH = fy.pivot(index="ticker", columns="fy", values="OShares")
years = sorted(W.columns)


def g_of(a, b):
    return np.where((a > 0) & (b > 0), b / a - 1, np.nan)


# ---------------------------------------------------------------- (a) trở về trung bình
G = pd.DataFrame({y: g_of(W[y - 1], W[y]) for y in years if y - 1 in W.columns}, index=W.index)
rows = []
for k in range(1, 6):
    sp, top_stay = [], []
    for y in G.columns:
        if y < 2009 or y + k not in G.columns:
            continue
        a, b = G[y], G[y + k]
        m = a.notna() & b.notna()
        if m.sum() < 50:
            continue
        sp.append(spearman(a[m], b[m]))
        q = a[m].rank(pct=True)
        qb = b[m].rank(pct=True)
        top_stay.append(((q > .8) & (qb > .8)).sum() / (q > .8).sum())
    rows.append({"k": k, "rank_corr_g_t_vs_g_t+k": np.mean(sp), "P(top20%_stay)": np.mean(top_stay), "n_years": len(sp)})
mr = pd.DataFrame(rows)
P("=== (a) tương quan hạng tăng trưởng NP năm t với năm t+k (2009+), P(top quintile còn top) — ngẫu nhiên = 0,20")
P(mr.round(3).to_string(index=False))
mr.to_csv(os.path.join(OUT, "t3a_mean_reversion.csv"), index=False)

# đường tắt dần: nhóm theo tăng trưởng trailing 3Y (CAGR NP_{t-3}→NP_t), tăng trưởng năm thứ j sau t
rows = []
for y in years:
    if y < 2009 or y - 3 not in W.columns:
        continue
    g3 = np.where((W[y - 3] > 0) & (W[y] > 0), (W[y] / W[y - 3]) ** (1 / 3) - 1, np.nan)
    df = pd.DataFrame({"ticker": W.index, "y": y, "g3": g3, "roe": ROE[y].values if y in ROE else np.nan})
    df["icb1"] = df.ticker.map(icb) // 1000
    df["mcap"] = (OSH[y] * 1.0).values  # placeholder thay bằng log NP tuyệt đối làm proxy quy mô
    df["size"] = np.log(W[y].clip(lower=1).values)
    for j in range(1, 8):
        if y + j in W.columns:
            df[f"gj{j}"] = g_of(W[y + j - 1].values, W[y + j].values)
            df[f"neg{j}"] = (W[y + j].values <= 0).astype(float)
            df.loc[W[y + j].isna().values, f"neg{j}"] = np.nan
    rows.append(df)
A = pd.concat(rows, ignore_index=True)
A = A[A.g3.notna()]
A["g3q"] = A.groupby("y").g3.transform(lambda s: pd.qcut(s.rank(method="first"), 5, labels=False))
A["roeq"] = A.groupby("y").roe.transform(lambda s: pd.qcut(s.rank(method="first"), 3, labels=False))
A["sizeq"] = A.groupby("y")["size"].transform(lambda s: pd.qcut(s.rank(method="first"), 3, labels=False))
gcols = [f"gj{j}" for j in range(1, 8)]
fade = A.groupby("g3q")[["g3"] + gcols].median()
P("=== đường tắt dần: TRUNG VỊ tăng trưởng NP năm j sau, theo ngũ phân vị CAGR 3Y quá khứ (0=thấp,4=cao)")
P(fade.round(3).to_string())
neg = A.groupby("g3q")[[f"neg{j}" for j in range(1, 6)]].mean()
P("tỷ lệ NP ≤ 0 năm j sau:"); P(neg.round(3).to_string())
fade.to_csv(os.path.join(OUT, "t3a_fade_by_g3q.csv"))
# top quintile × nhóm ROE / quy mô / ngành: tăng trưởng năm 1..5
for dim in ("roeq", "sizeq", "icb1"):
    t = A[A.g3q == 4].groupby(dim)[["g3"] + gcols[:5]].median()
    t["n"] = A[A.g3q == 4].groupby(dim).size()
    P(f"--- top quintile tăng trưởng, theo {dim}"); P(t.round(3).to_string())
    t.to_csv(os.path.join(OUT, f"t3a_top_by_{dim}.csv"))
# 'tuổi tăng trưởng': số năm liên tiếp g>15% tính tới t
streak = pd.DataFrame(0, index=G.index, columns=G.columns)
for y in G.columns:
    prev = streak[y - 1] if y - 1 in streak.columns else 0
    streak[y] = np.where(G[y] > 0.15, prev + 1, 0)
A["streak"] = [streak.at[t, y] if y in streak.columns else np.nan for t, y in zip(A.ticker, A.y)]
A["streak_b"] = pd.cut(A.streak, [-1, 0, 1, 2, 3, 99], labels=["0", "1", "2", "3", "4+"])
t = A.groupby("streak_b", observed=True)[gcols[:5]].median()
t["P(g1>15%)"] = A.groupby("streak_b", observed=True).gj1.apply(lambda s: (s > .15).mean())
t["n"] = A.groupby("streak_b", observed=True).size()
P("--- theo 'tuổi tăng trưởng' (số năm liên tiếp g>15%)"); P(t.round(3).to_string())
t.to_csv(os.path.join(OUT, "t3a_streak.csv"))
# hồi quy: g năm sau vs g3 quá khứ (winsor 1/99) ⇒ hệ số shrink kinh nghiệm IS/OOS
for per, sub in (("IS(y<=2016)", A[A.y <= 2016]), ("OOS(y>=2017)", A[A.y >= 2017])):
    for j in (1, 2, 3):
        s = sub[["g3", f"gj{j}"]].dropna()
        lo, hi = s.quantile(.01), s.quantile(.99)
        s = s.clip(lo, hi, axis=1)
        b = np.polyfit(s.g3, s[f"gj{j}"], 1)
        P(f"   {per} g_năm{j} = {b[1]:.3f} + {b[0]:.3f}·g3   (n={len(s)})")

# ---------------------------------------------------------------- (b) đường tăng trưởng vs NP thực, K=3,5
# gốc dự báo: dòng Q4 năm y; g_raw theo đúng engine; g_T = 5,5% (domestic_v2 cap luôn bị chạm 2014+)
gT = 0.055


def path(gc, spec, N):
    out = np.zeros((len(gc), N))
    kind = spec[0]
    for yy in range(N):
        if kind == "2s":  # (2s, shrink, n_explicit)
            s, n1 = spec[1], spec[2]
            ge = gT + s * (gc - gT)
            out[:, yy] = np.where(yy < n1, ge, gT)
        elif kind == "3s":  # (3s, shrink, n1, n2 fade)
            s, n1, n2 = spec[1], spec[2], spec[3]
            ge = gT + s * (gc - gT)
            if yy < n1:
                out[:, yy] = ge
            elif yy < n1 + n2:
                f = (yy - n1 + 1) / (n2 + 1)
                out[:, yy] = ge + f * (gT - ge)
            else:
                out[:, yy] = gT
        elif kind == "H":  # (H, shrink0, half-life) tắt dần mũ từ năm 1
            s, h = spec[1], spec[2]
            ge = gT + s * (gc - gT)
            out[:, yy] = gT + (ge - gT) * 0.5 ** (yy / h)
        elif kind == "flat0":
            out[:, yy] = 0.0
    return out


specs = {"2s_s0.5_N5 (HIỆN TẠI)": ("2s", .5, 5), "2s_s0_(g=gT)": ("2s", 0, 5), "2s_s0.25_N5": ("2s", .25, 5),
         "2s_s0.75_N5": ("2s", .75, 5), "2s_s1_N5": ("2s", 1, 5), "2s_s0.5_N3": ("2s", .5, 3),
         "2s_s1_N3": ("2s", 1, 3), "2s_s1_N1": ("2s", 1, 1), "3s_s1_N1_F3": ("3s", 1, 1, 3), "3s_s1_N2_F3": ("3s", 1, 2, 3),
         "3s_s0.5_N3_F5": ("3s", .5, 3, 5), "3s_s1_N3_F5": ("3s", 1, 3, 5),
         "H_s1_h1": ("H", 1, 1), "H_s1_h2": ("H", 1, 2), "H_s1_h3": ("H", 1, 3), "H_s0.5_h2": ("H", .5, 2),
         "g=0": ("flat0",)}
F = fy[["ticker", "fy", "ttm_np", "g_raw", "CF_OA_3Y", "CF_Invest_3Y"]].copy()
F["g_c"] = np.clip(np.where(F.g_raw.isna(), gT, F.g_raw), -0.02, 0.20)
F["base_fcfe"] = (F.CF_OA_3Y + F.CF_Invest_3Y.fillna(0)) / 3
res = []
for K in (3, 5):
    real = np.column_stack([F.merge(fy[["ticker", "fy", "ttm_np"]].assign(fy=fy.fy - j), on=["ticker", "fy"], how="left",
                                    suffixes=("", "_r")).ttm_np_r.values for j in range(1, K + 1)])
    realf = np.column_stack([F.merge(fy[["ticker", "fy", "ttm_fcfe"]].assign(fy=fy.fy - j), on=["ticker", "fy"],
                                     how="left").ttm_fcfe.values for j in range(1, K + 1)])
    ok = (F.ttm_np > 0) & np.isfinite(real).all(1) & (F.fy >= 2009) & (F.fy + K <= 2025)
    okf = (F.base_fcfe > 0) & (F.CF_OA_3Y > 0) & np.isfinite(realf).all(1) & (F.fy >= 2009) & (F.fy + K <= 2025)
    for name, sp in specs.items():
        pth = path(F.g_c.values, sp, K)
        cum = np.cumprod(1 + pth, axis=1)
        fc = (F.ttm_np.values[:, None] * cum).sum(1)
        rs = real.sum(1)
        mm = ok & (rs > 0)
        e = np.log(rs[mm] / fc[mm])
        fcf = (F.base_fcfe.values[:, None] * cum).sum(1)
        rf = realf.sum(1)
        mf = okf & (rf > 0)
        ef = np.log(rf[mf] / fcf[mf])
        yrs = F.fy[mm].values
        for per, sel in (("all", np.ones(mm.sum(), bool)), ("IS<=2015", yrs <= 2015), ("OOS>=2016", yrs >= 2016)):
            res.append({"K": K, "spec": name, "per": per, "n": int(sel.sum()), "np_mae_log": np.median(np.abs(e[sel])),
                        "np_bias_log": np.median(e[sel]), "share_np_cum<=0": float(1 - (rs[ok] > 0).mean())})
        res.append({"K": K, "spec": name, "per": "fcfe_all", "n": int(mf.sum()), "np_mae_log": np.median(np.abs(ef)),
                    "np_bias_log": np.median(ef), "share_np_cum<=0": float(1 - (rf[okf] > 0).mean())})
R = pd.DataFrame(res)
R.to_csv(os.path.join(OUT, "t3b_path_accuracy.csv"), index=False)
for K in (3, 5):
    t = R[R.K == K].pivot(index="spec", columns="per", values="np_mae_log")
    b = R[(R.K == K)].pivot(index="spec", columns="per", values="np_bias_log")
    t = t.join(b.add_suffix("_bias"))
    P(f"=== (b) K={K}: trung vị |log(Σ thực/Σ dự)| (NP; fcfe_all = FCFE) và bias (dương = thực > dự)")
    P(t.sort_values("all").round(3).to_string())

# ---------------------------------------------------------------- (c) nhất quán g = ROE × (1 − FCFE/NI)
fy["fcfe3"] = (fy.CF_OA_3Y + fy.CF_Invest_3Y.fillna(0))
np3 = W.T.rolling(3).sum().T  # tổng NP 3 năm
fy["np3"] = [np3.at[t, y] if y in np3.columns else np.nan for t, y in zip(fy.ticker, fy.fy)]
c = fy[(fy.np3 > 0) & (fy.fy >= 2014) & fy.ROE5Y.notna()].copy()
c["conv"] = (c.fcfe3 / c.np3).clip(-3, 3)
c["roe"] = c.ROE5Y / 100 if c.ROE5Y.abs().median() > 1 else c.ROE5Y
c["g_impl"] = c.roe * (1 - c.conv)
c["roeq"] = pd.qcut(c.roe.rank(method="first"), 3, labels=["ROE thấp", "ROE giữa", "ROE cao"])
P("=== (c) FCFE3Y/NP3Y (tỷ lệ chuyển đổi) và g ngầm định = ROE5Y×(1−FCFE/NI), 2014+")
P(c.groupby("roeq", observed=True)[["roe", "conv", "g_impl"]].median().round(3).to_string())
P("toàn bộ: median conv", round(c.conv.median(), 3), "median g_impl", round(c.g_impl.median(), 3),
  "| ROE5Y median", round(c.roe.median(), 4))
# với ROE_T = Ke 12,25%: payout ngụ ý = 1 − g/ROE
for g in (0.045, 0.05, 0.055, 0.06, 0.07):
    P(f"   g_T={g:.3f}: ROE_T=Ke 12,25% ⇒ FCFE/NI cần = {1-g/0.1225:.3f}; ROE_T=ROE trung vị {c.roe.median():.3f} ⇒ {1-g/c.roe.median():.3f}")
A.to_parquet(os.path.join(DATA, "growth_panel.parquet"))
