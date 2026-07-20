# -*- coding: utf-8 -*-
"""PANEL B — washout-event portfolio test (N=14, LOW POWER, directional reference only)
plus STRUCTURAL BOUND: how much can ANY change of ranking metric move the basket at all?
"""
import os, sys, io
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
px = con.execute(f"SELECT ticker, time, Close FROM {PRUNE}").df()
px["time"] = pd.to_datetime(px["time"])
P = px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index()
def fwd(tk, d, h):
    if tk not in P.columns: return np.nan
    s = P[tk].dropna(); s = s[s.index >= pd.Timestamp(d)]
    if len(s) < 2: return np.nan
    return s.iloc[min(h, len(s)-1)] / s.iloc[0] - 1

fin = D._load_financials()
rows = []
for d in EVENTS:
    e = con.execute(f"""SELECT ticker, (PB-PB_MA5Y)/NULLIF(PB_SD5Y,0) pbz, COALESCE(Price,Close) px
FROM {PRUNE} WHERE time = DATE '{d}' AND ROE_Min5Y>=0.12 AND ROIC5Y>=0.10 AND FSCORE>=6
  AND COALESCE(Price,Close)*Volume/1e9 >= 2""").df().dropna(subset=["pbz"])
    for _, r in e.iterrows():
        try:
            res = D.fair_value(r.ticker, d, price=float(r.px), fin=fin)
            mos = res.get("margin_of_safety") if res.get("ok") else np.nan
        except Exception:
            mos = np.nan
        rows.append({"event": d, "ticker": r.ticker, "pbz": float(r.pbz), "mos": mos,
                     **{f"r{h}": fwd(r.ticker, d, h) for h in (60, 120, 250)}})
E = pd.DataFrame(rows)
E["mos"] = pd.to_numeric(E["mos"], errors="coerce")
E.to_csv("mike/agents/Taylor/exp_capitdcf/panelB_events.csv", index=False)

def prod_pool(g):
    """Production cascade: pb_z<-1 else pb_z<0 else all, capped at 15."""
    gg = g[g.pbz < -1]
    if len(gg) < 3: gg = g[g.pbz < 0]
    if len(gg) < 3: gg = g
    return gg.nsmallest(15, "pbz") if len(gg) > 15 else gg

print("=== STRUCTURAL BOUND — how much room does the ranking metric even have? ===")
print(f"{'event':<12}{'gated':>7}{'prod_pool':>11}{'K':>4}{'choice?':>9}{'max_swap':>10}")
tot_choice = 0
for d, g in E.groupby("event"):
    pool = prod_pool(g)
    choice = len(pool) > K
    tot_choice += choice
    print(f"{d:<12}{len(g):>7}{len(pool):>11}{K:>4}{str(choice):>9}{max(0,min(len(pool)-K,K)):>10}")
print(f"\n  events where ranking metric changes ANYTHING: {tot_choice}/{len(EVENTS)} "
      f"(elsewhere pool <= K, basket = whole pool regardless of metric)")

def select(g, variant):
    pool = prod_pool(g)
    if variant == "base":
        return pool.sort_values(["pbz", "ticker"], kind="mergesort").head(K)
    if variant == "dcf_pool":     # DCF ranks WITHIN the production pb_z-filtered pool
        p = pool.copy(); p["key"] = p["mos"].fillna(p["mos"].median())
        return p.sort_values(["key", "ticker"], ascending=[False, True], kind="mergesort").head(K)
    if variant == "dcf_full":     # DCF replaces pb_z entirely: rank the full gated universe
        p = g.copy(); p["key"] = p["mos"].fillna(p["mos"].median())
        return p.sort_values(["key", "ticker"], ascending=[False, True], kind="mergesort").head(K)
    raise ValueError(variant)

print("\n=== PANEL B — basket forward return by variant (N=14 events, LOW POWER) ===")
for h in (60, 120, 250):
    ser = {v: pd.Series({d: select(g, v)[f"r{h}"].mean() for d, g in E.groupby("event")})
           for v in ("base", "dcf_pool", "dcf_full")}
    print(f"\n-- h={h} sessions --")
    print(f"  {'variant':<10}{'mean':>9}{'median':>9}{'hit':>7}")
    for v, s in ser.items():
        print(f"  {v:<10}{s.mean():>9.4f}{s.median():>9.4f}{(s>0).mean():>7.2f}")
    b = ser["base"]
    for v in ("dcf_pool", "dcf_full"):
        dl = (ser[v] - b).dropna()
        t = dl.mean()/(dl.std(ddof=1)/np.sqrt(len(dl))) if dl.std(ddof=1) > 0 else np.nan
        # leave-one-event-out
        loo = {e: dl.drop(e).mean() for e in dl.index}
        worst, best = min(loo, key=loo.get), max(loo, key=loo.get)
        print(f"   {v}-base delta={dl.mean():+.4f} t={t:+.2f} n={len(dl)} | "
              f"LOO range [{loo[best]:+.4f} drop {best} .. {loo[worst]:+.4f} drop {worst}]")
