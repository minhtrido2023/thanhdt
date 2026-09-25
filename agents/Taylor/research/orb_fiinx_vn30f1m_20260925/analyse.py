# -*- coding: utf-8 -*-
"""Phan tich doan MOI + DSR/PSR tren mau da mo rong."""
import numpy as np, pandas as pd
from scipy import stats as st

a = pd.read_csv("orb_trades_extended_20220217_20260925.csv")
a["dt"] = pd.to_datetime(a["date"])

def s(x, lab):
    n=len(x); mu=x.mean(); sd=x.std(ddof=1); sh=mu/sd*np.sqrt(252)
    nav=np.cumprod(1+x); mdd=(nav/np.maximum.accumulate(nav)-1).min()
    print("  %-30s n=%4d mean=%+7.2fbps Sharpe=%+6.2f cum=%+8.2f%% MaxDD=%+7.2f%% t=%+5.2f"
          %(lab,n,mu*1e4,sh,(nav[-1]-1)*100,mdd*100,mu/(sd/np.sqrt(n))))

print("=== 2023 tach theo nguon ===")
y23 = a[a["date"].str[:4]=="2023"]
for src,g in y23.groupby("src"): s(g["net"].values, "2023 %s (%s..%s)"%(src,g["date"].min(),g["date"].max()))

print("\n=== Nua nam ===")
a["half"] = a["date"].str[:4] + "H" + ((a["dt"].dt.month>6).astype(int)+1).astype(str)
for h,g in a.groupby("half"): s(g["net"].values, h+" ["+"/".join(sorted(g["src"].unique()))+"]")

print("\n=== Drawdown sau nhat cua doan MOI ===")
F = a[a["src"]=="fiinx"].reset_index(drop=True)
nav = np.cumprod(1+F["net"].values); dd = nav/np.maximum.accumulate(nav)-1
i = int(dd.argmin()); j = int(np.argmax(nav[:i+1]))
print("  peak %s -> day %s : %.2f%% (%d phien)"%(F["date"][j],F["date"][i],dd[i]*100,i-j))

print("\n=== PSR / DSR tren toan mau ghep (1129 trade) ===")
x = a["net"].values; n=len(x); mu=x.mean(); sd=x.std(ddof=1)
sk = st.skew(x); ku = st.kurtosis(x, fisher=False)
sr = mu/sd
def psr(sr, sr0, n, sk, ku):
    return st.norm.cdf((sr-sr0)*np.sqrt(n-1)/np.sqrt(1-sk*sr+(ku-1)/4*sr**2))
print("  SR/obs=%.5f skew=%.3f kurt=%.3f"%(sr,sk,ku))
print("  PSR(SR*=0) = %.4f"%psr(sr,0,n,sk,ku))
for N in (20,):
    g = 0.5772156649
    e = (1-g)*st.norm.ppf(1-1/N) + g*st.norm.ppf(1-1/(N*np.e))
    # sd cua SR giua cac trial: uoc bang sd cua SR/obs gia dinh ~ 1/sqrt(n)
    sr0 = e/np.sqrt(n)
    print("  DSR(N=%d, SR0=%.5f) = %.4f"%(N, sr0, psr(sr,sr0,n,sk,ku)))

print("\n=== So sanh 2 doan (khac biet co y nghia khong?) ===")
xF=a[a["src"]=="fiinx"]["net"].values; xL=a[a["src"]=="vnstock"]["net"].values
t=st.ttest_ind(xF,xL,equal_var=False)
print("  Welch t=%.3f p=%.4f | Mann-Whitney p=%.4f"%(t.statistic,t.pvalue,st.mannwhitneyu(xF,xL).pvalue))
print("  power: de phat hien delta=%.2fbps voi sd=%.2fbps can n~%.0f/nhom"
      %((xL.mean()-xF.mean())*1e4, x.std(ddof=1)*1e4,
        2*(x.std(ddof=1)/(xL.mean()-xF.mean()))**2*(1.96+0.84)**2))
