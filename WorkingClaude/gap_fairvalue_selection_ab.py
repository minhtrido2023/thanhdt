"""Selection-level A/B: does adding ROIC/PB to the rating_8l VALUE composite improve actual PICKS OOS?
Monthly rebalance, quality-gated liquid universe. Each month pick top-25 by:
  A = z(ey) + z(cfy)                 [current value axis proxy; ey=1/PE, cfy=1/PCF. PS absent in cache.]
  B = z(ey) + z(cfy) + z(ROIC/PB)    [+ quality-adjusted book yield, equal weight = unbiased, no tuning]
Measure equal-weight forward return (profit_1M ~ T+20 ~ monthly) of each selected basket. Paired monthly
delta B-A, IS 2014-19 / OOS 2020+. The DELTA is what's valid (absolute level = pooled proxy, not full rating).
profit_* = forward LABEL only. ROIC/PB rank == the justified-discount signal (r washes out of the rank).
"""
import duckdb, numpy as np, pandas as pd
PARQ = "data/bq_cache/ticker_prune.parquet"
q = f"""SELECT time,ticker,PE,PCF,PB,ROIC5Y,profit_1M,profit_2M
FROM read_parquet('{PARQ}')
WHERE time>=DATE '2014-01-01' AND PE>0 AND PB>0 AND ROIC5Y IS NOT NULL
AND ROE_Min3Y>=0 AND FSCORE>=5 AND Trading_Value_1M_P50>=5e9 AND profit_1M IS NOT NULL"""
df = duckdb.connect().execute(q).df()
df["ey"]  = np.where(df.PE>0, 1/df.PE, 0.0)
df["cfy"] = np.where(df.PCF>0, 1/df.PCF, 0.0)
df["rb"]  = df.ROIC5Y/df.PB                      # quality-adjusted book yield (== justified-discount rank)
df["time"]= pd.to_datetime(df.time); df["ym"]=df.time.dt.to_period("M")
month_last = df.groupby("ym")["time"].transform("max")
df = df[df.time==month_last].copy()              # monthly rebalance = last trading day each month
def zc(s):
    s=s.clip(s.quantile(.01),s.quantile(.99)); sd=s.std(); return (s-s.mean())/sd if sd>0 else s*0
g=df.groupby("ym")
df["zey"]=g["ey"].transform(zc); df["zcfy"]=g["cfy"].transform(zc); df["zrb"]=g["rb"].transform(zc)
df["A"]=df.zey+df.zcfy; df["B"]=df.zey+df.zcfy+df.zrb

K=25; rows=[]
for ym,gg in df.groupby("ym"):
    if len(gg)<50: continue
    tA=gg.nlargest(K,"A"); tB=gg.nlargest(K,"B")
    rows.append({"ym":ym, "yr":ym.year,
                 "A_1M":tA.profit_1M.mean(), "B_1M":tB.profit_1M.mean(),
                 "A_2M":tA.profit_2M.mean(), "B_2M":tB.profit_2M.mean(),
                 "overlap":len(set(tA.ticker)&set(tB.ticker))})
R=pd.DataFrame(rows)
def rep(lab,d):
    n=len(d)
    for h in ["1M","2M"]:
        a,b=d[f"A_{h}"].mean(),d[f"B_{h}"].mean(); dl=d[f"B_{h}"]-d[f"A_{h}"]
        t=dl.mean()/(dl.std()/np.sqrt(n)); win=(dl>0).mean()*100
        print(f"{lab:>9} {h:>3} | A {a:>5.2f}% B {b:>5.2f}% | delta {dl.mean():+.2f}pp (t={t:>4.1f}) win {win:>4.0f}% | n_months {n}")
print(f"Universe: {df.ticker.nunique()} names, {R.ym.min()}..{R.ym.max()}, top-{K} monthly, mean overlap {R.overlap.mean():.0f}/{K}\n")
print("basket forward return: A=ey+cfy (current value proxy)  B=+ROIC/PB.  delta=B-A (paired monthly).")
rep("ALL",R); rep("IS14-19",R[R.yr<=2019]); rep("OOS20+",R[R.yr>=2020])
print("\nPer-year delta (B-A, profit_1M, pp):")
print((R.groupby("yr").apply(lambda x:(x.B_1M-x.A_1M).mean(),include_groups=False)).round(2).to_string())
print("\nREAD: B beats A OOS with positive t + >50% win-months -> ROIC/PB improves SELECTION -> worth adding to rating_8l composite.")
print("Small/negative/flip -> value axis saturated; do NOT add. (DELTA valid; absolute level is a pooled proxy, not full archetype-routed rating.)")
