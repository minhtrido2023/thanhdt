import csv, statistics as st
from datetime import date
from math import comb
from collections import defaultdict
rows=[]
with open('episodes4.csv') as f:
    for r in csv.DictReader(f):
        def fl(k):
            v=r.get(k,''); 
            return float(v) if v not in ('','None','NaN') else None
        rows.append(dict(ticker=r['ticker'],date=r['entry_date'],yr=int(r['yr']),icb=r['ICB_Code'],
            PB=fl('PB'),roe=fl('ROE_Min3Y'),DE=fl('DE'),NPM=fl('NPM'),mkt_dd=fl('mkt_dd'),
            ex12=fl('ex12'),ex24=fl('ex24'),r12=fl('r12'),r24=fl('r24')))
def pdate(s): y,m,d=map(int,s.split('-')); return date(y,m,d)
def dedup(rs,gap=420):
    rs=sorted(rs,key=lambda x:(x['ticker'],x['date']));kept=[];last={}
    for x in rs:
        d=pdate(x['date']);lk=last.get(x['ticker'])
        if lk is None or (d-lk).days>gap: kept.append(x);last[x['ticker']]=d
    return kept

def base_rule(x): return x['mkt_dd']<-0.30 and x['PB']<0.7 and (x['roe'] is not None and x['roe']>=0)

def summ(rs, key='ex24'):
    v=[x[key] for x in rs if x[key] is not None]
    r24=[x['r24'] for x in rs if x['r24'] is not None]
    if not v: return "n=0"
    return (f"n={len(v)} med_{key}={st.median(v):+.1%} mean={st.mean(v):+.1%} "
            f"win={sum(1 for a in v if a>0)/len(v):.0%} | r24<-50%={sum(1 for a in r24 if a<-0.5)/len(r24):.1%} "
            f"r24<0={sum(1 for a in r24 if a<0)/len(r24):.0%}")

# dedup once at the deep-value candidate level (apply base_rule first so dedup anchors on real entries)
cand = dedup([x for x in rows if base_rule(x)], gap=420)
print(f"BASELINE combined rule (dedup 420): {summ(cand,'ex12')}")
print(f"BASELINE combined rule (dedup 420): {summ(cand,'ex24')}")
# PVX check
for x in cand:
    if x['ticker']=='PVX': print(f"  PVX in baseline: {x['date']} PB={x['PB']} DE={x['DE']} NPM={x['NPM']} r24={x['r24']:+.1%} ex24={x['ex24']:+.1%}")
print("  worst 8 r24:", sorted([(round(x['r24'],2),x['ticker'],x['date'],f\"DE{x['DE']}\",f\"NPM{x['NPM']}\") for x in cand if x['r24'] is not None])[:8])

def de_ok(x,cap): return x['DE'] is not None and x['DE']<=cap
def npm_ok(x,fl): return x['NPM'] is not None and x['NPM']>=fl

print("\n=== LEVERAGE CEILING sweep (Debt_Eq_P0 <= cap) ===")
for cap in (3.0,2.5,2.0,1.5):
    g=[x for x in cand if de_ok(x,cap)]
    dropped=[x['ticker'] for x in cand if not de_ok(x,cap)]
    print(f" DE<={cap}: {summ(g,'ex24')}  dropped={len(cand)-len(g)} {sorted(set(dropped))[:12]}")

print("\n=== MARGIN FLOOR sweep (NPM_P0 >= floor) ===")
for fl_ in (0.02,0.05,0.08):
    g=[x for x in cand if npm_ok(x,fl_)]
    print(f" NPM>={fl_}: {summ(g,'ex24')}  dropped={len(cand)-len(g)}")

print("\n=== COMBINED: DE<=2.5 AND NPM>=0.05 ===")
g=[x for x in cand if de_ok(x,2.5) and npm_ok(x,0.05)]
print(f" {summ(g,'ex12')}")
print(f" {summ(g,'ex24')}")
drop=[(x['ticker'],x['date'],x['DE'],x['NPM'],round(x['r24'],2)) for x in cand if not(de_ok(x,2.5) and npm_ok(x,0.05))]
print(f" dropped n={len(drop)}; of dropped r24<-30%: {sum(1 for d in drop if d[4] is not None and d[4]<-0.3)}/{len(drop)}")
print("  dropped sample (worst r24):", sorted([d for d in drop if d[4] is not None],key=lambda z:z[4])[:10])

# leverage-only, per-crisis-year sign test to confirm edge preserved
print("\n=== per-crisis-year median ex12: baseline vs DE<=2.5 ===")
for label,rs in (('baseline',cand),('DE<=2.5',[x for x in cand if de_ok(x,2.5)])):
    by=defaultdict(list)
    for x in rs:
        if x['ex12'] is not None: by[x['yr']].append(x['ex12'])
    meds={y:st.median(v) for y,v in by.items()}
    pos=sum(1 for m in meds.values() if m>0); tot=len(meds)
    p=sum(comb(tot,k) for k in range(pos,tot+1))/2**tot
    print(f" {label}: {pos}/{tot} yrs pos, p={p:.4f}, per-yr={ {y:round(meds[y],2) for y in sorted(meds)} }")
