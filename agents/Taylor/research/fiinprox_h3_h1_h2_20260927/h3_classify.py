#!/usr/bin/env python3
"""Phan lop su kien khong khop bang BANG CHUNG do duoc (khoang cach toi CA gan nhat,
dau delta, do phu CA cua ma/nam) — khong gan nguyen nhan."""
import csv, bisect
from collections import defaultdict
from pathlib import Path
D = Path(__file__).resolve().parent
ROOT = D.parents[4]
tdays = [r["d"] for r in csv.DictReader(open(D / "tdays.csv"))]
tidx = {d: i for i, d in enumerate(tdays)}
def tpos(d):
    if d in tidx: return tidx[d]
    i = bisect.bisect_left(tdays, d); return i if i < len(tdays) else len(tdays)-1

ca = defaultdict(list)
ca_year = defaultdict(int)
for r in csv.DictReader(open(D / "ca_iss_ais.csv")):
    ds = [x for x in (r["exright_date"], r["effective_date"], r["issue_date"]) if x]
    if not ds: continue
    ca[r["ticker"]].append((min(ds), r))
    ca_year[(r["ticker"], min(ds)[:4])] += 1

evs = []
for r in csv.DictReader(open(ROOT / "mike/data/fiinprox_oshares_pit_20260926.csv")):
    if not r["delta"] or "first_obs" in (r["flags"] or ""): continue
    sh, dl = float(r["shares"]), float(r["delta"]); b = sh - dl
    if b <= 0 or abs(dl/b) < 0.05: continue
    evs.append(dict(ticker=r["ticker"], date=r["date"], shares=sh, delta=dl, before=b, rel=dl/b))

def nearest(e):
    best = None
    for d, c in ca.get(e["ticker"], []):
        for f in ("exright_date", "effective_date", "issue_date"):
            if c[f]:
                g = tpos(c[f]) - tpos(e["date"])
                if best is None or abs(g) < abs(best[0]): best = (g, f, c)
    return best

matched = unmatched = 0
cls = defaultdict(int); rows = []
for e in evs:
    nb = nearest(e)
    if nb and abs(nb[0]) <= 3:
        matched += 1; continue
    unmatched += 1
    sign = "delta>0" if e["delta"] > 0 else "delta<0"
    if nb is None:
        k = f"{sign} | KHONG co dong ISS/AIS nao cho ma nay"
    elif ca_year[(e["ticker"], e["date"][:4])] == 0:
        k = f"{sign} | ma co CA nhung KHONG co dong ISS/AIS nao trong CUNG NAM"
    elif abs(nb[0]) <= 10:
        k = f"{sign} | co CA cach 4-10 phien"
    elif abs(nb[0]) <= 60:
        k = f"{sign} | co CA cach 11-60 phien"
    else:
        k = f"{sign} | CA gan nhat cach >60 phien (co dong trong cung nam)"
    cls[k] += 1
    rows.append([e["ticker"], e["date"], int(e["before"]), int(e["shares"]), int(e["delta"]),
                 round(100*e["rel"],3), nb[0] if nb else "", nb[1] if nb else "",
                 nb[2]["event_code"] if nb else "", ca_year[(e["ticker"], e["date"][:4])], k])

pos = [e for e in evs if e["delta"] > 0]; neg = [e for e in evs if e["delta"] < 0]
def r(sub):
    m = sum(1 for e in sub if (nb := nearest(e)) and abs(nb[0]) <= 3)
    return m, len(sub), 100.0*m/max(1,len(sub))
print(f"TONG      : {matched}/{len(evs)} = {100.0*matched/len(evs):.1f}% khop +/-3 phien")
print("delta > 0 : %d/%d = %.1f%%" % r(pos))
print("delta < 0 : %d/%d = %.1f%%  (ISS/AIS khong the mo ta giam so CP)" % r(neg))
print("\nLOP KHONG KHOP (bang chung, khong dien giai nguyen nhan):")
for k, v in sorted(cls.items(), key=lambda x: -x[1]):
    print(f"  {v:4d}  {k}")
with open(D / "h3_unmatched_classified.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ticker","date","shares_before","shares_after","delta","rel_pct",
                "nearest_ca_gap_tdays","nearest_ca_date_field","nearest_ca_event_code",
                "n_ca_rows_same_ticker_year","class"])
    w.writerows(sorted(rows, key=lambda x: (x[10], x[0], x[1])))
print(f"-> {D/'h3_unmatched_classified.csv'}")
