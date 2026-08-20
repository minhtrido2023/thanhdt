#!/usr/bin/env bash
# daily_retro_wake_metrics_selfcheck.sh — selfcheck cho KHỐI ĐO LƯỜNG hệ wake-up mà
# daily_retro.sh bơm vào draft prompt (Phase 4, thêm 2026-08-20).
#
# Bất biến kiểm tra:
#   1. File log thiếu ⇒ mọi số về 0, KHÔNG để rỗng lọt vào số học bash (đúng mẫu bug quoting
#      im lặng đã ăn 2 lần ở chính daily_retro.sh/kb_nightly.sh).
#   2. success-rate tính đúng trên ok/(ok+err); không có lượt push nào ⇒ "n/a", không chia 0.
#   3. CỬA SỔ NGÀY: chỉ đếm dòng của đúng ngày ICT đang review — dòng ngày khác trong CÙNG
#      file không được lọt (đây là bất biến dễ vỡ nhất: cả 3 file đều append liên tục).
#   4. Chỉ dòng SUCCESS mới tính là push thành công (dòng khác trong wake_thread.log không).
#   5. rescued > 0 ⇒ câu kết luận phải nói rõ CÒN BUG EDGE (đó là toàn bộ giá trị của số này:
#      lưới an toàn hoạt động KHÔNG có nghĩa là hết bug ở tầng edge).
#   6. rescued = 0 KHÔNG được tự động thành "khoẻ" (arch-reviewer N2, vòng 4). Reconciler MÙ
#      cả ngày (abort mọi chu kỳ) và reconciler CHẾT HẲN (cron bị gỡ) đều cho rescued=0 — nếu
#      verdict trấn an trong 2 ca đó thì báo cáo đo lường tái tạo đúng anti-pattern
#      "im lặng = khoẻ" mà cả bản redesign này sinh ra để diệt. Bốn nhánh phải PHÂN BIỆT được:
#      không-chạy / mù / phủ-cụt / chạy-sạch.
#   7. ĐỘ PHỦ, không chỉ "có chạy hay không" (arch-reviewer vòng 5). `cycles > 0` KHÔNG đủ để
#      trấn an: đo trên log thật, 4/288 chu kỳ (1,4%) vẫn cho ra câu "tầng edge phủ đủ trong
#      ngày". `fleet_housekeeping.sh` rotate cron log >300k lúc 22:00 CN (~2 tuần/lần) làm bộ
#      đếm cụt ĐỊNH KỲ và xoá luôn dòng CRITICAL ABORT ⇒ blind=0 ⇒ nhánh MÙ không tới.
#
# Khối bash được TRÍCH THẲNG từ bin/daily_retro.sh (không copy logic — cùng kỷ luật với
# daily_retro_failcause_selfcheck.sh vốn đọc regex thật từ file thật).
# Chạy: bash mike/bin/daily_retro_wake_metrics_selfcheck.sh   (exit 0 = PASS)
set -uo pipefail
REAL="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SB="$(mktemp -d)"
trap 'rm -rf "$SB"' EXIT

BLOCK="$SB/block.sh"
sed -n '/^# --- Đo lường hệ WAKE-UP/,/^echo "\$(date -Iseconds) \[wake-metrics\]/p' \
  "$REAL/bin/daily_retro.sh" > "$BLOCK"
grep -q '_wake_rate=' "$BLOCK" || { echo "FAIL: không trích được khối đo lường từ daily_retro.sh"; exit 1; }
grep -q '_wake_verdict=' "$BLOCK" || { echo "FAIL: khối trích thiếu _wake_verdict"; exit 1; }

pass=0; fail=0
assert() { # <ten> <thuc> <mong doi>
  if [ "$2" = "$3" ]; then pass=$((pass+1)); printf 'PASS %-52s = %s\n' "$1" "$2"
  else fail=$((fail+1)); printf 'FAIL %-52s thực=%q ≠ mong đợi=%q\n' "$1" "$2" "$3"; fi
}

# run_block <ngay> — chạy khối trong subshell với ROOT trỏ vào sandbox, in ra 8 giá trị.
# ⚠️ `_wake_rescued` (R[7]) THÊM 2026-08-20 sau arch-reviewer M7 (re-audit trước-commit): bản
# đầu của khối test này KHÔNG in giá trị này ra, nên revert F3 riêng cho wakeup_reconcile.log
# (con số DUY NHẤT quyết định nhánh verdict "CÒN BUG EDGE") không có test nào bắt được — sửa
# code đúng nhưng suite mù với đúng chỗ quan trọng nhất. Đừng bớt lại field nào khỏi đây.
run_block() {
  ( set -uo pipefail
    ROOT="$SB"; TODAY="$1"; LOG="$SB/daily_retro.log"
    # shellcheck disable=SC1090
    source "$BLOCK"
    printf '%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n' "$_wake_ok" "$_wake_err" "$_wake_total" \
      "$_wake_rate" "$_wake_cycles" "$_wake_blind" "$_wake_verdict" "$_wake_rescued" )
}

echo "== CA 1: chưa có file log nào ⇒ mọi số = 0, rate = n/a, và verdict PHẢI nói KHÔNG ĐO"
echo "         ĐƯỢC GÌ — không được trấn an từ sự vắng mặt bằng chứng (arch-reviewer N2)"
mkdir -p "$SB/logs"
mapfile -t R < <(run_block 2026-08-19)
assert "ok" "${R[0]}" "0"; assert "err" "${R[1]}" "0"; assert "total" "${R[2]}" "0"
assert "rate" "${R[3]}" "n/a (không có lượt push nào trong ngày)"
assert "cycles" "${R[4]}" "0"; assert "blind" "${R[5]}" "0"
assert "verdict nói RECONCILER KHÔNG CHẠY" "$(printf '%s' "${R[6]}" | grep -c 'KHÔNG CHẠY')" "1"
assert "verdict KHÔNG nói tầng edge phủ đủ" "$(printf '%s' "${R[6]}" | grep -c 'phủ đủ')" "0"

echo "== CA 2: 9 SUCCESS + 1 lỗi trong ngày ⇒ 90.0%; dòng NGÀY KHÁC và dòng không-SUCCESS bị loại"
for i in $(seq 1 9); do
  echo "2026-08-19T1$((i%10)):00:0$i+07:00 wake_thread: SUCCESS | job_id=j$i thread_id=1 task_id=$i" >> "$SB/logs/wake_thread.log"
done
echo "2026-08-18T11:00:00+07:00 wake_thread: SUCCESS | job_id=jold thread_id=1 task_id=0" >> "$SB/logs/wake_thread.log"
echo "2026-08-19T11:30:00+07:00 wake_thread: (dòng không phải SUCCESS)" >> "$SB/logs/wake_thread.log"
echo "2026-08-19T10:44:54+07:00 wake_thread: HTTP 409 | thread_id=1 name_suffix=x" >> "$SB/logs/wake_thread_errors.log"
echo "2026-08-18T10:44:54+07:00 wake_thread: HTTP 409 | thread_id=1 name_suffix=old" >> "$SB/logs/wake_thread_errors.log"
mapfile -t R < <(run_block 2026-08-19)
assert "ok (loại dòng ngày khác + dòng không SUCCESS)" "${R[0]}" "9"
assert "err (loại dòng ngày khác)" "${R[1]}" "1"
assert "rate" "${R[3]}" "90.0%"

echo "== CA 3: reconciler phải cứu ⇒ verdict PHẢI nói còn bug edge"
# Cron log là bằng chứng "đã thật sự đối chiếu" — thiếu nó thì mọi kết luận về tầng edge đều
# vô nghĩa, kể cả kết luận XẤU. Seed 288 chu kỳ = một ngày đủ nhịp */5.
for i in $(seq 1 288); do
  echo "OK 2026-08-19T00:00:00+07:00 candidates=0 fired=0 capped=0 errlog_new=0" >> "$SB/logs/wakeup_reconcile_cron.log"
done
echo "2026-08-19T12:00:00+07:00 RESCUED job=Taylor_x to=Taylor status=done thread=1 (chờ 600s)" >> "$SB/logs/wakeup_reconcile.log"
echo "2026-08-19T12:30:00+07:00 RESCUED job=Taylor_y to=Taylor status=done thread=2 (chờ 900s)" >> "$SB/logs/wakeup_reconcile.log"
echo "2026-08-18T12:30:00+07:00 RESCUED job=Taylor_z to=Taylor status=done thread=3 (chờ 900s)" >> "$SB/logs/wakeup_reconcile.log"
echo "2026-08-19T12:35:00+07:00 CYCLE-CAP đạt 3 wake/chu kỳ" >> "$SB/logs/wakeup_reconcile.log"
mapfile -t R < <(run_block 2026-08-19)
assert "verdict nêu CÒN BUG EDGE" "$(printf '%s' "${R[6]}" | grep -c 'CÒN BUG EDGE')" "1"
assert "verdict nêu đúng số lần cứu (2, không tính ngày khác/dòng khác)" \
  "$(printf '%s' "${R[6]}" | grep -c 'cứu 2 lần')" "1"
assert "đếm đúng số chu kỳ đối chiếu được" "${R[4]}" "288"

echo "== CA 5: reconciler MÙ vài chu kỳ ⇒ rescued KHÔNG được coi là con số đủ (sàn dưới)"
for i in $(seq 1 12); do
  echo "CRITICAL ABORT 2026-08-19T03:0$((i%10)):00+07:00 tasks.db không đọc được — không bắn wake nào (chu kỳ mù liên tiếp=$i, errlog_new=0)" >> "$SB/logs/wakeup_reconcile_cron.log"
done
echo "CRITICAL ABORT 2026-08-18T03:00:00+07:00 tasks.db không đọc được — ngày khác" >> "$SB/logs/wakeup_reconcile_cron.log"
mapfile -t R < <(run_block 2026-08-19)
assert "đếm đúng chu kỳ mù (loại ngày khác)" "${R[5]}" "12"
assert "verdict nói RECONCILER MÙ" "$(printf '%s' "${R[6]}" | grep -c 'RECONCILER MÙ')" "1"
assert "verdict gọi rescued là SÀN DƯỚI" "$(printf '%s' "${R[6]}" | grep -c 'SÀN DƯỚI')" "1"
assert "verdict KHÔNG nói tầng edge phủ đủ" "$(printf '%s' "${R[6]}" | grep -c 'phủ đủ')" "0"

echo "== CA 7: bằng chứng CỤT (24/288 chu kỳ — ngày bị fleet_housekeeping rotate lúc 22:00 CN)"
echo "         ⇒ KHÔNG được trấn an, phải nêu tỷ lệ n/288 (arch-reviewer vòng 5)"
rm -f "$SB/logs/wakeup_reconcile.log" "$SB/logs/wakeup_reconcile_cron.log"
for i in $(seq 1 24); do
  echo "OK 2026-08-19T22:00:00+07:00 candidates=0 fired=0 capped=0 errlog_new=0" >> "$SB/logs/wakeup_reconcile_cron.log"
done
mapfile -t R < <(run_block 2026-08-19)
assert "cycles đếm đúng phần còn lại" "${R[4]}" "24"
assert "verdict KHÔNG trấn an" "$(printf '%s' "${R[6]}" | grep -c 'phủ đủ trong ngày')" "0"
assert "verdict nêu tỷ lệ đo được" "$(printf '%s' "${R[6]}" | grep -c 'CHỈ ĐO ĐƯỢC 24/288')" "1"
assert "verdict KHÔNG dùng chữ 'chạy đủ'" "$(printf '%s' "${R[6]}" | grep -c 'chạy đủ')" "0"

echo "== CA 8: VỪA MÙ VỪA CỤT (24 OK + 1 abort) ⇒ nhánh MÙ KHÔNG được bypass cổng độ phủ"
echo "         — \"MÙ 1/25\" đọc ra là 96% khoẻ trong khi 263/288 chu kỳ không có bằng chứng"
rm -f "$SB/logs/wakeup_reconcile_cron.log"
for i in $(seq 1 24); do
  echo "OK 2026-08-19T22:00:00+07:00 candidates=0 fired=0 capped=0 errlog_new=0" >> "$SB/logs/wakeup_reconcile_cron.log"
done
echo "CRITICAL ABORT 2026-08-19T23:00:00+07:00 tasks.db không đọc được — không bắn wake nào (chu kỳ mù liên tiếp=1, errlog_new=0)" >> "$SB/logs/wakeup_reconcile_cron.log"
mapfile -t R < <(run_block 2026-08-19)
assert "cycles" "${R[4]}" "24"; assert "blind" "${R[5]}" "1"
assert "verdict vẫn nói RECONCILER MÙ" "$(printf '%s' "${R[6]}" | grep -c 'RECONCILER MÙ')" "1"
assert "verdict mang mẫu số ĐỘ PHỦ cả ngày (25/288)" \
  "$(printf '%s' "${R[6]}" | grep -c '25/288')" "1"
assert "KHÔNG để mẫu số 1/25 đứng một mình" "$(printf '%s' "${R[6]}" | grep -c 'MÙ 1/25')" "0"
assert "verdict KHÔNG trấn an" "$(printf '%s' "${R[6]}" | grep -c 'phủ đủ trong ngày')" "0"

echo "== CA 9: log ĐÃ ROTATE (.1.gz/.2.gz) vẫn phải được đếm — dữ liệu còn nguyên bên cạnh,"
echo "         báo \"không có bằng chứng\" khi bằng chứng còn đó là báo SAI (~20 lần/năm)"
rm -f "$SB/logs/wakeup_reconcile_cron.log" "$SB"/logs/wakeup_reconcile_cron.log.*.gz
for i in $(seq 1 200); do
  echo "OK 2026-08-19T10:00:00+07:00 candidates=0 fired=0 capped=0 errlog_new=0"
done | gzip -c > "$SB/logs/wakeup_reconcile_cron.log.1.gz"
{ for i in $(seq 1 62); do
    echo "OK 2026-08-19T20:00:00+07:00 candidates=0 fired=0 capped=0 errlog_new=0"
  done
  echo "CRITICAL ABORT 2026-08-19T21:00:00+07:00 tasks.db không đọc được — (chu kỳ mù liên tiếp=1)"
} | gzip -c > "$SB/logs/wakeup_reconcile_cron.log.2.gz"
for i in $(seq 1 26); do
  echo "OK 2026-08-19T23:00:00+07:00 candidates=0 fired=0 capped=0 errlog_new=0" >> "$SB/logs/wakeup_reconcile_cron.log"
done
mapfile -t R < <(run_block 2026-08-19)
assert "gộp hot + .1.gz + .2.gz (26+200+62)" "${R[4]}" "288"
assert "dòng CRITICAL trong .gz cũng được thấy" "${R[5]}" "1"
assert "KHÔNG double-count (không nhân đôi thành 576)" "$(printf '%s' "${R[4]}")" "288"
rm -f "$SB"/logs/wakeup_reconcile_cron.log.*.gz

echo "== CA 10: wake_thread.log/wake_thread_errors.log ĐÃ ROTATE cũng phải được đếm — bản đầu"
echo "          của F3 chỉ vá cron log, để 3 file kia undercount im lặng (arch-reviewer F3)"
rm -f "$SB/logs/wake_thread.log" "$SB/logs/wake_thread.log".*.gz \
      "$SB/logs/wake_thread_errors.log" "$SB/logs/wake_thread_errors.log".*.gz
for i in $(seq 1 5); do
  echo "2026-08-19T10:00:0$i+07:00 wake_thread: SUCCESS | job_id=r$i thread_id=1 task_id=$i"
done | gzip -c > "$SB/logs/wake_thread.log.1.gz"
echo "2026-08-19T20:00:00+07:00 wake_thread: SUCCESS | job_id=hot thread_id=1 task_id=9" \
  >> "$SB/logs/wake_thread.log"
echo "2026-08-19T09:00:00+07:00 wake_thread: HTTP 409 | thread_id=1 name_suffix=r0" \
  | gzip -c > "$SB/logs/wake_thread_errors.log.1.gz"
mapfile -t R < <(run_block 2026-08-19)
assert "push OK gộp hot(1) + .1.gz(5) = 6" "${R[0]}" "6"
assert "push lỗi gộp hot(0) + .1.gz(1) = 1" "${R[1]}" "1"
assert "rate tính trên tổng đã gộp 6/7" "${R[3]}" "85.7%"
rm -f "$SB/logs/wake_thread.log".*.gz "$SB/logs/wake_thread_errors.log".*.gz

echo "== CA 11: wakeup_reconcile.log (rescued) ĐÃ ROTATE cũng phải được đếm — con số DUY NHẤT"
echo "          quyết định nhánh verdict 'CÒN BUG EDGE' (arch-reviewer M7, re-audit 08-20:"
echo "          mutation revert riêng file này lọt qua CA 9/10 vì 2 ca đó không test rescued)"
rm -f "$SB/logs/wakeup_reconcile.log" "$SB/logs/wakeup_reconcile.log".*.gz \
      "$SB/logs/wakeup_reconcile_cron.log"
for i in $(seq 1 3); do
  echo "2026-08-19T0$i:00:00+07:00 RESCUED job=Taylor_rot$i to=Taylor status=done thread=1 (chờ 600s)"
done | gzip -c > "$SB/logs/wakeup_reconcile.log.1.gz"
echo "2026-08-19T12:00:00+07:00 RESCUED job=Taylor_hot to=Taylor status=done thread=2 (chờ 900s)" \
  >> "$SB/logs/wakeup_reconcile.log"
echo "2026-08-18T12:00:00+07:00 RESCUED job=Taylor_yday to=Taylor status=done thread=3 (chờ 900s)" \
  >> "$SB/logs/wakeup_reconcile.log"
for i in $(seq 1 288); do
  echo "OK 2026-08-19T00:0$((i%10)):00+07:00 candidates=0 fired=0 capped=0 stale=0 unreadable=0 errlog_new=0" >> "$SB/logs/wakeup_reconcile_cron.log"
done
mapfile -t R < <(run_block 2026-08-19)
assert "rescued gộp hot(1) + .1.gz(3) = 4, KHÔNG lẫn dòng ngày khác" "${R[7]}" "4"
assert "verdict phải nói CÒN BUG EDGE (rescued>0 không được trấn an)" \
  "$(printf '%s' "${R[6]}" | grep -c 'CÒN BUG EDGE')" "1"
rm -f "$SB/logs/wakeup_reconcile.log".*.gz

echo "== CA 6: chạy đủ chu kỳ, không mù, không phải cứu ⇒ ĐÂY mới là ca được trấn an"
rm -f "$SB/logs/wakeup_reconcile.log" "$SB/logs/wakeup_reconcile_cron.log"
for i in $(seq 1 288); do
  echo "OK 2026-08-19T00:00:00+07:00 candidates=0 fired=0 capped=0 errlog_new=0" >> "$SB/logs/wakeup_reconcile_cron.log"
done
mapfile -t R < <(run_block 2026-08-19)
assert "verdict nói phủ đủ" "$(printf '%s' "${R[6]}" | grep -c 'phủ đủ')" "1"
assert "verdict dẫn ĐỘ PHỦ làm bằng chứng" "$(printf '%s' "${R[6]}" | grep -c '288/288 chu kỳ')" "1"

echo "== CA 4: ngày không có gì trong file ĐÃ TỒN TẠI ⇒ vẫn 0/n/a, không lỗi cú pháp"
mapfile -t R < <(run_block 1999-01-01)
assert "ok" "${R[0]}" "0"; assert "err" "${R[1]}" "0"
assert "rate" "${R[3]}" "n/a (không có lượt push nào trong ngày)"
assert "ngày không có chu kỳ nào ⇒ verdict nói KHÔNG CHẠY, không trấn an" \
  "$(printf '%s' "${R[6]}" | grep -c 'KHÔNG CHẠY')" "1"

echo
echo "---"; echo "PASS=$pass FAIL=$fail"
[ "$fail" -eq 0 ]
