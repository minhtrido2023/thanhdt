#!/usr/bin/env bash
# restart.sh — kill the running bot, wait for it to die, then relaunch.
#
#   --delay N   sleep N seconds BEFORE killing. Lets an in-flight reply finish
#               posting before the bot process that posts it is replaced.
#
# Self-restart from inside a chat turn (after editing code/config) must DETACH so
# this script outlives the pkill:
#       setsid ./restart.sh --delay 20 >/dev/null 2>&1 </dev/null &
# restart.sh's cmdline is "/bin/bash .../restart.sh" so it never matches PATTERN
# and is never killed by the pkill below.
HERE="$(cd "$(dirname "$0")" && pwd)"
PATTERN="/home/trido/thanhdt/discord_bot/venv/bin/python /home/trido/thanhdt/discord_bot/bot.py"

DELAY=0
if [ "${1:-}" = "--delay" ]; then DELAY="${2:-0}"; fi
if [ "$DELAY" -gt 0 ] 2>/dev/null; then sleep "$DELAY"; fi

pkill -f "$PATTERN" 2>/dev/null || true
# Wait up to 30s for a clean exit — start.sh is idempotent and would no-op if the
# old instance were still alive, so it must be fully gone before we relaunch.
for _ in $(seq 1 30); do
  pgrep -f "$PATTERN" >/dev/null || break
  sleep 1
done
pkill -9 -f "$PATTERN" 2>/dev/null || true   # SIGKILL stragglers
sleep 1
exec "$HERE/start.sh"
