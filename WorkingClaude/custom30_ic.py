"""(a) CFO-yield IC test restricted to REAL custom30 PIT membership (tav2_bq.custom30_8l).

For each monthly panel date, keep only names that were active custom30 members as-of that
date (effective_from <= date < effective_to), then compute the same cross-sectional Spearman
IC. This tests whether a CFO-yield tilt adds reliable selection IC WITHIN the actual parking
basket the engine holds -- not a static moat list.
"""
import numpy as np, pandas as pd

def spearmanr(a, b):
    ra, rb = pd.Series(a, dtype=float).rank(), pd.Series(b, dtype=float).rank()
    if ra.nunique() < 2 or rb.nunique() < 2:
        return np.nan
    return float(np.corrcoef(ra, rb)[0, 1])

WD = "/home/trido/thanhdt/WorkingClaude"
df = pd.read_csv(f"{WD}/data/dcf_ic_panel.csv", parse_dates=["time"])
df["ym"] = df.time.values.astype("datetime64[M]"); df["year"] = df.time.dt.year
df["pb_z"] = (df.PB - df.PB_MA5Y) / df.PB_SD5Y.replace(0, np.nan)
df["F_cfy"] = np.where(df.PCF > 0, 1.0/df.PCF, np.nan)
df["F_ey"]  = np.where(df.PE  > 0, 1.0/df.PE,  np.nan)
df["F_dcf"] = df["F_cfy"] + df.ROIC_Trailing
df["F_pbz"] = -df.pb_z

# PIT membership: build interval list, mark each panel row
mem = pd.read_csv(f"{WD}/data/custom30_membership.csv", parse_dates=["effective_from", "effective_to"])
mem["effective_to"] = mem.effective_to.fillna(pd.Timestamp("2100-01-01"))
intervals = {}
for tk, g in mem.groupby("ticker"):
    intervals[tk] = list(zip(g.effective_from.values, g.effective_to.values))

def is_member(row):
    iv = intervals.get(row.ticker)
    if not iv:
        return False
    t = np.datetime64(row.time)
    return any(f <= t < to for f, to in iv)

df["cust30"] = df.apply(is_member, axis=1)
cust = df[df.cust30].copy()

FACTORS = ["F_cfy", "F_ey", "F_dcf", "F_pbz"]
FWDS = ["profit_1M", "profit_2M", "profit_3M"]

def xs_ic(d, fac, fwd):
    out = []
    for ym, g in d.groupby("ym"):
        s = g[[fac, fwd]].dropna()
        if len(s) >= 5 and s[fac].nunique() > 2:
            ic = spearmanr(s[fac], s[fwd])
            if np.isfinite(ic): out.append(ic)
    return np.array(out)

def summ(ics):
    if len(ics) == 0: return (np.nan, np.nan, np.nan, 0)
    t = ics.mean()/ics.std()*np.sqrt(len(ics)) if ics.std() > 0 else np.nan
    return (ics.mean(), t, (ics > 0).mean(), len(ics))

print(f"custom30 PIT panel: rows={len(cust)} names={cust.ticker.nunique()} "
      f"months={cust.ym.nunique()} avg_names/mo={cust.groupby('ym').size().mean():.1f}")
print(f"\n{'factor':8} | " + " | ".join(f"{fw:>20}" for fw in FWDS))
print(f"{'':8} | " + " | ".join(f"{'IC':>6} {'t':>5} {'hit':>4} {'n':>3}" for _ in FWDS))
print("-"*72)
for fac in FACTORS:
    cells = []
    for fwd in FWDS:
        ic, t, hit, n = summ(xs_ic(cust, fac, fwd))
        cells.append(f"{ic:+.3f} {t:>5.1f} {hit*100:>3.0f}% {n:>3}")
    print(f"{fac:8} | " + " | ".join(cells))

# orthogonality of F_cfy vs incumbent F_pbz on custom30
pooled = cust[["F_cfy", "F_pbz"]].dropna()
print(f"\npooled corr(F_cfy, F_pbz) = {spearmanr(pooled.F_cfy, pooled.F_pbz):+.3f}")
res, comb, pbz = [], [], []
for ym, g in cust.groupby("ym"):
    s = g[["F_cfy", "F_pbz", "profit_2M"]].dropna()
    if len(s) < 6: continue
    rd, rp, rf = s.F_cfy.rank(), s.F_pbz.rank(), s.profit_2M
    b = np.polyfit(rp, rd, 1); resid = rd - (b[0]*rp + b[1])
    if resid.nunique() > 2: res.append(spearmanr(resid, rf))
    comb.append(spearmanr((rd+rp)/2, rf)); pbz.append(spearmanr(rp, rf))
print(f"IC F_pbz alone           : {summ(np.array(pbz))[0]:+.3f} (t={summ(np.array(pbz))[1]:.1f})")
print(f"IC F_cfy residual ⟂ pbz  : {summ(np.array(res))[0]:+.3f} (t={summ(np.array(res))[1]:.1f})  <- orthogonal add")
print(f"IC composite cfy+pbz     : {summ(np.array(comb))[0]:+.3f} (t={summ(np.array(comb))[1]:.1f})")

print(f"\n--- by-year IC: F_cfy vs profit_2M (custom30) ---")
for y in range(2014, 2026):
    ic, t, hit, n = summ(xs_ic(cust[cust.year == y], "F_cfy", "profit_2M"))
    bar = "#"*int(abs(ic)*100) if np.isfinite(ic) else ""
    print(f"  {y}: IC={ic:+.3f} n={n:>2} {'+' if (ic or 0)>=0 else '-'}{bar}")
