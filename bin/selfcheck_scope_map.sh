#!/usr/bin/env bash
# selfcheck_scope_map.sh [module]
#
# In ra BẢN ĐỒ NGƯỢC "module `trading_bot` nào <- những selfcheck nào phụ thuộc vào nó", quét
# thật từ import của mọi `*selfcheck*.py` ở gốc WorkingClaude.
#
# DÙNG KHI NÀO: trước khi chạy selfcheck sau một lần sửa code — kb/coding_guidelines.md §23
# ("Chạy Selfcheck THEO PHẠM VI Cái Vừa Sửa"). Sửa một module lõi dùng chung (plan.py,
# config.py, executor.py, brokers.py, plan_funding_gate.py) thì phải quét rộng; sửa module
# rìa thì chạy đúng 1-6 file mà lệnh này chỉ ra.
#
# WHY LÀ SCRIPT, KHÔNG PHẢI BẢNG CHÉP TAY: một bảng phụ thuộc chép vào tài liệu sẽ MỐC ngay lần
# thêm selfcheck kế tiếp mà không ai biết; lệnh thì luôn đọc trạng thái thật của repo. §23 giữ
# bảng số liệu chỉ như MỐC THAM CHIẾU đo tại 2026-08-08, còn nguồn chuẩn tắc là script này.
# (Trước 2026-08-08 logic này nằm inline trong §23 dưới dạng snippet Python — cùng logic, chỉ
# đổi chỗ ở, để gọi được bằng TÊN từ dispatch prompt/skill/hook thay vì copy-paste.)
#
# Tham số tuỳ chọn: tên module cần lọc, chấp nhận cả 2 dạng viết —
#   bin/selfcheck_scope_map.sh trading_bot/plan.py
#   bin/selfcheck_scope_map.sh trading_bot.plan
# Không tham số = in toàn bộ bản đồ.
set -euo pipefail

WC_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FILTER="${1:-}"

cd "$WC_ROOT"
python3 - "$FILTER" <<'PY'
import re, glob, collections, sys

filt = sys.argv[1] if len(sys.argv) > 1 else ""
# Chuẩn hoá: chấp nhận "trading_bot/plan.py" lẫn "trading_bot.plan"
if filt:
    filt = filt.strip().removesuffix(".py").replace("/", ".").strip(".")

m = collections.defaultdict(set)
for f in sorted(glob.glob("*selfcheck*.py")):
    src = open(f, encoding="utf-8", errors="replace").read()
    for a, b in re.findall(r'from\s+(trading_bot[\w.]*)\s+import|import\s+(trading_bot[\w.]*)', src):
        m[a or b].add(f)

keys = sorted(m)
if filt:
    keys = [k for k in keys if k == filt]
    if not keys:
        print(f"(không selfcheck nào import '{filt}' — kiểm tra lại tên module, hoặc chạy không tham số để xem toàn bộ bản đồ)")
        sys.exit(0)

for k in keys:
    print(f"{k:38s} <- {', '.join(sorted(m[k]))}")
PY
