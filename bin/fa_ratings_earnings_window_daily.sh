#!/usr/bin/env bash
# fa_ratings_earnings_window_daily.sh — QUY TẮC VĨNH VIỄN mỗi quý (user chỉ đạo 2026-07-14,
# job Winston_20260714_160739; SỬA 2026-07-23 — user xác nhận với bq_admin rằng
# ticker_financial vẫn được cập nhật kể cả cuối tuần, nên bỏ điều kiện T2-T6; MỞ RỘNG CẢ HAI ĐẦU
# 2026-10-13 — user duyệt 19:51 ICT, job Taylor_20261013_125149): trong mùa BCTC — từ ngày 10 của
# THÁNG ĐẦU mỗi quý (1/4/7/10) đến HẾT ngày 10 của THÁNG KẾ TIẾP (2/5/8/11) — re-rate 8L MỖI NGÀY
# TRONG CỬA SỔ, KỂ CẢ CUỐI TUẦN (chỉ trừ lễ VN), vì báo cáo tài chính công bố dồn dập trong cửa sổ
# này và cohort ngày đầu thường chưa đầy đủ.
#
# VÌ SAO NỚI (audit Taylor_20261013_123622, finding M1): cửa sổ cũ 15..hết tháng đầu quý đóng đúng
# lúc nhóm công bố MUỘN ra báo cáo. Mùa Q2/2026: 28/117 sự kiện LAG qualify (toàn bộ nhóm release
# 07-31..08-07) bị cổng 8L≤3 chấm bằng rating QUÝ TRƯỚC lúc lập plan; ca thật TVN (rating Q2=4
# hiệu lực 07-31 nhưng vẫn UPCOMING 08-05/08-06). Đuôi ≤10 tháng kế tiếp phủ T+5 của mã công bố
# muộn + ngày rebalance custom30V (mùng 5 tháng 2/5/8/11). Đầu ≥10 (thay ≥15) bắt nhóm công bố sớm.
#
# Thay thế 2 dòng cron TẠM THỜI thứ Ba (Winston_20260713_103213, guard ≤20260804) — đã xoá
# cùng commit. Dòng thứ Bảy hàng tuần (08:30/09:15) GIỮ NGUYÊN làm baseline quanh năm.
#
# Crontab (server chạy UTC; 10:30 UTC = 17:30 ICT từ 2026-10-13 — trước đó 13:00 UTC = 20:00 ICT; chạy DAILY — gate ngày/tháng nằm ở đây):
#   30 10 * * * /home/trido/thanhdt/WorkingClaude/mike/bin/fa_ratings_earnings_window_daily.sh >> /home/trido/thanhdt/WorkingClaude/mike/logs/fa_ratings_earnings_window.log 2>&1
#
# Điều kiện chạy (tính theo ngày ICT qua trading_bot.vn_market — không tin TZ của cron):
#   (a)+(b) ngày nằm trong CỬA SỔ = một trong hai nhánh:
#         · ĐẦU : tháng ∈ {1,4,7,10} (tháng đầu quý)      ∧ ngày ≥ 10
#         · ĐUÔI: tháng ∈ {2,5,8,11} (tháng thứ hai quý)  ∧ ngày ≤ 10
#       Nhánh ĐẦU không cần check "≤ ngày cuối tháng" vì một date hợp lệ không bao giờ vượt quá
#       số ngày thật của tháng đó (kể cả năm nhuận); 31/01 → 01/02 liền mạch nhờ nhánh ĐUÔI.
#   (c) không phải lễ VN theo vn_market.is_holiday() — KHÔNG còn loại cuối tuần (sửa
#       2026-07-23: user xác nhận qua bq_admin rằng ticker_financial vẫn được cập nhật cả
#       Thứ Bảy/Chủ Nhật trong mùa BCTC, nên bỏ lỡ cuối tuần chỉ làm cohort chậm 1-2 ngày vô ích).
#       ⚠️ HẠN CHẾ ĐÃ BIẾT: vn_market chỉ encode lễ CỐ ĐỊNH (01/01, 30/04, 01/05, 02/09);
#       lễ biến động (Tết ÂL — có thể rơi vào cửa sổ tháng 1 — Giỗ Tổ, nghỉ bù) chưa khai
#       báo (_VARIABLE_HOLIDAYS rỗng). Best-effort: ngày Tết script vẫn chạy — vô hại
#       (chỉ tốn 1 lần refresh trên dữ liệu không đổi), KHÔNG giả vờ hoàn hảo.
#       30/04 rơi đúng cửa sổ tháng 4 và 01/05 rơi đúng nhánh ĐUÔI tháng 5 → được skip đúng.
#
# Nếu điều kiện sai → no-op im lặng: chỉ log 1 dòng skip-reason, không alert.
# Nếu đúng → chạy refresh_fa_ratings_8l.sh, rồi đợi đủ 45' kể từ lúc bắt đầu (giữ nguyên
# spacing như mẫu thứ Bảy 08:30→09:15 và thứ Ba tạm 20:00→20:45) rồi chạy refresh_fa_ratings.sh.
# Hai wrapper con tự verify artifact (bq show lastModified+numRows) + tự alert khi fail.
#
# 4 câu hỏi cron_registry.md: xem entry 17:30 (mùa BCTC) trong mike/kb/cron_registry.md.
# Bộ test gate: bin/fa_ratings_earnings_window_gate_selfcheck.sh (gọi --check, không chạy refresh).
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
# Cửa sổ = [ngày 10 tháng đầu quý .. ngày 10 tháng kế tiếp] (nới cả hai đầu 2026-10-13).
HEAD_MONTHS, TAIL_MONTHS, EDGE_DAY = (1, 4, 7, 10), (2, 5, 8, 11), 10
if d.month in HEAD_MONTHS:
    if d.day < EDGE_DAY:
        reasons.append(f"day={d.day} < {EDGE_DAY} (thang dau quy)")
elif d.month in TAIL_MONTHS:
    if d.day > EDGE_DAY:
        reasons.append(f"day={d.day} > {EDGE_DAY} (thang thu hai quy)")
else:
    reasons.append(f"month={d.month} ngoai cua so mua BCTC")
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

echo "[$TODAY_ICT] RUN — trong cua so mua BCTC (ngay 10 thang dau quy .. ngay 10 thang ke tiep, moi ngay ke ca cuoi tuan, tru le VN)"
START_EPOCH="$(date +%s)"

"$MIKE/bin/refresh_fa_ratings_8l.sh" >> "$LOG_8L" 2>&1
RC1=$?
echo "[$(TZ='Asia/Ho_Chi_Minh' date +'%F %T ICT')] refresh_fa_ratings_8l.sh exit=$RC1 (chi tiet: $LOG_8L)"

# exit 3 = cổng ticker-gate chặn (tav2_bq.ticker thiếu mã): refresh_fa_ratings.sh cũng đọc ticker ⇒ bỏ qua.
if [ "$RC1" -eq 3 ]; then
  echo "[$(TZ='Asia/Ho_Chi_Minh' date +'%F %T ICT')] ticker-gate chan (rc=3) — bo qua refresh_fa_ratings.sh, thu lai o lan cron ke"
  exit 3
fi

# Đợi cho đủ 45' kể từ START (nếu 8l chạy lâu hơn 45' thì chạy fa_ratings ngay).
ELAPSED=$(( $(date +%s) - START_EPOCH ))
WAIT=$(( SPACING_S - ELAPSED ))
[ "$WAIT" -gt 0 ] && sleep "$WAIT"

"$MIKE/bin/refresh_fa_ratings.sh" >> "$LOG_FA" 2>&1
RC2=$?
echo "[$(TZ='Asia/Ho_Chi_Minh' date +'%F %T ICT')] refresh_fa_ratings.sh exit=$RC2 (chi tiet: $LOG_FA)"

# Wrapper con đã tự alert khi fail — ở đây chỉ trả exit code tổng hợp cho log.
[ "$RC1" -eq 0 ] && [ "$RC2" -eq 0 ] && exit 0 || exit 1
