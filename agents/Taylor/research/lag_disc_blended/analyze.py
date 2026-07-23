#!/usr/bin/env python3
"""disc_c4/c5 in BLENDED V2.4 — metrics (full/IS/OOS), per-year, NAV-level LOO, DSR.
Reads combined_nav daily series from each run's audit CSV. Run with $DNA_PYEXE."""
import sys, os, glob
import numpy as np, pandas as pd
from scipy import stats

OUTDIR = "mike/agents/Taylor/research/lag_disc_blended"
RUNS = {"control": "discC4_control", "c4": "discC4", "c5": "discC5"}

def load_nav(tag):
    fs = glob.glob(f"data/v23_golive_audit_2014_now_*_exp_{tag}_univpit.csv")
    assert len(fs) == 1, f"{tag}: {fs}"
    df = pd.read_csv(fs[0], low_memory=False)
    d = df[df["combined_nav"].notna() & df["ymd"].notna()].copy()
    d["ymd"] = pd.to_datetime(d["ymd"], errors="coerce")
    d = d.dropna(subset=["ymd"]).sort_values("ymd")
    nav = d.groupby("ymd")["combined_nav"].last().astype(float)
    return nav, fs[0]

def cagr(s):
    s = s.dropna()
    if len(s) < 5: return float("nan")
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    return ((s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1) * 100

def maxdd(s):
    s = s.dropna(); peak = s.cummax(); return ((s / peak - 1).min()) * 100

def sharpe(s):
    r = s.pct_change().dropna()
    if r.std() == 0: return float("nan")
    n_per_yr = len(r) / ((s.index[-1] - s.index[0]).days / 365.25)
    return (r.mean() / r.std()) * np.sqrt(n_per_yr)

def sortino(s):
    r = s.pct_change().dropna(); dn = r[r < 0]
    if len(dn) == 0 or dn.std() == 0: return float("nan")
    n_per_yr = len(r) / ((s.index[-1] - s.index[0]).days / 365.25)
    return (r.mean() / dn.std()) * np.sqrt(n_per_yr)

def metrics(s):
    c = cagr(s); dd = maxdd(s)
    return dict(CAGR=c, Sharpe=sharpe(s), Sortino=sortino(s), MaxDD=dd,
                Calmar=(c / abs(dd) if dd else float("nan")))

def window(nav, y1, y2):
    return metrics(nav[(nav.index.year >= y1) & (nav.index.year <= y2)])

def dsr(s, n_trials, sr0_annual=0.0):
    """Deflated Sharpe on daily returns. n_trials for the deflation benchmark."""
    r = s.pct_change().dropna().values
    T = len(r); sr = r.mean() / r.std()
    g3 = stats.skew(r); g4 = stats.kurtosis(r, fisher=False)
    # expected max SR under n independent trials (Bailey & Lopez de Prado)
    emc = 0.5772156649
    if n_trials > 1:
        z1 = stats.norm.ppf(1 - 1.0 / n_trials)
        z2 = stats.norm.ppf(1 - 1.0 / (n_trials * np.e))
        sr0 = (1 - emc) * z1 + emc * z2   # in per-obs SR units (std of trial SRs ~1/sqrt(T))
        sr0 = sr0 / np.sqrt(T)
    else:
        sr0 = sr0_annual / np.sqrt(252)
    num = (sr - sr0) * np.sqrt(T - 1)
    den = np.sqrt(1 - g3 * sr + (g4 - 1) / 4.0 * sr ** 2)
    z = num / den
    return stats.norm.cdf(z), sr * np.sqrt(252), z

navs = {}; files = {}
for k, tag in RUNS.items():
    try:
        navs[k], files[k] = load_nav(tag)
    except AssertionError as e:
        print(f"[MISSING] {e}");
for k in navs: print(f"  {k:10s} <- {os.path.basename(files[k])}  ({len(navs[k])} days, {navs[k].index[0].date()}..{navs[k].index[-1].date()})")

print("\n" + "=" * 96)
print("  BLENDED V2.4 — disc_c4/c5 full-system metrics")
print("=" * 96)
hdr = f"  {'variant':<10}{'CAGR':>8}{'Sharpe':>8}{'Sortino':>9}{'MaxDD':>8}{'Calmar':>8}"
for w, lab in [((None, None), "FULL"), ((2014, 2019), "IS 2014-19"), ((2020, 2026), "OOS 2020-26")]:
    print(f"\n  --- {lab} ---"); print(hdr)
    for k in navs:
        m = metrics(navs[k]) if w == (None, None) else window(navs[k], *w)
        print(f"  {k:<10}{m['CAGR']:>7.2f}%{m['Sharpe']:>8.2f}{m['Sortino']:>9.2f}{m['MaxDD']:>7.1f}%{m['Calmar']:>8.2f}")

# per-year returns
print("\n" + "=" * 96); print("  PER-YEAR total return (%)"); print("=" * 96)
years = range(navs["control"].index[0].year, navs["control"].index[-1].year + 1)
print(f"  {'yr':<6}" + "".join(f"{k:>10}" for k in navs) + f"{'c4-ctrl':>10}")
for y in years:
    row = {}
    for k in navs:
        ny = navs[k][navs[k].index.year == y]
        row[k] = (ny.iloc[-1] / ny.iloc[0] - 1) * 100 if len(ny) >= 5 else float("nan")
    d = row.get("c4", float("nan")) - row.get("control", float("nan"))
    print(f"  {y:<6}" + "".join(f"{row[k]:>+9.1f}" for k in navs) + f"{d:>+9.1f}")

# NAV-level LOO: drop each year's daily returns, re-chain, full CAGR; delta treat-control
print("\n" + "=" * 96)
print("  LOO-by-year (NAV-level): full CAGR with one year's daily returns removed; delta vs control")
print("  (edge = treat_CAGR - control_CAGR must stay same-sign across all drops)")
print("=" * 96)
def loo_cagr(s, drop_y):
    r = s.pct_change().dropna()
    r = r[r.index.year != drop_y]
    nav = (1 + r).cumprod()
    return cagr(nav)
for treat in ("c4", "c5"):
    if treat not in navs: continue
    base_full = cagr((1 + navs["control"].pct_change().dropna()).cumprod())
    treat_full = cagr((1 + navs[treat].pct_change().dropna()).cumprod())
    print(f"\n  {treat}: full-period edge = {treat_full - base_full:+.2f}pp")
    print(f"  {'drop_yr':<9}{'ctrl':>9}{treat:>9}{'edge':>9}")
    for y in years:
        bc = loo_cagr(navs["control"], y); tc = loo_cagr(navs[treat], y)
        print(f"  {y:<9}{bc:>8.2f}%{tc:>8.2f}%{tc - bc:>+8.2f}")

# DSR
print("\n" + "=" * 96); print("  DSR (Deflated Sharpe Ratio) on daily combined NAV"); print("=" * 96)
N_TRIALS = int(os.environ.get("N_TRIALS", "10"))
for k in navs:
    p, annsr, z = dsr(navs[k], N_TRIALS)
    print(f"  {k:<10} DSR={p:.4f}  ann-SR={annsr:.3f}  z={z:.2f}  (N_trials={N_TRIALS})")
