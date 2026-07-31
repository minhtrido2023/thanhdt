#!/usr/bin/env bash
# csv_fresh_today.sh <đường-dẫn-file> [câu-cảnh-báo-tuỳ-biến]
#
# "File này có được GHI trong ngày (giờ VN) không?" — dùng cho cặp cron producer→consumer
# mà consumer chỉ đọc NỘI DUNG file: một file đứng im vì producer chết im lặng đọc y hệt
# file mới (audit §14 cron freshness, job Winston_20260731_062642).
#
# exit 0 + KHÔNG in gì   ⇒ file được ghi hôm nay (im lặng để không sinh cảnh báo giả)
# exit 1 + in 1 dòng WARN ⇒ file thiếu, hoặc mtime KHÔNG phải hôm nay
# Đây là CẢNH BÁO, không phải gate: caller chèn dòng này vào đầu báo cáo rồi VẪN gửi —
# báo cáo trễ còn hơn không có báo cáo.
#
# Ngày luôn tính theo TZ='Asia/Ho_Chi_Minh' TƯỜNG MINH, không dựa vào TZ của tiến trình
# gọi (cron chạy dưới TZ=UTC; bài học dt5g_writer_watch.py 2026-07-31 — bug TZ latent vì
# mọi caller tình cờ có TZ=ICT).
# FRESH_REF_DATE=YYYY-MM-DD ép ngày tham chiếu — CHỈ dùng cho selfcheck.
set -uo pipefail

F="${1:?usage: csv_fresh_today.sh <file> [warn_text]}"
CUSTOM="${2:-}"
TODAY="${FRESH_REF_DATE:-$(TZ='Asia/Ho_Chi_Minh' date +%F)}"
BASE="$(basename "$F")"

if [ ! -f "$F" ]; then
  echo "${CUSTOM:-⚠️ Thiếu file \`$BASE\` — dữ liệu có thể chưa cập nhật hôm nay.} (KHÔNG TÌM THẤY file)"
  exit 1
fi

MTIME_DATE="$(TZ='Asia/Ho_Chi_Minh' date -r "$F" +%F 2>/dev/null || echo "?")"
if [ "$MTIME_DATE" != "$TODAY" ]; then
  echo "${CUSTOM:-⚠️ Dữ liệu \`$BASE\` có thể chưa cập nhật hôm nay (file cũ).} (ghi lần cuối $MTIME_DATE, hôm nay $TODAY)"
  exit 1
fi
exit 0
