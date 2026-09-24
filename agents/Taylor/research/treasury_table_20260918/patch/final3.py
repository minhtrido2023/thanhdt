"""CHOT v3 — them 2 hang rao chong nham 'phat hanh' thanh 'ban CP quy'.
Ly do: ngay cua ISS/AIS TRE hon luc so CP thuc te doi (TPB: OShares nhay dung 100.000.000 trong
quy 2021Q2 nhung ISS record_date la 2021-09-14) => loc theo CUA SO NGAY bi ro.
  H1 VALUE-MATCH: |dOShares| trung (sai <0,5%) voi bat ky issue_volumn (ISS) / shares_delta (AIS)
     nao CUA CHINH MA DO o BAT KY ngay nao  -> tu choi (ISSUANCE_MATCH).
  H2 TRAN QUY MO 10% OShares: co CP quy that co p95=9,3% (n=112) => tren 10% nhieu kha nang la
     phat hanh. Danh doi do duoc: bo sot ~5/112 (4,5%) su kien that su lon.
"""
import pandas as pd, numpy as np, os
D=os.path.dirname(os.path.abspath(__file__))
ev  = pd.read_csv(f"{D}/events.csv", parse_dates=["public_date"])
fin = pd.read_csv(f"{D}/fin.csv",    parse_dates=["time"])
ca  = pd.read_csv(f"{D}/ca.csv",     parse_dates=["effective_date","record_date","issue_date"])
fin = fin.dropna(subset=["OShares"]); fin=fin[fin.OShares>0].sort_values(["ticker","time"])
# VA (Taylor 2026-09-18, job _103820): them SUSP/NLIS/MOVE — 3 ma nay CO shares_delta
# (SUSP 54 dong / NLIS 1 tren tap ticker nay) nen bo sot chung = lo hong confounder y het
# ISS/DIV da tung quy nham phat hanh thanh "ban CP quy" (ca VPB/TPB).
SHARE_CODES={"ISS","DIV","AIS","MA","SUSP","NLIS","MOVE"}
cac=ca[ca.event_code.isin(SHARE_CODES)].copy()
# tap gia tri phat hanh da biet cua tung ma (bat ky ngay nao)
issue_vals={}
for t,g in cac.groupby("ticker"):
    v=set(g.issue_volumn.dropna().astype("int64")) | set(g.shares_delta.dropna().astype("int64"))
    issue_vals[t]={x for x in v if x>0}
fin_by_t={t:g for t,g in fin.groupby("ticker")}; ca_by_t={t:g for t,g in cac.groupby("ticker")}
ev_by_t={t:g for t,g in ev.groupby("ticker")}
SIGN={"buy_done":-1,"sell_done":+1}; MAX_EXTRA=1; CAP=0.10

def ca_in(t,lo,hi):
    g=ca_by_t.get(t)
    if g is None: return 0
    m=False
    for c in ("effective_date","record_date","issue_date"): m=m|((g[c]>lo)&(g[c]<=hi))
    return int(m.sum())

def issuance_match(t,x):
    for v in issue_vals.get(t,()):
        if abs(x-v)<=max(1,0.005*v): return v
    return None

def infer(row):
    t,d,at=row.ticker,row.public_date,row.action_type
    g=fin_by_t.get(t)
    if g is None or len(g)<2: return None,"NO_DATA",""
    before,after=g[g.time<d],g[g.time>=d]
    if before.empty or after.empty: return None,"NO_DATA",""
    b=before.iloc[-1]
    for k in range(min(MAX_EXTRA+1,len(after))):
        a=after.iloc[k]; lo,hi=b.time,a.time
        if len(ev_by_t[t][(ev_by_t[t].public_date>lo)&(ev_by_t[t].public_date<=hi)])>1:
            return None,"MULTI_EVENT",f"{lo.date()}..{hi.date()}"
        dd=a.OShares-b.OShares
        if dd==0: continue
        if ca_in(t,lo,hi)>0: return None,"CA_CONFOUNDED",f"ISS/DIV/AIS trong {lo.date()}..{hi.date()}"
        mv=issuance_match(t,abs(dd))
        if mv is not None: return None,"ISSUANCE_MATCH",f"|dOSh|={int(abs(dd)):,} == phat hanh da biet {int(mv):,}"
        if np.sign(dd)!=SIGN[at]: return None,"SIGN_MISMATCH",f"dOSh={int(dd):,}"
        pct=abs(dd)/b.OShares
        if pct>CAP: return None,"OVER_CAP",f"{pct:.1%} > tran {CAP:.0%}"
        return int(abs(dd))*SIGN[at],"HIGH",f"dOSh={int(dd):,} ({pct:.2%}) q{lo.date()}..{hi.date()}"
    return None,"NO_MOVE","OShares bat dong qua 2 quy ke tiep"

r=ev.apply(lambda x: pd.Series(infer(x),index=["inferred","tier","why"]),axis=1)
out=pd.concat([ev,r],axis=1); out["is_unsized"]=out.shares_delta.isna()
ctl=out[~out.is_unsized].copy(); ctl["truth"]=ctl.shares_delta.abs()*ctl.action_type.map(SIGN)
hit=ctl[ctl.inferred.notna()].copy(); hit["err"]=(hit.inferred-hit.truth).abs()/hit.truth.abs()
print("="*74); print("CONTROL (131 su kien DA BIET co) — v3"); print("="*74)
print(f"  suy duoc {len(hit)}/131 | khop CHINH XAC {(hit.err<=0).sum()} ({(hit.err<=0).mean():.1%})"
      f" | sai<=5% {(hit.err<=.05).sum()} ({(hit.err<=.05).mean():.1%}) | sai<=20% {(hit.err<=.20).sum()} ({(hit.err<=.20).mean():.1%})")
for _,x in hit[hit.err>0.05].iterrows():
    print(f"    truot: {x.ticker:<5} {x.public_date.date()} {x.action_type:<9} that={int(x.truth):>10,} suy={int(x.inferred):>10,} sai={x.err:.1%}")
uns=out[out.is_unsized]
print("\n"+"="*74); print(f"NHOM THIEU CO (n={len(uns)})"); print("="*74)
for k,v in uns.tier.value_counts().items(): print(f"  {k:<16}{v:>4} ({v/len(uns):5.1%})")
got=uns[uns.inferred.notna()]
print(f"\n  SUY DUOC: {len(got)}/{len(uns)} ({len(got)/len(uns):.1%}) tren {got.ticker.nunique()} ma")
print(f"  KHONG CO DU LIEU: {len(uns)-len(got)} tren {uns[uns.inferred.isna()].ticker.nunique()} ma")
print("\n  Toan bo ca suy duoc, lon nhat truoc:")
for _,x in got.reindex(got.inferred.abs().sort_values(ascending=False).index).head(12).iterrows():
    print(f"    {x.ticker:<5} {x.public_date.date()} {x.action_type:<9} {int(x.inferred):>10,}  {x.why}")
out.to_csv(f"{D}/final_inferred_patched.csv",index=False); got.to_csv(f"{D}/resolved_patched.csv",index=False)
uns[uns.inferred.isna()].sort_values(["tier","ticker","public_date"]).to_csv(f"{D}/still_unsized_patched.csv",index=False)
