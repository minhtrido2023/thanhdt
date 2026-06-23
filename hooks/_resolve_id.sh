# _resolve_id.sh — sourced by the hooks. Sets $id, and exports $MIKE_SID / $MIKE_CWD
# (this session's id + cwd, from the hook's stdin JSON) for recap/continuity use.
#   - If $1 is given (spawn_child children with a baked id) → use it as $id.
#   - Else (retrofit: shared settings.local.json, no baked id) → resolve session_id to the
#     friendly fleet label and use that.
#   - Self-exclude: if the resolved id is in $MIKE_EXCLUDE (default "tri"), exit 0 silently
#     so excluded sessions never participate (tri shares a cwd with retrofitted sessions).
#   - Hard opt-out: if $MIKE_SKIP is set, exit 0 immediately (before any work). Used by
#     non-fleet sessions that share a hooked cwd — e.g. the ccdb Discord bot injects
#     MIKE_SKIP=1 via its CCDB_CLI_ENV_FILE overlay so its Claude subprocesses run no
#     fleet hooks. Inert for every normal fleet session, so the fleet is unaffected.
# Requires: $ROOT set by the caller. Reads stdin ONCE (the harness closes it, so safe).
[ -n "${MIKE_SKIP:-}" ] && exit 0
id="${1:-}"
_payload="$(cat 2>/dev/null || true)"
# Pull session_id (line 1) and cwd (line 2) — separate lines tolerate spaces in cwd.
_meta="$(printf '%s' "$_payload" | python3 -c 'import sys, json
try:
    d = json.load(sys.stdin); print(d.get("session_id", "")); print(d.get("cwd", ""))
except Exception:
    print(""); print("")' 2>/dev/null || true)"
MIKE_SID="$(printf '%s\n' "$_meta" | sed -n 1p)"
MIKE_CWD="$(printf '%s\n' "$_meta" | sed -n 2p)"
export MIKE_SID MIKE_CWD

if [ -z "$id" ]; then
  id="$("$ROOT/bin/discover_sessions.py" --resolve "$MIKE_SID" 2>/dev/null || true)"
  [ -n "$id" ] || id="${MIKE_SID:0:8}"
  [ -n "$id" ] || id="unknown"
fi
for _x in ${MIKE_EXCLUDE:-tri}; do
  if [ "$id" = "$_x" ]; then exit 0; fi
done
