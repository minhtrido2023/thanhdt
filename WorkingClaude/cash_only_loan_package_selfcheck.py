#!/usr/bin/env python3
"""cash_only_loan_package_selfcheck.py — verify the TV1 07-28 loanPackageId fix.

Bug (kb/INCIDENTS.md 2026-07-28): SpaceX config sets loan_package_id=1841 → every
order placed on SpaceX auto-attached loanPackageId=1841; TV1 (UPCOM) không đủ điều
kiện dưới gói này → DNSE reject. Fix = `cash_only` field on PlannedOrder carried down
to `place_order(..., no_loan_package=True)` which OMITS the loanPackageId key entirely.

Selfcheck (task-mandated a/b/c/d):
  (a) normal order (no cash_only) on SpaceX → body STILL carries loanPackageId=1841 (regression)
  (b) cash_only=True on SpaceX → body has NO loanPackageId KEY (assert key absent, not =0/None)
  (c) ZaloPay (no loan_package_id config) → unaffected either way (old behavior)
  (d) TV1 order with cash_only=True through DNSEBroker + discretionary engine

Run: python3 cash_only_loan_package_selfcheck.py   (no network — _request is stubbed)
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


def make_client(loan_default):
    """DNSEClient bypassing __init__ (no network); _request stubbed to capture body."""
    c = DNSEClient.__new__(DNSEClient)
    c.loan_package_id = loan_default
    cap = {}

    def fake_request(method, path, query=None, body=None, trading=False):
        cap["body"] = body
        cap["query"] = query
        return {"id": "TEST_OID"}

    c._request = fake_request
    return c, cap


print("=== (a) SpaceX normal order (loan default 1841, no_loan_package=False) ===")
c, cap = make_client(1841)
c.place_order("0002023347", "FPT", 100, "buy", price=100000)
check(cap["body"].get("loanPackageId") == 1841,
      "normal order body has loanPackageId=1841 (account default preserved)")

print("=== (b) SpaceX cash_only (no_loan_package=True) ===")
c, cap = make_client(1841)
c.place_order("0002023347", "TV1", 400, "buy", price=19900, no_loan_package=True)
check("loanPackageId" not in cap["body"],
      "cash_only body has NO loanPackageId KEY (key truly absent, not =0/None)")
check(cap["body"].get("symbol") == "TV1" and cap["body"].get("quantity") == 400,
      "cash_only body still well-formed (symbol/qty intact)")

print("=== (b') explicit loan_package_id still honored ===")
c, cap = make_client(1841)
c.place_order("0002023347", "FPT", 100, "buy", price=100000, loan_package_id=9999)
check(cap["body"].get("loanPackageId") == 9999,
      "explicit loan_package_id=9999 used (case b of 3-way)")

print("=== (b'') 0-sentinel guard: 0 is falsy → NOT a way to omit ===")
c, cap = make_client(1841)
c.place_order("0002023347", "FPT", 100, "buy", price=100000, loan_package_id=0)
check(cap["body"].get("loanPackageId") == 1841,
      "loan_package_id=0 falls back to default 1841 (proves 0 is unusable as sentinel; "
      "must use no_loan_package flag)")

print("=== (c) ZaloPay (no loan_package_id config = None) ===")
c, cap = make_client(None)
c.place_order("0001743768", "MBB", 100, "buy", price=25000)
check("loanPackageId" not in cap["body"],
      "ZaloPay normal order: no loanPackageId key (unchanged natural cash behavior)")
c, cap = make_client(None)
c.place_order("0001743768", "MBB", 100, "buy", price=25000, no_loan_package=True)
check("loanPackageId" not in cap["body"],
      "ZaloPay cash_only=True: still no loanPackageId key (no regression)")

print("=== (d) full chain: DNSEBroker.place_order → client, cash_only forwarded ===")
from trading_bot.brokers import DNSEBroker
b = DNSEBroker.__new__(DNSEBroker)
b.account_id = "0002023347"
b.label = "SpaceX"
import types
_cap = {}


class _FakeClient:
    def place_order(self, account_id, symbol, qty, side, order_type="LO",
                    price=None, no_loan_package=False):
        _cap["no_loan_package"] = no_loan_package
        _cap["symbol"] = symbol
        return {"id": "OID_D"}


b.client = _FakeClient()
b._log_raw = lambda *a, **k: None
oid = b.place_order("TV1", 400, "buy", price=19900, no_loan_package=True)
check(oid == "OID_D" and _cap.get("no_loan_package") is True,
      "DNSEBroker forwards no_loan_package=True to client for TV1")
oid = b.place_order("FPT", 100, "buy", price=100000)
check(_cap.get("no_loan_package") is False,
      "DNSEBroker default no_loan_package=False (BAL/LAG/CAPIT unchanged)")

print("=== (d2) discretionary engine stamps cash_only=True on injected order ===")
from trading_bot.discretionary_accumulation import compute_session_order
import json
state = json.load(open(os.path.join(
    WC_ROOT, "data/trade_plans/discretionary/state_TV1_SpaceX.json")))
# filled=0, prev turnover/price present, plan_date arbitrary
order, decision = compute_session_order(
    state, 0, 2_000_000_000, 19900.0, "2026-07-28", "2026-07-28T20:30:00+07:00")
check(order is not None and order.get("cash_only") is True,
      f"engine order cash_only=True (decision={decision['action']})")

print("=== (d3) PlannedOrder round-trips cash_only through load_plan filter ===")
from trading_bot.plan import PlannedOrder, load_plan
import dataclasses
o = PlannedOrder(id="X", ticker="TV1", side="buy", qty=400, ref_price=19900,
                 book="DISCRETIONARY_SPECIAL", cash_only=True)
check(o.cash_only is True, "PlannedOrder(cash_only=True) constructs")
check("cash_only" in {f.name for f in dataclasses.fields(PlannedOrder)},
      "cash_only is a real dataclass field (load_plan's `known` filter keeps it)")
# default regression
o2 = PlannedOrder(id="Y", ticker="FPT", side="buy", qty=100, ref_price=100000)
check(o2.cash_only is False, "PlannedOrder default cash_only=False (regression)")

print("=== (d4) load_plan preserves cash_only from real live plan file ===")
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
