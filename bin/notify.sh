#!/usr/bin/env bash
# notify.sh "<message>"   — push a fleet alert to Discord #mikefleet (topic: update task).
#
# This is the missing piece watchdog.sh / fleet_health.sh probe for: they call
#   [ -x bin/notify.sh ] && bin/notify.sh "<msg>"
# so until now every DOWN / ZOMBIE / usage / context alert was LOG-ONLY. With this
# file present, Mike can actually reach the user out-of-band.
#
# Design goals:
#   - NEVER break the caller: always exit 0, never block long.
#   - Anti-spam: identical message inside NOTIFY_DEDUP_SEC is logged but not re-sent.
#   - Kill-switch: MIKE_NOTIFY_OFF=1  OR  file state/NOTIFY_OFF  -> log only, no send.
#
# Usage:
#   bin/notify.sh "Mafee ZOMBIE — restarted"        # send one alert
#   bin/notify.sh --test                            # send a self-test ping
#   echo "multi-line\nbody" | bin/notify.sh -       # read message from stdin
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG="$ROOT/logs/notify.log"
STATE="$ROOT/state/notify"
DEDUP_SEC="${NOTIFY_DEDUP_SEC:-300}"
mkdir -p "$ROOT/logs" "$STATE" 2>/dev/null || true

# --- gather message ---------------------------------------------------------
if [ "${1:-}" = "--test" ]; then
  msg="ping — Mike notify.sh self-test ($(hostname -s 2>/dev/null || echo host))"
elif [ "${1:-}" = "-" ]; then
  msg="$(cat)"
else
  msg="$*"
fi
[ -n "${msg// /}" ] || { echo "notify.sh: empty message" >&2; exit 0; }

ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
host="$(hostname -s 2>/dev/null || echo host)"
full="**Mike fleet** · ${host} · ${ts}
${msg}"

log() { printf '%s | %s\n' "$ts" "$1" >>"$LOG" 2>/dev/null || true; }

# --- kill-switch ------------------------------------------------------------
if [ "${MIKE_NOTIFY_OFF:-0}" = "1" ] || [ -f "$STATE/../NOTIFY_OFF" ]; then
  log "SUPPRESSED (kill-switch) :: $msg"
  echo "notify.sh: suppressed by kill-switch (logged only)"
  exit 0
fi

# --- dedup ------------------------------------------------------------------
# hash the raw message (not the timestamped wrapper) so repeats collapse.
hash="$(printf '%s' "$msg" | cksum | cut -d' ' -f1)"
mark="$STATE/$hash"
now="$(date +%s)"
if [ -f "$mark" ]; then
  last="$(cat "$mark" 2>/dev/null || echo 0)"
  if [ $(( now - last )) -lt "$DEDUP_SEC" ]; then
    log "DEDUP (sent ${last}, <${DEDUP_SEC}s ago) :: $msg"
    echo "notify.sh: duplicate within ${DEDUP_SEC}s — logged, not re-sent"
    exit 0
  fi
fi

# --- send via Discord #mikefleet, topic "update task" -----------------------
rc=0
"$ROOT/bin/notify_discord.sh" "$full" "Mike fleet" "3447003" "update task" 2>/dev/null || rc=$?

if [ "$rc" -eq 0 ]; then
  echo "$now" >"$mark" 2>/dev/null || true
  log "SENT :: $msg"
  echo "notify.sh: sent"
else
  log "FAILED (rc=$rc) :: $msg"
  echo "notify.sh: send failed (rc=$rc)" >&2
fi
exit 0   # never break the caller
