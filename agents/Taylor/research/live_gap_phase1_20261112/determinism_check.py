"""So 2 ledger cùng cấu hình khác AUDIT_END trên các phiên CHUNG (job Taylor_20261112_104204, tiền đề a).
Usage: determinism_check.py A.csv B.csv"""
import sys, pandas as pd
def daily(p):
    X = pd.read_csv(p, low_memory=False); X = X[X.record_type == "DAILY"].copy()
    X["ymd"] = pd.to_datetime(X["ymd"].astype(str)); return X.set_index("ymd")["combined_nav"].astype(float)
A, B = daily(sys.argv[1]), daily(sys.argv[2]); c = A.index.intersection(B.index)
d = (A[c] - B[c]).abs(); m = c.to_period("M")
ra, rb = A[c].groupby(m).last().pct_change(), B[c].groupby(m).last().pct_change()
dm = (ra - rb).abs(); flips = ((ra * rb) < 0).sum()
print(f"common_days={len(c)} days_dNAV>1VND={(d>1).sum()} first_diff={d[d>1].index.min() if (d>1).any() else None} "
      f"max_dNAV={d.max():.0f} months_differ(>1e-9)={(dm>1e-9).sum()}/{dm.notna().sum()} sign_flips={flips} "
      f"nav_end_common A={A[c].iloc[-1]:.0f} B={B[c].iloc[-1]:.0f}")
