"""Doi chieu voi ket qua da pin trong data/results_registry.md ("1/PE raw IC +0.125, t=11.0, hit 94%").
Muc tieu: cung 1 panel, cung 1 phuong phap => do rieng anh huong cua BIAS GIA DIEU CHINH."""
import numpy as np, pandas as pd
from scipy import stats
W="/home/trido/thanhdt/WorkingClaude"
df=pd.read_csv(f"{W}/data/value_panel_2014.csv",parse_dates=["time"],
               usecols=["ticker","time","PE","profit_2M","route","Close"])
px=pd.read_csv("px_factor.csv",parse_dates=["time"])
df=df.merge(px[["ticker","time","Price","Close"]].rename(columns={"Close":"Close_bq"}),on=["ticker","time"],how="left")
df["F"]=np.where(df.Close_bq>0, df.Price/df.Close_bq, np.nan)
print("khop Price:", f"{df.F.notna().mean():.1%}", "| F median theo nam:",
      df.groupby(df.time.dt.year).F.median().round(2).to_dict())
df["ey_uncorr"]=np.where(df.PE>0,1/df.PE,np.nan)                    # dung Y HET nhu panel pin
df["PE_corr"]=np.where((df.PE>0)&df.F.notna(),df.PE*df.F,np.nan)
df["ey_corr"]=np.where(df.PE_corr>0,1/df.PE_corr,np.nan)
# 1 obs/(ticker,quy) = ban ghi CUOI cua quy (dung method da pin)
df["q"]=df.time.dt.to_period("Q")
df=df.sort_values("time").groupby(["ticker","q"]).tail(1)
def ic(col):
    r=[]
    for q,g in df.groupby("q"):
        g=g[[col,"profit_2M"]].dropna()
        if len(g)<30: continue
        r.append(stats.spearmanr(g[col],g.profit_2M).statistic)
    x=np.array(r); se=x.std(ddof=1)/np.sqrt(len(x))
    return len(x),x.mean(),x.mean()/se,(x>0).mean()
for c in ["ey_uncorr","ey_corr"]:
    n,m,t,h=ic(c); print(f"  {c:10}: N={n} quy  IC={m:+.4f}  t={t:+.2f}  hit={h:.0%}")

# --- vi sao panel cua toi (co CONG rating<=3 + liq>=3ty) cho IC ~0? Tai lap cong ngay tren panel pin ---
print("\n--- ap CONG production len chinh panel pin (kiem tra pipeline cua toi co bug khong) ---")
d2=pd.read_csv(f"{W}/data/value_panel_2014.csv",parse_dates=["time"],
               usecols=["ticker","time","PE","profit_2M","turnover"])
d2=d2.merge(px[["ticker","time","Price","Close"]],on=["ticker","time"],how="left")
d2["F"]=np.where(d2.Close>0,d2.Price/d2.Close,np.nan)
d2["ey_corr"]=np.where((d2.PE>0)&d2.F.notna(),1/(d2.PE*d2.F),np.nan)
d2["ey_uncorr"]=np.where(d2.PE>0,1/d2.PE,np.nan)
fa=pd.read_csv("fa8l.csv",parse_dates=["time"]).sort_values("time")
out=[]
for tk,g in d2.groupby("ticker",sort=False):
    f=fa[fa.ticker==tk]
    if f.empty: continue
    out.append(pd.merge_asof(g.sort_values("time"),f[["time","rating"]],on="time",direction="backward"))
d2=pd.concat(out,ignore_index=True); d2["q"]=d2.time.dt.to_period("Q")
d2=d2.sort_values("time").groupby(["ticker","q"]).tail(1)
def ic2(d,col,lab):
    r=[]
    for q,g in d.groupby("q"):
        g=g[[col,"profit_2M"]].dropna()
        if len(g)<30: continue
        r.append(stats.spearmanr(g[col],g.profit_2M).statistic)
    x=np.array(r)
    if len(x)<3: print(f"  {lab}: N={len(x)} — qua mong"); return
    se=x.std(ddof=1)/np.sqrt(len(x))
    print(f"  {lab:38}: N={len(x)} quy  IC={x.mean():+.4f}  t={x.mean()/se:+.2f}  hit={(x>0).mean():.0%}")
for col in ["ey_uncorr","ey_corr"]:
    ic2(d2,col,f"{col} | toan universe")
    ic2(d2[d2.rating<=3],col,f"{col} | rating<=3")
    ic2(d2[(d2.rating<=3)&(d2.turnover>=3e9)],col,f"{col} | rating<=3 & turnover>=3ty")
    ic2(d2[d2.turnover>=3e9],col,f"{col} | turnover>=3ty")
