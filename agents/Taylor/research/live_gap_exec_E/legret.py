"""Lợi suất kỳ mỗi ledger Luồng E (DAILY combined_nav; gốc = NAV đóng cửa trước cửa sổ, như decompose3) + md5 → legs.csv"""
import glob, hashlib, os, re, sys
import pandas as pd
R = os.path.dirname(os.path.abspath(__file__)); rows = []
for f in sorted(glob.glob(f"{R}/ledgers/*gapE_*.csv")):
    tag = re.search(r"exp_exp_(gapE_[A-Za-z0-9_]+?)_univpit", f).group(1)
    X = pd.read_csv(f, low_memory=False); D = X[X.record_type == "DAILY"].copy()
    D["d"] = pd.to_datetime(D.ymd.astype(str).str[:10]); n = D.set_index("d").sort_index().combined_nav.astype(float)
    a = "2026-06-30" if "_SX" in tag else "2026-07-06"; b = "2026-11-11"
    if "TBv" in tag: continue
    nA = n[n.index <= a]; n0 = float(nA.iloc[-1]) if len(nA) else float(n.iloc[0])
    rows.append(dict(tag=tag, r_ky_pct=round(100 * (float(n[n.index <= b].iloc[-1]) / n0 - 1), 4),
                     md5=hashlib.md5(open(f, "rb").read()).hexdigest()))
T = pd.DataFrame(rows); T.to_csv(f"{R}/legs.csv", index=False); print(T.to_string(index=False))
