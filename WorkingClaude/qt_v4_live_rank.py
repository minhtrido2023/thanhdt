#!/usr/bin/env python3
"""qt_v4_live_rank.py — current QT v4.x ranking (latest data snapshot)."""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import os, subprocess, tempfile, pickle
from io import StringIO
import numpy as np, pandas as pd
WORKDIR=r"/home/trido/thanhdt/WorkingClaude"
PROJECT="lithe-record-440915-m9"; BQ_BIN=r"bq"
STATE={1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}; PRI={"BOTH":3,"VALUE_FEAR":2,"GROWTH":1}
def bq(sql):
    with tempfile.NamedTemporaryFile(mode="w",suffix=".sql",delete=False,encoding="utf-8") as f: f.write(sql); tmp=f.name
    try:
        r=subprocess.run(f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=100000',capture_output=True,text=True,timeout=300,shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    return pd.read_csv(StringIO(r.stdout.strip()))

fa=pd.read_csv(os.path.join(WORKDIR,"fa_ratings_lh.csv"),parse_dates=["time","Release_Date"])
fa=fa.sort_values(["ticker","quarter"]).reset_index(drop=True)
fa["eff_release"]=fa["Release_Date"].fillna(fa["time"]+pd.Timedelta(days=60))
fa["is_ab"]=fa["tier"].isin(["A","B"]).astype(int); fa["qnum"]=fa.groupby("ticker").cumcount()+1
fa["pct_AB"]=fa.groupby("ticker")["is_ab"].cumsum()/fa["qnum"]*100; fa["valid_hist"]=fa["qnum"]>=12

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
panel=pd.merge_asof(panel,fa.sort_values("eff_release")[["ticker","eff_release","tier","pct_AB","valid_hist","MktCap"]].rename(columns={"eff_release":"time"}),on="time",by="ticker",direction="backward")
panel=pd.merge_asof(panel,fin.sort_values("eff_release")[["ticker","eff_release","NP_R","Revenue_YoY_P0","PEG"]].rename(columns={"eff_release":"time"}),on="time",by="ticker",direction="backward")
panel=panel.sort_values(["ticker","time"]).reset_index(drop=True)

snap_date=panel["time"].max()
st=bq("SELECT s.time,s.state FROM tav2_bq.vnindex_5state_dt5g_live AS s ORDER BY s.time DESC LIMIT 1")
cur_state=int(st["state"].iloc[0]); st_date=st["time"].iloc[0]

g=panel[panel["time"]==snap_date].copy()
qok=(g["pct_AB"]>=70)&(g["valid_hist"])&(g["tier"].isin(["A","B"]))&(g["liqv"]>=5e9)
g=g[qok].copy()
g["mc_pct"]=g["MktCap"].rank(pct=True); g["size"]=np.where(g["mc_pct"]>=0.667,"BLUECHIP","SMALL/MID")
g["sg"]=(g["NP_R"]>=0.20)&(g["Revenue_YoY_P0"]>=0.20)
g["sv"]=(g["pe_z"]<-1)|(g["pb_z"]<-1)|(g["dd52"]<-30)
# growth counts only for bluechip
g.loc[(~g["sv"])&(g["sg"])&(g["mc_pct"]<0.667),"sg"]=False
g["etype"]=np.where(g["sg"]&g["sv"],"BOTH",np.where(g["sg"],"GROWTH",np.where(g["sv"],"VALUE_FEAR","WATCH")))
sb=3 if cur_state in (1,2) else 0
g["score"]=g["etype"].map(PRI).fillna(0)*10+sb+(-g["pe_z"]).fillna(0)
g=g.sort_values(["score"],ascending=False)
fires=g[g["etype"]!="WATCH"]

print(f"QT v4.x ranking — snapshot {snap_date.date()} | DT5G state today = {STATE[cur_state]} ({cur_state}) @ {pd.Timestamp(st_date).date()}")
print(f"Quality universe (≥70% A/B, ≥12Q, A/B now, liq≥5B): {len(g)} | firing entry: {len(fires)}")
print(f"\n{'#':>2} {'tkr':<6}{'signal':<11}{'size':<10}{'tier':<5}{'MktCap_B':>9}{'pe_z':>6}{'dd52%':>7}{'NP_YoY':>8}{'Rev_YoY':>8}")
print("-"*82)
for i,(_,r) in enumerate(g.head(20).iterrows(),1):
    npr=r["NP_R"]*100 if pd.notna(r["NP_R"]) else np.nan; rev=r["Revenue_YoY_P0"]*100 if pd.notna(r["Revenue_YoY_P0"]) else np.nan
    print(f"{i:>2} {r['ticker']:<6}{r['etype']:<11}{r['size']:<10}{r['tier']:<5}{r['MktCap']/1e9:>9.0f}{r['pe_z']:>+6.1f}{r['dd52']:>+7.0f}"
          f"{npr:>+7.0f}%{rev:>+7.0f}%")
g.head(30).to_csv(os.path.join(WORKDIR,"data","qt_v4_live_rank.csv"),index=False)
print("\nSaved data/qt_v4_live_rank.csv")
