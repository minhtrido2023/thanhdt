#!/usr/bin/env python3
"""
tests_option_c.py
=================
Test 3 options to fix LH peak-reversal weakness:

  Option A: Trailing stop -25% / -30% / -35% from intra-hold peak
  Option B: LH score v2 with growth-direction gate (post-process tier demotion)
  Option C: Combine winning A + B variants

Validation:
  1) Full 50B canonical backtest 2014-2026
  2) 5-ticker lifecycle (VCS / DGC / VNM / FPT / MWG) — does the option exit at peak?
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np
from simulate_lh_nav import run_lh, compute_metrics, load_data, _CACHE

INIT_NAV = 50e9
PROBLEM_TICKERS = ["VCS", "DGC", "VNM", "FPT", "MWG"]

# ─── Generate LH score v2 (with growth gate) ─────────────────────────────
print("Generating LH ratings v2 (with growth-direction gate) ...")
r1 = pd.read_csv("fa_ratings_lh.csv", parse_dates=["time"])

# Pull NP_TTM and Revenue history for growth signal
import subprocess, tempfile
from io import StringIO

def bq(sql):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        cmd = f'type "{tmp}" | "C:\\Users\\hotro\\AppData\\Local\\Google\\Cloud SDK\\google-cloud-sdk\\bin\\bq.cmd" query --use_legacy_sql=false --project_id=lithe-record-440915-m9 --format=csv --max_rows=1000000'
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300, shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    return pd.read_csv(StringIO(r.stdout.strip()))

print("  Pulling growth indicators from BQ ...")
growth_data = bq("""
SELECT ticker, quarter, time,
  NP_P0+NP_P1+NP_P2+NP_P3 AS NP_TTM_now,
  NP_P4+NP_P5+NP_P6+NP_P7 AS NP_TTM_prv,
  Revenue_P0+Revenue_P1+Revenue_P2+Revenue_P3 AS Rev_TTM_now,
  Revenue_P4+Revenue_P5+Revenue_P6+Revenue_P7 AS Rev_TTM_prv
FROM tav2_bq.ticker_financial
WHERE time >= '2014-01-01'
""")
growth_data["time"] = pd.to_datetime(growth_data["time"])
growth_data["NP_growth_2Y"] = (growth_data["NP_TTM_now"] / growth_data["NP_TTM_prv"].abs().replace(0, np.nan) - 1).clip(-5, 5)
growth_data["Rev_growth_2Y"] = (growth_data["Rev_TTM_now"] / growth_data["Rev_TTM_prv"].abs().replace(0, np.nan) - 1).clip(-5, 5)

# Merge into ratings
r2 = r1.merge(growth_data[["ticker","quarter","NP_growth_2Y","Rev_growth_2Y"]],
              on=["ticker","quarter"], how="left")

# Growth-gate logic: if NP_TTM_growth_2Y < 0 AND Rev_growth_2Y < 5% → demote 1 tier
DEMOTE_MAP = {"A":"B", "B":"C", "C":"D", "D":"E", "E":"E"}
growth_failed = (r2["NP_growth_2Y"] < 0) & (r2["Rev_growth_2Y"] < 0.05)
r2["tier_v2"] = r2["tier"]
r2.loc[growth_failed, "tier_v2"] = r2.loc[growth_failed, "tier"].map(DEMOTE_MAP)

# Diagnostic: how often does the gate fire?
n_demoted = growth_failed.sum()
n_a_demoted = ((r2["tier"]=="A") & growth_failed).sum()
n_b_demoted = ((r2["tier"]=="B") & growth_failed).sum()
print(f"  Growth gate demoted {n_demoted}/{len(r2)} rows ({100*n_demoted/len(r2):.1f}%)")
print(f"  A→B demotions: {n_a_demoted}, B→C demotions: {n_b_demoted}")

# Save v2 ratings (overwrite tier column for downstream)
r2_save = r2.copy()
r2_save["tier"] = r2_save["tier_v2"]  # Use v2 tier
r2_save.drop(columns=["tier_v2"]).to_csv("fa_ratings_lh_v2.csv", index=False)

# Verify on problem tickers
print("\n  Tier changes on problem tickers:")
for tk in PROBLEM_TICKERS:
    sub = r2[r2["ticker"] == tk].sort_values("time")
    changed = sub[sub["tier"] != sub["tier_v2"]]
    if len(changed):
        print(f"    {tk}: {len(changed)}/{len(sub)} quarters demoted")
        # show first and last 3
        for _, row in changed.head(3).iterrows():
            print(f"      {row['quarter']:<8} {row['tier']} → {row['tier_v2']}  NP_g={row['NP_growth_2Y']:+.2f} Rev_g={row['Rev_growth_2Y']:+.2f}")
        if len(changed) > 6:
            print(f"      ...")
        for _, row in changed.tail(3).iterrows():
            print(f"      {row['quarter']:<8} {row['tier']} → {row['tier_v2']}  NP_g={row['NP_growth_2Y']:+.2f} Rev_g={row['Rev_growth_2Y']:+.2f}")
    else:
        print(f"    {tk}: no demotions")

# ─── BACKTEST VARIANTS ───────────────────────────────────────────────────
print("\n" + "="*100)
print("BACKTEST — Option A (trail stop), B (LH v2 score), C (combined)")
print("="*100)

# Common args (LH gated, A+B tier, staggered, 50B)
COMMON = dict(hold_quarters=4, n_positions=10, tier_set=("A","B"), incl_sub="all",
              refresh_mode="staggered", crisis_gate=True, init_nav=INIT_NAV)

VARIANTS = [
    ("BASELINE",   {"ratings_file": "fa_ratings_lh.csv",    "trail_pct": None}),
    ("A_trail25",  {"ratings_file": "fa_ratings_lh.csv",    "trail_pct": 0.25}),
    ("A_trail30",  {"ratings_file": "fa_ratings_lh.csv",    "trail_pct": 0.30}),
    ("A_trail35",  {"ratings_file": "fa_ratings_lh.csv",    "trail_pct": 0.35}),
    ("B_v2score",  {"ratings_file": "fa_ratings_lh_v2.csv", "trail_pct": None}),
    ("C_v2+t25",   {"ratings_file": "fa_ratings_lh_v2.csv", "trail_pct": 0.25}),
    ("C_v2+t30",   {"ratings_file": "fa_ratings_lh_v2.csv", "trail_pct": 0.30}),
    ("C_v2+t35",   {"ratings_file": "fa_ratings_lh_v2.csv", "trail_pct": 0.35}),
]

results = {}
for label, cfg in VARIANTS:
    print(f"\n→ {label} (ratings={cfg['ratings_file']}, trail={cfg['trail_pct']})")
    # Swap ratings file by temp renaming
    if cfg["ratings_file"] != "fa_ratings_lh.csv":
        if os.path.exists("fa_ratings_lh.csv"):
            os.rename("fa_ratings_lh.csv", "fa_ratings_lh.csv.bak")
        os.rename(cfg["ratings_file"], "fa_ratings_lh.csv")
    _CACHE.clear()  # force reload with new ratings
    try:
        res = run_lh(**COMMON, trail_pct=cfg["trail_pct"])
        results[label] = res
    finally:
        # restore
        if cfg["ratings_file"] != "fa_ratings_lh.csv":
            os.rename("fa_ratings_lh.csv", cfg["ratings_file"])
            if os.path.exists("fa_ratings_lh.csv.bak"):
                os.rename("fa_ratings_lh.csv.bak", "fa_ratings_lh.csv")

# ─── METRICS ─────────────────────────────────────────────────────────────
periods = [
    ("FULL 2014-2026", pd.Timestamp("2014-04-01"), pd.Timestamp("2026-05-13")),
    ("OOS_2024+",      pd.Timestamp("2024-01-01"), pd.Timestamp("2026-05-13")),
    ("Y2022_crash",    pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
    ("Q1_2026",        pd.Timestamp("2025-12-30"), pd.Timestamp("2026-03-30")),
]

def metrics_window(nav, start, end):
    s = nav[(nav.index >= start) & (nav.index <= end)]
    if len(s) < 30: return None
    nav_v = INIT_NAV * s / s.iloc[0]
    return compute_metrics(nav_v, start, end)

print("\n" + "="*120)
print("LH STANDALONE RESULTS (50B, A+B staggered, CRISIS gated)")
print("="*120)

for pname, ps, pe in periods:
    print(f"\n─── {pname} ───")
    print(f"  {'Variant':<14}{'CAGR':>10}{'Sharpe':>10}{'MaxDD':>10}{'Calmar':>10}{'trail_exits':>13}")
    for label, _ in VARIANTS:
        res = results[label]
        m = metrics_window(res["nav"]["nav"], ps, pe)
        if m is None: continue
        trades_in_win = res["trades"][(pd.to_datetime(res["trades"]["dt"]) >= ps) & (pd.to_datetime(res["trades"]["dt"]) <= pe)] if len(res["trades"]) > 0 else pd.DataFrame()
        n_trail = (trades_in_win["side"] == "TRAIL_STOP").sum() if len(trades_in_win) > 0 else 0
        print(f"  {label:<14}{m['CAGR']:>+10.2%}{m['Sharpe']:>+10.2f}{m['MaxDD']:>+10.2%}{m['Calmar']:>+10.2f}{n_trail:>13}")

# ─── 5-TICKER LIFECYCLE ──────────────────────────────────────────────────
print("\n" + "="*120)
print("5-TICKER LIFECYCLE — Did the variant exit each peak-reversal stock?")
print("="*120)

prices = pd.read_csv("prices_lh.csv", parse_dates=["time"])

for tk in PROBLEM_TICKERS:
    print(f"\n─── {tk} ───")
    p = prices[prices["ticker"] == tk].sort_values("time")
    peak_dt = p.loc[p["Close"].idxmax(), "time"]
    print(f"  Peak: {p['Close'].max():.0f} on {peak_dt.date()}")

    for label, _ in VARIANTS:
        res = results[label]
        # Find trades for this ticker
        tk_trades = res["trades"][res["trades"]["ticker"] == tk] if len(res["trades"]) > 0 else pd.DataFrame()
        if len(tk_trades) == 0:
            print(f"  {label:<14}  (no trades — not picked)")
            continue
        buys = tk_trades[tk_trades["side"] == "BUY"]
        sells = tk_trades[tk_trades["side"].isin(["SELL","TRAIL_STOP"])]
        first_buy = buys.iloc[0] if len(buys) else None
        last_sell = sells.iloc[-1] if len(sells) else None
        if first_buy is not None and last_sell is not None:
            entry_to_peak_days = (peak_dt - first_buy["dt"]).days
            exit_to_peak_days = (last_sell["dt"] - peak_dt).days
            print(f"  {label:<14}  buy {first_buy['dt'].strftime('%Y-%m-%d')} @ {first_buy['px']:.0f}  "
                  f"→ last_exit {last_sell['dt'].strftime('%Y-%m-%d')} @ {last_sell['px']:.0f}  "
                  f"(peak{exit_to_peak_days:+d}d) [{last_sell['side']}]")
        elif first_buy is not None:
            print(f"  {label:<14}  buy {first_buy['dt'].strftime('%Y-%m-%d')} @ {first_buy['px']:.0f}  → STILL HOLDING")

print("\nDONE")
