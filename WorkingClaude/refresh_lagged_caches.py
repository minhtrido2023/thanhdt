# -*- coding: utf-8 -*-
"""
refresh_lagged_caches.py
========================
Refresh the 4 LAGGED-leg caches that the paper-trade V12 sims depend on.

PROBLEM these caches fixed: the original builders (analyze_earnings_reaction.py,
backtest_lagged_pos.py, research_earnings_surprise.py) use a "load-if-exists,
never refresh" pattern — once the .pkl exists they are never re-pulled. So the
daily paper-trade window was frozen at the build date (2026-05-19), because
pt_dates.detect_end_date() caps END_DATE at the lagged_pos_ov.pkl max time.

This script (run as step 0 of papertrade_daily.bat) brings all 4 up to the
latest BQ ticker date:
  1. earnings_px.pkl            — daily Close (incremental append)
  2. lagged_pos_ov.pkl          — daily Open + Volume_3M_P50 (incremental append)
  3. earnings_surprise_data.pkl — quarterly NP_P0..P7 (full re-pull, cheap)
  4. earnings_events_classified.csv — recomputed pre/rel/post returns + pattern
     (raw events re-pulled, returns recomputed from the fresh px pivot)

All BQ access via simulate_holistic_nav.bq (same accessor the pt sims use), so
PATH/auth behave identically under the Windows scheduled task.
"""
import os, sys, io, pickle
import numpy as np, pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
from simulate_holistic_nav import bq

print("=" * 80)
print("  REFRESH LAGGED CACHES")
print("=" * 80)


def _save_pickle(obj, path):
    """Write atomically-ish; fall back to .new if locked (OneDrive/Excel).
    Force datetime64 → ns and StringDtype → object for cross-numpy compat."""
    obj = obj.copy()
    for c in obj.columns:
        if pd.api.types.is_datetime64_any_dtype(obj[c]):
            obj[c] = obj[c].astype("datetime64[ns]")   # us/ms → ns avoids NotImplementedError on older numpy
        elif hasattr(obj[c], "dtype") and str(obj[c].dtype) in ("string", "StringDtype"):
            obj[c] = obj[c].astype(object)
        elif isinstance(obj[c].dtype, pd.StringDtype):
            obj[c] = obj[c].astype(object)
    try:
        with open(path, "wb") as f: pickle.dump(obj, f)
        return path
    except PermissionError:
        alt = path.replace(".pkl", ".new.pkl")
        with open(alt, "wb") as f: pickle.dump(obj, f)
        print(f"  (locked, wrote {alt})")
        return alt


# ── 1. earnings_px.pkl — daily Close, incremental ──────────────────────────
print("\n[1] earnings_px.pkl (daily Close)...")
with open("data/earnings_px.pkl", "rb") as f: px = pickle.load(f)
px["time"] = pd.to_datetime(px["time"])
px_max = px["time"].max(); px_tks = set(px["ticker"].unique())
print(f"  current: {len(px):,} rows, max {px_max.date()}, {len(px_tks)} tickers")
new_px = bq(f"""SELECT t.ticker, t.time, t.Close FROM tav2_bq.ticker AS t
WHERE t.time > DATE '{px_max.date()}' AND t.Close > 0""")
if len(new_px):
    new_px["time"] = pd.to_datetime(new_px["time"])
    new_px = new_px[new_px["ticker"].isin(px_tks)]
    px = (pd.concat([px, new_px], ignore_index=True)
          .drop_duplicates(["ticker", "time"]).sort_values(["ticker", "time"]).reset_index(drop=True))
    _save_pickle(px, os.path.join(WORKDIR, "data/earnings_px.pkl"))
    print(f"  +{len(new_px):,} rows -> {len(px):,} total, new max {px['time'].max().date()}")
else:
    print("  already current, nothing to append")


# ── 2. lagged_pos_ov.pkl — daily Open + Volume_3M_P50, incremental ─────────
print("\n[2] lagged_pos_ov.pkl (Open + Volume_3M_P50)...")
with open("data/lagged_pos_ov.pkl", "rb") as f: ov = pickle.load(f)
ov["time"] = pd.to_datetime(ov["time"])
ov_max = ov["time"].max(); ov_tks = set(ov["ticker"].unique())
print(f"  current: {len(ov):,} rows, max {ov_max.date()}, {len(ov_tks)} tickers")
new_ov = bq(f"""SELECT t.ticker, t.time, t.Open, t.Volume_3M_P50 FROM tav2_bq.ticker AS t
WHERE t.time > DATE '{ov_max.date()}' AND t.Close > 0""")
if len(new_ov):
    new_ov["time"] = pd.to_datetime(new_ov["time"])
    new_ov = new_ov[new_ov["ticker"].isin(ov_tks)]
    ov = (pd.concat([ov, new_ov], ignore_index=True)
          .drop_duplicates(["ticker", "time"]).sort_values(["ticker", "time"]).reset_index(drop=True))
    _save_pickle(ov, os.path.join(WORKDIR, "data/lagged_pos_ov.pkl"))
    print(f"  +{len(new_ov):,} rows -> {len(ov):,} total, new max {ov['time'].max().date()}")
else:
    print("  already current, nothing to append")


# ── 3. earnings_surprise_data.pkl — full re-pull (cheap, quarterly) ────────
print("\n[3] earnings_surprise_data.pkl (NP_P0..P7)...")
fin = bq("""SELECT f.ticker, f.quarter, f.time, f.Release_Date,
       f.NP_P0, f.NP_P1, f.NP_P2, f.NP_P3, f.NP_P4, f.NP_P5, f.NP_P6, f.NP_P7,
       f.NP_R, f.Revenue_YoY_P0
FROM tav2_bq.ticker_financial AS f
WHERE f.Release_Date IS NOT NULL AND f.Release_Date >= '2009-01-01' AND f.NP_P0 IS NOT NULL""")
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])
fin["time"] = pd.to_datetime(fin["time"])
_save_pickle(fin, os.path.join(WORKDIR, "data/earnings_surprise_data.pkl"))
print(f"  re-pulled {len(fin):,} events, Release_Date max {fin['Release_Date'].max().date()}")


# ── 4. earnings_events_classified.csv — recompute from fresh px ────────────
print("\n[4] earnings_events_classified.csv (recompute pre/rel/post)...")
ev = bq("""SELECT f.ticker, f.quarter, f.Release_Date, f.NP_R, f.Revenue_YoY_P0, f.NP_P0, f.NP_P4
FROM tav2_bq.ticker_financial AS f
WHERE f.Release_Date IS NOT NULL AND f.Release_Date >= '2009-01-01' AND f.NP_R IS NOT NULL""")
ev["Release_Date"] = pd.to_datetime(ev["Release_Date"])
_save_pickle(ev, os.path.join(WORKDIR, "data/earnings_events.pkl"))

px_piv = px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
all_dates_arr = np.array(px_piv.index)

def close_offset(tk, ref_dt, off):
    if tk not in px_piv.columns: return np.nan
    pos = np.searchsorted(all_dates_arr, np.datetime64(ref_dt), side="right") - 1
    if pos < 0: return np.nan
    tgt = pos + off
    if tgt < 0 or tgt >= len(all_dates_arr): return np.nan
    return px_piv.iloc[tgt][tk]

def classify(npr, pre, rel, post):
    if pd.isna(npr): return "NO_NPR"
    good, bad = npr >= 15, npr <= -15
    if good:
        if pre >= 10 and rel <= -2: return "LEAK_RUNUP_POS"
        if abs(pre) < 5 and rel >= 3: return "EFFICIENT_POS"
        if abs(pre) < 5 and abs(rel) < 3 and post >= 5: return "LAGGED_POS"
        if pre >= 10 and rel >= 0 and post < 0: return "LEAK_RUNUP_POS"
    if bad:
        if pre <= -10 and rel >= 2: return "LEAK_DUMP_NEG"
        if abs(pre) < 5 and rel <= -3: return "EFFICIENT_NEG"
        if abs(pre) < 5 and abs(rel) < 3 and post <= -5: return "LAGGED_NEG"
    return "NOISE"

rows = []
for _, r in ev.iterrows():
    tk, rdt = r["ticker"], r["Release_Date"]
    if tk not in px_piv.columns: continue
    p_pre30 = close_offset(tk, rdt, -30); p_m1 = close_offset(tk, rdt, -1)
    p_p5 = close_offset(tk, rdt, +5);     p_p30 = close_offset(tk, rdt, +30)
    if any(pd.isna(p) for p in [p_pre30, p_m1, p_p5, p_p30]): continue
    if min(p_pre30, p_m1, p_p5, p_p30) <= 0: continue
    pre = (p_m1/p_pre30 - 1)*100; rel = (p_p5/p_m1 - 1)*100; post = (p_p30/p_p5 - 1)*100
    npr = r["NP_R"]*100 if pd.notna(r["NP_R"]) else np.nan
    rows.append({"ticker": tk, "quarter": r["quarter"], "Release_Date": rdt,
                 "NP_R": npr, "Rev_YoY": r["Revenue_YoY_P0"]*100 if pd.notna(r["Revenue_YoY_P0"]) else np.nan,
                 "pre_ret": pre, "rel_ret": rel, "post_ret": post,
                 "pattern": classify(npr, pre, rel, post)})
evdf = pd.DataFrame(rows)
out_csv = os.path.join(WORKDIR, "data/earnings_events_classified.csv")
try:
    evdf.to_csv(out_csv, index=False)
except PermissionError:
    out_csv = out_csv.replace(".csv", ".new.csv"); evdf.to_csv(out_csv, index=False)
    print(f"  (locked, wrote {out_csv})")
print(f"  recomputed {len(evdf):,} events with full windows, "
      f"Release_Date max {evdf['Release_Date'].max().date()}")

print("\n" + "=" * 80)
print("  REFRESH COMPLETE")
print(f"  earnings_px max:    {px['time'].max().date()}")
print(f"  lagged_pos_ov max:  {ov['time'].max().date()}")
print(f"  surprise rel max:   {fin['Release_Date'].max().date()}")
print(f"  events_cls rel max: {evdf['Release_Date'].max().date()}")
print("=" * 80)
