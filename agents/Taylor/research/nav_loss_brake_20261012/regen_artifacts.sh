#!/usr/bin/env bash
# Dựng lại TOÀN BỘ artifact vòng 3 của thư mục này từ dữ liệu thật (chỉ ĐỌC data/ thật; state ghi
# vào thư mục tạm; cảnh báo đi vào file sink, KHÔNG gửi Discord):
#   real_run_and_dgc_case.txt · sink_real_run.jsonl · replay_full_history.txt
# Vòng 3: monitor đo NAV toàn tài khoản ⇒ KHÔNG còn seed nào — state bắt đầu từ thư mục RỖNG.
# Dùng: bash regen_artifacts.sh   (chạy từ bất kỳ đâu)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN="$(cd "$HERE/../../../../bin" && pwd)"
NOW=2026-10-12T22:05:00               # đồng hồ giả lập của lượt cron tối 12/10 (dữ liệu 12/10 đã đủ)
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
MON="python3 $BIN/nav_loss_brake_monitor.py"
L="$T/live"; mkdir -p "$L"
export MIKE_LOSS_BRAKE_ALERT_SINK="$T/sink.jsonl"; : > "$MIKE_LOSS_BRAKE_ALERT_SINK"
{
  echo "### 1) CHẠY THẬT trên dữ liệu thật (state = thư mục RỖNG, cảnh báo → sink), --now $NOW"
  $MON --state-dir "$L" --now "$NOW" 2>&1 && echo "rc=0" || echo "rc=$?"
  echo "--- lần 2, lượt 00:20 hôm sau (idempotent)"
  $MON --state-dir "$L" --now 2026-10-13T00:20:00 2>&1 && echo "rc=0" || echo "rc=$?"
  echo "sink lines: $(wc -l < "$MIKE_LOSS_BRAKE_ALERT_SINK")"
  echo "run_log.jsonl:"; cat "$L/run_log.jsonl"
  echo "file trong state-dir sau 2 lượt: $(ls -A "$L" | tr '\n' ' ')"
  echo; echo "### 2) dòng ops_health sáng 13/10 (đọc status.json vừa ghi)"
  for a in SpaceX ZaloPay; do
    $MON --state-dir "$L" --now 2026-10-13T08:20:00 --health-line --account "$a" 2>&1 && echo "rc=0" || echo "rc=$?"
  done
  echo; echo "### 3) --date của phiên cũ ⇒ CHẠY KHÔ (không ghi status, không gửi) — đối chiếu số 09/10 đã báo user"
  $MON --state-dir "$L" --now "$NOW" --date 2026-10-09 2>&1 && echo "rc=0" || echo "rc=$?"
  echo "sink lines: $(wc -l < "$MIKE_LOSS_BRAKE_ALERT_SINK")"
  echo; echo "### 4) --now trên state SỐNG bị từ chối (K3) — không ghi gì"
  $MON --now "$NOW" 2>&1 && echo "rc=0" || echo "rc=$?"
  echo; echo "### 5) CA DGC — cổ tức tiền (GDKHQ 14/09, trả 25/09) trên NAV TỔNG của ZaloPay"
  python3 "$HERE/dgc_dividend_window.py"
} > "$HERE/real_run_and_dgc_case.txt"
cp "$MIKE_LOSS_BRAKE_ALERT_SINK" "$HERE/sink_real_run.jsonl"
$MON --state-dir "$L" --now "$NOW" --replay > "$HERE/replay_full_history.txt" 2>&1 || true
sed -i "s|$T|<tmp>|g" "$HERE/real_run_and_dgc_case.txt" "$HERE/replay_full_history.txt" "$HERE/sink_real_run.jsonl"
grep -E "===|phiên im lặng|cả lịch sử" "$HERE/replay_full_history.txt"
