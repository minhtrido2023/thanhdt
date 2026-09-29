#!/usr/bin/env python3
"""Tieu chi (2): tai ngay dong quy restate, fiinprox PIT phai cho so CU (truoc su kien).
Tach rieng lop 'du lieu som THAT' (ex-right da xay ra truoc ngay dong quy) — o lop do
PIT cho so MOI la DUNG, khong phai vi pham."""
import csv, bisect
from collections import defaultdict
from pathlib import Path
D=Path(__file__).resolve().parent; ROOT=D.parents[4]
pit=defaultdict(list)
for r in csv.DictReader(open(ROOT/"mike/data/fiinprox_oshares_pit_20260926.csv")):
    pit[r["ticker"]].append((r["date"], float(r["shares"])))
for t in pit: pit[t].sort()
def as_of(t,d):
    s=pit.get(t)
    if not s or d < s[0][0]: return None
    i=bisect.bisect_right([x[0] for x in s], d)-1
    return s[i][1]
iss=defaultdict(list)
for r in csv.DictReader(open(D/"ca_iss_ais.csv")):
    if r["event_code"]=="ISS" and r["exright_date"]: iss[r["ticker"]].append(r["exright_date"])
for t in iss: iss[t].sort()

rows=list(csv.DictReader(open(D/"restate_rows.csv")))
cls=defaultdict(int); detail=[]
for r in rows:
    t,d,osh = r["ticker"], r["fin_date"], float(r["osh"])
    v=as_of(t,d)
    if v is None:
        cls["PIT khong co so tai ngay do (ma ngoai universe / truoc mau)"]+=1; continue
    rel=abs(v-osh)/max(osh,1)
    # co ISS ex-right nao trong (fin_date, ais_eff) khong -> su kien CHUA xay ra tai fin_date?
    ex_before = [x for x in iss.get(t,[]) if x<=d]
    ex_between = [x for x in iss.get(t,[]) if d < x <= r["ais_eff_date"]]
    if rel > 0.001:
        cls["PIT cho so CU (dung PIT)"]+=1
    else:
        if ex_between and not ex_before:
            cls["PIT = so tuong lai, KHONG co ex-right nao <= ngay dong quy => VI PHAM PIT"]+=1
            detail.append([t,d,int(osh),int(v),r["ais_eff_date"],";".join(ex_between),"VIOLATION"])
        elif ex_before and ex_between:
            cls["PIT = so moi, CO ex-right <= ngay dong quy (du lieu som THAT, xem FPT)"]+=1
            detail.append([t,d,int(osh),int(v),r["ais_eff_date"],";".join(ex_between),"early_real"])
        elif ex_before:
            # ISS ex-right gan nhat TRUOC ngay dong quy: bao nhieu ngay?
            from datetime import date
            def dd(a,b):
                ya,ma,da=map(int,a.split("-")); yb,mb,db=map(int,b.split("-"))
                return (date(yb,mb,db)-date(ya,ma,da)).days
            gap=dd(ex_before[-1],d)
            if gap<=120:
                cls[f"PIT = so dong quy; ISS ex-right gan nhat cach {'<=120 ngay'} TRUOC ngay dong quy (AIS chi la thu tuc niem yet muon)"]+=1
                detail.append([t,d,int(osh),int(v),r["ais_eff_date"],ex_before[-1],"exright_before_le120d"])
            else:
                cls["PIT = so dong quy; ISS ex-right gan nhat >120 ngay truoc (khong xac dinh duoc)"]+=1
                detail.append([t,d,int(osh),int(v),r["ais_eff_date"],ex_before[-1],"undetermined_far"])
        else:
            cls["PIT = so dong quy; ma KHONG co ISS ex-right nao (khong xac dinh duoc bang CA)"]+=1
            detail.append([t,d,int(osh),int(v),r["ais_eff_date"],"","undetermined_no_iss"])
print(f"restate rows (tai lap {len(rows)}, pin 2026-08-13 = 2.667):")
for k,v in sorted(cls.items(),key=lambda x:-x[1]): print(f"  {v:5d}  {k}")
with open(D/"h3_restate_detail.csv","w",newline="") as fh:
    w=csv.writer(fh); w.writerow(["ticker","fin_date","oshares_fin","pit_asof","ais_eff_date","iss_exright_between","verdict"])
    w.writerows(sorted(detail,key=lambda x:(x[6],x[0],x[1])))
print(f"-> {D/'h3_restate_detail.csv'}")
