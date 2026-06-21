"""One-time FULL rebuild of the 3 LAG caches from BQ, bypassing the broken incremental load.
The existing ba_v11_*/earnings_* pickles were written with a newer-pandas StringDtype that
pandas 2.3.3 cannot deserialize. refresh_lagged_caches.py can't fix them (it loads-then-appends).
This does a clean full pull and writes with plain object dtype (loadable here). Schemas match
exactly what pt_v23_audit_2014.py / pt_v22_dt5g.py / pt_dates.detect_end_date consume.
"""
import subprocess, io, pickle
import numpy as np, pandas as pd

WD = "/home/trido/thanhdt/WorkingClaude"; PROJ = "lithe-record-440915-m9"

def bq(sql):
    r = subprocess.run(["bq","query","--use_legacy_sql=false",f"--project_id={PROJ}","--format=csv","--max_rows=20000000",sql],
                       capture_output=True, text=True)
    if r.returncode: raise RuntimeError(r.stderr[-1000:])
    return pd.read_csv(io.StringIO(r.stdout))

def save(obj, name):
    obj = obj.copy()
    if "ticker" in obj.columns:
        obj["ticker"] = obj["ticker"].astype(object)   # force plain object -> avoids StringDtype pickle trap
    for c in obj.columns:
        if obj[c].dtype == "string": obj[c] = obj[c].astype(object)
    with open(f"{WD}/{name}", "wb") as f: pickle.dump(obj, f)
    print(f"  wrote {name}: {len(obj):,} rows, cols={list(obj.columns)}")

# ── 3. earnings_surprise_data.pkl (full re-pull; same query as refresh_lagged_caches.py) ──
print("[3] earnings_surprise_data.pkl ...")
fin = bq("""SELECT f.ticker, f.quarter, f.time, f.Release_Date,
       f.NP_P0, f.NP_P1, f.NP_P2, f.NP_P3, f.NP_P4, f.NP_P5, f.NP_P6, f.NP_P7,
       f.NP_R, f.Revenue_YoY_P0
FROM tav2_bq.ticker_financial AS f
WHERE f.Release_Date IS NOT NULL AND f.Release_Date >= '2009-01-01' AND f.NP_P0 IS NOT NULL""")
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"]); fin["time"] = pd.to_datetime(fin["time"])
save(fin, "data/earnings_surprise_data.pkl")
universe = sorted(fin["ticker"].dropna().unique())
print(f"  LAG universe = {len(universe)} earnings tickers")
inl = ",".join(f"'{t}'" for t in universe)

# ── 1. earnings_px.pkl  (ticker, time, Close) ──
print("[1] earnings_px.pkl ...")
px = bq(f"""SELECT t.ticker, t.time, t.Close FROM tav2_bq.ticker AS t
WHERE t.ticker IN ({inl}) AND t.time >= DATE '2011-01-01' AND t.Close > 0""")
px["time"] = pd.to_datetime(px["time"])
px = px.drop_duplicates(["ticker","time"]).sort_values(["ticker","time"]).reset_index(drop=True)
save(px, "data/earnings_px.pkl")

# ── 2. lagged_pos_ov.pkl  (ticker, time, Open, Volume_3M_P50) ──
print("[2] lagged_pos_ov.pkl ...")
ov = bq(f"""SELECT t.ticker, t.time, t.Open, t.Volume_3M_P50 FROM tav2_bq.ticker AS t
WHERE t.ticker IN ({inl}) AND t.time >= DATE '2011-01-01' AND t.Close > 0""")
ov["time"] = pd.to_datetime(ov["time"])
ov = ov.drop_duplicates(["ticker","time"]).sort_values(["ticker","time"]).reset_index(drop=True)
save(ov, "data/lagged_pos_ov.pkl")

# ── verify all 3 reload cleanly + coverage check vs events CSV ──
print("\n[verify] reload + coverage:")
for nm in ["data/earnings_surprise_data.pkl","data/earnings_px.pkl","data/lagged_pos_ov.pkl"]:
    o = pickle.load(open(f"{WD}/{nm}","rb"))
    print(f"  {nm}: reload OK, {len(o):,} rows, time max {pd.to_datetime(o['time']).max().date()}")
ev = pd.read_csv(f"{WD}/data/earnings_events_classified.csv")
miss = set(ev["ticker"].unique()) - set(universe)
print(f"  events_classified tickers not in LAG universe: {len(miss)} {sorted(miss)[:10]}")
