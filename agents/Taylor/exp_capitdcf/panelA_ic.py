# -*- coding: utf-8 -*-
"""PANEL A analysis — pre-registered (PREREG.md). 3 ranking axes: DCF / PBZ / COMBO.
Primary: h=60, quarterly NON-OVERLAPPING obs dates. Robustness: h=250 annual; monthly
with year-block cluster bootstrap. LOO by year + IS/OOS on the paired DCF-PBZ difference.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
X = pd.read_csv("/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_capitdcf/panelA.csv",
                parse_dates=["obs"])

def add_ranks(g, na_mode="neutral"):
    """Within-date ranks, higher = more attractive. N/A MoS -> neutral (median rank)."""
    g = g.copy()
    n = len(g)
    g["rk_pbz"] = (-g["pbz"]).rank()                       # lower pbz = cheaper = better
    m = g["mos"]
    if na_mode == "drop":
        g = g[m.notna()].copy()
        if len(g) < 3: return None
        g["rk_dcf"] = g["mos"].rank()
        g["rk_pbz"] = (-g["pbz"]).rank()
    else:
        r = m.rank()                                        # NaN stays NaN
        g["rk_dcf"] = r.fillna((len(g) + 1) / 2.0)          # neutral = median rank
    g["rk_combo"] = (g["rk_dcf"].rank() + g["rk_pbz"].rank()) / 2.0
    return g

def ic_series(df, axis, retcol, na_mode="neutral", min_n=4):
    """Per-date Spearman IC between axis rank and realized forward return."""
    out = {}
    for d, g in df.groupby("obs"):
        g = g.dropna(subset=[retcol])
        if len(g) < min_n: continue
        g = add_ranks(g, na_mode)
        if g is None or len(g) < min_n: continue
        g = g.dropna(subset=[retcol])
        if len(g) < min_n or g[axis].nunique() < 2: continue
        out[d] = g[axis].corr(g[retcol], method="spearman")
    return pd.Series(out).dropna()

def tstat(s):
    if len(s) < 2 or s.std(ddof=1) == 0: return np.nan
    return s.mean() / (s.std(ddof=1) / np.sqrt(len(s)))

def nonoverlap(dates, h, sess_per_month=21):
    """Keep obs dates spaced >= h sessions apart (approx via months)."""
    step = max(1, int(np.ceil(h / sess_per_month)))
    dates = sorted(dates); keep, last = [], None
    for d in dates:
        if last is None or (d - last).days >= step * 28:
            keep.append(d); last = d
    return keep

AXES = [("rk_dcf", "DCF MoS"), ("rk_pbz", "pb_z (baseline)"), ("rk_combo", "COMBO 50/50")]

def run_block(title, df, retcol, dates, na_mode="neutral"):
    d = df[df.obs.isin(dates)]
    print(f"\n=== {title} ===")
    print(f"  obs dates used {d.obs.nunique()} | name-dates {len(d)}")
    print(f"  {'axis':<18}{'IC':>8}{'t':>7}{'n_dates':>9}{'hit>0':>8}")
    series = {}
    for a, lab in AXES:
        s = ic_series(d, a, retcol, na_mode)
        series[a] = s
        print(f"  {lab:<18}{s.mean():>8.3f}{tstat(s):>7.2f}{len(s):>9}{(s>0).mean():>8.2f}")
    # paired difference DCF - PBZ (pre-registered decision criterion ii)
    dd = (series["rk_dcf"] - series["rk_pbz"]).dropna()
    print(f"  PAIRED DCF-PBZ: diff={dd.mean():+.4f} t={tstat(dd):+.2f} n={len(dd)} "
          f"P(diff>0 by date)={(dd>0).mean():.2f}")
    return series, dd

# ---------- PRIMARY ----------
q_dates = nonoverlap(sorted(X.obs.unique()), 60)
prim_series, prim_dd = run_block("PRIMARY — h=60, quarterly non-overlapping (PRE-REGISTERED)",
                                 X, "r60", q_dates)

# criterion (iii) LOO by year, (iv) IS/OOS — on the primary paired difference
print("\n--- (iii) Leave-one-YEAR-out on paired DCF-PBZ [primary] ---")
yrs = sorted({d.year for d in prim_dd.index})
loo = {}
for y in yrs:
    sub = prim_dd[[d for d in prim_dd.index if d.year != y]]
    loo[y] = sub.mean()
    print(f"  drop {y}: diff={sub.mean():+.4f} (n={len(sub)})")
print(f"  LOO range [{min(loo.values()):+.4f}, {max(loo.values()):+.4f}] "
      f"| all positive: {all(v > 0 for v in loo.values())}")

print("\n--- (iv) IS/OOS split on paired DCF-PBZ [primary] ---")
for lab, sub in [("IS 2014-2019", prim_dd[[d for d in prim_dd.index if d.year <= 2019]]),
                 ("OOS 2020+",    prim_dd[[d for d in prim_dd.index if d.year >= 2020]])]:
    print(f"  {lab:<14} diff={sub.mean():+.4f} t={tstat(sub):+.2f} n={len(sub)}")

# ---------- ROBUSTNESS ----------
run_block("ROBUSTNESS — h=250, annual non-overlapping", X, "r250", nonoverlap(sorted(X.obs.unique()), 250))
run_block("ROBUSTNESS — h=60, ALL monthly obs (overlapping; see block bootstrap below)", X, "r60", sorted(X.obs.unique()))
run_block("SENSITIVITY — h=60 quarterly, DCF N/A DROPPED from measurement", X, "r60", q_dates, na_mode="drop")

# year-block cluster bootstrap on the monthly (overlapping) paired difference
sm = ic_series(X, "rk_dcf", "r60") - ic_series(X, "rk_pbz", "r60")
sm = sm.dropna()
yb = {y: sm[[d for d in sm.index if d.year == y]] for y in sorted({d.year for d in sm.index})}
ks = list(yb); rng = np.random.default_rng(17)
bs = np.array([pd.concat([yb[k] for k in rng.choice(ks, len(ks), replace=True)]).mean()
               for _ in range(5000)])
print(f"\n=== Year-block cluster bootstrap (monthly panel, paired DCF-PBZ, h=60) ===")
print(f"  point={sm.mean():+.4f} CI95=[{np.percentile(bs,2.5):+.4f},{np.percentile(bs,97.5):+.4f}] "
      f"P(diff>0)={np.mean(bs>0):.2f} | {len(ks)} year blocks")
