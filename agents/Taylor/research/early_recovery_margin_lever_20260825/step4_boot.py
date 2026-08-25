"""Step 4 — bootstrap CI cho dCAGR + LOO cho bien KHONG gate dinh gia + kiem tra tre thuc thi."""
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
EP={"2020_COVID":["2020-05-27","2020-07-17"],"2022_SCB_leg1":["2022-08-17"],"2023_SCB_leg2":["2023-04-12"]}

print("### BIEN D: BO gate dinh gia (chi DT5G exit -> DT5G ve BEAR/CRISIS, cap 18m) — LOO")
rows=[]
for f in [1.2,1.3]:
    a,_=build_window(SET_A,radar_cap=100.0); m=metrics(sim(f,a,interest="actual")[0]); m.update(f=f,drop="(none)",days=int(a.sum()))
    rows.append(m)
    for ep,dates in EP.items():
        keep=[x for x in SET_A if x not in dates]
        a2,_=build_window(keep,radar_cap=100.0); m2=metrics(sim(f,a2,interest="actual")[0]); m2.update(f=f,drop=ep,days=int(a2.sum()))
        rows.append(m2)
df_=pd.DataFrame(rows); df_["dCAGR_pp"]=(df_["CAGR"]-28.86).round(2)
print(df_[["f","drop","days","CAGR","dCAGR_pp","Sharpe","MaxDD","Calmar","finalB"]].to_string(index=False))

print("\n### TRE THUC THI (lag): bien D f=1.3, do nhay")
for lag in [0,1,2,3,5]:
    a,_=build_window(SET_A,radar_cap=100.0,lag=lag); m=metrics(sim(1.3,a,interest="actual")[0])
    print(f"  lag={lag} phien: CAGR {m['CAGR']} Sharpe {m['Sharpe']} MaxDD {m['MaxDD']} Calmar {m['Calmar']}")

print("\n### LAI VAY do nhay (bien D f=1.3, actual-borrow)")
for i in [0.08,0.10,0.125,0.15]:
    a,_=build_window(SET_A,radar_cap=100.0); m=metrics(sim(1.3,a,interest="actual",i_ann=i)[0])
    print(f"  i={i*100:.1f}%/nam: CAGR {m['CAGR']} Calmar {m['Calmar']}")

print("\n### BOOTSTRAP khoi (block=63 phien, B=2000) cho dCAGR — Set A va bien D, f=1.3")
rng=np.random.default_rng(12345)
rb=r.values.copy(); n=len(rb)
for nm,rc in [("Set A (co gate dinh gia)",67.0),("Bien D (bo gate dinh gia)",100.0)]:
    a,_=build_window(SET_A,radar_cap=rc)
    nv,_b=sim(1.3,a,interest="actual"); rl=nv.pct_change().values
    diff=np.nan_to_num(rl-rb)          # chuoi chenh lech ngay
    L=63; nb=n//L
    stats=[]
    for _ in range(2000):
        st=rng.integers(0,n-L,size=nb)
        s=np.concatenate([diff[i:i+L] for i in st])
        stats.append(s.mean()*252*100)
    lo,hi=np.percentile(stats,[5,95]); obs=diff.mean()*252*100
    print(f"  {nm}: dCAGR quan sat ~{obs:+.2f}pp/nam (xap xi cong don) | boot 90% CI [{lo:+.2f}, {hi:+.2f}]pp | P(d<=0)={np.mean(np.array(stats)<=0)*100:.1f}%")
