"""Find a MORE STABLE yield metric than trailing 1/PCF (user critique 2026-06-16: CFO not always
positive over 4Q, sign-unstable, cycle-distorted, only ~67% populated). Compare candidates on BOTH
predictive IC AND signal stability (populated %, by-year consistency, month-over-month rank persistence).

  F_cfy   = 1/PCF                         trailing CFO yield (baseline NOISY)
  F_evebY = 1/EVEB                         EBITDA/EV yield (stable: EBITDA no working-cap swings, rarely <0)
  F_ey    = 1/PE                           earnings yield (more populated, mildly cyclical)
  F_dy    = DY                             dividend yield (very stable cash-return)
  F_ncfy  = (1/PCF)*(CF_OA_5Y/5)/ttm_CFO   CYCLE-NORMALIZED cashflow yield (rescale current CFO to its 5Y norm)
  F_pbz   = -pb_z                          incumbent (PB vs own history)
"""
import numpy as np, pandas as pd

def spear(a, b):
    ra, rb = pd.Series(np.asarray(a, float)).rank(), pd.Series(np.asarray(b, float)).rank()
    if ra.nunique() < 2 or rb.nunique() < 2: return np.nan
    return float(np.corrcoef(ra, rb)[0, 1])

WD = "/home/trido/thanhdt/WorkingClaude"
df = pd.read_csv(f"{WD}/data/stable_yield_panel.csv", parse_dates=["time"])
df["ym"] = df.time.values.astype("datetime64[M]"); df["year"] = df.time.dt.year
df["pb_z"] = (df.PB - df.PB_MA5Y) / df.PB_SD5Y.replace(0, np.nan)
ttm = df[["CF_OA_P0","CF_OA_P1","CF_OA_P2","CF_OA_P3"]].sum(axis=1, min_count=1)
norm = df.CF_OA_5Y/5.0
df["F_cfy"]   = np.where(df.PCF > 0, 1.0/df.PCF, np.nan)
df["F_evebY"] = np.where(df.EVEB > 0, 1.0/df.EVEB, np.nan)
df["F_ey"]    = np.where(df.PE > 0, 1.0/df.PE, np.nan)
df["F_dy"]    = df.DY
df["F_ncfy"]  = df["F_cfy"] * np.clip(np.where((ttm > 0) & (norm > 0), norm/ttm, np.nan), 0.3, 3.0)
df["F_pbz"]   = -df.pb_z
FACS = ["F_cfy","F_evebY","F_ey","F_dy","F_ncfy","F_pbz"]

# custom30 PIT flag
mem = pd.read_csv(f"{WD}/data/custom30_membership.csv", parse_dates=["effective_from","effective_to"])
mem["effective_to"] = mem.effective_to.fillna(pd.Timestamp("2100-01-01"))
iv = {tk: list(zip(g.effective_from.values, g.effective_to.values)) for tk, g in mem.groupby("ticker")}
df["cust30"] = df.apply(lambda r: any(f <= np.datetime64(r.time) < t for f,t in iv.get(r.ticker, [])), axis=1)

def xs_ic(d, fac, fwd="profit_2M"):
    out = []
    for ym, g in d.groupby("ym"):
        s = g[[fac, fwd]].dropna()
        if len(s) >= 5 and s[fac].nunique() > 2:
            ic = spear(s[fac], s[fwd])
            if np.isfinite(ic): out.append((ym, ic))
    return pd.DataFrame(out, columns=["ym","ic"])

def persistence(d, fac):
    """avg month-over-month cross-sectional Spearman corr of the factor itself (signal stability)."""
    piv = d.pivot_table(index="ym", columns="ticker", values=fac)
    cs = []
    yms = list(piv.index)
    for i in range(1, len(yms)):
        a, b = piv.loc[yms[i-1]], piv.loc[yms[i]]
        m = a.notna() & b.notna()
        if m.sum() >= 8:
            c = spear(a[m], b[m])
            if np.isfinite(c): cs.append(c)
    return np.mean(cs) if cs else np.nan

def report(d, label):
    print(f"\n{'='*86}\n{label}  (rows={len(d)}, names={d.ticker.nunique()})")
    print(f"{'factor':8} | {'pop%':>5} | {'IC':>7} {'IR(t)':>6} | {'yrs+':>5} | {'persist':>7}  (signal stability)")
    print("-"*86)
    npop = len(d.dropna(subset=["profit_2M"]))
    for fac in FACS:
        ics = xs_ic(d, fac)
        ic_m = ics.ic.mean() if len(ics) else np.nan
        ir = ic_m/ics.ic.std()*np.sqrt(len(ics)) if len(ics) and ics.ic.std() > 0 else np.nan
        # by-year sign
        ics["yr"] = ics.ym.dt.year
        yr = ics.groupby("yr").ic.mean()
        yrs_pos = f"{(yr>0).sum()}/{len(yr)}"
        pop = d[fac].notna().sum()/len(d)*100
        per = persistence(d, fac)
        print(f"{fac:8} | {pop:>4.0f}% | {ic_m:+.3f} {ir:>6.1f} | {yrs_pos:>5} | {per:>7.2f}")

broad = df[df.turnover >= 5e9].copy()
report(broad, "BROAD (turnover>=5bn)")
report(df[df.cust30].copy(), "CUSTOM30 (PIT membership)")
