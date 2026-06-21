#!/usr/bin/env bash
# 8L daily EOD chain (5 steps): rating_8l -> unified_screener -> rank_8l
#   -> rank_8l_daily_alert (top-30 surprise-jump Telegram) -> cheap_pb_floor (rating x PB-floor x Ngu-Hanh buy-now Telegram)
set -e
cd "$(dirname "$0")/.."                                  # app root
source deploy_8l/env.sh 2>/dev/null || source env.sh
if [ -f venv/bin/activate ]; then source venv/bin/activate; PY=python; else PY=python3; fi   # venv (bare-metal) or system (container)
TS=$(date +%F); LOG="data/pt_8l_daily_${TS}.log"
{
  echo "==== 8L daily $(date) ===="
  echo "[1/5] rating_8l.py";            $PY rating_8l.py
  echo "[2/5] unified_screener.py";     $PY unified_screener.py
  echo "[3/5] rank_8l.py";              $PY rank_8l.py
  echo "[4/5] rank_8l_daily_alert.py";  $PY rank_8l_daily_alert.py
  echo "[5/5] cheap_pb_floor.py";       $PY cheap_pb_floor.py
  echo "done $(date)"
} >> "$LOG" 2>&1
