#!/usr/bin/env python3
"""
qt_v4x_archetypes.py — two multibagger archetypes (user insight 2026-05-29)
===========================================================================
User: entry condition must differ by company type.
  A) VALUE_FEAR  — quality intact but priced cheap/beaten/ignored (crisis, sector
     misunderstood, one-off incident scare). Pattern: VCS 2014, DGC 2015/2019.
     → needs CHEAP + fear (esp. CRISIS/BEAR state).
  B) GROWTH_BLUECHIP — established blue-chip STILL in strong-growth phase. Pattern:
     VNM 2005-2017 (~dozens×). → does NOT need cheap, just strong growth; exit when
     growth matures.

Tests, per (entry_type × size-class), at the STOCK level (event study, no portfolio):
  - 3Y point return + PEAK return within 3Y (captures "ăn bằng lần")
  - multibagger rates: peak ≥ +100% / +200% / +400% within 3Y
  - beat-VNINDEX
Hypothesis: GROWTH works for BLUECHIP (not cheap needed); VALUE_FEAR works for
SMALL/MID (cheap needed); GROWTH alone weak for small/mid.

Data: qt_panel_2014_2026.pkl + fa_ratings_lh.csv (tier, MktCap) + qt_v4_fin.pkl + DT5G.
Caveat: panel prices start 2014 (VCS 2015-11, DGC 2018-12) → cannot capture the
original VCS-2014 / DGC-2015 entries; tests the archetype across 2016-2026.
Output: data/qt_v4x_archetypes.md
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
STATE={1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}
FWD=1260  # 5Y window for peak/multibagger (captures the real VCS/DGC/MWG runs)

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
    fin=fin.sort_values(["ticker","eff_release"])

    panel=panel.sort_values("time")
    fa_a=fa.sort_values("eff_release")[["ticker","eff_release","tier","pct_AB","valid_hist","MktCap"]].rename(columns={"eff_release":"time"})
    panel=pd.merge_asof(panel,fa_a,on="time",by="ticker",direction="backward")
    fin_a=fin.sort_values("eff_release")[["ticker","eff_release","PEG","NP_R","Revenue_YoY_P0"]].rename(columns={"eff_release":"time"})
    panel=pd.merge_asof(panel,fin_a,on="time",by="ticker",direction="backward")

    # DT5G state
    st=bq_query("SELECT s.time,s.state FROM tav2_bq.vnindex_5state_dt5g_live AS s ORDER BY s.time")
    st["time"]=pd.to_datetime(st["time"])
    panel=pd.merge_asof(panel.sort_values("time"),st.sort_values("time"),on="time",direction="backward")
    panel=panel.sort_values(["ticker","time"]).reset_index(drop=True)

    # quality gate + size class (cross-sectional MktCap tercile among quality names per day)
    panel["qok"]=(panel["pct_AB"]>=70)&(panel["valid_hist"])&(panel["tier"].isin(["A","B"]))&(panel["liqv"]>=5e9)
    panel["mc_pct"]=panel[panel["qok"]].groupby("time")["MktCap"].rank(pct=True)
    panel["mc_pct"]=panel["mc_pct"]  # NaN for non-qok rows
    panel["size_class"]=np.where(panel["mc_pct"]>=0.667,"BLUECHIP",
                          np.where(panel["mc_pct"].notna(),"SMALLMID",None))

    # two entry signals (quality gated)
    panel["sig_growth"]=panel["qok"]&(panel["NP_R"]>=0.20)&(panel["Revenue_YoY_P0"]>=0.20)
    panel["sig_value"]=panel["qok"]&((panel["pe_z"]<-1)|(panel["pb_z"]<-1)|(panel["dd52"]<-30))

    vni=bq_query("SELECT t.time,t.Close FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' AND t.time>='2014-01-01' AND t.Close>100 ORDER BY t.time")
    vni["time"]=pd.to_datetime(vni["time"]); vni_s=vni.set_index("time")["Close"]
    def vni_fwd(d,H):
        i=vni_s.index.searchsorted(d); j=i+H
        return (vni_s.iloc[j]/vni_s.iloc[i]-1)*100 if i<len(vni_s) and j<len(vni_s) else np.nan

    # build events: fresh trigger of (growth OR value)
    events=[]
    for tk,g in panel.groupby("ticker"):
        g=g.reset_index(drop=True)
        sg=g["sig_growth"].values; sv=g["sig_value"].values; any_s=sg|sv
        cl=g["Close"].values; tm=g["time"].values
        for i in range(len(g)):
            if any_s[i] and (i==0 or not any_s[i-1]):
                ep=cl[i]
                if not np.isfinite(ep) or ep<=0: continue
                etype="BOTH" if (sg[i] and sv[i]) else ("GROWTH" if sg[i] else "VALUE_FEAR")
                end=min(i+FWD,len(g)-1)
                fwd=cl[i+1:end+1]; fwd=fwd[np.isfinite(fwd)]
                peak=(np.max(fwd)/ep-1)*100 if len(fwd) else np.nan
                r3y=(cl[end]/ep-1)*100 if np.isfinite(cl[end]) else np.nan
                events.append({"ticker":tk,"date":pd.Timestamp(tm[i]),"etype":etype,
                    "size":g["size_class"].values[i],"state":g["state"].values[i],
                    "pe_z_entry":g["pe_z"].values[i],
                    "MktCap_B":g["MktCap"].values[i]/1e9,"peak_pk":peak,"r_hold":r3y,
                    "fwd_days":(pd.Timestamp(tm[end])-pd.Timestamp(tm[i])).days,
                    "vni_h":vni_fwd(pd.Timestamp(tm[i]),min(FWD,end-i))})
    ev=pd.DataFrame(events)
    ev["exc"]=ev["r_hold"]-ev["vni_h"]

    P("# QT v4.x — two multibagger archetypes (VALUE_FEAR vs GROWTH_BLUECHIP)")
    P("")
    P(f"events {len(ev):,} | tickers {ev['ticker'].nunique()} | {ev['date'].min().date()}→{ev['date'].max().date()}")
    P(f"(peak_pk = max drawup within 5Y = the 'ăn bằng lần' opportunity; r_hold = disciplined 5Y hold)")
    P("")

    def cell(g):
        n=len(g)
        return (f"{n:>5}{g['peak_pk'].median():>+9.0f}%{g['r_hold'].median():>+9.0f}%"
                f"{100*(g['peak_pk']>=100).mean():>7.0f}%{100*(g['peak_pk']>=200).mean():>7.0f}%"
                f"{100*(g['peak_pk']>=400).mean():>7.0f}%{100*(g['peak_pk']>=900).mean():>7.0f}%{100*(g['exc']>0).mean():>8.0f}%")

    P("## Entry archetype × size class (5Y peak/hold)")
    P(f"{'cell':<26}{'N':>5}{'peakMed':>9}{'5YMed':>9}{'≥2x%':>7}{'≥3x%':>7}{'≥5x%':>7}{'≥10x%':>7}{'beatVNI':>8}")
    P("-"*86)
    for et in ["GROWTH","VALUE_FEAR","BOTH"]:
        for sz in ["BLUECHIP","SMALLMID"]:
            g=ev[(ev["etype"]==et)&(ev["size"]==sz)]
            if len(g)<8: continue
            P(f"{et+' × '+sz:<26}"+cell(g))
    P("")
    P("## By size class only (all entries)")
    for sz in ["BLUECHIP","SMALLMID"]:
        g=ev[ev["size"]==sz]
        if len(g)>=8: P(f"{sz:<26}"+cell(g))
    P("")
    P("## VALUE_FEAR by entry STATE (does crisis/bear boost it?)")
    P(f"{'state':<26}{'N':>5}{'peakMed':>9}{'5YMed':>9}{'≥2x%':>7}{'≥3x%':>7}{'≥5x%':>7}{'≥10x%':>7}{'beatVNI':>8}")
    vf=ev[ev["etype"].isin(["VALUE_FEAR","BOTH"])]
    for s in [1,2,3,4,5]:
        g=vf[vf["state"]==s]
        if len(g)>=8: P(f"{STATE[s]:<26}"+cell(g))
    P("")

    # valuation at entry by archetype (user point: growth = expensive but OK)
    P("## Valuation at entry (pe_z) by archetype — growth names ARE expensive")
    for et in ["GROWTH","VALUE_FEAR","BOTH"]:
        g=ev[ev["etype"]==et]["pe_z_entry"].dropna()
        if len(g): P(f"  {et:<12} median pe_z at entry = {g.median():+.2f}  (>0 = above own 5Y mean = expensive)")
    P("")

    # face validity — incl MWG/DGW/FRT/VTP growth compounders
    P("## Face validity — entries caught by the filter (5Y peak / 5Y hold)")
    for tk in ["VCS","DGC","MWG","DGW","FRT","VTP","VNM"]:
        g=ev[ev["ticker"]==tk].sort_values("date")
        if len(g)==0: P(f"  {tk}: no events (price-history / quality-gate limits)"); continue
        bestpeak=g["peak_pk"].max()
        P(f"  {tk} ({len(g)} events, best 5Y peak {bestpeak:+.0f}%):")
        for _,r in g.head(4).iterrows():
            P(f"    {r['date'].date()} {r['etype']:<10} {str(r['size']) or '?':<8} "
              f"MC={r['MktCap_B']:.0f}B pe_z={r['pe_z_entry']:+.1f}  peak5Y={r['peak_pk']:+.0f}%  hold5Y={r['r_hold']:+.0f}%")
    P("")
    ev.to_csv(os.path.join(WORKDIR,"data","qt_v4x_events.csv"),index=False)
    with open(os.path.join(WORKDIR,"data","qt_v4x_archetypes.md"),"w",encoding="utf-8") as f:
        f.write("\n".join(lines))
    P("Saved data/qt_v4x_archetypes.md + data/qt_v4x_events.csv")

if __name__=="__main__":
    main()
