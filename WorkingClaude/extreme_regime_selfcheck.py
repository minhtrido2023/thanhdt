# -*- coding: utf-8 -*-
"""Regression + behaviour self-check for the EXTREME-regime execution gate.

Drives trading_bot.executor.Executor with a fake broker/quote (no network, no live state).
Asserts:
  A. extreme_regime_enabled=False  → NORMAL path byte-identical (sell caps at ref×(1−3%),
     buy places normally, slice-mult ×1.0, _extreme_regime always False).
  B. extreme_regime_enabled=True   → 2-poll confirm, then SELL sells-to-floor, BUY pauses,
     cancel/reprice cadence shortens ×extreme_slice_mult.

Run: python extreme_regime_selfcheck.py   (exit 0 = all pass, non-zero = a check failed)
"""
import datetime as dt
import glob
import os
import sys

from trading_bot.config import DEFAULTS, EXEC_DIR
from trading_bot.plan import PlannedOrder, TradePlan
from trading_bot.executor import Executor
from trading_bot.vn_market import round_price

# Executor.__init__ eagerly loads state.json from the DEFAULT (account, plan_date) path
# BEFORE any test code can redirect it — a stale file from an earlier run (same account
# tag) silently corrupts this run's starting state (found 2026-07-06, see
# ghost_order_selfcheck.py's TAG comment for the full explanation).
TAG = "selfcheck-extreme"
for _f in glob.glob(os.path.join(EXEC_DIR, f"exec_{TAG}_*")):
    os.remove(_f)

REF = 50_000.0
FLOOR = round(REF * 0.93, -1)     # HOSE −7% daily floor
CEIL = round(REF * 1.07, -1)


class FakeQuote:
    def __init__(self, last, bid, ask, floor=FLOOR, ceiling=CEIL, day_volume=5_000_000):
        self.symbol = "TST"; self.exchange = "HOSE"
        self.last = last; self.ref = REF; self.bid = bid; self.ask = ask
        self.floor = floor; self.ceiling = ceiling; self.day_volume = day_volume
    def ok(self):
        return self.last is not None or self.ref is not None


class FakeBroker:
    """Minimal broker: one configurable quote per ticker; records placed orders."""
    name = "fake"
    def __init__(self, quotes):
        self.quotes = quotes; self.placed = []; self._oid = 0
        self.cash = 10_000_000_000
    def get_quote(self, sym):
        return self.quotes.get(sym)
    def place_order(self, symbol, qty, side, price=None, order_type="LO",
                    cash_only=False, loan_package_id=None):
        self._oid += 1
        self.placed.append(dict(symbol=symbol, qty=qty, side=side, price=price, type=order_type))
        return f"OID{self._oid}"
    def cancel_order(self, oid):
        pass
    def poll_orders(self):
        return {}
    def get_cash(self):
        return self.cash


def make_exec(cfg_over, orders):
    # HYBRID fill-timing GHIM TẮT làm nền (cfg_over vẫn bật lại được — nhóm D dùng).
    # Vì sao: bộ này đo TẦNG EXTREME, mà từ 2026-08-10 `fill_timing_hybrid_enabled`
    # mặc định True (bật trên paper). Mọi ca ở đây chạy mode="paper" và now=09:30 — NGOÀI
    # block MUA của HYBRID (11:00-13:45) ⇒ lệnh MUA bị HOÃN vì lịch HYBRID, không phải vì
    # cổng EXTREME. Đã đo trên chính bộ này: C1 (OFF ⇒ mua đặt bình thường) FAIL, và tệ
    # hơn — B6 (EXTREME ⇒ mua bị dừng) PASS VÌ LÝ DO SAI: nó pass kể cả khi cổng EXTREME
    # hỏng hoàn toàn. Ghim TẮT = cô lập đúng một biến (§23 hệ luận 1: selfcheck không
    # assert lên trạng thái SỐNG). Sự KẾT HỢP hai tầng đo riêng ở nhóm D, không bỏ sót.
    cfg = dict(DEFAULTS); cfg["fill_timing_hybrid_enabled"] = False
    cfg.update(cfg_over); cfg["mode"] = "paper"
    plan = TradePlan(plan_date="2099-01-01", signal_date="2099-01-01", strategy="tst",
                     strategy_version="0", state=3, state_name="NEUTRAL",
                     nav_basis={}, orders=orders, account=TAG,
                     created_at="2099-01-01T00:00:00")
    # floor-locked quote: last at floor, bid stuck at floor (nobody buying above it)
    quotes = {"TST": FakeQuote(last=FLOOR, bid=FLOOR, ask=round(FLOOR + 100, -2))}
    return Executor(plan, FakeBroker(quotes), cfg), quotes["TST"]


def approx(a, b, tol=1e-6):
    return abs(a - b) < tol


fails = []
def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


now = dt.datetime(2099, 1, 1, 9, 30, 0)
sell_o = PlannedOrder(id="SELL-TST-01", ticker="TST", side="sell", qty=10_000, ref_price=REF)
buy_o = PlannedOrder(id="BUY-TST-01", ticker="TST", side="buy", qty=10_000, ref_price=REF)

# ---------------------------------------------------------------- A. OFF = NORMAL byte-identical
print("A. extreme_regime_enabled=False (regression — NORMAL must be unchanged)")
ex_off, q = make_exec({"extreme_regime_enabled": False}, [sell_o])
check("A1 _extreme_regime always False when OFF",
      ex_off._extreme_regime(sell_o, q, now) is False)
check("A1b still False on 2nd poll when OFF",
      ex_off._extreme_regime(sell_o, q, now) is False)
px_off = ex_off._limit_price(sell_o, q, cross=True, extreme=False)
expected_cap = round_price(REF * (1 - DEFAULTS["max_chase_pct_sell"]), "TST", "HOSE", "up")
check("A2 sell limit == −3% cap (strands above floor)", approx(px_off, expected_cap),
      f"px={px_off:.0f} expected={expected_cap:.0f} floor={FLOOR:.0f}")
check("A3 −3% cap is strictly above the floor (would strand on gap-lock)", px_off > FLOOR)
check("A4 slice-mult == 1.0 when OFF", approx(ex_off._extreme_slice_mult(sell_o, now), 1.0))
# the extreme=False call must equal the legacy 3-arg call (default param unchanged)
check("A5 _limit_price default extreme arg == explicit False",
      approx(ex_off._limit_price(sell_o, q, cross=True),
             ex_off._limit_price(sell_o, q, cross=True, extreme=False)))

# ---------------------------------------------------------------- B. ON = mechanism fires
print("B. extreme_regime_enabled=True (mechanism)")
ex_on, q = make_exec({"extreme_regime_enabled": True}, [sell_o, buy_o])
# 2-poll confirm
r1 = ex_on._extreme_regime(sell_o, q, now)
r2 = ex_on._extreme_regime(sell_o, q, now + dt.timedelta(seconds=20))
check("B1 poll#1 not yet armed (needs 2-poll confirm)", r1 is False, f"r1={r1}")
check("B2 poll#2 armed (near-floor trigger confirmed)", r2 is True, f"r2={r2}")
# sell-to-floor pricing
px_ext = ex_on._limit_price(sell_o, q, cross=True, extreme=True)
check("B3 EXTREME sell limit == daily floor (sell-to-floor)", approx(px_ext, FLOOR),
      f"px={px_ext:.0f} floor={FLOOR:.0f}")
check("B4 EXTREME sell price < NORMAL −3% cap (chases deeper)", px_ext < expected_cap)
# faster cadence once armed
check("B5 slice-mult == extreme_slice_mult once armed",
      approx(ex_on._extreme_slice_mult(sell_o, now + dt.timedelta(seconds=25)),
             DEFAULTS["extreme_slice_mult"]))
# buy-pause end-to-end via _place_slices: arm the buy ticker, expect NO order + EXTREME_PAUSE
ex_buy, q = make_exec({"extreme_regime_enabled": True}, [buy_o])
# arm buy ticker directly (2-poll confirm already exercised above)
ex_buy._extreme_state["TST"] = {"n": 2,
    "until": (now + dt.timedelta(minutes=15)).isoformat(timespec="seconds")}
ex_buy._place_slices(now, "MORNING")
buy_orders = [p for p in ex_buy.broker.placed if p["side"] == "buy"]
check("B6 BUY paused — no order placed while EXTREME_DOWN", len(buy_orders) == 0,
      f"placed={buy_orders}")
import csv, os
paused = False
if os.path.exists(ex_buy.journal_file):
    with open(ex_buy.journal_file, encoding="utf-8") as f:
        paused = any(row and row[1] == "EXTREME_PAUSE" for row in csv.reader(f))
check("B7 EXTREME_PAUSE journaled", paused)

# ---------------------------------------------------------------- C. OFF end-to-end places normally
print("C. OFF end-to-end — buy still places (no accidental pause when disabled)")
ex_c, q = make_exec({"extreme_regime_enabled": False}, [buy_o])
ex_c._place_slices(now, "MORNING")
buy_c = [p for p in ex_c.broker.placed if p["side"] == "buy"]
check("C1 OFF: buy order placed normally", len(buy_c) == 1, f"placed={len(buy_c)}")

# ------------------------------------------------- D. EXTREME × HYBRID (hai tầng chồng nhau)
print("D. EXTREME × HYBRID — HYBRID BẬT (đúng trạng thái paper thật từ 2026-08-10)")
# Vì sao nhóm này phải tồn tại: khi HYBRID bật, "không đặt lệnh nào" có HAI nguyên nhân
# khác hẳn nhau — EXTREME_PAUSE (cổng RỦI RO) và HYBRID_DEFER (lịch CHI PHÍ). Đếm số lệnh
# KHÔNG phân biệt được chúng, nên B6 sẽ PASS kể cả khi cổng EXTREME chết hẳn (đó chính là
# thứ đã xảy ra từ 2026-08-10 đến khi bộ này được vá). Ở đây phân biệt bằng JOURNAL —
# tên sự kiện là bằng chứng nguyên nhân — và mỗi khẳng định đều kèm ca chứng minh ngược.
import tempfile


def _reset_state():
    """Xoá state/journal của TAG giữa các ca: Executor NẠP state ngay trong __init__ nên
    ca sau sẽ thừa hưởng lệnh con đang mở của ca trước và đi nhánh khác (xem ghi chú TAG
    đầu file). Không reset thì D1/D3 có thể 'pass' vì parent đã có child mở."""
    for _f in glob.glob(os.path.join(EXEC_DIR, f"exec_{TAG}_*")):
        os.remove(_f)


def _journal_events(ex):
    if not os.path.exists(ex.journal_file):
        return set()
    with open(ex.journal_file, encoding="utf-8") as f:
        return {row[1] for row in csv.reader(f) if len(row) > 1}


with tempfile.TemporaryDirectory() as _tmp:
    # D1/D2 — EXTREME armed + HYBRID bật ⇒ `_hybrid_bypass` mở, lệnh KHÔNG bị hoãn theo
    # lịch mà rơi xuống ĐÚNG cổng EXTREME. 09:30 nằm NGOÀI block MUA (11:00-13:45), nên
    # nếu bypass hỏng ta sẽ thấy HYBRID_DEFER thay cho EXTREME_PAUSE.
    _reset_state()
    ex_d, _ = make_exec({"extreme_regime_enabled": True,
                         "fill_timing_hybrid_enabled": True}, [buy_o])
    ex_d.journal_file = os.path.join(_tmp, "d1.csv")
    ex_d._extreme_state["TST"] = {"n": 2,
        "until": (now + dt.timedelta(minutes=15)).isoformat(timespec="seconds")}
    ex_d._place_slices(now, "MORNING")
    ev_d = _journal_events(ex_d)
    check("D1 HYBRID bật + EXTREME armed ⇒ dừng vì EXTREME_PAUSE (KHÔNG phải HYBRID_DEFER)",
          "EXTREME_PAUSE" in ev_d and "HYBRID_DEFER" not in ev_d, f"events={sorted(ev_d)}")
    check("D2 …và vẫn không đặt lệnh mua nào",
          len([p for p in ex_d.broker.placed if p["side"] == "buy"]) == 0)

    # D3 — CHỨNG MINH NGƯỢC cho D1: cùng cấu hình HYBRID, CHỈ tắt cờ EXTREME. Nếu D1 chỉ
    # phản ánh "HYBRID nuốt lệnh" thì ca này cũng phải ra EXTREME_PAUSE. Nó không được.
    _reset_state()
    ex_d2, _ = make_exec({"extreme_regime_enabled": False,
                          "fill_timing_hybrid_enabled": True}, [buy_o])
    ex_d2.journal_file = os.path.join(_tmp, "d3.csv")
    ex_d2._place_slices(now, "MORNING")
    ev_d2 = _journal_events(ex_d2)
    check("D3 CHỨNG MINH NGƯỢC: HYBRID bật + EXTREME tắt ⇒ HYBRID_DEFER, KHÔNG EXTREME_PAUSE",
          "HYBRID_DEFER" in ev_d2 and "EXTREME_PAUSE" not in ev_d2, f"events={sorted(ev_d2)}")

    # D4 — chốt rằng D3 là "hoãn theo lịch", không phải "bật HYBRID là hỏng đường đặt lệnh":
    # cùng cấu hình, dời vào ĐÚNG block MUA 11:00 thì lệnh đi bình thường.
    _reset_state()
    ex_d3, _ = make_exec({"extreme_regime_enabled": False,
                          "fill_timing_hybrid_enabled": True}, [buy_o])
    ex_d3.journal_file = os.path.join(_tmp, "d4.csv")
    ex_d3._place_slices(now.replace(hour=11, minute=0), "MORNING")
    check("D4 HYBRID bật, TRONG block MUA 11:00 ⇒ lệnh mua đặt bình thường",
          len([p for p in ex_d3.broker.placed if p["side"] == "buy"]) == 1,
          f"placed={len([p for p in ex_d3.broker.placed if p['side'] == 'buy'])}")

print()
if fails:
    print(f"❌ {len(fails)} check(s) FAILED: {fails}")
    sys.exit(1)
print("✅ ALL CHECKS PASSED — NORMAL byte-identical when OFF; mechanism fires when ON.")
sys.exit(0)
