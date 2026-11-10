import pandas as pd, numpy as np, glob, subprocess, io, os
R="/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-mike-lagadj-1110/agents/Taylor/research/lag_cache_adjusted_20261110"
H={}
for leg in ["off","1m"]:
  for t in ["ctrl","adj"]:
    p=glob.glob(f"{R}/sandbox_{t}/data/*exp_r3z_{t}_p0_{leg}_univpit*.csv")[0]
    x=pd.read_csv(p,low_memory=False)
    tx=x[(x.record_type=="TX")&(x.book=="LAG")].copy()
    for c in ["buy_amount","sell_amount","fee"]: tx[c]=pd.to_numeric(tx[c],errors="coerce").fillna(0)
    g=tx.groupby(["ticker","holding_id"]).agg(first=("ymd","min"),last=("ymd","max"),buy=("buy_amount","sum"),sell=("sell_amount","sum"),fee=("fee","sum")).reset_index()
    g["pnl"]=g.sell-g.buy-g.fee; g["first"]=pd.to_datetime(g["first"]).dt.normalize()
    H[(leg,t)]=g
tks=sorted(set().union(*[set(g.ticker) for g in H.values()]))
inl=",".join(f'"{t}"' for t in tks)
sql=f'SELECT t.ticker, t.time, t.Volume_3M_P50 v FROM tav2_bq.ticker AS t WHERE t.ticker IN ({inl}) AND t.time BETWEEN "2014-01-01" AND "2026-06-30"'
cache="/tmp/qs_lagadj/liq.csv"
if not os.path.exists(cache):
    out=subprocess.run(["bq","query","--use_legacy_sql=false","--project_id=lithe-record-440915-m9","--format=csv","--max_rows=5000000",sql],capture_output=True,text=True)
    open(cache,"w").write(out.stdout)
L=pd.read_csv(cache); L["time"]=pd.to_datetime(L.time)
L=L.set_index(["ticker","time"]).v
for leg in ["off","1m"]:
  r={}
  for t in ["ctrl","adj"]:
    g=H[(leg,t)].copy(); g["liq"]=[L.get((a,b),np.nan) for a,b in zip(g.ticker,g["first"])]
    z=g[~(g.liq>0)]
    print(leg,t,"  of which liq==0 (ADV 0 thật):",int((g.liq==0).sum()),"| liq NaN (không có dòng BQ — ETF/rổ):",int(g.liq.isna().sum()),"| liq<0:",int((g.liq<0).sum()), "| pnl liq==0 B", round(g[g.liq==0].pnl.sum()/1e9,2))
    r[t]=z; print(leg,t,"LAG holdings",len(g),"liq<=0/NaN at first buy:",len(z),"pnl B",round(z.pnl.sum()/1e9,2),"buy B",round(z.buy.sum()/1e9,1),"| total LAG pnl",round(g.pnl.sum()/1e9,2))
    print("   by year pnl B:", z.groupby(z["first"].dt.year).pnl.sum().div(1e9).round(2).to_dict())
  print(leg,"liq0 pnl adj-ctrl B:", round((r["adj"].pnl.sum()-r["ctrl"].pnl.sum())/1e9,2))
