# _resolve_id.sh — sourced by the hooks. Sets $id.
#   - If $1 is given (spawn_child children with a baked id) → use it.
#   - Else (retrofit: shared settings.local.json, no baked id) → read the hook's stdin
#     JSON, take session_id, resolve to the friendly fleet label, and use that.
#   - Self-exclude: if the resolved id is in $MIKE_EXCLUDE (default "tri"), exit 0 silently
#     so excluded sessions never participate (tri shares a cwd with retrofitted sessions).
# Requires: $ROOT set by the caller.
id="${1:-}"
if [ -z "$id" ]; then
  _payload="$(cat 2>/dev/null || true)"
  _sid="$(printf '%s' "$_payload" | python3 -c 'import sys,json
try: print(json.load(sys.stdin).get("session_id",""))
except Exception: print("")' 2>/dev/null || true)"
  id="$("$ROOT/bin/discover_sessions.py" --resolve "$_sid" 2>/dev/null || true)"
  [ -n "$id" ] || id="${_sid:0:8}"
  [ -n "$id" ] || id="unknown"
fi
for _x in ${MIKE_EXCLUDE:-tri}; do
  if [ "$id" = "$_x" ]; then exit 0; fi
done
