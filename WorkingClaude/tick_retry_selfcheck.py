# -*- coding: utf-8 -*-
"""Regression + behaviour self-check for the tick-size mismatch auto-retry fix.

Bug found live 2026-07-01 (SpaceX go-live): SHS/MBS (HNX-listed) orders were
rejected 1494x with "HTTP 400: Invalid price lot" — confirmed from the real
journal that the rejected prices (18450, 19850) are valid under HOSE's tiered
tick rule (divisible by 50) but NOT divisible by 100, which HNX/UPCOM require
flat. Root cause: `Quote.exchange` silently defaulted to "HOSE" when the live
feed didn't populate it, so `_limit_price` rounded to the wrong tick grid.

Fix: `Executor._retry_tick_mismatch()` — on an "Invalid price lot"-shaped
failure, retry ONCE with the other tick convention (HOSE<->HNX/UPCOM, which
share the same flat-100 tick so only one alternate exists) using the broker's
own real rejection as ground truth (no guessing the live JSON field name).
On success, cache the learned exchange in `self.state["exchange_override"]`
(persisted, survives resume) so subsequent cycles get it right first try.

Drives trading_bot.executor.Executor with a fake broker/quote (no network, no
live state, no real orders). Asserts:
  A. HNX-tick-only ticker, HOSE assumed by default → first place_order raises
     the real error shape, retry with HNX tick succeeds, override cached,
     TICK_RETRY_OK journaled.
  B. Second order for the SAME ticker after the fix was learned → places
     correctly on the FIRST try (no retry needed, HOSE never attempted again).
  C. Normal HOSE ticker (price already valid) → no retry ever triggered, zero
     override created (regression: existing tickers unaffected).
  D. Unrelated failure (e.g. insufficient funds, HTTP 500) → must NOT retry;
     falls through to the existing PLACE_FAIL path unchanged.
  E. Ticker already in `exchange_override` but STILL rejected → do not retry
     a second time (avoids infinite alternation); falls through to PLACE_FAIL.

Run: python tick_retry_selfcheck.py   (exit 0 = all pass, non-zero = a check failed)
"""
import datetime as dt
import glob
import os
import sys

from trading_bot.config import DEFAULTS, EXEC_DIR
from trading_bot.plan import PlannedOrder, TradePlan
from trading_bot.executor import Executor

for _f in glob.glob(os.path.join(EXEC_DIR, "exec_tickcheck-*_journal.csv")):
    os.remove(_f)
for _f in glob.glob(os.path.join(EXEC_DIR, "exec_tickcheck-*_state.json")):
    os.remove(_f)

REF = 18_400.0  # ~ SHS's real ref price range from the live journal


class FakeTickError(Exception):
    """Mimics dnse_api.DNSEError's shape (.status, str(e) contains the message)
    without importing the real broker module (test isolation)."""
    def __init__(self, message, status=None):
        super().__init__(message)
        self.status = status


class FakeQuote:
    def __init__(self, last, bid, ask, exchange="HOSE", floor=None, ceiling=None,
                 day_volume=5_000_000):
        self.symbol = "SHS"; self.exchange = exchange
        self.last = last; self.ref = REF; self.bid = bid; self.ask = ask
        self.floor = floor or round(REF * 0.90, -1)      # HNX -10% band
        self.ceiling = ceiling or round(REF * 1.10, -1)
        self.day_volume = day_volume

    def ok(self):
        return self.last is not None


class FakeBroker:
    """place_order raises FakeTickError on any price NOT on the flat-100 grid
    (i.e. simulates the real HNX venue), exactly matching the live bug's
    observed rejection of HOSE-tiered (÷50 but not ÷100) prices."""
    name = "fake"

    def __init__(self, quotes):
        self.quotes = quotes; self.placed = []; self._oid = 0
        self.cash = 10_000_000_000

    def get_quote(self, sym):
        return self.quotes.get(sym)

    def place_order(self, symbol, qty, side, price=None, order_type="LO"):
        if price is not None and round(price) % 100 != 0:
            raise FakeTickError("HTTP 400: Invalid price lot", status=400)
        self._oid += 1
        oid = f"OID{self._oid}"
        self.placed.append(dict(oid=oid, symbol=symbol, qty=qty, side=side, price=price))
        return oid

    def cancel_order(self, oid):
        pass

    def poll_orders(self):
        return {}

    def get_cash(self):
        return self.cash


def make_exec(orders, quote, tag):
    cfg = dict(DEFAULTS); cfg.update({"mode": "paper", "fill_timing_enabled": False})
    plan = TradePlan(plan_date="2099-01-01", signal_date="2099-01-01", strategy="tst",
                     strategy_version="0", state=3, state_name="NEUTRAL",
                     nav_basis={}, orders=orders, account=f"tickcheck-{tag}",
                     created_at="2099-01-01T00:00:00")
    return Executor(plan, FakeBroker({"SHS": quote}), cfg), quote


def journal_topics(ex):
    import csv
    if not os.path.exists(ex.journal_file):
        return []
    with open(ex.journal_file, encoding="utf-8") as f:
        return [row[1] for row in csv.reader(f) if row]


fails = []
def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


now = dt.datetime(2099, 1, 1, 10, 0, 0)

# ---------------------------------------------------------------- A. the live bug: HOSE assumed, HNX real
print("A. HNX ticker mis-assumed as HOSE (the live 2026-07-01 SHS/MBS bug)")
# ask deliberately lands on a HOSE-valid (÷50) but HNX-invalid (not ÷100) price
buy_o = PlannedOrder(id="BUY-SHS-01", ticker="SHS", side="buy", qty=30_000, ref_price=REF)
ex_a, q_a = make_exec([buy_o], FakeQuote(last=18_450, bid=18_400, ask=18_450, exchange="HOSE"), "a")
ex_a._place_slices(now, "MORNING")
check("A1 order placed despite the tick mismatch (auto-recovered)",
      len(ex_a.broker.placed) == 1, f"placed={ex_a.broker.placed}")
if ex_a.broker.placed:
    check("A2 final price lands on the flat-100 (HNX) grid", ex_a.broker.placed[0]["price"] % 100 == 0,
          f"price={ex_a.broker.placed[0]['price']}")
check("A3 exchange_override learned HNX for SHS",
      ex_a.state["exchange_override"].get("SHS") == "HNX",
      f"override={ex_a.state['exchange_override']}")
check("A4 TICK_RETRY_OK journaled", "TICK_RETRY_OK" in journal_topics(ex_a))
check("A5 PLACE_FAIL NOT journaled (recovered before giving up)",
      "PLACE_FAIL" not in journal_topics(ex_a))

# ---------------------------------------------------------------- B. learned override applies immediately
print("B. Same ticker, NEW order after the fix learned → correct on the FIRST try")
buy_o2 = PlannedOrder(id="BUY-SHS-02", ticker="SHS", side="buy", qty=10_000, ref_price=REF)
ex_b, q_b = make_exec([buy_o2], FakeQuote(last=18_450, bid=18_400, ask=18_450, exchange="HOSE"), "b")
ex_b.state["exchange_override"]["SHS"] = "HNX"   # simulate a resumed state that already learned it
ex_b._place_slices(now, "MORNING")
check("B1 placed on the very first attempt (no retry needed)",
      len(ex_b.broker.placed) == 1)
check("B2 no TICK_RETRY_OK this time (nothing to recover from)",
      "TICK_RETRY_OK" not in journal_topics(ex_b))

# ---------------------------------------------------------------- C. normal HOSE ticker unaffected
print("C. Ordinary HOSE ticker (price already ÷100) → zero retries, zero override (regression)")
buy_hose = PlannedOrder(id="BUY-VCB-01", ticker="VCB", side="buy", qty=1_000, ref_price=60_000)
q_hose = FakeQuote(last=60_000, bid=59_900, ask=60_000, exchange="HOSE")
ex_c, _ = make_exec([buy_hose], q_hose, "c")
ex_c.broker.quotes["VCB"] = q_hose
ex_c._place_slices(now, "MORNING")
check("C1 placed normally, first try", len(ex_c.broker.placed) == 1)
check("C2 no override created for a ticker that never failed",
      "VCB" not in ex_c.state["exchange_override"])
check("C3 no TICK_RETRY_OK noise", "TICK_RETRY_OK" not in journal_topics(ex_c))

# ---------------------------------------------------------------- D. unrelated error must not retry
print("D. Unrelated broker error (e.g. insufficient funds / HTTP 500) → no retry, unchanged PLACE_FAIL")
class InsufficientFundsBroker(FakeBroker):
    def place_order(self, *a, **k):
        raise FakeTickError("HTTP 500: internal error", status=500)
plan_d = TradePlan(plan_date="2099-01-01", signal_date="2099-01-01", strategy="tst",
                   strategy_version="0", state=3, state_name="NEUTRAL",
                   nav_basis={}, orders=[buy_o], account="tickcheck-d",
                   created_at="2099-01-01T00:00:00")
ex_d = Executor(plan_d, InsufficientFundsBroker({"SHS": FakeQuote(18_450, 18_400, 18_450)}),
               {**DEFAULTS, "mode": "paper", "fill_timing_enabled": False})
ex_d._place_slices(now, "MORNING")
check("D1 no order placed (genuine failure)", len(ex_d.broker.placed) == 0)
check("D2 PLACE_FAIL journaled unchanged", "PLACE_FAIL" in journal_topics(ex_d))
check("D3 no override created on an unrelated error",
      "SHS" not in ex_d.state["exchange_override"])

# ---------------------------------------------------------------- E. already-learned ticker still fails
print("E. Ticker already in exchange_override but STILL rejected → do not retry again")
ex_e, q_e = make_exec([buy_o], FakeQuote(last=18_450, bid=18_400, ask=18_450, exchange="HOSE"), "e")
ex_e.state["exchange_override"]["SHS"] = "HNX"
# force BOTH conventions to fail by making every price rejected
class AlwaysRejectBroker(FakeBroker):
    def place_order(self, *a, **k):
        raise FakeTickError("HTTP 400: Invalid price lot", status=400)
ex_e.broker = AlwaysRejectBroker({"SHS": q_e})
ex_e._place_slices(now, "MORNING")
check("E1 no infinite alternation — falls through to PLACE_FAIL",
      "PLACE_FAIL" in journal_topics(ex_e))
check("E2 exactly one PLACE_FAIL row (not stuck retrying)",
      journal_topics(ex_e).count("PLACE_FAIL") == 1, f"topics={journal_topics(ex_e)}")

print()
if fails:
    print(f"FAILED {len(fails)} check(s): {fails}")
    sys.exit(1)
print("ALL CHECKS PASSED — tick-mismatch self-heals via the broker's own rejection,"
      " learned override persists, unrelated errors and normal tickers are untouched.")
sys.exit(0)
