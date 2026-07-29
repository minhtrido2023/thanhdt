# -*- coding: utf-8 -*-
"""lag_rating_order_gate_selfcheck.py — self-check cho trading_bot.plan.filter_lag_rating_orders
(lưới an toàn tầng ORDER của gate 8L rating ≤3 cho book LAG, chính sách user chốt 2026-07-27).

Chạy:  $DNA_PYEXE lag_rating_order_gate_selfcheck.py          (unit, bq giả lập — offline)
       $DNA_PYEXE lag_rating_order_gate_selfcheck.py --live   (thêm 2 phần chạm BQ thật:
           REPLAY case TRC 07-23 / MST 07-27, và REPLAY toàn bộ plan THẬT 07-20→07-28
           để xác nhận 0 lệnh nào khác bị đổi)

Khác lag_rating_filter_selfcheck.py: file kia kiểm hàm lọc ứng viên ở TẦNG TÍN HIỆU (DataFrame
candidate); file này kiểm việc áp cùng gate đó lên TỪNG ORDER trong TradePlan ở tầng executor.
"""
import os
import sys

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
sys.path.insert(0, WORKDIR)

import pandas as pd

from trading_bot import plan as plan_mod
from trading_bot.plan import PlannedOrder, TradePlan, filter_lag_rating_orders
from lag_rating_filter import lag_filter_low_rating

ASOF = "2026-07-27"
PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name}  {detail}")


def mk_plan(specs, plan_date=ASOF):
    """specs: list (ticker, book, side). qty/ref_price cố định — gate không phụ thuộc chúng."""
    orders = [PlannedOrder(id=f"{sd.upper()}-{tk}-{i:02d}", ticker=tk, side=sd, qty=1000,
                           ref_price=20000.0, book=bk)
              for i, (tk, bk, sd) in enumerate(specs)]
    return TradePlan(plan_date=plan_date, signal_date=plan_date, strategy="test",
                     strategy_version="0", state=3, state_name="NEUTRAL",
                     nav_basis={}, orders=orders, account="SELFCHECK")


def fake_deps(ratings, boom=False):
    """ratings: {ticker: rating|None}; None = mã không có dòng rating nào ≤ asof."""
    def _bq(sql):
        if boom:
            raise RuntimeError("BQ down")
        recs = [{"ticker": tk, "rating": rt, "time": pd.Timestamp(ASOF) - pd.Timedelta(days=5)}
                for tk, rt in ratings.items() if f"'{tk}'" in sql and rt is not None]
        return pd.DataFrame(recs, columns=["ticker", "rating", "time"])
    return lambda: (_bq, lag_filter_low_rating)


def run(specs, ratings, boom=False, deps=None, plan_date=ASOF):
    orig = plan_mod._rating_gate_deps
    plan_mod._rating_gate_deps = deps or fake_deps(ratings, boom=boom)
    try:
        return filter_lag_rating_orders(mk_plan(specs, plan_date=plan_date))
    finally:
        plan_mod._rating_gate_deps = orig


print("=" * 78)
print("  UNIT (bq giả lập)")
print("=" * 78)

# 1. LAG buy rating ≤3 → PASS nguyên, không đụng
p, blk = run([("VPB", "LAG", "buy"), ("CSV", "LAG", "buy")], {"VPB": 2, "CSV": 3})
check("LAG buy rating≤3 → giữ nguyên", len(p.orders) == 2 and not blk, f"{blk}")

# 2. LAG buy rating=4 (case TRC/MST) → LOẠI lệnh đó, mã ≤3 cùng plan vẫn còn
p, blk = run([("MST", "LAG", "buy"), ("VPB", "LAG", "buy")], {"MST": 4, "VPB": 2})
check("LAG buy rating=4 → LOẠI lệnh", [o.ticker for o in p.orders] == ["VPB"],
      f"{[o.ticker for o in p.orders]}")
check("… blocked ghi đủ ticker/rating/order_id",
      len(blk) == 1 and blk[0]["ticker"] == "MST" and blk[0]["rating"] == 4
      and blk[0]["order_id"] and blk[0]["action"] == "BLOCKED", f"{blk}")

# 3. BIÊN rating 3 giữ / 4 loại
p, blk = run([("A", "LAG", "buy")], {"A": 3})
check("rating == 3 → GIỮ", len(p.orders) == 1 and not blk, f"{blk}")
p, blk = run([("A", "LAG", "buy")], {"A": 4})
check("rating == 4 → LOẠI", len(p.orders) == 0 and len(blk) == 1, f"{blk}")
p, blk = run([("A", "LAG", "buy")], {"A": 8})
check("rating == 8 → LOẠI", len(p.orders) == 0 and len(blk) == 1, f"{blk}")

# 4. KHÔNG tra được rating của MỘT mã → chỉ mã ĐÓ bị loại (fail-closed từng mã)
p, blk = run([("NORATE", "LAG", "buy"), ("VPB", "LAG", "buy")], {"NORATE": None, "VPB": 2})
check("rating thiếu 1 mã → chỉ loại mã đó (fail-closed)",
      [o.ticker for o in p.orders] == ["VPB"] and len(blk) == 1
      and blk[0]["ticker"] == "NORATE" and blk[0]["rating"] is None, f"{blk}")

# 5. CẢ NGUỒN hỏng → fail-OPEN toàn plan + cảnh báo (đồng bộ gate tầng tín hiệu)
p, blk = run([("MST", "LAG", "buy"), ("VPB", "LAG", "buy")], {"MST": 4, "VPB": 2}, boom=True)
check("BQ hỏng → fail-OPEN, giữ nguyên MỌI lệnh", len(p.orders) == 2, f"{[o.ticker for o in p.orders]}")
check("… và phát 1 cảnh báo FAIL_OPEN",
      len(blk) == 1 and blk[0]["action"] == "FAIL_OPEN" and "BQ down" in blk[0]["reason"], f"{blk}")


def _boom_deps():
    raise ImportError("no module named simulate_holistic_nav")


p, blk = run([("MST", "LAG", "buy")], {}, deps=_boom_deps)
check("import nguồn hỏng → fail-OPEN, giữ nguyên",
      len(p.orders) == 1 and len(blk) == 1 and blk[0]["action"] == "FAIL_OPEN", f"{blk}")

# 6. PHẠM VI: chỉ LAG × buy. Book khác / chiều bán KHÔNG bị đụng dù rating xấu.
p, blk = run([("MST", "CAPIT", "buy"), ("MST", "custom30V_parking", "buy"),
              ("MST", "LAG", "sell"), ("MST", "BAL", "buy")], {"MST": 4})
check("book khác + LAG sell → KHÔNG đụng (đúng phạm vi chính sách)",
      len(p.orders) == 4 and not blk, f"{blk}")

# 7. Plan không có LAG buy → no-op, KHÔNG gọi nguồn rating (không tốn query/không phụ thuộc BQ)
called = {"n": 0}


def _counting_deps():
    called["n"] += 1
    raise AssertionError("không được gọi nguồn rating khi plan không có LAG buy")


p, blk = run([("VNM", "CAPIT", "buy")], {}, deps=_counting_deps)
check("plan không có LAG buy → no-op, không chạm nguồn", called["n"] == 0 and len(p.orders) == 1)

# 8. book "lag" chữ thường / side "BUY" hoa → vẫn bắt (plan LLM-authored không đảm bảo case)
p, blk = run([("MST", "lag", "BUY")], {"MST": 4})
check("case-insensitive book/side → vẫn LOẠI", len(p.orders) == 0 and len(blk) == 1, f"{blk}")

# 9. Nhiều lệnh CÙNG mã xấu → loại hết; thứ tự các lệnh còn lại giữ nguyên
p, blk = run([("VPB", "LAG", "buy"), ("MST", "LAG", "buy"), ("CSV", "LAG", "buy"),
              ("MST", "LAG", "buy")], {"VPB": 2, "MST": 4, "CSV": 3})
check("loại hết lệnh cùng mã xấu, giữ thứ tự phần còn lại",
      [o.ticker for o in p.orders] == ["VPB", "CSV"] and len(blk) == 2,
      f"{[o.ticker for o in p.orders]} {blk}")

if "--live" in sys.argv:
    print("=" * 78)
    print("  REPLAY 1 — 2 case thật TRC (2026-07-23) / MST (2026-07-27) qua BQ THẬT")
    print("=" * 78)
    # Tái dựng đúng kịch bản lỗ hổng: plan LLM-authored viết thẳng lệnh LAG cho mã rating=4
    # (2 case này ĐỜI THẬT bị chặn ở tầng tín hiệu nên chưa từng vào plan — đây là kiểm chứng
    # "NẾU lọt tới plan thì lưới executor có chặn không").
    for tk, day in (("TRC", "2026-07-23"), ("MST", "2026-07-27")):
        p = mk_plan([(tk, "LAG", "buy"), ("VPB", "LAG", "buy")], plan_date=day)
        p, blk = filter_lag_rating_orders(p)
        names = [b["ticker"] for b in blk if b["action"] == "BLOCKED"]
        fo = [b for b in blk if b["action"] == "FAIL_OPEN"]
        print(f"  asof={day}  blocked={[(b['ticker'], b['rating']) for b in blk]}")
        check(f"live: {tk} (8L=4) BỊ CHẶN @{day}", names == [tk] and not fo, f"{blk}")
        check(f"live: VPB (8L≤3) GIỮ @{day}", [o.ticker for o in p.orders] == ["VPB"],
              f"{[o.ticker for o in p.orders]}")

    print("=" * 78)
    print("  REPLAY 2 — MỌI plan THẬT 07-20→07-28: 0 lệnh nào bị đổi")
    print("=" * 78)
    import copy
    import glob
    import json
    import dataclasses
    from trading_bot.plan import load_plan

    files = sorted(glob.glob(os.path.join("data", "trade_plans", "plan_*_2026-07-2[0-8].json")))
    n_plans = n_orders = n_lagbuy = 0
    changed = []
    for f in files:
        label = os.path.basename(f)[len("plan_"):-len("_YYYY-MM-DD.json")]
        day = os.path.basename(f)[-len("YYYY-MM-DD.json"):-len(".json")]
        pl = load_plan(day, account=label)
        if pl is None:
            continue
        n_plans += 1
        n_orders += len(pl.orders)
        n_lagbuy += sum(1 for o in pl.orders
                        if (o.book or "").upper() == "LAG" and (o.side or "").lower() == "buy")
        before = [dataclasses.asdict(o) for o in pl.orders]
        pl, blk = filter_lag_rating_orders(pl)
        after = [dataclasses.asdict(o) for o in pl.orders]
        if before != after or blk:
            changed.append((os.path.basename(f), blk,
                            [o["ticker"] for o in before], [o["ticker"] for o in after]))
    print(f"  {n_plans} plan / {n_orders} lệnh / {n_lagbuy} lệnh LAG-buy đã replay")
    for c in changed:
        print(f"  ⚠ ĐỔI: {c[0]}  blocked={c[1]}  {c[2]} → {c[3]}")
    check("live: replay 07-20→07-28 — 0 lệnh thật bị đổi", not changed, f"{changed}")
    check("live: replay có chạm ít nhất 1 lệnh LAG-buy thật (test không rỗng)", n_lagbuy >= 1,
          f"n_lagbuy={n_lagbuy}")

print("=" * 78)
print(f"  TỔNG: {PASS} PASS / {FAIL} FAIL")
sys.exit(1 if FAIL else 0)
