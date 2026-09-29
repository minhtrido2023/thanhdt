"""Cau hinh CHOT: chi nhan khi KHONG co corporate_action lam doi so CP trong cua so
(tang MEDIUM do duoc 0/4 dung -> loai han), cua so noi rong toi da +1 quy."""
import pandas as pd, numpy as np, os
D = os.path.dirname(os.path.abspath(__file__))
ev  = pd.read_csv(f"{D}/events.csv", parse_dates=["public_date"])
fin = pd.read_csv(f"{D}/fin.csv",    parse_dates=["time"])
ca  = pd.read_csv(f"{D}/ca.csv",     parse_dates=["effective_date","record_date","issue_date"])
fin = fin.dropna(subset=["OShares"]); fin = fin[fin.OShares>0].sort_values(["ticker","time"])
ca_sh = ca[ca.shares_delta.notna() & (ca.shares_delta!=0)].copy()
ca_sh["ca_date"] = ca_sh.effective_date.fillna(ca_sh.record_date).fillna(ca_sh.issue_date)
ca_sh = ca_sh.dropna(subset=["ca_date"])
fin_by_t={t:g for t,g in fin.groupby("ticker")}
ca_by_t ={t:g for t,g in ca_sh.groupby("ticker")}
ev_by_t ={t:g for t,g in ev.groupby("ticker")}
SIGN={"buy_done":-1,"sell_done":+1}
MAX_EXTRA=1

def infer(row):
    t,d,at = row.ticker,row.public_date,row.action_type
    g = fin_by_t.get(t)
    if g is None or len(g)<2: return None,"NO_DATA",""
    before,after = g[g.time<d], g[g.time>=d]
    if before.empty or after.empty: return None,"NO_DATA",""
    b = before.iloc[-1]; last="" ; flat=True
    for k in range(min(MAX_EXTRA+1,len(after))):
        a = after.iloc[k]; lo,hi=b.time,a.time
        ge = ev_by_t[t]
        if len(ge[(ge.public_date>lo)&(ge.public_date<=hi)])>1:
            return None,"MULTI_EVENT",f"{lo.date()}..{hi.date()}"
        cg = ca_by_t.get(t)
        n_ca = 0 if cg is None else len(cg[(cg.ca_date>lo)&(cg.ca_date<=hi)])
        dd = a.OShares-b.OShares
        if dd==0: continue
        flat=False
        if n_ca>0: return None,"CA_CONFOUNDED",f"{n_ca} CA doi so CP trong cua so"
        if np.sign(dd)!=SIGN[at]: return None,"SIGN_MISMATCH",f"dOSh={int(dd):,}"
        if abs(dd)/b.OShares>0.25: return None,"IMPLAUSIBLE",f"{abs(dd)/b.OShares:.1%} OShares"
        return int(abs(dd))*SIGN[at],"HIGH",f"dOSh={int(dd):,} ({abs(dd)/b.OShares:.2%}) q{lo.date()}..{hi.date()}"
    return None,"NO_MOVE","OShares bat dong qua 2 quy ke tiep"

r = ev.apply(lambda x: pd.Series(infer(x), index=["inferred","tier","why"]), axis=1)
out = pd.concat([ev,r],axis=1); out["is_unsized"]=out.shares_delta.isna()

ctl = out[~out.is_unsized].copy()
ctl["truth"]=ctl.shares_delta.abs()*ctl.action_type.map(SIGN)
hit = ctl[ctl.inferred.notna()].copy()
hit["err"]=(hit.inferred-hit.truth).abs()/hit.truth.abs()
print("="*76); print("CONTROL (131 su kien da biet co) — cau hinh CHOT")
print("="*76)
print(f"  suy duoc {len(hit)}/131   khop CHINH XAC {(hit.err<=0).sum()} ({(hit.err<=0).mean():.1%})"
      f"   sai<=5% {(hit.err<=.05).sum()} ({(hit.err<=.05).mean():.1%})"
      f"   sai<=20% {(hit.err<=.20).sum()} ({(hit.err<=.20).mean():.1%})")
print("  ca truot:")
for _,x in hit[hit.err>0.05].iterrows():
    print(f"    {x.ticker:<5} {x.public_date.date()} {x.action_type:<9} that={int(x.truth):>11,} suy={int(x.inferred):>11,} sai={x.err:.1%}")

uns = out[out.is_unsized]
print("\n"+"="*76); print(f"NHOM THIEU CO (n={len(uns)})"); print("="*76)
for k,v in uns.tier.value_counts().items(): print(f"  {k:<15}{v:>4}  ({v/len(uns):5.1%})")
got = uns[uns.inferred.notna()]
print(f"\n  SUY DUOC SO: {len(got)}/{len(uns)} ({len(got)/len(uns):.1%})  — tier HIGH, do chinh xac do o control ben tren")
print(f"  KHONG co du lieu: {len(uns)-len(got)}")
print(f"  So mã liên quan: suy duoc {got.ticker.nunique()} ma | con thieu {uns[uns.inferred.isna()].ticker.nunique()} ma")
out.to_csv(f"{D}/final_inferred.csv",index=False)
got.to_csv(f"{D}/resolved.csv",index=False)
uns[uns.inferred.isna()].sort_values(["tier","ticker","public_date"]).to_csv(f"{D}/still_unsized.csv",index=False)
print("\n  10 ca suy duoc lon nhat:")
for _,x in got.reindex(got.inferred.abs().sort_values(ascending=False).index).head(10).iterrows():
    print(f"    {x.ticker:<5} {x.public_date.date()} {x.action_type:<9} suy={int(x.inferred):>12,}  {x.why}")
