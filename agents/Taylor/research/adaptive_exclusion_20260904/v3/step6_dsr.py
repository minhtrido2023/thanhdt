"""
Bước 2.4 — DSR trên chuỗi excess-return (gate E vs no-gate A) OOS 2020+.
N_TRIALS tổng cả 3 vòng: v1=5 (kiến trúc gate ban đầu, 5 biến thể ngưỡng/luật đã thử) +
v2=1 (rule2 IntCov->EBITDA) + v3=1 (tiêu chí chọn ngưỡng IS-only percentile-95) = 7.
"""
import sys, math
import numpy as np, pandas as pd

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from dsr_pbo_annex import moments, expected_max_sr, dsr

A = pd.read_csv("../cache/nav_baseline_nobanned.csv", parse_dates=["date"]).set_index("date")["nav"]
E = pd.read_csv("cache/nav_scenarioE.csv", parse_dates=["date"]).set_index("date")["nav"]

A = A.sort_index(); E = E.sort_index()
common = A.index.intersection(E.index)
A = A.loc[common]; E = E.loc[common]

oos_mask = common >= pd.Timestamp("2020-01-01")
A_oos = A[oos_mask]; E_oos = E[oos_mask]
A_oos = A_oos / A_oos.iloc[0]; E_oos = E_oos / E_oos.iloc[0]

rA = A_oos.pct_change().dropna()
rE = E_oos.pct_change().dropna()
excess = (rE - rA).dropna()

print(f"n common daily obs OOS: {len(excess)}")
print(f"excess mean (daily): {excess.mean():.6f}  std: {excess.std():.6f}")

sr_hat, g3, g4 = moments(excess.values)
T = len(excess)
N_TRIALS = 7
var_sr = 1.0 / T  # per-obs SR variance approx (BLdP simplification used elsewhere in dsr_pbo_annex)
sr0 = expected_max_sr(var_sr, N_TRIALS)
p, stat = dsr(sr_hat, sr0, g3, g4, T)

ann = 252.0
print(f"\nPer-obs SR_hat (E-A excess): {sr_hat:.5f}  (annualized ~{sr_hat*math.sqrt(ann):.3f})")
print(f"N_TRIALS (v1=5 + v2=1 + v3=1): {N_TRIALS}")
print(f"SR0 (expected max SR under null, N={N_TRIALS} trials): {sr0:.5f}")
print(f"DSR = P(true SR > SR0) = {p:.4f}")
print(f"{'RED FLAG: DSR<0.95' if p < 0.95 else 'DSR>=0.95'}")

# also report OOS Sharpe of E and A directly (not excess) as context
def full_sharpe(r):
    return r.mean()/r.std()*math.sqrt(ann) if r.std() > 0 else 0
print(f"\ncontext: OOS annualized Sharpe A={full_sharpe(rA):.3f}  E={full_sharpe(rE):.3f}")
