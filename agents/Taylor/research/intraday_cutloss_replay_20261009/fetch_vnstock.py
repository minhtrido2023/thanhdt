#!/usr/bin/env python3
"""fetch_vnstock.py — bổ sung bar 15' (vnstock/VCI) cho mã ledger KHÔNG có trong data/intraday_full.pkl
và cho mọi mã giữ sau 2026-05-12 (pkl hết hạn). Chỉ đọc API công khai; ghi cache/vn15/<MÃ>.parquet.
Lọc về nhãn phiên 09:15..11:15, 13:00..14:15, 14:45 (VCI trả lưới 15' liên tục cả ngoài giờ)."""
import os
import sys
import time

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "cache", "vn15")
LABELS = {f"{h:02d}:{m:02d}" for h in (9, 10, 11, 13, 14) for m in (0, 15, 30, 45)}
LABELS = {x for x in LABELS if "09:15" <= x <= "11:15" or "13:00" <= x <= "14:15"} | {"14:45"}


def main():
    from vnstock import Quote
    os.makedirs(OUT, exist_ok=True)
    names = sorted({x.strip() for f in sys.argv[1:] for x in open(f) if x.strip()})
    for i, t in enumerate(names):
        p = os.path.join(OUT, f"{t}.parquet")
        if os.path.exists(p):
            continue
        for k in range(3):
            try:
                df = Quote(symbol=t, source="VCI").history(start="2023-09-01", end="2026-10-09", interval="15m")
                df["time"] = pd.to_datetime(df["time"])
                df = df[df.time.dt.strftime("%H:%M").isin(LABELS) & (df.time.dt.weekday < 5)]
                df.to_parquet(p)
                print(i, t, len(df), df.time.min(), df.time.max(), flush=True)
                break
            except Exception as e:     # noqa: BLE001
                print(i, t, "ERR", str(e)[:150], flush=True)
                time.sleep(20)
        time.sleep(3.2)


if __name__ == "__main__":
    main()
