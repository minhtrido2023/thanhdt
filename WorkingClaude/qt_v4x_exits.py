#!/usr/bin/env python3
"""
qt_v4x_exits.py — archetype-conditional EXIT test (user insight 2026-05-29)
===========================================================================
Per-position event study (no portfolio). For each QT v4.x entry, find when each
exit rule fires and measure realized return + hold + CAPTURE RATIO (realized /
5Y-peak) — how much of the available run the exit harvests.

User insight: growth runners trade expensive while growing (OVERVALUED would cut
them early); they should exit on DECELERATION (multiple de-rates after). Value
names mean-revert and should exit on OVERVALUED. So exit must be archetype-conditional.

Exit rules (point-in-time, as-of fundamentals):
  OVERVALUED  : pe_z>2.5 AND pb_z>1.5
  DECEL       : NP_R<10% AND Rev_YoY<10% (growth fell below threshold — pre -15% decline)
  FA_DEGRADE  : tier → C/D/E
  GROWTH_BROKEN: NP_R<-15% AND Rev_YoY<-15% (original QT v4)

Strategies:
  HOLD_5Y      : hold to 5Y/data-end (ceiling reference)
  OVERVALUED   : exit on OVERVALUED|FA (else hold)
  DECEL        : exit on DECEL|FA (growth/both entries) (else hold)
  QTV4_ANY     : exit on OVERVALUED|FA|GROWTH_BROKEN (original)
  ARCHETYPE    : VALUE→OVERVALUED|FA ; GROWTH/BOTH→DECEL|FA
Output: data/qt_v4x_exits.md
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
FWD=1260

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
    fin=fin.sort_values(["ticker","eff_release"])

    panel=panel.sort_values("time")
    fa_a=fa.sort_values("eff_release")[["ticker","eff_release","tier","pct_AB","valid_hist","MktCap"]].rename(columns={"eff_release":"time"})
    panel=pd.merge_asof(panel,fa_a,on="time",by="ticker",direction="backward")
    fin_a=fin.sort_values("eff_release")[["ticker","eff_release","PEG","NP_R","Revenue_YoY_P0"]].rename(columns={"eff_release":"time"})
    panel=pd.merge_asof(panel,fin_a,on="time",by="ticker",direction="backward")
    panel=panel.sort_values(["ticker","time"]).reset_index(drop=True)

    # entry signals
    qok=(panel["pct_AB"]>=70)&(panel["valid_hist"])&(panel["tier"].isin(["A","B"]))&(panel["liqv"]>=5e9)
    panel["sig_g"]=qok&(panel["NP_R"]>=0.20)&(panel["Revenue_YoY_P0"]>=0.20)
    panel["sig_v"]=qok&((panel["pe_z"]<-1)|(panel["pb_z"]<-1)|(panel["dd52"]<-30))
    # exit flags
    panel["x_ovr"]=(panel["pe_z"]>2.5)&(panel["pb_z"]>1.5)
    panel["x_decel"]=(panel["NP_R"]<0.10)&(panel["Revenue_YoY_P0"]<0.10)
    panel["x_fa"]=panel["tier"].isin(["C","D","E"])
    panel["x_gb"]=(panel["NP_R"]<-0.15)&(panel["Revenue_YoY_P0"]<-0.15)

    # events + per-strategy exits
    rows=[]
    for tk,g in panel.groupby("ticker"):
        g=g.reset_index(drop=True)
        sg=g["sig_g"].values; sv=g["sig_v"].values; anys=sg|sv
        cl=g["Close"].values
        xovr=g["x_ovr"].values; xdec=g["x_decel"].values; xfa=g["x_fa"].values; xgb=g["x_gb"].values
        n=len(g)
        for i in range(n):
            if not (anys[i] and (i==0 or not anys[i-1])): continue
            ep=cl[i]
            if not np.isfinite(ep) or ep<=0: continue
            et="BOTH" if (sg[i] and sv[i]) else ("GROWTH" if sg[i] else "VALUE_FEAR")
            end=min(i+FWD,n-1)
            fwd=cl[i+1:end+1]; fwd=fwd[np.isfinite(fwd)]
            peak=(np.max(fwd)/ep-1)*100 if len(fwd) else 0.0
            def first_exit(*flagarrs):
                comb=np.zeros(end-i,dtype=bool)
                for fl in flagarrs: comb|=fl[i+1:end+1]
                idx=np.argmax(comb) if comb.any() else None
                if idx is None: return end, (cl[end]/ep-1)*100
                j=i+1+idx
                return j,(cl[j]/ep-1)*100
            # strategies
            ovr_j,ovr_r=first_exit(xovr,xfa)
            dec_j,dec_r=first_exit(xdec,xfa)
            any_j,any_r=first_exit(xovr,xfa,xgb)
            hold_r=(cl[end]/ep-1)*100
            if et=="VALUE_FEAR": arch_r=ovr_r; arch_j=ovr_j
            else: arch_r=dec_r; arch_j=dec_j
            rows.append({"ticker":tk,"etype":et,"peak":peak,
                "HOLD_5Y":hold_r,"OVERVALUED":ovr_r,"DECEL":dec_r,"QTV4_ANY":any_r,"ARCHETYPE":arch_r,
                "hold_arch_d":int((arch_j-i)),"hold_ovr_d":int(ovr_j-i),"hold_dec_d":int(dec_j-i)})
    ev=pd.DataFrame(rows)

    P("# QT v4.x — archetype-conditional EXIT test (per-position, 5Y window)")
    P("")
    P(f"events {len(ev):,} | GROWTH+BOTH={int(ev['etype'].isin(['GROWTH','BOTH']).sum())} VALUE_FEAR={int((ev['etype']=='VALUE_FEAR').sum())}")
    P("Capture = realized exit return / 5Y peak (winners only, peak>20%). Higher = harvests more of the run.")
    P("")
    STR=["HOLD_5Y","OVERVALUED","DECEL","QTV4_ANY","ARCHETYPE"]

    def block(sub,label):
        P(f"## {label}  (N={len(sub)})")
        P(f"{'strategy':<12}{'med ret':>9}{'mean':>9}{'win%':>7}{'med capture':>13}")
        P("-"*50)
        win=sub[sub["peak"]>20]
        for s in STR:
            r=sub[s].dropna()
            cap=(win[s]/win["peak"]).replace([np.inf,-np.inf],np.nan).dropna()
            P(f"{s:<12}{r.median():>+8.1f}%{r.mean():>+8.1f}%{(r>0).mean()*100:>6.0f}%{cap.median()*100:>12.0f}%")
        P("")

    block(ev,"ALL entries")
    block(ev[ev["etype"]=="VALUE_FEAR"],"VALUE_FEAR entries (expect OVERVALUED best)")
    block(ev[ev["etype"].isin(["GROWTH","BOTH"])],"GROWTH+BOTH entries (expect DECEL > OVERVALUED)")
    P("## Median hold days by exit (GROWTH+BOTH)")
    gb=ev[ev["etype"].isin(["GROWTH","BOTH"])]
    P(f"  OVERVALUED {gb['hold_ovr_d'].median():.0f}d | DECEL {gb['hold_dec_d'].median():.0f}d | ARCHETYPE {gb['hold_arch_d'].median():.0f}d")
    P("")
    P("Read: for GROWTH+BOTH, if DECEL median ret/capture > OVERVALUED, exiting on")
    P("deceleration (not on high valuation) harvests more — confirms user's thesis.")
    P("ARCHETYPE (value→OVR, growth→DECEL) vs QTV4_ANY shows if conditional beats one-size.")
    P("")
    ev.to_csv(os.path.join(WORKDIR,"data","qt_v4x_exits.csv"),index=False)
    with open(os.path.join(WORKDIR,"data","qt_v4x_exits.md"),"w",encoding="utf-8") as f:
        f.write("\n".join(lines))
    P("Saved data/qt_v4x_exits.md")

if __name__=="__main__":
    main()
