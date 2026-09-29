"""2 chan doan: (a) NO_MOVE co nghia la co=0 khong? (b) noi rong cua so 1 quy co cuu duoc khong?"""
import pandas as pd, numpy as np, os
D = os.path.dirname(os.path.abspath(__file__))
ev = pd.read_csv(f"{D}/events.csv", parse_dates=["public_date"])
fin = pd.read_csv(f"{D}/fin.csv", parse_dates=["time"])
inf = pd.read_csv(f"{D}/inferred.csv", parse_dates=["public_date"])
fin = fin.dropna(subset=["OShares"]); fin = fin[fin.OShares>0].sort_values(["ticker","time"])
fin_by_t = {t:g for t,g in fin.groupby("ticker")}
ev_by_t  = {t:g for t,g in ev.groupby("ticker")}
SIGN={"buy_done":-1,"sell_done":+1}

print("="*78); print("(a) NO_MOVE co dong nghia 'co = 0' khong? — do tren nhom DA BIET co")
print("="*78)
nm = inf[(inf.tier=="NO_MOVE") & inf.shares_delta.notna()]
print(f"n={len(nm)} su kien co co THAT > 0 ma OShares KHONG he nhuc nhich")
if len(nm):
    s = nm.shares_delta.abs()
    print(f"  co that: p50={s.median():,.0f}  p90={s.quantile(.9):,.0f}  max={s.max():,.0f}")
    print(f"  so ca co that >= 1 trieu CP: {(s>=1e6).sum()}/{len(nm)}")
    print("  vi du lon nhat:")
    for _,r in nm.nlargest(4,"shares_delta").iterrows():
        print(f"    {r.ticker:<5} {r.public_date.date()} {r.action_type:<9} co that={int(r.shares_delta):>12,}")

print("\n"+"="*78); print("(b) Noi rong: neu quy ke tiep bat dong, nhin them 1 quy — con dung khong?")
print("="*78)
def infer_wide(row, extra):
    t,d,at = row.ticker,row.public_date,row.action_type
    g = fin_by_t.get(t)
    if g is None or len(g)<2: return None
    before, after = g[g.time<d], g[g.time>=d]
    if before.empty or len(after)<1: return None
    b = before.iloc[-1]
    for k in range(min(extra+1, len(after))):
        a = after.iloc[k]
        ge = ev_by_t[t]
        if len(ge[(ge.public_date>b.time)&(ge.public_date<=a.time)])>1: return None
        dd = a.OShares - b.OShares
        if dd!=0:
            if np.sign(dd)!=SIGN[at]: return None
            if abs(dd)/b.OShares>0.25: return None
            return int(abs(dd))*SIGN[at]
    return None

ctl = inf[inf.shares_delta.notna()].copy()
ctl["truth"] = ctl.shares_delta.abs()*ctl.action_type.map(SIGN)
for extra in [0,1,2]:
    ctl["w"] = ctl.apply(lambda r: infer_wide(r, extra), axis=1)
    c = ctl[ctl.w.notna()]
    err = (c.w-c.truth).abs()/c.truth.abs()
    print(f"  +{extra} quy: suy duoc {len(c):>3}/{len(ctl)}  |  khop chinh xac {(err<=0).sum():>3} "
          f"({(err<=0).mean():5.1%})  sai<=5% {(err<=0.05).sum():>3} ({(err<=0.05).mean():5.1%})")
