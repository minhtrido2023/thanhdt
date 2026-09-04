#!/usr/bin/env python3
"""IS/OOS/LOO/DSR analysis: baseline (prod funnel) vs gfloor (prod funnel + golden floor)."""
import pandas as pd, numpy as np, os

W = os.path.dirname(os.path.abspath(__file__))

def load(tag):
    d = pd.read_csv(f"{W}/nav_{tag}.csv", parse_dates=["time"]).set_index("time")["nav"]
    return d

base = load("baseline")
gf = load("gfloor")
vni = pd.read_csv(f"{W}/vnindex.csv", parse_dates=["time"]).set_index("time")["Close"]
vni = vni / vni.iloc[0]

def cagr(s, a=None, b=None):
    s = s.loc[a:b] if (a or b) else s
    s = s.dropna()
    if len(s) < 2:
        return np.nan
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    return (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1 if yrs > 0 else np.nan

def sharpe(s, a=None, b=None):
    s = s.loc[a:b] if (a or b) else s
    r = s.pct_change().dropna()
    if r.std() == 0 or len(r) < 20:
        return np.nan
    return r.mean() / r.std() * np.sqrt(252)

def maxdd(s, a=None, b=None):
    s = s.loc[a:b] if (a or b) else s
    s = s.dropna()
    roll_max = s.cummax()
    dd = s / roll_max - 1
    return dd.min()

def calmar(s, a=None, b=None):
    c = cagr(s, a, b); d = maxdd(s, a, b)
    return c / abs(d) if d else np.nan

print("=== FULL 2014-01..2026-09 ===")
for name, s in [("baseline", base), ("gfloor", gf), ("VNINDEX", vni)]:
    print(f"  {name:10s} CAGR={100*cagr(s):.2f}% Sharpe={sharpe(s):.2f} MaxDD={100*maxdd(s):.1f}% Calmar={calmar(s):.2f}")

print("\n=== IS 2014-07..2019-12 (fa_ratings_8l starts 2014-07-09) ===")
IS_A, IS_B = "2014-07-09", "2019-12-31"
for name, s in [("baseline", base), ("gfloor", gf), ("VNINDEX", vni)]:
    print(f"  {name:10s} CAGR={100*cagr(s, IS_A, IS_B):.2f}% Sharpe={sharpe(s, IS_A, IS_B):.2f} "
          f"MaxDD={100*maxdd(s, IS_A, IS_B):.1f}% Calmar={calmar(s, IS_A, IS_B):.2f}")

print("\n=== OOS 2020-01..2026-09 ===")
OOS_A, OOS_B = "2020-01-01", "2026-09-03"
for name, s in [("baseline", base), ("gfloor", gf), ("VNINDEX", vni)]:
    print(f"  {name:10s} CAGR={100*cagr(s, OOS_A, OOS_B):.2f}% Sharpe={sharpe(s, OOS_A, OOS_B):.2f} "
          f"MaxDD={100*maxdd(s, OOS_A, OOS_B):.1f}% Calmar={calmar(s, OOS_A, OOS_B):.2f}")

print("\n=== Per-year: gfloor CAGR minus baseline CAGR (delta, pp) ===")
years = range(2015, 2026)  # full calendar years only (2014 partial from Jul, 2026 partial to Sep)
deltas = []
for y in years:
    a, b = f"{y}-01-01", f"{y}-12-31"
    cb = cagr(base, a, b) if len(base.loc[a:b].dropna()) > 20 else np.nan
    cg = cagr(gf, a, b) if len(gf.loc[a:b].dropna()) > 20 else np.nan
    d = (cg - cb) * 100 if pd.notna(cb) and pd.notna(cg) else np.nan
    deltas.append(d)
    print(f"  {y}: baseline={100*cb:.2f}% gfloor={100*cg:.2f}% delta={d:+.2f}pp")
deltas_arr = np.array([d for d in deltas if pd.notna(d)])
print(f"\n  years with delta>0: {(deltas_arr>0).sum()}/{len(deltas_arr)}  mean delta={deltas_arr.mean():+.2f}pp  "
      f"median={np.median(deltas_arr):+.2f}pp  std={deltas_arr.std():.2f}pp")

print("\n=== Leave-one-year-out: FULL-period delta (gfloor-baseline) excluding each year ===")
full_delta_all = (cagr(gf) - cagr(base)) * 100
print(f"  all-years delta = {full_delta_all:+.2f}pp")
for y in years:
    a, b = f"{y}-01-01", f"{y}-12-31"
    b_ex = pd.concat([base.loc[:pd.Timestamp(a) - pd.Timedelta(days=1)], base.loc[pd.Timestamp(b) + pd.Timedelta(days=1):]])
    g_ex = pd.concat([gf.loc[:pd.Timestamp(a) - pd.Timedelta(days=1)], gf.loc[pd.Timestamp(b) + pd.Timedelta(days=1):]])
    # cumulative return excluding year y (splice out, chain the two remaining segments)
    def chained_ret(orig, a, b):
        seg1 = orig.loc[:pd.Timestamp(a) - pd.Timedelta(days=1)]
        seg2 = orig.loc[pd.Timestamp(b) + pd.Timedelta(days=1):]
        if len(seg1) < 2 or len(seg2) < 2:
            return np.nan
        r1 = seg1.iloc[-1] / seg1.iloc[0]
        r2 = seg2.iloc[-1] / seg2.iloc[0]
        return r1 * r2 - 1
    rb = chained_ret(base, a, b)
    rg = chained_ret(gf, a, b)
    d = (rg - rb) * 100 if pd.notna(rb) and pd.notna(rg) else np.nan
    print(f"  ex-{y}: total-return-delta = {d:+.2f}pp")

# ---- DSR (Deflated Sharpe Ratio) on the DAILY EXCESS return series (gfloor - baseline) ----
print("\n=== DSR on gfloor-vs-baseline daily excess return ===")
rb = base.pct_change().dropna()
rg = gf.pct_change().dropna()
common = rb.index.intersection(rg.index)
excess = (rg.loc[common] - rb.loc[common])
sr_ann = excess.mean() / excess.std() * np.sqrt(252) if excess.std() > 0 else np.nan
n = len(excess)
skew = excess.skew()
kurt = excess.kurtosis() + 3  # pandas kurtosis is excess kurtosis; DSR formula wants raw kurtosis
N_TRIALS = 1  # single hypothesis: does adding golden floor on top of the EXISTING gate_rating<=3
              # (byte-identical to production admission logic) change outcome. Not a family search.
# Bailey-Lopez de Prado DSR: SR0 from expected max SR of N_TRIALS iid trials (N=1 -> SR0=0, no
# multiple-testing haircut needed) then PSR(SR0) test.
from scipy.stats import norm
if N_TRIALS > 1:
    euler_gamma = 0.5772156649
    sr0 = (1 - euler_gamma) * norm.ppf(1 - 1.0 / N_TRIALS) + euler_gamma * norm.ppf(1 - 1.0 / (N_TRIALS * np.e))
    sr0 = sr0 / np.sqrt(252)  # scale to daily if using daily SR base... (kept simple, N_TRIALS=1 here anyway)
else:
    sr0 = 0.0
sr_daily = excess.mean() / excess.std() if excess.std() > 0 else np.nan
denom = np.sqrt(1 - skew * sr_daily + (kurt - 1) / 4 * sr_daily**2)
psr = norm.cdf((sr_daily - sr0) * np.sqrt(n - 1) / denom) if pd.notna(denom) and denom > 0 else np.nan
print(f"  n_days={n}  ann.excess.SR={sr_ann:.3f}  skew={skew:.2f}  kurt(raw)={kurt:.2f}  N_TRIALS={N_TRIALS}")
print(f"  DSR (=PSR at SR0 from N_TRIALS) = {psr:.3f}  {'PASS>=0.95' if pd.notna(psr) and psr>=0.95 else 'RED FLAG <0.95'}")
print(f"  win-rate (days gfloor>baseline) = {100*(excess>0).mean():.1f}%")
