#!/usr/bin/env python3
"""So BEFORE(Close) vs AFTER(Price) tren 4 CSV output cua rating_8l.py — job Taylor_20260802_081308.

Luu y phuong phap (bai hoc job Taylor_20260802_063752): pandas 3 StringDtype tra pd.NA khi astype(str)
va pd.NA != pd.NA -> dem nham la "khac". Phai fillna sentinel '<NA>' TRUOC khi so.
"""
import os, sys
import pandas as pd

SBX = sys.argv[1]
FILES = ["rating_8l.csv", "rating_8l_top30.csv", "rating_8l_buynow.csv", "rating_8l_screener.csv"]
KEY_INVARIANT = ["rating", "route", "zone_v2", "zone", "note", "redflag", "forensic", "golden_cell"]

for f in FILES:
    a = pd.read_csv(os.path.join(SBX, "BEFORE", "data", f))
    b = pd.read_csv(os.path.join(SBX, "AFTER", "data", f))
    print(f"\n=== {f} ===")
    print(f"  shape BEFORE={a.shape} AFTER={b.shape}")
    if set(a.columns) != set(b.columns):
        print("  !! COT KHAC:", set(a.columns) ^ set(b.columns)); continue
    ta, tb = set(a["ticker"]), set(b["ticker"])
    if ta != tb:
        print(f"  !! BO MA KHAC: chi BEFORE={sorted(ta-tb)} | chi AFTER={sorted(tb-ta)}")
    common = sorted(ta & tb)
    a = a.set_index("ticker").loc[common]
    b = b.set_index("ticker").loc[common]
    diffs = []
    for c in a.columns:
        x, y = a[c], b[c]
        if pd.api.types.is_bool_dtype(x) or pd.api.types.is_bool_dtype(y):
            m = x.astype(str).fillna("<NA>") != y.astype(str).fillna("<NA>")
            md = float("nan")
        elif pd.api.types.is_numeric_dtype(x) and pd.api.types.is_numeric_dtype(y):
            m = ~((x.isna() & y.isna()) | (x.sub(y).abs() <= 1e-9))
            md = (x - y).abs().max()
        else:
            m = x.astype(str).fillna("<NA>") != y.astype(str).fillna("<NA>")
            md = float("nan")
        n = int(m.sum())
        if n:
            diffs.append((c, n, md, list(a.index[m])[:5]))
    if not diffs:
        print("  IDENTICAL (moi cot, moi ma)")
    for c, n, md, ex in diffs:
        flag = "  <<< INVARIANT VI PHAM" if c in KEY_INVARIANT else ""
        print(f"  {c:<18} n_khac={n:<5} max|diff|={md}  vd={ex}{flag}")
