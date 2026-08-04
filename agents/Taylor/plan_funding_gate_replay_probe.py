#!/usr/bin/env python3
"""Replay `check_plan_funding` trên TOÀN BỘ plan THẬT trong `data/trade_plans/`.

Không phải selfcheck (đó là `plan_funding_gate_selfcheck.py` với broker stub tối thiểu) —
đây là test TÍCH HỢP: `load_plan()` thật, `PlannedOrder` thật, dữ liệu plan thật, để bắt
lỗi kiểu "gate đọc field không tồn tại" mà stub không lộ ra.

Hai kịch bản:
  (1) sức mua = ĐÚNG BẰNG Σ lệnh mua (biên `≤`)  → KHÔNG plan nào được bị CHẶN
  (2) sức mua = 1/2 Σ lệnh mua                    → MỌI plan có lệnh mua phải bị CHẶN

READ-ONLY: không mạng, không broker thật, không ghi file nào.
"""
import os
import sys
import glob
import shutil
import tempfile
import types

ROOT = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, ROOT)

import trading_bot.plan as plan_mod                          # noqa: E402
from trading_bot.plan import load_plan                       # noqa: E402
from trading_bot.plan_funding_gate import check_plan_funding, FEE_RATE   # noqa: E402


class ScaledBroker:
    """pp0Buy = `mult` × Σ giá trị lệnh mua (đã gồm phí) của CHÍNH plan này — bất kể gói vay."""

    def __init__(self, plan, mult):
        need = sum(o.qty * o.ref_price * (1 + FEE_RATE) for o in plan.orders
                   if str(o.side or "").lower() == "buy")
        self.bp = need * mult
        self.cash = 0.0
        self.client = types.SimpleNamespace(loan_package_id=None)

    def get_buying_power(self, symbol, price, loan_package_id=None):
        return self.bp

    def get_cash(self):
        return self.cash


def main():
    files = sorted(glob.glob(os.path.join(ROOT, "data", "trade_plans", "*.json")))
    print(f"{len(files)} file plan trong data/trade_plans/")
    tally = {1.0: {}, 0.5: {}}
    unloadable = []
    n_with_buys = 0
    n_loaded = 0
    # `load_plan(plan_date, account)` dựng đường dẫn từ (account, date), nên file có tên
    # không chuẩn (`..._v2`, `..._superseded_*`, `park_trim_*`) sẽ nằm ngoài tầm với nếu chỉ
    # tách tên. Chép SANG tmpdir dưới tên chuẩn rồi trỏ PLAN_DIR vào đó ⇒ MỌI file đều đi qua
    # ĐÚNG bộ parse thật của production, không viết lại logic đọc plan (nguồn phân kỳ).
    tmp = tempfile.mkdtemp(prefix="fundgate_replay_")
    plan_mod.PLAN_DIR = tmp
    for idx, path in enumerate(files):
        acct = f"probe{idx:03d}"
        shutil.copyfile(path, os.path.join(tmp, f"plan_{acct}_2000-01-01.json"))
        try:
            p = load_plan("2000-01-01", account=acct)
        except Exception as e:
            unloadable.append((os.path.basename(path), f"{type(e).__name__}: {e}"))
            continue
        if p is None:
            unloadable.append((os.path.basename(path), "load_plan trả None"))
            continue
        n_loaded += 1
        has_buys = any(str(o.side or "").lower() == "buy" for o in p.orders)
        n_with_buys += bool(has_buys)
        for mult in (1.0, 0.5):
            v = check_plan_funding(p, ScaledBroker(p, mult), "live")
            tally[mult][v["action"]] = tally[mult].get(v["action"], 0) + 1
            if mult == 1.0 and v["action"] == "BLOCK":
                print(f"  ⚠ CHẶN OAN ở biên: {os.path.basename(path)} — {v['reason'][:120]}")
            if mult == 0.5 and has_buys and v["action"] != "BLOCK":
                print(f"  ⚠ KHÔNG chặn khi thiếu 1/2 tiền: {os.path.basename(path)} "
                      f"— {v['action']}")

    print(f"\nplan load được: {n_loaded} "
          f"(có lệnh MUA: {n_with_buys})")
    print(f"[1] sức mua == Σ mua (biên) : {tally[1.0]}")
    print(f"[2] sức mua == 1/2 Σ mua    : {tally[0.5]}")
    if unloadable:
        print(f"\n{len(unloadable)} file KHÔNG load được (lỗi có sẵn của load_plan, không "
              f"liên quan gate):")
        for name, err in unloadable:
            print(f"  - {name}: {err}")

    ok = (tally[1.0].get("BLOCK", 0) == 0
          and tally[0.5].get("BLOCK", 0) == n_with_buys
          and tally[1.0].get("OK", 0) == n_with_buys)
    shutil.rmtree(tmp, ignore_errors=True)
    print("\n" + ("✅ REPLAY PASS" if ok else "❌ REPLAY FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
