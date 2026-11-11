# -*- coding: utf-8 -*-
"""trigger.py — rule mua "vốn hoá ≤ 0,85 × tâm" theo PHIÊN (tâm V(w) tính tại as-of, giữ tới as-of kế,
PIT), mẫu chính, chỉ dòng có số CP fiinprox. Đo: % phiên kích hoạt, % mã không bao giờ kích hoạt, tỉ phần
phương sai chỉ báo nằm GIỮA các mã; và (mô tả) lợi suất 12/36 tháng trừ trung vị cùng quý khi kích hoạt
tại as-of vs không. Run: $DNA_PYEXE trigger.py -> ../out/trigger.json
"""
import os, sys, json
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import duckdb
WC = "/home/trido/thanhdt/WorkingClaude"
p = load()
MAIN = (p.rating <= 3).values & (p.mc_src == "fiin").values & (p.V_s > 0).values & (p.V_l3 > 0).values
q = p[MAIN].copy()
px = duckdb.connect().execute(f"""SELECT ticker, CAST(time AS DATE) AS time, Price FROM read_parquet('{WC}/data/bq_cache/ticker/*.parquet')
    WHERE time >= DATE '2016-03-01' AND Price > 0""").df()
px["time"] = pd.to_datetime(px.time)
px = px[px.ticker.isin(set(q.ticker))]
fz = pd.read_csv(f"{WC}/mike/data/fiinprox_oshares_pit_20260926.csv", parse_dates=["date"]).sort_values("date")
px = px.sort_values("time")
px = pd.merge_asof(px, fz[["ticker", "date", "shares"]].rename(columns={"date": "time"}), on="time", by="ticker")
px = px[px.time <= fz.date.max()]
px["MC"] = px.Price * px.shares
WS = (0.0, 0.5, 0.8, 1.0)
for w in WS:
    q[f"V{w}"] = w * q.V_s + (1 - w) * q.V_l3
q = q.sort_values("asof")
d = pd.merge_asof(px.dropna(subset=["MC"]), q[["ticker", "asof"] + [f"V{w}" for w in WS]].rename(columns={"asof": "time"}),
                  on="time", by="ticker", tolerance=pd.Timedelta(days=95), direction="backward").dropna(subset=["V0.0"])
S = {"n_sessions": len(d), "n_tickers": int(d.ticker.nunique())}
for w in WS:
    t = (d.MC <= 0.85 * d[f"V{w}"]).astype(float)
    tm = t.groupby(d.ticker).mean()
    tot = t.var(); betw = t.groupby(d.ticker).transform("mean").var()
    S[f"w{w}"] = {"trigger_rate": float(t.mean()), "never_tickers": float((tm == 0).mean()),
                  "lt5pct_tickers": float((tm < 0.05).mean()), "gt80pct_tickers": float((tm > 0.8).mean()),
                  "between_ticker_var_share": float(betw / tot),
                  "by_year": {int(y): float(v) for y, v in t.groupby(d.time.dt.year).mean().items()}}
# mô tả: lợi suất tương lai (trừ trung vị cùng quý) khi kích hoạt tại as-of
for N in (12, 36):
    f = q[q[f"full{N}"]].copy()
    f["y"] = np.log(f[f"TR{N}"]); f["ydm"] = f.y - f.groupby("q").y.transform("median")
    for w in WS:
        trig = f.MC0 <= 0.85 * f[f"V{w}"]
        S[f"w{w}"][f"fwd{N}_dm_trig"] = float(f.ydm[trig].median()) if trig.any() else None
        S[f"w{w}"][f"fwd{N}_dm_not"] = float(f.ydm[~trig].median())
        S[f"w{w}"][f"asof_trig_rate_{N}"] = float(trig.mean())
        # CI Δ (trig − not) cụm mã
        g = list(pd.Series(np.arange(len(f))).groupby(f.ticker.values).indices.values())
        rng = np.random.default_rng(SEED); out = []
        yv, tv = f.ydm.values, trig.values
        for _ in range(1000):
            s = np.concatenate([g[j] for j in rng.integers(0, len(g), len(g))])
            out.append(np.median(yv[s][tv[s]]) - np.median(yv[s][~tv[s]]))
        S[f"w{w}"][f"fwd{N}_dm_delta_ci"] = ci(np.array(out))
json.dump(S, open(os.path.join(OUT, "trigger.json"), "w"), indent=1, default=float)
print(json.dumps(S, indent=0, default=float))
