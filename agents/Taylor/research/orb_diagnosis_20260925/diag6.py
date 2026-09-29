import numpy as np, pandas as pd
from scipy import stats as st
m=pd.read_csv("tape_full.csv",parse_dates=["date"]).sort_values("date").reset_index(drop=True)
x=m.net.values; n=len(x); MIN=100
def maxt(v):
    c1=np.cumsum(v); c2=np.cumsum(v*v); N=len(v)
    k=np.arange(MIN,N-MIN); n1=k; n2=N-k
    s1=c1[k-1]; s2=c1[-1]-s1; q1=c2[k-1]; q2=c2[-1]-q1
    m1=s1/n1; m2=s2/n2
    v1=(q1-n1*m1**2)/(n1-1); v2=(q2-n2*m2**2)/(n2-1)
    t=(m1-m2)/np.sqrt(v1/n1+v2/n2)
    return t,k
t,k=maxt(x); j=int(np.argmax(np.abs(t))); k0=int(k[j]); T=abs(t[j])
print("=== F. KIEM DINH DIEM GAY (sup-Wald, hoan vi) ===")
print(f"diem gay manh nhat: k={k0} ({m.date.iloc[k0].date()}), |t|max={T:.3f}")
print(f"  truoc: n={k0} mean={x[:k0].mean()*1e4:+.2f}bps | sau: n={n-k0} mean={x[k0:].mean()*1e4:+.2f}bps")
rng=np.random.default_rng(11)
null=np.array([np.abs(maxt(rng.permutation(x))[0]).max() for _ in range(5000)])
p=np.mean(null>=T)
print(f"  hoan vi 5000: |t|max null TB={null.mean():.3f}, 95pct={np.percentile(null,95):.3f}")
print(f"  p (da hieu chinh cho viec DO TIM diem gay) = {p:.4f}")
print("  => " + ("CO diem gay co y nghia" if p<0.05 else "KHONG loai duoc 'khong co diem gay' — bien dong nam trong pham vi nhieu"))
K=177
def worst(v):
    c=np.concatenate([[0],np.cumsum(v)]); s=(c[K:]-c[:-K])/K; return s.min()
obs=x[((m.date>="2023-01-01")&(m.date<="2023-09-30")).values].mean()
b=np.array([worst(rng.permutation(x)) for _ in range(5000)])
print(f"\n=== G. 'Doan 177 phien TE NHAT' co bat thuong khong? ===")
print(f"  quan sat 2023-01..09: {obs*1e4:+.2f}bps (n=177)")
print(f"  null iid: doan 177-phien te nhat TB {b.mean()*1e4:+.2f}bps, CI [{np.percentile(b,5)*1e4:+.2f},{np.percentile(b,95)*1e4:+.2f}]")
print(f"  p(te nhat cua chuoi ngau nhien <= quan sat) = {np.mean(b<=obs):.4f}")
