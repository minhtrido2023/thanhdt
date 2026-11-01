#!/usr/bin/env python3
"""MÔ TẢ nhanh (KHÔNG phải backtest, KHÔNG phải bằng chứng edge): bộ chọn DD v2 trên dữ liệu PIT tháng
2016-01 → 2026-07. Câu hỏi: top-1 theo từng biến thể có forward 3M hơn trung vị rank 2-8 cùng ngày không.

PIT: universe_pit in_universe tại asof (1 ruleset) · rating = fa_ratings_8l bản có rt_time ≤ asof
(bảng bị republish ⇒ lệch nhẹ, đã ghi registry) · tài chính = ticker_financial time ≤ asof (time = ngày
công bố, quy ước dcf_valuation) · DCF = dcf_valuation.fair_value số CP quý (fin-path), khung domestic_v2
(r hằng ⇒ không rò lãi suất tương lai; g_T dùng CPI — tháng gần đây forward-fill) · giá vào = Price chưa
đ/c phiên ≤ asof · forward = Close đ/c sau 63 phiên. Bỏ: thanh khoản ≥0,3 tỷ, redflag, BANNED/forensic,
mã đang giữ, cooldown 90 ngày, mã DCF-NA (tài chính) ⇒ pool KHÁC production; cfo_np xấp xỉ bằng
CF_OA_P0/NP_P0 quý (production đọc rating_8l). Chạy: $DNA_PYEXE quick_pit_variants.py  (threads=1)
"""
import os
import sys
import glob

os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
import pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WC)
OUT = os.path.dirname(os.path.abspath(__file__))
import dcf_valuation as D  # noqa: E402

os.chdir(OUT)
fin = D._load_financials()
fx = pd.read_parquet(f"{WC}/data/bq_cache/ticker_financial.parquet",
                     columns=["ticker", "time", "quarter", "NP_P0", "NP_P4", "CF_OA_P0", "ROE_Min3Y"])
fx["time"] = pd.to_datetime(fx["time"])
rt = pd.read_csv(f"{WC}/data/fa_ratings_8l_hist.csv", parse_dates=["rt_time"])
up = pd.concat([pd.read_parquet(p, columns=["time", "ticker", "in_universe", "ruleset_version"])
                for p in sorted(glob.glob(f"{WC}/data/bq_cache/universe_pit/*.parquet"))])
up["time"] = pd.to_datetime(up["time"])
rs = up["ruleset_version"].value_counts().index[0]
up = up[(up["ruleset_version"] == rs) & up["in_universe"]]
px = pd.concat([pd.read_parquet(p, columns=["time", "ticker", "Close", "Price"])
                for p in sorted(glob.glob(f"{WC}/data/bq_cache/ticker/*.parquet")) if int(os.path.basename(p)[:4]) >= 2015])
px["time"] = pd.to_datetime(px["time"])
cl = px.pivot_table(index="time", columns="ticker", values="Close")
pr = px.pivot_table(index="time", columns="ticker", values="Price")
days = cl.index
asofs = [days[days >= pd.Timestamp(y, m, 1)][0] for y in range(2016, 2027) for m in range(1, 13)
         if pd.Timestamp(y, m, 1) <= pd.Timestamp("2026-07-01")]

rows = []
for a in asofs:
    i = days.get_loc(a)
    if i + 63 >= len(days):
        continue
    uni = set(up.loc[up["time"] == up["time"][up["time"] <= a].max(), "ticker"])
    r = rt[rt["rt_time"] <= a].sort_values("rt_time").groupby("ticker").tail(1).set_index("ticker")["rating"]
    f = fx[fx["time"] <= a].sort_values("time").groupby("ticker").tail(1).set_index("ticker")
    last = fin[fin["time"] <= a].groupby("ticker").tail(1).set_index("ticker")
    for t in uni:
        if t not in r.index or r[t] > 3 or t not in f.index or not (f.at[t, "ROE_Min3Y"] >= 0):
            continue
        p = pr.at[a, t] if t in pr.columns else np.nan
        if not (p > 0) or t not in cl.columns:
            continue
        res = D.fair_value(t, str(a.date()), price=float(p), fin=fin,
                           oshares=float(last.at[t, "OShares"]) if t in last.index and pd.notna(last.at[t, "OShares"]) else None)
        if not res.get("ok") or res.get("margin_of_safety") is None:
            continue
        c0, c1 = cl.at[a, t], cl.iloc[i + 63][t]
        if not (c0 > 0 and c1 > 0):
            continue
        np0, np4, cfo = f.at[t, "NP_P0"], f.at[t, "NP_P4"], f.at[t, "CF_OA_P0"]
        fresh = (a - f.at[t, "time"]).days <= 45 and np0 > 0
        rows.append(dict(asof=a, ticker=t, rating=int(r[t]), mos=res["margin_of_safety"], fresh=fresh,
                         g=(np0 / np4 - 1) if (np4 > 0 and np0 > 0) else (np.inf if np0 > 0 else np.nan),
                         cfo_np=(cfo / np0) if np0 and np0 > 0 else np.nan, fwd=c1 / c0 - 1))
    print(a.date(), len(rows), flush=True)

df = pd.DataFrame(rows)
df.to_csv(os.path.join(OUT, "quick_pit_panel.csv"), index=False)


def score(g, variant):
    g = g.copy()
    g["V"] = g["mos"].rank(pct=True)
    e = pd.Series(0.0, index=g.index)
    fr = g["fresh"]
    if fr.any():
        e[fr] = g.loc[fr, "g"].fillna(-np.inf).rank(pct=True)
    q = np.where(g["cfo_np"] >= 0.5, 1.0, np.where(g["cfo_np"] < 0, 0.3, 0.6))
    q = np.where((g["g"] > 3.0) | np.isinf(g["g"]), 0.3, q)
    g["E"] = np.where(fr, e * q, 0.0)
    g["R"] = g["rating"].map({1: 1.0, 2: 0.67, 3: 0.33})
    w = {"prereg": (0.5, 0.3, 0.2), "V_only": (1, 0, 0), "E_heavy": (0.3, 0.5, 0.2)}[variant]
    g["s"] = w[0] * g["V"] + w[1] * g["E"] + w[2] * g["R"]
    return g.sort_values(["s", "mos"], ascending=False)


out = []
for v in ("prereg", "V_only", "E_heavy"):
    for a, g in df.groupby("asof"):
        if len(g) < 8:
            continue
        s = score(g, v)
        out.append(dict(variant=v, asof=a, n_pool=len(g), top1=s.iloc[0]["fwd"], rest=s.iloc[1:8]["fwd"].median(),
                        pool=g["fwd"].median()))
o = pd.DataFrame(out)
o["d_vs_rest"] = o["top1"] - o["rest"]
o["d_vs_pool"] = o["top1"] - o["pool"]
o.to_csv(os.path.join(OUT, "quick_pit_variants_out.csv"), index=False)
rng = np.random.default_rng(0)
lines = []
for v, g in o.groupby("variant"):
    for col in ("d_vs_rest", "d_vs_pool"):
        x = g[col].to_numpy()
        q = g[g["asof"].dt.month.isin([1, 4, 7, 10])][col].to_numpy()   # mẫu quý, không chồng 3M
        bs = [np.median(rng.choice(q, len(q))) for _ in range(2000)]
        lines.append(f"{v:8s} {col:9s} N_thang={len(x)} median={np.median(x):+.4f} hit={np.mean(x > 0):.2f} | "
                     f"N_quy={len(q)} median={np.median(q):+.4f} CI95=[{np.percentile(bs, 2.5):+.4f},{np.percentile(bs, 97.5):+.4f}]")
open(os.path.join(OUT, "quick_pit_variants_summary.txt"), "w").write(
    f"ruleset={rs} months={o['asof'].nunique()} rows={len(df)}\n" + "\n".join(lines) + "\n")
print("\n".join(lines))
