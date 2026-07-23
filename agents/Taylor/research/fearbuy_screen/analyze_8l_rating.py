import csv, statistics as st
from datetime import date
from collections import defaultdict
COMMODITY={"DRI","PHR","DPR","GVR","TRC","HRC","HPG","HSG","NKG","SMC","POM","DCM","DPM","DDV","LAS","DGC","CSV"}
SUGAR={"SLS","SBT","LSS","KTS","QNS"}; CEMENT={"CLH","HT1","HOM","BCC","HVX","SCJ","BTS","QNC","CCM"}
def fl(v): return float(v) if v not in ('','None','NaN',None) else None
rows=[]
with open('/tmp/panel_q.csv') as f:
    for r in csv.DictReader(f):
        rows.append({k:(r[k] if k in('ticker','entry_date') else fl(r[k])) for k in r})
def pd_(s): y,m,dd=map(int,s.split('-')); return date(y,m,dd)
def dedup(rs,gap=420):
    rs=sorted(rs,key=lambda x:(x['ticker'],x['entry_date']));kept=[];last={}
    for x in rs:
        d=pd_(x['entry_date']);lk=last.get(x['ticker'])
        if lk is None or (d-lk).days>gap: kept.append(x);last[x['ticker']]=d
    return kept
cand=dedup(rows)

def route(x):
    tk=x['ticker']; icb=x['ICB_Code']
    if icb is None: return "COMPOUNDER"
    ic=int(icb)
    if ic==8355: return "BANK"
    if 8530<=ic<=8579: return "INSURANCE"
    if 8770<=ic<=8779: return "SECURITIES"
    if tk in COMMODITY or tk in SUGAR or tk in CEMENT: return "CYCLICAL"
    if ic==8633: return "REALESTATE"
    return "COMPOUNDER"

def core_score(x):
    roic,roicm,roe_tr,de,fs,cfo_np=x['roic3y'],x['roic_min3y'],x['roe_tr'],x['real_lev'],x['FSCORE'],x['cfo_np']
    s=0
    s+=(2 if roic>=0.15 else 1 if roic>=0.10 else 0) if roic is not None else 0
    s+=(2 if roicm>=0.10 else 1 if roicm>=0.05 else 0) if roicm is not None else 0
    s+=(2 if roe_tr>=0.18 else 1 if roe_tr>=0.12 else 0) if roe_tr is not None else 0
    s+=(2 if de<=0.3 else 1 if de<=1.0 else 0) if de is not None else 0
    s+=(2 if (cfo_np is not None and cfo_np>=1.0 and x['cf_ttm'] and x['cf_ttm']>0) else 1 if (cfo_np is not None and cfo_np>=0.7) else 0)
    s+=(2 if fs>=8 else 1 if fs>=6 else 0) if fs is not None else 0
    return s
def bin_core(s): return 1 if s>=10 else 2 if s>=7 else 3 if s>=4 else 4 if s>=2 else 5

def rating_8l(x):
    rt=route(x); rl=x['real_lev']
    if rt in("BANK","INSURANCE"):
        roe=x['roe_tr'] if x['roe_tr'] is not None else x['roe3y']
        if roe is None: return 3
        if roe<0: return 5
        if rt=="INSURANCE": return 1 if roe>=0.15 else 2 if roe>=0.11 else 3 if roe>=0.07 else 4
        return 5 if roe<0.08 else 3 if roe<0.12 else 2   # bank: no AQ data PIT -> ROE tiers (>=0.12->2/3 band)
    if rt=="SECURITIES":
        roe=x['roe_tr'] if x['roe_tr'] is not None else x['roe3y']
        if roe is None: return 3
        if roe<0: return 5
        return 2 if roe>=0.13 else 3 if roe>=0.09 else 4 if roe>=0.05 else 5
    if rt=="REALESTATE":
        roe_tr,roic,de,fs,roicm=x['roe_tr'],x['roic3y'],rl,x['FSCORE'],x['roic_min3y']
        s=(2 if(roe_tr is not None and roe_tr>=0.18)else 1 if(roe_tr is not None and roe_tr>=0.10)else 0)
        s+=(2 if(roic is not None and roic>=0.12)else 1 if(roic is not None and roic>=0.07)else 0)
        s+=(2 if(de is not None and de<=0.5)else 1 if(de is not None and de<=1.5)else 0)
        s+=(1 if(x['cfo_np'] is not None and x['cfo_np']>=0.8)else 0)
        s+=(1 if(fs is not None and fs>=6)else 0)
        s+=(1 if(roicm is not None and roicm>=0)else 0)
        return 2 if s>=6 else 3 if s>=4 else 4
    # CYCLICAL / COMPOUNDER
    if rl is not None and rl>3: return 5
    s=core_score(x)
    if rt=="CYCLICAL":
        if rl is not None and rl>1.5: return 5
        prelim=bin_core(s)
        fortress=(rl is not None and rl<=0.2 and x['roic3y'] is not None and x['roic3y']>=0.20)
        return prelim if prelim>=2 else (1 if fortress else 2)
    prelim=bin_core(s)
    # gpm<0.15 -> WEAK moat, no notch (skip notch entirely as we lack moat audit)
    return prelim

for x in cand: x['route']=route(x); x['r8l']=rating_8l(x)

def gen_keep(x): return x['DE_total'] is not None and x['DE_total']<=2.5
def rl_keep(x):
    r=x['route']; rl=x['real_lev']
    if r in("BANK","INSURANCE","SECURITIES"): return True
    if rl is None: return True
    if r=="REALESTATE": return rl<=2.5
    if r=="CYCLICAL": return rl<=1.5
    return rl<=3.0
def r8l_keep(x): return x['r8l']<=3

def report(name,keepfn):
    kept=[x for x in cand if keepfn(x)]; drop=[x for x in cand if not keepfn(x)]
    kr=[x['r24'] for x in kept if x['r24'] is not None]; dr=[x['r24'] for x in drop if x['r24'] is not None]
    wd=sum(1 for v in dr if v>0.5); dd=sum(1 for v in dr if v<-0.3)
    km=f"{st.median(kr):+.1%}" if kr else "NA"; dm=f"{st.median(dr):+.1%}" if dr else "NA"
    print(f"[{name}] KEPT n={len(kept)}(r24 {len(kr)}) med={km} | DROP n={len(drop)}(r24 {len(dr)}) med={dm} winners_dropped={wd} disasters_dropped={dd}")

print(f"n_cand={len(cand)} (realized r24: {sum(1 for x in cand if x['r24'] is not None)})")
print("route dist:", dict(sorted(((k,sum(1 for x in cand if x['route']==k)) for k in set(x['route'] for x in cand)))))
print("8L rating dist:", dict(sorted(((k,sum(1 for x in cand if x['r8l']==k)) for k in set(x['r8l'] for x in cand)))))
print()
report("A generic DE_total<=2.5", gen_keep)
report("B route-aware real_lev", rl_keep)
report("C 8L rating<=3", r8l_keep)

# realized-only head-to-head: among episodes WITH r24, how does each gate's kept-set do
print("\n=== realized-only (n with r24) comparison ===")
real=[x for x in cand if x['r24'] is not None]
for nm,fn in (("no gate",lambda x:True),("A DE<=2.5",gen_keep),("B real_lev",rl_keep),("C 8L<=3",r8l_keep)):
    k=[x['r24'] for x in real if fn(x)]
    print(f"  {nm:12} n={len(k)} med={st.median(k):+.1%} mean={st.mean(k):+.1%} win={sum(1 for v in k if v>0)/len(k):.0%} blowup(<-50%)={sum(1 for v in k if v<-0.5)/len(k):.0%}")

# the 4 canonical cases
print("\n=== canonical cases (PIT 8L) ===")
for x in sorted(cand,key=lambda z:z['ticker']):
    if x['ticker'] in ("PVX","LPB","HDG","SCI","HBC"):
        print(f"  {x['ticker']:4} {x['entry_date']} {x['route']:11} DE_tot={x['DE_total']} real_lev={x['real_lev']} roic3y={x['roic3y']} FS={x['FSCORE']} cfo_np={x['cfo_np']} -> 8L={x['r8l']} | gen_keep={gen_keep(x)} 8L_keep={r8l_keep(x)} r24={x['r24']}")
