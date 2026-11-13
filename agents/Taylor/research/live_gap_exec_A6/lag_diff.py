"""A6 việc 2: lệnh LAG khác nhau L1 (LIQ off, ADV bq) vs L3P (lag+pit) ở cùng NAV. Lệnh = holding (ticker, ngày fill đầu).
Phân loại lệnh chỉ-L1 theo pit-ADV ngày fill đầu (ĐÚNG công thức engine pit, cache pin-era) và Volume_3M_P50 BQ (cổng live/engine bq):
  'ảo' = Volume_3M_P50 NULL/≤0 ngày fill (L1 mua trọn size không trần; L2/L3P chặn). Usage: lag_diff.py L1.csv L3P.csv"""
import sys, numpy as np, pandas as pd, duckdb
WC = "/home/trido/thanhdt/WorkingClaude"
def H(p):
    T = pd.read_csv(p, low_memory=False); T = T[(T.record_type == "TX") & (T.book == "LAG") & (T.action == "buy") & T.play_type.isin(["LAG_HI", "LAG_LO"])]
    T["ymd"] = pd.to_datetime(T.ymd); g = T.groupby("holding_id").agg(ticker=("ticker", "first"), d0=("ymd", "min"), amt=("buy_amount", "sum"))
    g["key"] = list(zip(g.ticker, g.d0)); return g.set_index("key")
a, b = H(sys.argv[1]), H(sys.argv[2])
tks = sorted(set(a.ticker) | set(b.ticker))
px = duckdb.sql(f"""SELECT ticker, CAST(time AS DATE) AS time, Volume, Volume_3M_P50 FROM read_parquet('{WC}/data/bq_cache_asof20260729_postrestate/ticker/*.parquet')
 WHERE ticker IN ({','.join(repr(t) for t in tks)})""").df()
px["time"] = pd.to_datetime(px.time); px = px.sort_values(["ticker", "time"], kind="mergesort")
px["vpit"] = px.groupby("ticker").Volume.transform(lambda x: x.shift(1).rolling(60, min_periods=20).median())
look = px.set_index(["ticker", "time"])
def cls(df):
    v = look.reindex(list(df.index)); ph = ~(v.Volume_3M_P50 > 0).values; z = ~(v.vpit > 0).values
    return ph, z
oa, ob = a.index.difference(b.index), b.index.difference(a.index)
print(f"L1 {len(a)} lệnh ({a.amt.sum()/1e9:.1f} tỷ), L3P {len(b)} lệnh ({b.amt.sum()/1e9:.1f} tỷ); chung {len(a.index.intersection(b.index))}; chỉ-L1 {len(oa)}; chỉ-L3P {len(ob)}")
ph, z = cls(a.loc[oa]); x = a.loc[oa]
print(f"  chỉ-L1: BQ Volume_3M_P50 NULL/≤0 ngày fill (fill ảo) {ph.sum()} lệnh, {x.amt[ph].sum()/1e9:.1f} tỷ = {x.amt[ph].sum()/a.amt.sum():.1%} vốn mua LAG L1; trong đó pit-ADV(60 phiên) ≤0/thiếu {(ph & z).sum()}")
ph1, z1 = cls(a); print(f"  toàn L1: lệnh fill ảo {ph1.sum()} ({a.amt[ph1].sum()/a.amt.sum():.1%} vốn mua LAG), pit≤0 trong đó {(ph1 & z1).sum()}")
ph2, _ = cls(b); print(f"  toàn L3P: lệnh ngày fill BQ P50 NULL/≤0 {ph2.sum()} (phải ~0 nếu pit cũng ≤0 — pit>0 vẫn mua được)")
