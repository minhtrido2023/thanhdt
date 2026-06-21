#!/usr/bin/env python3
"""
qt_v4x_concentrated.py — concentrated QT v4.x sleeve (5/8/12 names)
===================================================================
Diagnosis from qt_v4x_sleeve.py: a 25-name mechanical sleeve dilutes the
multibagger edge to ~index. Test whether CONCENTRATION captures it.

Spec (per the validated lessons):
  - Hold up to N names; fill free slots with highest-PRIORITY fresh signals.
  - PRIORITY: BOTH > VALUE_FEAR-in-CRISIS/BEAR > VALUE_FEAR > GROWTH-bluechip;
    tie-break cheaper (lower pe_z).
  - HOLD LONG: never sell on rules; drop only if FA tier → E. Let winners ride
    (equal-weight NEW money only; no forced down-rebalance) → low turnover.
  - NO state cash-timing (timing hurt in v1 sleeve) → deploy ~fully when signals exist.
Variants: TOP5 / TOP8 / TOP12 / FULL25 / VNINDEX. Report wealth/CAGR/MaxDD/vsVNI +
the actual TOP5 holdings & per-name contribution (transparency; concentration=luck-sensitive).
Output: data/qt_v4x_concentrated.md
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import os, subprocess, tempfile, pickle
from io import StringIO
import numpy as np, pandas as pd

WORKDIR=r"/home/trido/thanhdt/WorkingClaude"
PROJECT="lithe-record-440915-m9"
BQ_BIN=r"bq"
TC=0.0025
PRI={"BOTH":3,"VALUE_FEAR":2,"GROWTH":1}

def bq_query(sql):
    with tempfile.NamedTemporaryFile(mode="w",suffix=".sql",delete=False,encoding="utf-8") as f:
        f.write(sql); tmp=f.name
    try:
        cmd=f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=200000'
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=600,shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    return pd.read_csv(StringIO(r.stdout.strip()))

def main():
    lines=[]; P=lambda s="":(print(s),lines.append(s))
    fa=pd.read_csv(os.path.join(WORKDIR,"fa_ratings_lh.csv"),parse_dates=["time","Release_Date"])
    fa=fa.sort_values(["ticker","quarter"]).reset_index(drop=True)
    fa["eff_release"]=fa["Release_Date"].fillna(fa["time"]+pd.Timedelta(days=60))
    fa["is_ab"]=fa["tier"].isin(["A","B"]).astype(int)
    fa["qnum"]=fa.groupby("ticker").cumcount()+1
    fa["pct_AB"]=fa.groupby("ticker")["is_ab"].cumsum()/fa["qnum"]*100
    fa["valid_hist"]=fa["qnum"]>=12

    panel=pickle.load(open(os.path.join(WORKDIR,"qt_panel_2014_2026.pkl"),"rb"))
    panel["time"]=pd.to_datetime(panel["time"]); panel=panel.sort_values(["ticker","time"]).reset_index(drop=True)
    panel["hi52"]=panel.groupby("ticker")["Close"].transform(lambda x:x.rolling(252,min_periods=60).max())
    panel["dd52"]=(panel["Close"]/panel["hi52"]-1)*100
    panel["pe_z"]=((panel["PE"]-panel["PE_MA5Y"])/panel["PE_SD5Y"].replace(0,np.nan)).clip(-10,10)
    panel["pb_z"]=((panel["PB"]-panel["PB_MA5Y"])/panel["PB_SD5Y"].replace(0,np.nan)).clip(-10,10)
    panel["liqv"]=panel["Volume_3M_P50"]*panel["Close"]
    fin=pickle.load(open(os.path.join(WORKDIR,"qt_v4_fin.pkl"),"rb"))
    fin["eff_release"]=pd.to_datetime(fin["Release_Date"]).fillna(pd.to_datetime(fin["q_time"])+pd.Timedelta(days=60))

    panel=panel.sort_values("time")
    fa_a=fa.sort_values("eff_release")[["ticker","eff_release","tier","pct_AB","valid_hist","MktCap"]].rename(columns={"eff_release":"time"})
    panel=pd.merge_asof(panel,fa_a,on="time",by="ticker",direction="backward")
    fin_a=fin.sort_values("eff_release")[["ticker","eff_release","NP_R","Revenue_YoY_P0"]].rename(columns={"eff_release":"time"})
    panel=pd.merge_asof(panel,fin_a,on="time",by="ticker",direction="backward")
    panel=panel.sort_values(["ticker","time"]).reset_index(drop=True)

    qok=(panel["pct_AB"]>=70)&(panel["valid_hist"])&(panel["tier"].isin(["A","B"]))&(panel["liqv"]>=5e9)
    sig_g=qok&(panel["NP_R"]>=0.20)&(panel["Revenue_YoY_P0"]>=0.20)
    sig_v=qok&((panel["pe_z"]<-1)|(panel["pb_z"]<-1)|(panel["dd52"]<-30))
    panel["mc_pct"]=panel[qok].groupby("time")["MktCap"].rank(pct=True)
    panel["entry"]=sig_g|sig_v
    panel["etype"]=np.where(sig_g&sig_v,"BOTH",np.where(sig_g,"GROWTH","VALUE_FEAR"))
    panel.loc[(panel["etype"]=="GROWTH")&(panel["mc_pct"]<0.667),"entry"]=False  # growth=bluechip only
    panel["is_E"]=panel["tier"].eq("E")

    st=bq_query("SELECT s.time,s.state FROM tav2_bq.vnindex_5state_dt5g_live AS s ORDER BY s.time")
    st["time"]=pd.to_datetime(st["time"]); st=st.set_index("time")["state"]

    px=panel.pivot_table(index="time",columns="ticker",values="Close",aggfunc="first").sort_index().ffill()
    didx=px.index; st_ff=st.reindex(didx).ffill()
    # per-month fresh entries with score
    ent_by_m={}
    panel["fresh"]=panel.groupby("ticker")["entry"].transform(lambda x:x&~x.shift(1,fill_value=False))
    for d,g in panel.groupby("time"):
        e=g[g["fresh"]]
        if len(e)==0: ent_by_m[d]=[]; continue
        s=int(st_ff.get(d,3)) if pd.notna(st_ff.get(d,np.nan)) else 3
        rows=[]
        for _,r in e.iterrows():
            score=PRI.get(r["etype"],0)*10+(3 if s in(1,2) else 0)+(-r["pe_z"] if pd.notna(r["pe_z"]) else 0)
            rows.append((r["ticker"],r["etype"],score))
        rows.sort(key=lambda x:-x[2]); ent_by_m[d]=rows
    isE_by_m={d:set(g[g["is_E"]]["ticker"]) for d,g in panel.groupby("time")}

    me=pd.Series(didx).groupby([didx.year,didx.month]).max().values
    rebal=pd.DatetimeIndex(sorted(me)); rebal=rebal[(rebal>=pd.Timestamp("2014-06-01"))&(rebal<=pd.Timestamp("2026-05-15"))]
    def price(d,t):
        s=px.loc[:d,t] if t in px.columns else pd.Series(dtype=float); s=s.dropna()
        return s.iloc[-1] if len(s) else np.nan

    MAX_HOLD_M=36  # ~3Y rotation: free slot to capture later multibaggers
    def run(N,track=False,park=False,vni_ret=None):
        cash=1.0; sh={}; entry_m={}; hist=[]; cost={}; ret={}
        for mi,d in enumerate(rebal):
            if park and mi>0 and vni_ret is not None and pd.notna(vni_ret.iloc[mi]):
                cash*=(1+vni_ret.iloc[mi])  # idle cash parked in index
            # sell: tier->E OR held > MAX_HOLD_M months (rotate)
            for t in list(sh):
                if t in isE_by_m.get(d,set()) or (mi-entry_m.get(t,mi))>=MAX_HOLD_M:
                    p=price(d,t)
                    if pd.notna(p):
                        proc=sh[t]*p*(1-TC); cash+=proc
                        if track: ret[t]=ret.get(t,0)+proc
                    del sh[t]; entry_m.pop(t,None)
            eq=sum(v*price(d,t) for t,v in sh.items() if pd.notna(price(d,t))); nav=cash+eq
            free=N-len(sh)
            if free>0:
                cand=[(t,et) for t,et,_ in ent_by_m.get(d,[]) if t not in sh and t in px.columns and pd.notna(price(d,t))]
                slice_sz=nav/N
                for t,et in cand[:free]:
                    buy=min(slice_sz,cash)
                    if buy<1e-4: break
                    p=price(d,t); sh[t]=sh.get(t,0)+buy/p; cash-=buy; entry_m[t]=mi
                    if track: cost[t]=cost.get(t,0)+buy
            eq=sum(v*price(d,t) for t,v in sh.items() if pd.notna(price(d,t))); nav=cash+eq
            hist.append({"date":d,"nav":nav,"n":len(sh),"cash_pct":cash/nav if nav>0 else 0})
        h=pd.DataFrame(hist).set_index("date")
        # contributions: final value of each ever-held name (approx via last holding)
        contrib=None
        if track:
            last=rebal[-1]
            val={t:ret.get(t,0)+sh.get(t,0)*(price(last,t) if pd.notna(price(last,t)) else 0) for t in cost}
            contrib=pd.DataFrame({"invested":cost,"returned":val}).fillna(0)
            contrib["net"]=contrib["returned"]-contrib["invested"]
        return h,contrib

    vni=bq_query("SELECT t.time,t.Close FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' AND t.time>='2014-01-01' AND t.Close>100 ORDER BY t.time")
    vni["time"]=pd.to_datetime(vni["time"]); vni_m=vni.set_index("time")["Close"].reindex(didx).ffill().reindex(rebal).ffill()
    vni_m=vni_m/vni_m.iloc[0]; vni_ret=vni_m.pct_change()
    res={}
    for N in [5,8,12,25]:
        h,c=run(N,track=(N==5)); res[N]=(h,c)
    # index-parked variants (idle cash earns VNI) — fixes the cash drag
    park={N:run(N,park=True,vni_ret=vni_ret)[0] for N in [5,8,12]}
    def met(nav):
        s=nav.dropna(); yrs=(s.index[-1]-s.index[0]).days/365.25
        return ((s.iloc[-1]/s.iloc[0])**(1/yrs)-1)*100, (((s-s.cummax())/s.cummax()).min())*100, s.iloc[-1]/s.iloc[0]

    P("# QT v4.x — CONCENTRATED sleeve (does concentration capture the multibagger edge?)")
    P("")
    P(f"hold-long, drop only tier→E, no state cash-timing, equal-wt new money, TC {TC:.2%} | {rebal[0].date()}→{rebal[-1].date()}")
    P("")
    P(f"{'variant':<12}{'CAGR':>8}{'MaxDD':>9}{'Wealth':>9}{'vsVNI':>8}{'avg cash%':>10}")
    P("-"*55)
    cv,_,_=met(vni_m)
    for N in [5,8,12,25]:
        h,_=res[N]; c,dd,w=met(h["nav"])
        P(f"{'TOP'+str(N):<12}{c:>+7.2f}%{dd:>+8.2f}%{w:>+9.2f}{c-cv:>+7.2f}{h['cash_pct'].mean()*100:>9.0f}%")
    P(f"{'VNINDEX':<12}{cv:>+7.2f}%{met(vni_m)[1]:>+8.2f}%{met(vni_m)[2]:>+9.2f}")
    P("")
    P("## Idle cash PARKED in index (fixes cash drag — concentrated alpha ON TOP of beta)")
    P(f"{'variant':<14}{'CAGR':>8}{'MaxDD':>9}{'Wealth':>9}{'vsVNI':>8}")
    P("-"*48)
    for N in [5,8,12]:
        c,dd,w=met(park[N]["nav"]); P(f"{'TOP'+str(N)+'_PARK':<14}{c:>+7.2f}%{dd:>+8.2f}%{w:>+9.2f}{c-cv:>+7.2f}")
    P(f"{'VNINDEX':<14}{cv:>+7.2f}%{met(vni_m)[1]:>+8.2f}%{met(vni_m)[2]:>+9.2f}")
    P("")
    # TOP5 transparency
    h5,c5=res[5]
    P("## TOP5 — actual picks & net contribution (invested vs final value, terminal)")
    if c5 is not None:
        c5=c5.sort_values("net",ascending=False)
        P(f"  {len(c5)} names ever held (3Y rotation). Top/bottom by net contribution:")
        P(f"  {'ticker':<8}{'invested':>10}{'returned':>10}{'net':>10}")
        for t,r in pd.concat([c5.head(8),c5.tail(4)]).iterrows():
            P(f"  {t:<8}{r['invested']:>10.3f}{r['returned']:>10.3f}{r['net']:>+10.3f}")
    P("")
    P("Read: if TOP5 >> TOP25 and beats VNI → concentration captures multibaggers (edge real,")
    P("dilution was the killer). If TOP5 ≈ or < TOP25 / noisy → edge not robustly harvestable.")
    P("")
    pd.DataFrame({f"TOP{N}":res[N][0]["nav"] for N in [5,8,12,25]}|{"VNI":vni_m}).to_csv(
        os.path.join(WORKDIR,"data","qt_v4x_concentrated_nav.csv"))
    with open(os.path.join(WORKDIR,"data","qt_v4x_concentrated.md"),"w",encoding="utf-8") as f:
        f.write("\n".join(lines))
    P("Saved data/qt_v4x_concentrated.md")

if __name__=="__main__":
    main()
