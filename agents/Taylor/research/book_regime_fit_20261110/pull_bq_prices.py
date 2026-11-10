"""Pull full-session price table (Close adj, Price raw, Open, Volume_3M_P50) from live BQ for the LAG universe,
window 2026-06-01 -> latest. Output: data/lag_px_bq_fixed_2026H2.csv (non-canonical name; coding_guidelines §8)."""
import subprocess, io, pickle, pandas as pd
WC="/home/trido/thanhdt/WorkingClaude"; OUT=f"{WC}/mike/agents/Taylor/research/book_regime_fit_20261110/data"
PROJ="lithe-record-440915-m9"
def bq(sql):
    r=subprocess.run(["bq","query","--use_legacy_sql=false",f"--project_id={PROJ}","--format=csv","--max_rows=20000000",sql],capture_output=True,text=True)
    if r.returncode: raise RuntimeError(r.stderr[-1000:])
    return pd.read_csv(io.StringIO(r.stdout))
fin=pickle.load(open(f"{WC}/data/earnings_surprise_data.pkl","rb"))
uni=sorted(fin["ticker"].dropna().unique())
inl=",".join(f"'{t}'" for t in uni)
df=bq(f"""SELECT t.ticker,t.time,t.Close,t.Price,t.Open,t.Volume_3M_P50 FROM tav2_bq.ticker AS t
WHERE t.ticker IN ({inl}) AND t.time>=DATE '2026-06-01' AND t.Close>0""")
df["time"]=pd.to_datetime(df["time"]); df=df.drop_duplicates(["ticker","time"]).sort_values(["ticker","time"])
df.to_csv(f"{OUT}/lag_px_bq_fixed_2026H2.csv",index=False)
c=df.groupby("time").ticker.nunique(); print(len(df),df.time.min(),df.time.max()); print(c.to_string())
