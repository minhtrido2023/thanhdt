"""A4 việc 1(b,c): so deal LAG/BAL giữa 2 ledger + ADV bq vs pit tại ngày fill. Usage: decomp2.py bq.csv pit.csv"""
import sys, pandas as pd, numpy as np, duckdb
def load(p):
    X = pd.read_csv(p, low_memory=False); X["ymd"] = pd.to_datetime(X["ymd"].astype(str).str[:10], errors="coerce"); return X
A, B = load(sys.argv[1]), load(sys.argv[2])
def tx(X): 
    t = X[X.record_type=="TX"].copy()
    for c in ("shares","buy_amount","sell_amount","fee"): t[c]=t[c].astype(float)
    return t
ta, tb = tx(A), tx(B)
# BAL: byte-same?
for bk in ("BAL",):
    a=ta[ta.book==bk].reset_index(drop=True); b=tb[tb.book==bk].reset_index(drop=True)
    print(f"BAL TX bằng nhau (ticker,ymd,action,shares,buy,sell): {len(a)==len(b) and (a[['ticker','ymd','action','shares','buy_amount','sell_amount']].round(4).equals(b[['ticker','ymd','action','shares','buy_amount','sell_amount']].round(4)))}  n={len(a)}/{len(b)}")
# LAG: holdings
def hold(t):
    t=t[t.book=="LAG"]; g=t.groupby("holding_id")
    h=pd.DataFrame({"ticker":g.ticker.first(),"play":g.play_type.first(),"buy_d":g.apply(lambda d:d.loc[d.action=="buy","ymd"].min()),
       "buy_n":g.apply(lambda d:(d.action=="buy").sum()),"cost":g.buy_amount.sum()+g.fee.sum()*0,"proc":g.sell_amount.sum(),"fee":g.fee.sum(),
       "sell_d":g.apply(lambda d:d.loc[d.action=="sell","ymd"].max())})
    h["key"]=h.ticker+"|"+h.buy_d.dt.strftime("%Y%m%d")+"|"+h.play; h=h.reset_index(drop=True).set_index("key"); return h
ha, hb = hold(ta), hold(tb)
print("holdings LAG:", len(ha), len(hb), "chung id:", len(ha.index.intersection(hb.index)), "chỉ bq:", len(ha.index.difference(hb.index)), "chỉ pit:", len(hb.index.difference(ha.index)))
ha["pnl"]=ha.proc-ha.cost-ha.fee; hb["pnl"]=hb.proc-hb.cost-hb.fee
only_a=ha.loc[ha.index.difference(hb.index)]; only_b=hb.loc[hb.index.difference(ha.index)]; com=ha.index.intersection(hb.index)
print(f"chỉ bq: n={len(only_a)} cost {only_a.cost.sum()/1e9:.1f}B pnl {only_a.pnl.sum()/1e9:+.2f}B | chỉ pit: n={len(only_b)} cost {only_b.cost.sum()/1e9:.1f}B pnl {only_b.pnl.sum()/1e9:+.2f}B")
d=(hb.loc[com,"pnl"]-ha.loc[com,"pnl"]); dc=(hb.loc[com,"cost"]-ha.loc[com,"cost"])
print(f"chung: n={len(com)} Σ pnl bq {ha.loc[com,'pnl'].sum()/1e9:+.2f}B pit {hb.loc[com,'pnl'].sum()/1e9:+.2f}B; khác size(>0.5%) {(dc.abs()/ha.loc[com,'cost']>0.005).sum()}; khác ngày mua đầu {(ha.loc[com,'buy_d']!=hb.loc[com,'buy_d']).sum()}; khác ngày bán cuối {(ha.loc[com,'sell_d']!=hb.loc[com,'sell_d']).sum()}")
print(f"Σ pnl LAG toàn bộ bq {ha.pnl.sum()/1e9:+.1f}B pit {hb.pnl.sum()/1e9:+.1f}B")
for nm,o in (("chỉ bq",only_a),("chỉ pit",only_b)):
    print(f"-- {nm} theo năm mua đầu: "+" ".join(f"{y}:{n}/{p/1e9:+.1f}B" for y,(n,p) in o.groupby(o.buy_d.dt.year).agg(n=("pnl","size"),p=("pnl","sum")).iterrows()))
# top đóng góp khác biệt
dd=pd.concat([ha.pnl.rename("bq"),hb.pnl.rename("pit")],axis=1).fillna(0); dd["d"]=dd.pit-dd.bq
x=dd.sort_values("d"); print("Σ|d| chung / chỉ bq / chỉ pit (tỷ):", round(dd.loc[com].d.sum()/1e9,2), round(dd.loc[only_a.index].d.sum()/1e9,2), round(dd.loc[only_b.index].d.sum()/1e9,2))
jn=ha[["ticker","buy_d"]].combine_first(hb[["ticker","buy_d"]])
for nm,xx in (("xấu nhất",x.head(10)),("tốt nhất",x.tail(10))):
    print(f"top 10 {nm} (pit-bq, tỷ):"); 
    for k,r in xx.iterrows(): print(f"   {k:28s} bq {r.bq/1e9:+7.2f} pit {r.pit/1e9:+7.2f} d {r.d/1e9:+7.2f}")
# ADV bq vs pit tại ngày mua đầu, cho holdings chỉ-1-phía
C="/home/trido/thanhdt/WorkingClaude/data/bq_cache_asof20260729_postrestate/ticker/*.parquet"
tk=sorted(set(only_a.ticker)|set(only_b.ticker)); 
if tk:
    q=duckdb.sql(f"""SELECT ticker,time,Volume,Volume_3M_P50,COALESCE(Price,Close) px FROM read_parquet('{C}') WHERE ticker IN ({','.join("'"+t+"'" for t in tk)})""").df()
    q=q.sort_values(["ticker","time"]); g=q.groupby("ticker")
    q["pit"]=g.Volume.transform(lambda s:s.shift(1).rolling(60,min_periods=20).median())*g.px.shift(1); q["bqv"]=q.Volume_3M_P50*q.px
    q["time"]=pd.to_datetime(q.time)
    for nm,o in (("chỉ bq",only_a),("chỉ pit",only_b)):
        m=o.reset_index().merge(q,left_on=["ticker","buy_d"],right_on=["ticker","time"],how="left")
        print(f"-- {nm}: n={len(m)} | bqADV NULL {m.bqv.isna().sum()} | bqADV<=0 {(m.bqv<=0).sum()} | pitADV NULL {m.pit.isna().sum()} | pitADV<=0 {(m.pit<=0).sum()} | Volume=0 ngày fill {(m.Volume==0).sum()}")
        print("   median bqADV/pitADV (khi cả hai >0):", float((m.bqv/m.pit)[(m.bqv>0)&(m.pit>0)].median()))
