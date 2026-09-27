"""Danh sach ma VAO/RA '8L top-25' sau khi sua chieu sort (ec9750f2).
Tai dung DUNG bieu thuc cua screen (aviation_screen.py:237 mau chuan), chi doi chieu sort.
"""
import duckdb, pandas as pd, numpy as np, json, collections
PRUNE="data/bq_cache/ticker_prune/*.parquet"; R8L="data/bq_cache/fa_ratings_8l.parquet"
START="2014-01-01"
con=duckdb.connect()
days=con.execute(f"SELECT DISTINCT time FROM read_parquet('{PRUNE}') WHERE time>=DATE '{START}'").df()
days["time"]=pd.to_datetime(days.time); days=days.sort_values("time"); days["ym"]=days.time.dt.to_period("M")
rebal=sorted(days.groupby("ym")["time"].max().tolist())
rs=[d.strftime("%Y-%m-%d") for d in rebal]
r8=con.execute(f"SELECT ticker,time,rating FROM read_parquet('{R8L}')").df(); r8["time"]=pd.to_datetime(r8.time)
liq=con.execute(f"""SELECT p.time d,p.ticker,p.Trading_Value_1M_P50 tv FROM read_parquet('{PRUNE}') p
  WHERE p.time IN ({",".join(f"DATE '{d}'" for d in rs)}) AND p.Trading_Value_1M_P50>=1e9""").df()
liq["d"]=pd.to_datetime(liq.d)
cin=collections.Counter(); cout=collections.Counter(); ov=[]; nper=0
rat_old=[]; rat_new=[]; last=None
for d in rebal:
    asof=r8[r8.time<=d].sort_values("time").groupby("ticker").tail(1)
    m=asof.merge(liq[liq.d==d][["ticker","tv"]],on="ticker",how="inner")
    if len(m)<25: continue
    nper+=1
    old=m.sort_values(["rating","tv"],ascending=False).head(25)
    new=m.sort_values(["rating","tv"],ascending=[True,False]).head(25)
    so,sn=set(old.ticker),set(new.ticker)
    for t in sn-so: cin[t]+=1
    for t in so-sn: cout[t]+=1
    ov.append(len(so&sn)); rat_old.append(old.rating.mean()); rat_new.append(new.rating.mean())
    last=(d,sorted(so),sorted(sn),len(m))
print(f"KY REBAL: {nper} ({rebal[0].date()} -> {rebal[-1].date()})")
print(f"rating TB ro CU(bug) {np.mean(rat_old):.3f} | ro MOI {np.mean(rat_new):.3f}")
print(f"overlap TB {np.mean(ov):.2f}/25 | so ky roi nhau HOAN TOAN: {sum(1 for x in ov if x==0)}/{nper}")
print(f"\nMA VAO (top 30 theo so ky, tong {len(cin)} ma khac nhau):")
for t,c in cin.most_common(30): print(f"  {t} {c}")
print(f"\nMA RA  (top 30 theo so ky, tong {len(cout)} ma khac nhau):")
for t,c in cout.most_common(30): print(f"  {t} {c}")
BANNED={"PC1","VVS","KSF","NKG","HSG","HVN","VJC","NVL","GEG","SBA","DMC","IMP","TRA","TOS","VTP","BAF"}
print(f"\nMa BANNED nam trong ro CU: {sorted(set(cout)&BANNED)}")
print(f"Ma BANNED nam trong ro MOI: {sorted(set(cin)&BANNED)}")
d,so,sn,n=last
print(f"\nKY CUOI {d.date()} (n={n} ma du thanh khoan):")
print(f"  CU (bug): {' '.join(so)}")
print(f"  MOI     : {' '.join(sn)}")
json.dump({"n_periods":nper,"rating_mean_old":float(np.mean(rat_old)),"rating_mean_new":float(np.mean(rat_new)),
           "overlap_mean":float(np.mean(ov)),"in":dict(cin),"out":dict(cout),
           "last_date":str(d.date()),"last_old":so,"last_new":sn},
          open("mike/agents/Taylor/research/screen_regen_20260927/top25_inout.json","w"),indent=1)
