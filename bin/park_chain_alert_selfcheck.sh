#!/usr/bin/env bash
# park_chain_alert_selfcheck.sh — chứng minh rc!=0 của chuỗi PARK **tới được người** (2026-09-27).
#
# Vì sao không gọi thẳng park_trim_daily.sh: nó tự chặn ngoài ngày giao dịch / trước 15:00 ICT
# (guard đúng, không được nới để test). Nên lấy NGUYÊN VĂN hàm `alert_human` từ chính script rồi
# chạy nó trong harness — không chép tay ⇒ sửa script mà quên sửa test là test chết, không phải
# test xanh giả.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
n=0; fails=0
ok() { n=$((n+1)); if [ "$1" != "0" ]; then fails=$((fails+1)); echo "  FAIL $2"; else echo "  PASS $2"; fi; }

extract_fn() {   # $1 = script
  sed -n '/^alert_human() {/,/^}$/p' "$1"
}

for SCRIPT in park_trim_daily.sh jit_unpark_daily.sh; do
  P="$ROOT/bin/$SCRIPT"
  echo "=== $SCRIPT ==="

  FN="$(extract_fn "$P")"
  [ -n "$FN" ]; ok $? "$SCRIPT: trích được hàm alert_human"

  # (1) nhánh thất bại có GỌI alert_human (không chỉ `|| rc=1`)
  grep -q 'alert_human ' "$P"; ok $? "$SCRIPT: nhánh thất bại gọi alert_human"
  grep -q 'arc=\$?' "$P"; ok $? "$SCRIPT: giữ rc THẬT của tiến trình con (arc=\$?)"
  grep -q 'rc=\$arc' "$P"; ok $? "$SCRIPT: exit code mang rc thật, không dập về 1"

  # (2) chạy THẬT hàm alert_human với notify GIẢ THẤT BẠI ⇒ phải in LỖI THẬT ra stderr (§29)
  STUB="$(mktemp -d)"; mkdir -p "$STUB/bin"
  printf '#!/bin/sh\necho "boom: thread khong ton tai" >&2\nexit 9\n' > "$STUB/bin/notify_thread.sh"
  printf '#!/bin/sh\nexit 0\n' > "$STUB/bin/append_event.sh"
  chmod +x "$STUB/bin/notify_thread.sh" "$STUB/bin/append_event.sh"
  ERR="$( CHAIN_TAG=test ROOT="$STUB" PLAN_DATE=2026-09-28 \
          bash -c "$(printf '%s\n' "$FN" 'alert_human t-topic "noi dung thu"')" 2>&1 >/dev/null )"
  case "$ERR" in *"boom: thread khong ton tai"*) ok 0 "$SCRIPT: notify chết ⇒ in LỖI THẬT của notify (§29)";;
                 *) ok 1 "$SCRIPT: notify chết mà KHÔNG in lỗi thật — got: $ERR";; esac

  # (3) notify THÀNH CÔNG ⇒ nội dung đi đúng vào tham số, không im lặng, không thêm stderr
  printf '#!/bin/sh\necho "$1" > %s/sent.txt\nexit 0\n' "$STUB" > "$STUB/bin/notify_thread.sh"
  chmod +x "$STUB/bin/notify_thread.sh"
  ERR2="$( CHAIN_TAG=test ROOT="$STUB" PLAN_DATE=2026-09-28 \
           bash -c "$(printf '%s\n' "$FN" 'alert_human t-topic "NOI DUNG DAC TRUNG 4707"')" 2>&1 >/dev/null )"
  [ -z "$ERR2" ]; ok $? "$SCRIPT: notify OK ⇒ không rác stderr (got: $ERR2)"
  grep -q "NOI DUNG DAC TRUNG 4707" "$STUB/sent.txt" 2>/dev/null
  ok $? "$SCRIPT: nội dung cảnh báo tới đúng notify_thread.sh"

  # (4) opt-out test-mode KHÔNG gọi notify thật
  rm -f "$STUB/sent.txt"
  OUT4="$( CHAIN_TAG=test ROOT="$STUB" PLAN_DATE=2026-09-28 PARK_CHAIN_NO_NOTIFY=1 \
           bash -c "$(printf '%s\n' "$FN" 'alert_human t-topic "KHONG DUOC GUI"')" 2>&1 )"
  [ ! -f "$STUB/sent.txt" ]; ok $? "$SCRIPT: PARK_CHAIN_NO_NOTIFY=1 ⇒ KHÔNG post thật"
  case "$OUT4" in *"notify TẮT"*) ok 0 "$SCRIPT: opt-out in dấu vết tường minh";;
                  *) ok 1 "$SCRIPT: opt-out im lặng — got: $OUT4";; esac
  rm -rf "$STUB"
done

# (5) park_trim phải nói riêng ý nghĩa rc=7 (trần park không đọc được) — đúng killer objection
grep -q 'rc=7' "$ROOT/bin/park_trim_daily.sh"; ok $? "park_trim: cảnh báo giải thích riêng rc=7"
grep -q 'trading_rules.json' "$ROOT/bin/park_trim_daily.sh"; ok $? "park_trim: chỉ đúng file cần kiểm"

echo
if [ "$fails" = 0 ]; then echo "PASS  ($n assertion)"; else echo "FAIL  ($n assertion, $fails fail)"; fi
exit $([ "$fails" = 0 ] && echo 0 || echo 1)
