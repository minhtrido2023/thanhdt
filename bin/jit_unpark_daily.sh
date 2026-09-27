#!/usr/bin/env bash
# jit_unpark_daily.sh — L2 JIT-unpark cho MỌI account live. Ghi artifact
# data/trade_plans/jit_unpark_<account>_<plan_date>.json (plan_date = T+1).
#
# Vị trí trong chuỗi (19:40 ICT): DollarBill ghi plan ~19:0x → park_trim_daily.sh 19:30 →
# [L2 ĐÂY 19:40] → merge_park_daily.sh 20:20 → inject_discretionary_orders.sh 20:30 →
# send_plan_report.sh 21:00. Script CHỈ ĐỌC; không đặt lệnh, không ghi plan.
#
# FAIL-CLOSED trên L1: thiếu artifact park_trim_<acct>_<plan_date>.json ⇒ BỎ QUA account đó với
# rc≠0, KHÔNG chạy L2 "trần trụi". Lý do là kế toán, không phải cẩn thận thừa: `--l1-json` là
# thứ trừ trước phần trần TỔNG/phiên + số cổ phiếu mà L1 đã đề xuất bán; thiếu nó,
# compute_jit_unpark.py "coi như L1 không chạy" (help của chính cờ đó) ⇒ hai tầng cùng tiêu một
# lần dư địa ⇒ đề xuất bán vượt trần thật.
#
# --plan PHẢI truyền tường minh: mặc định của compute_jit_unpark.py là
# plan_<account>_<asof>.json với asof = HÔM NAY, tức plan đã thực thi xong, KHÔNG phải plan T+1.
#
# RÀNG BUỘC CỨNG sau 15:00 ICT + ngày giao dịch: giống park_trim_daily.sh (L2 dùng lại đúng
# đường giá live của L1). Guard cưỡng chế bằng code ở dưới.
#
# Cài 2026-08-14 (job Taylor_20260814_142151) theo §6 mà user duyệt trong
# mike/agents/Taylor/research/park_merge_wire_20260811.md. Xem mike/kb/cron_registry.md.
#
# Test không đụng production: PARK_CHAIN_PLAN_DIR=<thư mục sandbox> ./jit_unpark_daily.sh
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"
# shellcheck source=/dev/null
[ -f "$WC_ROOT/wc_env.sh" ] && source "$WC_ROOT/wc_env.sh" 2>/dev/null || true
PY="${DNA_PYEXE:-python3}"
PLAN_DIR="${PARK_CHAIN_PLAN_DIR:-$WC_ROOT/data/trade_plans}"
NOW_ICT="$(TZ='Asia/Ho_Chi_Minh' date +'%F %H:%M ICT')"

EXTRA_ARGS="${1:-}"   # cho phép truyền --json khi test

PLAN_DATE="$(cd "$WC_ROOT" && python3 -c "
import sys
from trading_bot.vn_market import now_ict, today_ict, is_holiday, next_trading_day
n = now_ict()
if n.weekday() >= 5 or is_holiday(n.date()):
    sys.exit('NOT_TRADING_DAY')
if n.hour < 15:
    sys.exit('BEFORE_1500_ICT')
print(next_trading_day(today_ict()))
" 2>&1)"
case "$PLAN_DATE" in
  NOT_TRADING_DAY) echo "[jit_unpark] $NOW_ICT — hôm nay không phải ngày giao dịch, bỏ qua."; exit 0 ;;
  BEFORE_1500_ICT) echo "[jit_unpark] $NOW_ICT — CHƯA tới 15:00 ICT, TỪ CHỐI chạy (giá đóng cửa chưa có; xem header)." >&2; exit 1 ;;
esac
if [[ ! "$PLAN_DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  echo "[jit_unpark] $NOW_ICT — không tính được ngày plan T+1: $PLAN_DATE" >&2
  exit 1
fi

LIVE_LABELS="$(cd "$WC_ROOT" && python3 -c "from trading_bot.config import live_dnse_labels; print(' '.join(live_dnse_labels()))" 2>/dev/null)"
if [ -z "$LIVE_LABELS" ]; then
  echo "[jit_unpark] $NOW_ICT — không lấy được live labels, dừng." >&2
  exit 1
fi

CHAIN_TAG="jit_unpark"
# ─── rc != 0 PHẢI tới NGƯỜI ─────────────────────────────────────────────────────────────────
# Trước 2026-09-27 mọi lỗi ở đây chỉ `|| rc=1` rồi `>> log 2>&1` của crontab: không Discord,
# không Telegram, không bus ⇒ một trading_rules.json hỏng (compute_park_trim rc=7 fail-closed)
# để sổ PARK nguyên ở mức cũ mà KHÔNG AI BIẾT cho tới khi có người mở log. Fail-closed mà
# không ai nghe thấy thì chỉ đổi một lỗi im lặng thành một lỗi im lặng khác.
# Discord là kênh CHÍNH; notify thất bại ⇒ in LỖI THẬT ra stderr (§29), không nuốt.
# Bus là kênh PHỤ. Tắt khi test: PARK_CHAIN_NO_NOTIFY=1
ALERT_TOPIC="${PARK_CHAIN_ALERT_TOPIC:-trading_daily}"   # TÊN kênh, không ID trần (discord_id_gate)
alert_human() {   # $1 = nhãn ngắn (topic bus)  $2 = nội dung đầy đủ
  if [ -n "${PARK_CHAIN_NO_NOTIFY:-}" ]; then
    echo "[$CHAIN_TAG] (notify TẮT bằng PARK_CHAIN_NO_NOTIFY) $2"
    return 0
  fi
  local _err
  if ! _err="$("$ROOT/bin/notify_thread.sh" "$2" "$ALERT_TOPIC" 2>&1 >/dev/null)"; then
    echo "[$CHAIN_TAG] LỖI: không post được Discord (cảnh báo KHÔNG tới người): $_err" >&2
  fi
  "$ROOT/bin/append_event.sh" Mike error "$1" \
    "{\"chain\":\"$CHAIN_TAG\",\"plan_date\":\"$PLAN_DATE\",\"chi_tiet\":\"xem Discord + log\"}" \
    >/dev/null 2>&1 || echo "[$CHAIN_TAG] (bus không ghi được — Discord vẫn là kênh chính)" >&2
}

rc=0
for ACCT in $LIVE_LABELS; do
  echo "=== [jit_unpark] $ACCT plan_date=$PLAN_DATE — $NOW_ICT ==="
  L1_JSON="$PLAN_DIR/park_trim_${ACCT}_${PLAN_DATE}.json"
  PLAN_JSON="$PLAN_DIR/plan_${ACCT}_${PLAN_DATE}.json"
  if [ ! -f "$L1_JSON" ]; then
    echo "[jit_unpark] $ACCT — THIẾU artifact L1 ($L1_JSON) ⇒ BỎ QUA (fail-closed, xem header)." >&2
    rc=1
    alert_human "park-chain-jit-unpark-missing-l1" \
"🟠 **JIT_UNPARK BỎ QUA** — \`$ACCT\` plan_date \`$PLAN_DATE\` ($NOW_ICT)
THIẾU artifact L1 \`$(basename "$L1_JSON")\` ⇒ fail-closed, KHÔNG rút vốn khỏi sổ PARK.
Nguyên nhân thường gặp: chuỗi 19:30 \`park_trim_daily.sh\` đã thất bại (xem cảnh báo PARK_TRIM cùng tối).
Việc cần làm: đọc \`logs/park_trim_daily.log\` + \`logs/jit_unpark_daily.log\`; lệnh MUA trong plan T+1 có thể thiếu vốn."
    continue
  fi
  if [ ! -f "$PLAN_JSON" ]; then
    echo "[jit_unpark] $ACCT — THIẾU plan T+1 ($PLAN_JSON) ⇒ BỎ QUA (không có lệnh mua nào để cấp vốn)." >&2
    rc=1; continue
  fi
  OUT_LOG="$(mktemp)"
  # shellcheck disable=SC2086  # EXTRA_ARGS cố ý tách từ (cùng khuôn inject_discretionary_orders.sh)
  (cd "$WC_ROOT" && "$PY" mike/bin/compute_jit_unpark.py --account "$ACCT" \
      --plan "$PLAN_JSON" --l1-json "$L1_JSON" \
      --out "$PLAN_DIR/jit_unpark_${ACCT}_${PLAN_DATE}.json" $EXTRA_ARGS) >"$OUT_LOG" 2>&1
  arc=$?
  cat "$OUT_LOG"
  if [ "$arc" -ne 0 ]; then
    rc=$arc
    alert_human "park-chain-jit-unpark-rc" \
"🔴 **JIT_UNPARK THẤT BẠI** — \`$ACCT\` plan_date \`$PLAN_DATE\` ($NOW_ICT)
rc=\`$arc\` từ \`compute_jit_unpark.py\`
\`\`\`
$(tail -n 12 "$OUT_LOG")
\`\`\`
Việc cần làm: đọc \`logs/jit_unpark_daily.log\`; lệnh MUA trong plan T+1 có thể thiếu vốn."
  fi
  rm -f "$OUT_LOG"
done
exit $rc
