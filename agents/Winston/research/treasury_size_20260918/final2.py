"""CHOT v2 — sua loi nghiem trong cua v1:
ISS (11.747 dong) va DIV (17.189) co shares_delta NULL 100% => bo loc confounder cua v1 MU
truoc moi dot phat hanh/co tuc CP. Hau qua do duoc: VPB 2023 gan 1,19 ty CP phat hanh rieng le
cho SMBC bi quy nham thanh 'ban CP quy'.
v2: BAT KY dong corporate_action nao co event_code lam doi so luong CP (ISS/DIV/AIS/MA) roi vao
cua so -> TU CHOI, khong tru du. Phat hien qua BAT KY cot ngay nao cua dong do."""
import pandas as pd, numpy as np, os
D=os.path.dirname(os.path.abspath(__file__))
ev  = pd.read_csv(f"{D}/events.csv", parse_dates=["public_date"])
fin = pd.read_csv(f"{D}/fin.csv",    parse_dates=["time"])
ca  = pd.read_csv(f"{D}/ca.csv",     parse_dates=["effective_date","record_date","issue_date"])
fin = fin.dropna(subset=["OShares"]); fin=fin[fin.OShares>0].sort_values(["ticker","time"])
SHARE_CODES={"ISS","DIV","AIS","MA"}
cac = ca[ca.event_code.isin(SHARE_CODES)].copy()
fin_by_t={t:g for t,g in fin.groupby("ticker")}
ca_by_t ={t:g for t,g in cac.groupby("ticker")}
ev_by_t ={t:g for t,g in ev.groupby("ticker")}
SIGN={"buy_done":-1,"sell_done":+1}; MAX_EXTRA=1

def ca_in(t,lo,hi):
    g=ca_by_t.get(t)
    if g is None: return 0
    m=False
    for c in ("effective_date","record_date","issue_date"):
        m = m | ((g[c]>lo)&(g[c]<=hi))
    return int(m.sum())

def infer(row):
    t,d,at=row.ticker,row.public_date,row.action_type
    g=fin_by_t.get(t)
    if g is None or len(g)<2: return None,"NO_DATA",""
    before,after=g[g.time<d],g[g.time>=d]
    if before.empty or after.empty: return None,"NO_DATA",""
    b=before.iloc[-1]
    for k in range(min(MAX_EXTRA+1,len(after))):
        a=after.iloc[k]; lo,hi=b.time,a.time
        ge=ev_by_t[t]
        if len(ge[(ge.public_date>lo)&(ge.public_date<=hi)])>1: return None,"MULTI_EVENT",f"{lo.date()}..{hi.date()}"
        dd=a.OShares-b.OShares
        if dd==0: continue
        n=ca_in(t,lo,hi)
        if n>0: return None,"CA_CONFOUNDED",f"{n} su kien ISS/DIV/AIS/MA trong {lo.date()}..{hi.date()}"
        if np.sign(dd)!=SIGN[at]: return None,"SIGN_MISMATCH",f"dOSh={int(dd):,}"
        if abs(dd)/b.OShares>0.25: return None,"IMPLAUSIBLE",f"{abs(dd)/b.OShares:.1%}"
        return int(abs(dd))*SIGN[at],"HIGH",f"dOSh={int(dd):,} ({abs(dd)/b.OShares:.2%}) q{lo.date()}..{hi.date()}"
    return None,"NO_MOVE","OShares bat dong qua 2 quy ke tiep"

r=ev.apply(lambda x: pd.Series(infer(x),index=["inferred","tier","why"]),axis=1)
out=pd.concat([ev,r],axis=1); out["is_unsized"]=out.shares_delta.isna()
ctl=out[~out.is_unsized].copy(); ctl["truth"]=ctl.shares_delta.abs()*ctl.action_type.map(SIGN)
hit=ctl[ctl.inferred.notna()].copy(); hit["err"]=(hit.inferred-hit.truth).abs()/hit.truth.abs()
print("="*74); print("CONTROL (131 su kien DA BIET co) — v2 nghiem ngat"); print("="*74)
print(f"  suy duoc {len(hit)}/131 | khop CHINH XAC {(hit.err<=0).sum()} ({(hit.err<=0).mean():.1%})"
      f" | sai<=5% {(hit.err<=.05).sum()} ({(hit.err<=.05).mean():.1%})")
print("  ca truot:")
for _,x in hit[hit.err>0.05].iterrows():
    print(f"    {x.ticker:<5} {x.public_date.date()} {x.action_type:<9} that={int(x.truth):>10,} suy={int(x.inferred):>10,} sai={x.err:.1%}")
uns=out[out.is_unsized]
print("\n"+"="*74); print(f"NHOM THIEU CO (n={len(uns)})"); print("="*74)
for k,v in uns.tier.value_counts().items(): print(f"  {k:<15}{v:>4} ({v/len(uns):5.1%})")
got=uns[uns.inferred.notna()]
print(f"\n  SUY DUOC: {len(got)}/{len(uns)} ({len(got)/len(uns):.1%}) tren {got.ticker.nunique()} ma")
print(f"  KHONG CO DU LIEU: {len(uns)-len(got)} tren {uns[uns.inferred.isna()].ticker.nunique()} ma")
print("\n  8 ca suy duoc lon nhat (kiem mat thuong):")
for _,x in got.reindex(got.inferred.abs().sort_values(ascending=False).index).head(8).iterrows():
    print(f"    {x.ticker:<5} {x.public_date.date()} {x.action_type:<9} {int(x.inferred):>11,}  {x.why}")
out.to_csv(f"{D}/final_inferred.csv",index=False); got.to_csv(f"{D}/resolved.csv",index=False)
uns[uns.inferred.isna()].sort_values(["tier","ticker","public_date"]).to_csv(f"{D}/still_unsized.csv",index=False)
print(f"\n  artifact: resolved.csv({len(got)}) still_unsized.csv({len(uns)-len(got)}) final_inferred.csv(577)")
