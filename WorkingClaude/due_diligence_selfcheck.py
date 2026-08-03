# -*- coding: utf-8 -*-
"""Selfcheck cho trading_bot/due_diligence.py (mandate due-diligence 2026-07-21).

Chạy: /home/trido/thanhdt/wc_venv/bin/python due_diligence_selfcheck.py
Hai phần: (A) unit trên dữ liệu tổng hợp — thresholds/cơ học/fail-safe; (B) integration trên
dữ liệu THẬT — tái tạo đúng phát hiện rà tay IVS/TMG/TRC + xác nhận mã sạch không báo động giả.
"""
import os
import unittest

import pandas as pd

import trading_bot.due_diligence as dd


def _row(**kw):
    base = dict(ticker="XXX", time="2026-07-20", Close=10000.0, Price=10000.0,
                Volume=1e6, Volume_3M_P50=1e6,
                NP_P0=10e9, NP_P1=8e9, NP_P2=7e9, NP_P3=6e9, NP_P4=5e9,
                ROE5Y=0.15, ROE_Min3Y=0.10, FSCORE=7.0, Debt_Eq_P0=0.5, PE=12.0)
    base.update(kw)
    return pd.Series(base)


class Unit(unittest.TestCase):
    def setUp(self):
        self._lr, self._ip, self._an = dd._latest_row, dd._in_universe, dd._anomaly_note
        dd._in_universe = lambda t, a: (True, "2026-07-20", "QUALITY_OK")
        dd._anomaly_note = lambda t, a: ""

    def tearDown(self):
        dd._latest_row, dd._in_universe, dd._anomaly_note = self._lr, self._ip, self._an

    def _dd(self, row, book="BAL", ctx=None):
        dd._latest_row = lambda t, a: row
        c = {"asof": "2026-07-21", "skip_dcf": True}
        c.update(ctx or {})
        return dd.run_due_diligence("XXX", book, c)

    def test_01_liquidity_ok(self):
        s = self._dd(_row())                       # ADV = 1e6 × 10k = 10 tỷ
        self.assertIn("thanh khoản OK", s)
        self.assertNotIn("🔴", s)

    def test_02_liquidity_thin(self):
        s = self._dd(_row(Volume_3M_P50=1e5))      # ADV = 1 tỷ < sàn 2 tỷ
        self.assertIn("thanh khoản mỏng", s)

    def test_03_liquidity_dead(self):
        s = self._dd(_row(Volume_3M_P50=0.0))      # đúng ca TMG
        self.assertIn("thanh khoản ~0", s)
        self.assertIn("NGOÀI mô hình backtest", s)

    def test_04_order_vs_adv(self):
        s = self._dd(_row(Volume_3M_P50=1e4), ctx={"est_value_vnd": 40e6})  # 40tr/100tr = 40%
        self.assertIn("40% ADV", s)
        self.assertIn("🔴", s)

    def test_05_outside_universe(self):
        dd._in_universe = lambda t, a: (False, "2025-12-31", None)
        self.assertIn("NGOÀI universe_pit", self._dd(_row()))

    def test_05b_universe_unknown_no_fallback(self):
        # đọc lỗi -> "n/a", KHÔNG được kết luận NGOÀI, KHÔNG được fallback ticker_prune (§4.3)
        dd._in_universe = lambda t, a: (None, None, None)
        s = self._dd(_row())
        self.assertIn("universe_pit: n/a", s)
        self.assertNotIn("NGOÀI", s)

    def test_05c_quality_flag_shown(self):
        dd._in_universe = lambda t, a: (True, "2026-07-20", "RATING_FAIL")
        self.assertIn("cờ chất lượng RATING_FAIL", self._dd(_row()))

    def test_06_pead_negative_base(self):
        s = self._dd(_row(NP_P4=-3e9), book="LAG")
        self.assertIn("surprise PHỒNG CƠ HỌC", s)

    def test_07_pead_loss_quarter_in_base(self):
        s = self._dd(_row(NP_P1=-1e9), book="LAG")   # đúng ca IVS
        self.assertIn("quý LỖ trong nền", s)

    def test_08_pead_clean(self):
        self.assertIn("nền YoY dương", self._dd(_row(), book="LAG"))

    def test_09_pead_only_for_lag(self):
        """Trục cơ học surprise chỉ có nghĩa với LAG/PEAD — không bôi vào book khác."""
        self.assertNotIn("nền YoY", self._dd(_row(), book="BAL"))

    def test_10_anomaly_echo(self):
        dd._anomaly_note = lambda t, a: "⚠ cờ bất thường H [IDIOCRASH] ngày 2026-07-20"
        self.assertIn("IDIOCRASH", self._dd(_row()))

    def test_11_unknown_ticker_no_raise(self):
        dd._latest_row = lambda t, a: None
        s = dd.run_due_diligence("ZZZZ", "BAL", {"asof": "2026-07-21"})
        self.assertIn("DD n/a", s)

    def test_12_internal_error_no_raise(self):
        """Fail-safe tuyệt đối: lỗi ở tầng dữ liệu KHÔNG được ném ra report."""
        def boom(t, a):
            raise RuntimeError("cache hỏng")
        dd._latest_row = boom
        s = dd.run_due_diligence("XXX", "BAL", {"asof": "2026-07-21"})
        self.assertIn("DD n/a", s)
        self.assertIn("cache hỏng", s)

    def test_13_as_dict(self):
        dd._latest_row = lambda t, a: _row()
        d = dd.run_due_diligence("XXX", "LAG", {"asof": "2026-07-21", "skip_dcf": True},
                                 as_dict=True)
        self.assertEqual(d["ticker"], "XXX")
        for k in ("liquidity", "fundamentals", "signal_mechanics", "in_universe", "quality_flag"):
            self.assertIn(k, d)

    def test_14_missing_fields(self):
        s = self._dd(_row(Volume_3M_P50=None, NP_P0=None, NP_P1=None, NP_P2=None,
                          NP_P3=None, NP_P4=None, FSCORE=None), book="LAG")
        self.assertIn("thanh khoản: n/a", s)
        self.assertIn("surprise: n/a", s)
        self.assertIn("FSCORE n/a", s)


class RedFlag(unittest.TestCase):
    """Cờ ĐỎ cơ học + bước xác nhận dd_override_reason (2026-08-03, sau case DHD).

    Bất biến quan trọng nhất: cờ sinh TẠI CHỖ tính (mã cờ), KHÔNG grep emoji — nên các test
    này khẳng định `red_flags` chứ không khẳng định câu chữ hiển thị."""

    def setUp(self):
        self._lr, self._ip, self._an = dd._latest_row, dd._in_universe, dd._anomaly_note
        dd._in_universe = lambda t, a: (True, "2026-07-20", "QUALITY_OK")
        dd._anomaly_note = lambda t, a: ""

    def tearDown(self):
        dd._latest_row, dd._in_universe, dd._anomaly_note = self._lr, self._ip, self._an

    def _d(self, row, book="BAL", ctx=None):
        dd._latest_row = lambda t, a: row
        c = {"asof": "2026-07-21", "skip_dcf": True}
        c.update(ctx or {})
        return dd.run_due_diligence("XXX", book, c, as_dict=True)

    def test_30_clean_no_red_flag(self):
        d = self._d(_row())
        self.assertEqual(d["red_flags"], [])
        self.assertFalse(d["has_red_flag"])

    def test_31_dead_liquidity_flag(self):
        self.assertIn("THANH_KHOAN_CHET", self._d(_row(Volume_3M_P50=0.0))["red_flags"])

    def test_32_thin_liquidity_is_NOT_red(self):
        """Mỏng (<2 tỷ) = mức ⚠ CÂN NHẮC, không phải mức phải viết lý do — giữ nguyên ngưỡng cũ."""
        d = self._d(_row(Volume_3M_P50=1e5))          # ADV 1 tỷ
        self.assertFalse(d["has_red_flag"])

    def test_33_outside_universe_flag(self):
        dd._in_universe = lambda t, a: (False, "2025-12-31", None)
        self.assertIn("NGOAI_UNIVERSE", self._d(_row())["red_flags"])

    def test_34_universe_unknown_is_NOT_red(self):
        """Không đọc được universe → "n/a", KHÔNG được kết luận NGOÀI ⇒ cũng không được cắm cờ."""
        dd._in_universe = lambda t, a: (None, None, None)
        self.assertFalse(self._d(_row())["has_red_flag"])

    def test_35_order_too_large_vs_adv(self):
        # ADV = 1e5 × 10.000đ = 1 tỷ (mỏng nhưng KHÔNG chết) → cô lập đúng trục kích thước lệnh
        d = self._d(_row(Volume_3M_P50=1e5), ctx={"est_value_vnd": 400e6})   # 40% ADV > 25%
        self.assertEqual(d["red_flags"], ["LENH_QUA_LON_VS_ADV"])
        # 12% ADV = chỉ ⚠, chưa tới ngưỡng đỏ
        self.assertFalse(self._d(_row(Volume_3M_P50=1e5),
                                 ctx={"est_value_vnd": 120e6})["has_red_flag"])

    def test_36_pead_inflated_surprise_flag(self):
        self.assertIn("SURPRISE_PHONG_CO_HOC", self._d(_row(NP_P4=-3e9), book="LAG")["red_flags"])
        # trục PEAD không áp cho book khác ⇒ không cờ
        self.assertFalse(self._d(_row(NP_P4=-3e9), book="BAL")["has_red_flag"])

    def test_37_dd_cannot_run_is_red(self):
        """Mua mã mà DD không chạy được = mua mù → vẫn phải có người xác nhận."""
        dd._latest_row = lambda t, a: None
        d = dd.run_due_diligence("ZZZZ", "BAL", {"asof": "2026-07-21"}, as_dict=True)
        self.assertEqual(d["red_flags"], ["DD_KHONG_CHAY_DUOC"])

        def boom(t, a):
            raise RuntimeError("cache hỏng")
        dd._latest_row = boom
        d2 = dd.run_due_diligence("XXX", "BAL", {"asof": "2026-07-21"}, as_dict=True)
        self.assertTrue(d2["has_red_flag"])

    def test_38_all_codes_documented(self):
        """Mọi mã cờ sinh ra phải có mô tả trong RED_FLAG_CODES (skill + report đọc từ đây)."""
        seen = set()
        dd._in_universe = lambda t, a: (False, "2025-12-31", None)
        # thanh khoản CHẾT (adv=0) làm trục %ADV tắt theo thiết kế → cần 2 lượt để phủ hết mã cờ
        seen |= set(self._d(_row(Volume_3M_P50=0.0, NP_P4=-3e9), book="LAG")["red_flags"])
        seen |= set(self._d(_row(Volume_3M_P50=1e5), book="LAG",
                            ctx={"est_value_vnd": 400e6})["red_flags"])
        dd._latest_row = lambda t, a: None
        seen |= set(dd.run_due_diligence("ZZZZ", "BAL", {"asof": "2026-07-21"},
                                         as_dict=True)["red_flags"])
        self.assertEqual(seen - set(dd.RED_FLAG_CODES), set())
        self.assertEqual(seen, set(dd.RED_FLAG_CODES))   # không có mã chết trong bảng mô tả

    def test_39_warning_line_needs_override(self):
        dd._latest_row = lambda t, a: _row(Volume_3M_P50=0.0)
        base = {"asof": "2026-07-21", "skip_dcf": True}
        s_no = dd.run_due_diligence("XXX", "BAL", base)
        self.assertIn("cần dd_override_reason", s_no)
        s_ok = dd.run_due_diligence("XXX", "BAL", dict(base, dd_override_reason="user chốt: size nhỏ"))
        self.assertIn("DD cờ đỏ", s_ok)
        self.assertNotIn("cần dd_override_reason", s_ok)
        # bên BÁN không hỏi lý do mua
        self.assertNotIn("DD cờ đỏ", dd.run_due_diligence("XXX", "BAL", dict(base, side="sell")))

    def test_40_dd_check_for_order_shape(self):
        dd._latest_row = lambda t, a: _row(Volume_3M_P50=0.0)
        c = dd.dd_check_for_order("XXX", "BAL", "2026-07-21", est_value_vnd=1e6)
        self.assertTrue(c["has_red_flag"])
        self.assertEqual(c["red_flags"], ["THANH_KHOAN_CHET"])
        for k in ("as_of", "data_date", "universe_source", "evidence"):
            self.assertIn(k, c)


class NotAGate(unittest.TestCase):
    """Bất biến MANDATE GỐC: due-diligence THUẦN THÔNG TIN — cờ đỏ KHÔNG chặn lệnh.

    Cơ chế 2026-08-03 chỉ thêm bước XÁC NHẬN (WARN + audit trail), user KHÔNG yêu cầu biến
    nó thành hard-gate. Test này là cái chặn việc ai đó sau này "tiện tay" biến WARN thành gate."""

    def test_50_execution_path_never_reads_dd_check(self):
        """bot_execute.py (đường quyết định đặt lệnh) không được biết tới dd_check."""
        import re
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "bot_execute.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn("dd_check", src)
        self.assertNotIn("has_red_flag", src)
        self.assertNotIn("dd_override_reason", src)
        # executor.py ĐƯỢC phép nhắc tới — nhưng chỉ trong khối publish audit-trail, không
        # được xuất hiện trong bất kỳ câu điều kiện nào dẫn tới continue/return/skip.
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "trading_bot", "executor.py"), encoding="utf-8") as f:
            ex = f.read().splitlines()
        for i, ln in enumerate(ex):
            if "has_red_flag" in ln:
                nxt = "\n".join(ex[i + 1:i + 4])
                self.assertIn("_publish_bot_event", nxt)
                self.assertFalse(re.search(r"\b(continue|return|break)\b", nxt))

    def test_51_red_flag_order_survives_plan_filters(self):
        """Lệnh có cờ đỏ + KHÔNG có override vẫn đi qua cascade lọc của plan → vẫn sẽ được đặt."""
        from trading_bot.plan import (PlannedOrder, TradePlan, filter_excluded_tickers,
                                      net_offsetting_orders)
        o = PlannedOrder(id="BUY-DHD-01", ticker="DHD", side="buy", qty=200, ref_price=26700,
                         book="LAG",
                         dd_check={"has_red_flag": True,
                                   "red_flags": ["THANH_KHOAN_CHET", "NGOAI_UNIVERSE"]},
                         dd_override_reason="")       # CỐ Ý thiếu lý do
        plan = TradePlan(plan_date="2026-08-03", signal_date="2026-07-31", strategy="V2.4",
                         strategy_version="v2.4", state=3, state_name="NEUTRAL",
                         nav_basis={}, orders=[o], account="TESTDD")
        plan, blocked = filter_excluded_tickers(plan, [])
        plan, _adj = net_offsetting_orders(plan)
        self.assertEqual([x.ticker for x in plan.orders], ["DHD"])
        self.assertEqual(blocked, [])

    def test_52_plan_roundtrip_keeps_dd_fields(self):
        """save→load_plan phải giữ dd_check/dd_override_reason (load_plan lọc field lạ)."""
        import tempfile
        import trading_bot.plan as P
        from trading_bot.plan import PlannedOrder, TradePlan
        o = PlannedOrder(id="BUY-DHD-01", ticker="DHD", side="buy", qty=200, ref_price=26700,
                         book="LAG", dd_check={"has_red_flag": True, "red_flags": ["X"]},
                         dd_override_reason="user chốt: size nhỏ, giữ cửa sổ PEAD")
        plan = TradePlan(plan_date="2026-08-03", signal_date="2026-07-31", strategy="V2.4",
                         strategy_version="v2.4", state=3, state_name="NEUTRAL",
                         nav_basis={}, orders=[o], account="TESTDDRT")
        old = P.PLAN_DIR
        with tempfile.TemporaryDirectory() as tmp:
            P.PLAN_DIR = tmp
            try:
                plan.save()
                back = P.load_plan("2026-08-03", account="TESTDDRT")
            finally:
                P.PLAN_DIR = old
        self.assertTrue(back.orders[0].dd_check["has_red_flag"])
        self.assertIn("size nhỏ", back.orders[0].dd_override_reason)


class Integration(unittest.TestCase):
    """Dữ liệu THẬT — phải tái tạo đúng những gì Mike+Taylor tìm bằng tay ngày 2026-07-21."""
    ASOF = "2026-07-21"

    def test_20_TMG_dead_liquidity(self):
        s = dd.run_due_diligence("TMG", "LAG", {"asof": self.ASOF})
        self.assertIn("thanh khoản ~0", s)
        self.assertIn("NGOÀI universe_pit", s)

    def test_21_IVS_thin_and_inflated_surprise(self):
        s = dd.run_due_diligence("IVS", "LAG", {"asof": self.ASOF, "est_value_vnd": 70e6})
        self.assertIn("thanh khoản mỏng", s)
        self.assertIn("NGOÀI universe_pit", s)
        self.assertIn("quý LỖ trong nền", s)

    def test_22_TRC_thin_but_in_universe(self):
        s = dd.run_due_diligence("TRC", "LAG", {"asof": self.ASOF})
        self.assertIn("thanh khoản mỏng", s)
        self.assertNotIn("NGOÀI universe_pit", s)
        # TRC ở TRONG universe nhưng rating 8L = 4 -> cờ chất lượng phải hiện (Q-C)
        self.assertIn("cờ chất lượng RATING_FAIL", s)

    def test_23_clean_names_no_false_alarm(self):
        for t in ("FPT", "MBB", "VNM"):
            s = dd.run_due_diligence(t, "BAL", {"asof": self.ASOF, "skip_dcf": True})
            self.assertIn("thanh khoản OK", s)
            self.assertNotIn("🔴", s)

    def test_24_DHD_case_2026_08_03(self):
        """Ca thật đã lọt lưới ngày 2026-08-03: DD in đủ 2 dòng 🔴 mà không ai phải xác nhận.

        Sau fix: cùng dữ liệu đó phải sinh cờ cơ học + đòi dd_override_reason."""
        ctx = {"asof": "2026-08-03", "skip_dcf": True, "est_value_vnd": 5.34e6}
        d = dd.run_due_diligence("DHD", "LAG", ctx, as_dict=True)
        self.assertEqual(sorted(d["red_flags"]), ["NGOAI_UNIVERSE", "THANH_KHOAN_CHET"])
        self.assertIn("cần dd_override_reason", dd.run_due_diligence("DHD", "LAG", ctx))
        self.assertNotIn("cần dd_override_reason",
                         dd.run_due_diligence("DHD", "LAG",
                                              dict(ctx, dd_override_reason="user chốt 08-03")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
