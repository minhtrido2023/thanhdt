#!/usr/bin/env bash
# bot_heartbeat.sh <account> [plan_date] [thread_id]
# Giám sát bot_execute.py trong giờ giao dịch — chạy qua cron mỗi 5' 09:00-15:00 ICT T2-T6.
# Báo Discord: (a) BOT DIE nếu process không còn sống, (b) digest lệnh mới (PLACE/FILL/DONE/
# PLACE_FAIL) từ journal kể từ lần check trước, (c) heartbeat im lặng (không tin mới) nếu
# process sống nhưng chưa có event mới.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"
[ -f "$WC_ROOT/wc_env.sh" ] && source "$WC_ROOT/wc_env.sh" 2>/dev/null || true

ACCOUNT="${1:?usage: bot_heartbeat.sh <account> [plan_date] [thread_id]}"
PLAN_DATE="${2:-$(TZ=Asia/Ho_Chi_Minh date +%Y-%m-%d)}"
THREAD_ID="${3:-$(cat "$ROOT/agents/Mike/state/ccdb_thread_id" 2>/dev/null || echo '')}"

JOURNAL="$WC_ROOT/data/execution_logs/exec_${ACCOUNT}_${PLAN_DATE}_journal.csv"
STATE_DIR="$ROOT/state/bot_heartbeat"
mkdir -p "$STATE_DIR"
LASTLINE_FILE="$STATE_DIR/${ACCOUNT}_${PLAN_DATE}.lastline"
DEADFLAG_FILE="$STATE_DIR/${ACCOUNT}_${PLAN_DATE}.dead_notified"

NOW_ICT="$(TZ=Asia/Ho_Chi_Minh date +'%H:%M ICT')"
NOW_HHMM="$(TZ=Asia/Ho_Chi_Minh date +'%H%M')"

_notify() {
  [ -n "$THREAD_ID" ] || { echo "$1"; return; }
  "$ROOT/bin/notify_thread.sh" "$1" "$THREAD_ID" 2>/dev/null || true
}

# ── 1. Process liveness ──────────────────────────────────────────────────────
PID="$(pgrep -f "bot_execute.py --account $ACCOUNT --date $PLAN_DATE" | head -1 || true)"

if [ -z "$PID" ]; then
  # After 14:50 ICT, market is closed — process exiting on its own is normal, not a DIE alert.
  if [ "$NOW_HHMM" -ge 1450 ] || [ "$NOW_HHMM" -lt 0900 ]; then
    exit 0
  fi
  if [ ! -f "$DEADFLAG_FILE" ]; then
    _notify "🔴 **BOT DIE** — bot_execute.py account **$ACCOUNT** ($PLAN_DATE) KHÔNG còn chạy lúc $NOW_ICT (còn trong giờ giao dịch). Lệnh chưa khớp sẽ không được theo dõi/cancel-stale. Cần restart ngay (setsid, không nohup+Bash-tool)."
    touch "$DEADFLAG_FILE"
  fi
  exit 1
fi
rm -f "$DEADFLAG_FILE"

# ── 2. Journal delta since last check ────────────────────────────────────────
if [ ! -f "$JOURNAL" ]; then
  _notify "⚠️ [$NOW_ICT] bot $ACCOUNT PID=$PID đang sống nhưng chưa có journal file."
  exit 0
fi

LAST="$(cat "$LASTLINE_FILE" 2>/dev/null || echo 0)"
TOTAL="$(wc -l < "$JOURNAL" | tr -d ' ')"

if [ "$TOTAL" -le "$LAST" ]; then
  # No new events — silent heartbeat every 5' (only text, no Discord spam beyond schedule)
  _notify "🟢 [$NOW_ICT] bot $ACCOUNT sống (PID $PID), không có event mới từ lần check trước."
  echo "$TOTAL" > "$LASTLINE_FILE"
  exit 0
fi

DELTA="$(tail -n "+$((LAST + 1))" "$JOURNAL")"
echo "$TOTAL" > "$LASTLINE_FILE"

DONE_LINES="$(echo "$DELTA" | grep ',DONE,' || true)"
FAIL_LINES="$(echo "$DELTA" | grep ',PLACE_FAIL,' || true)"
PLACE_LINES="$(echo "$DELTA" | grep ',PLACE,' || true)"

N_DONE="$(echo "$DONE_LINES" | grep -c . || true)"
N_FAIL="$(echo "$FAIL_LINES" | grep -c . || true)"
N_PLACE="$(echo "$PLACE_LINES" | grep -c . || true)"

DONE_TICKERS="$(echo "$DONE_LINES" | awk -F, '{print $4}' | sort -u | tr '\n' ',' | sed 's/,$//')"
FAIL_TICKERS="$(echo "$FAIL_LINES" | awk -F, '{print $4}' | sort -u | tr '\n' ',' | sed 's/,$//')"

MSG="🟢 [$NOW_ICT] bot $ACCOUNT PID=$PID — $N_PLACE lệnh mới đặt, $N_DONE khớp xong"
[ -n "$DONE_TICKERS" ] && MSG="$MSG (${DONE_TICKERS})"
if [ "$N_FAIL" -gt 0 ]; then
  MSG="$MSG; ⚠ $N_FAIL PLACE_FAIL (${FAIL_TICKERS})"
fi

# Overall progress snapshot
TOTAL_ORDERS="$(grep -c '^2026-\|,PLACE,' "$JOURNAL" 2>/dev/null || true)"
DONE_ALL="$(awk -F, '$2=="DONE"{print $4}' "$JOURNAL" | sort -u | wc -l | tr -d ' ')"
MSG="$MSG. Tổng đã khớp: ${DONE_ALL} tickers."

_notify "$MSG"
