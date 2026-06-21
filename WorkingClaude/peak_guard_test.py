"""Validate the user's intuition: high CFO-yield is good EXCEPT at cashflow/cycle peaks (value trap).
Test (Q1) whether the cf_peak guard cleans the signal:
  - IC of 1/PCF on NON-peak vs PEAK subset
  - forward return of TOP-yield names split by peak flag (is high-yield+peak a trap?)
cf_peak = trailing TTM CFO/assets >= 1.5x its own 5Y norm (same def as rating_8l.py).
"""
import numpy as np, pandas as pd

def spear(a, b):
    ra, rb = pd.Series(np.asarray(a, float)).rank(), pd.Series(np.asarray(b, float)).rank()
    if ra.nunique() < 2 or rb.nunique() < 2: return np.nan
    return float(np.corrcoef(ra, rb)[0, 1])

WD = "/home/trido/thanhdt/WorkingClaude"
df = pd.read_csv(f"{WD}/data/dcf_ic_panel2.csv", parse_dates=["time"])
df["ym"] = df.time.values.astype("datetime64[M]"); df["year"] = df.time.dt.year
df["F_cfy"] = np.where(df.PCF > 0, 1.0/df.PCF, np.nan)
ttm = df[["CF_OA_P0","CF_OA_P1","CF_OA_P2","CF_OA_P3"]].sum(axis=1, min_count=1)
norm = df["CF_OA_5Y"]/5.0
df["cf_peak"] = (ttm > 0) & (norm > 0) & (ttm >= 1.5*norm)

# custom30 PIT flag
mem = pd.read_csv(f"{WD}/data/custom30_membership.csv", parse_dates=["effective_from","effective_to"])
mem["effective_to"] = mem.effective_to.fillna(pd.Timestamp("2100-01-01"))
iv = {tk: list(zip(g.effective_from.values, g.effective_to.values)) for tk, g in mem.groupby("ticker")}
df["cust30"] = df.apply(lambda r: any(f <= np.datetime64(r.time) < t for f,t in iv.get(r.ticker, [])), axis=1)

def ic_split(d, fwd="profit_2M", label=""):
    def mean_ic(sub):
        ics = []
        for ym, g in sub.groupby("ym"):
            s = g[["F_cfy", fwd]].dropna()
            if len(s) >= 5 and s.F_cfy.nunique() > 2:
                ic = spear(s.F_cfy, s[fwd])
                if np.isfinite(ic): ics.append(ic)
        ics = np.array(ics)
        t = ics.mean()/ics.std()*np.sqrt(len(ics)) if len(ics) and ics.std()>0 else np.nan
        return ics.mean() if len(ics) else np.nan, t, len(ics)
    npk = mean_ic(d[~d.cf_peak]); pk = mean_ic(d[d.cf_peak])
    print(f"\n[{label}] IC(1/PCF vs {fwd})  by cashflow-peak split:")
    print(f"  NON-peak : IC={npk[0]:+.3f} (t={npk[1]:.1f}, n={npk[2]})")
    print(f"  PEAK     : IC={pk[0]:+.3f} (t={pk[1]:.1f}, n={pk[2]})")
    # share peak
    print(f"  share cf_peak rows: {d.cf_peak.mean()*100:.1f}%")

def topyield_trap(d, fwd="profit_2M", label=""):
    """Forward return of TOP-tercile CFO-yield names, split by peak. If high-yield+peak << high-yield+nonpeak => trap."""
    rows = []
    for ym, g in d.groupby("ym"):
        s = g[["F_cfy", "cf_peak", fwd]].dropna()
        if len(s) < 10: continue
        thr = s.F_cfy.quantile(2/3)
        hi = s[s.F_cfy >= thr]
        for pk in [False, True]:
            sub = hi[hi.cf_peak == pk]
            if len(sub): rows.append((pk, sub[fwd].mean()))
    r = pd.DataFrame(rows, columns=["peak", "fwd"])
    g = r.groupby("peak").fwd.agg(["mean", "count"])
    print(f"\n[{label}] forward {fwd} of TOP-tercile CFO-yield names, by peak:")
    for pk in [False, True]:
        if pk in g.index:
            print(f"  {'PEAK    ' if pk else 'NON-peak'}: mean fwd={g.loc[pk,'mean']:+.2f}%  (n_months={int(g.loc[pk,'count'])})")
    if False in g.index and True in g.index:
        print(f"  => trap gap (nonpeak - peak) = {g.loc[False,'mean']-g.loc[True,'mean']:+.2f}pp")

broad = df[df.turnover >= 5e9].copy()
ic_split(broad, label="BROAD")
topyield_trap(broad, label="BROAD")
cust = df[df.cust30].copy()
ic_split(cust, label="CUSTOM30")
topyield_trap(cust, label="CUSTOM30")
