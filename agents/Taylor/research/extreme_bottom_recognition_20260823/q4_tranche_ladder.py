"""Q4 — thang tranche theo DO SAU episode (dd52), do theo EPISODE khong theo ngay.
Net = fwd12 - lai vay (gia dinh 12,5%/nam, cung gia dinh yeu nhat cua Phase 0)."""
import pandas as pd, numpy as np
D="/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/extreme_bottom_recognition_20260823"
MGN=0.125
d=pd.read_csv(f"{D}/daily_panel.csv",parse_dates=["time"]).sort_values("time").reset_index(drop=True)
ep=pd.read_csv(f"{D}/episodes_dd52.csv")
d["ep"]=None
for _,r in ep.iterrows(): d.loc[(d["time"]>=r.arm_date)&(d["time"]<=r.end_date),"ep"]=r.episode
A=d[d["ep"].notna()&d["fwd12"].notna()].copy()

BK=[(-0.20,-0.275,"T1 -20..-27.5"),(-0.275,-0.35,"T2 -27.5..-35"),
    (-0.35,-0.45,"T3 -35..-45"),(-0.45,-9,"T4 <=-45")]
print("=== Thang do sau dd52: fwd12 theo tung EPISODE (%) — o trong = episode khong bao gio dat do sau do ===")
tab={}
for lo,hi,lab in BK:
    s=A[(A["dd52"]<=lo)&(A["dd52"]>hi)]
    tab[lab]=s.groupby("ep")["fwd12"].median()*100
T=pd.DataFrame(tab)
T.loc["--- median cac episode ---"]=T.median()
T.loc["--- n episode ---"]=T.iloc[:-1].notna().sum()
T.loc["--- net sau vay 12,5% ---"]=T.loc["--- median cac episode ---"]-MGN*100
pd.set_option("display.width",200)
print(T.round(1).to_string())

print("\n=== So ngay moi buc / tong ngay armed 1622 ===")
print({lab:int(((A['dd52']<=lo)&(A['dd52']>hi)).sum()) for lo,hi,lab in BK})

# LOO theo episode cho buc T3+T4 gop (= de xuat V8)
s=A[A["dd52"]<=-0.35]; pe=s.groupby("ep")["fwd12"].median()
print(f"\n=== V8 candidate: dd52<=-35% ===\nper-episode fwd12: {(pe*100).round(1).to_dict()}")
print(f"median cac episode = {pe.median()*100:+.1f}% | net sau vay = {(pe.median()-MGN)*100:+.1f}pp | n_ep={len(pe)}")
loo={e:round((pe.drop(e).median()-MGN)*100,1) for e in pe.index}
print(f"LOO (bo tung episode) net: {loo}  -> min {min(loo.values()):+.1f}pp")
# so voi phan armed CON LAI (dd52 > -35) — chinh la phan bu
r=A[A["dd52"]>-0.35].groupby("ep")["fwd12"].median()
print(f"Phan bu (armed nhung dd52>-35%): per-ep {(r*100).round(1).to_dict()} | median {r.median()*100:+.1f}% | net {(r.median()-MGN)*100:+.1f}pp n_ep={len(r)}")
