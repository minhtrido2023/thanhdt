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
import sys

from trading_bot.config import DEFAULTS
from trading_bot.plan import PlannedOrder, TradePlan
from trading_bot.executor import Executor
from trading_bot.vn_market import round_price

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
    def place_order(self, symbol, qty, side, price=None, order_type="LO"):
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
    cfg = dict(DEFAULTS); cfg.update(cfg_over); cfg["mode"] = "paper"
    plan = TradePlan(plan_date="2099-01-01", signal_date="2099-01-01", strategy="tst",
                     strategy_version="0", state=3, state_name="NEUTRAL",
                     nav_basis={}, orders=orders, account="selfcheck",
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

print()
if fails:
    print(f"❌ {len(fails)} check(s) FAILED: {fails}")
    sys.exit(1)
print("✅ ALL CHECKS PASSED — NORMAL byte-identical when OFF; mechanism fires when ON.")
sys.exit(0)
