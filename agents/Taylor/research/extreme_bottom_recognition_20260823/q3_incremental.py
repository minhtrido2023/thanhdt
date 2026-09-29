"""Q3 — spread DAILY co THEM thong tin so voi cong dd52 dang chay khong? Va N doc lap that la bao nhieu?"""
import pandas as pd, numpy as np
D="/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/extreme_bottom_recognition_20260823"
MGN_COST=0.125
d=pd.read_csv(f"{D}/daily_panel_spread.csv",parse_dates=["time"])
d=d[d["fwd12"].notna()&d["sp_ey_mgn"].notna()].copy()
d["armed"]=d["dd52"]<=-0.20
d["deep"] =d["dd52"]<=-0.35
d["sp0"]  =d["sp_ey_mgn"]>=0

def blocks(mask,gap=90):
    """N doc lap = so KHOI lien tuc cach nhau > gap ngay lich."""
    s=d.loc[mask,"time"].sort_values()
    if not len(s): return 0,[]
    b=[[s.iloc[0],s.iloc[0]]]
    for t in s.iloc[1:]:
        if (t-b[-1][1]).days<=gap: b[-1][1]=t
        else: b.append([t,t])
    return len(b),b

def rep(lab,mask):
    s=d[mask]
    if not len(s): print(f"{lab:38s} n=0"); return
    n,b=blocks(mask)
    med=[]
    for a,z in b: med.append(d[(d["time"]>=a)&(d["time"]<=z)&mask]["fwd12"].median())
    med=np.array(med); mm=np.median(med)
    loo=[np.median(np.delete(med,i)) for i in range(len(med))] if len(med)>1 else [np.nan]
    print(f"{lab:38s} n_day={len(s):5d} N_KHOI={n:2d} | fwd12 median-cua-khoi {mm:+7.1%} | net vay {mm-MGN_COST:+6.1%} "
          f"| %khoi>chi-phi {100*(med>MGN_COST).mean():3.0f}% | LOO net [{np.nanmin(loo)-MGN_COST:+.1%},{np.nanmax(loo)-MGN_COST:+.1%}]")

print("=== TAT CA do o cap KHOI DOC LAP (>90 ngay tach), khong phai cap NGAY ===")
rep("(0) toan bo mau 2007-2026",       pd.Series(True,index=d.index))
rep("(1) armed dd52<=-20% [DANG LIVE]", d["armed"])
rep("(2) armed & spread>=0",            d["armed"]&d["sp0"])
rep("(3) armed & spread<0",             d["armed"]&~d["sp0"])
rep("(4) KHONG armed & spread>=0",      (~d["armed"])&d["sp0"])
rep("(5) deep dd52<=-35% [V8a]",        d["deep"])
rep("(6) deep & spread>=0 [V8b]",       d["deep"]&d["sp0"])
rep("(7) spread>=0 (bat ke dd52) [V8c]",d["sp0"])
rep("(8) spread>=+1pp",                 d["sp_ey_mgn"]>=1.0)

print("\n=== Chong lan giua 2 truc (ngay armed) ===")
a=d[d["armed"]]
print(pd.crosstab(a["deep"],a["sp0"],rownames=["dd52<=-35%"],colnames=["spread>=0"]))
print(f"corr(dd52, spread) tren ngay armed = {a['dd52'].corr(a['sp_ey_mgn']):+.3f}")
print(f"corr(dd52, spread) toan mau        = {d['dd52'].corr(d['sp_ey_mgn']):+.3f}")
