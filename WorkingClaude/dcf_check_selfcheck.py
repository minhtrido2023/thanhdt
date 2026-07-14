# -*- coding: utf-8 -*-
"""Selfcheck: dcf_check echo (Pha 2 DCF, 2026-07-14).

Kiểm tra 3 điều:
  1. PlannedOrder đọc được dcf_check và dcf_override_reason từ raw JSON
  2. load_plan() backward-compat: plan không có dcf_check → không lỗi, dcf_check=None
  3. executor state chứa dcf_check nguyên vẹn trong parents[order_id]
  4. _sync_fills publish bus event khi BUY + RICH + robust=True; không publish khi CHEAP/NOT_COMPUTED

TAG = "selfcheck_dcf"  # unique — không dùng chung với selfcheck khác
"""

import dataclasses
import json
import os
import sys
import tempfile
import unittest

WORKDIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WORKDIR)

# Dọn state file fixture cũ (nếu có) trước khi import Executor để tránh resume corrupt.
_EXEC_DIR = os.path.join(WORKDIR, "data", "execution_logs")
_TAG = "selfcheck_dcf"
_STATE_FIXTURE = os.path.join(_EXEC_DIR, f"exec_{_TAG}_2026-07-14_state.json")
if os.path.exists(_STATE_FIXTURE):
    os.remove(_STATE_FIXTURE)

from trading_bot.plan import PlannedOrder, TradePlan, load_plan
from trading_bot.executor import Executor, _publish_bot_event
from trading_bot.config import EXEC_DIR, PLAN_DIR


# ---------------------------------------------------------------------------
# Stubs
# ---------------------------------------------------------------------------

class _FakeBroker:
    def poll_orders(self): return {}
    def cancel_order(self, oid): pass


class _FakeCfg(dict):
    pass


DCF_RICH = {
    "status": "RICH",
    "margin_of_safety": 0.22,
    "robust": True,
    "as_of": "2026-07-14",
}
DCF_CHEAP = {
    "status": "CHEAP",
    "margin_of_safety": 0.35,
    "robust": True,
    "as_of": "2026-07-14",
}
DCF_NOT_COMPUTED = {
    "status": "NOT_COMPUTED",
    "margin_of_safety": None,
    "robust": False,
    "reason": "fcfe_negative_buildout",
    "as_of": "2026-07-14",
}


def _make_order(ticker="VCB", side="buy", dcf_check=None, dcf_override_reason=""):
    return PlannedOrder(
        id=f"{side.upper()}-{ticker}-01",
        ticker=ticker,
        side=side,
        qty=100,
        ref_price=50000,
        dcf_check=dcf_check,
        dcf_override_reason=dcf_override_reason,
    )


def _make_plan(orders, account=_TAG):
    return TradePlan(
        plan_date="2026-07-14",
        signal_date="2026-07-11",
        strategy="V24",
        strategy_version="2.4",
        state=3,
        state_name="NEUTRAL",
        nav_basis={"account_nav": 1e9, "paper_nav": 1e9, "scale": 1.0},
        orders=orders,
        account=account,
        created_at="2026-07-14T00:00:00",
    )


def _make_executor(plan):
    cfg = _FakeCfg({
        "mode": "paper", "max_participation": 0.10,
        "fill_timing_enabled": False, "extreme_regime_enabled": False,
        "chase_cap_vol_scale_enabled": False,
    })
    return Executor(plan, _FakeBroker(), cfg, shared={})


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestDcfCheckEcho(unittest.TestCase):

    def test_1_plannedorder_carries_dcf_fields(self):
        """dcf_check và dcf_override_reason được giữ nguyên trong PlannedOrder."""
        o = _make_order(dcf_check=DCF_RICH, dcf_override_reason="quant conviction strong")
        self.assertEqual(o.dcf_check["status"], "RICH")
        self.assertTrue(o.dcf_check["robust"])
        self.assertEqual(o.dcf_override_reason, "quant conviction strong")
        print("  [1] PlannedOrder giữ dcf_check + dcf_override_reason: OK")

    def test_2_backward_compat_no_dcf_check(self):
        """Plan không có dcf_check → dcf_check=None, không lỗi."""
        o = _make_order()
        self.assertIsNone(o.dcf_check)
        self.assertEqual(o.dcf_override_reason, "")
        print("  [2] PlannedOrder backward-compat (dcf_check=None): OK")

    def test_3_load_plan_preserves_dcf_check(self):
        """load_plan đọc được dcf_check từ file JSON — field không bị filter."""
        raw_order = {
            "id": "BUY-VCB-01", "ticker": "VCB", "side": "buy",
            "qty": 100, "ref_price": 50000,
            "dcf_check": DCF_RICH,
            "dcf_override_reason": "valuation premium justified by ROIC",
        }
        raw_plan = {
            "plan_date": "2099-01-01", "signal_date": "2099-01-01",
            "strategy": "V24", "strategy_version": "2.4",
            "state": 3, "state_name": "NEUTRAL",
            "nav_basis": {"account_nav": 1e9, "paper_nav": 1e9, "scale": 1.0},
            "orders": [raw_order], "account": _TAG, "created_at": "2099-01-01T00:00:00",
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, f"plan_{_TAG}_2099-01-01.json")
            with open(path, "w") as f:
                json.dump(raw_plan, f)
            # Patch PLAN_DIR trong module
            import trading_bot.plan as _plan_mod
            orig = _plan_mod.PLAN_DIR
            try:
                _plan_mod.PLAN_DIR = tmp
                plan = load_plan("2099-01-01", account=_TAG)
            finally:
                _plan_mod.PLAN_DIR = orig
        self.assertIsNotNone(plan)
        o = plan.orders[0]
        self.assertEqual(o.dcf_check["status"], "RICH")
        self.assertEqual(o.dcf_override_reason, "valuation premium justified by ROIC")
        print("  [3] load_plan() giữ dcf_check từ JSON: OK")

    def test_4_executor_state_has_dcf_check(self):
        """Executor state['parents'][order_id]['dcf_check'] = dcf_check của order."""
        plan = _make_plan([_make_order(dcf_check=DCF_CHEAP)])
        e = _make_executor(plan)
        o = plan.orders[0]
        self.assertEqual(e.state["parents"][o.id]["dcf_check"], DCF_CHEAP)
        print("  [4] Executor state giữ dcf_check trong parents: OK")

    def test_5_executor_state_no_dcf_is_none(self):
        """Khi order không có dcf_check, parents[id]['dcf_check'] = None."""
        plan = _make_plan([_make_order()])
        e = _make_executor(plan)
        o = plan.orders[0]
        self.assertIsNone(e.state["parents"][o.id]["dcf_check"])
        print("  [5] Executor state dcf_check=None khi order không có: OK")

    def test_6_sync_fills_publishes_bus_for_rich_robust_buy(self):
        """_sync_fills gọi _publish_bot_event khi BUY + RICH + robust=True."""
        published = []

        import trading_bot.executor as _exec_mod
        orig_publish = _exec_mod._publish_bot_event

        def _capture(event_type, topic, payload):
            published.append({"event_type": event_type, "topic": topic, "payload": payload})

        _exec_mod._publish_bot_event = _capture
        try:
            plan = _make_plan([_make_order(dcf_check=DCF_RICH,
                                           dcf_override_reason="strong conviction")])
            e = _make_executor(plan)
            o = plan.orders[0]
            ps = e.state["parents"][o.id]
            # Simulate child order
            child_oid = "child-001"
            ps["children"] = [{"oid": child_oid, "qty": 100, "price": 50000,
                                "filled": 0, "status": "open"}]

            class _FakeUpdate:
                filled_qty = 100
                avg_price = 50100
                is_dead = False

            updates = {child_oid: _FakeUpdate()}
            e._sync_fills(updates)
        finally:
            _exec_mod._publish_bot_event = orig_publish

        self.assertEqual(len(published), 1)
        ev = published[0]
        self.assertEqual(ev["topic"], "dcf-rich-fill")
        self.assertEqual(ev["payload"]["ticker"], "VCB")
        self.assertEqual(ev["payload"]["dcf_check"]["status"], "RICH")
        print("  [6] _sync_fills publish bus event cho RICH+robust BUY: OK")

    def test_7_no_bus_event_for_cheap_or_not_computed(self):
        """_sync_fills KHÔNG publish khi status=CHEAP hoặc NOT_COMPUTED."""
        import trading_bot.executor as _exec_mod
        orig_publish = _exec_mod._publish_bot_event
        published = []
        _exec_mod._publish_bot_event = lambda *a, **kw: published.append(a)
        try:
            for dcf in [DCF_CHEAP, DCF_NOT_COMPUTED, None]:
                plan = _make_plan([_make_order(dcf_check=dcf)])
                e = _make_executor(plan)
                o = plan.orders[0]
                ps = e.state["parents"][o.id]
                ps["children"] = [{"oid": "c-1", "qty": 100, "price": 50000,
                                    "filled": 0, "status": "open"}]

                class _FU:
                    filled_qty = 100
                    avg_price = 50000
                    is_dead = False

                e._sync_fills({"c-1": _FU()})
        finally:
            _exec_mod._publish_bot_event = orig_publish
        self.assertEqual(len(published), 0)
        print("  [7] KHÔNG publish khi status=CHEAP/NOT_COMPUTED/None: OK")

    def test_8_no_bus_event_for_sell_rich(self):
        """_sync_fills KHÔNG publish khi SELL side dù status=RICH."""
        import trading_bot.executor as _exec_mod
        orig_publish = _exec_mod._publish_bot_event
        published = []
        _exec_mod._publish_bot_event = lambda *a, **kw: published.append(a)
        try:
            plan = _make_plan([_make_order(side="sell", dcf_check=DCF_RICH)])
            e = _make_executor(plan)
            o = plan.orders[0]
            ps = e.state["parents"][o.id]
            ps["children"] = [{"oid": "c-2", "qty": 100, "price": 50000,
                                "filled": 0, "status": "open"}]

            class _FU:
                filled_qty = 100
                avg_price = 50000
                is_dead = False

            e._sync_fills({"c-2": _FU()})
        finally:
            _exec_mod._publish_bot_event = orig_publish
        self.assertEqual(len(published), 0)
        print("  [8] KHÔNG publish khi SELL side dù RICH: OK")


if __name__ == "__main__":
    print("=== dcf_check_selfcheck.py ===")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDcfCheckEcho)
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
