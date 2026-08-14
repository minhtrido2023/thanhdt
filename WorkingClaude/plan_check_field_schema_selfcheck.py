# -*- coding: utf-8 -*-
"""Selfcheck: `dcf_check`/`dd_check` SAI KIỂU trong plan không được làm hỏng polling.

Tái lập ĐÚNG sự cố 2026-08-11 → 08-14 (bus question `plan-dd-check-string-gay-poll-fail-moi-fill`,
incident `mike/kb/incidents/2026-08/2026-08-11-plan-dd-check-string-poll-fail.md`): plan ghi
`dd_check`/`dcf_check` dạng CHUỖI văn xuôi thay vì object ⇒ `Executor._sync_fills` gọi
`_dd.get(...)` ⇒ `AttributeError: 'str' object has no attribute 'get'` sau MỖI fill ⇒ 22
POLL_FAIL ZaloPay + 27 SpaceX trong một phiên (POLL_FAIL khớp 1:1 số FILL).

Ca [1]-[3] là bằng chứng NGƯỢC (control): chúng dựng lại chính xác lỗi cũ trên plan THẬT của
production 08-11/08-12/08-14 và chứng minh nó vẫn nổ khi BỎ lớp chuẩn hoá — nếu ai xoá
`normalize_check_field()` thì các ca sau đỏ, không phải xanh im lặng.

Ca [10]-[12] khoá NGUỒN sinh chuỗi thứ nhất (`discretionary_accumulation.py`) — nguồn cố định,
tái diễn mọi phiên gom; vá ranh giới nạp plan mà để nguồn nguyên vẹn thì mỗi phiên vẫn ghi ra
một plan sai schema cho người đọc.

TAG = "selfcheck_chkfield"  # unique — không dùng chung với selfcheck khác
"""

import glob
import json
import os
import sys
import tempfile
import unittest

WORKDIR = os.path.dirname(os.path.abspath(__file__))
# §5b coding_guidelines: KHÔNG cho Executor._publish_bot_event ghi event GIẢ vào bus production.
# PHẢI đứng trước mọi lần dựng Executor.
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")

sys.path.insert(0, WORKDIR)

_TAG = "selfcheck_chkfield"
_PLAN_DATE = "2026-08-14"
_EXEC_DIR = os.path.join(WORKDIR, "data", "execution_logs")
for _f in glob.glob(os.path.join(_EXEC_DIR, f"exec_{_TAG}_*")):
    os.remove(_f)

from trading_bot.plan import (CHECK_FIELDS_AS_DICT, PlannedOrder, TradePlan,
                              load_plan, normalize_check_field)
from trading_bot.executor import Executor
from trading_bot.config import PLAN_DIR

# Chuỗi THẬT, sao y từ plan production (không phải chuỗi bịa) — mỗi dòng là một hình dạng khác
# nhau mà nguồn sinh plan đã thực sự ghi ra.
REAL_DD_STR = "PASS — dd_check_for_order 2026-08-11, 0 red flag"
REAL_DCF_STR = "CHEAP"
REAL_DISC_DCF_STR = "N/A (SOTP/asset-backed deep-value, không dùng LAG/BAL gate)"


class _FakeBroker:
    def poll_orders(self): return {}
    def cancel_order(self, oid): pass


class _FakeUpdate:
    filled_qty = 100
    avg_price = 50100
    is_dead = False


def _make_order(dcf_check=None, dd_check=None, side="buy", ticker="TV1"):
    return PlannedOrder(id=f"BUY-{ticker}-DISC-01", ticker=ticker, side=side, qty=100,
                        ref_price=50000, book="DISCRETIONARY_SPECIAL",
                        dcf_check=dcf_check, dd_check=dd_check)


def _make_plan(orders, account=_TAG):
    return TradePlan(plan_date=_PLAN_DATE, signal_date="2026-08-13", strategy="V24",
                     strategy_version="2.4", state=3, state_name="NEUTRAL",
                     nav_basis={"account_nav": 1e9, "paper_nav": 1e9, "scale": 1.0},
                     orders=orders, account=account,
                     created_at=f"{_PLAN_DATE}T00:00:00")


def _make_executor(plan):
    return Executor(plan, _FakeBroker(), {"mode": "paper", "max_participation": 0.10,
                                          "fill_timing_enabled": False,
                                          "extreme_regime_enabled": False,
                                          "chase_cap_vol_scale_enabled": False},
                    shared={})


def _run_one_fill(e, o):
    """Đúng đường đi của sự cố: 1 lệnh con khớp đủ → _sync_fills đọc dcf_check/dd_check."""
    ps = e.state["parents"][o.id]
    ps["children"] = [{"oid": "c-1", "qty": 100, "price": 50000, "filled": 0,
                       "status": "open"}]
    e._sync_fills({"c-1": _FakeUpdate()})


class TestReproduceIncident(unittest.TestCase):
    """[1]-[3] Control: lỗi cũ PHẢI tái lập được khi bỏ lớp chuẩn hoá."""

    def test_1_raw_str_still_breaks_sync_fills(self):
        """Gán chuỗi TRỰC TIẾP vào order SAU khi Executor đã chuẩn hoá ⇒ vẫn nổ y sự cố."""
        plan = _make_plan([_make_order()])
        e = _make_executor(plan)
        o = plan.orders[0]
        o.dd_check = REAL_DD_STR          # mô phỏng đúng: bỏ qua CẢ HAI lớp chuẩn hoá
        with self.assertRaises(AttributeError) as cm:
            _run_one_fill(e, o)
        self.assertIn("has no attribute 'get'", str(cm.exception))
        print(f"  [1] control: chuỗi thô vào _sync_fills VẪN nổ đúng lỗi cũ "
              f"({str(cm.exception)[:48]}…): OK")

    def test_2_dcf_str_also_breaks(self):
        """Cùng lỗi ở nhánh dcf_check (executor.py đọc _dcf.get trước _dd.get)."""
        plan = _make_plan([_make_order()])
        e = _make_executor(plan)
        o = plan.orders[0]
        o.dcf_check = REAL_DCF_STR
        with self.assertRaises(AttributeError):
            _run_one_fill(e, o)
        print("  [2] control: nhánh dcf_check cũng nổ khi là chuỗi: OK")

    def test_3_executor_normalizes_so_fill_survives(self):
        """Plan dựng trong bộ nhớ với CẢ HAI field là chuỗi → 1 fill đi qua, KHÔNG lỗi."""
        plan = _make_plan([_make_order(dcf_check=REAL_DCF_STR, dd_check=REAL_DD_STR)])
        e = _make_executor(plan)
        o = plan.orders[0]
        self.assertIsInstance(o.dcf_check, dict)
        self.assertIsInstance(o.dd_check, dict)
        _run_one_fill(e, o)                       # không raise = điều đang kiểm
        self.assertTrue(e.state["parents"][o.id]["done"])
        print("  [3] Executor chuẩn hoá ⇒ fill đi qua trọn vẹn, parent DONE: OK")


class TestNormalizeSemantics(unittest.TestCase):
    """[4]-[9] Ngữ nghĩa: giữ nguyên plan đúng, và 'chưa biết' ≠ 'đã kiểm và sạch'."""

    def test_4_dict_passthrough_unchanged(self):
        """dict → NGUYÊN VẸN, cùng object. Plan đúng schema không đổi một byte."""
        d = {"status": "CHEAP", "margin_of_safety": 0.35, "robust": True}
        self.assertIs(normalize_check_field("dcf_check", d, "X"), d)
        self.assertIsNone(normalize_check_field("dd_check", None, "X"))
        self.assertIsNone(normalize_check_field("dd_check", "   ", "X"))
        print("  [4] dict giữ nguyên object; None/chuỗi rỗng → None: OK")

    def test_5_dd_str_becomes_unknown_not_clean(self):
        """has_red_flag phải là None (CHƯA BIẾT), tuyệt đối KHÔNG False (khẳng định sạch)."""
        out = normalize_check_field("dd_check", REAL_DD_STR, "X", warn=False)
        self.assertIsNone(out["has_red_flag"])
        self.assertIsNot(out["has_red_flag"], False)
        self.assertTrue(out["schema_error"])
        self.assertIn(REAL_DD_STR, out["evidence"])      # text gốc KHÔNG được mất
        print("  [5] dd_check: has_red_flag=None (chưa biết) + giữ text gốc: OK")

    def test_6_dcf_str_becomes_not_computed(self):
        out = normalize_check_field("dcf_check", REAL_DCF_STR, "X", warn=False)
        self.assertEqual(out["status"], "NOT_COMPUTED")
        self.assertFalse(out["robust"])
        self.assertIsNone(out["margin_of_safety"])
        self.assertTrue(out["schema_error"])
        self.assertIn(REAL_DCF_STR, out["reason"])
        print("  [6] dcf_check: status=NOT_COMPUTED + giữ text gốc: OK")

    def test_7_no_audit_event_fires_from_normalized(self):
        """Dạng chuẩn hoá KHÔNG được kích event dcf-rich-fill / dd-redflag-fill (chưa biết
        gì thì không được báo như đã biết)."""
        import trading_bot.executor as _exec_mod
        published = []
        orig = _exec_mod._publish_bot_event
        _exec_mod._publish_bot_event = lambda *a, **kw: published.append(a)
        try:
            plan = _make_plan([_make_order(dcf_check=REAL_DCF_STR, dd_check=REAL_DD_STR)])
            e = _make_executor(plan)
            _run_one_fill(e, plan.orders[0])
        finally:
            _exec_mod._publish_bot_event = orig
        self.assertEqual(published, [])
        print("  [7] không kích audit event giả từ dạng 'chưa xác định': OK")

    def test_8_real_dict_audit_events_still_fire(self):
        """Chốt chặn ngược: fix KHÔNG được làm mất event thật của plan ĐÚNG schema."""
        import trading_bot.executor as _exec_mod
        published = []
        orig = _exec_mod._publish_bot_event
        _exec_mod._publish_bot_event = lambda et, tp, pl: published.append(tp)
        try:
            plan = _make_plan([_make_order(
                dcf_check={"status": "RICH", "robust": True, "margin_of_safety": -0.2},
                dd_check={"has_red_flag": True, "red_flags": ["X"]})])
            e = _make_executor(plan)
            _run_one_fill(e, plan.orders[0])
        finally:
            _exec_mod._publish_bot_event = orig
        self.assertEqual(sorted(published), ["dcf-rich-fill", "dd-redflag-fill"])
        print("  [8] event thật (RICH+robust / red flag) VẪN kích đúng: OK")

    def test_9_non_str_types_also_handled(self):
        """Không chỉ chuỗi: số/list/bool cũng phải ra dict, không được lọt xuống executor."""
        for bad in (123, ["a"], True, 1.5):
            for name in CHECK_FIELDS_AS_DICT:
                self.assertIsInstance(normalize_check_field(name, bad, "X", warn=False), dict)
        print("  [9] số/list/bool cũng được quy về dict: OK")


class TestSourceOne(unittest.TestCase):
    """[10]-[11] Nguồn sinh chuỗi #1 — discretionary_accumulation.py (lỗi CODE cố định)."""

    def test_10_no_literal_string_dcf_check_in_source(self):
        with open(os.path.join(WORKDIR, "trading_bot", "discretionary_accumulation.py"),
                  encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn(f'"dcf_check": "{REAL_DISC_DCF_STR}"', src)
        self.assertIn('"dcf_check": {"status": "NOT_COMPUTED"', src)
        print("  [10] discretionary_accumulation.py không còn literal chuỗi dcf_check: OK")

    def test_11_compute_session_order_emits_dict(self):
        """Gọi THẬT compute_session_order() → dcf_check là dict đúng schema."""
        from trading_bot.discretionary_accumulation import compute_session_order
        state = {"ticker": "TV1", "target_qty": 5000, "lot_size": 100,
                 "per_session_cap_pct_adv": 0.05, "adv_ref_vnd": 600_000_000,
                 "price_band": {"no_chase_ceiling": 20000, "resting_limit": 19500},
                 # dict, KHÔNG phải chuỗi ngày — engine đọc `hard_expiry.halted` (cờ do NGƯỜI
                 # xác nhận). Cả 2 state file production đều là dict; ghi chuỗi ở đây là lỗi
                 # fixture, không phải hình dạng dữ liệu thật.
                 "hard_expiry": {"halted": False}}
        order, _ = compute_session_order(state, filled_qty=0, prev_turnover_vnd=6e8,
                                         prev_price_vnd=19000, plan_date=_PLAN_DATE,
                                         now_iso=f"{_PLAN_DATE}T08:30:00")
        self.assertIsInstance(order, dict, f"compute_session_order không chèn lệnh: {order!r}")
        self.assertIsInstance(order["dcf_check"], dict)
        self.assertEqual(order["dcf_check"]["status"], "NOT_COMPUTED")
        self.assertEqual(order["dcf_check"]["as_of"], _PLAN_DATE)
        print("  [11] compute_session_order() sinh dcf_check dạng dict: OK")


class TestLoadPlanBoundary(unittest.TestCase):
    """[12]-[14] Ranh giới nạp plan — nguồn #2 (plan soạn tay) chỉ chặn được ở đây."""

    def _write_and_load(self, order_extra):
        path = os.path.join(PLAN_DIR, f"plan_{_TAG}_{_PLAN_DATE}.json")
        os.makedirs(PLAN_DIR, exist_ok=True)
        base = {"id": "BUY-TV1-DISC-01", "ticker": "TV1", "side": "buy", "qty": 100,
                "ref_price": 19000, "book": "DISCRETIONARY_SPECIAL"}
        base.update(order_extra)
        doc = {"plan_date": _PLAN_DATE, "signal_date": "2026-08-13", "strategy": "V24",
               "strategy_version": "2.4", "state": 3, "state_name": "NEUTRAL",
               "nav_basis": {"account_nav": 1e9, "paper_nav": 1e9, "scale": 1.0},
               "orders": [base], "account": _TAG,
               "created_at": f"{_PLAN_DATE}T00:00:00"}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False)
        try:
            return load_plan(_PLAN_DATE, _TAG)
        finally:
            os.remove(path)

    def test_12_load_plan_normalizes_handwritten_prose(self):
        p = self._write_and_load({"dd_check": REAL_DD_STR, "dcf_check": REAL_DCF_STR})
        o = p.orders[0]
        self.assertIsInstance(o.dd_check, dict)
        self.assertIsInstance(o.dcf_check, dict)
        self.assertIn(REAL_DD_STR, o.dd_check["evidence"])
        print("  [12] load_plan() chuẩn hoá plan soạn tay (nguồn #2): OK")

    def test_13_load_plan_keeps_valid_dict_intact(self):
        good = {"has_red_flag": True, "red_flags": ["THANH_KHOAN"], "as_of": "2026-08-14"}
        p = self._write_and_load({"dd_check": good})
        self.assertEqual(p.orders[0].dd_check, good)
        self.assertIsNone(p.orders[0].dcf_check)
        print("  [13] plan đúng schema đi qua load_plan() không đổi: OK")

    def test_14_real_production_plans_all_load_clean(self):
        """Chạy trên MỌI plan thật còn trên đĩa: nạp được + 1 fill không nổ. Đây là ca duy
        nhất chạm dữ liệu sống nên KHÔNG assert giá trị (§23) — chỉ assert BẤT BIẾN
        'field check luôn là dict-hoặc-None sau khi nạp'."""
        n_plan = n_fixed = 0
        for path in sorted(glob.glob(os.path.join(PLAN_DIR, "plan_*_2026-*.json"))):
            fn = os.path.basename(path)[len("plan_"):-len(".json")]
            acc, _, date = fn.rpartition("_")
            if not acc:
                continue
            try:
                p = load_plan(date, acc)
            except Exception as exc:                  # plan cũ khác schema — ngoài phạm vi
                print(f"      (bỏ qua {fn}: {type(exc).__name__})")
                continue
            if p is None:
                continue
            n_plan += 1
            for o in p.orders:
                for cf in CHECK_FIELDS_AS_DICT:
                    v = getattr(o, cf)
                    self.assertTrue(v is None or isinstance(v, dict),
                                    f"{fn} / {o.id} / {cf} = {type(v).__name__}")
                    if isinstance(v, dict) and v.get("schema_error"):
                        n_fixed += 1
        self.assertGreater(n_plan, 0, "không nạp được plan thật nào — kiểm PLAN_DIR")
        print(f"  [14] {n_plan} plan thật nạp sạch, {n_fixed} field sai kiểu được cứu: OK")


if __name__ == "__main__":
    print("=== plan_check_field_schema_selfcheck.py ===")
    unittest.main(verbosity=0, exit=True)
