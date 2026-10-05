#!/usr/bin/env python3
"""verify_against_bq tính chân tiền của sự kiện gộp CP+tiền (TPB 2026-10-02). Không gọi BQ (mock)."""
import os, sys, types
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import corp_actions as ca
import dividend_adjusted_return as dar

P = 14400.0
def run(cash, bq_factor):
    ev = types.SimpleNamespace(ex_date="2026-10-02", last_cum_price=P, last_cum_date="2026-10-01",
                               per_share=P - P / bq_factor)
    dar.detect_adjustments_batch = lambda *a, **k: ({"TPB": [ev]}, "2026-10-02")
    act = {"ticker": "TPB", "ex_date": "2026-10-02", "qty_multiplier": 1.15,
           "cash_leg_vnd_per_share": cash}
    return ca.verify_against_bq(act)["verdict"]

fails = 0
def chk(name, got, want):
    global fails
    ok = got == want
    fails += not ok
    print(("PASS " if ok else "FAIL ") + name, "" if ok else f"got={got} want={want}")

chk("gộp CP+tiền, BQ 1,1911, cash=500 ⇒ MATCH", run(500.0, 1.1911), "MATCH")
chk("cùng BQ 1,1911 nhưng cash=0 ⇒ MISMATCH (hành vi cũ giữ nguyên)", run(0.0, 1.1911), "MISMATCH")
chk("thuần CP 1,15, cash=0 ⇒ MATCH (byte-identical)", run(0.0, 1.15), "MATCH")
chk("cash=500 khai nhưng BQ chỉ 1,15 ⇒ MISMATCH", run(500.0, 1.15), "MISMATCH")
print(f"{4 - fails}/4 PASS")
sys.exit(1 if fails else 0)
