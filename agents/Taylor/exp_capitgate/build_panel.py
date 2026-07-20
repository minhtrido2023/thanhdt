# -*- coding: utf-8 -*-
"""Panel builder — CAPIT quality-gate relaxation study (job Taylor_20260720_160852).
Emits ONE row per (obs_date, ticker) over the LIQUID universe (ADV>=1B, the loosest gate
under test), carrying the raw gate variables + pb_z + forward returns, so every variant
Gk can be evaluated downstream by masking, with no re-query.
Point-in-time: ticker_prune columns at obs date (financials pre-joined by Release_Date).
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd, duckdb
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
OUT = f"{WORKDIR}/mike/agents/Taylor/exp_capitgate"
con = duckdb.connect(":memory:"); con.execute("SET threads=1")
PRUNE = f"read_parquet('{WORKDIR}/data/bq_cache/ticker_prune/*.parquet')"

EVENTS = ["2014-05-08","2015-08-24","2016-01-18","2018-05-28","2020-03-12","2022-04-20",
          "2022-06-20","2022-09-29","2023-10-31","2024-04-19","2024-08-05","2025-04-03",
          "2025-10-20","2026-03-09"]

cal = con.execute(f"SELECT DISTINCT time FROM {PRUNE} WHERE time>=DATE '2014-01-01' ORDER BY 1").df()
cal["time"] = pd.to_datetime(cal["time"])
obs_dates = sorted(set(cal.groupby(cal["time"].dt.to_period("M"))["time"].min().tolist())
                   | set(pd.to_datetime(EVENTS)))
print(f"obs dates {len(obs_dates)} ({obs_dates[0].date()} -> {obs_dates[-1].date()})")

px = con.execute(f"SELECT ticker, time, Close FROM {PRUNE}").df()
px["time"] = pd.to_datetime(px["time"])
P = px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index()

def fwd(tk, d, h):
    if tk not in P.columns: return np.nan
    s = P[tk].dropna(); s = s[s.index >= d]
    if len(s) < 2: return np.nan
    j = min(h, len(s) - 1)
    if j < h * 0.8: return np.nan          # truncated at panel end -> drop, don't bias
    return s.iloc[j] / s.iloc[0] - 1

frames = []
for i, d in enumerate(obs_dates):
    e = con.execute(f"""SELECT ticker, (PB-PB_MA5Y)/NULLIF(PB_SD5Y,0) pbz,
  ROE_Min5Y roe, ROIC5Y roic, FSCORE fs, COALESCE(Price,Close)*Volume/1e9 adv
FROM {PRUNE} WHERE time = DATE '{d.date()}'
  AND COALESCE(Price,Close)*Volume/1e9 >= 1""").df().dropna(subset=["pbz"])
    if e.empty: continue
    e["obs"] = d
    for h in (60, 250):
        e[f"r{h}"] = [fwd(t, d, h) for t in e["ticker"]]
    frames.append(e)
    if (i + 1) % 30 == 0: print(f"  ...{i+1}/{len(obs_dates)}", flush=True)

X = pd.concat(frames, ignore_index=True)
X = X[["obs","ticker","pbz","roe","roic","fs","adv","r60","r250"]]
X.to_csv(f"{OUT}/panel.csv", index=False)
print(f"\nwrote panel.csv: {len(X)} rows | {X.obs.nunique()} obs dates | "
      f"names/date median {X.groupby('obs').size().median():.0f} | r60 coverage {X.r60.notna().mean()*100:.0f}%")
