"""Buoc 2: correlation vs PROD breadth + predictive power IS/OOS."""
import pandas as pd, numpy as np
from scipy import stats
OUT="/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_breadth"
df=pd.read_csv(f"{OUT}/breadth_panel.csv",parse_dates=["d"])
df=df[df.d>="2014-01-01"].reset_index(drop=True)   # bo warmup 2013
IS=(df.d<"2020-01-01"); OOS=(df.d>="2020-01-01")

NEW=["B1_ad_line","B2_nhnl","B3_ma20","B3_ma50"]
PROD=["P_ma200","P_rsi_os"]
LVL={"B1_ad_line":"ad_line","B2_nhnl":"nhnl","B3_ma20":"b_ma20","B3_ma50":"b_ma50",
     "P_ma200":"b_ma200","P_rsi_os":"b_rsi_os"}

print("="*78);print("A) CORRELATION — metric MOI co trung lap voi 2 PROD breadth khong?");print("="*78)
print("\n[muc LEVEL]"); 
lv=df[[LVL[k] for k in NEW+PROD]].corr()
lv.columns=lv.index=NEW+PROD; print(lv.round(3).to_string())
print("\n[muc DIVERGENCE z(breadth,60)-z(vni,60)]")
dv=df[[f"div_{k}" for k in NEW+PROD]].corr(); dv.columns=dv.index=NEW+PROD
print(dv.round(3).to_string())

print("\n"+"="*78);print("B) PREDICTIVE POWER — Spearman IC(divergence_t, fwd VNINDEX ret)");print("="*78)
rows=[]
for k in NEW+PROD:
    for h in (5,20,60):
        r={"metric":k,"h":h}
        for lbl,m in (("IS",IS),("OOS",OOS),("Full",slice(None))):
            s=df.loc[m,[f"div_{k}",f"fwd{h}"]].dropna()
            ic,p=stats.spearmanr(s.iloc[:,0],s.iloc[:,1])
            r[f"IC_{lbl}"]=ic; r[f"p_{lbl}"]=p
        rows.append(r)
ic=pd.DataFrame(rows)
print(ic.to_string(index=False,float_format=lambda x:f"{x:+.4f}"))
ic.to_csv(f"{OUT}/ic_divergence.csv",index=False)

print("\n"+"="*78);print("C) TERCILE forward-return (divergence) — h=20, IS vs OOS");print("="*78)
for k in NEW+PROD:
    out=[]
    for lbl,m in (("IS",IS),("OOS",OOS)):
        s=df.loc[m,[f"div_{k}","fwd20"]].dropna().copy()
        s["t"]=pd.qcut(s[f"div_{k}"],3,labels=["LOW(pkyeu)","MID","HIGH(pkmanh)"])
        g=s.groupby("t",observed=True)["fwd20"].mean()*100
        out.append(f"{lbl}: L{g.iloc[0]:+.2f}% M{g.iloc[1]:+.2f}% H{g.iloc[2]:+.2f}% | H-L {g.iloc[2]-g.iloc[0]:+.2f}pp")
    print(f"{k:12s} "+"   ||   ".join(out))

print("\n"+"="*78);print("D) PER-YEAR IC (h=20) — 1-2 nam co ganh het edge khong?");print("="*78)
py=[]
for k in NEW+PROD:
    r={"metric":k}
    for y,g in df.groupby(df.d.dt.year):
        s=g[[f"div_{k}","fwd20"]].dropna()
        r[y]=stats.spearmanr(s.iloc[:,0],s.iloc[:,1])[0] if len(s)>30 else np.nan
    py.append(r)
print(pd.DataFrame(py).set_index("metric").to_string(float_format=lambda x:f"{x:+.2f}"))
