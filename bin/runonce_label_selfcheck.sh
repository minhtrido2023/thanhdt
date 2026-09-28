#!/usr/bin/env bash
# runonce_label_selfcheck.sh — `_runonce_label` phân biệt "không có account live" với "LỖI"
# (2026-09-28, user duyệt). Trước đây `2>/dev/null || true` gộp cả hai thành chuỗi rỗng ⇒ 3 check
# chạy-một-lần biến mất cho CẢ HAI account mà không dòng nào nói vì sao.
#
# Chạy hàm TRÍCH NGUYÊN VĂN từ script (không chép tay) trong sandbox có `trading_bot` giả.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OLD_REF="${RUNONCE_OLD_REF:-9c7e8bf6}"   # cha cua commit va (cap nhat sau khi commit)
n=0; fails=0
ok() { n=$((n+1)); if [ "$1" != "0" ]; then fails=$((fails+1)); echo "  FAIL $2"; else echo "  PASS $2"; fi; }

# Khối = từ dòng `RUNONCE_ERR=""` (bản mới) hoặc `_runonce_label() {` (bản cũ) tới hết phần xử lý.
extract() {   # $1 = nội dung script — bản MỚI: từ `_runonce_label() {` tới hết `esac`
  printf '%s\n' "$1" | sed -n '/^_runonce_label() {$/,/^esac$/p'
}
extract_old() {
  printf '%s\n' "$1" | sed -n '/^_runonce_label() {/,/^RUNONCE_LABEL=/p'
}

sandbox() {   # $1 = nội dung config.py giả  → in ra WC_ROOT
  local d; d="$(mktemp -d)"; mkdir -p "$d/trading_bot"
  : > "$d/trading_bot/__init__.py"
  printf '%s\n' "$1" > "$d/trading_bot/config.py"
  printf '%s' "$d"
}

NEW_SRC="$(cat "$ROOT/bin/ops_health_check.sh")"
OLD_SRC="$(git -C "$ROOT" show "$OLD_REF:bin/ops_health_check.sh")"

CFG_OK='def live_dnse_labels():
    return ["SpaceX", "ZaloPay"]'
CFG_EMPTY='def live_dnse_labels():
    return []'
CFG_BOOM='raise RuntimeError("config hong: thieu secrets/trading_bot_accounts.json")'

run_new() {   # $1 = cfg  → in "<label>|<err>"
  local d; d="$(sandbox "$1")"
  ( export WC_ROOT="$d"
    eval "$(extract "$NEW_SRC")" >/dev/null 2>"$d/err.txt"
    printf '%s|%s' "$RUNONCE_LABEL" "${RUNONCE_ERR:0:60}" )
  rm -rf "$d"
}
run_new_out() {   # $1 = cfg  → in stdout (để kiểm câu cảnh báo)
  local d; d="$(sandbox "$1")"
  ( export WC_ROOT="$d"; eval "$(extract "$NEW_SRC")" 2>/dev/null )
  rm -rf "$d"
}
run_old() {
  local d; d="$(sandbox "$1")"
  ( export WC_ROOT="$d"
    eval "$(extract_old "$OLD_SRC")" >/dev/null 2>&1
    printf '%s' "$RUNONCE_LABEL" )
  rm -rf "$d"
}

echo "=== bản MỚI ==="
r="$(run_new "$CFG_OK")";     [ "${r%%|*}" = "SpaceX" ] && [ -z "${r#*|}" ]; ok $? "account live ⇒ 'SpaceX', không lỗi (got: $r)"
r="$(run_new "$CFG_EMPTY")";  [ -z "${r%%|*}" ] && [ -z "${r#*|}" ];        ok $? "KHÔNG có account live ⇒ rỗng, KHÔNG báo lỗi (got: $r)"
r="$(run_new "$CFG_BOOM")";   [ -z "${r%%|*}" ] && [ -n "${r#*|}" ];        ok $? "config LỖI ⇒ rỗng NHƯNG có RUNONCE_ERR (got: $r)"
o="$(run_new_out "$CFG_BOOM")"
case "$o" in *"KHONG lay duoc nhan account live"*) ok 0 "config lỗi ⇒ IN cảnh báo";; *) ok 1 "không in cảnh báo — got: $o";; esac
case "$o" in *"RuntimeError"*|*"config hong"*) ok 0 "cảnh báo mang LỖI THẬT (§29)";; *) ok 1 "không trích lỗi thật — got: $o";; esac
case "$o" in *"anomaly_scan"*) ok 0 "cảnh báo nói rõ 3 check nào bị bỏ";; *) ok 1 "không nêu check bị bỏ";; esac
o2="$(run_new_out "$CFG_EMPTY")"
[ -z "$o2" ]; ok $? "ca hợp lệ (không account live) KHÔNG in gì — không thêm nhiễu (got: $o2)"

echo "=== 2 CHIỀU: bản CŨ @$OLD_REF ==="
r="$(run_old "$CFG_OK")";    [ "$r" = "SpaceX" ];  ok $? "bản cũ happy path vẫn 'SpaceX' (tiền đề A/B) (got: $r)"
r1="$(run_old "$CFG_EMPTY")"; r2="$(run_old "$CFG_BOOM")"
[ -z "$r1" ] && [ -z "$r2" ]; ok $? "bản cũ: 'không có account' và 'LỖI' cho CÙNG chuỗi rỗng ⇒ KHÔNG phân biệt được (got: '$r1' / '$r2')"

echo
if [ "$fails" = 0 ]; then echo "PASS  ($n assertion)"; else echo "FAIL  ($n assertion, $fails fail)"; fi
exit $([ "$fails" = 0 ] && echo 0 || echo 1)
