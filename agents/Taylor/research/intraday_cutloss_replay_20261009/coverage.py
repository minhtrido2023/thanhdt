#!/usr/bin/env python3
"""coverage.py — độ phủ thật của giá trong phiên trên các (ngày, mã) đang giữ trong cửa sổ replay."""
import datetime as dt
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv = [sys.argv[0]]
import replay as R  # noqa: E402

rows = []
hl = R.HL[(R.HL.d >= dt.date(2023, 9, 12)) & (R.HL.d <= R.LEDGER_END)]
pk = R.pkl()
pkd = {t: set(x.d) for t, x in pk.items()}
for (d, tk) in hl[["d", "ticker"]].itertuples(index=False):
    if d <= R.PKL_END and d in pkd.get(tk, ()):
        src = "pkl15"
    else:
        x = R.vn15(tk)
        src = "vnstock15" if x is not None and (x.d == d).any() else "NONE"
    rows.append((d, tk, src))
c = pd.DataFrame(rows, columns=["d", "ticker", "src"])
c.to_csv(os.path.join(HERE, "out", "coverage_ledger.csv"), index=False)
print(c.src.value_counts(normalize=True).round(4).to_string())
print("mã không có bar nào:", sorted(set(c[c.src == "NONE"].ticker) - set(c[c.src != "NONE"].ticker)))
v = sorted(f[:10] for f in os.listdir(os.path.join(R.C, "vni_1m")))
print("VNINDEX 1m:", v[0], "->", v[-1], len(v), "ngày")
s = sorted({f[:10] for f in os.listdir(os.path.join(R.C, "stk_1m"))})
print("cổ phiếu DNSE 1m:", s[0], "->", s[-1], len(s), "ngày")
