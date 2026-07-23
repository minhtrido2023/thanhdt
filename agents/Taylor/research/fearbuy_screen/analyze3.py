import csv, statistics as st, math
from collections import defaultdict
from datetime import date
rows=[]
with open('episodes2.csv') as f:
    for r in csv.DictReader(f):
        def fl(k):
            v=r.get(k,''); return float(v) if v not in ('','None') else None
        rows.append(dict(ticker=r['ticker'],date=r['entry_date'],yr=int(r['yr']),icb=r['ICB_Code'],
            PB=fl('PB'),roe=fl('ROE_Min3Y'),mkt_dd=fl('mkt_dd'),
            ex12=fl('ex12'),ex24=fl('ex24'),r12=fl('r12'),r24=fl('r24')))
def pdate(s): y,m,d=map(int,s.split('-')); return date(y,m,d)
def dedup(rs,gap=420):
    rs=sorted(rs,key=lambda x:(x['ticker'],x['date']));kept=[];last={}
    for x in rs:
        d=pdate(x['date']);lk=last.get(x['ticker'])
        if lk is None or (d-lk).days>gap: kept.append(x);last[x['ticker']]=d
    return kept
kept=dedup(rows)

# validate known cases caught
print("=== Known cases in screen? ===")
for tk in ('DGC','HPG','SSI'):
    hits=[x for x in kept if x['ticker']==tk]
    for h in hits: print(f"  {tk} {h['date']} PB={h['PB']} mkt_dd={h['mkt_dd']} ex12={h['ex12']} r24={h['r24']}")

def rule(x): return x['mkt_dd']<-0.30 and x['PB']<0.7 and (x['roe'] is not None and x['roe']>=0)
comb12=[x for x in kept if x['ex12'] is not None and rule(x)]
comb24=[x for x in kept if x['ex24'] is not None and rule(x)]

# tail analysis: absolute return, fraction big losers
print("\n=== TAIL (combined rule, absolute r24) ===")
r24v=[x['r24'] for x in comb24]
print(f"  n={len(r24v)} frac r24<-50%: {sum(1 for v in r24v if v<-0.5)/len(r24v):.1%}  frac r24<0: {sum(1 for v in r24v if v<0)/len(r24v):.1%}  frac r24>+100%: {sum(1 for v in r24v if v>1.0)/len(r24v):.1%}")
print("  worst 5 r24:", sorted([(round(x['r24'],2),x['ticker'],x['date']) for x in comb24])[:5])

# compare tail: BASE (no gates) vs combined
base24=[x for x in kept if x['r24'] is not None]
b=[x['r24'] for x in base24]
print(f"\n=== TAIL compare (r24<-50%) ===")
print(f"  BASE screen: n={len(b)} frac<-50%={sum(1 for v in b if v<-0.5)/len(b):.1%}")
print(f"  +deep-DD only: ", end="")
dd=[x['r24'] for x in kept if x['r24'] is not None and x['mkt_dd']<-0.30]
print(f"n={len(dd)} frac<-50%={sum(1 for v in dd if v<-0.5)/len(dd):.1%}")
print(f"  combined: n={len(r24v)} frac<-50%={sum(1 for v in r24v if v<-0.5)/len(r24v):.1%}")
# without golden floor
noroe=[x['r24'] for x in kept if x['r24'] is not None and x['mkt_dd']<-0.30 and x['PB']<0.7]
print(f"  deep-DD & PB<0.7 (NO roe floor): n={len(noroe)} frac<-50%={sum(1 for v in noroe if v<-0.5)/len(noroe):.1%}")
withlow=[x['r24'] for x in kept if x['r24'] is not None and x['mkt_dd']<-0.30 and x['PB']<0.7 and (x['roe'] is not None and x['roe']<0)]
print(f"  the roe<0 slice removed: n={len(withlow)} frac<-50%={(sum(1 for v in withlow if v<-0.5)/len(withlow) if withlow else 0):.1%} median={ (st.median(withlow) if withlow else 0):+.1%}")

# crisis-level sign test (N_eff = crisis years)
print("\n=== CRISIS-LEVEL robustness (combined rule, median excess per crisis-year) ===")
by=defaultdict(list)
for x in comb12: by[x['yr']].append(x['ex12'])
meds={y:st.median(v) for y,v in by.items()}
pos=sum(1 for m in meds.values() if m>0); tot=len(meds)
print(f"  crisis-years: {tot}, positive-median: {pos}")
print("  per-year median excess:", {y:round(meds[y],2) for y in sorted(meds)})
# binomial sign-test p (>=pos of tot at p=0.5)
from math import comb
p=sum(comb(tot,k) for k in range(pos,tot+1))/2**tot
print(f"  sign-test p(>= {pos}/{tot} positive | H0=0.5): {p:.4f}")

# commodity split under combined rule
def iscomm(icb): 
    return (icb[:2] in ('05','13','17')) or icb[:4] in ('2353','1757','1753')
print("\n=== commodity vs non (combined rule ex12) ===")
c=[x['ex12'] for x in comb12 if iscomm(x['icb'])]
o=[x['ex12'] for x in comb12 if not iscomm(x['icb'])]
print(f"  commodity: n={len(c)} median={st.median(c):+.1%}" if c else "  commodity n=0")
print(f"  non-comm : n={len(o)} median={st.median(o):+.1%}")
