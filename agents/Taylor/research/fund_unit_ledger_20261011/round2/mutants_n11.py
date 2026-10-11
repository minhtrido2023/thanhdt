# Mutant cho code N11 (commit 2) — (id, file, old, new).
P = "nav_period_returns.py"
S = "portfolio_status.py"
M_PERIOD = [
    ("N01", P, '"day": _period_result(ledger, i1 - 1, i1) if i1 else None,', '"day": _period_result(ledger, 0, i1) if i1 else None,'),
    ("N02", P, '"day": _period_result(ledger, i1 - 1, i1) if i1 else None,', '"day": _period_result(ledger, i1 - 1, i1),'),
    ("N03", P, '"day": _period_result(ledger, i1 - 1, i1) if i1 else None,', '"day": None,'),
    ("N04", P, '        "unit_price_ratio": factor,', '        "unit_price_ratio": round(factor, 5),'),
    ("N05", P, '        "unit_price_ratio": factor,', '        "unit_price_ratio": b["nav"] / a["nav"],'),
]
M_STATUS = [
    ("S01", S, 'day_chg_pct = (result["day"]["unit_price_ratio"] - 1) * 100 if result["day"] else None',
     'day_chg_pct = (today_row["nav"] / _prior_row["nav"] - 1) * 100'),
    ("S02", S, 'day_chg_pct = (result["day"]["unit_price_ratio"] - 1) * 100 if result["day"] else None',
     'day_chg_pct = (result["inception"]["unit_price_ratio"] - 1) * 100 + 1'),
    ("S03", S, '        inception_pct = result["inception"]["return_pct"]', '        inception_pct = (today_row["nav"] / 1e9 - 1) * 100'),
    ("S04", S, "load_nav_history(account, EXEC_DIR), load_inception(account))", "load_nav_history(account), load_inception(account))"),
    ("S05", S, '        for f in result["pending_flows"]:\n            print(f"portfolio_status: dòng tiền đã khai',
     '        for f in []:\n            print(f"portfolio_status: dòng tiền đã khai'),
    ("S06", S, '        print(f"portfolio_status: KHÔNG tính được tỉ suất NAV ({account} {date}) — in \'?\' thay "\n              f"cho phần trăm: {type(exc).__name__}: {exc}", file=sys.stderr)',
     '        pass'),
    ("S07", S, '    day_chg_pct = inception_pct = None\n    try:', '    day_chg_pct = inception_pct = 0.0\n    try:'),
]
import os
M = M_STATUS if os.environ.get("FU_TESTS") else M_PERIOD
