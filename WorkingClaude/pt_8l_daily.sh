#!/usr/bin/env bash
# pt_8l_daily.sh — Linux port of pt_8l_daily.bat
# 8L EOD: rating -> screener -> rank -> dna cards -> vn30 basket -> surprise alert
# -> cheap-PB-floor alert -> snapshot -> sector-lens monitor. Continue-on-error per step.
# Schedule ~17:45 ICT (before the 18:00 report so rating_8l.csv is fresh for its R column).
#
# Step [9] sector_lens_monitor (added 2026-07-06, job Taylor_20260706_082923; user approved DAILY
# cadence — transitions matter, the script is light so reading daily is cheap): evaluates the
# Group-A sector watchlist (16 names) -> 6 states, alerts state TRANSITIONS + a 8L-rating cross-
# check (rating<=2 golden/strong AND sector-lens BUY = ✓✓ DOUBLE-CONFIRM, two independent systems)
# to the SAME 8L Telegram channel (cfg chat_id via telegram_recommend). It runs AFTER step [1]
# rating_8l so the cross-check reads today's fresh rating_8l.csv. Research/monitor only — touches
# NO production trading (custom30V/BAL/LAG unchanged).
set -uo pipefail
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
export STATE_WORKDIR="$WORKDIR_8L"
PY="$DNA_PYEXE"; cd "$WORKDIR_8L"
LOG="data/pt_8l_daily_$(date +%Y-%m-%d).log"
exec >>"$LOG" 2>&1
echo "===== pt_8l_daily (linux) START $(date) acct=$(gcloud config get-value account 2>/dev/null) ====="

run() { echo; echo "--- $1 ---"; shift; if $PY "$@"; then echo "  [ok] $*"; else echo "  [FAIL exit $?] $*"; fi; }

run "[1] rating_8l"            rating_8l.py
run "[2] unified_screener"     unified_screener.py
run "[3] rank_8l"              rank_8l.py
run "[4] dna_card"             dna_card.py
run "[5] vn30_8l"              vn30_8l.py
run "[6] rank_8l_daily_alert"  rank_8l_daily_alert.py
run "[7] cheap_pb_floor"       cheap_pb_floor.py
echo; echo "--- [8] snapshot rank_8l (bot 'new') ---"
$PY -c "import bot_8l_commands as b; print(b.snapshot_today())" && echo "  [ok] snapshot" || echo "  [FAIL] snapshot"
run "[9] sector_lens_monitor"  sector_lens_monitor.py --telegram

find data -name 'pt_8l_daily_*.log' -mtime +30 -delete 2>/dev/null
echo; echo "===== pt_8l_daily (linux) DONE $(date) ====="
