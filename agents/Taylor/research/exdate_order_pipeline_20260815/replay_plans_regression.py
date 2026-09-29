#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy: cổng GDKHQ có đổi hành vi của MỘT plan lịch sử nào KHÔNG có sự kiện không?

Bất biến cần chứng minh (README §9 mục 3, đúng cách hai job trước đã làm): trên TOÀN BỘ kho
plan thật đã chạy, mọi plan mà không mã nào có `exright_date == plan_date` phải đi qua cổng
với **0 lệnh bị bỏ, 0 lệnh đổi giá trị**. Cổng chỉ được động vào đúng những ngày có sự kiện.

Chạy KHÔNG cần DNSE: dùng resolver GIẢ luôn báo lỗi. Đó là phép thử MẠNH HƠN chứ không yếu
hơn — nếu cổng lỡ chạm một mã lẽ ra không thuộc phạm vi, resolver giả sẽ khiến lệnh đó bị BỎ
và phép hồi quy đỏ ngay. Plan có sự kiện thật được liệt kê riêng để đọc bằng mắt.

Lịch sự kiện tra BQ MỘT lần cho toàn bộ mã × toàn bộ khoảng ngày của kho plan.

Chạy:
  python3 mike/agents/Taylor/research/exdate_order_pipeline_20260815/replay_plans_regression.py
"""
import glob
import json
import os
import sys

WC = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WC)
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")

from trading_bot import price_frame as pf                           # noqa: E402
from trading_bot.exdate_gate import apply_exdate_gate               # noqa: E402
from trading_bot.plan import load_plan                              # noqa: E402


def boom(*a, **k):
    """Resolver không bao giờ thành công — mọi mã LỌT vào phạm vi cổng sẽ bị BỎ và lộ ra."""
    return {"ok": False, "gate": "REPLAY", "ex_today": True,
            "reason": "resolver giả của phép hồi quy — mã này lẽ ra không được vào phạm vi cổng"}


def main():
    paths = sorted(glob.glob(os.path.join(WC, "data", "trade_plans", "plan_*.json")))
    plans = []
    for p in paths:
        base = os.path.basename(p)[len("plan_"):-len(".json")]
        acct, _, pdate = base.rpartition("_")
        if not acct or len(pdate) != 10:
            continue
        try:
            pl = load_plan(pdate, account=acct)
        except Exception as exc:                                    # noqa: BLE001
            print(f"  bỏ qua {base}: không nạp được ({type(exc).__name__}: {exc})")
            continue
        if pl and pl.orders:
            plans.append((acct, pdate, pl))
    if not plans:
        print("KHÔNG có plan nào để replay — không kết luận được gì.")
        return 1

    tickers = sorted({o.ticker for _, _, pl in plans for o in pl.orders})
    dates = sorted({d for _, d, _ in plans})
    print(f"Kho plan: {len(plans)} plan · {len(tickers)} mã · {dates[0]} → {dates[-1]}")

    import datetime as dt
    lo = (dt.date.fromisoformat(dates[0]) - dt.timedelta(days=2)).isoformat()
    events = pf.pricing_events(tickers, since=lo, until=dates[-1])
    emap = pf.events_by_ticker_date(events)
    print(f"Sự kiện làm-đổi-giá giao với kho plan: {len(events)}")

    n_touch = n_clean = 0
    dirty = []
    for acct, pdate, pl in plans:
        before = [(o.id, o.ticker, o.side, o.qty, o.ref_price,
                   o.hard_no_chase_ceiling_vnd) for o in pl.orders]
        has_ev = any(pf.events_on(emap, o.ticker, pdate) for o in pl.orders)
        pl, adj = apply_exdate_gate(pl, None, pdate, events_map=emap, resolver=boom)
        after = [(o.id, o.ticker, o.side, o.qty, o.ref_price,
                  o.hard_no_chase_ceiling_vnd) for o in pl.orders]
        changed = before != after
        if has_ev:
            n_touch += 1
            evs = sorted({o.ticker for o in
                          [x for x in [type("o", (), {"ticker": t})() for t in
                                       {b[1] for b in before}]]
                          if pf.events_on(emap, o.ticker, pdate)})
            print(f"  [CÓ SỰ KIỆN] {acct} {pdate}: mã {evs} — "
                  f"{len([a for a in adj if a['action'] == 'BLOCKED'])} lệnh bị cổng xử lý")
            continue
        n_clean += 1
        if changed:
            dirty.append((acct, pdate, before, after))

    print(f"\nPlan KHÔNG có sự kiện: {n_clean} · plan CÓ sự kiện: {n_touch}")
    if dirty:
        print(f"❌ HỎNG BẤT BIẾN — {len(dirty)} plan ngày thường bị cổng làm đổi:")
        for acct, pdate, b, a in dirty[:10]:
            print(f"   {acct} {pdate}\n     trước: {b}\n     sau  : {a}")
        return 1
    print(f"✅ BẤT BIẾN GIỮ: {n_clean}/{n_clean} plan không có sự kiện đi qua cổng với "
          f"0 lệnh bị bỏ, 0 lệnh đổi giá trị — kể cả khi resolver LUÔN thất bại.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
