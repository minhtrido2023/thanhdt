# -*- coding: utf-8 -*-
"""
analyze_crisis_reversal.py
==========================
Phân tích các segment CRISIS trong hệ thống 5-state hiện tại:
- Khi nào vào CRISIS, khi nào thoát
- Đáy thực sự nằm ở đâu trong CRISIS
- Độ trễ giữa đáy thực và lúc hệ thống nhận ra
- Liệt kê tín hiệu kỹ thuật có sẵn quanh đáy để thiết kế reversal sớm hơn
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# Load state history + VNINDEX
sh = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_history.csv"))
sh["time"] = pd.to_datetime(sh["time"])
vni = pd.read_csv(os.path.join(WORKDIR, "VNINDEX.csv"), low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
df = sh.merge(vni, on="time", how="left")

n = len(df)
state = df["state"].values
close = df["Close"].values
print(f"Total sessions: {n}  range: {df['time'].iloc[0].date()} → {df['time'].iloc[-1].date()}")

# ── Identify CRISIS segments (state == 1) ──
segments = []
i = 0
while i < n:
    if state[i] == 1:
        j = i
        while j < n and state[j] == 1:
            j += 1
        segments.append((i, j-1))   # inclusive
        i = j
    else:
        i += 1

print(f"\nTotal CRISIS segments: {len(segments)}")
print(f"{'#':>3} {'start':>12} {'end':>12} {'days':>5} {'entry_close':>11} {'bottom_close':>12} "
      f"{'bottom_date':>12} {'lag_to_bot':>10} {'lag_from_bot':>12} {'exit_close':>10} "
      f"{'bot→exit_%':>10} {'entry→exit_%':>13}")
print("-" * 130)

rows = []
for k, (s, e) in enumerate(segments, 1):
    seg = df.iloc[s:e+1]
    closes = seg["Close"].values
    if np.all(np.isnan(closes)):
        continue
    bot_local = int(np.nanargmin(closes))
    bot_global = s + bot_local
    days_seg = e - s + 1
    entry_close = closes[0]
    bot_close = closes[bot_local]
    exit_close = closes[-1]
    lag_entry_to_bot = bot_local            # phiên từ entry đến đáy
    lag_bot_to_exit = (e - bot_global)      # phiên từ đáy đến lúc thoát
    bot_to_exit = (exit_close/bot_close - 1) * 100
    entry_to_exit = (exit_close/entry_close - 1) * 100

    rows.append({
        "seg": k, "start_idx": s, "end_idx": e,
        "start": seg["time"].iloc[0].date(), "end": seg["time"].iloc[-1].date(),
        "days": days_seg,
        "entry_close": entry_close, "bot_close": bot_close, "exit_close": exit_close,
        "bot_idx": bot_global, "bot_date": df["time"].iloc[bot_global].date(),
        "lag_entry_to_bot": lag_entry_to_bot,
        "lag_bot_to_exit": lag_bot_to_exit,
        "bot_to_exit_pct": bot_to_exit,
        "entry_to_exit_pct": entry_to_exit,
    })
    print(f"{k:>3} {str(seg['time'].iloc[0].date()):>12} {str(seg['time'].iloc[-1].date()):>12} "
          f"{days_seg:>5} {entry_close:>11.2f} {bot_close:>12.2f} "
          f"{str(df['time'].iloc[bot_global].date()):>12} {lag_entry_to_bot:>10} {lag_bot_to_exit:>12} "
          f"{exit_close:>10.2f} {bot_to_exit:>9.1f}% {entry_to_exit:>12.1f}%")

res = pd.DataFrame(rows)
print(f"\nMedian lag bottom→exit (days)   : {res['lag_bot_to_exit'].median():.0f}")
print(f"Mean   lag bottom→exit (days)   : {res['lag_bot_to_exit'].mean():.1f}")
print(f"Median rally bottom→exit (%)    : {res['bot_to_exit_pct'].median():.1f}%")
print(f"Mean   rally bottom→exit (%)    : {res['bot_to_exit_pct'].mean():.1f}%")
print(f"  → if we could exit AT bottom, we'd save median ~{res['bot_to_exit_pct'].median():.1f}% extra upside before re-entry")

# ── Look at indicators in last 20 days before exit (and around bottom) ──
# Inspect: D_RSI, D_CMF, D_MACDdiff, ma200_dev, breadth, r_score
print(f"\n=== INDICATORS NEAR BOTTOM (-5..+10 days, sample 3 large CRISES) ===")
df["r_score"] = df["r_score"] if "r_score" in df.columns else np.nan
# Re-compute r_score from existing CSV? No: use state_raw transitions as proxy
# Show D_RSI, D_CMF, D_MACDdiff, MA200 dev, close
ma200 = df["Close"].rolling(200, min_periods=1).mean()
df["ma200"] = ma200
df["ma200_dev"] = df["Close"] / ma200 - 1
df["ma50"] = df["Close"].rolling(50, min_periods=1).mean()
df["ma20"] = df["Close"].rolling(20, min_periods=1).mean()

# Pick biggest 3 crises (by days)
top3 = res.sort_values("days", ascending=False).head(5)
for _, r in top3.iterrows():
    bot_idx = int(r["bot_idx"])
    print(f"\n  CRISIS #{int(r['seg'])} bottom={r['bot_date']} ({r['bot_close']:.2f}) days={int(r['days'])} lag_bot→exit={int(r['lag_bot_to_exit'])}")
    lo = max(0, bot_idx - 5)
    hi = min(n - 1, bot_idx + 15)
    snap = df.iloc[lo:hi+1][["time", "Close", "ma20", "ma50", "ma200_dev",
                              "D_RSI", "D_CMF", "D_MACDdiff", "state"]].copy()
    for c in ["Close", "ma20", "ma50"]:
        snap[c] = snap[c].round(2)
    snap["ma200_dev"] = (snap["ma200_dev"] * 100).round(1)
    snap["D_RSI"]    = snap["D_RSI"].round(3)
    snap["D_CMF"]    = snap["D_CMF"].round(3)
    snap["D_MACDdiff"] = snap["D_MACDdiff"].round(3)
    snap["mark"] = ""
    snap.loc[snap.index == bot_idx, "mark"] = "← BOTTOM"
    snap.loc[snap.index == int(r["end_idx"]), "mark"] = "← EXIT"
    print(snap.to_string(index=False))

# ── Count BullDvg occurrences WITHIN each CRISIS segment ──
if "bull_dvg" in vni.columns or True:
    # Need bear_dvg/bull_dvg — re-compute from VNINDEX.csv quickly using same formula
    pass

res.to_csv(os.path.join(WORKDIR, "crisis_segments.csv"), index=False)
print(f"\nSaved → crisis_segments.csv")
