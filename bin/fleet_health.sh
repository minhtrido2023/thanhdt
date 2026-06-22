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
printf "%-14s %-8s %-8s %-7s %-4s %-11s %-7s %s\n" AGENT STATE SERVING CTX RST UPTIME STREAK "LAST HB"
printf -- "%.0s-" {1..92}; echo

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

  unset hs
  # Authoritative liveness: is the agent actually serving a session? (systemd "active" can lie —
  # a host can be up yet serving nothing = the zombie that killed Mafee.)
  if [ "$active" = "active" ] && python3 "$ROOT/bin/is_serving.py" "$id" 2>/dev/null; then
    serve="yes"
  elif [ "$active" = "active" ]; then serve="NO"; else serve="-"; fi

  # Context fullness of the live conversation (built-in auto-compacts ~90%+; this warns earlier).
  read -r ctok climit cpct <<<"$(python3 "$ROOT/bin/context_watch.py" "$id" 2>/dev/null)"
  if [ "${cpct:-_}" = "_" ] || [ "$ctok" = "-" ]; then ctxcol="-"; else ctxcol="${cpct}%"; fi

  flag=""
  if [ "$active" != "active" ]; then
    degraded=1
    if [ "${streak:-0}" -ge 3 ]; then flag="  <== DOWN/LOGGED-OUT (claude login + restart)"; else flag="  <== DOWN"; fi
  elif [ "$serve" = "NO" ]; then
    degraded=1
    if [ "${streak:-0}" -ge 3 ]; then flag="  <== ZOMBIE PERSISTENT — re-pair in Claude app"; else flag="  <== ZOMBIE (active but not serving)"; fi
  elif [ -n "${cpct:-}" ] && [ "${cpct%%.*}" -ge "${CTX_WARN_PCT:-80}" ] 2>/dev/null; then
    flag="  <== context ${cpct}% — auto-compact will fire soon"
  fi

  printf "%-14s %-8s %-8s %-7s %-4s %-11s %-7s %s%s\n" "$id" "$active" "$serve" "$ctxcol" "$nrst" "$up" "$streak" "$hb" "$flag"
done

echo
echo "Recent watchdog alerts (last 8):"
tail -n 8 "$ROOT/logs/watchdog.log" 2>/dev/null | sed 's/^/  /' || echo "  (no watchdog.log yet)"

if [ "$degraded" = 1 ]; then
  echo
  echo "⚠ Degraded agents:"
  echo "   • DOWN              → watchdog auto-restarts; if STREAK≥3 it's a logout: \`claude login\` + \`systemctl --user restart mike@<id>\`"
  echo "   • ZOMBIE (SERVING=NO) → host up but serving nothing. Watchdog auto-recovers (clear stale"
  echo "                          bridge-pointer + restart). If STREAK≥3 it's stuck → open the agent in"
  echo "                          the Claude app (claude.ai/code) or check \`claude login\`."
fi
exit "$degraded"
