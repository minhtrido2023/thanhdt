#!/usr/bin/env python
"""CAU A diagnostic — is the FSCORE entry leg doing REAL screening work, or just shrinking
the basket (fewer names => less dilution => flattering average)?

The clean test: take the names V1_nofscore ADDS (i.e. the names FSCORE>=6 EXCLUDES) and compare
their own 60-session forward return against the names both variants KEEP. If FSCORE is noise,
the excluded names should return the same as the kept ones. Basket size is irrelevant to this
comparison — it is a name-level test, not an average-of-averages test.

Also splits by FSCORE bucket (name-level IC of the raw score inside the CAPIT-eligible pool).
"""
import os
import sys

import numpy as np
import pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.environ["BQ_LOCAL_CACHE"] = os.path.join(WORKDIR, "data", "bq_cache_asof20260729_postrestate")
os.environ.setdefault("BQ_CACHE_THREADS", "1")
from bq_local_cache import get_cache  # noqa: E402

CACHE = get_cache()
OUT = os.path.join(WORKDIR, "data", "fscore_review_20260801")
HOLD = 60


def q(sql):
    return CACHE.query(sql)


ev = pd.read_csv(os.path.join(WORKDIR, "data", "capit_qexit_20260801", "event_rollup.csv"))
EVENTS = [pd.Timestamp(d) for d in ev["date"]]
cal = q("SELECT DISTINCT t.time FROM tav2_bq.ticker_prune AS t "
        "WHERE t.ticker='VNM' AND t.time >= DATE '2014-01-01' ORDER BY t.time")
CAL = list(pd.to_datetime(cal["time"]))

# ---- full CAPIT-eligible pool per event (ROE/ROIC/liq floor only — the FSCORE-agnostic universe)
pool = []
for i, d in enumerate(EVENTS):
    e = q(f"""SELECT p.ticker, p.ICB_Code, p.FSCORE,
  SAFE_DIVIDE(p.PB-p.PB_MA5Y,p.PB_SD5Y) pbz, COALESCE(p.Price,p.Close)*p.Volume/1e9 liq
FROM tav2_bq.ticker_prune p WHERE p.time = DATE '{d.date()}'
  AND p.ROE_Min5Y>=0.12 AND p.ROIC5Y>=0.10 AND COALESCE(p.Price,p.Close)*p.Volume/1e9 >= 2""")
    e["event"] = i
    e["date"] = d
    pool.append(e)
pool = pd.concat(pool, ignore_index=True)
print(f"[pool] {len(pool)} (event,name) cells across {len(EVENTS)} events, "
      f"FSCORE populated {pool['FSCORE'].notna().mean()*100:.1f}%")

# ---- forward returns for the whole pool
allnames = sorted(pool["ticker"].unique())
inlist = ",".join(f"'{t}'" for t in allnames)
px = q(f"""SELECT p.ticker, p.time, p.Open FROM tav2_bq.ticker_prune p
WHERE p.ticker IN ({inlist}) AND p.time >= DATE '2014-01-01'""")
px["time"] = pd.to_datetime(px["time"])
PX = {t: g.set_index("time").sort_index()["Open"] for t, g in px.groupby("ticker")}


def fwd(t, d):
    g = PX.get(t)
    if g is None:
        return np.nan
    i0 = CAL.index(d)
    de, dx = CAL[i0 + 1], CAL[min(i0 + 1 + HOLD, len(CAL) - 1)]
    if de not in g.index or dx not in g.index:
        return np.nan
    p0, p1 = g[de], g[dx]
    return float(p1 / p0 - 1.0) if (p0 > 0 and p1 > 0) else np.nan


pool["ret"] = [fwd(t, d) for t, d in zip(pool["ticker"], pool["date"])]
pool = pool[pool["ret"].notna()].copy()
pool.to_csv(os.path.join(OUT, "eligible_pool.csv"), index=False)

# ---- the actual selected baskets (need the pb_z ladder, since only SELECTED names get bought)
comp = pd.read_csv(os.path.join(OUT, "basket_composition.csv"))
sel = {(r["event"], r["variant"]): set(x for x in str(r["names"]).split(",") if x)
       for _, r in comp.iterrows()}

kept, added, dropped = [], [], []
for i in range(len(EVENTS)):
    a, b = sel[(i, "V0_prod")], sel[(i, "V1_nofscore")]
    sub = pool[pool["event"] == i].set_index("ticker")
    for t in (a & b):
        if t in sub.index:
            kept.append(sub.loc[t, "ret"])
    for t in (b - a):
        if t in sub.index:
            added.append(sub.loc[t, "ret"])
    for t in (a - b):
        if t in sub.index:
            dropped.append(sub.loc[t, "ret"])

print("\n" + "=" * 78)
print("NAME-LEVEL: names FSCORE>=6 EXCLUDES vs names it KEEPS (size-confound removed)")
print("=" * 78)
for lbl, v in (("KEPT by both (FSCORE>=6, selected in prod)", kept),
               ("ADDED when FSCORE dropped (= names FSCORE excludes)", added),
               ("DROPPED when FSCORE dropped (pb_z-ladder shuffle)", dropped)):
    v = np.array(v)
    if len(v):
        print(f"  {lbl:<52} n={len(v):>3}  mean {v.mean()*100:>+6.2f}%  "
              f"median {np.median(v)*100:>+6.2f}%  win {(v>0).mean()*100:>4.1f}%")
    else:
        print(f"  {lbl:<52} n=0")

k, a = np.array(kept), np.array(added)
if len(k) and len(a):
    diff = k.mean() - a.mean()
    rng = np.random.default_rng(7)
    boot = [rng.choice(k, len(k)).mean() - rng.choice(a, len(a)).mean() for _ in range(10000)]
    lo, hi = np.percentile(boot, [5, 95])
    print(f"\n  KEPT - ADDED = {diff*100:+.2f}pp   bootstrap CI90 [{lo*100:+.2f}, {hi*100:+.2f}]pp   "
          f"P(diff<=0) = {np.mean(np.array(boot) <= 0):.3f}")

# ---- raw FSCORE -> forward return, inside the CAPIT-eligible pool (is the score monotone?)
print("\n" + "=" * 78)
print("FSCORE bucket -> 60-session forward return, INSIDE the CAPIT-eligible pool (all names)")
print("=" * 78)
p = pool[pool["FSCORE"].notna()].copy()
p["bucket"] = pd.cut(p["FSCORE"], [-.1, 3.5, 4.5, 5.5, 6.5, 7.5, 9.1],
                     labels=["<=3", "4", "5", "6", "7", "8-9"])
g = p.groupby("bucket", observed=True)["ret"].agg(["count", "mean", "median",
                                                   lambda s: (s > 0).mean()])
g.columns = ["n", "mean", "median", "win"]
for b, r in g.iterrows():
    print(f"  FSCORE {str(b):>4}: n={int(r['n']):>3}  mean {r['mean']*100:>+6.2f}%  "
          f"median {r['median']*100:>+6.2f}%  win {r['win']*100:>4.1f}%")
print(f"\n  >=6 vs <6 : {p[p.FSCORE>=6]['ret'].mean()*100:+.2f}% (n={len(p[p.FSCORE>=6])}) vs "
      f"{p[p.FSCORE<6]['ret'].mean()*100:+.2f}% (n={len(p[p.FSCORE<6])})")

# per-event Spearman IC of FSCORE inside the pool
ics = []
for i, gg in p.groupby("event"):
    if len(gg) >= 8:
        ics.append(gg["FSCORE"].corr(gg["ret"], method="spearman"))
ics = np.array([x for x in ics if not np.isnan(x)])
print(f"  per-event Spearman IC(FSCORE, fwd60) inside pool: mean {ics.mean():+.3f}  "
      f"n_events={len(ics)}  hit {(ics>0).mean()*100:.0f}%  "
      f"t={ics.mean()/(ics.std(ddof=1)/np.sqrt(len(ics))):+.2f}")
print(f"\n[written] {OUT}/eligible_pool.csv")
