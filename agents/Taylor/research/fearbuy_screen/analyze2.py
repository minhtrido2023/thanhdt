import csv, statistics as st
from collections import defaultdict, Counter
from datetime import date
rows=[]
with open('episodes2.csv') as f:
    for r in csv.DictReader(f):
        def fl(k):
            v=r.get(k,''); return float(v) if v not in ('','None') else None
        rows.append(dict(ticker=r['ticker'],date=r['entry_date'],yr=int(r['yr']),icb=r['ICB_Code'],
            PB=fl('PB'),PE=fl('PE'),roe=fl('ROE_Min3Y'),mkt_dd=fl('mkt_dd'),
            vni_r3m=fl('vni_r3m'),vni_r6m=fl('vni_r6m'),ex12=fl('ex12'),ex24=fl('ex24'),
            r12=fl('r12'),r24=fl('r24')))
def pdate(s): y,m,d=map(int,s.split('-')); return date(y,m,d)
def dedup(rs,gap=420):
    rs=sorted(rs,key=lambda x:(x['ticker'],x['date'])); kept=[];last={}
    for x in rs:
        d=pdate(x['date']);lk=last.get(x['ticker'])
        if lk is None or (d-lk).days>gap: kept.append(x);last[x['ticker']]=d
    return kept
def S(vals,label):
    vals=[v for v in vals if v is not None]
    if not vals: print(f"  {label}: n=0");return
    n=len(vals);sv=sorted(vals);lo=sv[int(0.05*n)];hi=sv[min(int(0.95*n),n-1)]
    wm=st.mean([min(max(v,lo),hi) for v in vals])
    print(f"  {label}: n={n} mean={st.mean(vals):+.1%} winsor={wm:+.1%} med={st.median(vals):+.1%} wr={sum(1 for v in vals if v>0)/n:.0%}")

kept=dedup(rows)
r12=[x for x in kept if x['ex12'] is not None]
print(f"BASE screen (dedup): n_realized12={len(r12)}")
S([x['ex12'] for x in r12],"ex12 ALL")

# --- TEST velocity gates to kill the 2010 slow-grind trap ---
for name,fn in [
  ("vni_r6m<-0.10 (recent sharp)", lambda x: x['vni_r6m'] is not None and x['vni_r6m']<-0.10),
  ("vni_r6m<-0.15", lambda x: x['vni_r6m'] is not None and x['vni_r6m']<-0.15),
  ("vni_r3m<-0.10", lambda x: x['vni_r3m'] is not None and x['vni_r3m']<-0.10),
  ("mkt_dd<-0.30 (deep)", lambda x: x['mkt_dd']<-0.30),
  ("mkt_dd<-0.35", lambda x: x['mkt_dd']<-0.35),
]:
    sub=[x for x in r12 if fn(x)]
    S([x['ex12'] for x in sub], name)

print("\n=== per-year under vni_r6m<-0.15 gate ===")
g=[x for x in r12 if x['vni_r6m'] is not None and x['vni_r6m']<-0.15]
by=defaultdict(list)
for x in g: by[x['yr']].append(x)
for y in sorted(by): S([x['ex12'] for x in by[y]],f"yr{y}")

print("\n=== per-year BASE (no velocity gate) for reference ===")
by=defaultdict(list)
for x in r12: by[x['yr']].append(x)
for y in sorted(by): S([x['ex12'] for x in by[y]],f"yr{y}")

# ROE_Min3Y golden-floor overlay
print("\n=== ROE_Min3Y>=0 golden-floor overlay (on base) ===")
S([x['ex12'] for x in r12 if x['roe'] is not None and x['roe']>=0], "roe_min3y>=0")
S([x['ex12'] for x in r12 if x['roe'] is not None and x['roe']<0], "roe_min3y<0 (excluded set)")
S([x['ex12'] for x in r12 if x['roe'] is None], "roe missing")

# combined: sharp panic + deep PB + quality
print("\n=== COMBINED RULE: mkt_dd<-0.30 & PB<0.7 & roe_min3y>=0 ===")
comb=[x for x in r12 if x['mkt_dd']<-0.30 and x['PB']<0.7 and (x['roe'] is not None and x['roe']>=0)]
S([x['ex12'] for x in comb],"combined ex12")
S([x['ex24'] for x in [x for x in dedup(rows) if x['ex24'] is not None and x['mkt_dd']<-0.30 and x['PB']<0.7 and (x['roe'] is not None and x['roe']>=0)]],"combined ex24")
by=defaultdict(list)
for x in comb: by[x['yr']].append(x)
print("  per-year:", {y:(len(by[y]),round(st.median([z['ex12'] for z in by[y]]),2)) for y in sorted(by)})
