#!/usr/bin/env python3
import csv, bisect
from collections import defaultdict
from pathlib import Path
D=Path(__file__).resolve().parent; ROOT=D.parents[4]
tdays=[r["d"] for r in csv.DictReader(open(D/"tdays.csv"))]; tidx={d:i for i,d in enumerate(tdays)}
def tpos(d):
    if d in tidx: return tidx[d]
    i=bisect.bisect_left(tdays,d); return i if i<len(tdays) else len(tdays)-1
ca=defaultdict(list)
for r in csv.DictReader(open(D/"ca_iss_ais.csv")): ca[r["ticker"]].append(r)
def f(x):
    try: return float(x)
    except Exception: return None
evs=[]
for r in csv.DictReader(open(ROOT/"mike/data/fiinprox_oshares_pit_20260926.csv")):
    if not r["delta"] or "first_obs" in (r["flags"] or ""): continue
    sh,dl=float(r["shares"]),float(r["delta"]); b=sh-dl
    if b<=0 or dl/b<0.05: continue
    evs.append(dict(ticker=r["ticker"],date=r["date"],shares=sh,delta=dl,before=b,rel=dl/b))
# 1) matched-by-which-code + gap distribution
bycode=defaultdict(int); bygap=defaultdict(int); pairs=[]
for e in evs:
    p=tpos(e["date"]); hits=[]
    for r in ca.get(e["ticker"],[]):
        for fl in ("exright_date","effective_date","issue_date"):
            if r[fl]:
                g=tpos(r[fl])-p
                if abs(g)<=3: hits.append((abs(g),g,fl,r)); break
    if not hits: continue
    hits.sort(key=lambda x:x[0])
    _,g,fl,r=hits[0]
    bycode[(r["event_code"],fl)]+=1; bygap[g]+=1
    pairs.append((e,r,fl,g,hits))
print("khop gan nhat theo (event_code, truong ngay):")
for k,v in sorted(bycode.items(),key=lambda x:-x[1]): print(f"  {k}: {v}")
print("phan bo gap (phien): "+" ".join(f"{k:+d}:{v}" for k,v in sorted(bygap.items())))
# 2) exercise_ratio vs rel — thu 2 don vi
ok1=ok100=n=0; ex=[]
for e,r,fl,g,hits in pairs:
    ers=[f(x["exercise_ratio"]) for _,_,_,x in hits if f(x["exercise_ratio"])]
    if not ers: continue
    n+=1
    s=sum(ers)
    if min(abs(e["rel"]-x) for x in ers+[s])<=0.02*e["rel"]+0.002: ok1+=1
    elif min(abs(e["rel"]-x/100) for x in ers+[s])<=0.02*e["rel"]+0.002: ok100+=1
    else: ex.append([e["ticker"],e["date"],round(100*e["rel"],3),";".join(str(x) for x in ers),
                     ";".join(sorted({x["issue_method"] for _,_,_,x in hits}))])
print(f"\nexercise_ratio co mat: {n}; khop khi doc la PHAN SO (1.0=100%): {ok1} ({100.0*ok1/max(1,n):.1f}%); "
      f"khop khi doc la PHAN TRAM: {ok100} ({100.0*ok100/max(1,n):.1f}%); lech ca 2: {len(ex)}")
with open(D/"h3_exratio_mismatch.csv","w",newline="") as fh:
    w=csv.writer(fh); w.writerow(["ticker","date","rel_pct_pit","exercise_ratio_ca","issue_method"])
    w.writerows(ex[:400])
print("mau 12 dong lech:")
for r in ex[:12]: print("   ",r)
