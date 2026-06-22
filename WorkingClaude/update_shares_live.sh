#!/usr/bin/env bash
# update_shares_live.sh — DAILY scan for new corporate-action factor resets
# (Winston/Data-Ops). Detection + alert only (Winston+Taylor via bus); the actual
# OShares write stays manual & gate-validated. Idempotent, self-deduping.
set -uo pipefail
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
PY="$DNA_PYEXE"; cd "$WORKDIR_8L"
LOG="data/shares_scan_$(date +%Y-%m).log"
echo "===== shares scan run $(date) =====" >> "$LOG"
ok=0
for attempt in $(seq 1 3); do
  if $PY update_shares_live.py --scan >> "$LOG" 2>&1; then ok=1; echo "  ok (attempt $attempt)" >> "$LOG"; break; fi
  echo "  attempt $attempt failed — retry in 3m" >> "$LOG"; sleep 180
done
[ "$ok" = 1 ] || echo "  !! all attempts failed" >> "$LOG"
echo "===== done (ok=$ok) $(date) =====" >> "$LOG"
find data -name 'shares_scan_2*.log' -mtime +60 -delete 2>/dev/null
exit 0
