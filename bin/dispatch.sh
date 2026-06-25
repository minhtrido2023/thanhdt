#!/usr/bin/env bash
# dispatch.sh <agent_id> "prompt" [--bg]
#
# Run a HEADLESS Claude session as the specified agent. The session inherits the
# agent's CLAUDE.md + hooks (KB context injection, bus writes, heartbeat).
#
# After the agent finishes, auto-runs consolidate.sh so bus findings land in KB
# immediately (no waiting for the 30-min cron). In --bg mode, also pushes a
# Telegram notification via notify.sh.
#
# Default (synchronous): blocks until done, prints Claude's response to stdout.
#   Mike gets the result DIRECTLY + KB is updated. Best for most tasks.
# --bg: background, output to log. Use only for very long tasks (>10 min).
#
# Examples:
#   bin/dispatch.sh Taylor "Phân tích kỹ thuật VNM"
#   bin/dispatch.sh Winston "Kiểm tra corp-action hôm nay" --bg
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE="/home/trido/.local/bin/claude"

id="${1:?usage: dispatch.sh <agent_id> \"prompt\" [--bg]}"
prompt="${2:?usage: dispatch.sh <agent_id> \"prompt\" [--bg]}"
bg="${3:-}"
AGENT_DIR="$ROOT/agents/$id"

if [ ! -d "$AGENT_DIR" ]; then
  echo "ERROR: agent '$id' not found at $AGENT_DIR" >&2
  exit 1
fi

mkdir -p "$ROOT/logs"
ts="$(date -u +%Y%m%d_%H%M%S)"
logfile="$ROOT/logs/dispatch_${id}_${ts}.log"

from="${DISPATCH_FROM:-Mike}"

dispatch_prompt="[DISPATCH từ $from] $prompt

Khi hoàn thành, GHI KẾT QUẢ lên bus bằng:
  $ROOT/bin/append_event.sh $id finding \"<chủ đề>\" '<payload>'
(hoặc decision/answer tùy loại). Đây là phiên headless — kết quả PHẢI nằm trên bus để fleet thấy."

export BQ_LOCAL_CACHE=data/bq_cache
if ! python3 "$ROOT/../preflight_bq_cache.py" --offline >/dev/null 2>&1; then
  echo "WARNING: BQ cache preflight failed — queries will fall back to BQ network" >&2
  unset BQ_LOCAL_CACHE
fi
cd "$AGENT_DIR"

if [ "$bg" = "--bg" ]; then
  # Background wrapper: run agent → consolidate → notify
  _bg_wrapper() {
    "$CLAUDE" -p "$dispatch_prompt" \
      --permission-mode auto \
      --max-turns 50 \
      > "$logfile" 2>&1
    exit_code=$?
    # Push bus → KB immediately
    "$ROOT/bin/consolidate.sh" >> "$ROOT/logs/consolidator.log" 2>&1 || true
    # Notify via Telegram
    if [ $exit_code -eq 0 ]; then
      "$ROOT/bin/notify.sh" "[dispatch] $id hoàn thành: $(head -c 200 "$logfile")" 2>/dev/null || true
    else
      "$ROOT/bin/notify.sh" "[dispatch] $id THẤT BẠI (exit=$exit_code) — xem $logfile" 2>/dev/null || true
    fi
  }
  _bg_wrapper &
  pid=$!
  echo "DISPATCHED $id (pid=$pid) → log: $logfile"
  echo "Khi xong: auto consolidate + Telegram notify."
  echo "$pid" > "$ROOT/logs/.dispatch_${id}_${ts}.pid"
else
  # Synchronous: Mike gets stdout directly
  "$CLAUDE" -p "$dispatch_prompt" \
    --permission-mode auto \
    --max-turns 50 \
    2>"$logfile.err" | tee "$logfile"
  # Push bus → KB immediately after agent finishes
  "$ROOT/bin/consolidate.sh" >> "$ROOT/logs/consolidator.log" 2>&1 || true
fi
