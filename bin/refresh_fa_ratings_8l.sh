#!/usr/bin/env bash
# refresh_fa_ratings_8l.sh — weekly cron wrapper for `rating_8l_history.py` (refreshes
# tav2_bq.fa_ratings_8l from full ticker_financial history + forensic/moat/bank-AQ overlays).
#
# Winston proposal 2026-07-11 (job Winston_20260711_104135), user approved 2026-07-11.
# Crontab (server runs UTC, = 08:30 ICT Sat):
#   30 1 * * 6 /home/trido/thanhdt/WorkingClaude/mike/bin/refresh_fa_ratings_8l.sh >> /home/trido/thanhdt/WorkingClaude/mike/logs/fa_ratings_8l_refresh.log 2>&1
#
# Why a wrapper instead of calling the python directly: rating_8l_history.py's
# refresh_bq_table() runs every bq subprocess with capture_output and NEVER checks
# returncodes — it prints "refreshed BQ table tav2_bq.fa_ratings_8l" even when the load or
# CREATE OR REPLACE failed. A cron that trusts that line reproduces exactly the
# silent-dead-writer failure this proposal exists to prevent. So the wrapper verifies the
# TABLE ITSELF moved (lastModifiedTime advanced past our start + sane row count) and alerts
# loudly when it didn't.
set -uo pipefail

# Auth: CLOUDSDK_CONFIG = dtienthanh@gmail.com (read-WRITE) — without this, cron's default
# gcloud config is bq-reader-8l (read-only) and every BQ write silently fails.
source /home/trido/thanhdt/WorkingClaude/wc_env.sh

ROOT="/home/trido/thanhdt/WorkingClaude"
MIKE="$ROOT/mike"
PROJECT="lithe-record-440915-m9"
TABLE="tav2_bq.fa_ratings_8l"
MIN_ROWS=50000                      # last known good: 52,433 (2026-06-20); rows only grow
DISCORD_TRADING_DAILY="trading_daily"
export PATH="/home/trido/google-cloud-sdk/bin:$PATH"

START_EPOCH="$(date +%s)"
echo "=== fa_ratings_8l weekly refresh — $(TZ='Asia/Ho_Chi_Minh' date +'%F %T ICT') ==="

cd "$ROOT"
python3 rating_8l_history.py
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
[ "$PY_RC" -ne 0 ] && FAIL_REASON="rating_8l_history.py exit=$PY_RC"
[ -z "$FAIL_REASON" ] && [ "$LM_S" -lt "$START_EPOCH" ] && \
  FAIL_REASON="table lastModified ($(date -d @"$LM_S" +'%F %T' 2>/dev/null)) < run start — BQ write silently failed (refresh_bq_table() không check returncode)"
[ -z "$FAIL_REASON" ] && [ "$NUM_ROWS" -lt "$MIN_ROWS" ] && \
  FAIL_REASON="numRows=$NUM_ROWS < $MIN_ROWS — bảng bị ghi thiếu/cụt"

if [ -n "$FAIL_REASON" ]; then
  MSG="⛔ fa_ratings_8l WEEKLY REFRESH FAILED ($(TZ='Asia/Ho_Chi_Minh' date +'%F %H:%M ICT')): $FAIL_REASON. Bảng vẫn là bản cũ — consumers (custom30 builder, golive sizing, DC-book, SIGNAL_V11 re-tune) đọc rating cũ. Check mike/logs/fa_ratings_8l_refresh.log"
  "$MIKE/bin/notify_thread.sh" "$MSG" "$DISCORD_TRADING_DAILY" 2>/dev/null || true
  "$MIKE/bin/append_event.sh" Winston error "fa_ratings_8l-refresh-failed" "{\"reason\":\"$FAIL_REASON\"}" 2>/dev/null || true
  echo "FAILED: $FAIL_REASON"
  exit 1
fi

echo "OK: refreshed — lastModified $(date -d @"$LM_S" +'%F %T'), rows=$NUM_ROWS"
"$MIKE/bin/append_event.sh" Winston status "fa_ratings_8l-refresh-ok" "{\"rows\":$NUM_ROWS}" 2>/dev/null || true
