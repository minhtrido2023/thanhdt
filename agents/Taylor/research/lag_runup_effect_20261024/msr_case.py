"""Ca MSR: sự kiện hiện tại (live_lag_candidates, PIT từ pkl) + các sự kiện NP_R>=15 trước đó (prior good) + run-up."""
import sys, numpy as np, pandas as pd, duckdb
WD = "/home/trido/thanhdt/WorkingClaude"; sys.path.insert(0, WD)
from lag_live_schedule import live_lag_candidates
L = live_lag_candidates(); m = L[L.ticker == "MSR"].sort_values("Release_Date")
print(m.tail(6).round(3).to_string(index=False))
px = duckdb.connect().execute(f"SELECT time,ticker,Close FROM read_parquet('{WD}/data/bq_cache/ticker/*.parquet') WHERE ticker IN ('MSR','VNINDEX') AND time>='2024-06-01'").df()
px["time"] = pd.to_datetime(px.time); pv = px.pivot(index="time", columns="ticker", values="Close").sort_index()
rel = m.Release_Date.iloc[-1]; b = pv.index[pv.index < rel][-1]; ye = pv.index[pv.index < f"{rel.year}-01-01"][-1]
i = pv.index.get_loc(b); s, v = pv.MSR, pv.VNINDEX
f = lambda a, k: (a.iloc[i] / a.iloc[i - k] - 1) * 100
print(f"latest rel {rel.date()} | bar trước công bố {b.date()} | YTD {(s[b]/s[ye]-1)*100:.1f}% (VNI {(v[b]/v[ye]-1)*100:.1f}%) | r60 {f(s,60):.1f} r120 {f(s,120):.1f} pre30 {f(s,30):.1f} | dist_hi250 {(s[b]/s.iloc[i-249:i+1].max()-1)*100:.1f}% | last {pv.index[-1].date()} YTD-now {(s.iloc[-1]/s[ye]-1)*100:.1f}%")
ev = pd.read_csv(f"{WD}/data/earnings_events_classified.csv", parse_dates=["Release_Date"])
g = ev[(ev.ticker == "MSR") & (ev.NP_R >= 15)].sort_values("Release_Date")
print(f"MSR prior good events n={len(g)}, mean post_ret {g.post_ret.mean():.2f}, n>0 {(g.post_ret>0).sum()}")
print(g[["quarter", "Release_Date", "NP_R", "pre_ret", "rel_ret", "post_ret"]].round(1).to_string(index=False))
