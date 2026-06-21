#!/usr/bin/env bash
# rubber_weekly.sh — DAILY natural-rubber feed + threshold alerting (Winston/Data-Ops)
# Despite the name, runs Mon-Fri so a WATCH/ALERT vs prior-week close fires the SAME day.
# Idempotent + self-deduping (data/rubber_alert_state.json). Retries a brief network block.
set -uo pipefail
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
PY="$DNA_PYEXE"; cd "$WORKDIR_8L"
LOG="data/rubber_weekly_$(date +%Y-%m).log"
echo "===== rubber_weekly run $(date) =====" >> "$LOG"
ok=0
for attempt in $(seq 1 4); do
  if $PY rubber_weekly.py >> "$LOG" 2>&1; then ok=1; echo "  ok (attempt $attempt)" >> "$LOG"; break; fi
  echo "  attempt $attempt failed — retry in 3m" >> "$LOG"; sleep 180
done
[ "$ok" = 1 ] || echo "  !! all attempts failed" >> "$LOG"
echo "===== done (ok=$ok) $(date) =====" >> "$LOG"
find data -name 'rubber_weekly_2*.log' -mtime +60 -delete 2>/dev/null
exit 0
