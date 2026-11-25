# -*- coding: utf-8 -*-
"""p1_features.py — đặc trưng hành vi theo THÁNG (PRELOCK_PILOT §2). Giá ngày một vintage, đúng 3 nguồn của b_panel.py.
Không profit_*, không ticker_prune. Out: ../out/feat.parquet, ../out/feat_build.json"""
import os, glob, json
import numpy as np, pandas as pd, duckdb
WC = "/home/trido/thanhdt/WorkingClaude"; HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out")
V3 = os.environ.get("V3_DIR", f"{WC}/wt-dcf-v3-20261125/agents/Taylor/research/dcf_vn_redesign_20261125c")
NS = "datetime64[ns]"; c = duckdb.connect(); LOG = {}
px = c.execute(f"""SELECT ticker, CAST(time AS DATE) AS time, Close, Price, Volume
      FROM read_parquet('{WC}/data/bq_cache/ticker/*.parquet') WHERE Close > 0 AND ICB_Code IS NOT NULL""").df()
px["time"] = pd.to_datetime(px.time).astype(NS)
pre = pd.read_csv(f"{V3}/out/px_pre2013_d.csv", parse_dates=["time"]); pre["time"] = pre.time.astype(NS)
pre = pre[(pre.time < px.time.min()) & (pre.Close > 0)]
px = pd.concat([pre[["ticker", "time", "Close", "Price", "Volume"]], px], ignore_index=True)
rows = []
for fp in sorted(glob.glob(f"{V3}/out/delisted/px_*.csv")):
    d = pd.read_csv(fp)
    if len(d) < 60 or "adClose" not in d.columns: continue
    d = d[(d.close > 0) & (d.adClose > 0)]
    rows.append(pd.DataFrame({"ticker": d.code, "time": pd.to_datetime(d.date).astype(NS), "Close": d.adClose * 1000.0,
                              "Price": d.close * 1000.0, "Volume": d.nmVolume.fillna(0)}))
dead = pd.concat(rows, ignore_index=True); dead = dead[~dead.ticker.isin(set(px.ticker))]
LOG["n_bq_tk"] = int(px.ticker.nunique()); LOG["n_dead_tk"] = int(dead.ticker.nunique())
px = pd.concat([px, dead], ignore_index=True).drop_duplicates(["ticker", "time"]).sort_values(["ticker", "time"]).reset_index(drop=True)
px["Volume"] = px.Volume.fillna(0.0)
# số CP PIT từ panel (tháng) → ffill theo mã; tháng trước dòng panel đầu tiên của mã: dùng N đầu tiên (ghi nhận: xấp xỉ)
pan = pd.read_parquet(f"{V3}/out_F/vp2.parquet", columns=["ticker", "ym", "N"])
px["ym"] = px.time.dt.to_period("M").astype(str)
px = px.merge(pan, on=["ticker", "ym"], how="left")
g = px.groupby("ticker", sort=False)
nfill = g.N.ffill(); LOG["share_N_backfilled"] = float((nfill.isna() & g.N.bfill().notna()).mean())
px["N"] = nfill.fillna(g.N.bfill())
lc = np.log(px.Close.values)
px["hi52"] = lc - np.log(g.Close.rolling(252, min_periods=120).max().reset_index(level=0, drop=True).sort_index().values)
px["mom"] = np.log(g.Close.shift(21) / g.Close.shift(252)); px["rev1"] = np.log(px.Close / g.Close.shift(21))
to = np.clip((px.Volume / px.N).fillna(0).values, 0, 1); cl = px.Close.values
first = (px.ticker != px.ticker.shift()).values; rp = np.empty(len(px)); cnt = np.empty(len(px), int)
r = 0.0; k = 0
for i in range(len(px)):
    if first[i]: r = cl[i]; k = 0
    else: r = (1 - to[i]) * r + to[i] * cl[i]; k += 1
    rp[i] = r; cnt[i] = k
px["cgo"] = np.where((cnt >= 250) & px.N.notna().values, lc - np.log(rp), np.nan)
# phụ (mô tả, KHÔNG nằm trong mô hình pilot): số phiên |Δ giá thô| ≥ 6,5% trong 60 phiên, MAX 21 phiên, turnover 60 phiên
pr = px.Price / g.Price.shift(1) - 1
px["up65"] = (pr >= 0.065).astype(float); px["dn65"] = (pr <= -0.065).astype(float)
g = px.groupby("ticker", sort=False)
for col, src, w, fn in (("n_up60", "up65", 60, "sum"), ("n_dn60", "dn65", 60, "sum")):
    px[col] = getattr(g[src].rolling(w, min_periods=40), fn)().reset_index(level=0, drop=True).sort_index().values
px["_ret"] = px.Close / g.Close.shift(1) - 1; px["_to"] = to
g = px.groupby("ticker", sort=False)
px["max21"] = g._ret.rolling(21, min_periods=15).max().reset_index(level=0, drop=True).sort_index().values
px["to60"] = g._to.rolling(60, min_periods=40).mean().reset_index(level=0, drop=True).sort_index().values
m = px.groupby(["ticker", "ym"]).tail(1)[["ticker", "ym", "time", "hi52", "cgo", "mom", "rev1", "n_up60", "n_dn60", "max21", "to60"]]
m.to_parquet(os.path.join(OUT, "feat.parquet"), index=False)
LOG["rows"] = int(len(m)); LOG["cover"] = {k: float(m[k].notna().mean()) for k in ["hi52", "cgo", "mom", "rev1"]}
json.dump(LOG, open(os.path.join(OUT, "feat_build.json"), "w"), indent=1); print(LOG)
