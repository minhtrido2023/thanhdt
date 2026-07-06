# -*- coding: utf-8 -*-
"""Regression self-check for the T+2-sellable cap on SELL orders (executor.py).

Incident 2026-07-06: the combined-trim plan scheduled SELL orders for 11 tickers
purchased 2 trading days earlier (T, still under T+2 settlement) starting at market
open. DNSE's `get_positions()` already distinguishes `total` (all held shares) from
`sellable` (shares that have settled and can actually be sold) — but the executor's
`_place_slices`/`_atc_sweep` never consulted it, so it blindly called `place_order()`
every ~20s and got `HTTP 400: Trade quantity not enough` ~2000 times before the shares
settled in the afternoon session. No capital/correctness impact (broker correctly
rejected every attempt), but wasted retries/API calls for over an hour.

Fix: `step()` fetches `get_positions()` once per cycle (only when the plan has any SELL
order) and passes it into `_place_slices`/`_atc_sweep`; both now cap sell qty to the
ticker's `sellable` amount (or skip entirely below 1 lot) with a new `WAIT_T2_SETTLEMENT`
journal event instead of calling `place_order()` and waiting for the broker to reject it.
Degrades gracefully if `get_positions()` itself fails (falls back to today's old
behavior — this is a retry-noise optimization, not a correctness guard, unlike the
ghost-order fail-safe-block in `step()`'s poll_orders() handling).

Run: python t2_settlement_selfcheck.py   (exit 0 = all pass)
"""
import datetime as dt
import glob
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trading_bot.plan import PlannedOrder, TradePlan  # noqa: E402
from trading_bot.executor import Executor  # noqa: E402
from trading_bot.config import load_config, EXEC_DIR  # noqa: E402

# Executor.__init__ eagerly loads state.json from the DEFAULT (account, plan_date) path
# BEFORE make_executor() below can redirect it to a tmpdir — a stale file from an earlier
# run (this file's own, or any other selfcheck that used the same account tag) silently
# corrupts this run's starting state. Found 2026-07-06 while adding excluded_tickers; see
# ghost_order_selfcheck.py's TAG comment for the full explanation.
TAG = "selfcheck-t2"
for _f in glob.glob(os.path.join(EXEC_DIR, f"exec_{TAG}_*")):
    os.remove(_f)

fails = []


def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


def make_quote(symbol, px=20000):
    from trading_bot.brokers import Quote
    q = Quote.__new__(Quote)
    q.raw = {}
    q.symbol = symbol
    q.exchange = "HOSE"
    q.last = q.ref = px
    q.ceiling = px * 1.07
    q.floor = px * 0.93
    q.bid = px - 50
    q.ask = px + 50
    q.day_volume = None  # tránh vướng logic quota fleet — không phải trọng tâm test này
    return q


class _RecordingBroker:
    """Ghi lại mọi lời gọi place_order (qty thật đã đặt) để assert cap đúng; raise nếu
    place_order bị gọi cho ticker lẽ ra phải bị skip hoàn toàn (đó chính là assertion)."""
    name = "recording"

    def __init__(self, positions, forbidden_tickers=()):
        self._positions = positions
        self._forbidden = set(forbidden_tickers)
        self.placed = []  # [(ticker, qty)]

    def get_quote(self, symbol, *a, **k):
        return make_quote(symbol)

    def place_order(self, symbol, qty, side, price=None, order_type="LO"):
        if symbol in self._forbidden:
            raise AssertionError(f"place_order called for {symbol} — should have been "
                                  f"skipped by the T+2 sellable cap!")
        self.placed.append((symbol, qty))
        return f"OID-{len(self.placed)}"

    def cancel_order(self, order_id):
        return None

    def get_cash(self):
        return 10**12

    def poll_orders(self):
        return {}

    def get_positions(self):
        return self._positions


def make_executor(tmpdir, orders, positions, forbidden_tickers=()):
    plan = TradePlan(plan_date="2099-01-01", signal_date="2099-01-01", strategy="selfcheck",
                     strategy_version="0", state=3, state_name="NEUTRAL",
                     nav_basis={"account_nav": 1e9, "scale": 1.0}, orders=orders,
                     account=TAG, created_at="2099-01-01T00:00:00")
    cfg = load_config()
    cfg["mode"] = "paper"
    broker = _RecordingBroker(positions, forbidden_tickers)
    ex = Executor(plan, broker, cfg, shared={})
    ex.state_file = os.path.join(tmpdir, "state.json")
    ex.journal_file = os.path.join(tmpdir, "journal.csv")
    return ex, broker


NOW = dt.datetime(2099, 1, 1, 9, 20)

with tempfile.TemporaryDirectory() as tmp:
    # A. sellable=0 (fully unsettled, e.g. bought yesterday, still morning T+2) -> SKIP
    #    entirely, place_order must NEVER be called, journal shows WAIT_T2_SETTLEMENT.
    o_a = PlannedOrder(id="SELL-01", ticker="T2ZERO", side="sell", qty=1000, ref_price=20000)
    ex, broker = make_executor(tmp, [o_a], {"T2ZERO": {"total": 1000, "sellable": 0}},
                               forbidden_tickers={"T2ZERO"})
    ex._place_slices(NOW, "MORNING", ghost_tickers=set(), positions=ex.broker.get_positions())
    journal_notes = "\n".join(open(ex.journal_file, encoding="utf-8").read().splitlines())
    check("A1 sellable=0 -> place_order never called", broker.placed == [], detail=str(broker.placed))
    check("A2 sellable=0 -> WAIT_T2_SETTLEMENT logged", "WAIT_T2_SETTLEMENT" in journal_notes)

    # B. sellable == full qty (fully settled) -> proceeds normally, unchanged behavior.
    o_b = PlannedOrder(id="SELL-01", ticker="SETTLED", side="sell", qty=1000, ref_price=20000)
    ex2, broker2 = make_executor(tmp, [o_b], {"SETTLED": {"total": 1000, "sellable": 1000}})
    ex2._place_slices(NOW, "MORNING", ghost_tickers=set(), positions=ex2.broker.get_positions())
    check("B1 sellable=full qty -> place_order called normally",
          len(broker2.placed) == 1 and broker2.placed[0][0] == "SETTLED",
          detail=str(broker2.placed))

    # C. sellable partial (300 of a wanted 1000) -> qty capped to sellable, NOT skipped,
    #    NOT the full requested amount.
    o_c = PlannedOrder(id="SELL-01", ticker="PARTIAL", side="sell", qty=1000, ref_price=20000)
    ex3, broker3 = make_executor(tmp, [o_c], {"PARTIAL": {"total": 1000, "sellable": 300}})
    ex3._place_slices(NOW, "MORNING", ghost_tickers=set(), positions=ex3.broker.get_positions())
    check("C1 partial sellable -> qty capped, order still placed",
          len(broker3.placed) == 1 and broker3.placed[0][1] == 300,
          detail=str(broker3.placed))

    # D. positions=None (get_positions() failed this cycle) -> graceful degrade, behaves
    #    exactly like before the fix (attempts the sell, doesn't block on missing data).
    o_d = PlannedOrder(id="SELL-01", ticker="NODATA", side="sell", qty=1000, ref_price=20000)
    ex4, broker4 = make_executor(tmp, [o_d], {})  # positions arg unused when we pass None below
    ex4._place_slices(NOW, "MORNING", ghost_tickers=set(), positions=None)
    check("D1 positions=None degrades to pre-fix behavior (sell attempted)",
          len(broker4.placed) == 1 and broker4.placed[0][0] == "NODATA",
          detail=str(broker4.placed))

    # E. BUY orders must be completely unaffected by the sellable cap (ticker missing
    #    from positions map entirely, since we only ever query it for SELL tickers).
    o_e = PlannedOrder(id="BUY-01", ticker="BUYME", side="buy", qty=1000, ref_price=20000)
    ex5, broker5 = make_executor(tmp, [o_e], {})  # empty positions map on purpose
    ex5._place_slices(NOW, "MORNING", ghost_tickers=set(), positions={})
    check("E1 BUY order unaffected by (empty) positions map",
          len(broker5.placed) == 1 and broker5.placed[0][0] == "BUYME",
          detail=str(broker5.placed))

    # F. _atc_sweep: sellable=0 must also skip during the ATC remainder sweep, not just
    #    the normal slicing path (same T+2 restriction applies at session close).
    o_f = PlannedOrder(id="SELL-01", ticker="ATCZERO", side="sell", qty=1000, ref_price=20000)
    ex6, broker6 = make_executor(tmp, [o_f], {"ATCZERO": {"total": 1000, "sellable": 0}},
                                 forbidden_tickers={"ATCZERO"})
    ex6.cfg["atc_remainder_sell"] = True
    ex6._atc_sweep(ghost_tickers=set(), positions=ex6.broker.get_positions())
    check("F1 ATC sweep also respects sellable=0 (never calls place_order)",
          broker6.placed == [], detail=str(broker6.placed))

print()
if fails:
    print(f"❌ {len(fails)} FAIL(s): {fails}")
    sys.exit(1)
print("✅ all T+2 sellable-cap checks passed")
sys.exit(0)
