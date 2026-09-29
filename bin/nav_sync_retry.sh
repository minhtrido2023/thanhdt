#!/usr/bin/env bash
# nav_sync_retry.sh — tự retry daily_nav_snapshot.py cho account bị chặn bởi gate
# PRICE_XCHECK (rc=4, "lệch giá TẠM THỜI" — marketPrice của vị thế broker tự đồng bộ
# trễ sau EOD, ca gốc PVT 2026-09-08: trễ ~65'). Cron 15'/lần, 19:15-21:15 ICT.
#
# Không đụng gate/tolerance trong daily_nav_snapshot.py — chỉ đóng khoảng trễ THỜI GIAN.
# Marker do eod_trading_report.sh ghi khi rc=4 (state/nav_pending_retry/<account>_<date>.log).
# Thành công → cập nhật nav_history_*.csv (side effect của chính daily_nav_snapshot.py) +
# báo bù Discord + xoá marker. Vẫn rc=4 sau cutoff 21:15 ICT (~2x độ trễ đã quan sát) →
# không còn là trễ đồng bộ thường thấy, coi là bất thường thật (khả năng corp-action như
# VHM 08-05/MBB 08-11) → escalate bus question, giữ lại marker (đổi hậu tố .stuck) làm
# bằng chứng thay vì xoá, dừng tự retry hôm đó.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"
if [ -f "$WC_ROOT/wc_env.sh" ]; then
  # shellcheck source=/dev/null
  source "$WC_ROOT/wc_env.sh"
fi

MARKER_DIR="$ROOT/state/nav_pending_retry"
[ -d "$MARKER_DIR" ] || exit 0

NOW_HHMM="$(TZ='Asia/Ho_Chi_Minh' date +%H%M)"
TODAY="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)"

shopt -s nullglob
for marker in "$MARKER_DIR"/*.log; do
  base="$(basename "$marker" .log)"
  ACCOUNT="${base%_*}"
  PLAN_DATE="${base##*_}"

  # Marker của ngày trước (worker cron chưa kịp xoá/đổi hậu tố sau 21:15 hôm đó) — không
  # retry chéo ngày, dọn luôn để không tồn đọng mãi.
  if [ "$PLAN_DATE" != "$TODAY" ]; then
    rm -f "$marker"
    continue
  fi

  OUT="$(python3 "$ROOT/bin/daily_nav_snapshot.py" --account "$ACCOUNT" --date "$PLAN_DATE" 2>&1)"
  RC=$?

  if [ "$RC" = "0" ]; then
    rm -f "$marker"
    NAV_LINE="$(printf '%s\n' "$OUT" | grep -v '^\[dnse\]')"
    "$ROOT/bin/notify_thread.sh" "✅ NAV $ACCOUNT ($PLAN_DATE) đã cập nhật bù — giá vị thế broker đã đồng bộ xong:
$NAV_LINE" "trading_report" 2>/dev/null || true
    continue
  fi

  if [ "$RC" != "4" ]; then
    # Đổi loại lỗi giữa chừng (vd thiếu balance record) — không còn là case của gate
    # PRICE_XCHECK nữa; để backstop khác (check_report_cadence.sh) xử lý, tránh 2 cơ chế
    # tự retry giẫm lên nhau trên cùng 1 marker.
    rm -f "$marker"
    continue
  fi

  # Vẫn rc=4 — còn trong cửa sổ thì im lặng chờ lượt cron kế (không spam progress mỗi 15').
  if [ "$NOW_HHMM" -ge "2115" ]; then
    mv -f "$marker" "$MARKER_DIR/${base}.stuck_${TODAY}"
    "$ROOT/bin/append_event.sh" Mafee question "nav-price-xcheck-stuck-${ACCOUNT}-${PLAN_DATE}" \
      "{\"account\":\"$ACCOUNT\",\"plan_date\":\"$PLAN_DATE\",\"summary\":\"Giá close_price(G1) vs marketPrice vị thế broker vẫn lệch >5% sau cutoff 21:15 ICT (~2h retry) — không còn khớp mẫu trễ đồng bộ thường thấy (PVT 08-09 tự hết trong ~65'), khả năng corp-action broker chưa đồng bộ (xem VHM 2026-08-05). Bằng chứng: $MARKER_DIR/${base}.stuck_${TODAY}\",\"urgency\":\"medium\"}" \
      2>/dev/null || true
    "$ROOT/bin/notify_thread.sh" "🟡 NAV $ACCOUNT ($PLAN_DATE) vẫn lệch giá >5% sau 2h tự retry — có thể là corp-action thật, đã escalate bus question, cần kiểm tra thủ công." "trading_report" 2>/dev/null || true
  fi
done
