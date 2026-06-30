#!/usr/bin/env bash
# run_bot.sh — deterministic execution wrapper cho bot_execute.py.
# Thay thế headless LLM dispatch cho các tác vụ trading thực tế (placement, fills).
#
# Usage:
#   bin/run_bot.sh [--account LABEL] [--date YYYY-MM-DD] [--auto-otp] [--dry-run]
#
# bot_execute.py tự publish events lên Mike fleet bus (STEP_FAIL, fill_lagging).
# Wrapper này thêm: start/end Discord notify + bus event.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"

ACCOUNT="SpaceX"
PLAN_DATE="$(date +%Y-%m-%d)"
AUTO_OTP=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --account) ACCOUNT="$2"; shift 2 ;;
    --date)    PLAN_DATE="$2"; shift 2 ;;
    --auto-otp) AUTO_OTP=true; shift ;;
    --dry-run)  DRY_RUN=true; shift ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

_tid="$(cat "$ROOT/agents/Mike/state/ccdb_thread_id" 2>/dev/null || true)"
_discord() {
  [ -n "${_tid:-}" ] || return 0
  "$ROOT/bin/notify_thread.sh" "$1" "$_tid" 2>/dev/null || true
}

LOG="$ROOT/logs/run_bot_${ACCOUNT}_${PLAN_DATE}.log"
mkdir -p "$ROOT/logs"

ts_start="$(date +%s)"
_discord "🤖 **bot_execute** khởi động — account **$ACCOUNT** plan $PLAN_DATE (auto-otp=$AUTO_OTP). Log: $LOG"

"$ROOT/bin/append_event.sh" Mafee status "bot-start" \
  "{\"account\":\"$ACCOUNT\",\"plan_date\":\"$PLAN_DATE\",\"auto_otp\":$AUTO_OTP}" 2>/dev/null || true

if [ "$DRY_RUN" = true ]; then
  echo "[DRY-RUN] would run: python bot_execute.py --account $ACCOUNT $([ "$AUTO_OTP" = true ] && echo '--auto-otp')"
  _discord "🔍 DRY-RUN — không thực thi lệnh thật."
  exit 0
fi

set +e
cd "$WC_ROOT"
OTP_FLAG=""
[ "$AUTO_OTP" = true ] && OTP_FLAG="--auto-otp"
# shellcheck disable=SC2086
python bot_execute.py --account "$ACCOUNT" --date "$PLAN_DATE" $OTP_FLAG \
  2>&1 | tee -a "$LOG"
rc=${PIPESTATUS[0]}
set -e

ts_end="$(date +%s)"
elapsed=$(( ts_end - ts_start ))

if [ "$rc" -eq 0 ]; then
  tail_preview="$(tail -c 300 "$LOG" 2>/dev/null | tr '\n' ' ')"
  _discord "✅ **bot_execute** xong (${elapsed}s) — account **$ACCOUNT** $PLAN_DATE. Preview: $tail_preview"
  "$ROOT/bin/append_event.sh" Mafee status "bot-done" \
    "{\"account\":\"$ACCOUNT\",\"plan_date\":\"$PLAN_DATE\",\"elapsed_s\":$elapsed,\"rc\":0}" 2>/dev/null || true
else
  tail_preview="$(tail -c 300 "$LOG" 2>/dev/null | tr '\n' ' ')"
  _discord "❌ **bot_execute** THẤT BẠI (rc=$rc, ${elapsed}s) — account **$ACCOUNT** $PLAN_DATE. Xem: $LOG. Preview: $tail_preview"
  "$ROOT/bin/append_event.sh" Mafee error "bot-fail" \
    "{\"account\":\"$ACCOUNT\",\"plan_date\":\"$PLAN_DATE\",\"elapsed_s\":$elapsed,\"rc\":$rc,\"log\":\"$LOG\"}" 2>/dev/null || true
fi

"$ROOT/bin/consolidate.sh" >> "$ROOT/logs/consolidator.log" 2>&1 || true
exit "$rc"
