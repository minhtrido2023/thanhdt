#!/usr/bin/env bash
# append_event.sh <agent_id> <event_type> <topic> <payload_json_or_string> [trace_id]
# Appends one JSONL event to bus/inbox/<agent_id>.jsonl (append-only, one file per child).
# event_id is a real UUID; flock guards this child's own file only (no cross-child contention).
#
# trace_id (optional 5th arg): correlates every event produced during ONE dispatch chain
# (caller -> agent -> auto-callback) so a job's full story can be pulled with one grep
# instead of matching on prompt_summary text. Falls back to $JOB_ID if set (dispatch.sh
# exports it into the headless agent's environment) — an agent calling this script with only
# 4 args still gets traced automatically as long as it's running inside a dispatch job.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUS="$ROOT/bus"
PY="$ROOT/bin/mike_json.py"

id="${1:?usage: append_event.sh <agent_id> <event_type> <topic> <payload> [trace_id]}"
etype="${2:?event_type required (finding|status|question|answer|decision|error)}"
topic="${3:?topic required}"
payload="${4:?payload required (json object/array, or plain string)}"
trace_id="${5:-${JOB_ID:-}}"

# --- Chống WORD-SPLIT im lặng (Wags coord-2026-08-13) ---------------------------------
# Sự cố thật: 13 event / 6 agent trong 1 tháng bị shell cắt payload giữa chừng (payload chứa
# dấu nháy đơn lẻ ⇒ chuỗi '...' của caller đóng sớm). Hậu quả CŨ: phần payload sau chỗ cắt
# thành arg 5 → ghi thẳng vào trace_id ("thêm", "nguoi", "capacity"...), phần còn lại bị vứt
# LẶNG LẼ, và mike_json.py fallback JSON-hỏng→chuỗi nên event vẫn "thành công". Câu hỏi
# question của Mike 2026-08-12 mất nguyên phần đuôi kiểu này. Fail LOUD thay vì ghi rác:
# mất 1 lần gọi (agent thấy lỗi, quote lại rồi gọi lại) rẻ hơn 1 event hỏng vĩnh viễn.
die() { echo "append_event.sh: $*" >&2; exit 1; }

if [ "$#" -gt 5 ]; then
  die "nhận $# tham số (tối đa 5) — payload gần như chắc chắn bị shell word-split.
  Thừa: $(printf '%q ' "${@:6}")
  Sửa: bọc payload trong nháy ĐƠN và escape mọi \"'\" bên trong, hoặc bỏ hẳn nháy đơn khỏi text."
fi

case "$trace_id" in
  "" ) : ;;                       # không có trace_id là hợp lệ
  *[[:space:]]* ) die "trace_id chứa khoảng trắng: $(printf '%q' "$trace_id") — dấu hiệu word-split." ;;
  *[!A-Za-z0-9_.:-]* ) die "trace_id có ký tự lạ: $(printf '%q' "$trace_id") — trace_id hợp lệ dạng <Agent>_<YYYYMMDD>_<HHMMSS>." ;;
esac

# Payload mở đầu bằng { hoặc [ mà không parse được = JSON cụt (bị cắt), KHÔNG phải chuỗi thường.
case "$payload" in
  \{*|\[* )
    python3 -c 'import json,sys; json.loads(sys.argv[1])' "$payload" 2>/dev/null \
      || die "payload bắt đầu bằng '{' hoặc '[' nhưng KHÔNG phải JSON hợp lệ — nhiều khả năng bị cắt cụt.
  Đuôi payload nhận được: ...$(printf '%s' "${payload: -60}")
  Muốn ghi chuỗi thường thì đừng mở đầu bằng { hoặc [." ;;
esac

kbver="$(tr -dc '0-9' < "$ROOT/kb/version.txt" 2>/dev/null || true)"; kbver="${kbver:-0}"
line="$(python3 "$PY" event "$id" "$etype" "$topic" "$payload" "$kbver" "$trace_id")"

mkdir -p "$BUS/inbox"
exec 9>>"$BUS/inbox/$id.jsonl"
flock 9
printf '%s\n' "$line" >&9
echo "appended $etype/$topic for $id"
