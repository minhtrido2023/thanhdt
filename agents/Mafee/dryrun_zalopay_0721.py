#!/usr/bin/env python3
"""Dry-run KHÔNG đặt lệnh — ZaloPay 2026-07-21, xác minh fix reconcile parents on resume.

Tái hiện ĐÚNG pipeline dựng executor của bot_execute.py (load_plan -> filter_excluded_tickers
-> cap_capit_orders -> Executor) trên BẢN SAO state production thật (state cũ 1 parent). Không
gọi step() -> KHÔNG đặt bất kỳ lệnh nào. Broker = dummy (Executor.__init__ không gọi broker).

Mục tiêu: executor khởi tạo được, KHÔNG KeyError ở seed_shared(), SELL-VPB-01 giữ nguyên
(đã done — không re-place), 5 CAPIT có parent sạch sẵn sàng cho phiên 13:00.
"""
import json
import os
import shutil
import sys
import tempfile

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

from trading_bot import executor as ex_mod
from trading_bot.executor import Executor
from trading_bot.plan import load_plan, filter_excluded_tickers, cap_capit_orders

PROD_STATE = os.path.join(WORKDIR, "data", "execution_logs",
                          "exec_ZaloPay_2026-07-21_state.json")


def main():
    plan = load_plan("2026-07-21", "ZaloPay")
    assert plan is not None
    print(f"[dryrun] load_plan: {len(plan.orders)} order — {[o.id for o in plan.orders]}")

    # đúng pipeline bot_execute.py
    plan, blocked = filter_excluded_tickers(plan, ["DGC"])
    print(f"[dryrun] filter_excluded_tickers(DGC): bỏ {len(blocked)} lệnh "
          f"(none của kế hoạch này là DGC)")
    plan, capped = cap_capit_orders(plan, "ZaloPay")
    print(f"[dryrun] cap_capit_orders: {len(capped)} điều chỉnh, "
          f"còn {len(plan.orders)} order sau cap")
    assert len(plan.orders) == 6, (
        f"cap_capit vẫn đang loại bớt order -> chỉ còn {len(plan.orders)}. "
        f"Artifact golive_v23_status.json chưa được Taylor fix xong? "
        f"capped={capped}")
    print("[dryrun] ✓ cả 6 order qua cap_capit (artifact CAPIT đã fix) — "
          "đây chính là tình huống resume+reconcile")

    with tempfile.TemporaryDirectory() as tmp:
        # sao chép state production THẬT (state cũ 1 parent) vào tmp — không mutate bản gốc
        tag = f"{plan.account}_{plan.plan_date}"
        shutil.copy(PROD_STATE, os.path.join(tmp, f"exec_{tag}_state.json"))
        with open(PROD_STATE, encoding="utf-8") as f:
            before_parents = set(json.load(f)["parents"].keys())
        print(f"[dryrun] state production SAO CHÉP: parents cũ = {sorted(before_parents)}")

        orig = ex_mod.EXEC_DIR
        ex_mod.EXEC_DIR = tmp
        try:
            # cfg tối thiểu như account (gap flag off -> không đọc parquet); KHÔNG connect broker
            e = Executor(plan, object(), {"mode": "live"})
            e.seed_shared()   # <-- hàm đã crash trong incident; KHÔNG place lệnh
        finally:
            ex_mod.EXEC_DIR = orig

        parents = e.state["parents"]
        assert set(parents) == {o.id for o in plan.orders}, \
            f"parents sau resume không khớp plan: {sorted(parents)}"
        sp = parents["SELL-VPB-01"]
        assert sp["done"] is True and sp["filled"] == 800, \
            f"SELL-VPB-01 bị thay đổi: {sp}"
        for oid in ["BUY-NCT-02", "BUY-PVT-03", "BUY-SAB-04", "BUY-SIP-05", "BUY-VNM-06"]:
            p = parents[oid]
            assert p["filled"] == 0 and p["done"] is False, f"{oid} backfill sai: {p}"

        # state PRODUCTION gốc bất biến (dry-run không được ghi đè)
        with open(PROD_STATE, encoding="utf-8") as f:
            after_parents = set(json.load(f)["parents"].keys())
        assert after_parents == before_parents == {"SELL-VPB-01"}, \
            "FAIL: dry-run đã sửa state production!"

    print("[dryrun] ✓ executor init OK, seed_shared() không KeyError")
    print("[dryrun] ✓ SELL-VPB-01 giữ nguyên done=True/filled=800 (sẽ KHÔNG re-place)")
    print("[dryrun] ✓ 5 CAPIT parent sạch, sẵn sàng cho phiên 13:00")
    print("[dryrun] ✓ state production gốc KHÔNG bị chạm")
    print("\n[dryrun] PASS ✅ — 0 lệnh đặt, executor khởi tạo & reconcile đúng")


if __name__ == "__main__":
    main()
