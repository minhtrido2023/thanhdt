#!/usr/bin/env python3
"""Selfcheck `egg_transfer_alert.py` — chạy THẬT `check_plan_funding` trên broker stub (không mạng).

Bất biến chính: số tiền cảnh báo "cần chuyển" X thoả — sau khi cộng X vào hũ tiền mặt, gate KHÔNG còn
BLOCK; và trừ đi 1 bước làm tròn (0,1tr) thì vẫn BLOCK. Tức cảnh báo biến mất ĐÚNG khi user chuyển đủ.
Chạy: python3 bin/egg_transfer_alert_selfcheck.py   (độc lập TZ; thử `env -u TZ` và `TZ=America/New_York`)
"""
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wc_paths  # noqa: E402

sys.path.insert(0, wc_paths.find_wc_root(__file__))
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")

import egg_transfer_alert as E                                      # noqa: E402
from trading_bot.plan_funding_gate import check_plan_funding       # noqa: E402

PASS = FAIL = 0


def ck(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} — {detail}")


def order(t, qty, px, side="buy", priority=5):
    o = types.SimpleNamespace(ticker=t, qty=qty, ref_price=px, side=side, id=f"{side}-{t}",
                              cash_only=True, loan_package_id=None, priority=priority)
    return o


class Broker:
    """Cash-only: pp0Buy = hũ tiền mặt (cash). Chuyển egg → cash ⇒ cộng thẳng vào hũ."""
    def __init__(self, pot):
        self.pot = pot
        self.client = types.SimpleNamespace(loan_package_id=None)
        self._resolve_loan_package_id = lambda t, *a, **k: 1841

    def get_buying_power(self, symbol, price, loan_package_id=None):
        return float(self.pot)

    def get_cash(self):
        return float(self.pot)


def fund(orders, pot):
    p = types.SimpleNamespace(orders=orders, account="SpaceX", plan_date="2026-10-26")
    return check_plan_funding(p, Broker(pot), "live")


print("A. thiếu tiền, egg đủ bù")
orders = [order("AAA", 10_000, 20_000)]                       # mua 200tr (+phí)
f = fund(orders, 50_000_000)
d = E.decide(f, 300_000_000)
ck("BLOCK → SHORT_EGG_COVERS", f["action"] == "BLOCK" and d["status"] == "SHORT_EGG_COVERS", (f["action"], d))
ck("X làm gate hết BLOCK", fund(orders, 50_000_000 + d["short"])["action"] == "OK", d)
ck("X − 0,1tr vẫn BLOCK (không báo thừa quá 1 bước làm tròn)",
   fund(orders, 50_000_000 + d["short"] - E.ROUND_UP_VND)["action"] == "BLOCK", d)
msg = E.render("SpaceX", "2026-10-26", "08:30", d, f, 300_000_000)
ck("tin nhắn nêu số tiền + hạn 09:05", "CHUYỂN" in msg and "09:05" in msg and f"{d['short']/1e6:,.1f}tr" in msg, msg)

print("B. egg không đủ bù → báo ĐỎ, nêu phần thiếu thêm")
d2 = E.decide(f, 40_000_000)
ck("SHORT_EGG_INSUFFICIENT", d2["status"] == "SHORT_EGG_INSUFFICIENT", d2)
ck("tin nhắn nêu 'THIẾU CẢ KHI CHUYỂN HẾT'", "THIẾU CẢ KHI CHUYỂN HẾT" in E.render("SpaceX", "x", "08:30", d2, f, 40_000_000))

print("C. đủ tiền → im lặng")
f3 = fund(orders, 500_000_000)
ck("OK → FUNDED, short=0", E.decide(f3, 300_000_000) == {"status": "FUNDED", "short": 0.0}, f3["action"])
ck("biên: sức mua đúng bằng Σ mua → FUNDED", E.decide(fund(orders, f["need_vnd"]), 0)["status"] == "FUNDED")

print("D. JIT-sell cùng plan trừ vào phần cần chuyển")
orders_j = orders + [order("BBB", 5_000, 20_000, side="sell", priority=1)]
fj = fund(orders_j, 50_000_000)
dj = E.decide(fj, 300_000_000)
ck("có JIT ⇒ cần chuyển ÍT hơn không JIT", dj["short"] < d["short"], (dj, d))
ck("X(JIT) làm gate hết BLOCK", fund(orders_j, 50_000_000 + dj["short"])["action"] == "OK", dj)

print("E. không áp dụng / không đo được → KHÔNG báo")
ck("plan chỉ có lệnh bán → NOT_APPLICABLE",
   E.decide(fund([order("CCC", 100, 10_000, side="sell")], 0), 1e9)["status"] == "NOT_APPLICABLE")
ck("UNVERIFIED → không báo (bot cũng không chặn)", E.decide({"action": "UNVERIFIED"}, 1e9)["status"] == "UNVERIFIED")

print(f"\n{PASS} PASS / {FAIL} FAIL")
sys.exit(1 if FAIL else 0)
