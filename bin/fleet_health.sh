#!/usr/bin/env bash
# fleet_health.sh — one-shot health dashboard for the Mike employee fleet. Read-only.
# For every ENABLED mike@ unit: systemd state, restart count, uptime, why-it-failed, the
# watchdog down-streak (a high streak = probable OAuth logout needing manual re-login), and
# the last heartbeat from its bus registry. Run this whenever you want to know "is everyone ok".
#
#   bin/fleet_health.sh            # table for all enabled agents
#
# Exit code: 0 if all healthy, 1 if any agent is down/degraded (handy for scripting/cron).
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FLAP="$ROOT/state/flap"
REG="$ROOT/bus/registry"
WANTS="$HOME/.config/systemd/user/default.target.wants"
shopt -s nullglob

export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
export DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-unix:path=$XDG_RUNTIME_DIR/bus}"

now=$(date -u +%s)
degraded=0

printf "Mike fleet health  —  %s\n" "$(date -u +%FT%TZ)"
printf "%-14s %-9s %-9s %-4s %-13s %-7s %-8s %s\n" AGENT STATE SUB RST UPTIME STREAK HB-AGE "LAST HEARTBEAT"
printf -- "%.0s-" {1..96}; echo

for link in "$WANTS"/mike@*.service; do
  unit="$(basename "$link")"
  id="${unit#mike@}"; id="${id%.service}"

  # Query each property on its own line — `systemctl show -p A,B,... --value` does NOT
  # guarantee output order matches the requested order, so per-property is the safe parse.
  active="$(systemctl --user show "$unit" -p ActiveState --value 2>/dev/null)"; active="${active:-unknown}"
  sub="$(systemctl --user show "$unit" -p SubState --value 2>/dev/null)"; sub="${sub:-?}"
  nrst="$(systemctl --user show "$unit" -p NRestarts --value 2>/dev/null)"; nrst="${nrst:-?}"
  result="$(systemctl --user show "$unit" -p Result --value 2>/dev/null)"

  # uptime from ActiveEnterTimestamp (human form)
  enter="$(systemctl --user show "$unit" -p ActiveEnterTimestamp --value 2>/dev/null)"
  if [ -n "$enter" ] && [ "$enter" != "n/a" ]; then
    es=$(date -d "$enter" +%s 2>/dev/null || echo 0)
    if [ "$es" -gt 0 ]; then
      d=$(( now - es )); up="$(( d/86400 ))d$(( (d%86400)/3600 ))h$(( (d%3600)/60 ))m"
    else up="?"; fi
  else up="-"; fi

  streak="$(cat "$FLAP/$unit" 2>/dev/null || echo 0)"

  # last heartbeat from registry + its age (a process can be alive but the session stuck/
  # logged-out and not crashing — systemd can't see that; a stale heartbeat can).
  hb="-"; hbage="-"
  if [ -f "$REG/$id.json" ]; then
    hb="$(grep -o '"last_heartbeat": *"[^"]*"' "$REG/$id.json" | head -1 | sed 's/.*"\([^"]*\)"$/\1/')"
    [ -z "$hb" ] && hb="-"
    if [ "$hb" != "-" ]; then
      hs=$(date -d "$hb" +%s 2>/dev/null || echo 0)
      if [ "$hs" -gt 0 ]; then a=$(( now - hs )); hbage="$(( a/3600 ))h$(( (a%3600)/60 ))m"; fi
    fi
  fi

  flag=""
  if [ "$active" != "active" ]; then degraded=1; flag="  <== DOWN"; fi
  if [ "${streak:-0}" -ge 3 ] 2>/dev/null; then degraded=1; flag="  <== LIKELY LOGGED OUT (re-login needed)"; fi
  # stale heartbeat while the unit is up = possible zombie/idle — flag for a session_brief look.
  if [ "$active" = "active" ] && [ -z "$flag" ] && [ "${hs:-0}" -gt 0 ] && [ "$(( now - hs ))" -gt "${STALE_SEC:-10800}" ]; then
    flag="  <== STALE ${hbage} (check: bin/session_brief.py $id)"
  fi
  unset hs

  printf "%-14s %-9s %-9s %-4s %-13s %-7s %-8s %s%s\n" "$id" "$active" "$sub" "$nrst" "$up" "$streak" "$hbage" "$hb" "$flag"
done

echo
echo "Recent watchdog alerts (last 8):"
tail -n 8 "$ROOT/logs/watchdog.log" 2>/dev/null | sed 's/^/  /' || echo "  (no watchdog.log yet)"

if [ "$degraded" = 1 ]; then
  echo
  echo "⚠ Some agents degraded. If STREAK ≥ 3 → that agent's claude.ai token likely expired:"
  echo "    1) re-auth that agent (claude login in its session/dir), 2) systemctl --user restart mike@<id>"
fi
exit "$degraded"
