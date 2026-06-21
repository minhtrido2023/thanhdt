#!/usr/bin/env python3
"""
analyze_earnings_reaction.py
=============================
Phân tích phản ứng giá cổ phiếu quanh ngày ra báo cáo tài chính.

Mục tiêu: phân loại từng (ticker, release_date) event thành 1 trong các pattern:
  LEAK_RUNUP_POS    : Good earnings + run-up trước + drop sau   (insider leak)
  LEAK_DUMP_NEG     : Bad earnings + drop trước + rebound sau   (insider leak phía bán)
  EFFICIENT_POS     : Good + ít pre-move + jump on release      (efficient up)
  EFFICIENT_NEG     : Bad  + ít pre-move + drop on release      (efficient down)
  LAGGED_POS        : Good + ít pre-move + ít release + drift up sau
  LAGGED_NEG        : Bad  + ít pre-move + ít release + drift down sau
  NOISE             : Không khớp pattern nào

Sau đó aggregate per-ticker → reaction profile để dùng làm yếu tố định giá:
  - High LEAK_RUNUP_POS freq  → tránh buy trước release
  - High LAGGED_POS freq      → có alpha window mua sau release (T+5 to T+30)
  - High EFFICIENT freq       → trade FA bình thường, không cần wait

Window:
  pre  = Close(T-1) / Close(T-30) - 1
  rel  = Close(T+5) / Close(T-1)  - 1
  post = Close(T+30) / Close(T+5) - 1

Earnings strength:
  GOOD = NP_R ≥ 15% (NP YoY > 15%)
  BAD  = NP_R ≤ -15%
  MID  = else
"""
import warnings; warnings.filterwarnings("ignore")
import os, subprocess, tempfile, sys, pickle
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import pandas as pd, numpy as np

PROJECT = "lithe-record-440915-m9"
BQ = r"bq"

def bq_query(sql):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        cmd = f'type "{tmp}" | "{BQ}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=10000000'
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800, shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    if r.returncode != 0: raise RuntimeError(r.stderr[:500])
    return pd.read_csv(StringIO(r.stdout.strip()))

# ─── 1. Pull release events ──────────────────────────────────────────────
ev_cache = "data/earnings_events.pkl"
if os.path.exists(ev_cache):
    with open(ev_cache,"rb") as f: ev = pickle.load(f)
    print(f"[1] Loaded events cache: {len(ev):,} events")
else:
    print("[1] Pulling release events from BQ ...")
    ev = bq_query("""
    SELECT f.ticker, f.quarter, f.Release_Date, f.NP_R, f.Revenue_YoY_P0, f.NP_P0, f.NP_P4
    FROM tav2_bq.ticker_financial AS f
    WHERE f.Release_Date IS NOT NULL
      AND f.Release_Date >= '2009-01-01'
      AND f.NP_R IS NOT NULL
    """)
    ev["Release_Date"] = pd.to_datetime(ev["Release_Date"])
    with open(ev_cache,"wb") as f: pickle.dump(ev, f)
    print(f"  Pulled {len(ev):,} events from {ev['ticker'].nunique()} tickers")

# ─── 2. Pull daily prices (Close only) for tickers in events ─────────────
px_cache = "data/earnings_px.pkl"
if os.path.exists(px_cache):
    with open(px_cache,"rb") as f: px = pickle.load(f)
    print(f"[2] Loaded price cache: {len(px):,} rows")
else:
    print("[2] Pulling daily Close for all event tickers (2009-2026) ...")
    tks = ev["ticker"].unique()
    print(f"  {len(tks)} tickers")
    px = bq_query("""
    SELECT t.ticker, t.time, t.Close
    FROM tav2_bq.ticker AS t
    WHERE t.time >= '2008-12-01' AND t.Close > 0
    """)
    px["time"] = pd.to_datetime(px["time"])
    px = px[px["ticker"].isin(tks)]
    with open(px_cache,"wb") as f: pickle.dump(px, f)
    print(f"  Pulled + cached: {len(px):,} rows")

px_piv = px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index()
# Use business-day forward fill for missing days (preserve event-day lookup)
px_piv = px_piv.ffill(limit=5)
print(f"  Pivot: {len(px_piv)} days × {len(px_piv.columns)} tickers")

# ─── 3. Compute pre/release/post returns per event ───────────────────────
print("\n[3] Computing event windows ...")
all_dates = px_piv.index
all_dates_arr = np.array(all_dates)

def get_close(tk, dt):
    if tk not in px_piv.columns: return np.nan
    # find nearest trading day on or before dt
    pos = np.searchsorted(all_dates_arr, np.datetime64(dt), side="right") - 1
    if pos < 0: return np.nan
    return px_piv.iloc[pos][tk]

def get_close_offset(tk, ref_dt, offset_days):
    """Nearest trading day at ref_dt + offset business days. offset_days can be negative."""
    if tk not in px_piv.columns: return np.nan, None
    ref = np.datetime64(ref_dt)
    pos_ref = np.searchsorted(all_dates_arr, ref, side="right") - 1
    if pos_ref < 0: return np.nan, None
    target_pos = pos_ref + offset_days
    if target_pos < 0 or target_pos >= len(all_dates_arr): return np.nan, None
    return px_piv.iloc[target_pos][tk], all_dates_arr[target_pos]

results = []
n_total = len(ev)
for i, row in ev.iterrows():
    if i % 5000 == 0: print(f"  Event {i}/{n_total} ...", flush=True)
    tk = row["ticker"]; rdt = row["Release_Date"]
    if tk not in px_piv.columns: continue
    p_pre30, _    = get_close_offset(tk, rdt, -30)
    p_m1, _       = get_close_offset(tk, rdt, -1)
    p_p5, _       = get_close_offset(tk, rdt, +5)
    p_p30, _      = get_close_offset(tk, rdt, +30)
    if any(pd.isna(p) for p in [p_pre30, p_m1, p_p5, p_p30]): continue
    if min(p_pre30, p_m1, p_p5, p_p30) <= 0: continue
    pre_ret  = (p_m1 / p_pre30 - 1) * 100
    rel_ret  = (p_p5 / p_m1   - 1) * 100
    post_ret = (p_p30/ p_p5   - 1) * 100
    results.append({
        "ticker": tk, "quarter": row["quarter"], "Release_Date": rdt,
        "NP_R": row["NP_R"]*100 if pd.notna(row["NP_R"]) else np.nan,
        "Rev_YoY": row["Revenue_YoY_P0"]*100 if pd.notna(row["Revenue_YoY_P0"]) else np.nan,
        "pre_ret": pre_ret, "rel_ret": rel_ret, "post_ret": post_ret,
    })

evdf = pd.DataFrame(results)
print(f"\n  Processed events with full windows: {len(evdf):,}")

# ─── 4. Classify pattern per event ───────────────────────────────────────
def classify(row):
    npr = row["NP_R"]
    if pd.isna(npr): return "NO_NPR"
    pre, rel, post = row["pre_ret"], row["rel_ret"], row["post_ret"]
    good = npr >= 15
    bad  = npr <= -15

    if good:
        if pre >= 10 and rel <= -2:                      return "LEAK_RUNUP_POS"
        if abs(pre) < 5 and rel >= 3:                    return "EFFICIENT_POS"
        if abs(pre) < 5 and abs(rel) < 3 and post >= 5:  return "LAGGED_POS"
        if pre >= 10 and rel >= 0 and post < 0:          return "LEAK_RUNUP_POS"  # variant
    if bad:
        if pre <= -10 and rel >= 2:                      return "LEAK_DUMP_NEG"
        if abs(pre) < 5 and rel <= -3:                   return "EFFICIENT_NEG"
        if abs(pre) < 5 and abs(rel) < 3 and post <= -5: return "LAGGED_NEG"
    return "NOISE"

evdf["pattern"] = evdf.apply(classify, axis=1)
print("\n[4] Pattern distribution (all events):")
dist = evdf["pattern"].value_counts()
for p, n in dist.items():
    print(f"  {p:<20}: {n:>6,}  ({n/len(evdf)*100:.1f}%)")

# ─── 5. Per-ticker reaction profile ──────────────────────────────────────
print("\n[5] Building per-ticker profile (≥8 events)...")
prof = evdf.groupby("ticker").agg(
    n_events=("ticker","size"),
    n_good=("NP_R", lambda x: (x>=15).sum()),
    n_bad =("NP_R", lambda x: (x<=-15).sum()),
    avg_pre_good =("pre_ret",  lambda x: x[evdf.loc[x.index,"NP_R"]>=15].mean()),
    avg_rel_good =("rel_ret",  lambda x: x[evdf.loc[x.index,"NP_R"]>=15].mean()),
    avg_post_good=("post_ret", lambda x: x[evdf.loc[x.index,"NP_R"]>=15].mean()),
    avg_pre_bad  =("pre_ret",  lambda x: x[evdf.loc[x.index,"NP_R"]<=-15].mean()),
    avg_rel_bad  =("rel_ret",  lambda x: x[evdf.loc[x.index,"NP_R"]<=-15].mean()),
    avg_post_bad =("post_ret", lambda x: x[evdf.loc[x.index,"NP_R"]<=-15].mean()),
)
for p in ["LEAK_RUNUP_POS","EFFICIENT_POS","LAGGED_POS",
          "LEAK_DUMP_NEG","EFFICIENT_NEG","LAGGED_NEG","NOISE"]:
    prof[f"freq_{p}"] = evdf[evdf["pattern"]==p].groupby("ticker").size()
    prof[f"freq_{p}"] = prof[f"freq_{p}"].fillna(0) / prof["n_events"] * 100

prof = prof[prof["n_events"] >= 8].copy()
print(f"  Tickers with ≥8 events: {len(prof)}")

# Profile score: -1=Leak, 0=Noise, +1=Efficient/Lagged
prof["leak_score"]      = prof["freq_LEAK_RUNUP_POS"] + prof["freq_LEAK_DUMP_NEG"]
prof["efficient_score"] = prof["freq_EFFICIENT_POS"]  + prof["freq_EFFICIENT_NEG"]
prof["lagged_score"]    = prof["freq_LAGGED_POS"]     + prof["freq_LAGGED_NEG"]

# ─── 6. Top tickers per pattern ──────────────────────────────────────────
print("\n" + "="*100)
print("  TOP 25 INSIDER-LEAK PRONE (high leak_score)")
print("="*100)
print(f"  {'Ticker':<7}{'N':>4}{'good':>6}{'bad':>6}{'leak%':>7}{'eff%':>7}{'lag%':>7}{'pre_g':>8}{'rel_g':>8}{'post_g':>8}")
for tk, r in prof.sort_values("leak_score", ascending=False).head(25).iterrows():
    print(f"  {tk:<7}{int(r['n_events']):>4}{int(r['n_good']):>6}{int(r['n_bad']):>6}"
          f"{r['leak_score']:>+7.1f}{r['efficient_score']:>+7.1f}{r['lagged_score']:>+7.1f}"
          f"{r['avg_pre_good']:>+7.1f}%{r['avg_rel_good']:>+7.1f}%{r['avg_post_good']:>+7.1f}%")

print("\n" + "="*100)
print("  TOP 25 LAGGED-REACTION (high lagged_score) — ALPHA WINDOW after release")
print("="*100)
print(f"  {'Ticker':<7}{'N':>4}{'good':>6}{'bad':>6}{'leak%':>7}{'eff%':>7}{'lag%':>7}{'pre_g':>8}{'rel_g':>8}{'post_g':>8}")
for tk, r in prof.sort_values("lagged_score", ascending=False).head(25).iterrows():
    print(f"  {tk:<7}{int(r['n_events']):>4}{int(r['n_good']):>6}{int(r['n_bad']):>6}"
          f"{r['leak_score']:>+7.1f}{r['efficient_score']:>+7.1f}{r['lagged_score']:>+7.1f}"
          f"{r['avg_pre_good']:>+7.1f}%{r['avg_rel_good']:>+7.1f}%{r['avg_post_good']:>+7.1f}%")

print("\n" + "="*100)
print("  TOP 25 EFFICIENT-REACTION (price matches earnings on release)")
print("="*100)
print(f"  {'Ticker':<7}{'N':>4}{'good':>6}{'bad':>6}{'leak%':>7}{'eff%':>7}{'lag%':>7}{'pre_g':>8}{'rel_g':>8}{'post_g':>8}")
for tk, r in prof.sort_values("efficient_score", ascending=False).head(25).iterrows():
    print(f"  {tk:<7}{int(r['n_events']):>4}{int(r['n_good']):>6}{int(r['n_bad']):>6}"
          f"{r['leak_score']:>+7.1f}{r['efficient_score']:>+7.1f}{r['lagged_score']:>+7.1f}"
          f"{r['avg_pre_good']:>+7.1f}%{r['avg_rel_good']:>+7.1f}%{r['avg_post_good']:>+7.1f}%")

# ─── 7. Aggregate stats: which pattern has best forward alpha? ───────────
print("\n" + "="*100)
print("  PATTERN-LEVEL AVERAGE RETURNS (all events)")
print("="*100)
print(f"  {'Pattern':<20}{'N':>6}{'avg_pre':>10}{'avg_rel':>10}{'avg_post':>10}{'total':>10}")
for pat, g in evdf.groupby("pattern"):
    avg_pre = g["pre_ret"].mean(); avg_rel = g["rel_ret"].mean(); avg_post = g["post_ret"].mean()
    total = avg_pre + avg_rel + avg_post
    print(f"  {pat:<20}{len(g):>6}{avg_pre:>+9.2f}%{avg_rel:>+9.2f}%{avg_post:>+9.2f}%{total:>+9.2f}%")

# ─── 8. Save outputs ─────────────────────────────────────────────────────
evdf.to_csv("data/earnings_events_classified.csv", index=False)
prof.to_csv("data/ticker_reaction_profile.csv")
print("\nSaved: earnings_events_classified.csv (events), ticker_reaction_profile.csv (per-ticker)")
print(f"\nUse `ticker_reaction_profile.csv` as input factor for valuation models.")
