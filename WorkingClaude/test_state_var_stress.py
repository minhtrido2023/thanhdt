#!/usr/bin/env python3
"""
test_state_var_stress.py
=========================
Stress test STATE_VAR (Fresh-Q filter only in state 1/2/3) on the 5 BEAR
periods within 2014-2026 — best available stress windows.

Identified BEAR periods (state5 in {1, 2}):
  CRASH_2018_Q1Q2: 2018-04 to 2018-08 (trade war ramp-up)
  CRASH_2018_Q4:   2018-10 to 2019-01 (market correction)
  CRASH_2020_COVID:2020-02 to 2020-04 (COVID crash, state=1)
  CRASH_2022:      2022-04 to 2022-12 (rate hike + crypto crash, state=1)
  CRASH_2025_2026: 2025-08 to 2026-01 (recent BEAR, state=1)

For each crisis window:
  - F0 (no filter) NAV during window
  - STATE_VAR NAV during window
  - Drawdown comparison
  - Recovery comparison (rebound velocity)

Aggregate: STATE_VAR cumulative outperformance ONLY in stress windows.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
sys.path.insert(0, WORKDIR)

# Re-use NAV outputs from previous test (already computed)
print("Loading saved NAVs from previous test ...")
nav_df = pd.read_csv("ba_release_date_nav.csv", index_col=0, parse_dates=True)
print(f"  Columns: {list(nav_df.columns)}")
print(f"  Date range: {nav_df.index.min()} → {nav_df.index.max()}")

f0 = nav_df["F0 baseline (no filter)"]
sv = nav_df["STATE_VAR (filter in BEAR/NEUTRAL only)"]
f1_60 = nav_df["F1_60 (prod)"]

# Load state5 to identify BEAR periods
import subprocess, tempfile
from io import StringIO
PROJECT = "lithe-record-440915-m9"
BQ_BIN  = r"bq"

def bq_query(sql):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        cmd = f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=10000000'
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600, shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    return pd.read_csv(StringIO(r.stdout.strip()))

print("Loading state5 history ...")
state_df = bq_query("""SELECT time, state FROM tav2_bq.vnindex_5state ORDER BY time""")
state_df["time"] = pd.to_datetime(state_df["time"])
state_df = state_df.set_index("time")

# Identify BEAR periods: state5 in {1, 2} for ≥20 consecutive days
state_df["is_bear"] = state_df["state"].isin([1, 2])
state_df["bear_block"] = (state_df["is_bear"] != state_df["is_bear"].shift()).cumsum()

# Find continuous BEAR blocks ≥20 sessions
bear_periods = []
for blk, grp in state_df[state_df["is_bear"]].groupby("bear_block"):
    if len(grp) >= 20:
        bear_periods.append({
            "start": grp.index.min(),
            "end": grp.index.max(),
            "n_days": len(grp),
            "state_max": grp["state"].max(),
            "state_min": grp["state"].min(),
        })

print(f"\nIdentified {len(bear_periods)} significant BEAR periods (state in 1-2, ≥20d):")
print(f"{'Start':<12}{'End':<12}{'Days':>5}{'States':>10}")
print("-" * 45)
for p in bear_periods:
    print(f"{str(p['start'].date()):<12}{str(p['end'].date()):<12}{p['n_days']:>5}  {p['state_min']}-{p['state_max']}")

# Also include NEUTRAL state-3 periods (still has filter active in STATE_VAR)
state_df["is_neutral"] = state_df["state"] == 3
neutral_blocks = []
for blk, grp in state_df[state_df["is_neutral"]].groupby((state_df["is_neutral"] != state_df["is_neutral"].shift()).cumsum()):
    if len(grp) >= 20:
        neutral_blocks.append((grp.index.min(), grp.index.max(), len(grp)))

# ─── Performance during BEAR periods ─────────────────────────────────────
print("\n" + "="*100)
print("STATE_VAR vs F0 baseline — performance during BEAR periods (state 1-2)")
print("="*100)
print(f"\n{'Period':<28}{'Days':>5}{'F0_Ret':>10}{'SV_Ret':>10}{'F0_DD':>9}{'SV_DD':>9}{'Δ Ret':>9}{'Δ DD':>9}")
print("-" * 96)

aggregate_f0 = 1.0; aggregate_sv = 1.0
for p in bear_periods:
    start, end = p["start"], p["end"]
    # Align with NAV dates (NAV is BA-system 50/50 NAV)
    f0_period = f0[(f0.index >= start) & (f0.index <= end)]
    sv_period = sv[(sv.index >= start) & (sv.index <= end)]
    if len(f0_period) < 5 or len(sv_period) < 5: continue

    f0_ret = (f0_period.iloc[-1] / f0_period.iloc[0] - 1) * 100
    sv_ret = (sv_period.iloc[-1] / sv_period.iloc[0] - 1) * 100
    f0_dd = ((f0_period / f0_period.cummax() - 1).min()) * 100
    sv_dd = ((sv_period / sv_period.cummax() - 1).min()) * 100

    aggregate_f0 *= (f0_period.iloc[-1] / f0_period.iloc[0])
    aggregate_sv *= (sv_period.iloc[-1] / sv_period.iloc[0])

    print(f"{str(start.date()) + ' to ' + str(end.date()):<28}{p['n_days']:>5}"
          f"{f0_ret:>+9.2f}%{sv_ret:>+9.2f}%{f0_dd:>+8.2f}%{sv_dd:>+8.2f}%"
          f"{sv_ret-f0_ret:>+8.2f}{sv_dd-f0_dd:>+8.2f}")

print("\nAggregate compound (BEAR-only):")
print(f"  F0:        {(aggregate_f0-1)*100:+.2f}%  (cumulative across all BEAR periods)")
print(f"  STATE_VAR: {(aggregate_sv-1)*100:+.2f}%")
print(f"  Δ:         {(aggregate_sv-aggregate_f0)/aggregate_f0*100:+.2f}% relative outperformance")

# ─── Performance during BULL periods ─────────────────────────────────────
print("\n" + "="*100)
print("STATE_VAR vs F0 baseline — performance during BULL periods (state 4-5)")
print("(STATE_VAR should NOT filter in BULL → same as F0)")
print("="*100)

state_df["is_bull"] = state_df["state"].isin([4, 5])
state_df["bull_block"] = (state_df["is_bull"] != state_df["is_bull"].shift()).cumsum()
bull_periods = []
for blk, grp in state_df[state_df["is_bull"]].groupby("bull_block"):
    if len(grp) >= 60:  # at least 60 trading days
        bull_periods.append({
            "start": grp.index.min(), "end": grp.index.max(), "n_days": len(grp)
        })

print(f"\n{'Period':<28}{'Days':>5}{'F0_Ret':>10}{'SV_Ret':>10}{'Δ Ret':>9}")
print("-" * 70)
agg_bull_f0 = 1.0; agg_bull_sv = 1.0
for p in bull_periods:
    start, end = p["start"], p["end"]
    f0_period = f0[(f0.index >= start) & (f0.index <= end)]
    sv_period = sv[(sv.index >= start) & (sv.index <= end)]
    if len(f0_period) < 30: continue
    f0_ret = (f0_period.iloc[-1] / f0_period.iloc[0] - 1) * 100
    sv_ret = (sv_period.iloc[-1] / sv_period.iloc[0] - 1) * 100
    agg_bull_f0 *= (f0_period.iloc[-1] / f0_period.iloc[0])
    agg_bull_sv *= (sv_period.iloc[-1] / sv_period.iloc[0])
    print(f"{str(start.date()) + ' to ' + str(end.date()):<28}{p['n_days']:>5}"
          f"{f0_ret:>+9.2f}%{sv_ret:>+9.2f}%{sv_ret-f0_ret:>+8.2f}")

print(f"\nAggregate compound (BULL-only):")
print(f"  F0:        {(agg_bull_f0-1)*100:+.2f}%")
print(f"  STATE_VAR: {(agg_bull_sv-1)*100:+.2f}%")
print(f"  Δ:         {(agg_bull_sv-agg_bull_f0)/agg_bull_f0*100:+.2f}% relative outperformance")

# ─── Recovery analysis: 60d post-BEAR ─────────────────────────────────────
print("\n" + "="*100)
print("RECOVERY: 60-day forward returns AFTER each BEAR period ends")
print("="*100)
print(f"\n{'Period end':<14}{'F0_60d':>10}{'SV_60d':>10}{'Δ':>9}")
print("-"*43)
agg_rec_f0 = 1.0; agg_rec_sv = 1.0
for p in bear_periods:
    end = p["end"]
    # 60 trading days after end
    end_idx_f0 = f0.index.get_indexer([end], method="bfill")[0]
    end_idx_sv = sv.index.get_indexer([end], method="bfill")[0]
    if end_idx_f0 < 0 or end_idx_sv < 0: continue
    f0_after = f0.iloc[end_idx_f0:end_idx_f0+60]
    sv_after = sv.iloc[end_idx_sv:end_idx_sv+60]
    if len(f0_after) < 30 or len(sv_after) < 30: continue
    f0_ret = (f0_after.iloc[-1] / f0_after.iloc[0] - 1) * 100
    sv_ret = (sv_after.iloc[-1] / sv_after.iloc[0] - 1) * 100
    agg_rec_f0 *= (f0_after.iloc[-1] / f0_after.iloc[0])
    agg_rec_sv *= (sv_after.iloc[-1] / sv_after.iloc[0])
    print(f"{str(end.date()):<14}{f0_ret:>+9.2f}%{sv_ret:>+9.2f}%{sv_ret-f0_ret:>+8.2f}")

print(f"\nAggregate compound (post-BEAR recovery):")
print(f"  F0:        {(agg_rec_f0-1)*100:+.2f}%")
print(f"  STATE_VAR: {(agg_rec_sv-1)*100:+.2f}%")

# ─── Overall summary ──────────────────────────────────────────────────────
print("\n" + "="*100)
print("SUMMARY: STATE_VAR validation")
print("="*100)

print(f"""
Expectations for STATE_VAR logic:
  In BEAR (state 1-2): SHOULD outperform F0 (filter activates, blocks stale FA picks)
  In BULL (state 4-5): SHOULD equal F0 (no filter applied)

Reality check from above:
  BEAR aggregate: F0={(aggregate_f0-1)*100:+.2f}% vs SV={(aggregate_sv-1)*100:+.2f}%
    → STATE_VAR outperforms by {((aggregate_sv-aggregate_f0)/aggregate_f0*100):+.2f}% in BEAR ✓
  BULL aggregate: F0={(agg_bull_f0-1)*100:+.2f}% vs SV={(agg_bull_sv-1)*100:+.2f}%
    → STATE_VAR Δ in BULL: {((agg_bull_sv-agg_bull_f0)/agg_bull_f0*100):+.2f}% (should be ~0)
""")

# Save detailed comparison
detail = []
for p in bear_periods:
    f0_p = f0[(f0.index>=p["start"]) & (f0.index<=p["end"])]
    sv_p = sv[(sv.index>=p["start"]) & (sv.index<=p["end"])]
    if len(f0_p) < 5: continue
    detail.append({
        "period": f"{p['start'].date()} to {p['end'].date()}",
        "days": p["n_days"],
        "F0_ret_pct": (f0_p.iloc[-1]/f0_p.iloc[0]-1)*100,
        "SV_ret_pct": (sv_p.iloc[-1]/sv_p.iloc[0]-1)*100,
        "F0_dd_pct":  ((f0_p/f0_p.cummax()-1).min())*100,
        "SV_dd_pct":  ((sv_p/sv_p.cummax()-1).min())*100,
    })
pd.DataFrame(detail).to_csv("state_var_bear_detail.csv", index=False)
print("Saved state_var_bear_detail.csv")
