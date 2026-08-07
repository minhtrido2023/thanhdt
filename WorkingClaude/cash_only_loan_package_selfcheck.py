#!/usr/bin/env python3
"""cash_only_loan_package_selfcheck.py — verify the TV1 07-28 loanPackageId RESOLVE fix.

Bug (kb/INCIDENTS.md 2026-07-28): SpaceX config sets loan_package_id=1841 (gói "GD Tiền
mặt" mainboard). It auto-attaches to every order. 1841 is valid for HOSE/HNX mainboard but
NOT for UPCOM → DNSE rejects TV1. The FIRST fix ("cash_only → OMIT the loanPackageId key")
was WRONG: DNSE requires the field → HTTP 400 "loanPackageId is required" (live PLACE_FAIL
loop 13:43 ICT 07-28).

Correct fix = per-symbol RESOLVE, not omit. `cash_only=True` on an order makes DNSEBroker
query GET /accounts/{acc}/loan-packages?symbol=X and:
  - default account id in the valid list  → use default (BAL/LAG/CAPIT mainboard unchanged)
  - default NOT in list (TV1)              → prefer type='N' (cash) pkg, else first valid id
  - query error/empty                      → fall back to default (request STILL carries the
                                             field; never omit — omission is the 400 bug)
Result is cached per symbol for the session.

Selfcheck (task-mandated a/b/c/d + no "key vanishes" assertion survives):
  L1 body-level (DNSEClient.place_order): field is ALWAYS present when a default exists.
  (a) HOSE symbol, valid=[1841,1840]     → resolve to default 1841 (no BAL/LAG/CAPIT change)
  (b) TV1, valid=[1122]                  → resolve to 1122 (NOT 1841, NOT omitted)
  (c) loan_packages error / empty        → fall back to default 1841, request has the field
  (d) cache: 2nd call same symbol        → loan_packages() NOT re-queried

Run: python3 cash_only_loan_package_selfcheck.py   (no network — stubbed)
"""
import os
import sys

WC_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WC_ROOT)

from dnse_api import DNSEClient

FAILS = []


def check(cond, msg):
    print(("  OK  " if cond else " FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


# ------------------------------------------------------------------ L1: client body
def make_client(loan_default):
    """DNSEClient bypassing __init__ (no network); _request stubbed to capture body."""
    c = DNSEClient.__new__(DNSEClient)
    c.loan_package_id = loan_default
    cap = {}

    def fake_request(method, path, query=None, body=None, trading=False):
        cap["body"] = body
        return {"id": "TEST_OID"}

    c._request = fake_request
    return c, cap


print("=== L1 (client body) default present → loanPackageId ALWAYS attached ===")
c, cap = make_client(1841)
c.place_order("0002023347", "FPT", 100, "buy", price=100000)
check(cap["body"].get("loanPackageId") == 1841,
      "no explicit id → account default 1841 attached (BAL/LAG/CAPIT unchanged)")

c, cap = make_client(1841)
c.place_order("0002023347", "TV1", 400, "buy", price=19900, loan_package_id=1122)
check(cap["body"].get("loanPackageId") == 1122,
      "explicit loan_package_id=1122 → body carries 1122 (TV1/UPCOM correct pkg)")
check("loanPackageId" in cap["body"],
      "field PRESENT (regression guard: fix must never OMIT the required key)")

c, cap = make_client(1841)
c.place_order("0002023347", "FPT", 100, "buy", price=100000, loan_package_id=0)
check(cap["body"].get("loanPackageId") == 1841,
      "loan_package_id=0 falls back to default 1841 (0 falsy — resolver never returns 0)")

c, cap = make_client(None)  # ZaloPay: no default configured
c.place_order("0001743768", "MBB", 100, "buy", price=25000)
check("loanPackageId" not in cap["body"],
      "no account default (ZaloPay) → no key, unchanged natural cash behavior")


# ------------------------------------------------------------------ L2: broker resolver
from trading_bot.brokers import DNSEBroker


class FakeClient:
    """Stub client for resolver tests. loan_packages() returns per-symbol mock and
    counts calls (cache test). place_order() captures the loan_package_id forwarded."""

    def __init__(self, default, pkg_map, raise_symbols=()):
        self.loan_package_id = default
        self._pkg_map = pkg_map
        self._raise = set(raise_symbols)
        self.calls = {}                 # symbol -> loan_packages() call count
        self.last_place = {}

    def loan_packages(self, account_id, market_type="STOCK", symbol=None):
        self.calls[symbol] = self.calls.get(symbol, 0) + 1
        if symbol in self._raise:
            raise RuntimeError("simulated loan-packages timeout")
        return {"loanPackages": self._pkg_map.get(symbol, [])}

    def place_order(self, account_id, symbol, qty, side, order_type="LO",
                    price=None, loan_package_id=None):
        self.last_place = {"symbol": symbol, "loan_package_id": loan_package_id}
        return {"id": "OID_" + symbol}


def make_broker(client):
    b = DNSEBroker.__new__(DNSEBroker)
    b.account_id = "0002023347"
    b.label = "SpaceX"
    b.client = client
    b._loan_pkg_cache = {}
    b._log_raw = lambda *a, **k: None
    return b


PKG_MAP = {
    # HOSE mainboard: default 1841 ("GD Tiền mặt" M) + 1840 ("RocketX" M) both valid
    "VNM": [{"id": 1841, "name": "GD Tiền mặt", "type": "M"},
            {"id": 1840, "name": "RocketX", "type": "M"}],
    # TV1 UPCOM: only 1122 ("GD Tiền mặt" N — pure cash), default 1841 NOT eligible
    "TV1": [{"id": 1122, "name": "GD Tiền mặt", "type": "N"}],
}

print("=== L2 (a) HOSE symbol, default 1841 in valid list → use default 1841 ===")
cl = FakeClient(1841, PKG_MAP)
b = make_broker(cl)
oid = b.place_order("VNM", 100, "buy", price=60000, cash_only=True)
check(cl.last_place["loan_package_id"] == 1841,
      "VNM cash_only: default 1841 valid → forwarded 1841 (BAL/LAG/CAPIT mainboard unchanged)")

print("=== L2 (b) TV1, default NOT in list → resolve to 1122 (cash type N) ===")
cl = FakeClient(1841, PKG_MAP)
b = make_broker(cl)
oid = b.place_order("TV1", 400, "buy", price=19900, cash_only=True)
check(cl.last_place["loan_package_id"] == 1122,
      "TV1 cash_only: default invalid → forwarded 1122 (NOT 1841, NOT None/omitted)")
check(oid == "OID_TV1", "TV1 place_order returned order id")

print("=== L2 (b') multiple valid, no default, prefer type='N' over 'M' ===")
cl = FakeClient(1841, {"XYZ": [{"id": 500, "type": "M"}, {"id": 501, "type": "N"}]})
b = make_broker(cl)
b.place_order("XYZ", 100, "buy", price=10000, cash_only=True)
check(cl.last_place["loan_package_id"] == 501,
      "no default in list, {M:500,N:501} → prefer cash pkg 501")

print("=== L2 (c1) loan_packages ERROR → fall back to default 1841 (field kept) ===")
cl = FakeClient(1841, PKG_MAP, raise_symbols=("TV1",))
b = make_broker(cl)
b.place_order("TV1", 400, "buy", price=19900, cash_only=True)
check(cl.last_place["loan_package_id"] == 1841,
      "query error → forwarded account default 1841 (fail-safe: never omit the field)")

print("=== L2 (c2) loan_packages EMPTY → fall back to default 1841 ===")
cl = FakeClient(1841, {"TV1": []})
b = make_broker(cl)
b.place_order("TV1", 400, "buy", price=19900, cash_only=True)
check(cl.last_place["loan_package_id"] == 1841,
      "empty list → forwarded account default 1841 (fail-safe)")

print("=== L2 (c3) cash_only=False → resolve theo MÃ (sửa 2026-08-07, ca DRI/UPCOM) ===")
# Hợp đồng CŨ ở đây là "lệnh thường forward lp=None, không query" — chính nó là BUG DRI:
# None ⇒ dnse_api rơi về gói default 1841 (mainboard-only) ⇒ DNSE reject cả ppse lẫn
# place_order với mã UPCOM ⇒ WAIT_CASH vô hạn trông y hệt thiếu tiền.
cl = FakeClient(1841, PKG_MAP)
b = make_broker(cl)
b.place_order("VNM", 100, "buy", price=60000)  # cash_only defaults False
check(cl.last_place["loan_package_id"] == 1841,
      "normal order (default hợp lệ): forward ĐÚNG gói default 1841 — lệnh đi ra y hệt cũ")
check(cl.calls.get("VNM", 0) == 1,
      "normal order query loan_packages 1 lần/mã/phiên (chi phí thêm: 1 GET, cache theo mã)")

print("=== L2 (d) cache: 2nd resolve of same symbol does NOT re-query ===")
cl = FakeClient(1841, PKG_MAP)
b = make_broker(cl)
b.place_order("TV1", 100, "buy", price=19900, cash_only=True)
b.place_order("TV1", 100, "buy", price=19900, cash_only=True)
check(cl.calls.get("TV1", 0) == 1,
      "TV1 resolved twice → loan_packages() queried exactly once (session cache)")


# ------------------------------------------------------------- plumbing / full chain
print("=== plumbing: DNSEBroker.place_order signature carries cash_only ===")
import inspect
sig = inspect.signature(DNSEBroker.place_order)
check("cash_only" in sig.parameters and "no_loan_package" not in sig.parameters,
      "DNSEBroker.place_order has cash_only param, no stale no_loan_package")

print("=== plumbing: EVERY concrete BrokerBase subclass accepts cash_only ===")
# Root cause of the 2026-07-30 paper-main outage (386 PLACE_FAIL/day, kb/INCIDENTS.md):
# this exact fix pattern (add a kwarg to BrokerBase.place_order) was applied to
# DNSEBroker/PHSBroker but PaperBroker was missed — executor.py calls
# broker.place_order(..., cash_only=...) unconditionally regardless of broker class, so any
# subclass missing the kwarg crashes 100% of orders for that broker. The single-class check
# above did not generalize; this one walks every subclass so a future kwarg addition to
# BrokerBase can't repeat the same miss.
from trading_bot.brokers import BrokerBase
import trading_bot.brokers as brokers_mod
base_params = set(inspect.signature(BrokerBase.place_order).parameters)
subclasses = [c for c in vars(brokers_mod).values()
              if isinstance(c, type) and issubclass(c, BrokerBase) and c is not BrokerBase]
for cls in subclasses:
    missing = base_params - set(inspect.signature(cls.place_order).parameters)
    check(not missing, f"{cls.__name__}.place_order carries all of BrokerBase's params "
                        f"(missing: {sorted(missing) or 'none'})")

print("=== discretionary engine stamps cash_only=True on injected order ===")
from trading_bot.discretionary_accumulation import compute_session_order
import json
state = json.load(open(os.path.join(
    WC_ROOT, "data/trade_plans/discretionary/state_TV1_SpaceX.json")))
order, decision = compute_session_order(
    state, 0, 2_000_000_000, 19900.0, "2026-07-28", "2026-07-28T20:30:00+07:00")
check(order is not None and order.get("cash_only") is True,
      f"engine order cash_only=True (decision={decision['action']})")

print("=== PlannedOrder round-trips cash_only through load_plan field filter ===")
from trading_bot.plan import PlannedOrder, load_plan
import dataclasses
o = PlannedOrder(id="X", ticker="TV1", side="buy", qty=400, ref_price=19900,
                 book="DISCRETIONARY_SPECIAL", cash_only=True)
check(o.cash_only is True and "cash_only" in {f.name for f in dataclasses.fields(PlannedOrder)},
      "PlannedOrder(cash_only=True) is a real dataclass field (survives load_plan filter)")
check(PlannedOrder(id="Y", ticker="FPT", side="buy", qty=1, ref_price=1).cash_only is False,
      "PlannedOrder default cash_only=False (BAL/LAG/CAPIT regression)")

print("=== load_plan preserves cash_only from real live plan file ===")
d = load_plan("2026-07-28", account="SpaceX")
tv1 = [x for x in (d.orders if d else []) if x.ticker == "TV1"]
check(bool(tv1) and tv1[0].cash_only is True,
      "load_plan('2026-07-28','SpaceX') → TV1 order.cash_only=True survives field filter")
non_tv1 = [x for x in (d.orders if d else []) if x.ticker != "TV1"]
check(all(x.cash_only is False for x in non_tv1),
      f"all {len(non_tv1)} non-TV1 orders in live plan cash_only=False (no collateral change)")

print()
if FAILS:
    print(f"SELFCHECK FAILED — {len(FAILS)} assertion(s):")
    for m in FAILS:
        print("  - " + m)
    sys.exit(1)
print("SELFCHECK PASSED — all assertions OK")
