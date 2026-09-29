import numpy as np, pandas as pd
from scipy import stats as st
pd.set_option("display.width",250,"display.max_columns",60)
m=pd.read_csv("tape_with_vn30.csv",parse_dates=["date"]).replace([np.inf,-np.inf],np.nan)
v=pd.read_csv("vn30_daily.csv",parse_dates=["time"]).rename(columns={"time":"date"})
m=m.merge(v[["date","Close","Open","High","Low"]],on="date",how="left")
m["basis"]=m.exit29-m.Close                       # F(14:29) - S(ATC 14:45): xap xi, lech 16'
m["basis_bps"]=m.basis/m.Close*1e4
m["agree"]=(np.sign(m.gross)==np.sign(m.sig)).astype(float)   # dau ca ngay == dau OR
m["absgross"]=m.gross.abs()
SEG=[("2022-02..2022-12","2022-02-01","2022-12-31"),("2023-01..2023-09 LO","2023-01-01","2023-09-30"),
     ("2023-10..2024-12","2023-10-01","2024-12-31"),("2025-01..2026-09","2025-01-01","2026-09-30")]
print("=== C. PHAN RA 2 THANH PHAN: P(dung chieu) x BIEN DO ===")
rr=[]
for nm,a,b in SEG:
    g=m[(m.date>=a)&(m.date<=b)]
    p=g.agree.mean(); n=len(g)
    z=(p-0.5)/np.sqrt(0.25/n)
    rr.append(dict(seg=nm,n=n,P_dung_chieu=p*100,z_vs_50=z,p_binom=2*(1-st.norm.cdf(abs(z))),
      bien_do_pct=g.absgross.mean()*100, edge_xap_xi_bps=(2*p-1)*g.absgross.mean()*1e4,
      thuc_te_bps=g.net.mean()*1e4, basis_bps=g.basis_bps.mean(), basis_sd=g.basis_bps.std()))
print(pd.DataFrame(rr).round(3).to_string(index=False))
print("\n=== C2. BASIS (F-S) theo nam, va tuong quan voi net ===")
print(m.groupby("yr").apply(lambda g: pd.Series(dict(n=len(g),basis_bps=g.basis_bps.mean(),
  basis_sd=g.basis_bps.std(),pct_discount=(g.basis_bps<0).mean()*100,
  net_bps=g.net.mean()*1e4)),include_groups=False).round(2).to_string())
mb=m.dropna(subset=["basis_bps"]).copy()
mb["bl"]=mb.basis_bps.shift(1)
mb=mb.dropna(subset=["bl"]); mb["q"]=pd.qcut(mb.bl,5,labels=[1,2,3,4,5])
print("\nnet theo ngu phan vi BASIS HOM TRUOC (lag1, khong look-ahead):")
print(mb.groupby("q",observed=True).apply(lambda g: pd.Series(dict(n=len(g),basis_bps=g.bl.mean(),
  net_bps=g.net.mean()*1e4,sharpe=g.net.mean()/g.net.std(ddof=1)*np.sqrt(250))),include_groups=False).round(2).to_string())
sp=st.spearmanr(mb.bl,mb.net); print(f"Spearman(basis_lag1, net) rho={sp.statistic:+.4f} p={sp.pvalue:.4f}")
print("\n=== C3. VN30 SPOT: OR-sign co du bao dau ca ngay tren SPOT khong? (kiem doc lap) ===")
# proxy: dau (Open->Close) spot so voi dau OR phai sinh
m["spot_dir"]=np.sign(m.Close-m.Open)
print(m.groupby("yr").apply(lambda g: pd.Series(dict(n=len(g),
   P_OR_khop_spot=(np.sign(g.or_ret)==g.spot_dir).mean()*100)),include_groups=False).round(2).to_string())
print("\n=== C4. TU TUONG QUAN dau OR (co momentum qua ngay khong?) ===")
for nm,a,b in SEG:
    g=m[(m.date>=a)&(m.date<=b)]
    s=np.sign(g.or_ret.values); ac=np.corrcoef(s[:-1],s[1:])[0,1]
    print(f"  {nm:20s} corr(sig_t, sig_t+1)={ac:+.3f}  P(OR cung chieu voi net hom truoc)={(np.sign(g.or_ret.values[1:])==np.sign(g.gross.values[:-1])).mean()*100:.1f}%")
m.to_csv("tape_full.csv",index=False)
