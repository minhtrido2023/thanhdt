#!/usr/bin/env bash
# spawn_child.sh <agent_id> <role> [description] [--start]
# Provisions a child agent's working dir under mike/agents/<id>:
#   - CLAUDE.md  rendered from CHILD_TEMPLATE.md
#   - .claude/settings.json wiring the 3 hooks (agent_id baked into each command)
#   - seeds bus/registry/<id>.json (status=idle)
# Does NOT start the systemd unit unless --start is given (Remote Control needs a valid
# claude.ai OAuth login first). Prints the start command otherwise.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOKS="$ROOT/hooks"
PY="$ROOT/bin/mike_json.py"

id="${1:?usage: spawn_child.sh <agent_id> <role> [description] [--start]}"
role="${2:?role required}"
desc="${3:-}"
start="no"
[ "${4:-}" = "--start" ] && start="yes"
[ "${3:-}" = "--start" ] && { start="yes"; desc=""; }

# id must be a clean token (used as systemd instance name + filename)
case "$id" in *[!A-Za-z0-9_-]*) echo "agent_id must be [A-Za-z0-9_-]"; exit 1;; esac

AGDIR="$ROOT/agents/$id"
mkdir -p "$AGDIR/.claude"

# --- CLAUDE.md (rendered from template; replace tokens safely via python) ---
if [ -f "$ROOT/CHILD_TEMPLATE.md" ]; then
  python3 - "$ROOT/CHILD_TEMPLATE.md" "$id" "$role" "$desc" "$ROOT" > "$AGDIR/CLAUDE.md" <<'PY'
import sys
tpl, aid, role, desc, root = sys.argv[1:6]
s = open(tpl, encoding="utf-8").read()
for k, v in (("{{AGENT_ID}}", aid), ("{{ROLE}}", role), ("{{DESC}}", desc), ("{{ROOT}}", root)):
    s = s.replace(k, v)
sys.stdout.write(s)
PY
else
  printf '# %s (id=%s)\n@%s/kb/context_pack.md\n' "$role" "$id" "$ROOT" > "$AGDIR/CLAUDE.md"
fi

# --- .claude/settings.json (hooks wired with this id as arg) ---
python3 "$PY" settings "$HOOKS" "$id" > "$AGDIR/.claude/settings.json"

# --- seed registry (idle) ---
"$ROOT/bin/heartbeat.sh" "$id" "$desc" idle

echo "provisioned child '$id' (role: $role) at $AGDIR"
if [ "$start" = "yes" ]; then
  systemctl --user enable --now "mike@$id" && echo "started systemd unit mike@$id"
else
  echo "next: systemctl --user enable --now mike@$id   (after claude.ai OAuth is valid)"
fi
