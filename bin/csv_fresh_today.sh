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
#
# FRESH_TRADING_DAY=1 (TÙY CHỌN, mặc định TẮT) — đổi mốc "hôm nay" thành "PHIÊN GIAO DỊCH
# GẦN NHẤT". Cần cho consumer chạy cả ngày không giao dịch: producer đứng sau một cron
# `1-5` thì thứ Hai (hay ngày sau nghỉ lễ) file mới nhất hợp lệ vẫn là của phiên trước, và
# luật "ghi HÔM NAY" sẽ kêu oan. Đây đúng lớp lỗi đã cắn 2 lần trong 2 ngày: preflight
# ticker_prune lag 2026-09-03 và macro_health tdays 2026-09-04 — cả hai đều đếm NGÀY LỊCH
# ở chỗ đáng lẽ phải đếm PHIÊN. Mặc định giữ nguyên hành vi cũ để caller đang chạy
# (telegram_run_daily.sh, chạy T2-T6 ngay sau producer cùng ngày) không đổi một byte.
set -uo pipefail

F="${1:?usage: csv_fresh_today.sh <file> [warn_text]}"
CUSTOM="${2:-}"
TODAY="${FRESH_REF_DATE:-$(TZ='Asia/Ho_Chi_Minh' date +%F)}"
BASE="$(basename "$F")"

# Mốc so sánh: mặc định là ngày lịch hôm nay; bật FRESH_TRADING_DAY thì lùi về phiên giao
# dịch gần nhất (tính CẢ hôm nay nếu hôm nay là phiên). Dùng chung nguồn ngày nghỉ với bot
# (`trading_bot.vn_market.is_holiday`) — KHÔNG tự chế lịch nghỉ thứ hai.
# Fail-open: thiếu/lỗi import ⇒ giữ nguyên mốc ngày lịch, tức hành vi cũ; một lỗi import
# không được phép biến cổng tươi này thành "luôn luôn tươi".
REF="$TODAY"
if [ "${FRESH_TRADING_DAY:-0}" = "1" ]; then
  _wc_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
  if _td="$(cd "$_wc_root" && python3 -c "
import sys, datetime as dt
sys.path.insert(0, '.')
from trading_bot.vn_market import is_holiday
d = dt.date.fromisoformat('$TODAY')
while d.weekday() >= 5 or is_holiday(d):
    d -= dt.timedelta(days=1)
print(d.isoformat())
" 2>/dev/null)" && [ -n "$_td" ]; then
    REF="$_td"
  else
    echo "⚠️ csv_fresh_today: FRESH_TRADING_DAY=1 nhưng không tính được phiên gần nhất" \
         "(import trading_bot.vn_market lỗi) — dùng lại mốc ngày lịch $TODAY." >&2
  fi
fi

if [ ! -f "$F" ]; then
  echo "${CUSTOM:-⚠️ Thiếu file \`$BASE\` — dữ liệu có thể chưa cập nhật hôm nay.} (KHÔNG TÌM THẤY file)"
  exit 1
fi

MTIME_DATE="$(TZ='Asia/Ho_Chi_Minh' date -r "$F" +%F 2>/dev/null || echo "?")"
if [ "$MTIME_DATE" != "$REF" ]; then
  echo "${CUSTOM:-⚠️ Dữ liệu \`$BASE\` có thể chưa cập nhật hôm nay (file cũ).} (ghi lần cuối $MTIME_DATE, mốc cần $REF)"
  exit 1
fi
exit 0
