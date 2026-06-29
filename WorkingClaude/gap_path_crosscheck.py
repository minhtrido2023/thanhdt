"""Within-day PATH cross-check on TRUE intraday (data/intraday_1m, 16 names, 2023-09..2026-06, 1-min).
Confirms the daily-proxy finding (gap_adaptive_proxy.py: abnormal UP-gap gives back, DOWN-gap recovers)
AND answers the wiring question: WHEN in the session does the move happen -> target fill time (11:15 vs ATC)?

Per (name, day): gap = open(09:15)/prior_ATC - 1 ; rvol = trailing-20d daily-ret std (causal) ; gap_z = gap/rvol.
Path = price at each checkpoint vs OPEN, in bps: (p_cp/open - 1)*1e4.
  <0 = below open = cheaper to BUY by waiting (give-back) | >0 = above open = open was the cheap entry (recovery).
So for a BUY-list name:  UP-gap path going negative => wait pays;  DOWN-gap path going positive => buy at open pays.
"""
import os, glob, numpy as np, pandas as pd
pd.set_option("display.width", 220)
CPS = ["09:45", "10:30", "11:15", "13:30", "14:30", "ATC"]
rows = []
for f in sorted(glob.glob("data/intraday_1m/*.csv")):
    tk = os.path.basename(f)[:-4]
    df = pd.read_csv(f); df["time"] = pd.to_datetime(df["time"])
    df["date"] = df["time"].dt.date; df["hhmm"] = df["time"].dt.strftime("%H:%M")
    df = df.sort_values("time")
    g = df.groupby("date")
    daily = pd.DataFrame({"open": g["open"].first(), "atc": g["close"].last()})
    daily["prev"] = daily["atc"].shift(1)
    daily["gap"] = daily["open"] / daily["prev"] - 1
    daily["rvol"] = daily["atc"].pct_change().rolling(20).std().shift(1)
    daily["gap_z"] = daily["gap"] / daily["rvol"]
    # checkpoint prices = last bar at or before each HH:MM
    for cp in CPS[:-1]:
        px = df[df["hhmm"] <= cp].groupby("date")["close"].last()
        daily[cp] = px
    daily["ATC"] = daily["atc"]
    d = daily.dropna(subset=["gap_z", "open", "prev"]).copy()
    d = d[(d["gap_z"].abs() <= 8) & (d["gap"].abs() <= 0.15) & (d["rvol"] > 0)]
    for cp in CPS:
        d[cp + "_b"] = (d[cp] / d["open"] - 1) * 1e4         # vs OPEN, bps
    d["tk"] = tk
    rows.append(d[["tk", "gap_z"] + [c + "_b" for c in CPS]])
R = pd.concat(rows, ignore_index=True)
BINS = [-99, -2, -1, 1, 2, 99]; LAB = ["z<-2 DOWN", "-2..-1", "-1..1 norm", "1..2", "z>2 UP"]
R["bucket"] = pd.cut(R["gap_z"], BINS, labels=LAB)

print(f"=== Within-day path vs OPEN (bps) | {R['tk'].nunique()} names, {len(R):,} ticker-days ===")
print("  <0 = below open (give-back, waiting buys cheaper) | >0 = above open (recovery, open was cheap)\n")
g = R.groupby("bucket", observed=True)
tab = pd.DataFrame({"N": g.size(), **{cp: (g[cp + "_b"].mean()).round(0).astype(int) for cp in CPS}})
print(tab.to_string())

print("\n--- ATC vs OPEN by bucket: t-stat (is the end-of-day give-back/recovery significant?) ---")
for lab in LAB:
    s = R[R["bucket"] == lab]["ATC_b"]
    if len(s) > 5:
        print(f"  {lab:11s} N={len(s):>5}  ATC {s.mean():>7.0f} bps  t={s.mean()/(s.std()/np.sqrt(len(s))):>6.1f}")

print("\n--- WIRING READ: fraction of the full Open->ATC move already realized by 11:15 (path/ATC) ---")
for lab in ["z>2 UP", "z<-2 DOWN"]:
    s = R[R["bucket"] == lab]
    if len(s) > 5 and abs(s["ATC_b"].mean()) > 1:
        frac = s["11:15_b"].mean() / s["ATC_b"].mean()
        print(f"  {lab:11s}: 11:15 {s['11:15_b'].mean():>6.0f} bps / ATC {s['ATC_b'].mean():>6.0f} bps = {frac*100:>4.0f}% done by 11:15")
print("\nNOTE: 16-name sample (2023-09+); confirms DIRECTION + path of the daily-proxy result, sets target fill time.")
