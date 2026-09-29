import numpy as np, pandas as pd, json
from scipy import stats as st
T="/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/orb_fiinx_vn30f1m_20260925/orb_trades_extended_20220217_20260925.csv"
d=pd.read_csv(T,parse_dates=["date"]).sort_values("date").reset_index(drop=True)
d["ym"]=d["date"].dt.to_period("M")
# gross (khong tru fee) de tach hieu ung phi
FEE=d["net"].iloc[0]  # khong dung; tinh lai gross tu gia
d["gross"]=d["sig"]*(d["exit29"]/d["entry"]-1)
d["fee"]=d["gross"]-d["net"]
# MFE / MAE trong cua so nam giu, theo chieu lenh
up=d["sig"]>0
d["mfe"]=np.where(up, d["maxhigh29"]/d["entry"]-1, 1-d["minlow29"]/d["entry"])
d["mae"]=np.where(up, 1-d["minlow29"]/d["entry"], d["maxhigh29"]/d["entry"]-1)
d["rng"]=(d["maxhigh29"]-d["minlow29"])/d["entry"]
d["eff"]=d["gross"]/d["rng"]          # -1..+1: +1 = di het bien do dung chieu
d["absor"]=d["or_ret"].abs()
d["gapov"]=d["c_first"]/d["exit29"].shift(1)-1   # gap qua dem (xap xi: close 14:29 hom truoc -> 09:00)

SEG=[("2022-02..2022-12 (bear 2022)","2022-02-01","2022-12-31"),
     ("2023-01..2023-09 (DOAN LO)","2023-01-01","2023-09-30"),
     ("2023-10..2024-12","2023-10-01","2024-12-31"),
     ("2025-01..2026-09","2025-01-01","2026-09-30")]
rows=[]
for nm,a,b in SEG:
    g=d[(d.date>=a)&(d.date<=b)]
    x=g["net"].values
    rows.append(dict(seg=nm,n=len(g),mean_bps=x.mean()*1e4,sd_bps=x.std(ddof=1)*1e4,
        sharpe_ann=x.mean()/x.std(ddof=1)*np.sqrt(250),cum_pct=(np.prod(1+x)-1)*100,
        winrate=(x>0).mean()*100, absor_bps=g["absor"].mean()*1e4,
        rng_pct=g["rng"].mean()*100, eff=g["eff"].mean(), eff_med=g["eff"].median(),
        mfe_pct=g["mfe"].mean()*100, mae_pct=g["mae"].mean()*100,
        absgap_bps=g["gapov"].abs().mean()*1e4,
        absnet_pct=g["gross"].abs().mean()*100))
R=pd.DataFrame(rows)
pd.set_option("display.width",250,"display.max_columns",50)
print("=== A. PHAN DOAN (tape ghep 1129 trade, config dang chay) ===")
print(R.round(3).to_string(index=False))

print("\n=== A2. THEO NAM ===")
yr=d.groupby("yr").apply(lambda g: pd.Series(dict(n=len(g),mean_bps=g.net.mean()*1e4,
   sharpe=g.net.mean()/g.net.std(ddof=1)*np.sqrt(250),wr=(g.net>0).mean()*100,
   absor_bps=g.absor.mean()*1e4,rng_pct=g.rng.mean()*100,eff=g.eff.mean(),
   eff_med=g.eff.median(),absgap_bps=g.gapov.abs().mean()*1e4)),include_groups=False)
print(yr.round(3).to_string())

# Welch doan lo vs phan con lai
L=d[(d.date>="2023-01-01")&(d.date<="2023-09-30")]["net"].values
O=d[~((d.date>="2023-01-01")&(d.date<="2023-09-30"))]["net"].values
t,p=st.ttest_ind(L,O,equal_var=False)
print(f"\nWelch doan-lo vs con-lai: t={t:.3f} p={p:.4f}  (nL={len(L)} nO={len(O)})")
for c in ["absor","rng","eff","mfe","mae"]:
    a=d[(d.date>="2023-01-01")&(d.date<="2023-09-30")][c].values
    b=d[~((d.date>="2023-01-01")&(d.date<="2023-09-30"))][c].values
    tt,pp=st.ttest_ind(a,b,equal_var=False)
    print(f"  {c:6s}: lo={a.mean():+.5f} conlai={b.mean():+.5f} Welch t={tt:+.2f} p={pp:.4f}")
d.to_csv("tape_enriched.csv",index=False)
R.to_csv("segment_stats.csv",index=False)
