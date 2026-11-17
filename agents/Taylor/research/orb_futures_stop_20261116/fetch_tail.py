# Lay bar 1m VN30F1M (VCI, cung nguon orb_pt.py) 2026-09-20..nay de noi tape den hien tai.
import pandas as pd
from vnstock.api.quote import Quote
f = Quote(symbol="VN30F1M", source="VCI").history(start="2026-09-20", end="2026-11-16", interval="1m")
f["time"] = pd.to_datetime(f["time"]); f = f.sort_values("time")
f.to_csv("vn30f1m_tail_20260920_20261116.csv", index=False)
print(len(f), f["time"].min(), f["time"].max())
