#!/usr/bin/env python3
"""Candidate (a) vs (b) measured TOGETHER: park fraction grid re-scored with the REALISED
idle-cash carry (Trung vang, measured 8.55%/yr simple/365 from dnse_raw balances) credited on
POSITIVE idle cash, instead of the backtest's 0%/yr assumption.

Same 12 pinned legs, same paired block bootstrap (L=21, B=4000, seed=12345) as
park_fraction_grid_20260927/paired_v2.py -- so the carry question is answered on the SAME
criterion that produced the 0.80->0.30 decision, not a new one.

Carry is credited only on max(bal_cash_ref+lag_cash_ref, 0): negative cash = margin debt, which
the engine already charges at 10%/yr; crediting it would double-count.
"""
import glob, json, sys, numpy as np, pandas as pd

DATA = "/home/trido/thanhdt/WorkingClaude/data"
TAGS = ["000","010","020","030","040","050","060","070","075","080","090","100"]
XS = np.array([int(t)/100 for t in TAGS])
L, B, SEED = 21, 4000, 12345
CARRY = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0855   # %/yr simple, 365d

def load(tag):
    hits = sorted(glob.glob(f"{DATA}/*_parkgrid_{tag}_univpit.csv"))
    assert len(hits) == 1, (tag, hits)
    df = pd.read_csv(hits[0], low_memory=False)
    d = df.dropna(subset=["combined_nav"])
    t = pd.to_datetime(d["ymd"], errors="coerce")
    d = d[t.notna()].copy(); t = t[t.notna()]
    g = d.groupby(t.dt.normalize()).last()
    nav = g["combined_nav"].astype(float)
    cash = g[["bal_cash_ref","lag_cash_ref"]].fillna(0).sum(axis=1).astype(float)
    park = g[["bal_etf_ref","lag_etf_ref"]].fillna(0).sum(axis=1).astype(float)
    return nav, cash, park

NAV, CASH, PARK = {}, {}, {}
for t in TAGS:
    NAV[t], CASH[t], PARK[t] = load(t)
idx = NAV["000"].index
for t in TAGS:
    assert NAV[t].index.equals(idx), t
YRS = (idx[-1]-idx[0]).days/365.25
N = len(idx)-1
ANN = N/YRS
print(f"12 legs aligned, {len(idx)} days {idx[0].date()}->{idx[-1].date()}, {YRS:.3f} yrs, obs/yr={ANN:.1f}")
print(f"carry applied = {CARRY*100:.3f}%/yr simple on max(idle cash,0), 365-day accrual\n")

print(f"{'x':>5} {'cashShare%':>10} {'parkShare%':>10} {'poolShare%':>10} {'negCashDays%':>12} {'carry_pp/yr':>11}")
rows=[]
dts = np.array([(idx[i+1]-idx[i]).days for i in range(N)], dtype=float)
CARRY_RET = {}
for t in TAGS:
    nav, cash, park = NAV[t], CASH[t], PARK[t]
    cs = float((cash/nav).mean()); ps = float((park/nav).mean())
    neg = float((cash<0).mean())
    # daily carry as a fraction of NAV, credited over the calendar gap to the NEXT nav point
    cr = (np.maximum(cash.values[:-1],0.0)/nav.values[:-1]) * CARRY * dts/365.0
    CARRY_RET[t]=cr
    ann = (1+cr).prod()**(1/YRS)-1
    rows.append((t,cs,ps,cs+ps,neg,ann))
    print(f"{int(t)/100:5.2f} {cs*100:10.2f} {ps*100:10.2f} {(cs+ps)*100:10.2f} {neg*100:12.2f} {ann*100:11.3f}")

R0 = np.column_stack([np.diff(np.log(NAV[t].values)) for t in TAGS])
RC = np.column_stack([np.diff(np.log(NAV[t].values)) + np.log1p(CARRY_RET[t]) for t in TAGS])

def metrics(r):
    nav = np.exp(np.cumsum(r, axis=0)); peak = np.maximum.accumulate(nav, axis=0)
    yrs = r.shape[0]/ANN
    cagr = nav[-1]**(1/yrs)-1
    sh = r.mean(axis=0)/r.std(axis=0)*np.sqrt(ANN)
    dd = (nav/peak-1).min(axis=0)
    return cagr, sh, dd, cagr/np.abs(dd)

def boot(R):
    rng = np.random.default_rng(SEED); nblk = int(np.ceil(N/L)); off = np.arange(L)
    C=np.empty((B,12)); D=np.empty((B,12)); K=np.empty((B,12))
    for b in range(B):
        st = rng.integers(0,N,nblk)
        ix = ((st[:,None]+off[None,:]) % N).ravel()[:N]
        c,s,d,k = metrics(R[ix]); C[b],D[b],K[b]=c,d,k
    return C,D,K

out={}
for name,R in (("base0pct",R0),("carry",RC)):
    ACT=metrics(R); C,D,K=boot(R)
    D5=np.percentile(D,5,axis=0); C5=np.percentile(C,5,axis=0); K5=np.percentile(K,5,axis=0)
    EK=K.mean(axis=0); ED=D.mean(axis=0); EC=C.mean(axis=0)
    floor=D5[0]-0.02
    print(f"\n=== {name}: paired bootstrap (L=21,B=4000,seed=12345) ===")
    print(f"{'x':>5} {'CAGRact':>8} {'Calmar_act':>10} {'E[Calmar]':>9} {'Cal5th':>7} {'E[MaxDD]':>9} {'DD5th':>7} {'E[CAGR]':>8} {'CAGR5th':>8} {'gate2.0':>8}")
    for i,t in enumerate(TAGS):
        print(f"{XS[i]:5.2f} {ACT[0][i]*100:7.2f}% {ACT[3][i]:10.3f} {EK[i]:9.3f} {K5[i]:7.3f} {ED[i]*100:8.1f}% {D5[i]*100:6.1f}% {EC[i]*100:7.2f}% {C5[i]*100:7.2f}% {'OK' if D5[i]>=floor else 'FAIL':>8}")
    cand=[i for i in range(12) if D5[i]>=floor]
    best=max(cand,key=lambda i:EK[i]); tie=[i for i in cand if abs(EK[i]-EK[best])<0.03]
    pick=min(tie,key=lambda i:XS[i])
    print(f"  DD5th@x=0 {D5[0]*100:.2f}% -> floor {floor*100:.2f}% | pass {[float(XS[i]) for i in cand]}")
    print(f"  max E[Calmar] x={XS[best]:.2f}; tie {[float(XS[i]) for i in tie]} -> PICK x={XS[pick]:.2f}")
    out[name]={"cagr_act":[round(float(v)*100,3) for v in ACT[0]],
               "calmar_act":[round(float(v),4) for v in ACT[3]],
               "E_calmar":[round(float(v),4) for v in EK],
               "dd5_pct":[round(float(v)*100,2) for v in D5],
               "cagr5_pct":[round(float(v)*100,3) for v in C5],
               "E_cagr_pct":[round(float(v)*100,3) for v in EC],
               "gate_pass":[float(XS[i]) for i in cand],"pick":float(XS[pick]),
               "tie":[float(XS[i]) for i in tie]}
out["shares"]=[{"x":float(int(t)/100),"cash_share":round(r[1],4),"park_share":round(r[2],4),
                "pool_share":round(r[3],4),"neg_cash_days":round(r[4],4),
                "carry_pp_yr":round(r[5]*100,3)} for t,r in zip(TAGS,[r for r in rows])]
out["carry_rate"]=CARRY; out["N"]=int(N); out["yrs"]=round(YRS,4)
json.dump(out,open("carry_paired_results.json","w"),indent=1)
d0=np.array(out["base0pct"]["dd5_pct"]); d1=np.array(out["carry"]["dd5_pct"])
print(f"\nDD5th shift from carry (pp): {np.round(d1-d0,2).tolist()}")
print(f"CAGR_act shift from carry (pp): {np.round(np.array(out['carry']['cagr_act'])-np.array(out['base0pct']['cagr_act']),3).tolist()}")
print("wrote carry_paired_results.json")
