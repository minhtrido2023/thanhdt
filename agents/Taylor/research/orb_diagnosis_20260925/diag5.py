import numpy as np, pandas as pd
from scipy import stats as st
m=pd.read_csv("tape_full.csv",parse_dates=["date"]).replace([np.inf,-np.inf],np.nan).sort_values("date").reset_index(drop=True)
m["agree"]=(m.gross>0).astype(float); m["absgross"]=m.gross.abs()
p=m.agree.mean(); n=len(m); W=m[m.gross>0].gross.mean(); L=m[m.gross<=0].gross.mean()
z=(p-0.5)/np.sqrt(0.25/n)
print("=== D. TOAN MAU 2022-02-17 -> 2026-09-25 ===")
print(f"n={n}  P(dung chieu)={p*100:.2f}%  z vs 50%={z:+.3f}  p={2*(1-st.norm.cdf(abs(z))):.4f}")
lo,hi=st.binomtest(int(m.agree.sum()),n).proportion_ci(0.95)
print(f"  CI95 cua P: [{lo*100:.2f}%, {hi*100:.2f}%]  -> CHUA loai duoc 50%")
print(f"lai TB khi thang W={W*100:.4f}%  lo TB khi thua L={L*100:.4f}%  payoff={abs(W/L):.3f}")
g_real=p*W+(1-p)*L; g_coin=0.5*(W+L); fee=m.fee.mean()
print(f"\nPHAN RA E[gross]={g_real*1e4:+.2f}bps:")
print(f"  (i) thanh phan DOI XUNG PAYOFF (gia su P=50%): {g_coin*1e4:+.2f}bps")
print(f"  (ii) thanh phan DU BAO CHIEU (P-50%)*(W-L):   {(p-0.5)*(W-L)*1e4:+.2f}bps")
print(f"  phi trung binh: {-fee*1e4:+.2f}bps -> E[net] {(g_real-fee)*1e4:+.2f}bps (thuc do {m.net.mean()*1e4:+.2f})")
print(f"  => NEU P dung bang 50% (dong xu), chien luoc van {(g_coin-fee)*1e4:+.2f}bps/phien")
# payoff asymmetry co y nghia khong? bootstrap
rng=np.random.default_rng(7); b=[]
gr=m.gross.values
for _ in range(20000):
    s=rng.choice(gr,n,replace=True); ww=s[s>0]; ll=s[s<=0]
    b.append(0.5*(ww.mean()+ll.mean()))
b=np.array(b); print(f"  bootstrap CI95 thanh phan payoff: [{np.percentile(b,2.5)*1e4:+.2f},{np.percentile(b,97.5)*1e4:+.2f}]bps, P(<=0)={np.mean(b<=0):.4f}")

print("\n=== E. BO LOC |OR|>=0.2%: delta (trong-ngoai) tren MOI cua so 74 phien lien tiep ===")
K=74; dl=[];pv=[]
for i in range(n-K+1):
    g=m.iloc[i:i+K]; a=g[g.absor>=0.002].net.values; c=g[g.absor<0.002].net.values
    if len(a)>2 and len(c)>2:
        dl.append((a.mean()-c.mean())*1e4); pv.append(st.ttest_ind(a,c,equal_var=False).pvalue)
dl=np.array(dl);pv=np.array(pv)
OBS=-17.29-31.06
print(f"so cua so={len(dl)}  delta: TB {dl.mean():+.2f}bps, sd {dl.std():.2f}, min {dl.min():+.1f}, max {dl.max():+.1f}")
print(f"  P(delta <= {OBS:.1f}bps quan sat o cua so live) = {np.mean(dl<=OBS)*100:.1f}%")
print(f"  P(|delta| >= {abs(OBS):.1f}) = {np.mean(np.abs(dl)>=abs(OBS))*100:.1f}%")
print(f"  P(Welch p <= 0.028) = {np.mean(pv<=0.028)*100:.1f}%  (neu KHONG co hieu ung that, ky vong ~2.8% -> quan sat duoc {np.mean(pv<=0.028)*100:.1f}%)")
print(f"  so lan doi DAU cua delta giua cac nam: 2022 -15.0 / 2023 +2.5 / 2024 -5.8 / 2025 +23.9 / 2026 -21.5 = 4/4 lan chuyen tiep doi dau")
