#!/usr/bin/env bash
# nav_snapshot_daily.sh — ghi nav_history_<account>.csv cho MỌI account live, MỌI phiên, ĐỘC LẬP
# với eod_trading_report.sh (aria-G, job Wags_20260913_064538, user duyệt 13/09).
#
# Vì sao: eod_trading_report.sh chỉ gọi daily_nav_snapshot.py ở case HOLD (dòng ~249) và case
# render đầy đủ (dòng ~595). Mọi lối thoát sớm TRƯỚC đó bỏ qua NAV hoàn toàn — không có plan file
# (case 1, `exit $?` dòng ~243, ca 08-25) / có lệnh nhưng không có state file (case 3, dòng ~271,
# ca 08-07) — cộng rc=2 (DNSE timeout) không ai retry ⇒ 3/11 + 2 phiên thiếu dòng NAV (Taylor
# aria-A2). Cron này là đường ghi THỨ HAI; EOD wrapper giữ nguyên lệnh gọi của nó.
#
# Hợp đồng (không đổi logic tính NAV — chỉ điều phối quanh daily_nav_snapshot.py):
# - Idempotent: nav_history đã có dòng hôm nay ⇒ BỎ QUA, không gọi lại, không ghi đè. Cron chạy
#   SAU EOD (EOD ghi xong ~19:10:40, đo 8 phiên) nên ngày EOD đã ghi thì lượt này là no-op ⇒ hai
#   đường không bao giờ cho 2 kết quả cùng ngày. EOD của CÂY NÀY còn chạy ⇒ chờ nó xong trước.
# - Marker nav_pending_retry/<account>_<today>.log (hoặc .stuck_*) ⇒ BỎ QUA: đó là việc của
#   nav_sync_retry.sh (rc=4), không chạy song song trên cùng account.
# - rc=2 (thiếu dữ liệu/timeout DNSE) hoặc treo quá NAV_SNAPSHOT_PY_TIMEOUT_S ⇒ retry tối đa 2 VÒNG
#   cách 5' (vòng ngoài = lần thử, vòng trong = account ⇒ tổng ngủ ≤10' dù bao nhiêu account);
#   hết retry ⇒ báo Trading Daily.
# - rc=3 (sanity guard) ⇒ không retry, báo Trading Daily (daily_nav_snapshot đã tự chặn ghi).
# - rc=4 (PRICE_XCHECK) ⇒ không ghi, tạo marker cùng định dạng EOD để nav_sync_retry.sh tự retry
#   tới 21:15 ICT rồi escalate — tái dùng cơ chế sẵn có, không dựng cơ chế retry thứ hai.
# - Chỉ ngày HÔM NAY (ICT) và chỉ phiên giao dịch: đường live của daily_nav_snapshot.py luôn đọc
#   vị thế broker HIỆN TẠI ⇒ chạy cho ngày cũ là ghi số sai âm thầm (backfill dùng --from-raw).
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"
if [ -f "$WC_ROOT/wc_env.sh" ]; then
  # shellcheck source=/dev/null
  source "$WC_ROOT/wc_env.sh"
fi

TODAY="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)"
EXEC_DIR="$WC_ROOT/data/execution_logs"
MARKER_DIR="$ROOT/state/nav_pending_retry"
RETRY_SLEEP_S="${NAV_SNAPSHOT_RETRY_SLEEP_S:-300}"
PY_TIMEOUT_S="${NAV_SNAPSHOT_PY_TIMEOUT_S:-180}"   # chạy thường ~30s (EOD đo 19:10:07→19:10:36)
EOD_WAIT_MAX_S="${NAV_SNAPSHOT_EOD_WAIT_MAX_S:-600}"
EOD_POLL_S="${NAV_SNAPSHOT_EOD_POLL_S:-30}"
MAX_RETRIES=2
log() { echo "[nav_snapshot_daily $(TZ='Asia/Ho_Chi_Minh' date +'%F %T')] $*"; }
# Lỗi gửi ⇒ literal NOTIFY_FAILED để cron_health_check.py bắt được (không chìm trong log).
notify_daily() { "$ROOT/bin/notify_thread.sh" "$1" "trading_daily" >/dev/null 2>&1 || echo "NOTIFY_FAILED: nav_snapshot_daily → trading_daily: $1"; }

# Chạy trùng (cron + tay) ⇒ lượt sau thoát êm. Lượt trước không treo mãi được: python có timeout.
mkdir -p "$ROOT/state" "$MARKER_DIR"
exec 9>"$ROOT/state/nav_snapshot_daily.lock"
if ! flock -n 9; then
  log "lượt khác đang chạy — bỏ qua."
  exit 0
fi

# Guard ngày giao dịch (cùng luật eod_trading_report.sh:32-43). Lỗi import ⇒ fail-open (cron 1-5
# đã chặn cuối tuần; daily_nav_snapshot tự gác dữ liệu).
if _nt="$(cd "$WC_ROOT" && python3 -c "
import sys, datetime as dt
sys.path.insert(0, '.')
from trading_bot.vn_market import is_holiday
d = dt.date.fromisoformat('$TODAY')
print('1' if d.weekday() >= 5 or is_holiday(d) else '0')
" 2>/dev/null)" && [ "$_nt" = "1" ]; then
  log "$TODAY không phải phiên giao dịch — bỏ qua."
  exit 0
fi

LABELS="$(cd "$WC_ROOT" && python3 -c "from trading_bot.config import live_dnse_labels; print(' '.join(live_dnse_labels()))")"
if [ $? -ne 0 ] || [ -z "$LABELS" ]; then
  echo "❌ nav_snapshot_daily $TODAY: KHÔNG đọc được danh sách account live — dừng."   # không qua log(): cron_health neo ^\s*❌
  notify_daily "🔴 nav_snapshot_daily $TODAY: không đọc được danh sách account live (trading_bot.config) — NAV hôm nay CHƯA được ghi bởi cron độc lập."
  exit 1
fi

# EOD của CHÍNH cây này đang chạy ⇒ chờ nó ghi xong (nó là writer chính). Neo pattern vào argv
# thật của tiến trình bash (`bash <ROOT>/bin/eod_trading_report.sh …`, hoặc for_each_live_account
# đang giữa 2 account) — `pgrep -f` trần khớp cả prompt `claude -p` nhắc tới đường dẫn này
# (arch-review aria-G vòng 1, tái hiện thật). Quá trần vẫn tiếp tục: thiếu NAV tệ hơn, và guard
# dòng-đã-có bên dưới vẫn chặn ghi đè nếu EOD kịp ghi.
ROOT_RE="$(printf '%s' "$ROOT" | sed 's/[.[\*^$()+?{|]/\\&/g')"
EOD_RE="^bash ${ROOT_RE}/bin/(for_each_live_account\.sh ${ROOT_RE}/bin/)?eod_trading_report\.sh( |$)"
waited=0
while pgrep -f "$EOD_RE" >/dev/null 2>&1 && [ "$waited" -lt "$EOD_WAIT_MAX_S" ]; do
  sleep "$EOD_POLL_S"; waited=$((waited + EOD_POLL_S))
done
[ "$waited" -gt 0 ] && log "đã chờ EOD ${waited}s."

has_row() {  # $1=account — nav_history đã có dòng TODAY?
  local f="$EXEC_DIR/nav_history_$1.csv"
  [ -f "$f" ] && awk -F, -v d="$TODAY" 'NR>1 && $1==d {found=1} END {exit !found}' "$f"
}

declare -A RC_OF LAST_OUT
PENDING="$LABELS"
overall=0
for attempt in $(seq 0 "$MAX_RETRIES"); do
  if [ "$attempt" -gt 0 ]; then
    log "retry $attempt/$MAX_RETRIES cho [$PENDING] sau ${RETRY_SLEEP_S}s."
    sleep "$RETRY_SLEEP_S"
  fi
  NEXT=""
  for ACCOUNT in $PENDING; do
    # Kiểm lại MỖI vòng: EOD/nav_sync_retry có thể đã ghi hoặc đặt marker trong lúc ngủ.
    if has_row "$ACCOUNT"; then
      log "$ACCOUNT: đã có dòng $TODAY — bỏ qua (idempotent)."
      RC_OF[$ACCOUNT]=skip; continue
    fi
    if compgen -G "$MARKER_DIR/${ACCOUNT}_${TODAY}.*" >/dev/null; then
      log "$ACCOUNT: đang có marker nav_pending_retry — để nav_sync_retry.sh xử lý."
      RC_OF[$ACCOUNT]=skip; continue
    fi
    OUT="$(timeout "$PY_TIMEOUT_S" python3 "$ROOT/bin/daily_nav_snapshot.py" --account "$ACCOUNT" --date "$TODAY" 2>&1)"
    RC=$?
    OUT="$(printf '%s\n' "$OUT" | grep -v '^\[dnse\]')"
    [ "$RC" = "124" ] && OUT="(timeout ${PY_TIMEOUT_S}s)"$'\n'"$OUT"
    log "$ACCOUNT: rc=$RC (lần thử $attempt)"
    RC_OF[$ACCOUNT]=$RC
    case "$RC" in
      0)
        printf '%s\n' "$OUT"
        if has_row "$ACCOUNT"; then
          notify_daily "✅ NAV $ACCOUNT ($TODAY) được ghi bởi cron độc lập nav_snapshot_daily (EOD không ghi hôm nay):
$(printf '%s\n' "$OUT" | grep -m1 'NAV')"
        else
          log "$ACCOUNT: rc=0 nhưng không có dòng (chưa có ngày giao dịch nào) — không làm gì."
        fi
        ;;
      4)
        # Không in raw (dòng "❌ … LỆCH") vào log: ca tự hết, cron_health sẽ báo ERRORS_FOUND giả
        # 10 ngày. Chi tiết nằm trong marker.
        printf '%s\n' "$OUT" > "$MARKER_DIR/${ACCOUNT}_${TODAY}.log"
        log "$ACCOUNT: rc=4 PRICE_XCHECK — chi tiết ở marker, giao nav_sync_retry.sh."
        notify_daily "⏳ NAV $ACCOUNT ($TODAY) tạm hoãn (rc=4 PRICE_XCHECK) — nav_sync_retry.sh tự retry tới 21:15 ICT rồi escalate."
        ;;
      2|124)
        # Chỉ in raw ở lần thử CUỐI (vòng dưới): blip DNSE đã tự hồi không được để lại ❌ trong log.
        LAST_OUT[$ACCOUNT]="$OUT"
        NEXT="$NEXT $ACCOUNT"
        ;;
      *)
        printf '%s\n' "$OUT"
        ;;
    esac
  done
  PENDING="${NEXT# }"
  [ -z "$PENDING" ] && break
done

for ACCOUNT in $LABELS; do
  rc="${RC_OF[$ACCOUNT]:-skip}"
  case "$rc" in
    skip|0|4) ;;
    *)
      overall=1
      [ -n "${LAST_OUT[$ACCOUNT]:-}" ] && [ "$rc" != 3 ] && printf '%s\n' "${LAST_OUT[$ACCOUNT]}"
      echo "❌ nav_snapshot_daily $TODAY $ACCOUNT: NAV KHÔNG ghi được (rc=$rc)."   # không qua log(): cron_health neo ^\s*❌
      notify_daily "🔴 NAV $ACCOUNT ($TODAY) KHÔNG ghi được (rc=$rc$( [ "$rc" = 2 ] || [ "$rc" = 124 ] && echo ", sau $MAX_RETRIES vòng retry")) — cần kiểm tra tay, xem logs/nav_snapshot_daily.log + kb/ops_runbook.md § NAV thiếu dòng."
      ;;
  esac
done
exit "$overall"
