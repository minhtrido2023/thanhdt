#!/usr/bin/env python
"""CAPIT trigger study — Q1 dose-response, Q2 metric, Q3 state sizing, Q4 confirmation.
Significance via stationary block bootstrap (block=60) — overlapping fwd60 windows make
i.i.d. t-stats invalid.
"""
import numpy as np, pandas as pd
P = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_capittrig/panel.parquet"
d = pd.read_parquet(P).dropna(subset=["fwd60_ew"])
rng = np.random.default_rng(20260720)
H = 60

def block_boot_mean(x, n=4000, block=H):
    """Stationary block bootstrap of the mean; returns (lo90, hi90)."""
    x = np.asarray(x, float); N = len(x)
    if N < 2: return (np.nan, np.nan)
    nb = int(np.ceil(N / block))
    means = np.empty(n)
    for i in range(n):
        starts = rng.integers(0, N, nb)
        idx = np.concatenate([np.arange(s, s + block) % N for s in starts])[:N]
        means[i] = x[idx].mean()
    return tuple(np.percentile(means, [5, 95]))

def boot_diff(xa, xb, n=4000, block=H):
    """CI of mean(xa)-mean(xb) resampling each independently (different fire sets)."""
    xa, xb = np.asarray(xa, float), np.asarray(xb, float)
    if len(xa) < 2 or len(xb) < 2: return (np.nan, np.nan)
    out = np.empty(n)
    for i in range(n):
        for j, x in enumerate((xa, xb)):
            N = len(x); nb = int(np.ceil(N / block))
            s = rng.integers(0, N, nb)
            idx = np.concatenate([np.arange(k, k + block) % N for k in s])[:N]
            out[i] = x[idx].mean() if j == 0 else out[i] - x[idx].mean()
    return tuple(np.percentile(out, [5, 95]))

def events(mask, gap=30):
    """Cluster fire days into events exactly like production (>=30 CALENDAR-day gap)."""
    t = d.index[mask]
    if len(t) == 0: return pd.DatetimeIndex([])
    g = pd.Series(t).diff().dt.days.fillna(999)
    return pd.DatetimeIndex(pd.Series(t)[(g >= gap).cumsum().duplicated(keep="first") == False])

print("=" * 88); print("Q1 — DOSE-RESPONSE: is fwd60 monotone in oversold breadth?"); print("=" * 88)
q = pd.qcut(d["bd_rsi30"], 5, labels=[f"Q{i+1}" for i in range(5)], duplicates="drop")
for lab, g in d.groupby(q, observed=True):
    lo, hi = block_boot_mean(g["fwd60_ew"])
    print(f"  {lab}  breadth[{g['bd_rsi30'].min():.3f},{g['bd_rsi30'].max():.3f}]  "
          f"n={len(g):4d}  mean_fwd60={g['fwd60_ew'].mean():+.2%}  CI90=[{lo:+.2%},{hi:+.2%}]")
rho = d["bd_rsi30"].corr(d["fwd60_ew"], method="spearman")
print(f"\n  Spearman rho(breadth, fwd60_ew) = {rho:+.4f}")
# bootstrap the rho itself
rs = []
for _ in range(2000):
    nb = int(np.ceil(len(d) / H)); s = rng.integers(0, len(d), nb)
    idx = np.concatenate([np.arange(k, k + H) % len(d) for k in s])[:len(d)]
    sub = d.iloc[idx]
    rs.append(sub["bd_rsi30"].corr(sub["fwd60_ew"], method="spearman"))
print(f"  block-bootstrap CI90 of rho = [{np.percentile(rs,5):+.4f}, {np.percentile(rs,95):+.4f}]")

print("\n" + "=" * 88); print("Q1b — THRESHOLD SWEEP (event-level, production clustering)"); print("=" * 88)
base_all = d["fwd60_ew"].mean()
print(f"  unconditional mean fwd60_ew (all days) = {base_all:+.2%}\n")
res = {}
for thr in [0.20, 0.25, 0.30, 0.35, 0.40]:
    m = d["bd_rsi30"] >= thr
    ev = events(m.values)
    y = d.loc[d.index.isin(ev), "fwd60_ew"].dropna()
    lo, hi = block_boot_mean(d.loc[m, "fwd60_ew"].dropna()) if m.sum() > 1 else (np.nan, np.nan)
    res[thr] = y
    tag = " <-- PRODUCTION" if abs(thr - 0.30) < 1e-9 else ""
    print(f"  thr={thr:.2f}  fire_days={m.sum():4d}  events={len(ev):3d}  "
          f"event_mean_fwd60={y.mean():+.2%}  allday_CI90=[{lo:+.2%},{hi:+.2%}]  "
          f"win={np.mean(y>0):.0%}{tag}")
print("\n  Diff vs production 0.30 (event-level, block bootstrap CI90):")
for thr in [0.20, 0.25, 0.35, 0.40]:
    lo, hi = boot_diff(res[thr].values, res[0.30].values)
    dm = res[thr].mean() - res[0.30].mean()
    print(f"    {thr:.2f} - 0.30 = {dm:+.2%}  CI90=[{lo:+.2%},{hi:+.2%}]  "
          f"{'EXCLUDES 0' if (lo>0 or hi<0) else 'spans 0'}")

print("\n  IS(2014-19) / OOS(2020+) split, event-level:")
for thr in [0.20, 0.25, 0.30, 0.35, 0.40]:
    y = res[thr]
    i_, o_ = y[y.index < "2020-01-01"], y[y.index >= "2020-01-01"]
    print(f"    thr={thr:.2f}  IS n={len(i_):2d} {i_.mean():+.2%}   OOS n={len(o_):2d} {o_.mean():+.2%}")

print("\n" + "=" * 88); print("Q2 — ALTERNATIVE BREADTH METRICS (matched fire-rate)"); print("=" * 88)
n_fire = int((d["bd_rsi30"] >= 0.30).sum())
print(f"  matching production fire-day count = {n_fire}\n")
d["composite"] = np.where(d["dd52"] <= -10, d["bd_rsi30"], 0.0)   # gate ∧ market drawdown
for name in ["bd_rsi30", "bd_ma200", "bd_at1mlow", "composite"]:
    cut = d[name].nlargest(n_fire).min()
    m = d[name] >= cut
    ev = events(m.values); y = d.loc[d.index.isin(ev), "fwd60_ew"].dropna()
    allday = d.loc[m, "fwd60_ew"].dropna()
    lo, hi = block_boot_mean(allday)
    fp = np.mean(y <= 0)
    tag = " <-- PRODUCTION" if name == "bd_rsi30" else ""
    print(f"  {name:11s} cut={cut:.3f}  events={len(ev):3d}  event_mean={y.mean():+.2%}  "
          f"allday_mean={allday.mean():+.2%} CI90=[{lo:+.2%},{hi:+.2%}]  false_pos={fp:.0%}{tag}")

print("\n" + "=" * 88); print("Q3 — STATE-CONDITIONAL SIZING: does fwd60 rank match the size table?"); print("=" * 88)
SIZE = {1: 1.00, 2: 0.50, 3: 0.75, 4: 0.50, 5: 0.50}
NAME = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EXBULL"}
ev30 = events((d["bd_rsi30"] >= 0.30).values)
fire = d.loc[d.index.isin(ev30)]
print("  (a) at ACTUAL fire events (n=%d):" % len(fire))
for s, g in fire.groupby("state"):
    print(f"    state={int(s)} {NAME[int(s)]:8s} n={len(g):2d}  mean_fwd60={g['fwd60_ew'].mean():+.2%}  "
          f"median={g['fwd60_ew'].median():+.2%}  current_size={SIZE[int(s)]:.2f}")
print("\n  (b) at ALL oversold-ish days (breadth>=0.10, larger sample):")
sub = d[d["bd_rsi30"] >= 0.10]
for s, g in sub.groupby("state"):
    lo, hi = block_boot_mean(g["fwd60_ew"])
    print(f"    state={int(s)} {NAME[int(s)]:8s} n={len(g):4d}  mean_fwd60={g['fwd60_ew'].mean():+.2%}  "
          f"CI90=[{lo:+.2%},{hi:+.2%}]  current_size={SIZE[int(s)]:.2f}")
print("\n  (c) rank check — does forward-return ordering invert the size table?")
r_emp = sub.groupby("state")["fwd60_ew"].mean().sort_values(ascending=False)
print(f"    empirical fwd60 rank (best->worst): {[NAME[int(s)] for s in r_emp.index]}")
r_size = pd.Series(SIZE).sort_values(ascending=False)
print(f"    size-table rank       (big->small): {[NAME[int(s)] for s in r_size.index]}")
print("\n  (d) dd52w depth as an ADDITIONAL sizing signal (within oversold days):")
for lab, g in sub.groupby(pd.cut(sub["dd52"], [-100, -25, -15, -8, 0])):
    lo, hi = block_boot_mean(g["fwd60_ew"])
    print(f"    dd52 in {str(lab):16s} n={len(g):4d}  mean_fwd60={g['fwd60_ew'].mean():+.2%}  CI90=[{lo:+.2%},{hi:+.2%}]")

print("\n" + "=" * 88); print("Q4 — CONFIRMATORY WAIT: fire at first touch vs wait for breadth to roll over"); print("=" * 88)
fire_dates, conf_dates = list(ev30), []
idx = d.index
for d0 in fire_dates:
    i0 = idx.get_loc(d0)
    # walk forward up to 20 sessions: confirm when breadth falls 2 consecutive days from a peak
    peak, conf = d["bd_rsi30"].iloc[i0], None
    for j in range(i0 + 1, min(i0 + 21, len(idx))):
        b = d["bd_rsi30"].iloc[j]
        peak = max(peak, b)
        if j >= i0 + 2 and b < d["bd_rsi30"].iloc[j-1] < d["bd_rsi30"].iloc[j-2] and peak > d["bd_rsi30"].iloc[i0] * 0.0:
            conf = idx[j]; break
    conf_dates.append(conf)
kept = [(a, c) for a, c in zip(fire_dates, conf_dates) if c is not None]
y0 = d.loc[[a for a, _ in kept], "fwd60_ew"]
y1 = d.loc[[c for _, c in kept], "fwd60_ew"]
lo, hi = boot_diff(y1.dropna().values, y0.dropna().values)
print(f"  events with a confirmation within 20 sessions: {len(kept)}/{len(fire_dates)} "
      f"(dropped {len(fire_dates)-len(kept)})")
print(f"  fire-at-touch   mean_fwd60 = {y0.mean():+.2%}  (n={y0.notna().sum()})")
print(f"  wait-for-rollover mean_fwd60 = {y1.mean():+.2%}  (n={y1.notna().sum()})")
print(f"  diff = {y1.mean()-y0.mean():+.2%}  CI90=[{lo:+.2%},{hi:+.2%}]  "
      f"{'EXCLUDES 0' if (lo>0 or hi<0) else 'spans 0'}")
mean_lag = np.mean([(c - a).days for a, c in kept])
print(f"  mean confirmation delay = {mean_lag:.1f} calendar days")

print("\n" + "=" * 88); print("PER-YEAR leave-one-out on the production gate (edge concentration)"); print("=" * 88)
fy = d.loc[d.index.isin(ev30), "fwd60_ew"].dropna()
print(f"  all events mean = {fy.mean():+.2%} (n={len(fy)})")
for yr in sorted(set(fy.index.year)):
    loo = fy[fy.index.year != yr]
    print(f"    drop {yr}: n={len(loo):2d}  mean={loo.mean():+.2%}  "
          f"(that year: n={sum(fy.index.year==yr)} {fy[fy.index.year==yr].mean():+.2%})")
