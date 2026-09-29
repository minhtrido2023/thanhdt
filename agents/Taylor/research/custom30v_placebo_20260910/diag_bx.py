"""Chan doan: vi sao chuoi loi suat GROSS tai lap tu bx khong on dinh giua 2 lan chay."""
import os, sys
import numpy as np, pandas as pd
OUT = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/custom30v_placebo_20260910"
sys.path.insert(0, OUT); sys.path.insert(1, "/home/trido/thanhdt/WorkingClaude")
os.chdir("/home/trido/thanhdt/WorkingClaude")
os.environ.setdefault("BQ_CACHE_THREADS", "1")
os.environ.setdefault("BQ_LOCAL_CACHE", "data/bq_cache_asof20260729_postrestate")
from simulate_holistic_nav import bq
import custom_basket as cb
mem = pd.read_csv(f"{OUT}/members_ctrl.csv")
union = sorted(mem.ticker.unique()); inlist = ",".join(f"'{x}'" for x in union)
bx = bq(f"""WITH fin AS (
  SELECT f.ticker, f.time AS ftime, f.OShares,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS nft
  FROM tav2_bq.ticker_financial AS f WHERE f.OShares IS NOT NULL)
SELECT t.ticker, t.time, t.Close, {cb.pxw_sql()} AS pxw,
       COALESCE(t.Price,t.Close)*t.Volume AS tv, fin.OShares
FROM tav2_bq.ticker AS t
LEFT JOIN fin ON fin.ticker=t.ticker AND t.time>=fin.ftime AND (fin.nft IS NULL OR t.time<fin.nft)
WHERE t.ticker IN ({inlist})
  AND t.time >= DATE '2013-12-23' AND t.time <= DATE '2026-06-19'""")
bx["time"] = pd.to_datetime(bx["time"])
d = bx.groupby(["ticker", "time"]).size()
dup = d[d > 1]
print(f"rows={len(bx):,}  cap (ticker,time) TRUNG = {len(dup):,}  (tren {d.size:,} cap)")
if len(dup):
    k = bx.merge(dup.rename("n").reset_index()[["ticker", "time"]], on=["ticker", "time"])
    g = k.groupby(["ticker", "time"])["OShares"].nunique()
    print(f"  trong so cap trung: {int((g > 1).sum()):,} cap co OShares KHAC NHAU")
    print("  vi du (5 cap dau co OShares khac nhau):")
    for (tk, tm) in g[g > 1].index[:5]:
        print("   ", tk, tm.date(), k[(k.ticker == tk) & (k.time == tm)][["OShares", "Close"]].to_dict("records"))
    yr = pd.Series([t.year for t in g[g > 1].index.get_level_values(1)]).value_counts().sort_index()
    print("  phan bo theo nam:", dict(yr))
    print("  ticker bi dinh:", sorted(set(g[g > 1].index.get_level_values(0)))[:30])
