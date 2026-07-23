#!/usr/bin/env bash
# fa_ratings_earnings_window_daily.sh — QUY TẮC VĨNH VIỄN mỗi quý (user chỉ đạo 2026-07-14,
# job Winston_20260714_160739; SỬA 2026-07-23 — user xác nhận với bq_admin rằng
# ticker_financial vẫn được cập nhật kể cả cuối tuần, nên bỏ điều kiện T2-T6): trong mùa BCTC —
# từ ngày 15 của THÁNG ĐẦU mỗi quý (1/4/7/10) đến HẾT tháng đó — re-rate 8L MỖI NGÀY TRONG CỬA
# SỔ, KỂ CẢ CUỐI TUẦN (chỉ trừ lễ VN), vì báo cáo tài chính công bố dồn dập trong cửa sổ này và
# cohort ngày đầu thường chưa đầy đủ.
#
# Thay thế 2 dòng cron TẠM THỜI thứ Ba (Winston_20260713_103213, guard ≤20260804) — đã xoá
# cùng commit. Dòng thứ Bảy hàng tuần (08:30/09:15) GIỮ NGUYÊN làm baseline quanh năm.
#
# Crontab (server chạy UTC; 13:00 UTC = 20:00 ICT, chạy DAILY — gate ngày/tháng nằm ở đây):
#   0 13 * * * /home/trido/thanhdt/WorkingClaude/mike/bin/fa_ratings_earnings_window_daily.sh >> /home/trido/thanhdt/WorkingClaude/mike/logs/fa_ratings_earnings_window.log 2>&1
#
# Điều kiện chạy (cả 3 phải đúng, tính theo ngày ICT qua trading_bot.vn_market — không tin
# TZ của cron):
#   (a) tháng ∈ {1,4,7,10} (tháng đầu quý)
#   (b) ngày ≥ 15 — không cần check "≤ ngày cuối tháng" vì một date hợp lệ không bao giờ
#       vượt quá số ngày thật của tháng đó (kể cả năm nhuận); cửa sổ tự đóng khi sang tháng
#       sau vì (a) fail.
#   (c) không phải lễ VN theo vn_market.is_holiday() — KHÔNG còn loại cuối tuần (sửa
#       2026-07-23: user xác nhận qua bq_admin rằng ticker_financial vẫn được cập nhật cả
#       Thứ Bảy/Chủ Nhật trong mùa BCTC, nên bỏ lỡ cuối tuần chỉ làm cohort chậm 1-2 ngày vô ích).
#       ⚠️ HẠN CHẾ ĐÃ BIẾT: vn_market chỉ encode lễ CỐ ĐỊNH (01/01, 30/04, 01/05, 02/09);
#       lễ biến động (Tết ÂL — có thể rơi vào cửa sổ tháng 1 — Giỗ Tổ, nghỉ bù) chưa khai
#       báo (_VARIABLE_HOLIDAYS rỗng). Best-effort: ngày Tết script vẫn chạy — vô hại
#       (chỉ tốn 1 lần refresh trên dữ liệu không đổi), KHÔNG giả vờ hoàn hảo.
#       30/04 rơi đúng cửa sổ tháng 4 → được skip đúng.
#
# Nếu điều kiện sai → no-op im lặng: chỉ log 1 dòng skip-reason, không alert.
# Nếu đúng → chạy refresh_fa_ratings_8l.sh, rồi đợi đủ 45' kể từ lúc bắt đầu (giữ nguyên
# spacing như mẫu thứ Bảy 08:30→09:15 và thứ Ba tạm 20:00→20:45) rồi chạy refresh_fa_ratings.sh.
# Hai wrapper con tự verify artifact (bq show lastModified+numRows) + tự alert khi fail.
#
# 4 câu hỏi cron_registry.md: xem entry 20:00 (mùa BCTC) trong mike/kb/cron_registry.md.
set -uo pipefail

ROOT="/home/trido/thanhdt/WorkingClaude"
MIKE="$ROOT/mike"
LOG_8L="$MIKE/logs/fa_ratings_8l_refresh.log"
LOG_FA="$MIKE/logs/fa_ratings_refresh.log"
SPACING_S=2700   # 45 phút giữa lúc BẮT ĐẦU 8l và lúc bắt đầu fa_ratings

# --check YYYY-MM-DD: chỉ in RUN/SKIP cho ngày mô phỏng, không chạy gì (dùng để test logic).
CHECK_DATE="${2:-}"
MODE="${1:-run}"

_gate() {  # $1 = YYYY-MM-DD hoặc rỗng (= hôm nay ICT). In "RUN" hoặc "SKIP: <lý do>".
  python3 - "$1" <<'PY'
import sys, datetime as dt
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from trading_bot.vn_market import today_ict, is_holiday
arg = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else ""
d = dt.date.fromisoformat(arg) if arg else today_ict()
reasons = []
if d.month not in (1, 4, 7, 10):
    reasons.append(f"month={d.month} khong phai thang dau quy")
if d.day < 15:
    reasons.append(f"day={d.day} < 15")
if is_holiday(d):
    reasons.append("le VN (fixed-list; le bien dong nhu Tet CHUA encode — best-effort)")
print("RUN" if not reasons else "SKIP: " + "; ".join(reasons))
PY
}

if [ "$MODE" = "--check" ]; then
  _gate "$CHECK_DATE"
  exit 0
fi

TODAY_ICT="$(TZ='Asia/Ho_Chi_Minh' date +'%F %T ICT')"
GATE="$(_gate "")"
if [ "$GATE" != "RUN" ]; then
  echo "[$TODAY_ICT] $GATE"
  exit 0
fi

echo "[$TODAY_ICT] RUN — trong cua so mua BCTC (15..het thang dau quy, moi ngay ke ca cuoi tuan, tru le VN)"
START_EPOCH="$(date +%s)"

"$MIKE/bin/refresh_fa_ratings_8l.sh" >> "$LOG_8L" 2>&1
RC1=$?
echo "[$(TZ='Asia/Ho_Chi_Minh' date +'%F %T ICT')] refresh_fa_ratings_8l.sh exit=$RC1 (chi tiet: $LOG_8L)"

# Đợi cho đủ 45' kể từ START (nếu 8l chạy lâu hơn 45' thì chạy fa_ratings ngay).
ELAPSED=$(( $(date +%s) - START_EPOCH ))
WAIT=$(( SPACING_S - ELAPSED ))
[ "$WAIT" -gt 0 ] && sleep "$WAIT"

"$MIKE/bin/refresh_fa_ratings.sh" >> "$LOG_FA" 2>&1
RC2=$?
echo "[$(TZ='Asia/Ho_Chi_Minh' date +'%F %T ICT')] refresh_fa_ratings.sh exit=$RC2 (chi tiet: $LOG_FA)"

# Wrapper con đã tự alert khi fail — ở đây chỉ trả exit code tổng hợp cho log.
[ "$RC1" -eq 0 ] && [ "$RC2" -eq 0 ] && exit 0 || exit 1
