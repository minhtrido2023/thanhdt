#!/bin/bash
# Winston daily new-listing feed — runs after pt_8l_daily (17:45 ICT) at 18:00 ICT Mon-Fri
# Detects tickers newly added to BQ in the last 90 days, flags those needing 8L manual rating.

source /home/trido/thanhdt/WorkingClaude/wc_env.sh
LOG=/home/trido/thanhdt/WorkingClaude/mike/logs/new_listings.log

echo "[$(date '+%Y-%m-%dT%H:%M:%S%z')] fetch_new_listings_daily START" >> "$LOG"
"$DNA_PYEXE" /home/trido/thanhdt/WorkingClaude/fetch_new_listings.py >> "$LOG" 2>&1
EC=$?
echo "[$(date '+%Y-%m-%dT%H:%M:%S%z')] fetch_new_listings_daily EXIT $EC" >> "$LOG"
exit $EC
