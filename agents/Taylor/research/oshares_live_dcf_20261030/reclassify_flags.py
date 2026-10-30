#!/usr/bin/env python3
"""Áp quy tắc mới (oshares_dcf.classify_oshares_gap) lên CÙNG dữ liệu quy tắc cũ đã dùng:
erp_domestic_v2_20261030/data/oshares_check.csv, cửa sổ (2026-06-30, 2026-10-29]. Chạy từ worktree outer."""
import os, sys
import pandas as pd
sys.path.insert(0, os.getcwd())
import oshares_dcf as osd
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/erp_domestic_v2_20261030/data/oshares_check.csv"
o = pd.read_csv(SRC)
a, b = o[o.time == "2026-06-30"].set_index("ticker"), o[o.time == "2026-10-29"].set_index("ticker")
j = a.index.intersection(b.index)
fr = pd.DataFrame({"ticker": j, "Close_d0": a.loc[j, "Close"].values, "Price_d0": a.loc[j, "Price"].values,
                   "OShares_d0": a.loc[j, "OShares"].values, "OShares_d1": b.loc[j, "OShares"].values}).dropna()
res = osd.oshares_gap_check(fr, "2026-06-30", "2026-10-29")
fr["verdict"] = fr.ticker.map(lambda t: res[t][0])
fr["expected"] = fr.ticker.map(lambda t: res[t][1].get("expected_ratio"))
fr["adj"] = fr.Close_d0 / fr.Price_d0
fr["osr"] = fr.OShares_d1 / fr.OShares_d0
fr["old_flag"] = (fr.adj < 0.93) & (fr.osr < 0.95 / fr.adj)
fr.round(4).to_csv(os.path.join(HERE, "out_reclassify_flags.csv"), index=False)
print(f"mã {len(fr)} | cờ cũ {int(fr.old_flag.sum())} | cờ mới OSHARES_LAG {int((fr.verdict == 'OSHARES_LAG').sum())}")
print("verdict (toàn bộ):", fr.verdict.value_counts().to_dict())
print("verdict trên 30 cờ cũ:", fr[fr.old_flag].verdict.value_counts().to_dict())
print(fr[fr.old_flag | (fr.verdict != "NO_EVENT") & (fr.verdict != "CASH_DIV")][["ticker", "adj", "osr", "expected", "old_flag", "verdict"]].round(4).to_string(index=False))
