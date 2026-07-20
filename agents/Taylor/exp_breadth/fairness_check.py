"""Kiem tra CONG BANG: divergence-spec co dang lam yeu breadth mot cach oan uong khong?
KHONG phai trial moi (khong them metric) — chi kiem tra spec cua chinh minh."""
import pandas as pd, numpy as np
from scipy import stats
OUT="/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_breadth"
df=pd.read_csv(f"{OUT}/breadth_panel.csv",parse_dates=["d"])
df=df[df.d>="2014-01-01"].reset_index(drop=True)
IS=(df.d<"2020-01-01"); OOS=(df.d>="2020-01-01")
M={"B1_ad_line":"ad_line","B2_nhnl":"nhnl","B3_ma20":"b_ma20","B3_ma50":"b_ma50",
   "P_ma200":"b_ma200","P_rsi_os":"b_rsi_os"}

print("="*72);print("E) Dung LEVEL (khong phai divergence) — IC h=20/60");print("="*72)
for k,c in M.items():
    o=[]
    for h in (20,60):
        for lbl,m in (("IS",IS),("OOS",OOS)):
            s=df.loc[m,[c,f"fwd{h}"]].dropna()
            o.append(f"h{h}{lbl} {stats.spearmanr(s.iloc[:,0],s.iloc[:,1])[0]:+.3f}")
    print(f"{k:12s} "+"  ".join(o))

print("\n"+"="*72);print("F) CHI o DUOI cuc doan (decile 1 vs 10 cua divergence) — fwd20 mean");print("="*72)
for k in M:
    o=[]
    for lbl,m in (("IS",IS),("OOS",OOS)):
        s=df.loc[m,[f"div_{k}","fwd20"]].dropna()
        lo=s[s[f"div_{k}"]<=s[f"div_{k}"].quantile(.10)]["fwd20"].mean()*100
        hi=s[s[f"div_{k}"]>=s[f"div_{k}"].quantile(.90)]["fwd20"].mean()*100
        o.append(f"{lbl}: D1{lo:+.2f}% D10{hi:+.2f}% (n={len(s)//10})")
    print(f"{k:12s} "+" || ".join(o))

print("\n"+"="*72);print("G) SIGN-STABILITY scorecard (IS vs OOS cung dau?)");print("="*72)
ic=pd.read_csv(f"{OUT}/ic_divergence.csv")
ic["same_sign"]=np.sign(ic.IC_IS)==np.sign(ic.IC_OOS)
print(ic.groupby("metric")["same_sign"].agg(["sum","count"]).to_string())
print(f"\nTONG: {ic.same_sign.sum()}/{len(ic)} cap (metric,horizon) giu dung dau IS->OOS")
