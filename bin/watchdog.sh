#!/usr/bin/env bash
# watchdog.sh — runs from cron (e.g. every 10 min). Restarts any ENABLED mike@ unit that
# isn't active, and distinguishes a TRANSIENT down (a restart fixes it) from a PERSISTENT
# failure (likely a claude.ai OAuth logout — a restart can NOT fix that; a human must
# `claude login` and restart). Per-unit consecutive-down counts live in state/flap/.
#
# This is the safety net Mike gives the employee fleet, the same way WorkingClaude gave it
# to Mike: a logout used to fail SILENTLY (flap every 10 min forever). Now it's logged
# loudly and escalated. Notifications are LOG-ONLY by default (logs/watchdog.log); if an
# executable bin/notify.sh exists it is also called, but none is shipped (user chose log-only).
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG="$ROOT/logs/watchdog.log"
FLAP="$ROOT/state/flap"          # one file per unit holding consecutive-down count
mkdir -p "$ROOT/logs" "$FLAP"
shopt -s nullglob

# How many consecutive down-checks (≈ runs × cron interval) before we call it a persistent
# failure / probable logout rather than a transient crash. 3 × 10 min ≈ 30 min.
ESCALATE_AFTER="${WATCHDOG_ESCALATE_AFTER:-3}"

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
  cnt_file="$FLAP/$unit"

  if systemctl --user is-active --quiet "$unit"; then
    # Healthy: clear any prior down-streak (and announce recovery if it had been escalated).
    if [ -f "$cnt_file" ]; then
      prev="$(cat "$cnt_file" 2>/dev/null || echo 0)"
      [ "${prev:-0}" -ge "$ESCALATE_AFTER" ] && notify "$unit RECOVERED after $prev consecutive down-checks"
      rm -f "$cnt_file"
    fi
    continue
  fi

  # Down: bump the consecutive-down counter.
  cnt="$(cat "$cnt_file" 2>/dev/null || echo 0)"; cnt=$(( ${cnt:-0} + 1 )); echo "$cnt" > "$cnt_file"

  # Why is it down? (start-limit-hit / exit-code / signal → useful for the human reading the log.)
  result="$(systemctl --user show "$unit" -p Result --value 2>/dev/null || true)"

  if [ "$cnt" -ge "$ESCALATE_AFTER" ]; then
    notify "$unit PERSISTENT FAILURE ($cnt consecutive down, Result=$result) — likely claude.ai OAuth logout. A restart can't fix this: run \`claude login\` for that agent, then \`systemctl --user restart $unit\`."
  else
    notify "$unit is DOWN (#$cnt, Result=$result) — restarting"
  fi

  systemctl --user reset-failed "$unit" 2>/dev/null || true   # clear any start-limit block
  systemctl --user restart "$unit" 2>>"$LOG" || notify "$unit restart FAILED"
done
[ "$found" = 1 ] || notify "no enabled mike@ units found in $WANTS"
