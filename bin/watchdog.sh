#!/usr/bin/env bash
# watchdog.sh — runs from cron (e.g. every 10 min). For each known agent (one registry
# file per agent), checks its systemd user unit and restarts it if down. Any restart is
# logged and, if mike/bin/notify.sh exists, pushed through it (wire your Telegram bot there).
# A persistently-failing unit usually means the claude.ai OAuth token expired → re-login.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUS="$ROOT/bus"; LOG="$ROOT/logs/watchdog.log"
mkdir -p "$ROOT/logs"
shopt -s nullglob

notify() {  # notify "<message>"
  echo "$(date -u +%FT%TZ) $1" >> "$LOG"
  [ -x "$ROOT/bin/notify.sh" ] && "$ROOT/bin/notify.sh" "[Mike watchdog] $1" || true
}

for r in "$BUS"/registry/*.json; do
  id="$(basename "$r" .json)"
  unit="mike@$id"
  # Skip agents never enabled as a unit.
  systemctl --user list-unit-files "$unit.service" >/dev/null 2>&1 || continue
  if ! systemctl --user is-active --quiet "$unit"; then
    notify "$unit is DOWN — restarting (check claude.ai OAuth if it keeps failing)"
    systemctl --user restart "$unit" 2>>"$LOG" || notify "$unit restart FAILED"
  fi
done
