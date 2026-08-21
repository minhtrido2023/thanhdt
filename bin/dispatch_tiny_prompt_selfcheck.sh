#!/usr/bin/env bash
# dispatch_tiny_prompt_selfcheck.sh — guard "prompt rỗng/quá ngắn" của bin/dispatch.sh.
#
# Sự cố gốc 2026-08-20T16:22Z (job Wags_20260820_162234): một dispatch chỉ có nội dung "x"
# chạy hết một phiên headless; agent (đúng) từ chối đoán việc và post question "dispatch-rong"
# — câu hỏi KHÔNG có nội dung nào để user quyết nhưng vẫn nằm trong backlog 48h của
# ops_health_check #5 và làm wags_autofix dispatch lặp.
#
# CHẠY DƯỚI CẢ HAI LOCALE là điểm chính, không phải trang trí: `${#var}` của bash đếm BYTE
# dưới LANG=C và đếm KÝ TỰ dưới C.UTF-8, nên bản đầu tiên của guard chặn "Rà lại KQ" ở
# locale này mà cho qua ở locale kia (arch-reviewer F2). Bộ assertion toàn ASCII sẽ PASS 6/6
# dưới cả hai locale dù hành vi khác nhau ⇒ các ca tiếng Việt 5-7 ký tự dưới đây là thứ DUY
# NHẤT phát hiện được phân kỳ đó.
#
# Mọi ca đều KHÔNG có side-effect: hoặc dừng ở guard, hoặc dừng ở check "agent not found"
# NGAY SAU guard — không ca nào tạo job record hay chạy CLI thật.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
D="$ROOT/bin/dispatch.sh"
# TỰ CÁCH LY: mỗi lượt chạy sinh ~10 reject. Ghi thẳng vào logs/dispatch_rejected_prompts.log
# thì check 10b (cửa sổ 24h) WARN bằng chính rác của test này mỗi ngày có ai chạy bộ selfcheck
# — cảnh báo THẬT chìm mất (đo thật 2026-08-21: 56/56 dòng trong file là do selfcheck sinh ra).
# Ghi đè bằng MIKE_DISPATCH_REJECT_LOG; đường dẫn MẶC ĐỊNH vẫn được kiểm riêng ở cuối file
# bằng một bản sao dispatch.sh trong thư mục tạm (chạy THẬT, không phải chỉ grep).
TMPD="$(mktemp -d)"; trap 'rm -rf "$TMPD"' EXIT
export MIKE_DISPATCH_REJECT_LOG="$TMPD/reject.log"
REJLOG="$MIKE_DISPATCH_REJECT_LOG"
PRODLOG="$ROOT/logs/dispatch_rejected_prompts.log"
PRODLINES_BEFORE="$( [ -f "$PRODLOG" ] && wc -l < "$PRODLOG" || echo 0 )"
pass=0; fail=0

ck() {  # ck <mô tả> <chuỗi mong đợi trong stderr> <env> <prompt>
  local desc="$1" want="$2" env="$3" prompt="$4" out
  out="$(env MIKE_DISPATCH_REJECT_LOG="$REJLOG" $env "$D" NoSuchAgentXYZ "$prompt" 2>&1 </dev/null | head -6)"
  if printf '%s' "$out" | grep -qF "$want"; then
    echo "  PASS  $desc"; pass=$((pass+1))
  else
    echo "  FAIL  $desc — mong '$want', nhận: $out"; fail=$((fail+1))
  fi
}
assert() {  # assert <mô tả> <điều kiện đã eval sẵn: 0/1>
  if [ "$2" = "0" ]; then echo "  PASS  $1"; pass=$((pass+1));
  else echo "  FAIL  $1"; fail=$((fail+1)); fi
}

BLOCKED="dispatch bị HUỶ — prompt rỗng/quá ngắn"
PASSED_GUARD="not found"   # tới được check agent ⇒ đã QUA guard

for L in C C.UTF-8; do
  echo "== LC_ALL=$L — chặn đúng"
  ck "prompt 'x' (1 byte) bị chặn"                 "$BLOCKED"      "LC_ALL=$L" "x"
  ck "prompt toàn whitespace bị chặn"              "$BLOCKED"      "LC_ALL=$L" "   "
  ck "prompt ASCII 7 byte bị chặn"                 "$BLOCKED"      "LC_ALL=$L" "abcdefg"

  echo "== LC_ALL=$L — KHÔNG chặn nhầm"
  # "ping test" = prompt NGẮN NHẤT từng dispatch thật trong 1.781 job record (trim → 8 byte).
  ck "'ping test' (ngắn nhất lịch sử) qua guard"   "$PASSED_GUARD" "LC_ALL=$L" "ping test"
  ck "prompt dài bình thường qua guard"            "$PASSED_GUARD" "LC_ALL=$L" "kiểm tra job board rồi báo lại"
  ck "escape hatch MIKE_ALLOW_TINY_PROMPT=1"       "$PASSED_GUARD" "LC_ALL=$L MIKE_ALLOW_TINY_PROMPT=1" "x"

  echo "== LC_ALL=$L — TIẾNG VIỆT vùng phân kỳ locale (5-7 ký tự, >8 byte)"
  # Đây là các ca mà bản guard đếm-ký-tự chặn NHẦM dưới C.UTF-8. Đếm byte ⇒ luôn qua.
  ck "'Rà lại KQ' (7 ký tự / 10 byte) qua guard"   "$PASSED_GUARD" "LC_ALL=$L" "Rà lại KQ"
  ck "'Sửa lỗi' (6 ký tự / 10 byte) qua guard"     "$PASSED_GUARD" "LC_ALL=$L" "Sửa lỗi"

  echo "== LC_ALL=$L — thông báo đếm BYTE, không đếm ký tự"
  ck "thông báo lỗi nói 'byte'"                    "byte sau khi trim" "LC_ALL=$L" "x"
done

echo "== gợi ý gõ nhầm THỨ TỰ tham số"
ck "prompt bắt đầu bằng '--' được gợi ý đảo thứ tự" "gõ nhầm THỨ TỰ tham số" "" "--bg"

echo "== dấu vết bền (reject log) — nếu người gọi là MÁY thì stderr không ai đọc"
_before="$( [ -f "$REJLOG" ] && wc -l < "$REJLOG" || echo 0 )"
env MIKE_DISPATCH_REJECT_LOG="$REJLOG" "$D" NoSuchAgentXYZ "zz" >/dev/null 2>&1 </dev/null
_after="$( [ -f "$REJLOG" ] && wc -l < "$REJLOG" || echo 0 )"
[ "$_after" -eq $((_before + 1)) ]; assert "mỗi lần reject ghi ĐÚNG 1 dòng vào logs/dispatch_rejected_prompts.log" "$?"
tail -1 "$REJLOG" | grep -qP '^\d{4}-\d{2}-\d{2}T\S+\tto=NoSuchAgentXYZ\tfrom=\S+\tbytes=2\tprompt=zz$'
assert "dòng log đủ trường ts/to/from/bytes/prompt và parse được" "$?"
grep -q "CHECK10B_BEGIN" "$ROOT/bin/ops_health_check.sh"
assert "ops_health_check có check 10b ĐỌC file log này (fail-loud phải có người đọc)" "$?"
grep -q "dispatch_rejected_prompts.log" "$ROOT/bin/ops_health_check.sh"
assert "check 10b trỏ đúng tên file" "$?"

# Ghi đè ở trên làm mọi ca trên KHÔNG còn chứng minh đường dẫn MẶC ĐỊNH đúng — một lỗi đánh
# máy trong nhánh `:-` sẽ xanh 100%. Nên chạy THẬT một bản sao dispatch.sh đặt trong ROOT giả
# (thư mục tạm), KHÔNG set biến ghi đè, rồi đòi file xuất hiện đúng ở <ROOT_giả>/logs/…
FAKE="$TMPD/fakeroot"; mkdir -p "$FAKE/bin" "$FAKE/logs"
cp "$D" "$ROOT/bin/usage_limit_phrases.sh" "$FAKE/bin/" 2>/dev/null
( unset MIKE_DISPATCH_REJECT_LOG; "$FAKE/bin/dispatch.sh" NoSuchAgentXYZ "x" ) >/dev/null 2>&1 </dev/null
[ -s "$FAKE/logs/dispatch_rejected_prompts.log" ]
assert "KHÔNG set biến ghi đè ⇒ ghi đúng <ROOT>/logs/dispatch_rejected_prompts.log (đường dẫn mặc định)" "$?"

echo "== test KHÔNG được làm bẩn log production (nếu bẩn, check 10b WARN mỗi ngày bằng rác test)"
PRODLINES_AFTER="$( [ -f "$PRODLOG" ] && wc -l < "$PRODLOG" || echo 0 )"
[ "$PRODLINES_AFTER" -eq "$PRODLINES_BEFORE" ]
assert "logs/dispatch_rejected_prompts.log không tăng dòng nào ($PRODLINES_BEFORE → $PRODLINES_AFTER)" "$?"

echo
if [ "$fail" -eq 0 ]; then echo "PASS — $pass/$pass assertion đúng"; exit 0; fi
echo "FAIL — $fail/$((pass+fail)) assertion sai"; exit 1
