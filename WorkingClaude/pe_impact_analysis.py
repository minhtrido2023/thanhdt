# -*- coding: utf-8 -*-
import sys, io, os, subprocess, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import pandas as pd, numpy as np

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# OLD baseline state (BQ backup, OLD PE + clean Close/CMF)
old = pd.read_csv(os.path.join(WORKDIR, "data/state_pre_pe.csv"), parse_dates=["time"])
# Current state (NEW PE + clean Close/CMF — both clean now)
new = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_4b_full_history.csv"), parse_dates=["time"])
new = new.rename(columns={"state":"state_new","state_raw":"raw_new"})
df = old.merge(new, on="time", how="inner")
chg = df[df.state_old != df.state_new].copy()
chg["yr"] = chg.time.dt.year

print("="*60)
print(f"PE-only state-flip effect: {len(chg)}/{len(df)} ({len(chg)/len(df)*100:.1f}%)")
print("="*60)
print(f'{"Year":<6}{"n":>4}  OLD->NEW pattern')
for yr, g in chg.groupby("yr"):
    patterns = g.apply(lambda r: f"{int(r.state_old)}->{int(r.state_new)}", axis=1).value_counts()
    pstr = ", ".join([f"{p}:{c}" for p,c in patterns.items()])
    print(f"{yr:<6}{len(g):>4}  {pstr}")

chg["delta"] = chg.state_new - chg.state_old
print(f"\nNet shift: sum_delta={chg.delta.sum()} (+ bullish, - bearish)")
print(f"  Days more bullish: {(chg.delta>0).sum()}")
print(f"  Days more bearish: {(chg.delta<0).sum()}")

# Get OLD PE via BQ time-travel
print("\nPulling OLD PE from BQ time-travel...")
sql = """
SELECT time, VNINDEX_PE AS pe_old FROM `lithe-record-440915-m9.tav2_bq.ticker`
  FOR SYSTEM_TIME AS OF TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
WHERE ticker = 'VNINDEX' AND time >= '2014-01-01' ORDER BY time
"""
with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as f:
    f.write(sql); qp = f.name
BQ = r"bq"
cmd = f'"{BQ}" query --use_legacy_sql=false --project_id=lithe-record-440915-m9 --format=csv --max_rows=10000 < "{qp}"'
r = subprocess.run(cmd, capture_output=True, text=True, shell=True)
os.unlink(qp)
pe_old = pd.read_csv(io.StringIO(r.stdout))
pe_old["time"] = pd.to_datetime(pe_old["time"])

pe_new = pd.read_csv(r"/home/trido/thanhdt/WorkingClaude/data/VNINDEX.csv", usecols=["time","VNINDEX_PE"])
pe_new["time"] = pd.to_datetime(pe_new["time"])
pe_new = pe_new.rename(columns={"VNINDEX_PE":"pe_new"})

m = pe_new.merge(pe_old, on="time", how="inner")
m["pe_diff"] = m.pe_new - m.pe_old
m["changed"] = m.pe_diff.abs() > 0.001
chg_pe = m[m.changed].copy()
print(f"\nPE values changed (NEW vs OLD BQ): {len(chg_pe)}/{len(m)} ({len(chg_pe)/len(m)*100:.1f}%)")
print(f"PE diff (NEW-OLD): mean={chg_pe.pe_diff.mean():.3f}, median={chg_pe.pe_diff.median():.3f}, std={chg_pe.pe_diff.std():.3f}")
print(f"Direction: NEW > OLD (PE corrected UP): {(chg_pe.pe_diff>0).sum()} days")
print(f"           NEW < OLD (PE corrected DOWN): {(chg_pe.pe_diff<0).sum()} days")
chg_pe["yr"] = chg_pe.time.dt.year
print("\nPE changes by year:")
print(chg_pe.groupby("yr").agg(n=("pe_diff","size"),mean_d=("pe_diff","mean"),min_d=("pe_diff","min"),max_d=("pe_diff","max")).to_string())

print("\n===== Largest PE adjustments =====")
big = chg_pe.iloc[chg_pe.pe_diff.abs().argsort().iloc[::-1].values[:15]]
print(big[["time","pe_old","pe_new","pe_diff"]].to_string(index=False))
