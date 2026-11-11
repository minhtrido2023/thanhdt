# -*- coding: utf-8 -*-
"""trigger_freq.py — (f) tần suất kích hoạt rule mua 'giá <= 0,85 x tâm' theo NGÀY.
FV của as-of quý t giữ nguyên cho các phiên (t, t_next] (FV cập nhật mỗi quý, PIT: chỉ dùng FV đã
tính tại as-of <= phiên). Đường giá cùng khung = P0 * Close_d / Close_t. Mẫu = primary (rating<=3).
Run: $DNA_PYEXE trigger_freq.py  -> ../out/trigger_freq.json
"""
import os, json
import numpy as np, pandas as pd, duckdb
WC = "/home/trido/thanhdt/WorkingClaude"
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out")
p = pd.read_parquet(os.path.join(OUT, "panel.parquet"))
p = p[p["ok"] & (p["rating"] <= 3) & (p["FV"] > 0)].copy()
px = duckdb.connect().execute(f"""SELECT ticker, CAST(time AS DATE) AS time, Close FROM read_parquet('{WC}/data/bq_cache/ticker/*.parquet')
    WHERE time >= DATE '2016-01-01' AND Close > 0""").df()
px["time"] = pd.to_datetime(px["time"])
asofs = sorted(pd.read_parquet(os.path.join(OUT, "panel.parquet"))["asof"].unique())
nxt = {a: (asofs[i + 1] if i + 1 < len(asofs) else pd.Timestamp("2026-03-31")) for i, a in enumerate(asofs)}
pxb = {t: g for t, g in px.groupby("ticker")}
rows = []
for r in p.itertuples():
    g = pxb.get(r.ticker)
    if g is None: continue
    c0 = g[g.time == r.asof].Close
    if len(c0) == 0: continue
    seg = g[(g.time > r.asof) & (g.time <= nxt[r.asof])]
    if len(seg) == 0: continue
    path = r.P0 * seg.Close.values / float(c0.iloc[0])
    rows.append(pd.DataFrame({"ticker": r.ticker, "time": seg.time.values,
                              "trig85": path <= 0.85 * r.FV, "le_c": path <= r.FV}))
d = pd.concat(rows, ignore_index=True)
d["yr"] = d["time"].dt.year
ty = d.groupby(["ticker", "yr"]).agg(any85=("trig85", "max"), frac85=("trig85", "mean"), anyc=("le_c", "max"))
byyr = ty.groupby(level="yr").agg(ticker_years=("any85", "size"), frac_ty_any85=("any85", "mean"),
                                  mean_day_frac85=("frac85", "mean"), frac_ty_any_le_c=("anyc", "mean"))
tk = d.groupby("ticker").trig85.agg(["mean", "max", "size"])
out = {"n_ticker_days": len(d), "n_tickers": int(d.ticker.nunique()),
       "day_frac_trig85": float(d.trig85.mean()), "day_frac_le_center": float(d.le_c.mean()),
       "ticker_year_frac_any85": float(ty.any85.mean()),
       "ticker_frac_ever85": float(tk["max"].mean()),
       "ticker_frac_trig85_lt5pct_days": float((tk["mean"] < 0.05).mean()),
       "by_year": byyr.round(4).to_dict(orient="index")}
json.dump(out, open(os.path.join(OUT, "trigger_freq.json"), "w"), indent=1, default=float)
print(json.dumps({k: v for k, v in out.items() if k != "by_year"}, indent=1)); print(byyr.round(3))
