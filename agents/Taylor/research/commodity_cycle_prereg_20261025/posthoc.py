"""POST-HOC (không thuộc PREREG): kiểm tra biến thể tốt nhất lưới 1.05 + tái lập tay + ca MSR."""
import numpy as np, pandas as pd
import run as R
from scipy.stats import binomtest
# 1) tái lập tay 3 sự kiện chính
ev = pd.read_csv("events_main.csv")
for k in [1, 8, 19]:
    e = ev.iloc[k]; t = pd.Timestamp(e.entry); i = R.days.get_loc(t); j = min(i + 126, len(R.days) - 1)
    tk = e.exp.split(","); r = (R.close[tk].iloc[j] / R.close[tk].iloc[i] - 1).mean()
    print("recheck", e.family, e.entry, "r_exp csv=%.6f hand=%.6f" % (e.r_exp, r))
# 2) post-hoc 1.05: baseline cùng chân trời + LOCO + bỏ từng họ + DSR-kiểu (Bonferroni 9)
for hn, h in [("3M", 63), ("6M", 126), ("12M", 252)]:
    e = R.run(1.05, h); cm = e.groupby("cluster").X.mean(); n = len(cm)
    base = R.baseline(h); bmix = np.mean([base[f][0] for f in e.family])
    t = cm.mean() / (cm.std() / np.sqrt(n))
    from scipy.stats import t as T
    p1 = 1 - T.cdf(t, n - 1)
    lofo = {f: round(e[e.family != f].groupby("cluster").X.mean().mean(), 4) for f in e.family.unique()}
    loco = min(cm.drop(k).mean() for k in cm.index)
    print(f"1.05/{hn}: n_ev={len(e)} n_cl={n} mean_cl={cm.mean():.4f} ev_mean={e.X.mean():.4f} baseline_mix={bmix:.4f} "
          f"ev-base={e.X.mean()-bmix:.4f} t={t:.2f} p1={p1:.4f} p_bonf9={min(1,9*p1):.4f} loco_min={loco:.4f} lofo={lofo}")
    if hn == "3M":
        e.to_csv("events_posthoc_105_3M.csv", index=False)
# 3) MSR: đường giá vs mốc LAG (release 2026-10-22, entry 2026-10-29)
m = R.close["MSR"].loc["2025-06-01":]
me = m.resample("ME").last()
print("MSR month-end close:"); print((me / me.iloc[0]).round(2).to_string())
