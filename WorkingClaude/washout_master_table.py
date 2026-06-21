#!/usr/bin/env python3
"""washout_master_table.py — every market washout (oversold breadth >=40%) since 2014,
with DT5G state + days-to-bottom + basket forward returns. Answers: is a washout a
good buy even when DT5G is NOT crisis?"""
import warnings; warnings.filterwarnings("ignore")
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
W=r"/home/trido/thanhdt/WorkingClaude"
STN={1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}

D=pd.read_csv(os.path.join(W,"data","daily_comovement_dt5g.csv"),parse_dates=["time"]).sort_values("time").reset_index(drop=True)
D["ew"]=(1+D["avg_ret"]).cumprod()
bt=pd.read_csv(os.path.join(W,"data","bt_capitulation_STRONG.csv"),parse_dates=["date"]).set_index("date")

# de-cluster washout days (>=40% oversold), 30d gap = one episode; record PEAK oversold in cluster
ws=D[D["pct_oversold"]>=0.40].copy().sort_values("time")
ws["g"]=ws["time"].diff().dt.days.fillna(999); ws["c"]=(ws["g"]>=30).cumsum()
rows=[]
ewv=D["ew"].values; tv=D["time"].values
for _,grp in ws.groupby("c"):
    d0=grp.iloc[0]["time"]; peak_os=grp["pct_oversold"].max(); ndays=len(grp)
    i0=D.index[D["time"]==d0][0]; st=int(D["state"].iloc[i0])
    # days from signal to EW bottom within next 90 trading days
    H=min(90,len(D)-1-i0); seg=ewv[i0:i0+H+1]
    tmin=int(np.argmin(seg)); further=seg[tmin]/seg[0]-1
    r=bt.loc[d0] if d0 in bt.index else None
    rows.append(dict(
        date=d0.date(), state=st, regime=STN[st], peak_oversold=round(peak_os*100),
        ws_days=ndays, days_to_bottom=tmin, further_drop=round(further*100,1),
        basket60=r["FIX60_ret"] if r is not None else np.nan,
        basket120=r["FIX120_ret"] if r is not None else np.nan,
        tier=r["tier"] if r is not None else "?"))
M=pd.DataFrame(rows)
# repeat-washout flag = another washout within 90 trading days after (grinding bear)
M["rep_after"]=False
for i in range(len(M)-1):
    di=D.index[D["time"]==pd.Timestamp(M.loc[i,"date"])][0]
    dj=D.index[D["time"]==pd.Timestamp(M.loc[i+1,"date"])][0]
    if dj-di<=90: M.loc[i,"rep_after"]=True
M["type"]=np.where(M["rep_after"],"GRIND(repeat)","SHARP(isolated)")

print("="*104)
print("ALL MARKET WASHOUTS (oversold breadth >= 40%), 2014-2026   [basket = 8L quality+golden, 0.3% cost]")
print("="*104)
show=M.copy()
print(show[["date","regime","peak_oversold","ws_days","days_to_bottom","further_drop","basket60","basket120","tier","type"]].to_string(index=False))

def stat(df,lbl):
    b=df["basket60"].dropna()
    print(f"  {lbl:<26} n={len(df):2d} | basket60 mean {b.mean():5.1f}% / median {b.median():5.1f}% / win {100*(b>0).mean():3.0f}%")

print("\n"+"-"*70)
print("SPLIT BY DT5G STATE AT THE WASHOUT:")
stat(M[M.state==1],"CRISIS (state 1)")
stat(M[M.state!=1],"NOT crisis (state 2-5)")
stat(M[M.state==2],"  - BEAR (2)")
stat(M[M.state.isin([3])],"  - NEUTRAL (3)")
stat(M[M.state.isin([4,5])],"  - BULL/EX-BULL (4-5)")
print("\nSPLIT BY SHAPE (does the washout repeat within 90d = grinding bear?):")
stat(M[M["type"].str.startswith("SHARP")],"SHARP / isolated")
stat(M[M["type"].str.startswith("GRIND")],"GRIND / repeated")
M.to_csv(os.path.join(W,"data","washout_master_table.csv"),index=False)
print("\nSaved: data/washout_master_table.csv")
