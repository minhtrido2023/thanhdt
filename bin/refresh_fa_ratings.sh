#!/usr/bin/env bash
# refresh_fa_ratings.sh — weekly cron wrapper for `refresh_fa_ratings.py` (append-only
# refresh of tav2_bq.fa_ratings: frozen quarters untouched, 2 open quarters re-ranked,
# new quarters appended once cohort ≥ 30).
#
# Taylor proposal 2026-07-11 (job Taylor_20260711_153405, continuation of feasibility
# job Taylor_20260711_145129) — PENDING user approval; Mike presents the cron diff first.
# Proposed crontab (server runs UTC; = 09:15 ICT Sat, 45' after fa_ratings_8l's 08:30):
#   15 2 * * 6 /home/trido/thanhdt/WorkingClaude/mike/bin/refresh_fa_ratings.sh >> /home/trido/thanhdt/WorkingClaude/mike/logs/fa_ratings_refresh.log 2>&1
#
# Why a wrapper on top of a script that already self-verifies: refresh_fa_ratings.py
# aborts (exit≠0) on its own gates (frozen-quarter statistical match, post-publish
# counts), but the lesson from fa_ratings_8l stands — never trust a script's own "OK"
# for the question "did the TABLE actually move". The wrapper independently checks
# lastModifiedTime advanced past run start + a sane row floor, and alerts loudly
# (Discord Trading Daily + bus event) when anything failed.
set -uo pipefail

ROOT="/home/trido/thanhdt/WorkingClaude"
MIKE="$ROOT/mike"
PROJECT="lithe-record-440915-m9"
TABLE="tav2_bq.fa_ratings"
MIN_ROWS=12000                     # frozen history alone is 12,367 minus at most the 2
                                   # open quarters' churn; anything under 12k = truncated
DISCORD_TRADING_DAILY="1521470705563340910"
export PATH="/home/trido/google-cloud-sdk/bin:$PATH"

START_EPOCH="$(date +%s)"
echo "=== fa_ratings weekly append-only refresh — $(TZ='Asia/Ho_Chi_Minh' date +'%F %T ICT') ==="

cd "$ROOT"
python3 refresh_fa_ratings.py
PY_RC=$?

_table_meta() {  # prints "<lastModified_epoch_s> <numRows>"
  bq show --format=prettyjson "${PROJECT}:${TABLE}" 2>/dev/null | python3 -c "
import json,sys
d = json.load(sys.stdin)
print(int(d.get('lastModifiedTime', 0)) // 1000, d.get('numRows', 0))"
}

read -r LM_S NUM_ROWS <<< "$(_table_meta || echo '0 0')"
LM_S="${LM_S:-0}"; NUM_ROWS="${NUM_ROWS:-0}"

FAIL_REASON=""
[ "$PY_RC" -ne 0 ] && FAIL_REASON="refresh_fa_ratings.py exit=$PY_RC (xem log — có thể là ABORT chủ động: frozen-quarter match dưới floor 70%/99% = KHÔNG phải drift giá bình thường, cần điều tra trước khi publish)"
[ -z "$FAIL_REASON" ] && [ "$LM_S" -lt "$START_EPOCH" ] && \
  FAIL_REASON="table lastModified ($(date -d @"$LM_S" +'%F %T' 2>/dev/null)) < run start — BQ write silently failed (khả năng identity cron không có quyền ghi, giống case bq-reader-8l)"
[ -z "$FAIL_REASON" ] && [ "$NUM_ROWS" -lt "$MIN_ROWS" ] && \
  FAIL_REASON="numRows=$NUM_ROWS < $MIN_ROWS — bảng bị ghi thiếu/cụt"

if [ -n "$FAIL_REASON" ]; then
  MSG="⛔ fa_ratings WEEKLY REFRESH FAILED ($(TZ='Asia/Ho_Chi_Minh' date +'%F %H:%M ICT')): $FAIL_REASON. Bảng vẫn là bản cũ — consumers (SIGNAL_V11 fa_tier gate của book BAL, pt_v22/pt_v23, bq_cache) đọc rating cũ; quý mới BCTC không vào. Check mike/logs/fa_ratings_refresh.log"
  "$MIKE/bin/notify_thread.sh" "$MSG" "$DISCORD_TRADING_DAILY" 2>/dev/null || true
  "$MIKE/bin/append_event.sh" Taylor error "fa_ratings-refresh-failed" "{\"reason\":\"$FAIL_REASON\"}" 2>/dev/null || true
  echo "FAILED: $FAIL_REASON"
  exit 1
fi

echo "OK: refreshed — lastModified $(date -d @"$LM_S" +'%F %T'), rows=$NUM_ROWS"
"$MIKE/bin/append_event.sh" Taylor status "fa_ratings-refresh-ok" "{\"rows\":$NUM_ROWS}" 2>/dev/null || true
