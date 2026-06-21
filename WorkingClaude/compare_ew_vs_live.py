# -*- coding: utf-8 -*-
"""
compare_ew_vs_live.py
Compare EW staging vs LIVE Tinh Tế: distributions, transitions, divergence days.
"""
import sys, io, os, subprocess, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import pandas as pd
import numpy as np

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
BQ      = r"bq"
PROJECT = "lithe-record-440915-m9"
STATE_NAMES = {1:"CRISIS", 2:"BEAR", 3:"NEUTRAL", 4:"BULL", 5:"EX-BULL"}

# Pull LIVE
print("Pulling LIVE Tinh Tế ...")
sql = "SELECT time, state, state_raw FROM tav2_bq.vnindex_5state ORDER BY time"
with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as f:
    f.write(sql); qp = f.name
cmd = f'"{BQ}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=10000000 < "{qp}"'
r = subprocess.run(cmd, capture_output=True, text=True, shell=True)
os.unlink(qp)
live = pd.read_csv(io.StringIO(r.stdout))
live["time"] = pd.to_datetime(live["time"])
live = live.rename(columns={"state":"state_live", "state_raw":"raw_live"})

# Load EW staging
print("Loading EW staging ...")
ew = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_ew_staging.csv"))
ew["time"] = pd.to_datetime(ew["time"])
ew = ew.rename(columns={"state":"state_ew", "state_raw":"raw_ew"})

# Join
df = live.merge(ew, on="time", how="inner")
print(f"  Common dates: {len(df)} | {df['time'].min().date()} → {df['time'].max().date()}")

# Restrict to 2014+ (where EW is meaningful)
df14 = df[df["time"] >= "2014-01-01"].copy()
print(f"  Post-2014: {len(df14)} sessions")

# ── State distribution
def dist_table(s, name):
    c = s.value_counts(normalize=True).sort_index() * 100
    return {STATE_NAMES.get(int(k), str(k)): round(v, 1) for k, v in c.items()}

print("\n" + "="*70)
print("STATE DISTRIBUTION (post-2014, % of sessions)")
print("="*70)
d_live = dist_table(df14["state_live"], "live")
d_ew   = dist_table(df14["state_ew"],  "ew")
print(f"  {'State':<10} {'LIVE Tinh Tế':>15} {'EW staging':>15} {'Δ':>10}")
for s_name in ["CRISIS", "BEAR", "NEUTRAL", "BULL", "EX-BULL"]:
    a = d_live.get(s_name, 0.0); b = d_ew.get(s_name, 0.0)
    print(f"  {s_name:<10} {a:>14.1f}% {b:>14.1f}% {b-a:>+9.1f}pp")

# ── Agreement / disagreement
df14["agree"] = (df14["state_live"] == df14["state_ew"])
agree_pct = df14["agree"].mean() * 100
print(f"\nAgreement (live==ew state): {agree_pct:.1f}%")

# Disagreement breakdown
print("\nDisagreement matrix (count of sessions):")
ct = pd.crosstab(df14["state_live"], df14["state_ew"],
                 rownames=["LIVE\\EW"], colnames=[""])
ct.index = [STATE_NAMES.get(int(k), str(k)) for k in ct.index]
ct.columns = [STATE_NAMES.get(int(k), str(k)) for k in ct.columns]
print(ct.to_string())

# ── Transition count
def n_transitions(s):
    return int((s.values != np.roll(s.values, 1))[1:].sum())
print(f"\nTransitions:")
print(f"  LIVE post-2014: {n_transitions(df14['state_live'])}")
print(f"  EW post-2014:   {n_transitions(df14['state_ew'])}")

# ── Recent 30 sessions side-by-side
print("\n" + "="*70)
print("LAST 30 SESSIONS (side-by-side)")
print("="*70)
recent = df14.tail(30)[["time", "state_live", "raw_live", "state_ew", "raw_ew"]].copy()
recent["time"] = recent["time"].dt.strftime("%Y-%m-%d")
recent["L"] = recent["state_live"].astype(int).map(STATE_NAMES).str[:3]
recent["E"] = recent["state_ew"].astype(int).map(STATE_NAMES).str[:3]
recent["diff"] = recent.apply(lambda r: "‼️" if r["state_live"] != r["state_ew"] else "", axis=1)
print(recent[["time", "L", "raw_live", "E", "raw_ew", "diff"]].to_string(index=False))

# ── Notable historical events
print("\n" + "="*70)
print("HISTORICAL EVENT WINDOWS (state on key dates)")
print("="*70)
events = [
    ("2018-04-09", "VNI ATH 2018 (1204)"),
    ("2018-07-11", "2018 trade-war bottom"),
    ("2020-03-30", "COVID crash bottom (~660)"),
    ("2021-12-30", "Late-2021 bull peak (~1500)"),
    ("2022-04-06", "Vinhomes peak / pre-crash"),
    ("2022-11-15", "2022 bear bottom (~880)"),
    ("2023-09-29", "2023 peak (1255)"),
    ("2024-08-05", "2024 mid-correction"),
    ("2025-09-01", "2025 mid-year"),
    ("2026-04-09", "2026 Q1 bear bottom (~1675)"),
]
for d, label in events:
    row = df[df["time"] == pd.Timestamp(d)]
    if len(row) == 0:
        # nearest
        idx = (df["time"] - pd.Timestamp(d)).abs().idxmin()
        row = df.iloc[[idx]]
    r = row.iloc[0]
    lname = STATE_NAMES.get(int(r['state_live']), '?')
    ename = STATE_NAMES.get(int(r['state_ew']), '?')
    flag = "  ‼️" if r["state_live"] != r["state_ew"] else ""
    print(f"  {r['time'].strftime('%Y-%m-%d')} {label:<35} LIVE={lname:<8} EW={ename:<8}{flag}")

# ── Year-by-year %BULL+EX-BULL (risk-on bias)
print("\n" + "="*70)
print("YEAR-BY-YEAR: %sessions in BULL/EX-BULL (risk-on)")
print("="*70)
df14["year"] = df14["time"].dt.year
def risk_on_pct(group, col):
    return (group[col].isin([4,5])).mean() * 100
years = sorted(df14["year"].unique())
print(f"  {'Year':<6} {'LIVE %ON':>10} {'EW %ON':>10} {'Δ':>8}")
for y in years:
    g = df14[df14["year"] == y]
    a = risk_on_pct(g, "state_live"); b = risk_on_pct(g, "state_ew")
    print(f"  {y:<6} {a:>9.1f}% {b:>9.1f}% {b-a:>+7.1f}pp")
