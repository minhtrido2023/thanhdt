import numpy as np, pandas as pd
from scipy import stats as st
pd.set_option("display.width",250,"display.max_columns",60)
m=pd.read_csv("tape_full.csv",parse_dates=["date"]).replace([np.inf,-np.inf],np.nan)
m["agree"]=(m.gross>0).astype(float)          # SUA: dung chieu = lai truoc phi
m["absgross"]=m.gross.abs()
SEG=[("2022-02..2022-12","2022-02-01","2022-12-31"),("2023-01..2023-09 LO","2023-01-01","2023-09-30"),
     ("2023-10..2024-12","2023-10-01","2024-12-31"),("2025-01..2026-09","2025-01-01","2026-09-30")]
rr=[]
for nm,a,b in SEG:
    g=m[(m.date>=a)&(m.date<=b)]; p=g.agree.mean(); n=len(g); z=(p-0.5)/np.sqrt(0.25/n)
    win=g[g.gross>0].gross.mean(); los=g[g.gross<=0].gross.mean()
    rr.append(dict(seg=nm,n=n,P_dungchieu=p*100,z_vs50=z,p_binom=2*(1-st.norm.cdf(abs(z))),
      bien_do_pct=g.absgross.mean()*100, lai_tb_pct=win*100, lo_tb_pct=los*100,
      payoff=abs(win/los), net_bps=g.net.mean()*1e4, fee_bps=g.fee.mean()*1e4))
print("=== C(SUA). P(dung chieu) x BIEN DO — 'dung chieu' = gross>0 ===")
print(pd.DataFrame(rr).round(3).to_string(index=False))
print("\n=== C-yr ===")
print(m.groupby("yr").apply(lambda g: pd.Series(dict(n=len(g),P_dungchieu=g.agree.mean()*100,
  bien_do_pct=g.absgross.mean()*100,lai_tb=g[g.gross>0].gross.mean()*100,
  lo_tb=g[g.gross<=0].gross.mean()*100,net_bps=g.net.mean()*1e4)),include_groups=False).round(3).to_string())
# doan lo: so sanh voi phan con lai
L=m[(m.date>="2023-01-01")&(m.date<="2023-09-30")]; O=m[~m.index.isin(L.index)]
print(f"\nP(dung chieu) doan lo {L.agree.mean()*100:.2f}% vs con lai {O.agree.mean()*100:.2f}% "
      f"(chi2 p={st.chi2_contingency([[L.agree.sum(),len(L)-L.agree.sum()],[O.agree.sum(),len(O)-O.agree.sum()]])[1]:.4f})")
print(f"Bien do |gross| doan lo {L.absgross.mean()*100:.3f}% vs con lai {O.absgross.mean()*100:.3f}% "
      f"(Welch p={st.ttest_ind(L.absgross,O.absgross,equal_var=False).pvalue:.5f})")
print(f"Lai TB khi thang: lo {L[L.gross>0].gross.mean()*100:.3f}% vs con lai {O[O.gross>0].gross.mean()*100:.3f}%")
print(f"Lo TB khi thua : lo {L[L.gross<=0].gross.mean()*100:.3f}% vs con lai {O[O.gross<=0].gross.mean()*100:.3f}%")
