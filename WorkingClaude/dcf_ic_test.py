"""
Reverse-DCF valuation factor — IC test vs incumbent pb_z on the 8L quality baskets.

Question: does an ABSOLUTE (DCF-flavored) valuation signal add reliable, ORTHOGONAL
cross-sectional IC beyond the incumbent relative signal pb_z (PB vs own 5Y history)?

Key robustness note: a 2-stage Gordon reverse-DCF gives g_implied = r - cashflow_yield,
so the undervaluation margin = ROIC - (r - 1/PCF). r is an additive constant across names
on a given date => it does NOT change the cross-sectional RANK at all. So the reverse-DCF
rank-signal reduces to rank(1/PCF + ROIC_Trailing) -- cashflow yield + quality. WACC-fragility
is irrelevant for ranking. We test that, plus simpler baselines.

Factors (signed so HIGHER = more attractive => expect POSITIVE IC vs forward return):
  F_cfy  = 1/PCF                       (operating cashflow yield -- pure absolute cheapness)
  F_ey   = 1/PE                        (earnings yield)
  F_dcf  = 1/PCF + ROIC_Trailing       (reverse-DCF undervaluation margin, rank-equiv)
  F_pbz  = -pb_z                       (INCUMBENT: cheap vs own 5Y history)

IC = per-month cross-sectional Spearman corr(factor, fwd return), averaged over months.
t-stat = mean(IC)/std(IC)*sqrt(n_months). Marginal IC = IC of F_dcf after residualizing
out F_pbz each month (the orthogonal contribution -- the whole point of the test).
"""
import numpy as np, pandas as pd

def spearmanr(a, b):
    a = pd.Series(np.asarray(a, float)); b = pd.Series(np.asarray(b, float))
    ra, rb = a.rank(), b.rank()
    if ra.nunique() < 2 or rb.nunique() < 2:
        return (np.nan, None)
    return (float(np.corrcoef(ra, rb)[0, 1]), None)

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
MOAT = pd.read_csv(f"{WORKDIR}/data/moat_tags.csv")
WIDE   = set(MOAT[MOAT.moat_tier=="WIDE"].ticker)
NARROW = set(MOAT[MOAT.moat_tier=="NARROW"].ticker)
MOAT36 = WIDE | NARROW

df = pd.read_csv(f"{WORKDIR}/data/dcf_ic_panel.csv", parse_dates=["time"])
df["ym"]   = df.time.values.astype("datetime64[M]")
df["year"] = df.time.dt.year

# pb_z = (PB - PB_MA5Y)/PB_SD5Y  (replicates rating_8l.py)
df["pb_z"] = (df.PB - df.PB_MA5Y) / df.PB_SD5Y.replace(0, np.nan)

# factors (higher = more attractive)
df["F_cfy"] = np.where(df.PCF > 0, 1.0/df.PCF, np.nan)
df["F_ey"]  = np.where(df.PE  > 0, 1.0/df.PE,  np.nan)
df["F_dcf"] = df["F_cfy"] + df.ROIC_Trailing          # cashflow-yield + quality
df["F_pbz"] = -df.pb_z

FACTORS = ["F_cfy", "F_ey", "F_dcf", "F_pbz"]
FWDS    = ["profit_1M", "profit_2M", "profit_3M"]


def xs_ic(d, fac, fwd):
    """per-month cross-sectional Spearman IC list."""
    ics = []
    for ym, g in d.groupby("ym"):
        s = g[[fac, fwd]].dropna()
        if len(s) >= 5 and s[fac].nunique() > 2:
            ic, _ = spearmanr(s[fac], s[fwd])
            if np.isfinite(ic):
                ics.append(ic)
    return np.array(ics)


def summ(ics):
    if len(ics) == 0:
        return dict(IC=np.nan, t=np.nan, hit=np.nan, n=0)
    t = ics.mean()/ics.std()*np.sqrt(len(ics)) if ics.std() > 0 else np.nan
    return dict(IC=ics.mean(), t=t, hit=(ics > 0).mean(), n=len(ics))


def report(d, label):
    print(f"\n{'='*78}\n{label}   (rows={len(d)}, names={d.ticker.nunique()}, months={d.ym.nunique()})")
    print(f"{'factor':8} | " + " | ".join(f"{fw:>22}" for fw in FWDS))
    print(f"{'':8} | " + " | ".join(f"{'IC':>6} {'t':>5} {'hit%':>5} {'n':>3}" for _ in FWDS))
    print("-"*78)
    for fac in FACTORS:
        cells = []
        for fwd in FWDS:
            s = summ(xs_ic(d, fac, fwd))
            cells.append(f"{s['IC']:+.3f} {s['t']:>5.1f} {s['hit']*100:>4.0f}% {s['n']:>3}")
        print(f"{fac:8} | " + " | ".join(cells))


def orthogonality(d, fac="F_dcf", fwd="profit_2M"):
    """corr(fac, F_pbz) pooled, and marginal IC of fac residualized vs F_pbz per month."""
    pooled = d[[fac, "F_pbz"]].dropna()
    rho, _ = spearmanr(pooled[fac], pooled.F_pbz)
    # residualize fac on F_pbz each month (rank space), then IC of residual vs fwd
    res_ics, comb_ics, pbz_ics = [], [], []
    for ym, g in d.groupby("ym"):
        s = g[[fac, "F_pbz", fwd]].dropna()
        if len(s) < 6:
            continue
        rd = s[fac].rank(); rp = s.F_pbz.rank(); rf = s[fwd]
        # OLS residual of rd on rp
        b = np.polyfit(rp, rd, 1)
        resid = rd - (b[0]*rp + b[1])
        if resid.nunique() > 2:
            res_ics.append(spearmanr(resid, rf)[0])
        comb = (rd + rp)/2.0          # equal-weight composite
        comb_ics.append(spearmanr(comb, rf)[0])
        pbz_ics.append(spearmanr(rp, rf)[0])
    res_ics = np.array([x for x in res_ics if np.isfinite(x)])
    comb_ics = np.array([x for x in comb_ics if np.isfinite(x)])
    pbz_ics = np.array([x for x in pbz_ics if np.isfinite(x)])
    print(f"\n--- orthogonality / marginal value: {fac} vs incumbent F_pbz ({fwd}) ---")
    print(f"  pooled Spearman corr({fac}, F_pbz) = {rho:+.3f}   ({'orthogonal' if abs(rho)<0.3 else 'overlapping'})")
    print(f"  IC F_pbz alone                : {summ(pbz_ics)['IC']:+.3f} (t={summ(pbz_ics)['t']:.1f})")
    print(f"  IC {fac} residual ⟂ F_pbz     : {summ(res_ics)['IC']:+.3f} (t={summ(res_ics)['t']:.1f})  <- orthogonal add")
    print(f"  IC composite ({fac}+F_pbz)    : {summ(comb_ics)['IC']:+.3f} (t={summ(comb_ics)['t']:.1f})")


def by_year(d, fac, fwd="profit_2M"):
    print(f"\n--- by-year IC: {fac} vs {fwd} (anti-2022-artifact check) ---")
    for y in range(2014, 2026):
        s = summ(xs_ic(d[d.year == y], fac, fwd))
        bar = "#"*int(abs(s['IC'])*100) if np.isfinite(s['IC']) else ""
        sign = "+" if (s['IC'] or 0) >= 0 else "-"
        print(f"  {y}: IC={s['IC']:+.3f} n={s['n']:>2} {sign}{bar}")


# ---- liquidity filter for broad universe (investable) ----
LIQ = 5e9  # turnover floor (Close*Volume); ACB ~ 9.8e9 sample
broad = df[df.turnover >= LIQ].copy()

report(broad, "BROAD universe (ticker_prune, turnover>=5bn)")
orthogonality(broad, "F_dcf")
orthogonality(broad, "F_cfy")
by_year(broad, "F_cfy")

moat = df[df.ticker.isin(MOAT36)].copy()
report(moat, "MOAT-36 basket (WIDE+NARROW)")
orthogonality(moat, "F_dcf")
orthogonality(moat, "F_cfy")
by_year(moat, "F_cfy")

report(df[df.ticker.isin(NARROW)].copy(), "NARROW-33 slice")

# WIDE-3: cross-section degenerate; report pooled time-series IC only, with caveat
w = df[df.ticker.isin(WIDE)].dropna(subset=["F_dcf", "profit_2M"])
print(f"\n{'='*78}\nWIDE-3 (VNM/TLG/DHG) — CROSS-SECTION DEGENERATE (3 names), pooled time-series only:")
for fac in FACTORS:
    s = df[df.ticker.isin(WIDE)].dropna(subset=[fac, "profit_2M"])
    if len(s) > 30:
        rho = spearmanr(s[fac], s.profit_2M)[0]
        print(f"  pooled corr({fac}, profit_2M) = {rho:+.3f}  n={len(s)}  [NOT a real XS-IC, name/time confound]")
