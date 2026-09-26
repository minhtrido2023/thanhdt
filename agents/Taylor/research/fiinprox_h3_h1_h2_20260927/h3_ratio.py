#!/usr/bin/env python3
"""Khop TY LE: delta PIT vs shares_delta / shares_total_after / exercise_ratio cua CA."""
import csv, bisect
from collections import defaultdict
from pathlib import Path
D = Path(__file__).resolve().parent; ROOT = D.parents[4]
tdays = [r["d"] for r in csv.DictReader(open(D/"tdays.csv"))]; tidx={d:i for i,d in enumerate(tdays)}
def tpos(d):
    if d in tidx: return tidx[d]
    i=bisect.bisect_left(tdays,d); return i if i<len(tdays) else len(tdays)-1
ca=defaultdict(list)
for r in csv.DictReader(open(D/"ca_iss_ais.csv")):
    ca[r["ticker"]].append(r)
evs=[]
for r in csv.DictReader(open(ROOT/"mike/data/fiinprox_oshares_pit_20260926.csv")):
    if not r["delta"] or "first_obs" in (r["flags"] or ""): continue
    sh,dl=float(r["shares"]),float(r["delta"]); b=sh-dl
    if b<=0 or abs(dl/b)<0.05: continue
    evs.append(dict(ticker=r["ticker"],date=r["date"],shares=sh,delta=dl,before=b,rel=dl/b))
def f(x):
    try: return float(x)
    except Exception: return None
# do phu cot CA
cov=defaultdict(int)
for t,rs in ca.items():
    for r in rs:
        cov[(r["event_code"],"shares_delta")] += bool(f(r["shares_delta"]))
        cov[(r["event_code"],"shares_total_after")] += bool(f(r["shares_total_after"]))
        cov[(r["event_code"],"exercise_ratio")] += bool(f(r["exercise_ratio"]))
        cov[(r["event_code"],"N")] += 1
for code in ("ISS","AIS"):
    n=cov[(code,"N")]
    print(f"do phu cot {code} (N={n}): shares_delta {cov[(code,'shares_delta')]/n:.0%} "
          f"shares_total_after {cov[(code,'shares_total_after')]/n:.0%} "
          f"exercise_ratio {cov[(code,'exercise_ratio')]/n:.0%}")
WIN=3
stats=defaultdict(int); bad=[]
for e in evs:
    if e["delta"]<=0: continue
    p=tpos(e["date"]); cands=[]
    for r in ca.get(e["ticker"],[]):
        for fl in ("exright_date","effective_date","issue_date"):
            if r[fl] and abs(tpos(r[fl])-p)<=WIN:
                cands.append(r); break
    if not cands: continue
    stats["matched_date"]+=1
    # 1) shares_delta: tong cac AIS/ISS trong cua so (nhieu tranche cung ngay)
    sds=[f(r["shares_delta"]) for r in cands if f(r["shares_delta"])]
    stas=[f(r["shares_total_after"]) for r in cands if f(r["shares_total_after"])]
    ok=None
    if sds:
        errs=[abs(e["delta"]-s)/e["delta"] for s in sds]+[abs(e["delta"]-sum(sds))/e["delta"]]
        ok=min(errs); stats["have_shares_delta"]+=1
    if stas:
        e2=min(abs(e["shares"]-s)/e["shares"] for s in stas)
        ok=e2 if ok is None else min(ok,e2); stats["have_total_after"]+=1
    if ok is None:
        stats["no_qty_col"]+=1
        ers=[f(r["exercise_ratio"]) for r in cands if f(r["exercise_ratio"])]
        if ers:
            stats["only_exercise_ratio"]+=1
            er=min(abs(e["rel"]-x/100.0) for x in ers)
            if er<=0.02*max(e["rel"],1e-9)+0.002: stats["exercise_ratio_ok"]+=1
        continue
    if ok<=0.01: stats["qty_ok_1pct"]+=1
    elif ok<=0.05: stats["qty_ok_5pct"]+=1
    else:
        stats["qty_bad"]+=1
        bad.append([e["ticker"],e["date"],int(e["delta"]),int(e["shares"]),round(ok,4),
                    ";".join(sorted({r["event_code"] for r in cands}))])
m=stats["matched_date"]
print(f"\nSu kien delta>0 khop ngay +/-3: {m}")
for k in ("have_shares_delta","have_total_after","no_qty_col","only_exercise_ratio",
          "exercise_ratio_ok","qty_ok_1pct","qty_ok_5pct","qty_bad"):
    print(f"  {k:22s} {stats[k]:5d}  ({100.0*stats[k]/m:.1f}%)")
q=stats["qty_ok_1pct"]+stats["qty_ok_5pct"]+stats["qty_bad"]
print(f"  => trong {q} su kien CO cot so luong: khop <=1% {100.0*stats['qty_ok_1pct']/q:.1f}%, "
      f"<=5% {100.0*(stats['qty_ok_1pct']+stats['qty_ok_5pct'])/q:.1f}%")
with open(D/"h3_qty_mismatch.csv","w",newline="") as fh:
    w=csv.writer(fh); w.writerow(["ticker","date","delta_pit","shares_after_pit","rel_err","ca_codes"])
    w.writerows(sorted(bad,key=lambda x:-x[4]))
print(f"-> {D/'h3_qty_mismatch.csv'} ({len(bad)} dong)")
