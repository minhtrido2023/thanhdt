#!/usr/bin/env bash
# dispatch_tiny_prompt_selfcheck.sh — guard "prompt rỗng/quá ngắn" của bin/dispatch.sh.
#
# Sự cố gốc 2026-08-20T16:22Z (job Wags_20260820_162234): một dispatch chỉ có nội dung "x"
# chạy hết một phiên headless; agent (đúng) từ chối đoán việc và post question "dispatch-rong"
# — câu hỏi KHÔNG có nội dung nào để user quyết nhưng vẫn nằm trong backlog 48h của
# ops_health_check #5 và làm wags_autofix dispatch lặp.
#
# Mọi ca ở đây đều KHÔNG có side-effect: hoặc dừng ở guard, hoặc dừng ở check "agent not
# found" NGAY SAU guard — không ca nào tạo job record hay chạy CLI thật.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
D="$ROOT/bin/dispatch.sh"
pass=0; fail=0
ck() {  # ck <mô tả> <chuỗi mong đợi trong stderr> <env> <prompt>
  local desc="$1" want="$2" env="$3" prompt="$4" out
  out="$(env $env "$D" NoSuchAgentXYZ "$prompt" 2>&1 </dev/null | head -3)"
  if printf '%s' "$out" | grep -qF "$want"; then
    echo "  PASS  $desc"; pass=$((pass+1))
  else
    echo "  FAIL  $desc — mong '$want', nhận: $out"; fail=$((fail+1))
  fi
}

BLOCKED="dispatch bị HUỶ — prompt rỗng/quá ngắn"
PASSED_GUARD="not found"   # tới được check agent ⇒ đã QUA guard

echo "== chặn đúng"
ck "prompt 'x' (1 ký tự) bị chặn"            "$BLOCKED"      "" "x"
ck "prompt toàn whitespace bị chặn"          "$BLOCKED"      "" "   "
ck "prompt 7 ký tự (dưới ngưỡng) bị chặn"    "$BLOCKED"      "" "abcdefg"

echo "== KHÔNG chặn nhầm"
# "ping test" = prompt NGẮN NHẤT từng dispatch thật trong 1.781 job record (9 ký tự, trim → 8).
ck "'ping test' (ngắn nhất lịch sử) qua guard" "$PASSED_GUARD" "" "ping test"
ck "prompt dài bình thường qua guard"          "$PASSED_GUARD" "" "kiểm tra job board rồi báo lại"
ck "escape hatch MIKE_ALLOW_TINY_PROMPT=1"     "$PASSED_GUARD" "MIKE_ALLOW_TINY_PROMPT=1" "x"

echo
if [ "$fail" -eq 0 ]; then echo "PASS — $pass/$pass assertion đúng"; exit 0; fi
echo "FAIL — $fail/$((pass+fail)) assertion sai"; exit 1
