#!/usr/bin/env python3
"""H1 A/B — rate_bank_proxy (ROE-only, dang dung cho 2014-2026 trong fa_ratings_8l)
vs rate_bank (AQ-aware) voi NPL/LLR FiinPro 2010Q1-2026Q2.

PREREG (khoa truoc khi chay):
  - NPL/LLR chi dung cho THU HANG / cong nhi phan; KHONG dat nguong tuyet doi moi.
  - Tre cong bo: >=45 ngay sau ngay ket thuc quy; Q4 >=90 ngay.
  - Tieu chi GO: (b) so quyet dinh V2.4 doi == so do duoc; neu 0 thi khong chay R3.
"""
import csv, numpy as np
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
D=Path(__file__).resolve().parent

# ---- nguong NGUYEN VAN tu rating_8l.py::rate_bank / rating_8l_history.py::rate_bank_proxy ----
def rate_bank_aq(roe, npl, cov):
    if roe is None or np.isnan(roe): return 3
    if roe < 0.08: return 5
    pristine = npl is not None and not np.isnan(npl) and npl<=0.012 and cov is not None and not np.isnan(cov) and cov>=1.5
    strong   = npl is not None and not np.isnan(npl) and npl<=0.020 and cov is not None and not np.isnan(cov) and cov>=0.9
    if roe>=0.15 and pristine: return 1
    if roe>=0.14 and strong:   return 2
    if roe>=0.12: return 3
    return 4

def rate_bank_proxy(roe):
    if roe is None or np.isnan(roe): return 3
    if roe < 0.08: return 5
    if roe >= 0.18: return 1
    if roe >= 0.14: return 2
    if roe >= 0.12: return 3
    return 4

# ---- CHUNG MINH GIAI TICH: hai ham cho CUNG phan hoach <=3 / >=4 ----
grid_roe = [x/1000.0 for x in range(0, 501)]                      # ROE 0% -> 50%, buoc 0,1pp
grid_npl = [None, float("nan"), 0.0, 0.005, 0.012, 0.0121, 0.02, 0.0201, 0.05, 0.36]
grid_cov = [None, float("nan"), 0.0, 0.5, 0.899, 0.9, 1.4999, 1.5, 2.8]
bad=0; flip=0
for roe in grid_roe:
    p = rate_bank_proxy(roe)
    for npl in grid_npl:
        for cov in grid_cov:
            a = rate_bank_aq(roe, npl, cov)
            if (p<=3) != (a<=3): flip+=1
            if a<1 or a>5: bad+=1
print(f"[chung minh] luoi {len(grid_roe)}x{len(grid_npl)}x{len(grid_cov)} = "
      f"{len(grid_roe)*len(grid_npl)*len(grid_cov):,} to hop (ROE, NPL, coverage)")
print(f"[chung minh] so to hop ma CONG nhi phan (rating<=3) DOI dau: {flip}")
print("[chung minh] ly do: CA HAI ham deu tra <=3 khi va chi khi ROE>=12%; "
      "=4 khi 8%<=ROE<12%; =5 khi ROE<8%. NPL/coverage chi phan biet 1/2/3 BEN TRONG vung <=3.")

# ---- A/B THUC NGHIEM tren du lieu that ----
fin = defaultdict(dict)
for r in csv.DictReader(open(D/"bank_roe.csv")):
    roe = None
    for c in ("ROE_Trailing","ROE5Y","ROE3Y"):
        try:
            v=float(r[c])
            if v==v: roe=v; break
        except (TypeError,ValueError): pass
    fin[r["ticker"]][r["quarter"]] = dict(roe=roe, ftime=r["ftime"], rel=r["rel"])
fp = {}
for r in csv.DictReader(open(D.parents[4]/"mike/data/fiinprox_bank_ratios_quarterly_20260914.csv")):
    q = f"{r['year']}Q{r['quarter']}"
    def g(c):
        try:
            v=float(r[c]); return v if v==v else None
        except (TypeError,ValueError): return None
    fp[(r["ticker"], q)] = dict(npl=g("npl_ratio_3_5_pct"), llr=g("llr_coverage_pct"))

QEND={1:(3,31),2:(6,30),3:(9,30),4:(12,31)}
def avail_date(q):
    y=int(q[:4]); qq=int(q[-1]); m,dd=QEND[qq]
    return date(y,m,dd)+timedelta(days=90 if qq==4 else 45)

rows=[]; n_chg=0; n_gate=0; n_have_fp=0; dist=defaultdict(int)
for tk, qs in sorted(fin.items()):
    for q, v in sorted(qs.items()):
        roe=v["roe"]
        p=rate_bank_proxy(roe if roe is not None else float("nan"))
        # PIT: tai ngay hieu luc `eff`, dung quy FiinPro MOI NHAT ma da qua tre cong bo
        eff = v["rel"] or v["ftime"]
        try:
            ey,em,ed=map(int,eff[:10].split("-")); effd=date(ey,em,ed)
        except Exception: effd=None
        npl=cov=None; q_used=""
        if effd is not None:
            cands=[qq for (t2,qq) in fp if t2==tk and avail_date(qq)<=effd]
            if cands:
                q_used=max(cands, key=lambda qq:(int(qq[:4]), int(qq[-1])))
                f=fp[(tk,q_used)]
                npl = f["npl"]/100.0 if f["npl"] is not None else None
                cov = f["llr"]/100.0 if f["llr"] is not None else None
        if npl is not None or cov is not None: n_have_fp+=1
        a=rate_bank_aq(roe if roe is not None else float("nan"), npl, cov)
        dist[(p,a)]+=1
        if a!=p:
            n_chg+=1
            rows.append([tk,q,eff[:10] if eff else "",q_used,round(roe,4) if roe is not None else "",
                         round(npl*100,3) if npl else "", round(cov*100,1) if cov else "", p, a,
                         "GATE_FLIP" if (p<=3)!=(a<=3) else "rating_only"])
            if (p<=3)!=(a<=3): n_gate+=1
tot=sum(dist.values())
print(f"\n[thuc nghiem] {tot} dong (ma-quy) 8355 co ROE; {n_have_fp} dong CO NPL/LLR FiinPro "
      f"dung duoc sau tre cong bo ({100.0*n_have_fp/tot:.1f}%)")
print(f"[thuc nghiem] rating DOI: {n_chg} dong ({100.0*n_chg/tot:.1f}%)")
print(f"[thuc nghiem] quyet dinh V2.4 (cong nhi phan <=3) DOI: {n_gate}")
print("[thuc nghiem] ma tran proxy->AQ (chi cac o khac 0):")
for (p,a),c in sorted(dist.items()):
    if p!=a: print(f"    {p} -> {a}: {c}")
with open(D/"h1_rating_changes.csv","w",newline="") as fh:
    w=csv.writer(fh); w.writerow(["ticker","quarter","eff_date","fiinpro_quarter_used","roe","npl_pct","llr_pct",
                                  "rating_proxy","rating_aq","kind"]); w.writerows(rows)
print(f"-> {D/'h1_rating_changes.csv'} ({len(rows)} dong)")
# on dinh thu hang: so lan doi rating lien tiep cho moi ma
byt=defaultdict(list)
for r in rows: byt[r[0]].append(r[1])
print(f"[thuc nghiem] {len(byt)} ma co it nhat 1 quy doi rating; top: "
      + ", ".join(f"{k}({len(v)})" for k,v in sorted(byt.items(),key=lambda x:-len(x[1]))[:10]))
