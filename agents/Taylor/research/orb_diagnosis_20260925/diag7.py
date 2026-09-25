import numpy as np, pandas as pd
from scipy import stats as st
pd.set_option("display.width",250)
m=pd.read_csv("tape_full.csv",parse_dates=["date"]).sort_values("date").reset_index(drop=True)
m["agree"]=(m.gross>0).astype(float)
def q5(df,col,lab):
    g=df.dropna(subset=[col]).copy(); g["q"]=pd.qcut(g[col],5,labels=[1,2,3,4,5],duplicates="drop")
    r=g.groupby("q",observed=True).apply(lambda z: pd.Series(dict(n=len(z),x=z[col].mean(),
      net_bps=z.net.mean()*1e4,Pdung=z.agree.mean()*100,
      sharpe=z.net.mean()/z.net.std(ddof=1)*np.sqrt(250))),include_groups=False)
    sp=st.spearmanr(g[col],g.net)
    print(f"\n--- {lab} ---"); print(r.round(3).to_string())
    print(f"Spearman rho={sp.statistic:+.4f} p={sp.pvalue:.4f} n={len(g)}")
print("=== H. DO 4 CO CHE UNG VIEN (moi cai mot bien quan sat duoc TRUOC/TAI 09:30) ===")
q5(m,"gapov","H1 GAP QUA DEM co dau (thong tin qua dem chay qua ATO?)")
m["absgap"]=m.gapov.abs(); q5(m,"absgap","H1b DO LON gap qua dem")
# ngay den dao han: thu 5 tuan 3
def exp_day(d):
    import calendar
    c=[x for x in pd.date_range(d.replace(day=1),d.replace(day=calendar.monthrange(d.year,d.month)[1])) if x.weekday()==3]
    return c[2]
m["expd"]=m.date.apply(exp_day); m["dte"]=(m.expd-m.date).dt.days
m.loc[m.dte<0,"dte"]=np.nan
print("\n--- H2 SO NGAY TOI DAO HAN (roll/expiry) ---")
print(m.dropna(subset=["dte"]).groupby(pd.cut(m.dte,[-1,2,7,14,40])).apply(lambda g: pd.Series(dict(
  n=len(g),net_bps=g.net.mean()*1e4,Pdung=g.agree.mean()*100)),include_groups=False).round(2).to_string())
print("ngay DAO HAN (dte=0):", end=" ")
z=m[m.dte==0]; print(f"n={len(z)} net={z.net.mean()*1e4:+.2f}bps")
q5(m,"rv20_lag","H3 VOL 20 PHIEN (lag1) — breakout can vol?")
q5(m,"vol_ma20_lag","H4 THANH KHOAN VN30 spot 20 phien (lag1)")
print("\n--- H5 THEO THU TRONG TUAN ---")
m["wd"]=m.date.dt.dayofweek
print(m.groupby("wd").apply(lambda g: pd.Series(dict(n=len(g),net_bps=g.net.mean()*1e4,
  Pdung=g.agree.mean()*100)),include_groups=False).round(2).to_string())
print("\n--- H6 dau OR: LONG vs SHORT (edge co phai chi la beta mua rong?) ---")
print(m.groupby("sig").apply(lambda g: pd.Series(dict(n=len(g),net_bps=g.net.mean()*1e4,
  Pdung=g.agree.mean()*100,sharpe=g.net.mean()/g.net.std(ddof=1)*np.sqrt(250))),include_groups=False).round(3).to_string())
vn=m.dropna(subset=["Close"]); dd=vn.Close.pct_change().mean()*1e4
print(f"  (tham chieu) VN30 spot buy&hold trung binh {dd:+.2f}bps/phien tren cung mau")
