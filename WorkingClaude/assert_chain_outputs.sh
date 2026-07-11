#!/usr/bin/env bash
# assert_chain_outputs.sh — post-chain output freshness assertion (audit Winston_20260710_173031).
#
# Root cause của vụ EW-leg frozen 3 tuần (BULL candidate giả 07-10): 1 writer ghi nhầm
# WORKDIR root trong khi chain đọc data/ — MỌI step vẫn exit 0, không gì kiểm tra file
# output kỳ vọng có THẬT SỰ được ghi mới trong lần chạy này hay không. Script này là cơ
# chế tổng quát: sau khi chain chạy xong phần compute, kiểm tra mtime của TOÀN BỘ file
# output kỳ vọng >= thời điểm chain bắt đầu. File thiếu hoặc cũ hơn → exit 1 kèm liệt kê
# rõ ràng — caller (daily_refresh_v34b_linux.sh) die + alert TRƯỚC khi publish BQ, để dữ
# liệu stale không bao giờ lên production. Bắt generic mọi writer sót trong tương lai
# (kể cả path ghép bằng f-string), không phải vá từng file riêng lẻ.
#
# Usage: assert_chain_outputs.sh <start_epoch> <file> [<file>...]
#   <start_epoch>: epoch seconds lúc chain bắt đầu compute (date +%s)
#   exit 0 = mọi file tồn tại và mtime >= start_epoch (fresh)
#   exit 1 = có file MISSING/STALE (in từng dòng), hoặc usage sai
#
# Test: dt5g_chain_freshness_selfcheck.py (mô phỏng cả stale-phải-die lẫn fresh-phải-pass).
set -uo pipefail

if [ "$#" -lt 2 ]; then
  echo "usage: $0 <start_epoch> <file> [<file>...]" >&2
  exit 1
fi

START="$1"; shift
case "$START" in
  ''|*[!0-9]*) echo "assert_chain_outputs: start_epoch '$START' không phải số" >&2; exit 1 ;;
esac

fail=0
for f in "$@"; do
  if [ ! -f "$f" ]; then
    echo "  MISSING: $f (không tồn tại — writer không chạy hoặc ghi sai path)"
    fail=1
  else
    mt="$(stat -c %Y "$f" 2>/dev/null || echo 0)"
    if [ "$mt" -lt "$START" ]; then
      echo "  STALE:   $f (mtime $(date -d "@$mt" '+%Y-%m-%d %H:%M:%S') < chain start $(date -d "@$START" '+%Y-%m-%d %H:%M:%S') — writer sót/ghi sai path)"
      fail=1
    else
      echo "  fresh:   $f ($(date -d "@$mt" '+%Y-%m-%d %H:%M:%S'))"
    fi
  fi
done
exit "$fail"
