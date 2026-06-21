# -*- coding: utf-8 -*-
"""
lag_forensic_audit.py — does the LAG (PEAD) book load peak-earnings / non-operating / forensic names,
and is the damage STATE-conditional (euphoria vs pessimism)? User insight 2026-06-20.
Faithful schedule from earnings_events_classified.csv (NP_R in %, post_ret = PEAD hold return):
  e_lag = NP_R>=15 & prior_n_good>=4 & pa_HL3>=5  (same as build_v21_and_test/pt_lagvn30_audit).
Join: peak_earn=ROE_Trailing/ROE5Y, non_op=NPM>1.2*EBITM, DT5G state @entry, forensic flag.
Analyze post_ret split by state x peak x non_op x forensic.
"""
import os, sys, subprocess, tempfile
from io import StringIO
import numpy as np, pandas as pd
WORKDIR=os.environ.get("WORKDIR_8L","/home/trido/thanhdt/WorkingClaude"); sys.path.insert(0,WORKDIR)
def bq(sql):
    f=tempfile.NamedTemporaryFile(mode="w",suffix=".sql",delete=False); f.write(sql); f.close()
    r=subprocess.run(f'cat {f.name} | bq query --quiet --use_legacy_sql=false --project_id=lithe-record-440915-m9 --format=csv --max_rows=900000',capture_output=True,text=True,shell=True); os.unlink(f.name)
    if not r.stdout.strip(): raise RuntimeError(r.stderr[-700:])
    return pd.read_csv(StringIO(r.stdout.strip()))

ev=pd.read_csv(f"{WORKDIR}/data/earnings_events_classified.csv",parse_dates=["Release_Date"])
ev=ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True)
# faithful prior_n_good + pa_HL3 (decay HL=3y over prior NP_R>=15 events' post_ret)
LN2=np.log(2); HL=3.0; ev["prior_n_good"]=0; ev["pa_HL3"]=np.nan
for tk,g in ev.groupby("ticker"):
    hist=[]
    for ri in g.index.tolist():
        row=ev.loc[ri]; cd=row["Release_Date"]; ev.at[ri,"prior_n_good"]=len(hist)
        if hist:
            da=pd.to_datetime([d for d,_ in hist]); pa=np.array([p for _,p in hist])
            w=np.exp(-LN2*((cd-da).days.values/365.25)/HL); ev.at[ri,"pa_HL3"]=(pa*w).sum()/w.sum() if w.sum()>0 else np.nan
        if pd.notna(row["NP_R"]) and row["NP_R"]>=15 and pd.notna(row["post_ret"]): hist.append((cd,row["post_ret"]))
lag=ev[(ev["NP_R"]>=15)&(ev["prior_n_good"]>=4)&(ev["pa_HL3"]>=5)&(ev["Release_Date"]>="2014-01-01")].copy()

# quality fields by (ticker,quarter)
fin=bq("""SELECT f.ticker,f.quarter,f.NPM_P0,f.EBITM_P0,f.ROE_Trailing FROM tav2_bq.ticker_financial f WHERE f.quarter IS NOT NULL""")
lag=lag.merge(fin,on=["ticker","quarter"],how="left")
# ROE5Y as-of Release_Date + DT5G state as-of
roe5=bq("""SELECT t.ticker,t.time,t.ROE5Y FROM tav2_bq.ticker t WHERE t.time>=DATE '2013-06-01' AND t.ROE5Y IS NOT NULL""")
roe5["time"]=pd.to_datetime(roe5["time"]); roe5=roe5.sort_values("time")
lag=pd.merge_asof(lag.sort_values("Release_Date"),roe5.sort_values("time"),left_on="Release_Date",right_on="time",by="ticker",direction="backward")
st=bq("SELECT s.time,s.state FROM tav2_bq.vnindex_5state_dt5g_live s"); st["time"]=pd.to_datetime(st["time"]); st=st.sort_values("time")
lag=pd.merge_asof(lag.sort_values("Release_Date"),st.sort_values("time"),left_on="Release_Date",right_on="time",direction="backward",suffixes=("","_st"))
lag=lag.dropna(subset=["state","post_ret"]).copy()
lag["peak_earn"]=(lag["ROE_Trailing"]/lag["ROE5Y"].clip(lower=0.02)).clip(0,6)
lag["non_op"]=(lag["NPM_P0"]>1.2*lag["EBITM_P0"])&(lag["EBITM_P0"].notna())
try: fset=set(pd.read_csv(f"{WORKDIR}/data/forensic_flags.csv").query("severity=='exclude'").ticker)
except Exception: fset=set()
lag["forensic"]=lag["ticker"].isin(fset)
SN={1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EXBULL"}

print(f"LAG entries 2014+: {len(lag)}  | peak>1.5: {(lag.peak_earn>1.5).sum()}  non_op: {lag.non_op.sum()}  forensic: {lag.forensic.sum()}")
print("\n### LAG post_ret by DT5G STATE (euphoria vs pessimism) ###")
print(f"  {'state':<9}{'n':>5}{'med%':>8}{'mean%':>8}{'win%':>7}{'crash%':>8}")
for s in (1,2,3,4,5):
    g=lag[lag.state==s]
    if len(g)>=8: print(f"  {SN[s]:<9}{len(g):>5}{g.post_ret.median():>8.2f}{g.post_ret.mean():>8.2f}{100*(g.post_ret>0).mean():>6.0f}%{100*(g.post_ret<-20).mean():>7.0f}%")

print("\n### peak-earnings LAG entries: post_ret, peak>1.5 vs <=1.5, BY STATE ###")
print(f"  {'state':<9}{'group':<11}{'n':>5}{'med%':>8}{'crash%':>8}")
for s in (1,2,3,4,5):
    g=lag[lag.state==s]
    if len(g)<15: continue
    for lbl,sub in [("peak>1.5",g[g.peak_earn>1.5]),("peak<=1.5",g[g.peak_earn<=1.5])]:
        if len(sub)>=5: print(f"  {SN[s]:<9}{lbl:<11}{len(sub):>5}{sub.post_ret.median():>8.2f}{100*(sub.post_ret<-20).mean():>7.0f}%")

print("\n### non-op vs clean (all states, then BEAR/CRISIS only) ###")
for scope,d in [("ALL states",lag),("BEAR+CRISIS",lag[lag.state.isin([1,2])]),("BULL+EXBULL",lag[lag.state.isin([4,5])])]:
    for lbl,sub in [("non_op",d[d.non_op]),("clean",d[~d.non_op])]:
        if len(sub)>=5: print(f"  {scope:<12} {lbl:<7} n={len(sub):>4} med {sub.post_ret.median():+6.2f}% crash {100*(sub.post_ret<-20).mean():>3.0f}%")

print("\n### forensic-flagged names appearing in LAG history ###")
ff=lag[lag.forensic]
print(ff.groupby("ticker").agg(n=("post_ret","size"),med=("post_ret","median")).round(1).to_string() if len(ff) else "  none in schedule historically")
lag.to_csv(f"{WORKDIR}/data/lag_forensic_audit.csv",index=False); print(f"\n-> data/lag_forensic_audit.csv ({len(lag)} rows)")
