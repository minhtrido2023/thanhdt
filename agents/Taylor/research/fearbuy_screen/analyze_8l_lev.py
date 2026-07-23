import csv, statistics as st
from datetime import date
from collections import defaultdict
COMMODITY={"DRI","PHR","DPR","GVR","TRC","HRC","HPG","HSG","NKG","SMC","POM","DCM","DPM","DDV","LAS","DGC","CSV"}
SUGAR={"SLS","SBT","LSS","KTS","QNS"}
CEMENT={"CLH","HT1","HOM","BCC","HVX","SCJ","BTS","QNC","CCM"}
rows=[]
with open('/tmp/panel_rl.csv') as f:
    for r in csv.DictReader(f):
        def fl(k):
            v=r.get(k,'')
            return float(v) if v not in ('','None','NaN') else None
        rows.append(dict(tk=r['ticker'],d=r['entry_date'],yr=int(r['yr']),
            icb=fl('ICB_Code'),DE=fl('DE_total'),rl=fl('real_lev'),r24=fl('r24')))
def pd_(s): y,m,dd=map(int,s.split('-')); return date(y,m,dd)
def dedup(rs,gap=420):
    rs=sorted(rs,key=lambda x:(x['tk'],x['d']));kept=[];last={}
    for x in rs:
        d=pd_(x['d']);lk=last.get(x['tk'])
        if lk is None or (d-lk).days>gap: kept.append(x);last[x['tk']]=d
    return kept
cand=dedup(rows)
print(f"deduped candidate episodes: n={len(cand)} (with r24: {sum(1 for x in cand if x['r24'] is not None)})")

def route(x):
    tk,icb=x['tk'],x['icb']
    if icb is None: return "COMPOUNDER"
    ic=int(icb)
    if ic==8355: return "BANK"
    if 8530<=ic<=8579: return "INSURANCE"
    if 8770<=ic<=8779: return "SECURITIES"
    if tk in COMMODITY or tk in SUGAR or tk in CEMENT: return "CYCLICAL"
    if ic==8633: return "REALESTATE"
    return "COMPOUNDER"

def gen_keep(x):  # generic Debt_Eq_P0 total-liab <= 2.5
    return x['DE'] is not None and x['DE']<=2.5

def routeaware_keep(x):  # 8L-style: real_lev(interest-bearing) thresholds by route; financials exempt
    r=route(x); rl=x['rl']
    if r in ("BANK","INSURANCE","SECURITIES"): return True          # leverage operational -> ignore
    if rl is None: return True                                       # fail-safe keep (no data)
    if r=="REALESTATE": return rl<=2.5                               # lenient real-debt (customer advances not counted)
    if r=="CYCLICAL":   return rl<=1.5                               # trough-fragile
    return rl<=3.0                                                    # COMPOUNDER

def med(rs,k='r24'):
    v=[x[k] for x in rs if x[k] is not None]
    return (st.median(v),st.mean(v),len(v)) if v else (None,None,0)

def report(name,keepfn):
    kept=[x for x in cand if keepfn(x)]
    drop=[x for x in cand if not keepfn(x)]
    dk=[x for x in drop if x['r24'] is not None]
    km,ka,kn=med(kept); dm,da,dn=med(drop)
    win_drop=sum(1 for x in dk if x['r24']>0.5)   # winners (>+50%) wrongly dropped
    dis_drop=sum(1 for x in dk if x['r24']<-0.3)  # disasters (<-30%) correctly dropped
    print(f"\n[{name}]")
    print(f"  KEPT n={kn} med_r24={km:+.1%} mean={ka:+.1%}")
    print(f"  DROPPED n={len(drop)} (w/r24 {dn}) med_r24={dm if dm is None else f'{dm:+.1%}'} | winners(>+50%) dropped={win_drop} | disasters(<-30%) dropped={dis_drop}")
    return kept,drop

print("\n=== ROUTE distribution of candidates ===")
rc=defaultdict(int)
for x in cand: rc[route(x)]+=1
print("  "+", ".join(f"{k}:{v}" for k,v in sorted(rc.items())))

kg,dg=report("A) GENERIC Debt_Eq_P0(total-liab) <= 2.5", gen_keep)
kr,dr=report("B) ROUTE-AWARE 8L real_lev(interest-bearing)", routeaware_keep)

# names dropped by generic but KEPT by route-aware (the false-positives generic destroys)
sg={(x['tk'],x['d']) for x in dg}; sr={(x['tk'],x['d']) for x in kr}
rescued=[x for x in cand if (x['tk'],x['d']) in sg and (x['tk'],x['d']) in sr and x['r24'] is not None]
rescued.sort(key=lambda z:-z['r24'])
print(f"\n=== Rescued by route-aware (generic DROPPED, 8L KEEPS) — n={len(rescued)}, med r24={st.median([x['r24'] for x in rescued]):+.1%} ===")
for x in rescued[:15]:
    print(f"  {x['tk']:5} {x['d']} {route(x):11} DE_total={x['DE']} real_lev={x['rl']} r24={x['r24']:+.1%}")

# PVX specifically
print("\n=== PVX check ===")
for x in cand:
    if x['tk']=='PVX':
        print(f"  PVX {x['d']} route={route(x)} DE_total={x['DE']} real_lev={x['rl']} r24={x['r24']} | gen_keep={gen_keep(x)} routeaware_keep={routeaware_keep(x)}")
