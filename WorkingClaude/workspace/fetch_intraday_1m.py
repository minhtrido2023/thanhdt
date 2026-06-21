# -*- coding: utf-8 -*-
"""Fetch & cache bar 1-phut cho ro ticker dai dien universe V2.3 (execution backtest).

Nguon: vnstock VCI (nhu orb_pt.py). Chunk 6 thang, idempotent: ticker da co file
day du (max time >= END_GUARD) thi skip. Output: data/intraday_1m/{ticker}.csv
"""
import os, sys, time, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pandas as pd
from vnstock import Vnstock

WD = r"/home/trido/thanhdt/WorkingClaude"
OUT = os.path.join(WD, "data", "intraday_1m")
os.makedirs(OUT, exist_ok=True)

# mix thanh khoan: 10 liquid + 6 mid/small, deu nam trong top traded cua backtest V2.x
TICKERS = ["VIX","GEX","MWG","STB","SSI","HPG","VPB","MSN","PVD","DXG",
           "PHR","HT1","VEA","DHA","D2D","NNC"]
START = "2023-09-01"
END = "2026-06-12"
END_GUARD = "2026-06-01"   # file cache co bar >= ngay nay coi nhu du

CHUNKS = []
s = pd.Timestamp(START)
while s < pd.Timestamp(END):
    e = min(s + pd.DateOffset(months=6), pd.Timestamp(END))
    CHUNKS.append((s.strftime("%Y-%m-%d"), e.strftime("%Y-%m-%d")))
    s = e

for tk in TICKERS:
    path = os.path.join(OUT, f"{tk}.csv")
    if os.path.exists(path):
        try:
            old = pd.read_csv(path, usecols=["time"])
            if old["time"].max() >= END_GUARD:
                print(f"[skip] {tk} cached -> {old['time'].max()}")
                continue
        except Exception:
            pass
    frames = []
    for c0, c1 in CHUNKS:
        for attempt in range(3):
            try:
                df = Vnstock().stock(symbol=tk, source="VCI").quote.history(
                    start=c0, end=c1, interval="1m")
                if df is not None and len(df):
                    frames.append(df)
                break
            except Exception as ex:
                print(f"[warn] {tk} {c0}->{c1} attempt{attempt}: {ex}")
                time.sleep(5 * (attempt + 1))
        time.sleep(1.5)
    if not frames:
        print(f"[FAIL] {tk}: khong co data")
        continue
    allb = pd.concat(frames, ignore_index=True)
    allb["time"] = pd.to_datetime(allb["time"])
    allb = allb.drop_duplicates("time").sort_values("time").reset_index(drop=True)
    allb.to_csv(path, index=False)
    print(f"[ok] {tk}: {len(allb):,} bars {allb['time'].min()} -> {allb['time'].max()}")

print("DONE")
