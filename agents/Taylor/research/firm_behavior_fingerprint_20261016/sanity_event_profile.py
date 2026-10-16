"""Sanity: Release_Date có trùng ngày thông tin tới thị trường không? Profile |AR| & volume quanh t0, và phân bố thứ trong tuần."""
import glob, warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
C="/home/trido/thanhdt/WorkingClaude/data/bq_cache"
ev=pd.read_csv("events_features.csv.gz",parse_dates=["rd"]); ev=ev[ev.in_universe]
print("rd weekday dist:", ev.rd.dt.dayofweek.value_counts().sort_index().to_dict())
tf=pd.read_parquet(f"{C}/ticker_financial.parquet",columns=["ticker","time","Release_Date","ID_Release"]); tf["rd"]=pd.to_datetime(tf.Release_Date)
print("ID_Release sample:", tf.dropna(subset=["ID_Release"]).ID_Release.head(5).tolist())
px=pd.concat([pd.read_parquet(f,columns=["time","ticker","Close","Volume"]) for f in sorted(glob.glob(f"{C}/ticker/20*.parquet")) if int(f[-12:-8])>=2013])
px["time"]=pd.to_datetime(px.time); px=px.drop_duplicates(["ticker","time"])
cal=pd.DatetimeIndex(sorted(px[px.ticker=="VNINDEX"].time.unique()))
cl=px.pivot(index="time",columns="ticker",values="Close").reindex(cal); cl=cl.where(cl>0)
vo=px.pivot(index="time",columns="ticker",values="Volume").reindex(cal)
r=cl.pct_change(fill_method=None); ar=r.sub(r["VNINDEX"],axis=0).abs().values; V=vo.values
ti={t:i for i,t in enumerate(cl.columns)}
t0=np.searchsorted(cal.values,ev.rd.values); J=ev.ticker.map(ti).values
out=[]
for k in range(-10,11):
    a=[];v=[]
    for t,j in zip(t0,J):
        if 30<=t+k<len(cal) and t+k>=0:
            a.append(ar[t+k,j]); base=np.nanmean(V[t-30:t-10,j]); v.append(V[t+k,j]/base if base>0 else np.nan)
    out.append((k,np.nanmean(a),np.nanmedian(v),np.nanmean(np.clip(v,0,10))))
print(pd.DataFrame(out,columns=["k","mean_absAR","med_volratio","mean_volratio_clip10"]).round(4).to_string(index=False))
