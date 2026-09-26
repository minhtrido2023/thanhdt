import csv,bisect
from collections import defaultdict
from pathlib import Path
from datetime import date
D=Path(__file__).resolve().parent; ROOT=D.parents[4]
tdays=[r["d"] for r in csv.DictReader(open(D/"tdays.csv"))]; tidx={d:i for i,d in enumerate(tdays)}
def tpos(d):
    if d in tidx: return tidx[d]
    i=bisect.bisect_left(tdays,d); return i if i<len(tdays) else len(tdays)-1
ca=defaultdict(list)
for r in csv.DictReader(open(D/"ca_iss_ais.csv")): ca[r["ticker"]].append(r)
evs=[]
for r in csv.DictReader(open(ROOT/"mike/data/fiinprox_oshares_pit_20260926.csv")):
    if not r["delta"] or "first_obs" in (r["flags"] or ""): continue
    sh,dl=float(r["shares"]),float(r["delta"]); b=sh-dl
    if b<=0 or abs(dl/b)<0.05: continue
    evs.append(dict(ticker=r["ticker"],date=r["date"],delta=dl,rel=dl/b,shares=sh,before=b))
pos=[e for e in evs if e["delta"]>0]
for w in (3,5,10,20):
    n=0
    for e in pos:
        p=tpos(e["date"])
        if any(r[f] and abs(tpos(r[f])-p)<=w for r in ca.get(e["ticker"],[])
               for f in ("exright_date","effective_date","issue_date")): n+=1
    print(f"delta>0 khop +/-{w:<2d} : {n}/{len(pos)} = {100.0*n/len(pos):.1f}%")
# khoang cach ISS exright -> AIS effective cua CUNG ma, AIS dau tien sau exright
def dd(a,b):
    ya,ma,da=map(int,a.split("-")); yb,mb,db=map(int,b.split("-")); return (date(yb,mb,db)-date(ya,ma,da)).days
gaps=[]
for t,rs in ca.items():
    ex=sorted(r["exright_date"] for r in rs if r["event_code"]=="ISS" and r["exright_date"])
    ai=sorted(r["effective_date"] for r in rs if r["event_code"]=="AIS" and r["effective_date"])
    for x in ex:
        nxt=[a for a in ai if a>x]
        if nxt: gaps.append(dd(x,nxt[0]))
gaps.sort()
def pct(p): return gaps[int(p*(len(gaps)-1))]
print(f"\nkhoang cach ISS exright -> AIS effective ke tiep (N={len(gaps)}): "
      f"p10={pct(.1)} p25={pct(.25)} median={pct(.5)} p75={pct(.75)} p90={pct(.9)} ngay")
# hand-check MBB 2016-03-21
for r in csv.DictReader(open(ROOT/"mike/data/fiinprox_oshares_pit_20260926.csv")):
    if r["ticker"]=="MBB" and r["date"].startswith("2016"): print("PIT MBB:",r)
for r in ca.get("MBB",[]):
    if (r["exright_date"] or r["effective_date"] or "").startswith("2016"):
        print("CA MBB:",r["event_code"],r["exright_date"],r["effective_date"],r["exercise_ratio"],r["shares_delta"],r["issue_method"][:40])
