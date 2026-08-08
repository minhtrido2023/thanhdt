#!/usr/bin/env bash
# test_naming_gate.sh <file.py> [file2.py ...]
#
# Pre-commit gate — CHẶN CỨNG một file MỚI đặt tên `test_*.py` / `*_test.py` ở GỐC
# WorkingClaude/ mà thực chất KHÔNG phải test (không có hàm `def test_` nào).
#
# WHY (vấn đề thật, đo được, không phải quy ước cho vui):
# Kiểm kê 2026-08-08 (mike/agents/Taylor/research/test_suite_inventory_20260808.md, job
# Taylor_20260808_035850) tìm ra 165 file khớp `test_*.py`/`*_test.py` ở gốc WorkingClaude
# (đếm trên đĩa; git index còn 167 đường dẫn vì 2 file đã bị xoá khỏi đĩa), và **0 file nào có
# `def test_`** — TẤT CẢ đều là script backtest/R&D đặt tên theo thói quen
# lịch sử. Hậu quả không phải thẩm mỹ: `pytest` gom nhầm chúng, ai đó "chạy bộ test" thì chạy
# trúng script nghiên cứu (có cái gọi BigQuery, có cái ghi file), và người mới không phân biệt
# nổi đâu là hồi quy thật đâu là artifact. kb/coding_guidelines.md §23 hệ luận 2 đã chốt quy
# ước: `test_*.py` dành riêng cho test thật; script R&D mới đặt `exp_*` / `probe_*` / `stress_*`.
# Gate này biến quy ước đó thành ĐIỀU KIỆN CƠ HỌC để commit — cùng lý do bin/shellcheck_gate.sh
# và bin/discord_id_gate.sh tồn tại: một luật chỉ sống trong văn xuôi thì phụ thuộc CON NGƯỜI
# NHỚ, và ở repo này chuyện đó đã hỏng nhiều lần.
#
# PHẠM VI CỐ Ý HẸP (curated, đừng đun sôi đại dương — cùng triết lý bin/shellcheck_gate.sh):
#   1. CHỈ file MỚI. 165 file cũ được GRANDFATHER: kiểm tra bằng `git cat-file -e HEAD:<path>`
#      chứ KHÔNG phải `git ls-files` — pre-commit đã stage file mới vào INDEX rồi, nên
#      `git ls-files` coi file mới là "đã có" và gate sẽ không bao giờ bắn. Đối chiếu HEAD là
#      cách duy nhất phân biệt "mới" với "đã tồn tại". Sửa/commit lại một file cũ KHÔNG bị chặn.
#   2. CHỈ gốc WorkingClaude/ (đúng 1 cấp, không có "/" thứ hai). Không đụng trading_bot/,
#      stockquery/, .claude/skills/... — những chỗ đó có test pytest THẬT và đúng quy ước rồi.
#      mike/ là repo lồng riêng, có .pre-commit-config.yaml của nó, không thuộc phạm vi này.
#   3. Ngoại lệ đích danh: test_trading_bot.py — bộ hồi quy THẬT nhưng chạy dạng script thuần
#      (không có `def test_`, xác nhận 2026-08-08). Giữ nguyên tên vì nó là test thật.
set -uo pipefail

EXEMPT="test_trading_bot.py"
BLOCKED=0

if [ "$#" -eq 0 ]; then
  exit 0
fi

for path in "$@"; do
  [ -f "$path" ] || continue

  # (2) chỉ gốc WorkingClaude/ — đúng một cấp
  case "$path" in
    WorkingClaude/*/*) continue ;;
    WorkingClaude/*) ;;
    *) continue ;;
  esac

  base="${path##*/}"
  case "$base" in
    test_*.py|*_test.py) ;;
    *) continue ;;
  esac

  # (3) ngoại lệ đích danh
  [ "$base" = "$EXEMPT" ] && continue

  # (1) đã có trong HEAD => file cũ, grandfathered
  if git cat-file -e "HEAD:$path" 2>/dev/null; then
    continue
  fi

  # test thật thì phải có ít nhất một `def test_`
  if grep -qE '^[[:space:]]*def test_' "$path"; then
    continue
  fi

  BLOCKED=$(( BLOCKED + 1 ))
  echo "  🔴 $path — tên kiểu test nhưng KHÔNG có hàm 'def test_' nào." >&2
done

if [ "$BLOCKED" -gt 0 ]; then
  {
    echo ""
    echo "🔴 test_naming_gate: $BLOCKED file MỚI bị chặn."
    echo ""
    echo "   Quy ước của fleet (kb/coding_guidelines.md §23, hệ luận 2): tên 'test_*.py' /"
    echo "   '*_test.py' ở gốc WorkingClaude/ DÀNH RIÊNG cho test thật (có 'def test_')."
    echo "   Script backtest/R&D/thăm dò đặt tên: exp_*.py / probe_*.py / stress_*.py"
    echo ""
    echo "   Đây là file nghiên cứu?  -> đổi tên, ví dụ:  git mv <file> exp_<mô-tả>.py"
    echo "   Đây là test thật?        -> viết ít nhất một 'def test_...()' rồi commit lại."
    echo ""
    echo "   (165 file cũ đặt sai tên được grandfather có chủ đích — gate chỉ chặn file MỚI,"
    echo "    xem mike/agents/Taylor/research/test_suite_inventory_20260808.md.)"
  } >&2
  exit 1
fi
exit 0
