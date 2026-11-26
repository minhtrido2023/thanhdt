#!/usr/bin/env bash
# run_subagent.sh — run an isolated stateless subagent from ~/.claude/agents/<name>.md
# inside mike/agents/_reviewers/ so it avoids inheriting Mike/WorkingClaude's ~35KB+
# CLAUDE.md + KB autoloads, cutting turn-1 prompt cost by ~80-90%.
#
# Usage:
#   bin/run_subagent.sh <agent_name> "<prompt>" [--model M] [--effort E] [--max-turns N] [--dir PATH]
#   echo "prompt" | bin/run_subagent.sh <agent_name> - [--model haiku]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"
CLAUDE="${CLAUDE_BIN:-/home/trido/.local/bin/claude}"

if [ $# -lt 2 ]; then
  echo "usage: run_subagent.sh <agent_name> \"<prompt>\" [--model M] [--effort E] [--max-turns N] [--dir PATH]" >&2
  exit 2
fi

name="$1"
prompt="$2"
shift 2

if ! [[ "$name" =~ ^[A-Za-z0-9_-]+$ ]]; then
  echo "run_subagent: invalid agent name '$name'" >&2
  exit 2
fi

if [ "$prompt" = "-" ]; then
  prompt="$(cat)"
fi
[ -n "$prompt" ] || { echo "run_subagent: empty prompt" >&2; exit 2; }

model_ovr=""
effort_ovr=""
max_turns=25
add_dir="$WC_ROOT"

while [ $# -gt 0 ]; do
  case "$1" in
    --model) model_ovr="${2:?--model requires a value}"; shift 2 ;;
    --model=*) model_ovr="${1#*=}"; shift ;;
    --effort) effort_ovr="${2:?--effort requires a value}"; shift 2 ;;
    --effort=*) effort_ovr="${1#*=}"; shift ;;
    --max-turns) max_turns="${2:?--max-turns requires a value}"; shift 2 ;;
    --max-turns=*) max_turns="${1#*=}"; shift ;;
    --dir) add_dir="${2:?--dir requires a value}"; shift 2 ;;
    --dir=*) add_dir="${1#*=}"; shift ;;
    *) echo "run_subagent: unknown arg '$1'" >&2; exit 2 ;;
  esac
done

agent_def="$HOME/.claude/agents/${name}.md"
[ -f "$agent_def" ] || { echo "run_subagent: agent def not found: $agent_def" >&2; exit 2; }
[ -d "$add_dir" ] || { echo "run_subagent: --dir not found: $add_dir" >&2; exit 2; }

rev_dir="$ROOT/agents/_reviewers"
[ -d "$rev_dir" ] || rev_dir="$add_dir"

parsed="$(python3 - "$agent_def" <<'PY'
import json, re, sys
raw = open(sys.argv[1], encoding="utf-8").read()
meta = {}
body = raw
m = re.match(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", raw, re.S)
if m:
    fm, body = m.group(1), m.group(2)
    for ln in fm.splitlines():
        if ":" in ln:
            k, v = ln.split(":", 1)
            meta[k.strip().lower()] = v.strip()
tools_raw = meta.get("tools", "")
tools = " ".join(p.strip() for p in tools_raw.split(",") if p.strip())
print(json.dumps({
    "model": meta.get("model", ""),
    "tools": tools,
    "body": body.strip(),
}, ensure_ascii=False))
PY
)"

fm_model="$(printf '%s' "$parsed" | python3 -c 'import json,sys; print(json.load(sys.stdin)["model"])')"
fm_tools="$(printf '%s' "$parsed" | python3 -c 'import json,sys; print(json.load(sys.stdin)["tools"])')"
sys_body="$(printf '%s' "$parsed" | python3 -c 'import json,sys; print(json.load(sys.stdin)["body"])')"

model="${model_ovr:-${fm_model:-sonnet}}"
tools="${fm_tools:-Bash Read Grep Glob}"

full_prompt="${sys_body}

--- TASK ---
Workspace root: $add_dir (mike fleet root: $ROOT).

${prompt}"

sid="$(cat /proc/sys/kernel/random/uuid 2>/dev/null || python3 -c 'import uuid; print(uuid.uuid4())' 2>/dev/null || true)"
cmd=(
  "$CLAUDE" -p "$full_prompt"
  --model "$model"
  --permission-mode auto
  --allowedTools "$tools"
  --add-dir "$add_dir"
  --max-turns "$max_turns"
)
[ -n "$effort_ovr" ] && cmd+=( --effort "$effort_ovr" )
if [[ "$sid" =~ ^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$ ]]; then
  cmd+=( --session-id "$sid" )
fi

cd "$rev_dir"
exec env MIKE_SKIP=1 "${cmd[@]}"
