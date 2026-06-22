#!/usr/bin/env bash
# watchdog.sh — runs from cron (e.g. every 10 min). Keeps the ENABLED mike@ fleet healthy.
# It checks TWO failure modes, because `systemctl is-active` alone is not enough:
#
#   1. DOWN     — the systemd unit isn't active. A restart usually fixes it; if it keeps
#                 failing fast (≥ESCALATE_AFTER in a row) it's a probable claude.ai OAuth
#                 logout — a restart can NOT fix that, a human must `claude login` + restart.
#   2. ZOMBIE   — the unit IS active (host process alive, journal says "Ready") but the agent
#                 isn't actually serving a session (bin/is_serving.py == false). This is what
#                 killed Mafee: systemd thought it was healthy while it was dead. A plain
#                 restart was VERIFIED not to recover this state, so we do NOT churn-restart —
#                 we LOG it for manual re-pair (open the agent in the Claude app / re-establish
#                 the remote-control session). Surfaced on demand by bin/fleet_health.sh.
#
# Per-unit consecutive-bad counts live in state/flap/. Notifications are LOG-ONLY
# (logs/watchdog.log); if an executable bin/notify.sh exists it is also called (none shipped —
# user chose log-only). This is the safety net Mike gives the fleet, the same way WorkingClaude
# gave it to Mike: a death that used to be silent is now logged and escalated.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG="$ROOT/logs/watchdog.log"
FLAP="$ROOT/state/flap"          # one file per unit holding the consecutive-bad count
CTXW="$ROOT/state/ctxwarn"       # one file per agent: marks "already warned at this high context"
mkdir -p "$ROOT/logs" "$FLAP" "$CTXW"
shopt -s nullglob

# Consecutive bad checks (≈ runs × cron interval) before escalating from "transient" to
# "persistent / needs a human". 3 × 10 min ≈ 30 min.
ESCALATE_AFTER="${WATCHDOG_ESCALATE_AFTER:-3}"
# Warn (log only) when a conversation's context passes this % of the limit — ahead of the
# session's built-in auto-compact (~90%+). Just visibility; compaction is the session's own job.
CTX_WARN="${CTX_WARN_PCT:-85}"

# cron has no systemd-user session env — without these, `systemctl --user` can't reach the bus.
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
export DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-unix:path=$XDG_RUNTIME_DIR/bus}"

notify() {  # notify "<message>"
  echo "$(date -u +%FT%TZ) $1" >> "$LOG"
  [ -x "$ROOT/bin/notify.sh" ] && "$ROOT/bin/notify.sh" "[Mike watchdog] $1" || true
}

# clear_bridge <id> — move aside a stale remote-control bridge pointer so the host provisions
# a FRESH environment on restart. VERIFIED fix for the Mafee zombie (2026-06-22): the host was
# pinned to a stuck environment via bridge-pointer.json and never reached "Ready"; removing it
# + restart → serving in ~10s. Safe: only called for a NOT-serving agent; the file is recreated.
clear_bridge() {
  local enc bp
  enc="$(printf '%s' "$ROOT/agents/$1" | sed 's#/#-#g')"
  bp="$HOME/.claude/projects/$enc/bridge-pointer.json"
  [ -f "$bp" ] && mv -f "$bp" "$bp.stale.$(date -u +%s)" 2>/dev/null || true
}

# Source of truth for "should be running" = the enabled instances (symlinks in *.wants).
WANTS="$HOME/.config/systemd/user/default.target.wants"
found=0
for link in "$WANTS"/mike@*.service; do
  found=1
  unit="$(basename "$link")"            # e.g. mike@Mafee.service
  id="${unit#mike@}"; id="${id%.service}"
  cnt_file="$FLAP/$unit"

  active=0; serving=0
  systemctl --user is-active --quiet "$unit" && active=1
  [ "$active" = 1 ] && python3 "$ROOT/bin/is_serving.py" "$id" 2>/dev/null && serving=1

  if [ "$active" = 1 ] && [ "$serving" = 1 ]; then
    # Healthy: clear any prior streak (announce recovery if it had been escalated).
    if [ -f "$cnt_file" ]; then
      prev="$(cat "$cnt_file" 2>/dev/null || echo 0)"
      [ "${prev:-0}" -ge "$ESCALATE_AFTER" ] && notify "$unit RECOVERED (now serving) after $prev bad checks"
      rm -f "$cnt_file"
    fi
    # Context-fullness watch: log once when a conversation crosses CTX_WARN% so a long chat is
    # visible BEFORE the built-in auto-compact (~90%+) fires. Debounced via state/ctxwarn/<id>
    # (log on the up-crossing, clear when it drops back) so we don't repeat every run. The
    # actual compaction is the session's own built-in job — Mike can't /compact another session.
    pct="$(python3 "$ROOT/bin/context_watch.py" "$id" 2>/dev/null | awk '{print $3}')"
    mark="$CTXW/$id"
    if [ -n "$pct" ] && [ "$pct" != "-" ] && [ "${pct%%.*}" -ge "$CTX_WARN" ] 2>/dev/null; then
      [ -f "$mark" ] || notify "$unit context ${pct}% of limit — large chat; built-in auto-compact will fire near ~90%. (FYI; no action needed.)"
      echo "$pct" > "$mark"
    else
      rm -f "$mark" 2>/dev/null || true
    fi
    continue
  fi

  # Bad: bump the consecutive-bad counter.
  cnt="$(cat "$cnt_file" 2>/dev/null || echo 0)"; cnt=$(( ${cnt:-0} + 1 )); echo "$cnt" > "$cnt_file"

  if [ "$active" = 0 ]; then
    # --- Mode 1: DOWN — restart (a restart is the right fix here). Escalate if it persists.
    result="$(systemctl --user show "$unit" -p Result --value 2>/dev/null || true)"
    if [ "$cnt" -ge "$ESCALATE_AFTER" ]; then
      notify "$unit PERSISTENT DOWN ($cnt in a row, Result=$result) — likely claude.ai OAuth logout. Restart can't fix: \`claude login\` for $id then \`systemctl --user restart $unit\`."
    else
      notify "$unit is DOWN (#$cnt, Result=$result) — restarting"
    fi
    systemctl --user reset-failed "$unit" 2>/dev/null || true
    systemctl --user restart "$unit" 2>>"$LOG" || notify "$unit restart FAILED"
  else
    # --- Mode 2: ZOMBIE — active but not serving. A PLAIN restart does NOT recover this
    # (Mafee, 2026-06-22); the working fix is clear_bridge + restart (fresh environment).
    if [ "$cnt" = 1 ]; then
      notify "$unit ZOMBIE — active but NOT serving (#1). Auto-recovery: clear stale bridge-pointer + restart."
      clear_bridge "$id"
      systemctl --user reset-failed "$unit" 2>/dev/null || true
      systemctl --user restart "$unit" 2>>"$LOG" || notify "$unit restart FAILED"
    elif [ "$cnt" -lt "$ESCALATE_AFTER" ]; then
      notify "$unit ZOMBIE — still not serving after bridge reset (#$cnt). Will escalate at $ESCALATE_AFTER."
    elif [ "$cnt" = "$ESCALATE_AFTER" ]; then
      notify "$unit ZOMBIE PERSISTENT — auto-recovery (bridge reset + restart) didn't help. MANUAL: open $id in the Claude app (claude.ai/code), or check \`claude login\`. (watchdog stops restarting it now.)"
    fi
    # cnt > ESCALATE_AFTER: stay silent (already flagged); bin/fleet_health.sh shows it on demand.
  fi
done
[ "$found" = 1 ] || notify "no enabled mike@ units found in $WANTS"
