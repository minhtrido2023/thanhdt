#!/usr/bin/env bash
# telegram_run_daily.sh — BUILD + DIRECT SEND with retry (no WARP/VPN).
# Server reaches api.telegram.org directly. The VN ISP block is intermittent & rare; a
# retry-backoff window rides through a short block. Keeps @AbV6_bot + CSV attachment,
# VN-time (wc_env TZ=ICT). Run by host cron @ 18:00 ICT (11:00 UTC).
set -uo pipefail
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
export STATE_WORKDIR="$WORKDIR_8L"
PY="$DNA_PYEXE"; cd "$WORKDIR_8L"
LOG="telegram_run_$(date +%Y-%m-%d).log"
OUT="data/telegram_report_latest.txt"; DATED="data/telegram_report_$(date +%Y-%m-%d).txt"
echo "===== telegram report run $(date) =====" >> "$LOG"

# 1) on-demand fallback file (dry-run; BQ direct)
$PY telegram_recommend.py --dry-run --no-attach 2>>"$LOG" \
  | sed -n '/MESSAGE PREVIEW/,/\[--dry-run\]/p' \
  | sed '1,2d;/^=*$/d;/\[--dry-run\]/d;/Message length:/d' | sed 's/<[^>]*>//g' > "$OUT.tmp"
[ -s "$OUT.tmp" ] && { mv "$OUT.tmp" "$OUT"; cp "$OUT" "$DATED"; } || rm -f "$OUT.tmp"

# 2) DIRECT SEND with retry-backoff (rides a short intermittent block: ~8 tries / ~30 min)
sent=0
for attempt in $(seq 1 8); do
  echo "--- send attempt $attempt $(date +%H:%M:%S) ---" >> "$LOG"
  if $PY telegram_recommend.py >> "$LOG" 2>&1; then sent=1; echo "  ✓ sent (attempt $attempt)" >> "$LOG"; break; fi
  echo "  send failed (telegram maybe briefly blocked) — retry in 4m" >> "$LOG"; sleep 240
done
[ "$sent" = 1 ] || echo "  !! all send attempts failed (>30m) — report file built for on-demand resend" >> "$LOG"
echo "===== done (sent=$sent) $(date) =====" >> "$LOG"
find . -maxdepth 1 -name 'telegram_run_*.log' -mtime +30 -delete 2>/dev/null
find data -name 'telegram_report_2*.txt' -mtime +30 -delete 2>/dev/null
exit 0
