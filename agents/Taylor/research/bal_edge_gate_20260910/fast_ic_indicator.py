# -*- coding: utf-8 -*-
"""fast_ic_indicator.py — BUOC 2: does a fwd-1M cross-sectional IC flag a momentum FLIP
earlier than the production fwd-3M IC, and at what false-alarm cost?

Reuses data/edge_panel.csv (produced by edge_health_monitor.py --refresh; it ALREADY
carries fwd_1m alongside fwd_3m -- no new data source, no new BQ cost).

Two clocks are kept strictly apart:
  SIGNAL month m  -- the month the cross-section is measured in.
  AVAILABLE date  -- when that month's IC can first be computed:
                     fwd_1m -> m + 1 month, fwd_3m -> m + 3 months.
Every verdict below is evaluated on the AVAILABLE clock, so "earlier" means earlier in
wall-clock time for an operator, not earlier in signal-index terms.

Verdict rule = the production one (edge_health_monitor.classify), with ONE change made
for causality: the "full" reference mean is EXPANDING up to the evaluation date, not the
whole sample (production compares recent-12M vs full-sample, which peeks at the future --
fine for a dashboard read today, wrong for dating a historical alarm).
"""
import os, sys, io
import numpy as np, pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
sys.path.insert(0, WORKDIR)
from edge_health_monitor import map_sector, spearman, MIN_NAMES, MIN_NAMES_SEC, ROLL, RECENT, T_SIG, MAG_MIN

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
LAG_M = {"fwd_1m": 1, "fwd_3m": 3}
SIGNALS = ["mom_200", "D_RSI"]
SCOPES = ["ALL", "CYCLICAL"]

df = pd.read_csv("data/edge_panel.csv", parse_dates=["time"])
df["sector"] = df["icb"].map(map_sector)
df["ym"] = df["time"].dt.to_period("M")
print(f"panel {len(df):,} rows  {df.ym.min()} -> {df.ym.max()}")


def monthly_ic(sub, col, fwd, min_names):
    lo, hi = sub[fwd].quantile([0.005, 0.995])
    s_all = sub.assign(**{fwd: sub[fwd].clip(lo, hi)})
    out = {}
    for ym, g in s_all.groupby("ym"):
        s = g[[col, fwd]].dropna()
        if len(s) < min_names or s[col].nunique() < 5:
            continue
        ic = spearman(s[col].values, s[fwd].values)
        if ic is not None and np.isfinite(ic):
            out[ym] = ic
    return pd.Series(out).sort_index()


def classify(full, recent, tstat):
    if not np.isfinite(tstat) or abs(tstat) < T_SIG:
        return "WEAK"
    if np.sign(recent) != np.sign(full) and abs(recent) >= MAG_MIN:
        return "FLIPPED"
    ratio = abs(recent) / abs(full) if full else 0.0
    if ratio < 0.33:   return "DECAYED"
    if ratio < 0.66:   return "FADING"
    if ratio > 1.30:   return "STRENGTH"
    return "HEALTHY"


def realtime_verdicts(ic, lag_m):
    """For each wall-clock month t, use only signal-months m with m + lag_m <= t."""
    rows = []
    months = pd.period_range(ic.index.min() + lag_m, ic.index.max() + lag_m, freq="M")
    for t in months:
        avail = ic[ic.index <= (t - lag_m)]
        if len(avail) < RECENT + 12:      # need an expanding baseline + a recent window
            continue
        full = avail.mean(); sd = avail.std(ddof=1); n = len(avail)
        tstat = full / (sd / np.sqrt(n)) if sd and sd > 0 else 0.0
        recent = avail.tail(RECENT).mean()
        rows.append(dict(avail_month=t, sig_month=avail.index[-1], n=n,
                         full=full, recent=recent, tstat=tstat,
                         verdict=classify(full, recent, tstat)))
    return pd.DataFrame(rows)


def alarms(v, label):
    """FLIPPED episodes on the availability clock: (first month, length, reverted?)"""
    f = (v["verdict"] == "FLIPPED").values
    eps, i = [], 0
    while i < len(f):
        if f[i]:
            j = i
            while j + 1 < len(f) and f[j + 1]:
                j += 1
            eps.append((v["avail_month"].iloc[i], v["avail_month"].iloc[j], j - i + 1))
            i = j + 1
        else:
            i += 1
    return eps


res = {}
allv = []
for sig in SIGNALS:
    for scope in SCOPES:
        sub = df if scope == "ALL" else df[df["sector"] == scope]
        mn = MIN_NAMES if scope == "ALL" else MIN_NAMES_SEC
        for fwd in ("fwd_1m", "fwd_3m"):
            ic = monthly_ic(sub, sig, fwd, mn)
            v = realtime_verdicts(ic, LAG_M[fwd])
            v["signal"] = sig; v["scope"] = scope; v["fwd"] = fwd
            res[(sig, scope, fwd)] = (ic, v)
            allv.append(v)
pd.concat(allv).to_csv(os.path.join(OUT, "realtime_verdicts.csv"), index=False)

print("\n" + "=" * 100)
print("FLIPPED ALARMS ON THE AVAILABILITY CLOCK (when an operator could first have seen them)")
print("=" * 100)
lead_rows = []
for sig in SIGNALS:
    for scope in SCOPES:
        e1 = alarms(res[(sig, scope, "fwd_1m")][1], "1m")
        e3 = alarms(res[(sig, scope, "fwd_3m")][1], "3m")
        print(f"\n--- {sig} / {scope} ---")
        print(f"  fwd_1m alarms ({len(e1)}): " + ", ".join(f"{a}..{b}({n}m)" for a, b, n in e1))
        print(f"  fwd_3m alarms ({len(e3)}): " + ", ".join(f"{a}..{b}({n}m)" for a, b, n in e3))
        # match each 3m alarm to the nearest preceding-or-equal 1m alarm start
        for a3, b3, n3 in e3:
            cands = [a1 for a1, b1, n1 in e1 if a1 <= b3 and b1 >= a3 - 12]
            if cands:
                a1 = min(cands)
                lead = (a3 - a1).n
                lead_rows.append(dict(signal=sig, scope=scope, alarm_3m=str(a3),
                                      alarm_1m=str(a1), lead_months=lead))
                print(f"    3m alarm {a3}  <- 1m first flagged {a1}  = LEAD {lead} months")
            else:
                lead_rows.append(dict(signal=sig, scope=scope, alarm_3m=str(a3),
                                      alarm_1m=None, lead_months=None))
                print(f"    3m alarm {a3}  <- NO matching 1m alarm (MISS)")
        # 1m alarms with no 3m confirmation within 12m = false positives
        fp = [a1 for a1, b1, n1 in e1 if not any(a3 <= b1 + 12 and a3 >= a1 - 1 for a3, b3, n3 in e3)]
        print(f"    FALSE POSITIVES (1m alarm never confirmed by a 3m alarm within 12m): "
              f"{len(fp)}/{len(e1)}" + (" -> " + ", ".join(str(x) for x in fp) if fp else ""))

ld = pd.DataFrame(lead_rows)
ld.to_csv(os.path.join(OUT, "flip_lead_times.csv"), index=False)
print("\n" + "=" * 100)
print("LEAD-TIME SUMMARY (months the fwd-1M indicator fired before the fwd-3M one)")
print("=" * 100)
print(ld.to_string(index=False))
good = ld["lead_months"].dropna()
if len(good):
    print(f"\n  n matched alarms = {len(good)}   median lead = {good.median():.1f}m   "
          f"mean = {good.mean():.1f}m   range = [{good.min():.0f}, {good.max():.0f}]")
print(f"  MECHANICAL floor: publication lag differs by 3-1 = 2 months by construction.")

# current reading
print("\n" + "=" * 100)
print("LATEST READING (both clocks)")
print("=" * 100)
for sig in SIGNALS:
    for scope in SCOPES:
        for fwd in ("fwd_1m", "fwd_3m"):
            ic, v = res[(sig, scope, fwd)]
            if not len(v): continue
            r = v.iloc[-1]
            print(f"  {sig:9s} {scope:9s} {fwd}: avail={r.avail_month} sig_month={r.sig_month} "
                  f"full={r.full:+.4f} recent12={r.recent:+.4f} t={r.tstat:+.2f} -> {r.verdict}")
