#!/usr/bin/env bash
# stop_circuit_breaker_selfcheck.sh — kiểm tra hooks/stop.sh's F2 circuit breaker
# (2026-08-19, sau 2 sự cố im lặng 08-13/08-19: job async còn treo, không ai đánh thức lại).
#
# Cái nó phải chứng minh, không phải "hook chạy không lỗi":
#   K1. Khi PHẢI chặn, JSON in ra đúng CONTRACT của Claude Code Stop hook — {"decision":
#       "block", ...} ở TOP LEVEL. Đây là assertion trực tiếp bắt được bug thật đã xảy ra:
#       bản đầu bọc trong {"hookSpecificOutput": {...}} bị harness ÂM THẦM BỎ QUA (variant
#       Stop của hookSpecificOutput chỉ nhận additionalContext, không nhận decision) — hook
#       tưởng đã chặn nhưng lượt vẫn kết thúc bình thường. Assertion cũ (chỉ kiểm tra "có in
#       ra gì đó") KHÔNG bắt được lỗi này; assertion ở đây kiểm tra field "decision" nằm
#       Ở NGOÀI CÙNG của JSON, không nằm trong hookSpecificOutput.
#   K2. ScheduleWakeup gọi TRONG chính lượt đang kết thúc phải được nhận ra — KHÔNG được
#       chặn. ccdb chỉ ghi one-shot task vào DB SAU KHI CLI thoát, mà hook chạy TRONG LÚC
#       CLI còn sống, nên probe ccdb luôn miss với wakeup của CHÍNH lượt này — cơ chế thật
#       phải đọc transcript, không phải hỏi ccdb, cho câu hỏi "lượt NÀY có gọi chưa".
#   K3. Một job scheduled bởi lượt TRƯỚC (không phải lượt này) mà ccdb còn pending -> không
#       chặn (đường dự phòng vẫn hoạt động cho trường hợp không đọc được transcript).
#   K4. Zombie: job kẹt status=running nhưng KHÔNG heartbeat từ lâu (job --bg chết, không
#       deadline để job-reap đóng) -> KHÔNG được chặn mãi mãi (HB_LIVE_BOUND_S).
#   F.  Mọi đường fail-open: không thread, không job, id≠Mike, stop_hook_active=true, API
#       chết, API trả body thiếu field "tasks" (fail-open ĐÚNG, không phải fail-closed ngược
#       — "tasks" vắng mặt ≠ "tasks" rỗng).
#
# Chạy trên sandbox riêng (mktemp -d, symlink cửa trước — pattern claim_reply_selfcheck.sh),
# KHÔNG đụng bus/jobs thật, KHÔNG gọi ccdb thật (mock HTTP server cục bộ trên cổng ngẫu nhiên).
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SB="$(mktemp -d)"
trap 'kill $MOCK_PID_A $MOCK_PID_B $MOCK_PID_C 2>/dev/null; rm -rf "$SB"' EXIT

FAIL=0
assert() { # assert <mô tả> <thực tế> <mong đợi>
  if [ "$2" = "$3" ]; then
    echo "  ok   $1 ($2)"
  else
    echo "  FAIL $1: được '$2', mong đợi '$3'"; FAIL=1
  fi
}

# --- sandbox root: symlink cửa trước (ROOT hardcode trong stop.sh) ---
FAKE="$SB/fakeroot"
mkdir -p "$FAKE/hooks" "$FAKE/bin" "$FAKE/bus/jobs" "$FAKE/bus/registry" "$FAKE/bus/inbox" "$FAKE/logs"
ln -s "$ROOT/hooks/stop.sh" "$FAKE/hooks/stop.sh"
ln -s "$ROOT/hooks/_resolve_id.sh" "$FAKE/hooks/_resolve_id.sh"
ln -s "$ROOT/bin/heartbeat.sh" "$FAKE/bin/heartbeat.sh"
ln -s "$ROOT/bin/mike_json.py" "$FAKE/bin/mike_json.py"

mkjob() { # mkjob <job_id> <status> <thread_id> <started_at_offset_seconds>
  local id="$1" status="$2" tid="$3" off="${4:-0}"
  printf '{"job_id":"%s","from":"Mike","to":"Taylor","status":"%s","discord_thread_id":"%s","started_at":%d}' \
    "$id" "$status" "$tid" "$(( $(date +%s) + off ))" > "$FAKE/bus/jobs/$id.json"
}

# --- mock ccdb tasks API: 3 servers (empty / has-pending-999999 / malformed) ---
cat > "$SB/mockapi.py" <<'PY'
import sys, json
from http.server import BaseHTTPRequestHandler, HTTPServer
MODE, PORT = sys.argv[1], int(sys.argv[2])
class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if MODE == "pending":
            body = {"tasks": [{"enabled": True, "one_shot": True, "thread_id": "999999"}]}
        elif MODE == "malformed":
            body = {"status": "ok"}
        else:
            body = {"tasks": []}
        self.wfile.write(json.dumps(body).encode())
HTTPServer(("127.0.0.1", PORT), H).serve_forever()
PY
_free_port() { python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1]); s.close()'; }
PORT_EMPTY="$(_free_port)"; PORT_PENDING="$(_free_port)"; PORT_MALFORMED="$(_free_port)"
python3 "$SB/mockapi.py" empty "$PORT_EMPTY" & MOCK_PID_A=$!
python3 "$SB/mockapi.py" pending "$PORT_PENDING" & MOCK_PID_B=$!
python3 "$SB/mockapi.py" malformed "$PORT_MALFORMED" & MOCK_PID_C=$!
sleep 0.5
API_EMPTY="http://127.0.0.1:$PORT_EMPTY/api/tasks"
API_PENDING="http://127.0.0.1:$PORT_PENDING/api/tasks"
API_MALFORMED="http://127.0.0.1:$PORT_MALFORMED/api/tasks"
API_DOWN="http://127.0.0.1:1/api/tasks"   # nothing listens on port 1 (privileged, unbindable)

# --- transcript fixtures (format thật: message.role/content, tool_use ScheduleWakeup) ---
T_WITH="$SB/with_sw.jsonl"
cat > "$T_WITH" <<'EOF'
{"message":{"role":"user","content":"do the task"}}
{"message":{"role":"assistant","content":[{"type":"tool_use","id":"t2","name":"ScheduleWakeup","input":{"delaySeconds":300}}]}}
{"message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t2","content":"scheduled"}]}}
{"message":{"role":"assistant","content":[{"type":"text","text":"done"}]}}
EOF
T_WITHOUT="$SB/without_sw.jsonl"
cat > "$T_WITHOUT" <<'EOF'
{"message":{"role":"user","content":"do the task"}}
{"message":{"role":"assistant","content":[{"type":"tool_use","id":"t2","name":"Bash","input":{"command":"echo hi"}}]}}
{"message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t2","content":"hi"}]}}
{"message":{"role":"assistant","content":[{"type":"text","text":"done, no wakeup"}]}}
EOF
T_OLD_TURN="$SB/old_turn.jsonl"
cat > "$T_OLD_TURN" <<'EOF'
{"message":{"role":"user","content":"first task"}}
{"message":{"role":"assistant","content":[{"type":"tool_use","id":"t1","name":"ScheduleWakeup","input":{"delaySeconds":300}}]}}
{"message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t1","content":"scheduled"}]}}
{"message":{"role":"assistant","content":[{"type":"text","text":"ended first turn"}]}}
{"message":{"role":"user","content":"second task, new prompt"}}
{"message":{"role":"assistant","content":[{"type":"text","text":"done with second task, no new wakeup"}]}}
EOF

run() { # run <id> <thread_id> <stop_hook_active> <transcript> <api_url>
  local id="$1" tid="$2" sha="$3" transcript="$4" api="$5"
  local payload
  payload="$(python3 -c 'import json,sys; print(json.dumps({"session_id":"s1","cwd":sys.argv[1],"stop_hook_active":sys.argv[2]=="true","transcript_path":sys.argv[3]}))' "$FAKE" "$sha" "$transcript")"
  printf '%s' "$payload" | DISCORD_THREAD_ID="$tid" WAGS_STOP_TASKS_API="$api" "$FAKE/hooks/stop.sh" "$id" 2>/dev/null
}
is_blocked() { # is_blocked <stdout> -> "1"/"0"; assert đúng CONTRACT (decision Ở TOP LEVEL)
  python3 -c '
import json, sys
raw = sys.stdin.read().strip()
if not raw:
    print("0"); sys.exit(0)
try:
    d = json.loads(raw)
except Exception:
    print("MALFORMED"); sys.exit(0)
# K1: "decision" phải ở TOP LEVEL — {"hookSpecificOutput":{"decision":...}} KHÔNG đếm,
# vì Claude Code bỏ qua field đó cho Stop hook (chỉ đọc top-level).
print("1" if d.get("decision") == "block" else "0")
'
}

echo "== CA A: job sống, KHÔNG ScheduleWakeup lượt này, KHÔNG ccdb pending -> BLOCK, đúng contract top-level"
rm -f "$FAKE/bus/jobs"/*.json
mkjob J1 running 999999 0
OUT="$(run Mike 999999 false "$T_WITHOUT" "$API_EMPTY")"
assert "blocked (top-level decision)" "$(printf '%s' "$OUT" | is_blocked)" "1"
assert "reason không rỗng" "$(printf '%s' "$OUT" | python3 -c 'import json,sys;d=json.load(sys.stdin);print("yes" if d.get("reason") else "no")' 2>/dev/null || echo no)" "yes"

echo "== CA B (K2): ScheduleWakeup gọi TRONG lượt này -> KHÔNG block dù ccdb chưa thấy gì"
OUT="$(run Mike 999999 false "$T_WITH" "$API_EMPTY")"
assert "không block" "$(printf '%s' "$OUT" | is_blocked)" "0"

echo "== CA C: ScheduleWakeup ở lượt TRƯỚC (không phải lượt này) -> vẫn BLOCK"
OUT="$(run Mike 999999 false "$T_OLD_TURN" "$API_EMPTY")"
assert "blocked" "$(printf '%s' "$OUT" | is_blocked)" "1"

echo "== CA D (K3): không ScheduleWakeup lượt này, NHƯNG ccdb có pending task từ lượt trước -> KHÔNG block"
OUT="$(run Mike 999999 false "$T_WITHOUT" "$API_PENDING")"
assert "không block" "$(printf '%s' "$OUT" | is_blocked)" "0"

echo "== CA E: API trả body thiếu field tasks (malformed) -> fail-OPEN, KHÔNG block"
OUT="$(run Mike 999999 false "$T_WITHOUT" "$API_MALFORMED")"
assert "không block (fail-open)" "$(printf '%s' "$OUT" | is_blocked)" "0"

echo "== CA F: API chết hẳn -> fail-OPEN, KHÔNG block"
OUT="$(run Mike 999999 false "$T_WITHOUT" "$API_DOWN")"
assert "không block (fail-open)" "$(printf '%s' "$OUT" | is_blocked)" "0"

echo "== CA G: không có job nào sống trên thread -> KHÔNG block"
rm -f "$FAKE/bus/jobs"/*.json
OUT="$(run Mike 999999 false "$T_WITHOUT" "$API_EMPTY")"
assert "không block" "$(printf '%s' "$OUT" | is_blocked)" "0"

echo "== CA H: không có Discord thread -> KHÔNG block"
mkjob J1 running 999999 0
payload="$(python3 -c 'import json; print(json.dumps({"session_id":"s1","cwd":"'"$FAKE"'","stop_hook_active":False}))')"
OUT="$(printf '%s' "$payload" | WAGS_STOP_TASKS_API="$API_EMPTY" "$FAKE/hooks/stop.sh" Mike 2>/dev/null)"
assert "không block" "$(printf '%s' "$OUT" | is_blocked)" "0"

echo "== CA I: id != Mike -> KHÔNG block (scope guard)"
OUT="$(run Wags 999999 false "$T_WITHOUT" "$API_EMPTY")"
assert "không block" "$(printf '%s' "$OUT" | is_blocked)" "0"

echo "== CA J: stop_hook_active=true -> KHÔNG block (chống vòng lặp)"
OUT="$(run Mike 999999 true "$T_WITHOUT" "$API_EMPTY")"
assert "không block" "$(printf '%s' "$OUT" | is_blocked)" "0"

echo "== CA K (K4): job zombie — status=running từ 2h trước, chưa từng heartbeat -> KHÔNG block (HB_LIVE_BOUND_S)"
rm -f "$FAKE/bus/jobs"/*.json
mkjob J2 running 999999 -7200
OUT="$(run Mike 999999 false "$T_WITHOUT" "$API_EMPTY")"
assert "không block (zombie loại trừ)" "$(printf '%s' "$OUT" | is_blocked)" "0"

echo "== CA L: job mới dispatch (chưa kịp heartbeat, started_at vừa xong) -> VẪN tính là sống -> BLOCK"
rm -f "$FAKE/bus/jobs"/*.json
mkjob J3 running 999999 0
OUT="$(run Mike 999999 false "$T_WITHOUT" "$API_EMPTY")"
assert "blocked (job mới vẫn sống)" "$(printf '%s' "$OUT" | is_blocked)" "1"

echo
if [ "$FAIL" -eq 0 ]; then echo "stop_circuit_breaker_selfcheck: PASS"; else echo "stop_circuit_breaker_selfcheck: FAIL"; fi
exit "$FAIL"
