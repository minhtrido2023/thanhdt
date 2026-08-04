#!/usr/bin/env bash
# paper_main_early_check.sh — phát hiện SỚM khi paper-main (probe harness cho EXTREME-regime
# gate + vol-scale chase-cap + fill-timing) không sinh evidence thật, thay vì chỉ biết qua báo
# cáo EOD 15:20 hay khi user hỏi. Chạy ~30' sau mỗi cron executor (09:10 sáng / 13:05 chiều ICT).
#
# Gốc sự cố 2026-07-08/09: ghost-guard/TZ bug khiến journal tồn tại nhưng 0 lệnh thật cả 2
# ngày liền — không ai biết cho tới khi user hỏi trực tiếp 07-09 chiều. Script này đóng đúng
# gap đó cho tương lai: kiểm tra journal hôm nay CÓ PLACE/FILL/DONE thật chưa, báo Discord
# ngay nếu KHÔNG — đủ sớm trong ngày để còn kịp chẩn đoán + sửa trước khi hết phiên.
#
# SỬA 2026-08-04 (đính chính bản sửa 08-03 — sau khi bản đó lại tự tạo ra đúng loại lỗi nó
# định chống): bản 08-03 coi "netting hôm nay khớp về 0" là hành vi ĐÚNG thiết kế nên im lặng
# hoàn toàn (exit 0) — đúng cho MỘT tài khoản THẬT (SpaceX/ZaloPay có thể hợp lệ có ngày 0 lệnh).
# Nhưng "main" KHÔNG PHẢI tài khoản thật — nó CHỈ tồn tại để sinh evidence (paper_main_probe_plan.py:
# "Mục đích duy nhất: đảm bảo executor chạy phiên paper `main` MỖI ngày ... để 2-3 chương trình
# paper tích lũy evidence"). Với account NÀY, "netted về 0" KHÔNG BAO GIỜ là chuyện bình thường —
# nó luôn có nghĩa "hôm nay 0 evidence cho mọi chương trình paper phụ thuộc harness này". Im lặng
# hoàn toàn (như bản 08-03) đã khiến netting production (commit ab20a77, 07-27) giết evidence của
# CẢ 3 chương trình 8 NGÀY LIỀN (07-28→08-04) mà không ai biết — chỉ lộ ra khi Taylor tự đào sâu
# lúc làm checkpoint review (job Taylor_20260804_091700/091703), không phải qua alert nào.
# Xem kb/incidents/2026-08/2026-08-04-paper-main-netted-evidence-silent-8-days.md.
#
# Bản sửa này KHÔNG quay lại RED-mỗi-ngày (đó là bug gốc 08-03 phàn nàn) — thay vào đó LUÔN báo
# (không còn nhánh im lặng), mức độ tăng dần theo streak liên tiếp: ngày 1 = ⚠️ WARN (đủ để thấy,
# không đủ để gây mệt mỏi cảnh báo giả 1 lần), streak ≥2 ngày = 🔴 RED (không còn là ngẫu nhiên).
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"

TRADING_DAILY_THREAD="trading_daily"
TODAY="$(TZ=Asia/Ho_Chi_Minh date +%Y-%m-%d)"
NOW_ICT="$(TZ=Asia/Ho_Chi_Minh date +'%H:%M ICT')"
SESSION="${1:-morning}"   # morning | afternoon — chỉ để hiển thị trong message

PLAN_FILE="$WC_ROOT/data/trade_plans/plan_main_${TODAY}.json"
JOURNAL="$WC_ROOT/data/execution_logs/exec_main_${TODAY}_journal.csv"
RUNBOT_SUFFIX=""
[ "$SESSION" = "afternoon" ] && RUNBOT_SUFFIX="_afternoon"
RUNBOT_LOG="$ROOT/logs/run_bot_main_${TODAY}${RUNBOT_SUFFIX}.log"
STREAK_STATE="$ROOT/state/paper_main_zero_evidence_streak.json"
mkdir -p "$ROOT/state"
[ -f "$STREAK_STATE" ] || echo '{"streak": 0, "last_zero_date": null}' > "$STREAK_STATE"

_notify() {
  "$ROOT/bin/notify_thread.sh" "$1" "$TRADING_DAILY_THREAD" 2>/dev/null || true
}

_bump_streak() {
  python3 -c "
import json
p = '$STREAK_STATE'
s = json.load(open(p))
if s.get('last_zero_date') != '$TODAY':
    s['streak'] = s.get('streak', 0) + 1
    s['last_zero_date'] = '$TODAY'
    json.dump(s, open(p, 'w'), indent=1)
print(s['streak'])
"
}

_reset_streak() {
  echo '{"streak": 0, "last_zero_date": null}' > "$STREAK_STATE"
}

# Không có probe plan hôm nay (vd lỗi paper_main_probe_plan.py) → tự nó đã là bất thường,
# vì cron này chạy T2-T6 nên LUÔN phải có plan.
if [ ! -f "$PLAN_FILE" ]; then
  _notify "🔴 **paper-main early-check ($SESSION, $NOW_ICT)** — KHÔNG có plan hôm nay ($PLAN_FILE thiếu). paper_main_probe_plan.py (cron 08:52 ICT) có thể đã lỗi — kiểm tra mike/logs/paper_main_probe_plan.log."
  exit 1
fi

if [ ! -f "$JOURNAL" ]; then
  # "netted về 0" (run_bot's own log tự xác nhận) là hành vi ĐÚNG THIẾT KẾ cho 1 tài khoản THẬT,
  # nhưng "main" chỉ tồn tại để sinh evidence — KHÔNG được im lặng nữa (xem đính chính ở đầu file).
  IS_NETTED_ZERO=0
  if [ -f "$RUNBOT_LOG" ] && grep -q "không phải lỗi, chỉ là ngày không giao dịch" "$RUNBOT_LOG" 2>/dev/null; then
    IS_NETTED_ZERO=1
  fi

  if [ "$IS_NETTED_ZERO" = "1" ]; then
    STREAK="$(_bump_streak)"
    if [ "$STREAK" -ge 2 ]; then
      _notify "🔴 **paper-main early-check ($SESSION, $NOW_ICT)** — ${STREAK} ngày LIÊN TIẾP netting khớp lệnh về 0 (không phải crash — run_bot tự xác nhận), nghĩa là evidence cho EXTREME-regime/vol-scale-chase-cap/fill-timing ĐỨNG YÊN ${STREAK} ngày. Đây không còn là hiện tượng ngẫu nhiên, cần kiểm tra basket SELL/BUY của paper_main_probe_plan.py có bị net hết bởi net_offsetting_orders() không."
    else
      _notify "⚠️ **paper-main early-check ($SESSION, $NOW_ICT)** — netting khớp lệnh hôm nay về 0 (run_bot xác nhận không phải crash), 0 evidence hôm nay cho EXTREME-regime/vol-scale-chase-cap/fill-timing. Ngày đầu tiên trong streak — sẽ báo RED nếu lặp lại ngày mai."
    fi
  else
    _reset_streak
    _notify "🔴 **paper-main early-check ($SESSION, $NOW_ICT)** — có plan nhưng KHÔNG có journal ($JOURNAL thiếu), và log run_bot ($RUNBOT_LOG) không tự xác nhận đây là ngày 0-lệnh-hợp-lệ. Executor có thể chưa chạy/chết ngay khi khởi động — kiểm tra $RUNBOT_LOG."
  fi
  exit 1
fi

HAS_REAL="$(python3 -c "
import csv
try:
    with open('$JOURNAL', encoding='utf-8') as f:
        print('yes' if any(r.get('event') in ('PLACE','FILL','DONE') for r in csv.DictReader(f)) else 'no')
except OSError:
    print('no')
" 2>/dev/null || echo no)"

if [ "$HAS_REAL" != "yes" ]; then
  GHOST_COUNT="$(grep -c ',GHOST_ORDER,' "$JOURNAL" 2>/dev/null || echo 0)"
  _notify "🔴 **paper-main early-check ($SESSION, $NOW_ICT)** — journal tồn tại nhưng 0 lệnh PLACE/FILL/DONE thật (GHOST_ORDER: $GHOST_COUNT dòng). Đây đúng dấu hiệu sự cố 07-08/09 (ghost-guard/TZ) — evidence cho EXTREME-regime gate + vol-scale chase-cap hôm nay = 0, không tính vào tiến độ. Cần kiểm tra ngay, đừng đợi báo cáo EOD 15:20."
  exit 1
fi

# Healthy — reset streak netting-zero (evidence đã chảy lại), im lặng (không cần báo mỗi lần OK,
# theo quiet-heartbeat convention).
_reset_streak
exit 0
