import csv, statistics as st
from collections import defaultdict, Counter

rows=[]
with open('episodes.csv') as f:
    for r in csv.DictReader(f):
        def fl(k):
            v=r[k]
            return float(v) if v not in ('','None') else None
        rows.append(dict(ticker=r['ticker'], date=r['entry_date'], yr=int(r['yr']),
            icb=r['ICB_Code'], PB=fl('PB'), PE=fl('PE'), mkt_dd=fl('mkt_dd'),
            r12=fl('r12'), r24=fl('r24'), vni_r12=fl('vni_r12'), vni_r24=fl('vni_r24'),
            ex12=fl('ex12'), ex24=fl('ex24')))
print(f"total raw episodes: {len(rows)}")

# --- Dedup: min spacing 300 trading-ish days (~calendar) per ticker to avoid double-counting same crisis
from datetime import date
def pdate(s): y,m,d=map(int,s.split('-')); return date(y,m,d)
rows.sort(key=lambda x:(x['ticker'], x['date']))
kept=[]; last={}
for x in rows:
    d=pdate(x['date'])
    lk=last.get(x['ticker'])
    if lk is None or (d-lk).days>420:   # >~14 months apart = distinct crisis episode
        kept.append(x); last[x['ticker']]=d
print(f"after dedup (>420d apart per ticker): {len(kept)}")

def stats(vals, label):
    vals=[v for v in vals if v is not None]
    if not vals: 
        print(f"  {label}: n=0"); return
    n=len(vals); mean=st.mean(vals); med=st.median(vals)
    wr=sum(1 for v in vals if v>0)/n
    # winsorize 5/95
    sv=sorted(vals); lo=sv[int(0.05*n)]; hi=sv[int(0.95*n)]
    wv=[min(max(v,lo),hi) for v in vals]
    wmean=st.mean(wv)
    print(f"  {label}: n={n} mean={mean:+.1%} winsor_mean={wmean:+.1%} median={med:+.1%} winrate={wr:.0%} min={min(vals):+.0%} max={max(vals):+.0%}")

# only episodes with realized forward returns
r12set=[x for x in kept if x['ex12'] is not None]
r24set=[x for x in kept if x['ex24'] is not None]
print(f"\n=== OVERALL (dedup, realized fwd) ===")
print(f"episodes w/ r12: {len(r12set)}, w/ r24: {len(r24set)}")
stats([x['r12'] for x in r12set], "stock r12 (absolute)")
stats([x['ex12'] for x in r12set], "EXCESS ex12 vs VNINDEX")
stats([x['r24'] for x in r24set], "stock r24 (absolute)")
stats([x['ex24'] for x in r24set], "EXCESS ex24 vs VNINDEX")

print(f"\n=== PER CRISIS YEAR (excess 12m) ===")
byyr=defaultdict(list)
for x in r12set: byyr[x['yr']].append(x)
for y in sorted(byyr):
    stats([x['ex12'] for x in byyr[y]], f"yr {y}")

# commodity classification by ICB prefix
def icbcat(icb):
    if not icb: return 'unknown'
    p=icb[:2]
    # 05=oil&gas,13=chemicals,17=basic resources(steel/mining),18=const materials
    if p in ('05',): return 'oil_gas'
    if p in ('13',): return 'chemicals'
    if p in ('17',): return 'basic_resources'
    if icb[:4] in ('2353','1757','1753','1750'): return 'materials'
    return 'other'
print(f"\n=== COMMODITY vs OTHER (excess 12m) ===")
comm=[x for x in r12set if icbcat(x['icb']) in ('oil_gas','chemicals','basic_resources','materials')]
oth=[x for x in r12set if icbcat(x['icb']) not in ('oil_gas','chemicals','basic_resources','materials')]
stats([x['ex12'] for x in comm], "COMMODITY-ish")
stats([x['ex12'] for x in oth], "NON-commodity")

print(f"\n=== EXCLUDING super-cycle windows 2009 & 2020-21 entries (ex12) ===")
# entries whose 12m forward overlaps commodity supercycles: 2009 recovery, 2020-2021
robust=[x for x in r12set if x['yr'] not in (2009,2020,2021)]
stats([x['ex12'] for x in robust], "entries NOT in 2009/2020/2021")
stats([x['ex12'] for x in r12set if x['yr'] in (2009,2020,2021)], "entries IN 2009/2020/2021")

print(f"\n=== PB bucket (excess 12m, dedup) ===")
for name,lo,hi in [("PB<0.5",0,0.5),("0.5-0.7",0.5,0.7),("0.7-0.85",0.7,0.85),("0.85-1.0",0.85,1.0)]:
    sub=[x for x in r12set if lo<=x['PB']<hi]
    stats([x['ex12'] for x in sub], name)

print(f"\n=== distinct tickers, crisis-year counts ===")
print("episodes per year:", dict(sorted(Counter(x['yr'] for x in kept).items())))
