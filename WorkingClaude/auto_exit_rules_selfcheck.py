#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-check: auto_exit_rules.py — boundary tests cho mốc LAG/BAL/CAPIT (job
Taylor_20260930_080814). Hàm ở đây THUẦN (không đọc đồng hồ/TZ/file) nên không có bẫy §16 —
chạy dưới `env -u TZ` vẫn chỉ để xác nhận điều đó (không có phụ thuộc môi trường nào để lộ ra).

Chạy: python3 auto_exit_rules_selfcheck.py
"""
import sys

import auto_exit_rules as rules

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'} — {name}" + (f"  [{detail}]" if detail else ""))


def main():
    check("LAG @24 KHÔNG exit", rules.lag_should_exit(24) is False)
    check("LAG @25 exit (boundary đúng)", rules.lag_should_exit(25) is True)
    check("LAG @26 exit", rules.lag_should_exit(26) is True)
    check("LAG None KHÔNG exit (fail-safe)", rules.lag_should_exit(None) is False)

    check("BAL @44 KHÔNG exit", rules.bal_should_exit(44) is False)
    check("BAL @45 exit (boundary đúng)", rules.bal_should_exit(45) is True)
    check("BAL None KHÔNG exit (fail-safe)", rules.bal_should_exit(None) is False)

    check("BAL stop-loss @-19.9%,@10phiên KHÔNG trigger", rules.bal_stop_loss_hit(-0.199, 10) is False)
    check("BAL stop-loss @-20%,@10phiên trigger (boundary đúng)",
          rules.bal_stop_loss_hit(-0.20, 10) is True)
    check("BAL stop-loss @-25%,@10phiên trigger", rules.bal_stop_loss_hit(-0.25, 10) is True)
    check("BAL stop-loss @+5% (lãi),@10phiên KHÔNG trigger", rules.bal_stop_loss_hit(0.05, 10) is False)
    check("BAL stop-loss pnl_pct None KHÔNG trigger (fail-safe)",
          rules.bal_stop_loss_hit(None, 10) is False)
    check("BAL stop-loss @-25%,@0phiên KHÔNG trigger (min_hold=2, pin chưa kiểm chứng)",
          rules.bal_stop_loss_hit(-0.25, 0) is False)
    check("BAL stop-loss @-25%,@1phiên KHÔNG trigger (chưa đủ min_hold)",
          rules.bal_stop_loss_hit(-0.25, 1) is False)
    check("BAL stop-loss @-25%,@2phiên trigger (boundary min_hold đúng)",
          rules.bal_stop_loss_hit(-0.25, 2) is True)
    check("BAL stop-loss sessions_held None KHÔNG trigger (fail-safe)",
          rules.bal_stop_loss_hit(-0.25, None) is False)

    check("CAPIT @54 KHÔNG exit, KHÔNG nhắc",
          rules.capit_should_exit(54) is False and rules.capit_should_remind(54) is False)
    check("CAPIT @55 nhắc, CHƯA exit (boundary đúng)",
          rules.capit_should_remind(55) is True and rules.capit_should_exit(55) is False)
    check("CAPIT @59 vẫn nhắc, CHƯA exit", rules.capit_should_remind(59) is True
          and rules.capit_should_exit(59) is False)
    check("CAPIT @60 exit, KHÔNG còn ở trạng thái nhắc (boundary đúng)",
          rules.capit_should_exit(60) is True and rules.capit_should_remind(60) is False)
    check("CAPIT @61 exit", rules.capit_should_exit(61) is True)
    check("CAPIT None: không exit, không nhắc (fail-safe)",
          rules.capit_should_exit(None) is False and rules.capit_should_remind(None) is False)

    check("Hằng số khớp nguồn backtest pin: LAG=25", rules.LAG_EXIT_SESSIONS == 25)
    check("Hằng số khớp nguồn backtest pin: BAL=45", rules.BAL_EXIT_SESSIONS == 45)
    check("Hằng số khớp nguồn backtest pin: BAL stop-loss=-0.20",
          rules.BAL_STOP_LOSS_PCT == -0.20)
    check("Hằng số khớp nguồn backtest pin: BAL stop-loss min_hold=2",
          rules.BAL_STOP_LOSS_MIN_HOLD == 2)
    check("Hằng số khớp nguồn backtest pin: CAPIT=60", rules.CAPIT_EXIT_SESSIONS == 60)
    check("Hằng số nhắc CAPIT=55 (60-5)", rules.CAPIT_REMINDER_SESSIONS == 55)

    print(f"\n{len(PASS)} PASS, {len(FAIL)} FAIL")
    if FAIL:
        print("FAILED:", FAIL)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
