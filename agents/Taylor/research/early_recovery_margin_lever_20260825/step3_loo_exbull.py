"""Step 3 — per-episode breakdown, leave-one-out, EX-BULL swap."""
import pandas as pd, numpy as np, sys
W = "/home/trido/thanhdt/WorkingClaude"; sys.path.insert(0, W)
OUT = W + "/mike/agents/Taylor/research/early_recovery_margin_lever_20260825"
exec(open(OUT+"/step2_sim.py").read().split("# ---- bo episode ----")[0].replace(
     'print("=== gross exposure','pass #').replace('print(g_by.round(3).to_string())','pass'))

def metrics(nv):
    rr = nv.pct_change().dropna(); yrs=(nv.index[-1]-nv.index[0]).days/365.25
    c=((nv.iloc[-1]/nv.iloc[0])**(1/yrs)-1)*100; dd=(nv/nv.cummax()-1).min()*100
    return dict(CAGR=round(c,2),Sharpe=round(rr.mean()/rr.std()*np.sqrt(252),2),
                MaxDD=round(dd,1),Calmar=round(c/abs(dd),2),finalB=round(nv.iloc[-1]/1e9,1))

SET_A = ["2020-05-27","2020-07-17","2022-08-17","2023-04-12"]
EPISODES = {"2020_COVID": ["2020-05-27","2020-07-17"], "2022_SCB_leg1": ["2022-08-17"], "2023_SCB_leg2": ["2023-04-12"]}

print("### PER-EPISODE: return trong tung cua so (base vs f), interest=actual")
rows=[]
for f in [1.0,1.1,1.2,1.3]:
    for ep,dates in EPISODES.items():
        act,spans = build_window(dates)
        nv,b = sim(f, act, interest="actual")
        # return chi tinh trong cac phien active
        m = act.values
        seg_base = float(np.prod(1+np.nan_to_num(r.values[m]))-1)*100
        rr_lev = nv.pct_change().values
        seg_lev = float(np.prod(1+np.nan_to_num(rr_lev[m]))-1)*100
        # DD trong cua so (path-local)
        sub = nv[act]; ddw = ((sub/sub.cummax()-1).min()*100) if len(sub) else np.nan
        subb = nav[act]; ddb = ((subb/subb.cummax()-1).min()*100) if len(subb) else np.nan
        rows.append(dict(f=f, episode=ep, days=int(m.sum()),
                         ret_base_pct=round(seg_base,2), ret_lev_pct=round(seg_lev,2),
                         delta_pp=round(seg_lev-seg_base,2), DD_in_win_base=round(ddb,1), DD_in_win_lev=round(ddw,1),
                         max_borrow_pct=round(float(b.max())*100,1)))
print(pd.DataFrame(rows).to_string(index=False))

print("\n### LEAVE-ONE-OUT (Set A, interest=actual): bo tung episode")
loo=[]
for f in [1.1,1.2,1.3]:
    full_act,_ = build_window(SET_A); full = metrics(sim(f, full_act, interest="actual")[0])
    loo.append(dict(f=f, drop="(none)", **full))
    for ep,dates in EPISODES.items():
        keep = [x for x in SET_A if x not in dates]
        a,_ = build_window(keep); m = metrics(sim(f,a,interest="actual")[0])
        m["delta_vs_base_pp"]=round(m["CAGR"]-28.86,2)
        loo.append(dict(f=f, drop=ep, **m))
    loo[-4]["delta_vs_base_pp"]=round(full["CAGR"]-28.86,2)
print(pd.DataFrame(loo).to_string(index=False))

print("\n### BUOC 4 — EX-BULL vs EARLY-RECOVERY")
print("EX-BULL days (state=5):", int((d['state']==5).sum()),
      "| gross mean %.3f max %.3f -> tran 130%% CO BINDING khong?" % (gross[d['state']==5].mean(), gross[d['state']==5].max()))
exb = (state_s==5.0).shift(2).fillna(False)   # tre 1 phien thuc thi, giong build_window
combos = {
 "hien tai (base R3, EXBULL 130% danh nghia)": (None,1.0),
 "lever f=1.2 CHI o EX-BULL": (exb,1.2),
 "lever f=1.3 CHI o EX-BULL": (exb,1.3),
 "lever f=1.2 CHI o early-recovery (Set A)": (build_window(SET_A)[0],1.2),
 "lever f=1.3 CHI o early-recovery (Set A)": (build_window(SET_A)[0],1.3),
}
out=[]
for nm,(a,f) in combos.items():
    if a is None: m = metrics(nav); m["days_active"]=0
    else:
        m = metrics(sim(f,a,interest="actual")[0]); m["days_active"]=int(a.sum())
    m["config"]=nm; m["f"]=f; out.append(m)
print(pd.DataFrame(out)[["config","f","days_active","CAGR","Sharpe","MaxDD","Calmar","finalB"]].to_string(index=False))

print("\n### Cua so 18 thang co bao gio BINDING khong?")
for months in [6,12,18,24,36]:
    a,sp = build_window(SET_A, months=months)
    print(f"  cap {months}m: {a.sum()} phien active, ly do dong: {[s[2] for s in sp]}")
print("\n### Bo cong valuation (radar_cap=100 = tat gate dinh gia), Set A dates")
a2,sp2 = build_window(SET_A, radar_cap=100.0)
for E,C,why in sp2: print(f"   {E.date()} -> {C.date()} ({why})")
for f in [1.2,1.3]:
    print(f"  f={f}", metrics(sim(f,a2,interest="actual")[0]), "days", int(a2.sum()))
