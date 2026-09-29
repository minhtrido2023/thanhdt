import numpy as np
from scipy import stats

# name, 12mo_ret, 24mo_ret, months_uptrend, drawdown_pct(negative), decline_days, recovery_pct, recovery_days, breadth_heal_sessions
rows = [
    ("2007-2009 Wave1",   182.52, 393.93, 3.8,  -79.88, 715,  165.00, 240, 10),
    ("2011-2012 Wave2/3",  66.47, -42.52, 2.8,  -46.05, 1107,  40.68, 217, 91),
    ("2018",                65.44, 110.42, 1.8,  -26.21, 204,   11.56, 449, None),
    ("2020 COVID",           9.37,  -8.75, 14.8, -33.50, 62,   131.88, 653, 12),
    ("2022",                33.71,  59.93, 5.3,  -40.34, 313,   36.58, 295, 47),
    ("07/2026 (partial)",   48.14,  51.44, 1.3,  -13.46, 65,     9.80,  38, 5),
]

names = [r[0] for r in rows]
r12   = np.array([r[1] for r in rows])
r24   = np.array([r[2] for r in rows])
mup   = np.array([r[3] for r in rows])
dd    = np.array([r[4] for r in rows])
ddays = np.array([r[5] for r in rows])
rec_pct = np.array([r[6] for r in rows])
rec_days= np.array([r[7] for r in rows])
heal  = [r[8] for r in rows]

def report(xname, x, yname, y, n_note=""):
    pear = stats.pearsonr(x, y)
    spear = stats.spearmanr(x, y)
    print(f"{xname} vs {yname} (N={len(x)}{n_note}): Pearson r={pear.statistic:+.3f} (p={pear.pvalue:.3f}) | Spearman rho={spear.statistic:+.3f} (p={spear.pvalue:.3f})")

print("=== Full N=6 (bao gồm 07/2026 partial/right-censored cho recovery) ===")
report("12mo_return", r12, "drawdown_pct", dd)
report("24mo_return", r24, "drawdown_pct", dd)
report("months_uptrend", mup, "drawdown_pct", dd)
report("12mo_return", r12, "decline_days", ddays)
report("24mo_return", r24, "decline_days", ddays)
report("months_uptrend", mup, "decline_days", ddays)
report("12mo_return", r12, "recovery_pct", rec_pct)
report("12mo_return", r12, "recovery_days", rec_days)
report("months_uptrend", mup, "recovery_days", rec_days)

print("\n=== N=5, loại 07/2026 (recovery chưa kết thúc, right-censored - không nên coi 'recovery' của nó là hoàn chỉnh) ===")
r12_5, dd_5, ddays_5, recpct_5, recdays_5, mup_5 = r12[:5], dd[:5], ddays[:5], rec_pct[:5], rec_days[:5], mup[:5]
report("12mo_return", r12_5, "drawdown_pct", dd_5, " N=5")
report("12mo_return", r12_5, "decline_days", ddays_5, " N=5")
report("12mo_return", r12_5, "recovery_pct", recpct_5, " N=5")
report("12mo_return", r12_5, "recovery_days", recdays_5, " N=5")
report("months_uptrend", mup_5, "decline_days", ddays_5, " N=5")
report("months_uptrend", mup_5, "recovery_days", recdays_5, " N=5")

# recovery speed rate = %/day
rate = rec_pct/rec_days
print("\nrecovery rate (%/ngày) mỗi episode:")
for n,v in zip(names, rate):
    print(f"  {n}: {v:.4f} %/ngày")
report("12mo_return", r12, "recovery_rate(%/day)", rate)
report("12mo_return", r12[:5], "recovery_rate(%/day)_N5", rate[:5], " N=5")

print("\n=== N=5, loại 2007-2009 (thị trường mỏng, có thể là outlier cực đoan khác chất so với 5 case sau) ===")
idx = slice(1,6)
report("12mo_return", r12[idx], "drawdown_pct", dd[idx], " N=5 excl2007")
report("months_uptrend", mup[idx], "drawdown_pct", dd[idx], " N=5 excl2007")
report("12mo_return", r12[idx], "decline_days", ddays[idx], " N=5 excl2007")
report("months_uptrend", mup[idx], "decline_days", ddays[idx], " N=5 excl2007")
report("12mo_return", r12[idx], "recovery_rate(%/day)", rate[idx], " N=5 excl2007")
