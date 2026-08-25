"""Step 1 sanity validation of macro_state_live.get_macro_state() for 2008-2013 window.
Per Mike dispatch (job Taylor_20260825_055651): must PASS before running the 2008 backtest.
"""
import sys, os
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
os.chdir("/home/trido/thanhdt/WorkingClaude")
import pandas as pd
from macro_state_live import get_macro_state

# Confirmed via dna_report.py STATE_MAP: BQ state column is 1-indexed, NOT 0-indexed.
STATE_NAMES = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}

df = get_macro_state(start="2008-01-01", end="2013-12-31")
df["time"] = pd.to_datetime(df["time"])
df["state_name"] = df["state"].map(STATE_NAMES)

print(f"Rows: {len(df)}, range {df['time'].min().date()} -> {df['time'].max().date()}")
print(df["state_name"].value_counts())
print()

def window_summary(label, start, end):
    w = df[(df["time"] >= start) & (df["time"] <= end)]
    if len(w) == 0:
        print(f"{label}: NO ROWS in [{start},{end}]")
        return
    vc = w["state_name"].value_counts()
    print(f"{label} [{start} -> {end}], n={len(w)}: {dict(vc)}")

print("=== Check 1: 2008-10 -> 2009-03 (VNINDEX -71%), expect CRISIS or BEAR dominant ===")
window_summary("Check1", "2008-10-01", "2009-03-31")

print()
print("=== Check 2: 2009-09 -> 2009-12 recovery, expect transition toward BEAR/NEUTRAL ===")
window_summary("Check2", "2009-09-01", "2009-12-31")

print()
print("=== Check 3: 2011-05 -> 2012-06 (CPI 23%, VNINDEX -50%), expect BEAR or CRISIS ===")
window_summary("Check3", "2011-05-01", "2012-06-30")

print()
print("=== Full state transition timeline (state changes only) ===")
df["state_chg"] = df["state"].diff().fillna(0) != 0
chg = df[df["state_chg"]]
for _, r in chg.iterrows():
    print(f"{r['time'].date()}  -> {r['state_name']}  (cap={r['cap']})")

out_csv = "/home/trido/thanhdt/WorkingClaude/agents/Taylor/research/dt5g_pre2014_validate_20260825.csv"
df.to_csv(out_csv, index=False)
print(f"\nSaved full series to {out_csv}")
