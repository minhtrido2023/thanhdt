#!/usr/bin/env bash
# watchdog.sh — runs from cron (e.g. every 10 min). Restarts any ENABLED mike@ unit that
# isn't active. Restarts are logged and, if mike/bin/notify.sh exists, pushed through it.
# A unit that keeps failing fast usually means the claude.ai OAuth token expired → re-login.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG="$ROOT/logs/watchdog.log"
mkdir -p "$ROOT/logs"
shopt -s nullglob

# cron has no systemd-user session env — without these, `systemctl --user` can't reach the bus.
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
export DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-unix:path=$XDG_RUNTIME_DIR/bus}"

notify() {  # notify "<message>"
  echo "$(date -u +%FT%TZ) $1" >> "$LOG"
  [ -x "$ROOT/bin/notify.sh" ] && "$ROOT/bin/notify.sh" "[Mike watchdog] $1" || true
}

# Source of truth for "should be running" = the enabled instances (symlinks in *.wants).
WANTS="$HOME/.config/systemd/user/default.target.wants"
found=0
for link in "$WANTS"/mike@*.service; do
  found=1
  unit="$(basename "$link")"            # e.g. mike@Mike.service
  if ! systemctl --user is-active --quiet "$unit"; then
    notify "$unit is DOWN — restarting (check claude.ai OAuth if it keeps failing)"
    systemctl --user reset-failed "$unit" 2>/dev/null || true   # clear any start-limit block
    systemctl --user restart "$unit" 2>>"$LOG" || notify "$unit restart FAILED"
  fi
done
[ "$found" = 1 ] || notify "no enabled mike@ units found in $WANTS"
