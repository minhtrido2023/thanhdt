# -*- coding: utf-8 -*-
"""
demo_c4_benchmark_difference.py
Retrospective: if we'd shadow-tested v3.1 during Q1 2026 (Apr 1 → May 20),
what would C4 say under different forward-return benchmarks?

Compares:
  - VNI T+5         (circular — VIN-dominated)
  - VNINDEX_EW T+5  (broad, primary in v2 of C4)
  - Breadth T+5     (% advances)

This shows WHY using VNI to validate Tam Quan is self-defeating.
"""
import sys, io, os, subprocess, tempfile, bisect
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import pandas as pd, numpy as np

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
BQ      = r"bq"
PROJECT = "lithe-record-440915-m9"
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}

def bq_csv(sql):
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); qp = f.name
    cmd = f'"{BQ}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=10000 < "{qp}"'
    r = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    os.unlink(qp)
    return pd.read_csv(io.StringIO(r.stdout))

START = "2026-04-01"
END   = "2026-05-15"  # need T+5 buffer, so window ends 5 days before today's data

print("="*78)
print(f"RETROSPECTIVE: C4 benchmark comparison — Q1 2026 VIN rally")
print(f"Window: {START} → {END}")
print("="*78)

# Pull states
live = bq_csv(f"SELECT s.time, s.state AS live FROM tav2_bq.vnindex_5state AS s WHERE s.time BETWEEN '{START}' AND '{END}'")
stag = bq_csv(f"SELECT s.time, s.state AS stag FROM tav2_bq.vnindex_5state_staging AS s WHERE s.time BETWEEN '{START}' AND '{END}'")
live["time"] = pd.to_datetime(live["time"]); stag["time"] = pd.to_datetime(stag["time"])
df = live.merge(stag, on="time", how="inner")

# Pull VNI + EW + breadth
vni = bq_csv(f"SELECT t.time, t.Close AS vni_close FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' AND t.time BETWEEN '{START}' AND '2026-05-21'")
vni["time"] = pd.to_datetime(vni["time"])
ew = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_ew_full.csv"))
ew["time"] = pd.to_datetime(ew["time"])
ew = ew[(ew["time"]>=START) & (ew["time"]<="2026-05-21")][["time","Close"]].rename(columns={"Close":"ew_close"})
breadth_sql = f"""
WITH ret_t5 AS (
  SELECT t.ticker, t.time, t.Close,
         LEAD(t.Close, 5) OVER (PARTITION BY t.ticker ORDER BY t.time) AS close_t5
  FROM tav2_bq.ticker AS t
  WHERE t.time BETWEEN '{START}' AND '2026-05-21'
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
    AND t.Close > 0
)
SELECT time, COUNT(*) AS n_total, COUNTIF(close_t5 > Close) AS n_up
FROM ret_t5 WHERE close_t5 IS NOT NULL GROUP BY time ORDER BY time
"""
bd = bq_csv(breadth_sql); bd["time"] = pd.to_datetime(bd["time"])
bd["breadth_t5"] = bd["n_up"] / bd["n_total"]

# Merge + compute T+5 returns
df = df.merge(vni, on="time", how="left").merge(ew, on="time", how="left").merge(bd[["time","breadth_t5"]], on="time", how="left")
df = df.sort_values("time").reset_index(drop=True)
df["vni_fwd5"] = df["vni_close"].shift(-5) / df["vni_close"] - 1
df["ew_fwd5"]  = df["ew_close"].shift(-5)  / df["ew_close"]  - 1

# Show divergence days only
div = df[df["live"] != df["stag"]].copy()
print(f"\nDivergence days: {len(div)} / {len(df)} ({len(div)/len(df)*100:.0f}%)")
print(f"  All: LIVE=BULL while STAG=NEUTRAL (Tam Quan's intended behavior)")

def stag_correct(stag, live, ret):
    if pd.isna(ret): return None
    if stag < live and ret < 0: return True
    if stag > live and ret > 0: return True
    if stag < live and ret >= 0: return False
    if stag > live and ret <= 0: return False
    return None

print(f"\n{'Date':<12} {'LIVE':<8} {'STAG':<8}  {'VNI T+5':>9}  {'EW T+5':>9}  {'Breadth T+5':>13}  {'VNI verd':>10}  {'EW verd':>9}")
for _, r in div.iterrows():
    ln = STATE_NAMES.get(int(r['live']), '?')[:3]
    sn = STATE_NAMES.get(int(r['stag']), '?')[:3]
    vni_s = f"{r['vni_fwd5']*100:+.2f}%" if not pd.isna(r['vni_fwd5']) else "n/a"
    ew_s  = f"{r['ew_fwd5']*100:+.2f}%"  if not pd.isna(r['ew_fwd5']) else "n/a"
    bd_s  = f"{r['breadth_t5']*100:.0f}% up" if not pd.isna(r['breadth_t5']) else "n/a"
    vni_v = stag_correct(r["stag"], r["live"], r["vni_fwd5"])
    ew_v  = stag_correct(r["stag"], r["live"], r["ew_fwd5"])
    vni_str = "✓ right" if vni_v else ("✗ wrong" if vni_v is False else "—")
    ew_str  = "✓ right" if ew_v  else ("✗ wrong" if ew_v  is False else "—")
    print(f"{r['time'].strftime('%Y-%m-%d')}  {ln:<8} {sn:<8}  {vni_s:>9}  {ew_s:>9}  {bd_s:>13}  {vni_str:>10}  {ew_str:>9}")

# Aggregate
print(f"\n" + "="*78)
print("AGGREGATE C4 — what each benchmark would say")
print("="*78)

for label, col in [("VNI T+5 (circular!)", "vni_fwd5"), ("EW T+5 (broad, primary)", "ew_fwd5")]:
    correct = wrong = 0
    for _, r in div.iterrows():
        v = stag_correct(r["stag"], r["live"], r[col])
        if v is True: correct += 1
        elif v is False: wrong += 1
    total = correct + wrong
    if total > 0:
        pct = correct / total * 100
        verdict = "GREEN" if pct >= 55 else ("YELLOW" if pct >= 40 else "RED")
        print(f"  {label:<28}: {correct}/{total} = {pct:>5.1f}% correct  →  C4 = {verdict}")
    else:
        print(f"  {label:<28}: no T+5 data")

# Breadth-based
correct = wrong = 0
for _, r in div.iterrows():
    if pd.isna(r["breadth_t5"]): continue
    bd_ret = r["breadth_t5"] - 0.5
    v = stag_correct(r["stag"], r["live"], bd_ret)
    if v is True: correct += 1
    elif v is False: wrong += 1
total = correct + wrong
if total > 0:
    pct = correct / total * 100
    verdict = "GREEN" if pct >= 55 else ("YELLOW" if pct >= 40 else "RED")
    print(f"  {'Breadth %adv T+5 (broad)':<28}: {correct}/{total} = {pct:>5.1f}% correct  →  C4 = {verdict}")

print(f"\n→ Interpretation:")
print(f"   If VNI-C4 and EW-C4 disagree, this is EXACTLY the case where Tam Quan adds value:")
print(f"   VNI says 'STAG was wrong' but broad market (EW) confirms 'STAG was right'.")
print(f"   The whole point of Tam Quan is to ignore VNI when broad market disagrees.")
