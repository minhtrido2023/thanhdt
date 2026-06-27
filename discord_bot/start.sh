#!/usr/bin/env bash
# start.sh — idempotent launcher. Safe to call repeatedly (cron every 5 min).
#   bot already alive  -> no-op
#   bot not running     -> background run.sh, record PID
# This + cron is the supervisor (no systemd): @reboot starts it, */5 revives it.
HERE="$(cd "$(dirname "$0")" && pwd)"
PATTERN="/home/trido/thanhdt/discord_bot/venv/bin/python /home/trido/thanhdt/discord_bot/bot.py"

if pgrep -f "$PATTERN" >/dev/null; then
  exit 0          # already running -> no-op
fi

cd "$HERE"
nohup "$HERE/run.sh" >> "$HERE/bot.log" 2>&1 &
echo $! > "$HERE/bot.pid"
