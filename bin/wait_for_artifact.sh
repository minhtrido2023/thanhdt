#!/usr/bin/env bash
# wait_for_artifact.sh <file> [producer_hint]
#
# Chờ tới khi <file> TỒN TẠI và có mtime HÔM NAY (giờ VN), rồi exit 0. Hết trần thời gian mà
# vẫn chưa có ⇒ exit 1 + in LOUD ra stderr: đã chờ bao lâu, trần bao nhiêu, file mong đợi,
# ai là producer, và lý do mới nhất của csv_fresh_today.sh (§29 — không nuốt chẩn đoán).
#
# LÝ DO TỒN TẠI (sự cố 2026-09-12, hit_details_daily.sh): cặp cron producer→consumer được
# đồng bộ bằng ĐỒNG HỒ (producer 19:00, consumer 19:05) trong khi producer thật sự ghi file
# lúc 19:06-19:07 ⇒ consumer đọc file của PHIÊN TRƯỚC mà không hề báo lỗi. Đồng hồ không bao
# giờ là cơ chế đồng bộ đáng tin: thời gian chạy của producer thay đổi theo tải/BQ/số mã.
# Consumer phải chờ ARTIFACT. Xem kb/coding_guidelines_ext.md §14.
#
# Biến môi trường: WAIT_ARTIFACT_MAX (trần giây, mặc định 600) · WAIT_ARTIFACT_POLL (chu kỳ
# giây, mặc định 30). Cả hai chỉ để selfcheck rút ngắn — production dùng mặc định.
# Điều kiện "tươi" uỷ quyền cho bin/csv_fresh_today.sh (đã neo TZ='Asia/Ho_Chi_Minh' tường
# minh) — không tự chế lại phép so ngày ở đây.
set -uo pipefail

F="${1:?usage: wait_for_artifact.sh <file> [producer_hint]}"
HINT="${2:-}"
BIN="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAX="${WAIT_ARTIFACT_MAX:-600}"
POLL="${WAIT_ARTIFACT_POLL:-30}"

waited=0
while :; do
  if reason="$("$BIN/csv_fresh_today.sh" "$F" 2>&1)"; then
    [ "$waited" -gt 0 ] && echo "ℹ️ wait_for_artifact: đã chờ ${waited}s cho $(basename "$F")." >&2
    exit 0
  fi
  if [ "$waited" -ge "$MAX" ]; then
    {
      echo "❌ wait_for_artifact: HẾT TRẦN — đã chờ ${waited}s (trần ${MAX}s) mà artifact vẫn chưa tươi."
      echo "   file mong đợi : $F  (cần mtime = hôm nay, giờ VN)"
      [ -n "$HINT" ] && echo "   producer      : $HINT"
      echo "   lý do cuối    : $reason"
    } >&2
    exit 1
  fi
  sleep "$POLL"
  waited=$((waited + POLL))
done
