#!/usr/bin/env python3
"""plan_funding_gate_fee_sync_selfcheck.py — khoá phí của gate tiền P0 với nguồn phí chuẩn.

`trading_bot/plan_funding_gate.py` KHÔNG import được `mike/bin/dnse_fee_rates.py` (ranh giới repo)
nên hardcode `FEE_RATE`. File này nằm ở mike/bin, import được CẢ HAI, và fail nếu 2 số lệch nhau —
đổi phí ở một nơi mà quên nơi kia là bị bắt ở lần chạy selfcheck kế tiếp (run_selfchecks.sh).

    python3 bin/plan_funding_gate_fee_sync_selfcheck.py [WORKINGCLAUDE_ROOT]

Đối số tuỳ chọn = gốc WorkingClaude chứa `trading_bot/` (mặc định bản canonical) — để kiểm một
worktree/patch trước khi land. Không đọc broker, không đọc giờ hệ thống ⇒ không phụ thuộc TZ.
aria-H 2026-09-13 (job Taylor_20260913_075547).
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WC_ROOT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else "/home/trido/thanhdt/WorkingClaude"

sys.path.insert(0, HERE)
import dnse_fee_rates  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "plan_funding_gate_under_check", os.path.join(WC_ROOT, "trading_bot", "plan_funding_gate.py"))
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

fails = []


def check(name, ok, got):
    print(f"  {'✔' if ok else '✗ FAIL'} {name}  (got {got})")
    if not ok:
        fails.append(name)


print(f"gate: {spec.origin}")
buy = dnse_fee_rates.FEE_RATE_BUY_PCT / 100.0
sell = dnse_fee_rates.FEE_RATE_SELL_PCT / 100.0
check("FEE_RATE == dnse_fee_rates.FEE_RATE_BUY_PCT/100 (phí vào Σ mua)",
      abs(gate.FEE_RATE - buy) < 1e-12, (gate.FEE_RATE, buy))
check("FEE_RATE == dnse_fee_rates.FEE_RATE_SELL_PCT/100 (net tín dụng JIT bán)",
      abs(gate.FEE_RATE - sell) < 1e-12, (gate.FEE_RATE, sell))
# UPCOM rẻ hơn HOSE ⇒ một hằng số HOSE là cận trên an toàn cho gate (chặt hơn, không lỏng hơn).
upcom = (dnse_fee_rates.BROKER_FEE_PCT + dnse_fee_rates.EXCHANGE_FEE_PCT["UPCOM"]) / 100.0
check("FEE_RATE ≥ phí UPCOM (hằng số duy nhất là cận trên)", gate.FEE_RATE >= upcom - 1e-12,
      (gate.FEE_RATE, upcom))

if fails:
    print(f"FAIL {len(fails)}: {fails}")
    sys.exit(1)
print("PASS 3/3 — plan_funding_gate.FEE_RATE đồng bộ dnse_fee_rates")
