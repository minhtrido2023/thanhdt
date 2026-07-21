# -*- coding: utf-8 -*-
"""Selfcheck cho trading_bot/due_diligence.py (mandate due-diligence 2026-07-21).

Chạy: /home/trido/thanhdt/wc_venv/bin/python due_diligence_selfcheck.py
Hai phần: (A) unit trên dữ liệu tổng hợp — thresholds/cơ học/fail-safe; (B) integration trên
dữ liệu THẬT — tái tạo đúng phát hiện rà tay IVS/TMG/TRC + xác nhận mã sạch không báo động giả.
"""
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
        self._lr, self._ip, self._an = dd._latest_row, dd._in_prune, dd._anomaly_note
        dd._in_prune = lambda t, a: (True, "2026-07-20")
        dd._anomaly_note = lambda t, a: ""

    def tearDown(self):
        dd._latest_row, dd._in_prune, dd._anomaly_note = self._lr, self._ip, self._an

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

    def test_05_outside_prune(self):
        dd._in_prune = lambda t, a: (False, "2025-12-31")
        self.assertIn("NGOÀI ticker_prune", self._dd(_row()))

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
        for k in ("liquidity", "fundamentals", "signal_mechanics", "in_prune"):
            self.assertIn(k, d)

    def test_14_missing_fields(self):
        s = self._dd(_row(Volume_3M_P50=None, NP_P0=None, NP_P1=None, NP_P2=None,
                          NP_P3=None, NP_P4=None, FSCORE=None), book="LAG")
        self.assertIn("thanh khoản: n/a", s)
        self.assertIn("surprise: n/a", s)
        self.assertIn("FSCORE n/a", s)


class Integration(unittest.TestCase):
    """Dữ liệu THẬT — phải tái tạo đúng những gì Mike+Taylor tìm bằng tay ngày 2026-07-21."""
    ASOF = "2026-07-21"

    def test_20_TMG_dead_liquidity(self):
        s = dd.run_due_diligence("TMG", "LAG", {"asof": self.ASOF})
        self.assertIn("thanh khoản ~0", s)
        self.assertIn("NGOÀI ticker_prune", s)

    def test_21_IVS_thin_and_inflated_surprise(self):
        s = dd.run_due_diligence("IVS", "LAG", {"asof": self.ASOF, "est_value_vnd": 70e6})
        self.assertIn("thanh khoản mỏng", s)
        self.assertIn("NGOÀI ticker_prune", s)
        self.assertIn("quý LỖ trong nền", s)

    def test_22_TRC_thin_but_in_prune(self):
        s = dd.run_due_diligence("TRC", "LAG", {"asof": self.ASOF})
        self.assertIn("thanh khoản mỏng", s)
        self.assertNotIn("NGOÀI ticker_prune", s)

    def test_23_clean_names_no_false_alarm(self):
        for t in ("FPT", "MBB", "VNM"):
            s = dd.run_due_diligence(t, "BAL", {"asof": self.ASOF, "skip_dcf": True})
            self.assertIn("thanh khoản OK", s)
            self.assertNotIn("🔴", s)


if __name__ == "__main__":
    unittest.main(verbosity=2)
