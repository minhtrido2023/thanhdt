"""Step 5 — CHUNG DOI CHIEU QUYET DINH: dieu kien hoa early-recovery co them gia tri gi
so voi 'lever mac dinh moi ngay khong-CRISIS/BEAR'? (dispatch khong hoi, nhung day la
chan doi chung duy nhat tach duoc 'edge cua CUA SO' khoi 'edge cua trien khai tien nhan roi')."""
import pandas as pd, numpy as np, sys
W="/home/trido/thanhdt/WorkingClaude"; sys.path.insert(0,W)
OUT=W+"/mike/agents/Taylor/research/early_recovery_margin_lever_20260825"
exec(open(OUT+"/step2_sim.py").read().split("# ---- bo episode ----")[0].replace(
     'print("=== gross exposure','pass #').replace('print(g_by.round(3).to_string())','pass'))
def metrics(nv):
    rr=nv.pct_change().dropna(); yrs=(nv.index[-1]-nv.index[0]).days/365.25
    c=((nv.iloc[-1]/nv.iloc[0])**(1/yrs)-1)*100; dd=(nv/nv.cummax()-1).min()*100
    return dict(CAGR=round(c,2),Sharpe=round(rr.mean()/rr.std()*np.sqrt(252),2),
                MaxDD=round(dd,1),Calmar=round(c/abs(dd),2),finalB=round(nv.iloc[-1]/1e9,1))
SET_A=["2020-05-27","2020-07-17","2022-08-17","2023-04-12"]
winA,_=build_window(SET_A); winD,_=build_window(SET_A,radar_cap=100.0)
notcb=(state_s.isin([3.0,4.0,5.0])).shift(2).fillna(False)          # moi phien NEUTRAL/BULL/EXBULL
neu  =(state_s==3.0).shift(2).fillna(False)                          # chi NEUTRAL
exb  =(state_s==5.0).shift(2).fillna(False)
bull =(state_s.isin([4.0,5.0])).shift(2).fillna(False)
cfg={"BASE R3 (f=1.0)":(None,1.0),
     "A. early-recovery + gate dinh gia":(winA,1.3),
     "D. early-recovery, BO gate dinh gia":(winD,1.3),
     "E. MOI phien NEUTRAL (khong dieu kien recovery)":(neu,1.3),
     "F. MOI phien khong-CRISIS/BEAR":(notcb,1.3),
     "G. chi BULL+EXBULL":(bull,1.3),
     "H. chi EX-BULL":(exb,1.3)}
rows=[]
for nm,(a,f) in cfg.items():
    if a is None: m=metrics(nav); m.update(days=0)
    else: m=metrics(sim(f,a,interest="actual")[0]); m.update(days=int(a.sum()))
    m["config"]=nm; m["dCAGR_pp"]=round(m["CAGR"]-28.86,2)
    m["pp_moi_100_phien_active"]=round(m["dCAGR_pp"]/max(m["days"],1)*100,3) if m["days"] else 0
    rows.append(m)
print(pd.DataFrame(rows)[["config","days","CAGR","dCAGR_pp","Sharpe","MaxDD","Calmar","finalB","pp_moi_100_phien_active"]].to_string(index=False))

print("\n### Ket hop EX-BULL + early-recovery (D) — co cong don khong?")
both = (winD | exb)
m=metrics(sim(1.3,both,interest="actual")[0]); print("  D + EXBULL f=1.3:", m, "days", int(both.sum()))

print("\n### Vay toi da (kiem tra tinh hop ly, quy chieu NAV 1 ty VND)")
for nm,a in [("A",winA),("D",winD),("F",notcb)]:
    _,b=sim(1.3,a,interest="actual")
    print(f"  {nm} f=1.3: vay max {b.max()*100:.1f}% NAV (= {b.max()*1e9/1e6:.0f} tr VND tren NAV 1 ty), "
          f"so phien thuc su vay {int((b>1e-9).sum())}/{int(a.sum())}, lai/nam toi da ~{b.max()*0.10*1e9/1e6:.1f} tr")
