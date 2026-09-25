import numpy as np, pandas as pd
from scipy import stats as st
pd.set_option("display.width",250,"display.max_columns",60)
d=pd.read_csv("tape_enriched.csv",parse_dates=["date"])
d=d.replace([np.inf,-np.inf],np.nan)
v=pd.read_csv("vn30_daily.csv",parse_dates=["time"]).rename(columns={"time":"date"}).sort_values("date")
# --- bien QUAN SAT DUOC TRUOC PHIEN (khong look-ahead): dung shift(1) ---
v["ret"]=v.Close.pct_change()
v["rv20"]=v.ret.rolling(20).std()*np.sqrt(250)          # realized vol nam
v["rng_d"]=(v.High-v.Low)/v.Close
v["clr"]=(v.Close-v.Low)/(v.High-v.Low)                  # close-location: 1=dong o dinh
v["trendday"]=((v.clr>0.8)|(v.clr<0.2)).astype(float)    # ngay trend (dong o cuc tri)
v["trend60"]=v.trendday.rolling(60).mean()
v["gap"]=(v.Open/v.Close.shift(1)-1).abs()
v["vol_ma20"]=v.Volume.rolling(20).mean()
for c in ["rv20","rng_d","trend60","vol_ma20"]:
    v[c+"_lag"]=v[c].shift(1)                            # biet TRUOC khi vao lenh
m=d.merge(v[["date","rv20_lag","rng_d_lag","trend60_lag","vol_ma20_lag","clr","trendday"]],on="date",how="left")
print("=== B1. VN30 SPOT — dac diem theo doan (tinh doc lap voi tape phai sinh) ===")
SEG=[("2022-02..2022-12","2022-02-01","2022-12-31"),("2023-01..2023-09 LO","2023-01-01","2023-09-30"),
     ("2023-10..2024-12","2023-10-01","2024-12-31"),("2025-01..2026-09","2025-01-01","2026-09-30")]
rr=[]
for nm,a,b in SEG:
    g=v[(v.date>=a)&(v.date<=b)]
    rr.append(dict(seg=nm,n=len(g),rv20_ann_pct=g.rv20.mean()*100,rng_d_pct=g.rng_d.mean()*100,
      trendday_pct=g.trendday.mean()*100, clr_sd=g.clr.std(), gap_bps=g.gap.mean()*1e4,
      vol_trieu=g.Volume.mean()/1e6, ret_cum_pct=(g.Close.iloc[-1]/g.Close.iloc[0]-1)*100))
print(pd.DataFrame(rr).round(3).to_string(index=False))

print("\n=== B2. ORB net theo NGU PHAN VI realized-vol 20 phien (LAG 1 — khong look-ahead) ===")
mm=m.dropna(subset=["rv20_lag"]).copy()
mm["q"]=pd.qcut(mm.rv20_lag,5,labels=[1,2,3,4,5])
print(mm.groupby("q",observed=True).apply(lambda g: pd.Series(dict(n=len(g),
   rv20_pct=g.rv20_lag.mean()*100, mean_bps=g.net.mean()*1e4,
   sharpe=g.net.mean()/g.net.std(ddof=1)*np.sqrt(250), wr=(g.net>0).mean()*100,
   eff=g.eff.mean())),include_groups=False).round(3).to_string())
sp=st.spearmanr(mm.rv20_lag,mm.net); print(f"Spearman(rv20_lag, net) rho={sp.statistic:+.4f} p={sp.pvalue:.4f} n={len(mm)}")

print("\n=== B3. ORB net theo ngu phan vi TY LE NGAY-TREND 60 phien (lag 1) ===")
mt=m.dropna(subset=["trend60_lag"]).copy(); mt["q"]=pd.qcut(mt.trend60_lag,5,labels=[1,2,3,4,5])
print(mt.groupby("q",observed=True).apply(lambda g: pd.Series(dict(n=len(g),trend60=g.trend60_lag.mean(),
   mean_bps=g.net.mean()*1e4,sharpe=g.net.mean()/g.net.std(ddof=1)*np.sqrt(250))),include_groups=False).round(3).to_string())
sp=st.spearmanr(mt.trend60_lag,mt.net); print(f"Spearman(trend60_lag, net) rho={sp.statistic:+.4f} p={sp.pvalue:.4f}")

print("\n=== B4. |OR| — bien BIET TAI 09:30. net theo ngu phan vi |OR| TOAN MAU ===")
d2=d.dropna(subset=["absor"]).copy(); d2["q"]=pd.qcut(d2.absor,5,labels=[1,2,3,4,5])
print(d2.groupby("q",observed=True).apply(lambda g: pd.Series(dict(n=len(g),absor_bps=g.absor.mean()*1e4,
  mean_bps=g.net.mean()*1e4,sharpe=g.net.mean()/g.net.std(ddof=1)*np.sqrt(250),wr=(g.net>0).mean()*100,
  eff=g.eff.mean())),include_groups=False).round(3).to_string())
sp=st.spearmanr(d2.absor,d2.net); print(f"Spearman(|OR|, net) rho={sp.statistic:+.4f} p={sp.pvalue:.4f} n={len(d2)}")

print("\n=== B5. BO LOC |OR|>=0.2% — trong vs ngoai, THEO TUNG DOAN + tung nam ===")
def io(g):
    a=g[g.absor>=0.002].net.values; b=g[g.absor<0.002].net.values
    t,p=(st.ttest_ind(a,b,equal_var=False) if len(a)>2 and len(b)>2 else (np.nan,np.nan))
    return pd.Series(dict(n_in=len(a),in_bps=a.mean()*1e4 if len(a) else np.nan,
       n_out=len(b),out_bps=b.mean()*1e4 if len(b) else np.nan,
       delta_bps=(a.mean()-b.mean())*1e4 if len(a) and len(b) else np.nan,welch_t=t,p=p))
for nm,a,b in SEG:
    print(f"{nm:22s}",io(d[(d.date>=a)&(d.date<=b)]).round(3).to_dict())
print()
print(d.groupby("yr").apply(io,include_groups=False).round(3).to_string())
m.to_csv("tape_with_vn30.csv",index=False)
