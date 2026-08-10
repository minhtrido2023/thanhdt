#!/usr/bin/env python3
"""Selfcheck cho 2 bất biến lệnh thêm vào bin/preflight_check.sh ngày 2026-08-07.

Sự cố nguồn: plan_{SpaceX,ZaloPay}_2026-08-07.json (đã user duyệt 12:36) chứa CẢ lệnh gộp
`SELL-<mã>-PARK-nn` (mang `merged_from`, đã cộng phần L2) LẪN lệnh nguồn `SELL-JIT-PARK-<mã>-01`
còn sót → bán 2 lần cùng một lô. Thừa 1.200cp (SpaceX) + 400cp (ZaloPay). Không tầng nào chặn;
Wags phát hiện thủ công 15 phút trước giờ chạy 13:05.

Selfcheck này KHÔNG chép lại logic: nó TRÍCH khối python thật đang nằm trong preflight_check.sh
và chạy khối đó. Khối bị đổi tên/di chuyển ⇒ trích thất bại ⇒ FAIL to (không im lặng pass).

Chạy: python3 bin/preflight_order_invariants_selfcheck.py
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREFLIGHT = ROOT / "bin" / "preflight_check.sh"

# Cho phép trỏ sang bản HEAD cũ để đối chứng: PF_SRC=<path> python3 <selfcheck>
import os
PREFLIGHT = Path(os.environ.get("PF_SRC", PREFLIGHT))

fails = []
oks = []


def check(name, cond, detail=""):
    (oks if cond else fails).append(f"{name}: {detail}")
    print(("  ✅ " if cond else "  ❌ ") + name + (f" — {detail}" if detail else ""))


def extract_block():
    src = PREFLIGHT.read_text(encoding="utf-8")
    m = re.search(r'PLAN_INFO=\$\(python3 - "\$PLAN_FILE".*?<<\'PY\'\n(.*?)\nPY\n', src, re.S)
    if not m:
        print("❌ FATAL: không trích được khối python plan-info trong "
              f"{PREFLIGHT} — khối đã bị đổi/di chuyển, selfcheck vô hiệu.")
        sys.exit(1)
    return m.group(1)


def run_block(block, plan):
    with tempfile.TemporaryDirectory() as td:
        py = Path(td) / "block.py"
        py.write_text(block, encoding="utf-8")
        pj = Path(td) / "plan.json"
        pj.write_text(json.dumps(plan), encoding="utf-8")
        r = subprocess.run([sys.executable, str(py), str(pj)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            return f"__CRASH__ {r.stderr.strip()[-300:]}"
        return r.stdout.strip()


def plan(orders):
    """Plan tối thiểu đủ để khối chạy — chỉ orders[] là biến số của test."""
    return {"approved_by": "user (test)", "mode": "live", "state_name": "NEUTRAL",
            "state_source": "test", "nav_basis": {"account_nav": 1e9}, "orders": orders}


def merged(tk, qty, l1, l2, sellable):
    return {"id": f"SELL-{tk}-PARK-01", "side": "sell", "ticker": tk, "qty": qty,
            "merged_from": {"L1_park_trim_qty": l1, "L2_jit_unpark_qty": l2,
                            "sellable_at_calc": sellable}}


def jit(tk, qty):
    return {"id": f"SELL-JIT-PARK-{tk}-01", "side": "sell", "ticker": tk, "qty": qty,
            "play_type": "JIT_UNPARK"}


print(f"preflight_order_invariants_selfcheck — nguồn: {PREFLIGHT}")
block = extract_block()

# 1. Hình dạng SỰ CỐ THẬT 08-07 (SpaceX ACB): gộp 400 = 300 L1 + 100 L2, còn sót JIT 100.
out = run_block(block, plan([merged("ACB", 400, 300, 100, 1500), jit("ACB", 100)]))
check("#1 bắt được lệnh nguồn còn sót sau merge (hình dạng sự cố 08-07)",
      "MERGE_STALE_SRC" in out and "ACB" in out, out)

# 2. Plan ĐÃ SỬA (DollarBill 12:50): chỉ còn lệnh gộp → phải sạch.
out = run_block(block, plan([merged("ACB", 400, 300, 100, 1500),
                             {"id": "BUY-DRI-LAG-01", "side": "buy",
                              "ticker": "DRI", "qty": 3500}]))
check("#2 plan đã gộp đúng (không còn lệnh nguồn) KHÔNG báo động giả",
      "MERGE_STALE_SRC" not in out and "SELL_GT_SELLABLE" not in out, out)

# 3. Bán vượt sellable_at_calc (ca ZaloPay VHM thật: sellable 300, gửi 300+100).
out = run_block(block, plan([merged("VHM", 300, 200, 100, 300), jit("VHM", 100)]))
check("#3 bắt được tổng bán > sellable_at_calc", "SELL_GT_SELLABLE" in out
      and "VHM(400>300)" in out, out)

# 4. Bán ĐÚNG bằng sellable (biên) — không được báo động.
out = run_block(block, plan([merged("VHM", 300, 300, 0, 300)]))
check("#4 bán đúng bằng sellable (biên =) không báo động giả",
      "SELL_GT_SELLABLE" not in out, out)

# 5. Trùng (side,ticker) nhưng KHÔNG có lệnh gộp nào → không phải chữ ký sự cố này,
#    không được fail (chia nhỏ lệnh là hợp lệ).
out = run_block(block, plan([{"id": "A", "side": "sell", "ticker": "MBB", "qty": 500},
                             {"id": "B", "side": "sell", "ticker": "MBB", "qty": 400}]))
check("#5 chia nhỏ lệnh (không có merged_from) KHÔNG bị fail oan",
      "MERGE_STALE_SRC" not in out, out)

# 6. Plan HOLD 0 lệnh — khối vẫn chạy được, không crash, không cờ lệnh.
out = run_block(block, plan([]))
check("#6 plan 0 lệnh: không crash, không cờ bất biến lệnh",
      not out.startswith("__CRASH__") and "MERGE_STALE_SRC" not in out
      and "SELL_GT_SELLABLE" not in out, out)

# 7. Thiếu qty/quantity (schema plan cũ) — không được crash preflight.
out = run_block(block, plan([{"id": "X", "side": "sell", "ticker": "ACB"},
                             merged("ACB", 400, 300, 100, 1500)]))
check("#7 lệnh thiếu qty không làm crash khối plan-info",
      not out.startswith("__CRASH__"), out)

# 8. Nhiều mã cùng lỗi → liệt kê đủ, không chỉ mã đầu.
out = run_block(block, plan([merged("ACB", 400, 300, 100, 1500), jit("ACB", 100),
                             merged("MBB", 900, 700, 200, 2400), jit("MBB", 200)]))
check("#8 liệt kê ĐỦ các mã bị trùng (ACB+MBB)",
      "ACB" in out and "MBB" in out and "MERGE_STALE_SRC" in out, out)

# 9. Cờ mới KHÔNG được phá format 8 trường phân tách '|' mà preflight_check.sh đọc lại.
out = run_block(block, plan([merged("ACB", 400, 300, 100, 1500), jit("ACB", 100)]))
check("#9 dòng kết quả vẫn có ≥8 trường '|' (IFS read của caller còn đọc đúng)",
      len(out.split("|")) >= 8, f"{len(out.split('|'))} trường")

# ── #10-#12: thu hẹp nhánh (a) sau khi mike/bin/merge_park_orders.py lên pipeline ────────
# (job Taylor_20260810_185646). #10 và #11 là CẶP VI SAI: hai plan chỉ khác nhau ở ĐÚNG một
# thuộc tính của lệnh thứ hai (`play_type`/`book`). #10 phải im, #11 phải kêu — nếu bộ phân
# biệt hỏng theo bất kỳ hướng nào thì đúng một trong hai đỏ, không thể xanh cả hai.


def pm(tk, qty, l1, l2, sellable):
    """Lệnh do merge_park_orders.py sinh ra — mang cả `merge_owner` lẫn `merged_from`."""
    o = merged(tk, qty, l1, l2, sellable)
    o.update({"id": f"PARKMERGE-SELL-{tk}", "merge_owner": "park_merge_v1",
              "book": "PARK", "play_type": "PARK_TRIM+JIT_UNPARK"})
    return o


def foreign_sell(tk, qty):
    """Lệnh bán của writer KHÁC, ngoài miền merge (book khác) — merge cố ý giữ lại (I5)."""
    return {"id": f"SELL-LAG-{tk}-01", "side": "sell", "ticker": tk, "qty": qty,
            "book": "LAG", "play_type": "LAG_EXIT"}


out = run_block(block, plan([pm("VHM", 300, 200, 100, 2000), foreign_sell("VHM", 500)]))
check("#10 lệnh merge + lệnh bán NGOÀI miền cùng mã KHÔNG còn báo động giả (ca S3)",
      "MERGE_STALE_SRC" not in out, out)

out = run_block(block, plan([pm("VHM", 300, 200, 100, 2000), jit("VHM", 100)]))
check("#11 lệnh merge + lệnh nguồn PARK/JIT còn sót VẪN bị bắt (độ phủ 08-07 giữ nguyên)",
      "MERGE_STALE_SRC" in out and "VHM" in out, out)

# Nhánh (b) không đổi: trần tiền vẫn chặn lệnh do merge sinh ra. Không có ca này thì #10
# đọc thành "đã tắt lưới an toàn cho lệnh merge" — nó chỉ tắt heuristic cấu trúc.
out = run_block(block, plan([pm("VHM", 400, 300, 100, 300), foreign_sell("VHM", 100)]))
check("#12 SELL_GT_SELLABLE VẪN chặn lệnh merge vượt trần (nhánh (b) không bị thu hẹp)",
      "SELL_GT_SELLABLE" in out and "VHM(500>300)" in out, out)

print()
if fails:
    print(f"❌ FAIL {len(fails)}/{len(fails)+len(oks)}")
    for f in fails:
        print("   -", f)
    sys.exit(1)
print(f"✅ PASS {len(oks)}/{len(oks)}")
