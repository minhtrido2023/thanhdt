"""A4 việc 1(d): CAGR FULL (lịch, như metrics.py) của 10 seed tie-break × {bq, pit}; sd, Δ ghép cặp theo seed, so với Δ −0,48pp."""
import glob, re, numpy as np, pandas as pd
def cagr(p):
    X=pd.read_csv(p,low_memory=False); X["ymd"]=pd.to_datetime(X["ymd"].astype(str).str[:10],errors="coerce")
    s=X[X.record_type=="DAILY"].set_index("ymd").sort_index()["combined_nav"].astype(float)
    return (s.iloc[-1]/s.iloc[0])**(365.25/(s.index[-1]-s.index[0]).days)-1
R={}
for p in glob.glob("ledgers/*exp_A4_TB*_s*_univpit*.csv"):
    m=re.search(r"TB(bq|pit)_s(\d+)_",p); R[(m[1],int(m[2]))]=cagr(p)*100
for k in ("bq","pit"):
    v=np.array([R[(k,s)] for s in sorted(s for (kk,s) in R if kk==k)]); print(f"{k}: n={len(v)} mean {v.mean():.2f} sd {v.std(ddof=1):.3f} min {v.min():.2f} max {v.max():.2f}  seeds:", " ".join(f"{x:.2f}" for x in v))
S=sorted(set(s for (k,s) in R if ("bq",s) in R and ("pit",s) in R)); d=np.array([R[("pit",s)]-R[("bq",s)] for s in S])
print(f"Δ(pit-bq) ghép theo seed n={len(S)}: mean {d.mean():+.3f}pp sd {d.std(ddof=1):.3f} se {d.std(ddof=1)/np.sqrt(len(d)):.3f}  t={d.mean()/(d.std(ddof=1)/np.sqrt(len(d))):.2f}; min {d.min():+.2f} max {d.max():+.2f}; số seed Δ<0: {(d<0).sum()}/{len(d)}")
print("Δ pin tie-break mặc định (không seed) = 22,91-23,39 = -0,48pp (A3)")
