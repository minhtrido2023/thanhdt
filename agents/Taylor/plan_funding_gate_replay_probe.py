#!/usr/bin/env python3
"""Replay `check_plan_funding` trên TOÀN BỘ plan THẬT trong `data/trade_plans/`.

Không phải selfcheck (đó là `plan_funding_gate_selfcheck.py` với broker stub tối thiểu) —
đây là test TÍCH HỢP: `load_plan()` thật, `PlannedOrder` thật, dữ liệu plan thật, để bắt
lỗi kiểu "gate đọc field không tồn tại" mà stub không lộ ra.

Hai kịch bản (vế phải = pp0Buy + tín dụng JIT, xem `ScaledBroker` — cập nhật 2026-08-07):
  (1) TỔNG NGUỒN = ĐÚNG BẰNG Σ lệnh mua (biên `≤`) → KHÔNG plan nào được bị CHẶN
  (2) TỔNG NGUỒN = 1/2 Σ lệnh mua                  → phải CHẶN, TRỪ plan tự cấp vốn hoàn toàn
      (tín dụng JIT ≥ nhu cầu — hạ pp0Buy không chạm tới được nguồn đó)
Phán quyết bằng ORACLE ĐỘC LẬP tính lại từ định nghĩa "tổng nguồn < nhu cầu ⇒ CHẶN", không
hardcode số lượng kỳ vọng.

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
from trading_bot.plan_funding_gate import (                              # noqa: E402
    check_plan_funding, FEE_RATE, _jit_sell_credit)


class ScaledBroker:
    """pp0Buy sao cho TỔNG NGUỒN (pp0Buy + tín dụng JIT) = `mult` × Σ lệnh mua — bất kể gói vay.

    Từ 2026-08-07 vế phải của gate = pp0Buy + tín dụng JIT (tiền lệnh BÁN cùng plan chạy trước).
    Nếu vẫn đặt pp0Buy = mult × need như bản cũ thì kịch bản (2) không còn nghĩa "thiếu 1/2
    tiền": plan tự cấp vốn có tổng nguồn tới 1,5× nhu cầu nên KHÔNG chặn là ĐÚNG, không phải
    lỗi. Trừ tín dụng ra khỏi pp0Buy giữ nguyên Ý ĐỊNH gốc của cả hai kịch bản dưới công thức mới.
    """

    def __init__(self, plan, mult):
        need = sum(o.qty * o.ref_price * (1 + FEE_RATE) for o in plan.orders
                   if str(o.side or "").lower() == "buy")
        buys = [o for o in plan.orders if str(o.side or "").lower() == "buy"]
        credit = _jit_sell_credit(plan, buys)[0] if buys else 0.0
        # sàn 1,0đ: pp0Buy ≤ 0 rơi sang nhánh (3) cận-ngoài (đường code KHÁC), không còn đo
        # được nhánh (1) — mà nhánh (1) mới là thứ kịch bản này muốn kiểm.
        self.bp = max(need * mult - credit, 1.0)
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
    mismatches = []
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
            b = ScaledBroker(p, mult)
            v = check_plan_funding(p, b, "live")
            tally[mult][v["action"]] = tally[mult].get(v["action"], 0) + 1
            # ORACLE ĐỘC LẬP: tính lại kỳ vọng từ ĐỊNH NGHĨA (tổng nguồn < nhu cầu ⇒ phải CHẶN),
            # không chép lại phép tính bên trong gate. `mult=1.0` ⇒ hoà đúng biên ⇒ KHÔNG chặn.
            buys_l = [o for o in p.orders if str(o.side or "").lower() == "buy"]
            need = sum(o.qty * o.ref_price * (1 + FEE_RATE) for o in buys_l)
            credit = _jit_sell_credit(p, buys_l)[0] if buys_l else 0.0
            want_block = has_buys and (b.bp + credit) < need - 1e-6
            if want_block and v["action"] != "BLOCK":
                mismatches.append((os.path.basename(path), mult,
                                   f"kỳ vọng BLOCK (nguồn {b.bp + credit:,.0f} < cần "
                                   f"{need:,.0f}) nhưng nhận {v['action']}"))
            if not want_block and v["action"] == "BLOCK":
                mismatches.append((os.path.basename(path), mult,
                                   f"CHẶN OAN (nguồn {b.bp + credit:,.0f} ≥ cần {need:,.0f}) "
                                   f"— {v['reason'][:100]}"))

    print(f"\nplan load được: {n_loaded} "
          f"(có lệnh MUA: {n_with_buys})")
    print(f"[1] sức mua == Σ mua (biên) : {tally[1.0]}")
    print(f"[2] sức mua == 1/2 Σ mua    : {tally[0.5]}")
    if unloadable:
        print(f"\n{len(unloadable)} file KHÔNG load được (lỗi có sẵn của load_plan, không "
              f"liên quan gate):")
        for name, err in unloadable:
            print(f"  - {name}: {err}")

    if mismatches:
        print(f"\n❌ {len(mismatches)} plan LỆCH so với oracle độc lập:")
        for name, mult, why in mismatches:
            print(f"  - [{mult}] {name}: {why}")
    # Tiêu chí = ORACLE (0 lệch) + biên `≤` không chặn oan plan nào.
    # KHÔNG còn khẳng định "mult=0,5 ⇒ CHẶN HẾT n_with_buys": plan TỰ CẤP VỐN (tín dụng JIT ≥
    # nhu cầu) thì hạ pp0Buy bao nhiêu cũng không chặn được, vì nguồn không đến từ pp0Buy. Đó là
    # tính chất ĐÚNG của công thức mới, không phải lỗi — nên để oracle phán, không hardcode số.
    ok = (not mismatches
          and tally[1.0].get("BLOCK", 0) == 0
          and tally[1.0].get("OK", 0) == n_with_buys)
    shutil.rmtree(tmp, ignore_errors=True)
    print("\n" + ("✅ REPLAY PASS" if ok else "❌ REPLAY FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
