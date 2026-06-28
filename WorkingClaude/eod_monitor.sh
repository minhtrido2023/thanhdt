#!/usr/bin/env bash
# eod_monitor.sh — independent EOD health check (OPS-1 + OPS-7).
# Runs at 23:55 ICT Mon-Fri AFTER daily_refresh (23:15) + BQ cache sync (23:45).
# Orthogonal to pipeline: fires even if the refresh aborted mid-way.
set -uo pipefail
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
cd "$WORKDIR_8L"
LOG="data/eod_monitor_$(date +%Y-%m-%d).log"
echo "===== eod_monitor START $(date) =====" >> "$LOG"
"$DNA_PYEXE" eod_monitor.py >> "$LOG" 2>&1
RC=$?
echo "===== eod_monitor DONE rc=$RC $(date) =====" >> "$LOG"
exit $RC
