# -*- coding: utf-8 -*-
"""CP-DVR1 gate analysis (job Taylor_20260711_235305) — reads the 4 _exp_dvr8l CSVs, computes
Full/IS/OOS CAGR + Sharpe + MaxDD + Calmar, and per-year LOO CAGR deltas (tilt vs same-cache base).
Analysis only: no new trial, no new config. Conventions mirror extract_peryear.py (combined_nav,
calendar-time CAGR) and the audit header (Sharpe 252 on daily returns)."""
import pandas as pd, numpy as np

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
PAT = (WORKDIR + "/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_"
       "etfliqcustompitg_wtnamecap_exp_dvr8l{}.csv")

def nav_series(tag):
    df = pd.read_csv(PAT.format(tag), low_memory=False)
    d = df[df["combined_nav"].notna() & df["ymd"].notna()].copy()
    d["ymd"] = pd.to_datetime(d["ymd"], errors="coerce")
    d = d.dropna(subset=["ymd"]).sort_values("ymd")
    return d.groupby("ymd")["combined_nav"].last().astype(float)

def cagr(s):
    if len(s) < 5: return np.nan
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    return ((s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1) * 100

def metrics(s):
    r = s.pct_change().dropna()
    sh = r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else np.nan
    dd = (s / s.cummax() - 1).min() * 100
    c = cagr(s)
    return c, sh, dd, (c / abs(dd) if dd < 0 else np.nan)

def loo_cagr(s, drop_year):
    """CAGR compounding daily returns of all years except drop_year; annualize on the
    calendar-time span actually kept (days-per-session basis of the kept subset)."""
    r = s.pct_change().dropna()
    keep = r[r.index.year != drop_year]
    total = float((1 + keep).prod())
    # calendar-equivalent years of the kept subset: full span minus the dropped year's span
    full_yrs = (s.index[-1] - s.index[0]).days / 365.25
    ydates = s.index[s.index.year == drop_year]
    drop_yrs = ((ydates[-1] - ydates[0]).days / 365.25) if len(ydates) > 1 else 0.0
    yrs = full_yrs - drop_yrs
    return (total ** (1 / yrs) - 1) * 100 if yrs > 0 else np.nan

navs = {t: nav_series(t) for t in ("base", "r1", "r2", "r3")}
print("== Headline (Full / IS<=2019 / OOS>=2020) ==")
for t, s in navs.items():
    f = metrics(s); i = metrics(s[s.index <= "2019-12-31"]); o = metrics(s[s.index >= "2020-01-01"])
    print(f"{t:>4}: FULL {f[0]:6.2f}% Sh {f[1]:.3f} DD {f[2]:6.2f}% Cal {f[3]:.3f} | "
          f"IS {i[0]:6.2f}% | OOS {o[0]:6.2f}% Sh {o[1]:.3f} DD {o[2]:6.2f}% Cal {o[3]:.3f}")

print("\n== Per-year LOO CAGR delta vs same-cache base (tilt - base), pp ==")
years = sorted(set(navs["base"].index.year))
hdr = "year " + "".join(f"{t:>10}" for t in ("r1", "r2", "r3"))
print(hdr)
for y in years:
    row = f"{y}  "
    for t in ("r1", "r2", "r3"):
        d = loo_cagr(navs[t], y) - loo_cagr(navs["base"], y)
        row += f"{d:>+10.3f}"
    print(row)
print("\n(delta full-sample, pp): " +
      "  ".join(f"{t}={cagr(navs[t]) - cagr(navs['base']):+.3f}" for t in ("r1", "r2", "r3")))
