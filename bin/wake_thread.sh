#!/usr/bin/env bash
# wake_thread.sh <thread_id> "<prompt>" [name_suffix]
#
# Actively RESUME a live Discord thread's Claude/Codex session — different from
# notify_thread.sh, which only posts a passive message nobody's session reacts to
# (ccdb's on_message handler ignores anything the bot itself wrote, precisely to
# stop the bot replying to its own notifications). This uses ccdb's scheduler API
# (`POST /api/tasks`, run_immediately=true, one_shot=true, thread_id=<target>) —
# the SAME primitive the harness's own ScheduleWakeup tool is bridged onto
# (mike/kb/... ScheduleWakeup → ccdb SQLite TaskRepository one-shot task), just
# triggered externally instead of from inside a live tool call. ccdb's scheduler
# master loop polls for due tasks every 30s (claude_discord/cogs/scheduler.py,
# MASTER_LOOP_INTERVAL_SECONDS), so a run_immediately task fires within ~30s —
# no 60s floor (that floor is a policy ScheduleWakeup's harness bridge applies
# client-side, not a constraint of the underlying /api/tasks endpoint).
#
# Used by dispatch.sh's _bg_wrapper on job completion (see MIKE.md §8 rev
# 2026-08-15) so a live Mike session waiting on a dispatched job is woken the
# moment the job actually finishes, instead of only via its own blind-interval
# ScheduleWakeup ladder. Kept as a SEPARATE primitive from notify_thread.sh
# (not a replacement) — callers that just want a visible completion message with
# no resume (e.g. informational report channels with no live waiting session)
# should keep using notify_thread.sh; waking a thread with no active waiter
# spins up a brand-new Claude/Codex session there (ccdb starts fresh when no
# session record exists for that thread), which is wasted spend, not a bonus.
#
# Fails soft (never breaks the caller's completion path): unreachable API,
# bad thread_id, or task-name collision all just log to
# logs/wake_thread_errors.log and exit 1. ⚠️ CHƯA có checker nào đọc file log này
# (kiểm chứng 2026-08-20 — câu cũ "ops_health_check.sh reads both" là SAI); lỗi push
# vì thế im lặng hoàn toàn cho tới khi có người tự phát hiện. Đề xuất reconciler:
# agents/Mike/research/wakeup_architecture_redesign_20260820.md
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

thread_id="${1:?usage: wake_thread.sh <thread_id> \"<prompt>\" [name_suffix]}"
prompt="${2:?usage: wake_thread.sh <thread_id> \"<prompt>\" [name_suffix]}"
name_suffix="${3:-$(date +%s%N)}"

if ! [[ "$thread_id" =~ ^[0-9]+$ ]]; then
  echo "wake_thread: thread_id must be numeric, got '$thread_id'" >&2
  exit 1
fi

_log_fail() {
  mkdir -p "$ROOT/logs"
  printf '%s wake_thread: %s | thread_id=%s name_suffix=%s\n' \
    "$(date -Iseconds)" "$1" "$thread_id" "$name_suffix" \
    >> "$ROOT/logs/wake_thread_errors.log"
}

# Ghi CẢ lần push THÀNH CÔNG (2026-08-17) — trước đó chỉ có nhánh lỗi được ghi, nên khi
# audit double-answer phải suy ngược "push có tới không" từ log ccdb ở repo KHÁC. Không có
# dòng thành công thì "push im lặng không chạy" và "push chạy ngon" nhìn giống hệt nhau
# trong logs/ của fleet này.
# `name_suffix` chính là job_id: cả hai call site trong dispatch.sh (_bg_wrapper nhánh done
# và nhánh fail) đều truyền "$job_id" vào tham số 3. Gọi tay không truyền tham số 3 thì đó
# là timestamp tự sinh — vẫn ghi nguyên văn, không bịa.
_log_ok() {
  mkdir -p "$ROOT/logs"
  local _task_id
  # Body thật: {"status":"created","id":<int>} (claude_discord/ext/api_server.py POST
  # /api/tasks). Body lạ/không phải JSON -> '?' chứ KHÔNG bỏ luôn dòng log: biết đã push
  # thành công mà không biết task nào vẫn hơn là không biết gì.
  _task_id="$(printf '%s' "$1" | python3 -c 'import sys,json
try:
    print(json.load(sys.stdin).get("id","?"))
except Exception:
    print("?")' 2>/dev/null)" || _task_id="?"
  [ -n "$_task_id" ] || _task_id="?"
  printf '%s wake_thread: SUCCESS | job_id=%s thread_id=%s task_id=%s\n' \
    "$(date -Iseconds)" "$name_suffix" "$thread_id" "$_task_id" \
    >> "$ROOT/logs/wake_thread.log"
}

if ! out="$(python3 - "$thread_id" "$prompt" "$name_suffix" << 'PY' 2>&1
import sys, json, urllib.request, urllib.error

thread_id, prompt, name_suffix = sys.argv[1], sys.argv[2], sys.argv[3]

# Bash truyền argv theo BYTE; Python decode bằng surrogateescape, nên một chuỗi bị cắt
# giữa ký tự UTF-8 nhiều byte (vd `tail -c 500` trong _bg_wrapper chém đôi một chữ tiếng
# Việt/emoji) mang theo lone surrogate (\udcXX). json.dumps escape nó qua được HTTP, nhưng
# sqlite phía ccdb chết khi INSERT ("surrogates not allowed") — và handler ở đó dán nhãn
# NHẦM mọi lỗi insert thành "409 Task name already exists". Đã ăn 3 lần thật (2026-08-15,
# 08-19, 08-20 — ca 08-20 còn XOÁ mất ladder wakeup đang chờ của thread trước khi chết,
# thread ngủ 12' tới khi user tự phát hiện). Sanitize tại đây = chặn cả class cho MỌI
# caller, không cần restart ccdb. Incident:
# kb/incidents/2026-08/2026-08-20-wake-push-utf8-surrogate-deletes-ladder.md
prompt = prompt.encode("utf-8", "replace").decode("utf-8")
name_suffix = name_suffix.encode("utf-8", "replace").decode("utf-8")
payload = json.dumps({
    "name": f"dispatch-wake-{name_suffix}",
    "prompt": prompt,
    "interval_seconds": 60,
    "channel_id": int(thread_id),
    "thread_id": int(thread_id),
    "run_immediately": True,
    "one_shot": True,
}).encode()
req = urllib.request.Request(
    "http://127.0.0.1:8199/api/tasks",
    data=payload, method="POST",
    headers={"Content-Type": "application/json"},
)
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        print(r.read().decode())
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.read().decode()}", file=sys.stderr)
    sys.exit(1)
except urllib.error.URLError as e:
    print(f"unreachable: {e}", file=sys.stderr)
    sys.exit(1)
PY
)"; then
  _log_fail "$out"
  exit 1
fi
# Ghi log KHÔNG được biến một push đã thành công thành exit 1 (dispatch.sh coi exit != 0 là
# push hỏng) — nhưng cũng không nuốt im lặng: hỏng thì kêu ra stderr.
_log_ok "$out" || echo "wake_thread: push OK nhưng ghi logs/wake_thread.log THẤT BẠI" >&2
echo "$out"
