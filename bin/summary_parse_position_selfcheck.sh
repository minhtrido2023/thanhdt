#!/usr/bin/env bash
# summary_parse_position_selfcheck.sh — canh hồi quy lớp lỗi "parse dòng tóm tắt theo VỊ TRÍ".
#
# Bối cảnh (retro 2026-08-26, coord-2026-08-27): script Python in dòng tóm tắt rồi gọi subprocess
# KẾ THỪA stdout. stdout của con không đi qua buffer của Python, nên khi chạy dưới $(...) dòng của
# con có thể in TRƯỚC dòng tóm tắt ⇒ caller bash dùng `head -1` bắt nhầm dòng, im lặng báo 0.
# Vá phía sản xuất (sys.stdout.flush()) phụ thuộc kỷ luật của tác giả tương lai; vá phía TIÊU THỤ
# (neo theo tiền tố duy nhất của dòng tóm tắt) diệt cả lớp lỗi. Selfcheck này canh phía tiêu thụ —
# chính Wags đã chứng minh repro trên dữ liệu thật KHÔNG bắn được (84 job > buffer 8KB nên Python
# tự xả sớm), nên nếu không có test tổng hợp thì xoá nhầm bản vá là hồi quy VÔ HÌNH.
#
# Kiểu extract-and-test: lấy ĐÚNG biểu thức parse từ file thật rồi eval trên input tổng hợp —
# không chép lại biểu thức vào đây (chép lại thì test xanh trong khi file thật đã hỏng).
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAIL=0
ok()   { echo "  ✅ $1"; }
bad()  { echo "  ❌ $1"; FAIL=1; }

# Trích khối gán nhiều dòng: từ dòng bắt đầu bằng <VAR>= tới dòng đóng bằng )"
extract_assign() {  # $1=file  $2=tên biến
  awk -v v="$2" '
    $0 ~ "^"v"=" { inb=1 }
    inb { print }
    inb && /\)"[[:space:]]*$/ { exit }
  ' "$1"
}

echo "== 1. cron_health_check_daily.sh :: BAD_COUNT — dòng tóm tắt KHÔNG ở vị trí đầu"
EXPR="$(extract_assign "$ROOT/bin/cron_health_check_daily.sh" BAD_COUNT)"
[ -n "$EXPR" ] || bad "không trích được biểu thức BAD_COUNT (file đã đổi cấu trúc?)"
# Input tổng hợp: dòng của subprocess in TRƯỚC — đúng thứ tự khi Python không flush.
OUT='[append_event] wrote event 0 cần chú ý decoy
cron_health_check — 84 job có log target, 19 cần chú ý

=== STALE (19) ===' 
eval "$EXPR"
[ "${BAD_COUNT:-}" = "19" ] && ok "lấy đúng 19 dù dòng con in trước" \
                            || bad "BAD_COUNT='${BAD_COUNT:-}' — mong đợi 19"

echo "== 2. cron_health_check_daily.sh :: BAD_COUNT — thứ tự bình thường vẫn đúng"
OUT='cron_health_check — 84 job có log target, 0 cần chú ý

=== OK (84) ==='
eval "$EXPR"
[ "${BAD_COUNT:-}" = "0" ] && ok "trường hợp sạch ra 0" || bad "BAD_COUNT='${BAD_COUNT:-}' — mong đợi 0"

echo "== 3. cron_health_check_daily.sh :: không có dòng tóm tắt ⇒ fallback 0, không rỗng"
OUT='Traceback (most recent call last):'
eval "$EXPR"
[ "${BAD_COUNT:-}" = "0" ] && ok "fallback 0 khi output hỏng" || bad "BAD_COUNT='${BAD_COUNT:-}' — mong đợi 0"

echo "== 4. daily_retro.sh :: _time_claim_count — chuỗi notify chứa số MỒI"
EXPR2="$(extract_assign "$ROOT/bin/daily_retro.sh" _time_claim_count)"
[ -n "$EXPR2" ] || bad "không trích được biểu thức _time_claim_count"
# Cả dòng con lẫn chuỗi notify của chính script đều chứa "N mismatch" — chỉ tiền tố mới phân biệt.
_time_claim_out='⏱️ time_claim_audit: 7 mismatch(es) trong 1 ngày qua. Ví dụ: ...
time_claim_audit: scanned last 1 day(s), 2 mismatch(es) found
{"job":"x"}'
eval "$EXPR2"
[ "${_time_claim_count:-}" = "2" ] && ok "lấy 2 (dòng tóm tắt), không phải 7 (chuỗi notify)" \
                                   || bad "_time_claim_count='${_time_claim_count:-}' — mong đợi 2"

echo "== 5. Không còn parse theo VỊ TRÍ ở 2 call-site này"
for f in bin/cron_health_check_daily.sh bin/daily_retro.sh; do
  if grep -nE '\$OUT"?\s*\|\s*head -1|_time_claim_out"?\s*\|\s*head -1' "$ROOT/$f" >/dev/null; then
    bad "$f còn ống 'head -1' trên output của script Python"
  else
    ok "$f không parse theo vị trí"
  fi
done

echo
[ "$FAIL" -eq 0 ] && echo "✅ summary_parse_position_selfcheck: PASS" \
                  || echo "❌ summary_parse_position_selfcheck: FAIL"
exit "$FAIL"
