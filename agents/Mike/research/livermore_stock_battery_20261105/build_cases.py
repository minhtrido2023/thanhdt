import subprocess, json, io, random, sys
import pandas as pd
SEED=20261105
sql=f"""
WITH u AS (
  SELECT ticker, time FROM `lithe-record-440915-m9.tav2_mike.universe_pit`
  WHERE in_universe AND time BETWEEN '2012-01-03' AND '2025-09-30'
),
s AS (SELECT ticker, time, ROW_NUMBER() OVER (ORDER BY FARM_FINGERPRINT(CONCAT(ticker, CAST(time AS STRING), '{SEED}'))) rn FROM u),
pick AS (SELECT ticker, time FROM s WHERE rn<=1500)
SELECT p.ticker pk, p.time asof, t.time, t.Open, t.High, t.Low, t.Close, t.Volume
FROM pick p JOIN `lithe-record-440915-m9.tav2_bq.ticker` t
 ON t.ticker=p.ticker AND t.time BETWEEN DATE_SUB(p.time, INTERVAL 520 DAY) AND DATE_ADD(p.time, INTERVAL 60 DAY)
ORDER BY pk, asof, t.time
"""
out=subprocess.run(["bq","query","--use_legacy_sql=false","--format=csv","--max_rows=2000000","--project_id=lithe-record-440915-m9",sql],capture_output=True,text=True)
if out.returncode: print(out.stderr); sys.exit(1)
df=pd.read_csv(io.StringIO(out.stdout),parse_dates=["asof","time"])
df.to_pickle("raw.pkl")
rng=random.Random(SEED)
groups=[(k,g.reset_index(drop=True)) for k,g in df.groupby(["pk","asof"])]
rng.shuffle(groups)
chosen=[];cnt={};last={}
truth=[]
for (tk,asof),g in groups:
    if len(truth)==100: break
    if cnt.get(tk,0)>=2: continue
    if any(abs((asof-a).days)<60 for a in last.get(tk,[])): continue
    i=g.index[g.time==asof]
    if len(i)!=1: continue
    i=int(i[0])
    if i<249 or i+20>=len(g): continue
    w=g.iloc[i-249:i+1]
    if (w.Volume==0).mean()>0.2: continue          # chuỗi thủng thanh khoản
    n=len(truth)+1; lab=f"S{n:03d}"
    base=w.Close.iloc[0]; vm=w.Volume.median()
    pd.DataFrame({"session":range(250),"open":(w.Open.values/base*100).round(2),"high":(w.High.values/base*100).round(2),
      "low":(w.Low.values/base*100).round(2),"close":(w.Close.values/base*100).round(2),
      "vol_rel":(w.Volume.values/vm).round(2)}).to_csv(f"cases/{lab}.csv",index=False)
    c0=g.Close[i]; fwd=g.Close[i+20]/c0-1
    truth.append(dict(label=lab,ticker=tk,asof=str(asof.date()),fwd20=float(fwd),up=int(fwd>0),
      mom20=int(c0/g.Close[i-20]>1),mom60=int(c0/g.Close[i-60]>1)))
    cnt[tk]=cnt.get(tk,0)+1; last.setdefault(tk,[]).append(asof)
json.dump(truth,open("SEALED_truth.json","w"),indent=1)
print(len(truth),"cases; base rate up=",sum(t['up'] for t in truth)/len(truth))
