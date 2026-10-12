#!/usr/bin/env python3
"""Nghiệm thu 2 (CHỈ ĐỌC dữ liệu thật): bảng phần dư đẳng thức tiền toàn lịch sử + phân bố nhiễu.
Dùng: python3 history_residuals.py <đường dẫn worktree/bin> [asof]"""
import datetime, json, statistics, sys
sys.path.insert(0, sys.argv[1])
import cash_identity as ci
asof = datetime.date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else None
allv = []
for acct in ("SpaceX", "ZaloPay"):
    res = ci.check_account(acct, asof=asof)
    print(f"== {acct}: {len(res['windows'])} cửa sổ, ngưỡng ±{res['threshold_pct']}% NAV, "
          f"{len(res['suspects'])} vượt ngưỡng, {len(res['uncheckable'])} không kiểm được")
    print(ci._table(res))
    for w in res["suspects"]:
        print(ci.suspect_line(acct, w))
    allv += [(abs(w["pct_nav"]), acct, w) for w in res["windows"] if w["checkable"]]
vals = sorted(v[0] for v in allv)
def pct(p): return vals[min(len(vals) - 1, int(round(p / 100 * (len(vals) - 1))))]
print(f"\n== PHÂN BỐ |phần dư| theo % NAV, N={len(vals)} cửa sổ (2 tài khoản)")
print(f"median {statistics.median(vals):.4f} · p90 {pct(90):.4f} · p95 {pct(95):.4f} · p99 {pct(99):.4f} · max {vals[-1]:.4f}")
for cut in (0.005, 0.01, 0.02, 0.05, 0.1):
    print(f"  > {cut}%: {sum(v > cut for v in vals)} cửa sổ")
print("== 12 cửa sổ lớn nhất")
for v, acct, w in sorted(allv, key=lambda x: -x[0])[:12]:
    print(f"  {acct:8} {w['date0']} → {w['date1']}  {w['unexplained']:>12,.0f} VND  {w['pct_nav']:+.4f}%")
