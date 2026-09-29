#!/usr/bin/env bash
# user_prompt_submit.sh <agent_id>
# Fires on every prompt the child submits. Injects a TRUE per-agent delta: only the
# events ingested at a KB version newer than this child last saw (short summaries, not
# raw JSON). So a child learns other children's results without re-reading what it
# already saw — ~18× less injected than dumping the full last-20 block every time.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KB="$ROOT/kb"
source "$ROOT/hooks/_resolve_id.sh"   # sets $id from $1 or stdin session_id; exits 0 if excluded

# [now: …] fact injection (§S2.3, discord_time_reasoning_by_construction_plan_20260821.md):
# headless dispatch has no Discord bridge to inject it, so every agent turn gets it here
# instead — same derived time+market fact ccdb shows on the Discord side. Never fails loud.
now_line="$(python3 "$ROOT/bin/now_line.py" 2>/dev/null || true)"
[ -n "$now_line" ] && echo "$now_line"

cur="$(tr -dc '0-9' < "$KB/version.txt" 2>/dev/null || true)"; cur="${cur:-0}"
cache="${XDG_CACHE_HOME:-$HOME/.cache}/mike_kbver_$id"
mkdir -p "$(dirname "$cache")"
seen="$(cat "$cache" 2>/dev/null || echo -1)"

if [ "$cur" != "$seen" ]; then
  printf '%s' "$cur" > "$cache"
  # TRUE delta: only events with ingest-version > what this agent last saw (capped 15).
  delta="$(python3 "$ROOT/bin/mike_json.py" delta-since "$KB/recent_delta.jsonl" "${seen:-0}" 15 2>/dev/null || true)"
  if [ -n "${delta//[[:space:]]/}" ]; then
    # KỶ LUẬT TOPIC (2026-07-22): the delta is fleet-wide — it carries results of work that
    # belongs to OTHER Discord topics. Injecting it bare made Mike narrate topic A's results
    # inside whatever topic the user was currently reading. It stays background knowledge
    # unless it's relevant to what the user asked HERE.
    echo "[Mike KB → v$cur] Kết quả MỚI từ agent khác kể từ lượt trước (dùng luôn, không hỏi lại; chi tiết đầy đủ ở kb/KNOWLEDGE.md)."
    echo "KỶ LUẬT TOPIC: đây là thông tin NỀN fleet-wide, KHÔNG phải nội dung của topic hiện tại. Chỉ nêu ở đây nếu"
    echo "liên quan trực tiếp điều user đang hỏi TẠI topic này; việc thuộc topic khác → báo vào ĐÚNG topic đó"
    echo "(bin/notify_thread.sh \"<msg>\" <thread_id>), không tiện tay kể ở topic user đang đọc:"
    printf '%s\n' "$delta"
  fi
fi

# Surface any NEW directive Mike assigned to this agent (once, via offset cache).
source "$ROOT/hooks/_directives.sh"

# Compact nudge: one-time hint when this session's context exceeds ~300K tokens.
# Uses context_watch.py (reads real token count from transcript usage fields).
# Flag file per agent+session ensures the nudge fires only once.
nudge_flag="${XDG_CACHE_HOME:-$HOME/.cache}/mike_compact_nudged_${id}_${MIKE_SID:-unknown}"
if [ ! -f "$nudge_flag" ] && [ -n "${MIKE_SID:-}" ]; then
  ctx_line="$(python3 "$ROOT/bin/context_watch.py" "$id" 2>/dev/null || true)"
  ctx_tok="$(echo "$ctx_line" | awk '{print $1}')"
  if [ -n "$ctx_tok" ] && [ "$ctx_tok" != "-" ] && [ "$ctx_tok" -gt 300000 ] 2>/dev/null; then
    echo "[⚠ Phiên đã dài (~${ctx_tok} token). Cân nhắc /compact hoặc mở phiên mới để giữ tốc độ + tiết kiệm token.]"
    touch "$nudge_flag"
  fi
fi
exit 0
