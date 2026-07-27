# -*- coding: utf-8 -*-
"""Self-check netting lệnh ngược chiều cùng mã — `trading_bot.plan.net_offsetting_orders`.

Case gốc (plan ZaloPay 2026-07-27): SELL VPB 800 (custom30V_parking) + BUY VPB 700 (LAG)
cùng 1 plan/ngày/account → chỉ nên gửi 1 lệnh NET SELL 100cp ra broker, 700cp chuyển nội bộ.

Chạy: python3 net_offsetting_orders_selfcheck.py   (không phụ thuộc pickle/pandas)
KHÔNG đọc broker/BQ thật — thuần logic trên PlannedOrder/TradePlan.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trading_bot import plan as planmod  # noqa: E402
from trading_bot.plan import (PlannedOrder, TradePlan, net_offsetting_orders,  # noqa: E402
                              filter_excluded_tickers, cap_lag_orders)

FAILS = []
NCHECK = [0]


def check(name, cond, detail=""):
    NCHECK[0] += 1
    print(("  ✅ " if cond else "  ❌ ") + name + (f" — {detail}" if detail else ""))
    if not cond:
        FAILS.append(name)


def mkplan(orders, plan_date="2026-07-27"):
    return TradePlan(plan_date=plan_date, signal_date="2026-07-24", strategy="V2.4",
                     strategy_version="r3", state=3, state_name="NEUTRAL",
                     nav_basis={}, orders=orders, account="selfcheck_net")


def order(tk, side, qty, px=24_900, book="LAG", play="", pri=5, urg="normal",
          note="", dcf=None, dcf_reason=""):
    return PlannedOrder(id=f"{side.upper()}-{tk}-{pri:02d}", ticker=tk, side=side, qty=qty,
                        ref_price=px, book=book, play_type=play, priority=pri, urgency=urg,
                        note=note, dcf_check=dcf, dcf_override_reason=dcf_reason)


# ── A. CASE THẬT VPB: SELL 800 park + BUY 700 LAG → 1 lệnh NET SELL 100 ────────────────
print("\nA. Case thật VPB (SELL 800 custom30V_parking + BUY 700 LAG)")
p, adj = net_offsetting_orders(mkplan([
    order("VPB", "sell", 800, book="custom30V_parking", play="PARK_TRIM", pri=1, urg="high",
          note="trim park"),
    order("VPB", "buy", 700, book="LAG", play="LAG_LO", pri=2, note="LAG entry"),
]))
check("chỉ còn 1 lệnh ra broker", len(p.orders) == 1, f"{len(p.orders)} lệnh")
o = p.orders[0]
check("net là SELL (bên bán lớn hơn)", o.side == "sell", f"side={o.side}")
check("qty net = 800-700 = 100", o.qty == 100, f"qty={o.qty}")
check("book net = bên lớn (custom30V_parking)", o.book == "custom30V_parking", f"book={o.book}")
check("priority giữ sell-first (min bên dom = 1)", o.priority == 1, f"pri={o.priority}")
check("urgency high (bên bán high)", o.urgency == "high", f"urg={o.urgency}")
check("net SELL → dcf_check = None", o.dcf_check is None, f"dcf={o.dcf_check}")
check("adj ghi 1 record NETTED", len(adj) == 1 and adj[0]["action"] == "NETTED")
r = adj[0]
check("adj.internal_qty = 700 (min mua/bán)", r["internal_qty"] == 700, f"{r['internal_qty']}")
check("adj.net_qty = -100", r["net_qty"] == -100, f"{r['net_qty']}")
# (b) book-level ledger giữ nguyên trong adj: leg gốc từng book còn đủ để audit/báo cáo
check("buy_legs giữ đúng book+qty LAG", r["buy_legs"] == [{"book": "LAG", "qty": 700, "note": "LAG entry"}],
      f"{r['buy_legs']}")
check("sell_legs giữ đúng book+qty park",
      r["sell_legs"] == [{"book": "custom30V_parking", "qty": 800, "note": "trim park"}],
      f"{r['sell_legs']}")

# ── B. net=0 (mua=bán) → KHÔNG gửi lệnh nào ───────────────────────────────────────────
print("\nB. net=0 — mua 500 = bán 500 → 0 lệnh ra broker (100% nội bộ)")
p, adj = net_offsetting_orders(mkplan([
    order("HPG", "buy", 500, book="LAG"),
    order("HPG", "sell", 500, book="custom30V_parking"),
]))
check("0 lệnh ra broker", len(p.orders) == 0, f"{len(p.orders)} lệnh")
check("adj = INTERNAL_ONLY", len(adj) == 1 and adj[0]["action"] == "INTERNAL_ONLY")
check("internal_qty = 500", adj[0]["internal_qty"] == 500)
check("net_qty = 0, net_side None", adj[0]["net_qty"] == 0 and adj[0]["net_side"] is None)

# ── C. bên MUA lớn hơn → net BUY, book bên mua, dcf giữ nguyên ─────────────────────────
print("\nC. Bên mua lớn hơn (BUY 900 LAG + SELL 200 park) → NET BUY 700 book LAG")
dcf = {"status": "CHEAP", "robust": True, "margin_of_safety": 0.2, "as_of": "2026-07-24"}
p, adj = net_offsetting_orders(mkplan([
    order("SSI", "buy", 900, book="LAG", play="LAG_LO", pri=3, dcf=dcf, dcf_reason="ok"),
    order("SSI", "sell", 200, book="custom30V_parking", pri=1),
]))
o = p.orders[0]
check("net BUY", o.side == "buy" and o.qty == 700, f"{o.side} {o.qty}")
check("book = LAG (bên mua lớn)", o.book == "LAG", f"book={o.book}")
check("net BUY → dcf_check giữ từ leg mua dom", o.dcf_check == dcf, f"dcf={o.dcf_check}")
check("dcf_override_reason giữ", o.dcf_override_reason == "ok")

# ── D. khác mã / một chiều → GIỮ NGUYÊN, không đổi hành vi ─────────────────────────────
print("\nD. Không có đối ứng — giữ nguyên toàn bộ")
orders_in = [
    order("AAA", "buy", 100, book="LAG"),
    order("BBB", "sell", 200, book="custom30V_parking"),
    order("CCC", "buy", 300, book="BAL"),
    order("CCC", "buy", 400, book="LAG"),   # 2 buy CÙNG chiều 1 mã → KHÔNG gộp
]
p, adj = net_offsetting_orders(mkplan(list(orders_in)))
check("số lệnh giữ nguyên = 4", len(p.orders) == 4, f"{len(p.orders)}")
check("không có netting nào", adj == [], f"adj={adj}")
check("2 buy CCC cùng chiều KHÔNG bị gộp",
      sum(1 for x in p.orders if x.ticker == "CCC") == 2)
check("thứ tự xuất hiện giữ nguyên",
      [x.id for x in p.orders] == [x.id for x in orders_in])

# ── E. (e) không sai giá trị vốn/exposure: Δbroker = net; tổng leg bảo toàn ────────────
print("\nE. Bảo toàn kinh tế — thay đổi vị thế broker = đúng net, nội bộ không tạo/mất cp")
p, adj = net_offsetting_orders(mkplan([
    order("VPB", "sell", 800, px=24_900, book="custom30V_parking"),
    order("VPB", "buy", 700, px=24_900, book="LAG"),
]))
o = p.orders[0]
broker_delta = (-o.qty if o.side == "sell" else o.qty)   # cp broker thay đổi
book_delta = 700 - 800                                    # LAG +700, park -800
check("Δ vị thế broker = Σ Δ book (=-100)", broker_delta == book_delta,
      f"broker={broker_delta} book={book_delta}")
# giá trị 1 lệnh net + phần nội bộ = đúng ý định gốc (không phóng đại/thu nhỏ vốn)
check("giá trị lệnh net = |net|×giá", abs(o.value - 100 * 24_900) < 1,
      f"value={o.value}")

# ── F. Tích hợp pipeline: filter_excluded → NET → cap_lag (đúng thứ tự bot_execute) ────
print("\nF. Tích hợp: net TRƯỚC cap_lag — bên bán lớn → net SELL không bị trần %ADV buy")
_orig = planmod._adv_for_gate
# ADV nhỏ để nếu cap_lag áp NHẦM lên phần gross 700 sẽ TRIM/BLOCK; net SELL không được đụng
planmod._adv_for_gate = lambda tk, asof: (1e9, "2026-07-26", None)  # trần buy = 20%×1tỷ=200tr
try:
    pl = mkplan([
        order("VPB", "sell", 800, px=24_900, book="custom30V_parking", pri=1, urg="high"),
        order("VPB", "buy", 700, px=24_900, book="LAG", pri=2),
    ])
    pl, _ = filter_excluded_tickers(pl, [])
    pl, net_adj = net_offsetting_orders(pl)
    pl, lag_adj = cap_lag_orders(pl, "SpaceX", live_labels=["SpaceX"], account_mode="live")
    check("sau net: 1 lệnh SELL 100", len(pl.orders) == 1 and pl.orders[0].side == "sell"
          and pl.orders[0].qty == 100, f"{[(x.side, x.qty) for x in pl.orders]}")
    check("cap_lag KHÔNG đụng lệnh net SELL (không phải LAG-buy)", lag_adj == [],
          f"lag_adj={lag_adj}")

    print("\nF2. Bên MUA lớn → net BUY vẫn bị cap_lag áp trần %ADV lên phần dư")
    pl2 = mkplan([
        order("MWG", "buy", 900, px=24_900, book="LAG", pri=2),   # net BUY 700
        order("MWG", "sell", 200, px=24_900, book="custom30V_parking", pri=1),
    ])
    pl2, _ = net_offsetting_orders(pl2)
    check("net BUY 700 book LAG", pl2.orders[0].side == "buy" and pl2.orders[0].qty == 700
          and pl2.orders[0].book == "LAG")
    pl2, lag_adj2 = cap_lag_orders(pl2, "SpaceX", live_labels=["SpaceX"], account_mode="live")
    # 700×24900 = 17.43tr > trần 200tr? Không — 17.43tr < 200tr, KHÔNG bị trim. Dùng ADV nhỏ hơn:
    check("net BUY được cap_lag XÉT (là LAG-buy) — ADV lớn nên qua",
          all(x.side == "buy" for x in pl2.orders))
    # ép trần rất nhỏ để chứng minh cap_lag THẬT SỰ áp lên net BUY
    planmod._adv_for_gate = lambda tk, asof: (5e6, "2026-07-26", None)  # trần=20%×5tr=1tr < 1 lô
    pl3 = mkplan([order("MWG", "buy", 900, px=24_900, book="LAG"),
                  order("MWG", "sell", 200, px=24_900, book="custom30V_parking")])
    pl3, _ = net_offsetting_orders(pl3)
    pl3, lag_adj3 = cap_lag_orders(pl3, "SpaceX", live_labels=["SpaceX"], account_mode="live")
    check("trần cực nhỏ → net BUY bị cap_lag BLOCK (chứng minh cap áp lên phần dư)",
          len(pl3.orders) == 0 and lag_adj3 and lag_adj3[0]["action"] == "BLOCKED",
          f"orders={len(pl3.orders)} adj={lag_adj3}")
finally:
    planmod._adv_for_gate = _orig

# ── G. Nhiều leg mỗi bên: net theo tổng, book = leg lớn nhất bên dom ───────────────────
print("\nG. Nhiều leg mỗi chiều — net theo tổng, book = leg lớn nhất bên dominant")
p, adj = net_offsetting_orders(mkplan([
    order("FPT", "sell", 300, book="custom30V_parking", pri=1),
    order("FPT", "sell", 500, book="BAL", pri=2),            # tổng bán 800
    order("FPT", "buy", 200, book="LAG", pri=3),             # tổng mua 200 → net SELL 600
]))
o = p.orders[0]
check("net SELL 600 (800-200)", o.side == "sell" and o.qty == 600, f"{o.side} {o.qty}")
check("book = leg bán lớn nhất (BAL 500)", o.book == "BAL", f"book={o.book}")
check("internal = 200", adj[0]["internal_qty"] == 200)
check("adj ghi đủ 2 sell_legs + 1 buy_leg",
      len(adj[0]["sell_legs"]) == 2 and len(adj[0]["buy_legs"]) == 1)

print(f"\n{'='*60}\n{NCHECK[0]} checks, {len(FAILS)} FAIL")
if FAILS:
    for f in FAILS:
        print("  ❌", f)
    sys.exit(1)
print("✅ TẤT CẢ PASS")
