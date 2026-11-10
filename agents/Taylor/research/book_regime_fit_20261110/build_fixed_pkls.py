"""Build NON-canonical price pkls with the gap sessions filled from live BQ (never overwrite data/*.pkl).
Gap sessions = dates where pkl has < 50 tickers although it is a weekday trading session (BQ has >800).
Variant A  (raw, minimal): keep every existing pkl cell untouched; ADD rows for gap dates from BQ on RAW basis:
           Close_raw = BQ.Price ; Open_raw = BQ.Open * (BQ.Price / BQ.Close)   (ratio Price/Close constant between ex-dates).
           Same basis as pkl (pkl Close = price at fetch time = raw, no later dividend adjustment) -> cash dividends NOT credited.
           ex-date trap (ticker_price_stale_on_exdate): BQ.Price on an ex-date row may be stale-CUM -> on rows where
           Price/Close differs from the previous day's ratio by >0.5% and Close moved <3%, use Close (post-ex) instead.
Variant B  (total-return adjusted): for dates > ANCHOR use BQ.Close (adjusted, vintage today) scaled per ticker by
           f = pkl_Close(ANCHOR) / BQ_Close(ANCHOR) so the series splices onto the pkl history; Open scaled likewise.
           Cash dividends / splits after ANCHOR are then credited through the price path (ex-date drop disappears).
Volume_3M_P50 gap cells: BQ value (non-adjusted quantity).
"""
import pickle, pandas as pd, numpy as np
WC="/home/trido/thanhdt/WorkingClaude"; R=f"{WC}/mike/agents/Taylor/research/book_regime_fit_20261110"
px=pickle.load(open(f"{WC}/data/earnings_px.pkl","rb")); px["time"]=pd.to_datetime(px["time"])
ov=pickle.load(open(f"{WC}/data/lagged_pos_ov.pkl","rb")); ov["time"]=pd.to_datetime(ov["time"])
bq=pd.read_csv(f"{R}/data/lag_px_bq_fixed_2026H2.csv",parse_dates=["time"])
cnt=px.groupby("time").ticker.nunique()
gap=sorted(d for d in cnt.index if d>=pd.Timestamp("2026-06-01") and cnt[d]<50 and d.weekday()<5)
bqd=set(bq.time.unique()); gap=[d for d in gap if d in bqd]
print("gap dates:",[str(d.date()) for d in gap])
ANCHOR=pd.Timestamp("2026-06-24")
bq["ratio"]=bq.Price/bq.Close
# --- Variant A
a=bq[bq.time.isin(gap)].copy()
prev=bq.sort_values("time").groupby("ticker").ratio.shift(1)
bq["prev_ratio"]=prev
a=a.merge(bq[["ticker","time","prev_ratio"]],on=["ticker","time"],how="left")
stale=(abs(a.ratio/a.prev_ratio-1)>0.005)&(abs(a.Close/a.Price-1)<0.2)&a.prev_ratio.notna()
a["Close_raw"]=a.Price; a["Open_raw"]=a.Open*a.ratio
print("rows",len(a),"ex-date-stale-suspect rows (dropped to Close basis):",int(stale.sum()))
a.loc[stale,"Close_raw"]=a.loc[stale,"Close"]; a.loc[stale,"Open_raw"]=a.loc[stale,"Open"]
newpx=a[["ticker","time"]].assign(Close=a.Close_raw)
newov=a[["ticker","time"]].assign(Open=a.Open_raw,Volume_3M_P50=a.Volume_3M_P50)
# drop the near-empty pkl rows on gap dates then add full rows
pxA=pd.concat([px[~px.time.isin(gap)],newpx],ignore_index=True).sort_values(["ticker","time"]).reset_index(drop=True)
ovA=pd.concat([ov[~ov.time.isin(gap)],newov],ignore_index=True).sort_values(["ticker","time"]).reset_index(drop=True)
pickle.dump(pxA,open(f"{R}/engine/earnings_px_fixedA.pkl","wb")); pickle.dump(ovA,open(f"{R}/engine/lagged_pos_ov_fixedA.pkl","wb"))
# --- Variant B
anc=px[px.time==ANCHOR].set_index("ticker").Close; ancq=bq[bq.time==ANCHOR].set_index("ticker").Close
f=(anc/ancq).dropna().rename("f")
b=bq[bq.time>ANCHOR].merge(f,left_on="ticker",right_index=True,how="inner")
b["Close_s"]=b.Close*b.f; b["Open_s"]=b.Open*b.f
bpx=b[["ticker","time"]].assign(Close=b.Close_s); bov=b[["ticker","time"]].assign(Open=b.Open_s,Volume_3M_P50=b.Volume_3M_P50)
pxB=pd.concat([px[px.time<=ANCHOR],bpx],ignore_index=True).sort_values(["ticker","time"]).reset_index(drop=True)
ovB=pd.concat([ov[ov.time<=ANCHOR],bov],ignore_index=True).sort_values(["ticker","time"]).reset_index(drop=True)
pickle.dump(pxB,open(f"{R}/engine/earnings_px_fixedB.pkl","wb")); pickle.dump(ovB,open(f"{R}/engine/lagged_pos_ov_fixedB.pkl","wb"))
for n,x in [("A",pxA),("B",pxB)]:
    c=x.groupby("time").ticker.nunique(); print(n,"min tickers/day since 2026-06-01 weekdays:",int(c["2026-06-01":][c["2026-06-01":].index.weekday<5].min()))
