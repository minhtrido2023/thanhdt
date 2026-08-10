#!/usr/bin/env python3
"""Thiet ke tham so: TRAN DUOI GIA co gioi han cho LAG tai phien 2/3 cua cua so entry.

Doc lai CSV su kien do boi measure_entry_lag.py. Khong goi BQ lai.

Nhanh do: tai phien e+k, cho phep mua neu Price[e+k] <= anchor*(1+cap).
  cap = 0     -> dung LUAT HIEN TAI (hard_no_chase_ceiling_vnd = anchor)
  cap = +inf  -> CHASE khong gioi han
  cap = 1..8% -> cac phuong an trung gian
"""
import numpy as np
import pandas as pd
from scipy import stats

CSV = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_lag_entrylag_20260810/exp_lag_entry_lag_events.csv"
df = pd.read_csv(CSV, parse_dates=["release", "entry"])

CAPS = [0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08, np.inf]


def arm(sub, k, cap):
    prem = sub[f"px_prem_{k}"].values
    ret = sub[f"ret_chase_{k}"].values
    ok = np.isfinite(prem) & np.isfinite(ret)
    filled = ok & (prem <= cap + 1e-12)
    n = ok.sum()
    fr = filled.sum() / n if n else np.nan
    cond = ret[filled].mean() if filled.any() else np.nan
    return fr, cond, (fr * cond if filled.any() else 0.0), filled, ok


for k in (1, 2):
    sub = df.dropna(subset=[f"px_prem_{k}", f"ret_chase_{k}"]).copy()
    print("=" * 84)
    print(f"PHIEN {k+1} CUA CUA SO (k={k})   N = {len(sub)} su kien doc lap "
          f"({sub['ticker'].nunique()} ma, {sub['release'].nunique()} ngay cong bo)")
    print("=" * 84)
    print(f"{'tran duoi':<14}{'fill%':>8}{'ret|fill':>11}{'ret*fill (von)':>17}"
          f"{'vs luat nay':>14}{'so nam thang':>14}")
    print("-" * 84)
    fr0, c0, e0, _, _ = arm(sub, k, 0.0)
    for cap in CAPS:
        fr, cond, eff, filled, ok = arm(sub, k, cap)
        # so nam ma nhanh nay >= nhanh cap=0
        wins = 0
        tot = 0
        for y, gg in sub.groupby("entry"):
            pass
        yrs = sub["entry"].dt.year
        for y in sorted(yrs.unique()):
            m = (yrs == y).values
            _, _, ey, _, _ = arm(sub[m], k, cap)
            _, _, e0y, _, _ = arm(sub[m], k, 0.0)
            tot += 1
            if ey >= e0y:
                wins += 1
        lbl = "KHONG GIOI HAN" if not np.isfinite(cap) else (
            "LUAT HIEN TAI" if cap == 0 else f"anchor +{cap*100:.0f}%")
        print(f"{lbl:<14}{fr*100:>7.1f}%{cond*100:>10.2f}%{eff*100:>16.2f}%"
              f"{(eff-e0)*100:>13.2f}%{wins:>8}/{tot}")
    print()

# ── kiem tra chon loc nguoc: nhom BI CHAN co te hon khong?
print("=" * 84)
print("KIEM TRA CHON LOC NGUOC (adverse selection cua tran anchor)")
print("=" * 84)
for k in (1, 2):
    sub = df.dropna(subset=[f"px_prem_{k}", f"ret_chase_{k}"])
    prem = sub[f"px_prem_{k}"].values
    ret = sub[f"ret_chase_{k}"].values
    passed = prem <= 1e-12
    a, b = ret[passed], ret[~passed]
    t, pv = stats.ttest_ind(a, b, equal_var=False)
    print(f"phien {k+1}: duoc-phep n={len(a)} ret {a.mean()*100:.2f}%  |  "
          f"BI-CHAN n={len(b)} ret {b.mean()*100:.2f}%  |  "
          f"Welch t={t:.2f} p={pv:.2e}  -> chenh {(b.mean()-a.mean())*100:+.2f}pp")
    # cum theo ngay cong bo (su kien don theo mua BCTC) — sai so chuan cum
    g = sub.assign(passed=passed).groupby("release").apply(
        lambda x: pd.Series({"d": x.loc[~x["passed"], f"ret_chase_{k}"].mean()
                             - x.loc[x["passed"], f"ret_chase_{k}"].mean()}),
        include_groups=False).dropna()
    tt, pp = stats.ttest_1samp(g["d"].values, 0.0)
    print(f"          cum theo ngay cong bo: n_cum={len(g)} chenh TB {g['d'].mean()*100:+.2f}pp "
          f"t={tt:.2f} p={pp:.2e}")

# ── leave-one-year-out cho phuong an de xuat
print()
print("=" * 84)
print("LEAVE-ONE-YEAR-OUT — 'anchor +3%' tai phien 3 (k=2) so voi luat hien tai")
print("=" * 84)
k, CAP = 2, 0.03
sub = df.dropna(subset=[f"px_prem_{k}", f"ret_chase_{k}"]).copy()
sub["year"] = sub["entry"].dt.year
_, _, eff_all, _, _ = arm(sub, k, CAP)
_, _, e0_all, _, _ = arm(sub, k, 0.0)
print(f"toan mau: {(eff_all-e0_all)*100:+.2f}pp")
print(f"{'bo nam':<10}{'chenh con lai':>16}")
for y in sorted(sub["year"].unique()):
    s2 = sub[sub["year"] != y]
    _, _, ea, _, _ = arm(s2, k, CAP)
    _, _, eb, _, _ = arm(s2, k, 0.0)
    print(f"{y:<10}{(ea-eb)*100:>15.2f}pp")
print()
print(f"{'nam':<8}{'N':>5}{'fill@0%':>9}{'fill@3%':>9}{'von@0%':>9}{'von@3%':>9}{'chenh':>9}")
for y, gg in sub.groupby("year"):
    f0, c0y, e0y, _, _ = arm(gg, k, 0.0)
    f3, c3y, e3y, _, _ = arm(gg, k, CAP)
    print(f"{y:<8}{len(gg):>5}{f0*100:>8.1f}%{f3*100:>8.1f}%"
          f"{e0y*100:>8.2f}%{e3y*100:>8.2f}%{(e3y-e0y)*100:>8.2f}%")
