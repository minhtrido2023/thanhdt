#!/usr/bin/env python3
"""Selfcheck cho fix reconcile parents on resume (incident ZaloPay 2026-07-21).

Tình huống tái hiện: state cũ chỉ có 1 parent (SELL-VPB-01, done) do cap_capit_orders()
fail-closed loại 5 lệnh CAPIT khi state tạo lần đầu; sau đó plan đầy đủ 6 order trở lại
mà created_at KHÔNG đổi -> _load_state() nhận nhánh "resume" nạp state cũ -> seed_shared()
KeyError vì 5 CAPIT không có trong state["parents"].

Verify fix: _load_state() backfill 5 parent mới sạch, GIỮ NGUYÊN SELL-VPB-01 done/filled=800,
seed_shared() không crash.

Chạy: python3 mike/agents/Mafee/reconcile_parents_selfcheck.py
"""
import json
import os
import sys
import tempfile

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

from trading_bot import executor as ex_mod
from trading_bot.executor import Executor
from trading_bot.plan import load_plan


def main():
    plan = load_plan("2026-07-21", "ZaloPay")
    assert plan is not None, "không đọc được plan ZaloPay 2026-07-21"
    order_ids = [o.id for o in plan.orders]
    print(f"[selfcheck] plan orders ({len(order_ids)}): {order_ids}")
    assert len(order_ids) == 6, f"expect 6 order, got {len(order_ids)}"
    sell_id = order_ids[0]
    assert sell_id == "SELL-VPB-01", f"order đầu phải là SELL-VPB-01, got {sell_id}"
    capit_ids = order_ids[1:]

    # state cũ: CHỈ có SELL-VPB-01 (done), plan_created_at khớp plan.created_at (đều "")
    stale_state = {
        "plan_date": plan.plan_date,
        "plan_created_at": plan.created_at,
        "px_hist": {"VPB": [["2026-07-21T09:15:15", 24800.0]]},
        "exchange_override": {},
        "parents": {
            sell_id: {
                "filled": 800, "done": True, "atc_sent": False,
                "children": [{"oid": "39541", "qty": 800, "price": 24800,
                              "filled": 800, "status": "closed",
                              "ts": "2026-07-21T09:15:15", "released": True}],
                "last_slice_ts": "2026-07-21T09:15:15", "dcf_check": None,
            }
        },
        "_ghost_warned": {},
    }

    with tempfile.TemporaryDirectory() as tmp:
        # redirect EXEC_DIR sang tmp để KHÔNG chạm file production
        orig_exec_dir = ex_mod.EXEC_DIR
        ex_mod.EXEC_DIR = tmp
        try:
            tag = f"{plan.account}_{plan.plan_date}"
            fixture = os.path.join(tmp, f"exec_{tag}_state.json")
            with open(fixture, "w", encoding="utf-8") as f:
                json.dump(stale_state, f, ensure_ascii=False, indent=2)

            # cfg tối thiểu: mọi gap/extreme flag off -> _load_gap_ref_data return sớm.
            # broker dummy: __init__ chỉ lưu, không gọi method.
            e = Executor(plan, object(), {})

            parents = e.state["parents"]
            # (1) đủ 6 parent
            for oid in order_ids:
                assert oid in parents, f"FAIL: {oid} không được backfill vào parents"
            print(f"[selfcheck] ✓ đủ {len(parents)} parent sau resume")

            # (2) SELL-VPB-01 GIỮ NGUYÊN 100%
            sp = parents[sell_id]
            assert sp["done"] is True, "FAIL: SELL-VPB-01 done bị đổi"
            assert sp["filled"] == 800, f"FAIL: SELL-VPB-01 filled đổi -> {sp['filled']}"
            assert len(sp["children"]) == 1 and sp["children"][0]["oid"] == "39541", \
                "FAIL: SELL-VPB-01 children bị mất/đổi"
            print("[selfcheck] ✓ SELL-VPB-01 nguyên vẹn (done=True, filled=800, child 39541)")

            # (3) 5 CAPIT backfill sạch
            for oid in capit_ids:
                p = parents[oid]
                assert p["filled"] == 0 and p["done"] is False and p["children"] == [] \
                    and p["atc_sent"] is False and p["last_slice_ts"] is None, \
                    f"FAIL: {oid} backfill không đúng fresh-state: {p}"
            print(f"[selfcheck] ✓ 5 CAPIT backfill sạch (filled=0, done=False, children=[]): {capit_ids}")

            # (4) seed_shared() KHÔNG crash (đây là hàm đã KeyError trong incident)
            e.shared = {}
            e.seed_shared()
            # child SELL-VPB-01 status="closed" (đã khớp) -> seed_shared cộng filled=800 vào
            # shared["VPB"] (đúng bất biến: KL đã khớp). CAPIT chưa có child -> không cộng.
            assert e.shared == {"VPB": 800}, \
                f"FAIL: seed_shared reservation không đúng: {e.shared} (kỳ vọng VPB=800)"
            print(f"[selfcheck] ✓ seed_shared() chạy không KeyError; shared={e.shared}")

        finally:
            ex_mod.EXEC_DIR = orig_exec_dir

    print("\n[selfcheck] TẤT CẢ PASS ✅  (reconcile parents on resume — incident ZaloPay 2026-07-21)")


if __name__ == "__main__":
    main()
