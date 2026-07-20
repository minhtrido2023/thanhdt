# -*- coding: utf-8 -*-
"""Stage 2 — POOL-level pre-registered variant comparison.
Rebuild the production-eligible CAPIT pool at each washout event, then simulate:
  (c) BASELINE : rank pb_z asc, take top-K            [control]
  (a) HARD     : drop DCF-RICH (mos<=0) from pool, then rank pb_z, top-K   [N/A = PASS]
  (b) SOFT     : rank pb_z, but sort RICH names last (stable), top-K       [N/A = PASS]
N_TRIALS PRE-REGISTERED = 3 (a, b, c). Horizons 60/120/250 sessions, all reported.
"""
import os, sys, io, pickle
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd, duckdb
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
import dcf_valuation as D

EVENTS = ['2014-05-08','2015-08-24','2016-01-18','2018-05-28','2020-03-12','2022-04-20',
          '2022-06-20','2022-09-29','2023-10-31','2024-04-19','2024-08-05','2025-04-03',
          '2025-10-20','2026-03-09']
K = 5
con = duckdb.connect(":memory:"); con.execute("SET threads=1")
PRUNE = f"read_parquet('{WORKDIR}/data/bq_cache/ticker_prune/*.parquet')"

def pool_at(d):
    """Exact production golden-path eligibility from capit_basket()."""
    q = f"""SELECT ticker, (PB-PB_MA5Y)/NULLIF(PB_SD5Y,0) pbz, COALESCE(Price,Close) px
FROM {PRUNE} WHERE time = DATE '{d}' AND ROE_Min5Y>=0.12 AND ROIC5Y>=0.10 AND FSCORE>=6
  AND COALESCE(Price,Close)*Volume/1e9 >= 2"""
    e = con.execute(q).df().dropna(subset=["pbz"])
    if e.empty: return e
    g = e[e.pbz < -1]; c = e[e.pbz < 0]
    pick = g if len(g) >= 3 else (c if len(c) >= 3 else e)
    return pick.nsmallest(15, "pbz").reset_index(drop=True)

# price panel for forward returns (adjusted Close)
px = con.execute(f"SELECT ticker, time, Close FROM {PRUNE}").df()
px["time"] = pd.to_datetime(px["time"])
P = px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index()
def fwd(tk, d, h):
    if tk not in P.columns: return np.nan
    s = P[tk].dropna(); s = s[s.index >= pd.Timestamp(d)]
    if len(s) < 2: return np.nan
    j = min(h, len(s) - 1)
    return s.iloc[j] / s.iloc[0] - 1

fin = D._load_financials()
recs = []
for d in EVENTS:
    pool = pool_at(d)
    if pool.empty: print(f"{d}: EMPTY pool"); continue
    for _, r in pool.iterrows():
        try:
            res = D.fair_value(r.ticker, d, price=float(r.px), fin=fin)
            mos = res.get("margin_of_safety") if res.get("ok") else np.nan
        except Exception:
            mos = np.nan
        recs.append({"event": d, "ticker": r.ticker, "pbz": r.pbz, "mos": mos,
                     **{f"r{h}": fwd(r.ticker, d, h) for h in (60, 120, 250)}})
X = pd.DataFrame(recs)
X["rich"] = X["mos"].notna() & (X["mos"] <= 0)
X.to_csv("mike/agents/Taylor/exp_capitdcf/pool_dcf.csv", index=False)
print(f"pool rows {len(X)} over {X.event.nunique()} events | "
      f"DCF computed {X.mos.notna().mean()*100:.0f}% | RICH share {X.rich.mean()*100:.0f}%")

def select(g, variant):
    g = g.sort_values(["pbz", "ticker"], kind="mergesort")   # stable, deterministic tie-break
    if variant == "base": return g.head(K)
    if variant == "hard":
        keep = g[~g.rich]
        return (keep if len(keep) >= 3 else g).head(K)       # min-3 fallback, never empty a basket
    if variant == "soft":
        return g.sort_values(["rich"], kind="mergesort").head(K)
    raise ValueError(variant)

print(f"\n=== Pre-registered variants (N_trials=3), K={K}, equal-weight basket ===")
out = {}
for h in (60, 120, 250):
    rows = []
    for v in ("base", "hard", "soft"):
        per_ev = {}
        for ev, g in X.groupby("event"):
            sel = select(g, v)
            per_ev[ev] = sel[f"r{h}"].mean()
        rows.append((v, pd.Series(per_ev)))
    out[h] = dict(rows)
    print(f"\n-- horizon {h} sessions --")
    print(f"{'variant':<8}{'mean':>9}{'median':>9}{'hit':>7}{'IS(<=2019)':>12}{'OOS(2020+)':>12}")
    for v, s in rows:
        isr = s[[e for e in s.index if e < '2020']].mean()
        oos = s[[e for e in s.index if e >= '2020']].mean()
        print(f"{v:<8}{s.mean():>9.4f}{s.median():>9.4f}{(s>0).mean():>7.2f}{isr:>12.4f}{oos:>12.4f}")
    b = rows[0][1]
    for v, s in rows[1:]:
        dlt = (s - b).dropna()
        t = dlt.mean()/(dlt.std(ddof=1)/np.sqrt(len(dlt))) if dlt.std(ddof=1) > 0 else np.nan
        rng = np.random.default_rng(11)
        bs = np.array([rng.choice(dlt.values, len(dlt), replace=True).mean() for _ in range(5000)])
        print(f"   {v}-base delta={dlt.mean():+.4f} t={t:+.2f} n_ev={len(dlt)} "
              f"CI95=[{np.percentile(bs,2.5):+.4f},{np.percentile(bs,97.5):+.4f}] "
              f"P(delta>0)={np.mean(bs>0):.2f}")
    # how often does the filter even change the basket?
    ch = sum(1 for ev, g in X.groupby("event")
             if set(select(g,'base').ticker) != set(select(g,'hard').ticker))
    print(f"   [hard changes basket in {ch}/{X.event.nunique()} events]")
pickle.dump(out, open("mike/agents/Taylor/exp_capitdcf/variant_series.pkl", "wb"))
