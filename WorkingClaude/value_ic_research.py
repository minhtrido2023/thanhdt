# -*- coding: utf-8 -*-
"""
value_ic_research.py  (Stage 1 of 8L valuation v3)
===================================================
IC-test the candidate valuation lenses on data/value_panel_2014.csv → a DECISION TABLE
(component × universe/route → IC / t / hit% / coverage), + orthogonality + by-year.
Drives the data-driven weights of Composite v3. Read-only research (no writes to prod).

Factors (higher = cheaper/more attractive), negative-safe (PE/PCF/PS≤0 → NaN = no signal):
  F_ey        = 100/PE                      cross-sectional earnings yield (incumbent absolute)
  F_pez       = -(PE-PE_MA5Y)/PE_SD5Y       PE cheap-vs-own-5Y (plain own-history)
  F_eyspread_z= z(100/PE - refi vs own hist) USER's deposit-anchor idea (rate-adjusted own-history)
  F_cfy       = 100/PCF                      cashflow yield (dcf_ic_test said STRONGEST)
  F_cfynorm   = cycle-normalized 1/PCF       cfo_normy (current ±0.08 confirm)
  F_pbz       = -pb_z                        incumbent relative (linear)
  F_golden    = 1[pb_z<=-1]                  non-linear golden-cell flag
  F_ps        = 100/PS                       sales yield (for RETAIL/CONSUMER)
"""
import os, numpy as np, pandas as pd
from scipy.stats import spearmanr
WORKDIR = os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude")
df = pd.read_csv(f"{WORKDIR}/data/value_panel_2014.csv", parse_dates=["time"])
MOAT = pd.read_csv(f"{WORKDIR}/data/moat_tags.csv")
MOAT36 = set(MOAT[MOAT.moat_tier.isin(["WIDE","NARROW"])].ticker)

# ---- factors ----
df["F_ey"]  = np.where(df.PE  > 0, 100.0/df.PE,  np.nan)
df["F_cfy"] = np.where(df.PCF > 0, 100.0/df.PCF, np.nan)
df["F_ps"]  = np.where(df.PS  > 0, 100.0/df.PS,  np.nan)
df["F_pez"] = -((df.PE - df.PE_MA5Y) / df.PE_SD5Y.replace(0, np.nan))
df["F_pbz"] = -df.pb_z
df["F_golden"] = np.where(df.pb_z.notna(), (df.pb_z <= -1).astype(float), np.nan)
_ttm = df[["CF_OA_P0","CF_OA_P1","CF_OA_P2","CF_OA_P3"]].sum(axis=1, min_count=1)
df["F_cfynorm"] = np.where((df.PCF>0)&(_ttm>0)&(df.CF_OA_3Y>0),
                           (100.0/df.PCF)*np.clip((df.CF_OA_3Y/3.0)/_ttm, 0.3, 3.0), np.nan)
# deposit-anchor: earnings-yield spread vs refi, z-scored vs the name's OWN trailing history
df = df.sort_values(["ticker","time"])
df["_spread"] = df.F_ey - df.refi_rate            # both in % units
g = df.groupby("ticker")["_spread"]
_m = g.transform(lambda s: s.rolling(60, min_periods=24).mean())
_sd = g.transform(lambda s: s.rolling(60, min_periods=24).std())
df["F_eyspread_z"] = ((df._spread - _m) / _sd.replace(0, np.nan))

FACTORS = ["F_ey","F_pez","F_eyspread_z","F_cfy","F_cfynorm","F_pbz","F_golden","F_ps"]
FWDS = ["profit_1M","profit_2M","profit_3M"]

def xs_ic(d, fac, fwd, minn=8):
    ics=[]
    for _,gm in d.groupby(d.time):
        s = gm[[fac,fwd]].dropna()
        if len(s) >= minn and s[fac].nunique()>2:
            ics.append(spearmanr(s[fac], s[fwd]).correlation)
    ics=[x for x in ics if pd.notna(x)]
    if len(ics)<6: return None
    a=np.array(ics); t=a.mean()/(a.std(ddof=1)/np.sqrt(len(a))) if a.std()>0 else 0
    return dict(IC=a.mean(), t=t, hit=(a>0).mean(), nm=len(a))

def cov(d, fac): return 100*d[fac].notna().mean()

def table(d, label, fwd="profit_2M"):
    print(f"\n=== {label}  (n_rows={len(d)}, fwd={fwd}) ===")
    print(f"  {'factor':<14}{'IC':>8}{'t':>7}{'hit%':>6}{'cov%':>6}{'mo':>5}")
    for f in FACTORS:
        r = xs_ic(d, f, fwd)
        if r: print(f"  {f:<14}{r['IC']:>+8.3f}{r['t']:>7.1f}{100*r['hit']:>6.0f}{cov(d,f):>6.0f}{r['nm']:>5}")
        else: print(f"  {f:<14}{'(insufficient)':>30}")

def orth(d, fac, base, fwd="profit_2M"):
    """marginal IC of `fac` residualized on `base` (rank space), per month."""
    res=[]; pr=[]
    for _,gm in d.groupby(d.time):
        s=gm[[fac,base,fwd]].dropna()
        if len(s)<10: continue
        rf=s[fac].rank(); rb=s[base].rank()
        b=np.polyfit(rb, rf, 1); resid=rf-(b[0]*rb+b[1])
        res.append(spearmanr(resid, s[fwd]).correlation)
        pr.append(spearmanr(s[base], s[fwd]).correlation)
    res=[x for x in res if pd.notna(x)]; pr=[x for x in pr if pd.notna(x)]
    if len(res)<6: return
    ra=np.array(res); pa=np.array(pr)
    print(f"  {fac:<13}⟂{base:<13} base-IC {pa.mean():+.3f} | resid-IC {ra.mean():+.3f} (t={ra.mean()/(ra.std(ddof=1)/np.sqrt(len(ra))):.1f})")

def by_year(d, fac, fwd="profit_2M"):
    print(f"  by-year {fac} ({fwd}):", end=" ")
    for y,gy in d.groupby(d.time.dt.year):
        r=xs_ic(gy, fac, fwd, minn=8)
        print(f"{y}:{r['IC']:+.02f}" if r else f"{y}:--", end="  ")
    print()

LIQ=5e9
broad = df[df.turnover>=LIQ].copy()
moat  = broad[broad.ticker.isin(MOAT36)].copy()
# consumer/retail proxy via ICB (food/bev/personal/household 35xx-37xx, retail 53xx)
icb=df.ICB_Code
cons = broad[broad.ICB_Code.apply(lambda c: pd.notna(c) and (3500<=c<3800 or 5300<=c<5400))].copy()

for fwd in FWDS:
    table(broad, f"BROAD (turnover>={LIQ:.0e})", fwd)
table(moat, "MOAT-36 (WIDE+NARROW)")
for rt in ["COMPOUNDER","CYCLICAL","BANK","SECURITIES","REALESTATE","POWER"]:
    table(broad[broad.route==rt], f"ROUTE={rt}")
table(cons, "CONSUMER/RETAIL proxy (ICB 35xx-37xx,53xx)")

print("\n### ORTHOGONALITY (profit_2M, BROAD) ###")
for fac in ["F_cfy","F_cfynorm","F_eyspread_z","F_pez"]:
    orth(broad, fac, "F_ey")
orth(broad, "F_cfy", "F_pbz"); orth(broad, "F_eyspread_z", "F_pez")

print("\n### BY-YEAR robustness (profit_2M) ###")
for fac in ["F_cfy","F_ey","F_eyspread_z","F_pez","F_pbz","F_golden"]:
    by_year(broad, fac)
print("\n[done]")
