#!/usr/bin/env python3
"""
qt_v4x_sleeve.py — realistic long-horizon QUALITY sleeve (user spec 2026-05-29)
================================================================================
Builds the actual investment sleeve from the validated QT v4.x findings:
  - Universe = QT v4.x quality archetype picks (priority: BOTH > VALUE_FEAR in
    CRISIS/BEAR > VALUE_FEAR other > GROWTH-bluechip).
  - HOLD LONG, low turnover: never sell on rules (hold beats all exits); drop a
    name only if FA tier → E. Let winners run (no forced down-rebalance).
  - State-aware accumulation (DT5G): target equity exposure by state breathes the
    cash buffer — heavy in CRISIS/BEAR (deploy dry powder into cheap quality),
    light in BULL/EX-BULL (raise dry powder). Names don't churn; only equity/cash %.
  - Equal-weight new-money per name; positions ride after.

Measured for the LONG-TERM GOAL (not Sharpe-obsessed): wealth multiple, CAGR,
MaxDD (context), vs VNINDEX, avg equity%, turnover, top contributors.
Variants: SLEEVE_STATE (this), SLEEVE_FULL (always 100%, no state breathing), VNI.
Output: data/qt_v4x_sleeve.md + data/qt_v4x_sleeve_nav.csv
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
N_MAX=25; TC=0.0025
TEQ={1:1.00,2:0.95,3:0.80,4:0.65,5:0.50}   # state-aware target equity
PRIORITY={"BOTH":3,"VALUE_FEAR":2,"GROWTH":1}

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
    fa=pd.read_csv(os.path.join(WORKDIR,"data/fa_ratings_lh.csv"),parse_dates=["time","Release_Date"])
    fa=fa.sort_values(["ticker","quarter"]).reset_index(drop=True)
    fa["eff_release"]=fa["Release_Date"].fillna(fa["time"]+pd.Timedelta(days=60))
    fa["is_ab"]=fa["tier"].isin(["A","B"]).astype(int)
    fa["qnum"]=fa.groupby("ticker").cumcount()+1
    fa["pct_AB"]=fa.groupby("ticker")["is_ab"].cumsum()/fa["qnum"]*100
    fa["valid_hist"]=fa["qnum"]>=12

    panel=pickle.load(open(os.path.join(WORKDIR,"data/qt_panel_2014_2026.pkl"),"rb"))
    panel["time"]=pd.to_datetime(panel["time"]); panel=panel.sort_values(["ticker","time"]).reset_index(drop=True)
    panel["hi52"]=panel.groupby("ticker")["Close"].transform(lambda x:x.rolling(252,min_periods=60).max())
    panel["dd52"]=(panel["Close"]/panel["hi52"]-1)*100
    panel["pe_z"]=((panel["PE"]-panel["PE_MA5Y"])/panel["PE_SD5Y"].replace(0,np.nan)).clip(-10,10)
    panel["pb_z"]=((panel["PB"]-panel["PB_MA5Y"])/panel["PB_SD5Y"].replace(0,np.nan)).clip(-10,10)
    panel["liqv"]=panel["Volume_3M_P50"]*panel["Close"]
    fin=pickle.load(open(os.path.join(WORKDIR,"data/qt_v4_fin.pkl"),"rb"))
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
    panel["is_E"]=panel["tier"].eq("E")
    # GROWTH entry only counts for blue-chips (validated: growth-smallmid weak)
    panel.loc[(panel["etype"]=="GROWTH")&(panel["mc_pct"]<0.667),"entry"]=False

    # DT5G state daily
    st=bq_query("SELECT s.time,s.state FROM tav2_bq.vnindex_5state_dt5g_live AS s ORDER BY s.time")
    st["time"]=pd.to_datetime(st["time"]); st=st.set_index("time")["state"]

    # pivots
    px=panel.pivot_table(index="time",columns="ticker",values="Close",aggfunc="first").sort_index().ffill()
    didx=px.index
    entry_tk={}; etype_tk={}; isE={}
    for d,g in panel.groupby("time"):
        e=g[g["entry"]]
        entry_tk[d]=dict(zip(e["ticker"],e["etype"]))
        isE[d]=set(g[g["is_E"]]["ticker"])
    st_ff=st.reindex(didx).ffill()

    # monthly grid
    me=pd.Series(didx).groupby([didx.year,didx.month]).max().values
    rebal=pd.DatetimeIndex(sorted(me)); rebal=rebal[(rebal>=pd.Timestamp("2014-06-01"))&(rebal<=pd.Timestamp("2026-05-15"))]

    def price(d,t):
        s=px.loc[:d,t] if t in px.columns else pd.Series(dtype=float); s=s.dropna()
        return s.iloc[-1] if len(s) else np.nan

    def run(state_aware):
        cash=1.0; sh={}; hist=[]; turn_tot=0; eq_sum=0
        for d in rebal:
            s=st_ff.get(d); s=int(s) if pd.notna(s) else 3
            # drop tier-E names (hard floor)
            for t in [t for t in list(sh) if t in isE.get(d,set())]:
                p=price(d,t)
                if pd.notna(p): cash+=sh[t]*p*(1-TC); turn_tot+=sh[t]*p
                del sh[t]
            eq=sum(v*price(d,t) for t,v in sh.items() if pd.notna(price(d,t)))
            nav=cash+eq
            teq=TEQ[s] if state_aware else 1.0
            target_eq=teq*nav
            # candidate new names (entry this month, not held), priority order
            cands=[(t,et) for t,et in entry_tk.get(d,{}).items() if t not in sh and t in px.columns and pd.notna(price(d,t))]
            cands.sort(key=lambda x:-PRIORITY.get(x[1],0))
            slice_sz=nav/N_MAX
            if eq < target_eq-1e-9:  # DEPLOY
                budget=target_eq-eq
                # 1) new names
                for t,et in cands:
                    if len(sh)>=N_MAX or budget<slice_sz*0.5: break
                    buy=min(slice_sz,budget,cash)
                    if buy<1e-4: continue
                    p=price(d,t); sh[t]=sh.get(t,0)+buy/p; cash-=buy; budget-=buy; turn_tot+=buy
                # 2) crisis/bear: top up existing equally with remaining budget (accumulate)
                if state_aware and s in (1,2) and budget>1e-4 and sh:
                    per=budget/len(sh)
                    for t in list(sh):
                        p=price(d,t)
                        if pd.isna(p): continue
                        buy=min(per,cash)
                        if buy<1e-4: continue
                        sh[t]+=buy/p; cash-=buy; turn_tot+=buy
            elif eq > target_eq+1e-9:  # TRIM proportionally (raise dry powder)
                excess=eq-target_eq; frac=excess/eq
                for t in list(sh):
                    p=price(d,t)
                    if pd.isna(p): continue
                    seld=sh[t]*frac; cash+=seld*p*(1-TC); sh[t]-=seld; turn_tot+=seld*p
            eq=sum(v*price(d,t) for t,v in sh.items() if pd.notna(price(d,t)))
            nav=cash+eq; eq_sum+=eq/nav if nav>0 else 0
            hist.append({"date":d,"nav":nav,"eq_pct":eq/nav if nav>0 else 0,"n":len(sh),"state":s})
        h=pd.DataFrame(hist).set_index("date")
        return h, turn_tot/(len(rebal)), eq_sum/len(rebal)

    h_state,turn_s,eqavg_s=run(True)
    h_full,turn_f,eqavg_f=run(False)
    vni=bq_query("SELECT t.time,t.Close FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' AND t.time>='2014-01-01' AND t.Close>100 ORDER BY t.time")
    vni["time"]=pd.to_datetime(vni["time"]); vni_s=vni.set_index("time")["Close"].reindex(didx).ffill()
    vni_m=vni_s.reindex(rebal).ffill(); vni_m=vni_m/vni_m.iloc[0]

    def met(nav):
        s=nav.dropna(); rets=s.pct_change().dropna(); yrs=(s.index[-1]-s.index[0]).days/365.25
        cagr=(s.iloc[-1]/s.iloc[0])**(1/yrs)-1
        dd=((s-s.cummax())/s.cummax()).min()
        return cagr*100, dd*100, s.iloc[-1]/s.iloc[0]

    P("# QT v4.x — realistic long-horizon QUALITY sleeve")
    P("")
    P(f"N_MAX={N_MAX} | TC={TC:.2%} | hold-long (sell only tier→E) | state-aware target equity {TEQ}")
    P(f"{rebal[0].date()}→{rebal[-1].date()} monthly")
    P("")
    P(f"{'variant':<14}{'CAGR':>8}{'MaxDD':>9}{'Wealth':>9}{'avg eq%':>9}{'mo turn':>9}")
    P("-"*58)
    for nm,h,ta,ea in [("SLEEVE_STATE",h_state,turn_s,eqavg_s),("SLEEVE_FULL",h_full,turn_f,eqavg_f)]:
        c,dd,w=met(h["nav"]); P(f"{nm:<14}{c:>+7.2f}%{dd:>+8.2f}%{w:>+9.2f}{ea*100:>8.0f}%{ta*100:>8.1f}%")
    c,dd,w=met(vni_m); P(f"{'VNINDEX':<14}{c:>+7.2f}%{dd:>+8.2f}%{w:>+9.2f}")
    P("")
    P(f"holdings over time (STATE): start {h_state['n'].iloc[0]}, median {int(h_state['n'].median())}, max {h_state['n'].max()}")
    P(f"equity% by state (STATE): "+", ".join(f"{ {1:'CRI',2:'BEA',3:'NEU',4:'BUL',5:'EXB'}[s] }={h_state[h_state['state']==s]['eq_pct'].mean()*100:.0f}%" for s in [1,2,3,4,5] if (h_state['state']==s).any()))
    P("")
    # period breakdown
    P("## Sub-periods (wealth growth)")
    for lo,hi,lab in [("2014-06-01","2020-04-30","2014-COVID"),("2020-04-30","2022-12-31","2020-22 bull+bear"),
                      ("2022-12-31","2026-05-15","2023-26 OOS")]:
        row=f"  {lab:<18}"
        for nm,h in [("STATE",h_state),("FULL",h_full),("VNI",vni_m.to_frame("nav"))]:
            s=h["nav"] if "nav" in h else h
            seg=s[(s.index>=lo)&(s.index<=hi)]
            if len(seg)>2: row+=f"{nm} {(seg.iloc[-1]/seg.iloc[0]-1)*100:+6.0f}%  "
        P(row)
    P("")
    pd.DataFrame({"STATE":h_state["nav"],"FULL":h_full["nav"],"VNI":vni_m,
                  "eq_pct":h_state["eq_pct"],"n":h_state["n"],"state":h_state["state"]}).to_csv(
                  os.path.join(WORKDIR,"data","qt_v4x_sleeve_nav.csv"))
    with open(os.path.join(WORKDIR,"data","qt_v4x_sleeve.md"),"w",encoding="utf-8") as f:
        f.write("\n".join(lines))
    P("Saved data/qt_v4x_sleeve.md + data/qt_v4x_sleeve_nav.csv")

if __name__=="__main__":
    main()
