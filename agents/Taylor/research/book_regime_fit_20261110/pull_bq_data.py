"""Saved BQ pull for data/{dt5g,vnindex,xsec}.csv (originals were pulled ad hoc; this script regenerates them to data/regen_*.csv and
diffs vs the originals — see regen_check.txt for the match status; originals untouched).
 dt5g   : tav2_bq.vnindex_5state_dt5g_live (time,state,state_raw,asof_date)   [NOT the un-suffixed vnindex_5state table = v3.4b BASE]
 vnindex: tav2_bq.ticker WHERE ticker='VNINDEX' (Close, MA200, MA50) from 2006-01-01
 xsec   : tav2_mike.universe_pit (in_universe, ruleset_version=1, PIT) joined to tav2_bq.ticker (Close,MA200) from 2007-01-01:
          n_ma=#in_universe names with MA200; breadth=share Close>MA200; n_r21/disp21/iqr21 = count / std / IQR of 21-session Close returns;
          disp1 = std of 1-session return; ew_r1 = equal-weight mean 1-session return."""
import subprocess, io, pandas as pd, numpy as np
P="lithe-record-440915-m9"; R="/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/book_regime_fit_20261110/data"
def bq(sql):
    r=subprocess.run(["bq","query","--use_legacy_sql=false",f"--project_id={P}","--format=csv","--max_rows=50000000",sql],capture_output=True,text=True)
    if r.returncode: raise SystemExit(r.stderr[-800:])
    return pd.read_csv(io.StringIO(r.stdout))
bq("SELECT 1")
dt=bq("SELECT d.time,d.state,d.state_raw,d.asof_date FROM tav2_bq.vnindex_5state_dt5g_live AS d WHERE d.time>=DATE '2014-01-01' ORDER BY 1"); dt.to_csv(f"{R}/regen_dt5g.csv",index=False)
vn=bq("SELECT t.time,t.Close,t.MA200,t.MA50 FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' AND t.time>=DATE '2006-01-01' ORDER BY 1"); vn.to_csv(f"{R}/regen_vnindex.csv",index=False)
px=bq("""SELECT t.time,t.ticker,t.Close,t.MA200 FROM tav2_bq.ticker AS t JOIN tav2_mike.universe_pit AS u ON u.ticker=t.ticker AND u.time=t.time
WHERE u.in_universe AND u.ruleset_version=1 AND t.time>=DATE '2006-01-01' AND t.Close>0""")
px["time"]=pd.to_datetime(px["time"]); px=px.sort_values(["ticker","time"])
px["r1"]=px.groupby("ticker").Close.pct_change(); px["r21"]=px.groupby("ticker").Close.pct_change(21)
px=px[px.time>="2007-01-01"]; g=px.groupby("time")
xs=pd.DataFrame({"n_ma":g.MA200.count(),"breadth":g.apply(lambda d:(d.Close[d.MA200.notna()]>d.MA200[d.MA200.notna()]).mean()),"n_r21":g.r21.count(),
  "disp21":g.r21.std(),"iqr21":g.r21.quantile(.75)-g.r21.quantile(.25),"disp1":g.r1.std(),"ew_r1":g.r1.mean()}); xs.to_csv(f"{R}/regen_xsec.csv")
out=[]
for n in ["dt5g","vnindex","xsec"]:
    a=pd.read_csv(f"{R}/{n}.csv",parse_dates=["time"]).set_index("time"); b=pd.read_csv(f"{R}/regen_{n}.csv",parse_dates=["time"]).set_index("time")
    idx=a.index.intersection(b.index); cols=[c for c in a.columns if c in b.columns and c!="asof_date"]
    mx={c:float(np.nanmax(np.abs(a.loc[idx,c].astype(float)-b.loc[idx,c].astype(float)))) for c in cols}
    out.append(f"{n}: rows orig {len(a)} regen {len(b)} common {len(idx)} max|diff| {mx}")
open(f"{R}/../regen_check.txt","w").write("\n".join(out)); print("\n".join(out))
