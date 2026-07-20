# -*- coding: utf-8 -*-
"""Position-level panel — CAPIT exit-mechanism study (job Taylor_20260720_164006).

One row per (event, ticker, session_offset 0..60) carrying price / pb_z / quality-gate
variables, so every exit variant can be evaluated downstream by masking with NO re-query.

Basket reproduces production EXACTLY (pt_v23_audit_2014.py::capit_basket, no-overflow path
== golive_recommend_v23.py lines 312-328):
    quality gate ROE_Min5Y>=0.12 AND ROIC5Y>=0.10 AND FSCORE>=6 AND Price*Volume/1e9 >= 2
    g = pbz < -1 ; c = pbz < 0 ; pick = g if len(g)>=3 else (c if len(c)>=3 else all)
    pick = nsmallest(15, pbz)
Point-in-time: ticker_prune columns as-of each session (financials pre-joined by Release_Date).
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd, duckdb

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
OUT = f"{WORKDIR}/mike/agents/Taylor/exp_capitexit"
con = duckdb.connect(":memory:"); con.execute("SET threads=1")
PRUNE = f"read_parquet('{WORKDIR}/data/bq_cache/ticker_prune/*.parquet')"

# same 14 washout events as job Taylor_20260720_160852 (exp_capitgate)
EVENTS = ["2014-05-08","2015-08-24","2016-01-18","2018-05-28","2020-03-12","2022-04-20",
          "2022-06-20","2022-09-29","2023-10-31","2024-04-19","2024-08-05","2025-04-03",
          "2025-10-20","2026-03-09"]
HOLD = 60

cal = con.execute(f"SELECT DISTINCT time FROM {PRUNE} WHERE time>=DATE '2013-06-01' ORDER BY 1").df()
CAL = pd.to_datetime(cal["time"]).tolist()

def sess_after(d, n):
    """n-th trading session strictly after d (n=1 -> next session)."""
    i = np.searchsorted(np.array(CAL), np.datetime64(d), side="right")
    j = i + n - 1
    return CAL[j] if j < len(CAL) else None

# ---- 1. reproduce production basket at each event ------------------------------------
baskets = {}
for ds in EVENTS:
    e = con.execute(f"""
        SELECT ticker, (PB-PB_MA5Y)/NULLIF(PB_SD5Y,0) AS pbz
        FROM {PRUNE}
        WHERE time = DATE '{ds}'
          AND ROE_Min5Y >= 0.12 AND ROIC5Y >= 0.10 AND FSCORE >= 6
          AND COALESCE(Price, Close) * Volume / 1e9 >= 2
    """).df().dropna(subset=["pbz"])
    if e.empty:
        baskets[ds] = pd.DataFrame(columns=["ticker", "pbz"]); print(f"{ds}: pool EMPTY"); continue
    g = e[e["pbz"] < -1]; c = e[e["pbz"] < 0]
    pick = g if len(g) >= 3 else (c if len(c) >= 3 else e)
    pick = pick.nsmallest(15, "pbz") if len(pick) > 15 else pick
    baskets[ds] = pick.sort_values("pbz").reset_index(drop=True)
    print(f"{ds}: pool={len(e):3d} deep(pbz<-1)={len(g):3d} cheap(pbz<0)={len(c):3d} -> basket={len(pick):2d} "
          f"(cap15 binding={len(pick)==15})")

# ---- 2. daily path per position -------------------------------------------------------
tickers = sorted({t for b in baskets.values() for t in b["ticker"]})
in_list = ",".join(f"'{t}'" for t in tickers)
raw = con.execute(f"""
    SELECT ticker, time, Open, Close, Price, Volume,
           (PB-PB_MA5Y)/NULLIF(PB_SD5Y,0) AS pbz,
           ROE_Min5Y, ROIC5Y, FSCORE
    FROM {PRUNE} WHERE ticker IN ({in_list}) AND time >= DATE '2014-01-01'
""").df()
raw["time"] = pd.to_datetime(raw["time"])
raw = raw.sort_values(["ticker", "time"])

# VNINDEX path (for the redeploy-proxy robustness variant)
vni = con.execute(f"""SELECT time, VNINDEX FROM {PRUNE} WHERE VNINDEX IS NOT NULL
                      GROUP BY time, VNINDEX ORDER BY time""").df()
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.groupby("time")["VNINDEX"].first()

rows = []
for ds, b in baskets.items():
    d0 = pd.Timestamp(ds)
    entry_day = sess_after(d0, 1)          # T+1 Open entry, per audit convention
    if entry_day is None: continue
    for _, r in b.iterrows():
        tk = r["ticker"]
        s = raw[(raw["ticker"] == tk) & (raw["time"] >= entry_day)].head(HOLD + 2)
        if s.empty or pd.isna(s.iloc[0]["Open"]) or s.iloc[0]["Open"] <= 0:
            print(f"  SKIP {ds} {tk}: no entry Open"); continue
        px_in = float(s.iloc[0]["Open"])
        n = min(len(s), HOLD + 1)
        if n < HOLD * 0.8:
            print(f"  SKIP {ds} {tk}: path truncated ({n} sessions)"); continue
        for k in range(n):
            row = s.iloc[k]
            rows.append(dict(
                event=ds, ticker=tk, pbz_entry=float(r["pbz"]), k=k, time=row["time"],
                px_in=px_in, close=row["Close"], open=row["Open"],
                pbz=row["pbz"], roe_min5y=row["ROE_Min5Y"], roic5y=row["ROIC5Y"],
                fscore=row["FSCORE"],
                adv_b=float(row["Price"] * row["Volume"] / 1e9) if pd.notna(row["Price"]) else np.nan,
                vni=float(vni.reindex([row["time"]]).iloc[0]) if row["time"] in vni.index else np.nan,
            ))

pan = pd.DataFrame(rows)
pan.to_csv(f"{OUT}/panel.csv", index=False)
print(f"\npanel rows={len(pan)} positions={pan.groupby(['event','ticker']).ngroups} "
      f"events={pan['event'].nunique()}")
print(pan.groupby("event").apply(lambda x: x.groupby("ticker").ngroups, include_groups=False))
