#!/usr/bin/env python3
"""
lag_dnpr_event_study.py  (job Taylor_20260627_120256)
Event-study: does ΔNP_R (earnings-acceleration) split forward returns inside the
LAG/PEAD positive-surprise pool?

Faithful to the live LAG book (build_v21_and_test.py):
  - events from data/earnings_events_classified.csv (ticker, quarter, Release_Date, NP_R)
  - entry = Release_Date + 5 sessions (open), exit = Release_Date + 30 sessions (open)
    => 25-session hold ("T+25"), open-to-open, on the GLOBAL session calendar.
  - d_NPR (PIT) from ticker_financial.parquet NP_P0..P5:
        NP_R_cur = NP_P0/NP_P4 - 1 ; NP_R_prior = NP_P1/NP_P5 - 1 ; d_NPR = cur - prior
        guard NP_P4==0 or NP_P5==0 -> NaN
  - pool gate (task): NP_R > 0  (positive surprise).
  - Split A: d_NPR>=0 (accelerating) vs B: d_NPR<0 (decelerating).
  - IS=2014-2019, OOS=2020+ by Release_Date year.
"""
import numpy as np, pandas as pd, duckdb

BQC = "data/bq_cache"
WIN = 1.0  # winsor pct each tail for mean robustness

# ---------- 1. events ----------
ev = pd.read_csv("data/earnings_events_classified.csv", parse_dates=["Release_Date"])
ev = ev[["ticker","quarter","Release_Date","NP_R","post_ret"]].copy()

# ---------- 2. d_NPR from financial parquet ----------
fin = duckdb.sql(f"""
  SELECT ticker, quarter, Release_Date, NP_P0,NP_P1,NP_P4,NP_P5
  FROM read_parquet('{BQC}/ticker_financial.parquet')
""").df()
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])
def safe_yoy(num, den):
    den = den.where(den != 0, np.nan)
    return num/den - 1.0
fin["NP_R_cur"]   = safe_yoy(fin["NP_P0"], fin["NP_P4"])
fin["NP_R_prior"] = safe_yoy(fin["NP_P1"], fin["NP_P5"])
fin["d_NPR"]      = fin["NP_R_cur"] - fin["NP_R_prior"]
ev = ev.merge(fin[["ticker","quarter","Release_Date","d_NPR"]],
              on=["ticker","quarter","Release_Date"], how="left")

# ---------- 3. faithful T+25 open-to-open from ticker_prune ----------
px = duckdb.sql(f"""
  SELECT time, ticker, Open FROM read_parquet('{BQC}/ticker_prune.parquet')
  WHERE time >= DATE '2009-06-01'
""").df()
px["time"] = pd.to_datetime(px["time"])
px_open = (px.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first")
             .sort_index())
all_dt = np.array(px_open.index.values)           # global session calendar
px_open = px_open.ffill(limit=5)

def off(rdt, k):
    r = np.datetime64(pd.Timestamp(rdt))
    p = np.searchsorted(all_dt, r, side="right") - 1
    if p < 0: return None
    t = p + k
    return t if 0 <= t < len(all_dt) else None

def ret25(row):
    tk = row["ticker"]
    if tk not in px_open.columns: return np.nan
    ie, ix = off(row["Release_Date"], 5), off(row["Release_Date"], 30)
    if ie is None or ix is None: return np.nan
    pe = px_open.iat[ie, px_open.columns.get_loc(tk)]
    pxx = px_open.iat[ix, px_open.columns.get_loc(tk)]
    if not (pe > 0) or not (pxx > 0): return np.nan
    return (pxx/pe - 1.0) * 100.0   # percent

ev["ret25"] = ev.apply(ret25, axis=1)

# ---------- 4. filter pool + windows ----------
ev["year"] = ev["Release_Date"].dt.year
pool = ev[(ev["NP_R"] > 0) & ev["d_NPR"].notna() & ev["ret25"].notna()].copy()
pool["win"] = np.where(pool["year"].between(2014,2019), "IS",
              np.where(pool["year"] >= 2020, "OOS", "PRE"))

def wmean(x):
    x = np.asarray(x, float)
    if len(x) < 5: return np.nan
    lo, hi = np.nanpercentile(x, [WIN, 100-WIN])
    return np.nanmean(np.clip(x, lo, hi))

def stats(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    n = len(x)
    if n == 0: return dict(n=0)
    mean = wmean(x); med = np.median(x)
    hit = (x > 0).mean()*100
    sharpe = mean/np.std(x) if np.std(x) > 0 else np.nan   # per-trade Sharpe (winsor mean / raw std)
    return dict(n=n, mean=round(mean,2), med=round(med,2),
                hit=round(hit,1), sharpe=round(sharpe,3))

print("="*78)
print("LAG ΔNP_R event-study | pool: NP_R>0 | T+25 open-to-open (Release+5→+30)")
print("="*78)
rows=[]
for win in ["IS","OOS","PRE"]:
    sub = pool[pool["win"]==win]
    A = stats(sub[sub["d_NPR"]>=0]["ret25"])
    B = stats(sub[sub["d_NPR"]<0]["ret25"])
    rows.append((win,"A d_NPR>=0",A))
    rows.append((win,"B d_NPR<0", B))
    print(f"\n--- {win} (Release_Date yr) ---")
    for lbl,s in [("A d_NPR>=0 (accel)",A),("B d_NPR<0  (decel)",B)]:
        print(f"  {lbl}: n={s.get('n')} mean={s.get('mean')}% med={s.get('med')}% "
              f"hit={s.get('hit')}% sharpe={s.get('sharpe')}")
    if A.get('n') and B.get('n'):
        print(f"  A-B spread: mean {round(A['mean']-B['mean'],2)}pp  hit {round(A['hit']-B['hit'],1)}pp")

# full-pool (all yrs) for reference
print("\n--- FULL (2011+) ---")
A = stats(pool[pool["d_NPR"]>=0]["ret25"]); B = stats(pool[pool["d_NPR"]<0]["ret25"])
print(f"  A: n={A['n']} mean={A['mean']}% hit={A['hit']}% sharpe={A['sharpe']}")
print(f"  B: n={B['n']} mean={B['mean']}% hit={B['hit']}% sharpe={B['sharpe']}")

# ---------- 5. robustness: actual live LAG gate NP_R>=15 ----------
print("\n"+"="*78)
print("ROBUSTNESS — actual deployed LAG entry gate NP_R>=15 (subset)")
print("="*78)
g = ev[(ev["NP_R"]>=15) & ev["d_NPR"].notna() & ev["ret25"].notna()].copy()
g["win"] = np.where(g["year"].between(2014,2019),"IS",
           np.where(g["year"]>=2020,"OOS","PRE"))
for win in ["IS","OOS"]:
    sub=g[g["win"]==win]
    A=stats(sub[sub["d_NPR"]>=0]["ret25"]); B=stats(sub[sub["d_NPR"]<0]["ret25"])
    print(f"  {win}: A n={A.get('n')} mean={A.get('mean')}% hit={A.get('hit')}% | "
          f"B n={B.get('n')} mean={B.get('mean')}% hit={B.get('hit')}%")

# stash for verdict
pool.to_csv("data/lag_dnpr_pool.csv", index=False)
print("\n[saved] data/lag_dnpr_pool.csv  rows=",len(pool))
