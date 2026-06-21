#!/usr/bin/env python3
"""
qt_v4x_trailing.py — trailing-stop-from-peak exit vs HOLD (per-position, 5Y)
============================================================================
Prior test: all FUNDAMENTAL-trigger exits (OVERVALUED/DECEL/FA) lose to HOLD
because they cut compounders early. Trailing-stop is the remaining candidate:
it does NOT cut early — only locks a run AFTER a drawdown from the running peak,
so it preserves multibaggers (VTP/MWG) while avoiding round-trips (VNM/DGC-2022).

Per event: walk daily from entry; running_peak = cummax(Close); exit when
Close ≤ running_peak·(1−stop). Variants:
  HOLD_5Y          : hold to 5Y/data-end
  TS25/TS35/TS50   : trailing stop 25/35/50% from peak (Close-based)
  TS35_act20       : 35% trail, but only ACTIVE after peak first exceeds +20%
Metrics: median/mean realized return, win%, capture (realized/5Y-peak, winners),
median hold. By archetype. Face validity on VTP/MWG vs VNM/DGC.
Output: data/qt_v4x_trailing.md
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import os, pickle
import numpy as np, pandas as pd

WORKDIR=r"/home/trido/thanhdt/WorkingClaude"
FWD=1260

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
    fa_a=fa.sort_values("eff_release")[["ticker","eff_release","tier","pct_AB","valid_hist"]].rename(columns={"eff_release":"time"})
    panel=pd.merge_asof(panel,fa_a,on="time",by="ticker",direction="backward")
    fin_a=fin.sort_values("eff_release")[["ticker","eff_release","NP_R","Revenue_YoY_P0"]].rename(columns={"eff_release":"time"})
    panel=pd.merge_asof(panel,fin_a,on="time",by="ticker",direction="backward")
    panel=panel.sort_values(["ticker","time"]).reset_index(drop=True)

    qok=(panel["pct_AB"]>=70)&(panel["valid_hist"])&(panel["tier"].isin(["A","B"]))&(panel["liqv"]>=5e9)
    panel["sig_g"]=qok&(panel["NP_R"]>=0.20)&(panel["Revenue_YoY_P0"]>=0.20)
    panel["sig_v"]=qok&((panel["pe_z"]<-1)|(panel["pb_z"]<-1)|(panel["dd52"]<-30))

    def ts_exit(seg, stop, act=0.0):
        """seg = Close[entry..end]; return realized return %. act=activate trail after +act peak."""
        ep=seg[0]; runmax=np.maximum.accumulate(seg)
        thresh=runmax*(1-stop)
        active=(runmax>=ep*(1+act))
        trig=(seg<=thresh)&active; trig[0]=False
        idx=np.argmax(trig) if trig.any() else None
        px=seg[idx] if idx is not None else seg[-1]
        return (px/ep-1)*100, (idx if idx is not None else len(seg)-1)

    rows=[]
    for tk,g in panel.groupby("ticker"):
        g=g.reset_index(drop=True)
        sg=g["sig_g"].values; sv=g["sig_v"].values; anys=sg|sv; cl=g["Close"].values; n=len(g)
        for i in range(n):
            if not (anys[i] and (i==0 or not anys[i-1])): continue
            ep=cl[i]
            if not np.isfinite(ep) or ep<=0: continue
            et="BOTH" if (sg[i] and sv[i]) else ("GROWTH" if sg[i] else "VALUE_FEAR")
            end=min(i+FWD,n-1); seg=cl[i:end+1]
            seg=np.where(np.isfinite(seg),seg,np.nan)
            if np.isnan(seg).any():  # ffill within segment
                seg=pd.Series(seg).ffill().values
            peak=(np.max(seg[1:])/ep-1)*100 if len(seg)>1 else 0.0
            r={"ticker":tk,"date":g["time"].values[i],"etype":et,"peak":peak,
               "HOLD_5Y":(seg[-1]/ep-1)*100}
            for nm,st,ac in [("TS25",0.25,0),("TS35",0.35,0),("TS50",0.50,0),("TS35_act20",0.35,0.20)]:
                rr,hd=ts_exit(seg,st,ac); r[nm]=rr;
                if nm=="TS35": r["hold_ts35_d"]=hd
            rows.append(r)
    ev=pd.DataFrame(rows)
    STR=["HOLD_5Y","TS25","TS35","TS50","TS35_act20"]

    P("# QT v4.x — trailing-stop-from-peak vs HOLD (per-position, 5Y window)")
    P("")
    P(f"events {len(ev):,} | GROWTH+BOTH={int(ev['etype'].isin(['GROWTH','BOTH']).sum())} VALUE_FEAR={int((ev['etype']=='VALUE_FEAR').sum())}")
    P("Capture = realized / 5Y-peak (winners, peak>20%). Higher = harvests more of the run.")
    P("")
    def block(sub,label):
        P(f"## {label} (N={len(sub)})")
        P(f"{'strategy':<13}{'med ret':>9}{'mean':>9}{'win%':>7}{'capture':>9}")
        P("-"*47)
        win=sub[sub["peak"]>20]
        for s in STR:
            r=sub[s].dropna(); cap=(win[s]/win["peak"]).replace([np.inf,-np.inf],np.nan).dropna()
            P(f"{s:<13}{r.median():>+8.1f}%{r.mean():>+8.1f}%{(r>0).mean()*100:>6.0f}%{cap.median()*100:>8.0f}%")
        P("")
    block(ev,"ALL entries")
    block(ev[ev["etype"]=="VALUE_FEAR"],"VALUE_FEAR")
    block(ev[ev["etype"].isin(["GROWTH","BOTH"])],"GROWTH+BOTH")

    P("## Face validity — TS35 vs HOLD on key names (best entry per name)")
    P(f"{'ticker':<7}{'etype':<11}{'peak':>8}{'HOLD':>9}{'TS35':>9}{'TS25':>9}")
    for tk in ["VTP","MWG","VCS","DGC","VNM"]:
        g=ev[ev["ticker"]==tk]
        if len(g)==0: P(f"  {tk}: none"); continue
        r=g.loc[g["peak"].idxmax()]
        P(f"{tk:<7}{r['etype']:<11}{r['peak']:>+7.0f}%{r['HOLD_5Y']:>+8.0f}%{r['TS35']:>+8.0f}%{r['TS25']:>+8.0f}%")
    P("")
    P("Read: trailing-stop WINS if it keeps multibaggers (VTP/MWG TS≈peak) while")
    P("cutting round-trips (VNM/DGC TS>HOLD). Best stop = highest mean+capture vs HOLD.")
    P("")
    ev.to_csv(os.path.join(WORKDIR,"data","qt_v4x_trailing.csv"),index=False)
    with open(os.path.join(WORKDIR,"data","qt_v4x_trailing.md"),"w",encoding="utf-8") as f:
        f.write("\n".join(lines))
    P("Saved data/qt_v4x_trailing.md")

if __name__=="__main__":
    main()
