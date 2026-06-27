#!/usr/bin/env bash
# dispatch.sh <agent_id> "prompt" [--bg] [--timeout SEC] [--retries N]
#
# Run a HEADLESS Claude session as the specified agent. The session inherits the
# agent's CLAUDE.md + hooks (KB context injection, bus writes, heartbeat).
#
# Every dispatch is tracked as a JOB in bus/jobs/<job_id>.json (running → done /
# failed / timeout). Poll it with bin/jobs.sh — a coordinator never has to block
# blindly. The claude run is wrapped in `timeout` so it can NEVER hang forever.
#
# After the agent finishes, auto-runs consolidate.sh so bus findings land in KB
# immediately (no waiting for the 30-min cron). In --bg mode, also pushes a
# Telegram notification via notify.sh.
#
# Default (synchronous): blocks until done (bounded by --timeout), prints Claude's
#   response to stdout. Best for short tasks where the caller wants the result now.
# --bg: background, output to log; auto-retries once on failure/timeout (--retries),
#   then notifies. Use for long tasks (>5 min) or parallel fan-out — caller returns
#   immediately with a job_id and polls jobs.sh.
#
# Options:
#   --timeout SEC  hard cap per attempt (default 600 = 10 min)
#   --retries N    extra attempts after the first, --bg only (default 1)
#
# Examples:
#   bin/dispatch.sh Taylor "Phân tích kỹ thuật VNM"
#   bin/dispatch.sh Winston "Kiểm tra corp-action hôm nay" --bg --timeout 1200
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Override only for tests; production always uses the real CLI.
CLAUDE="${DISPATCH_CLAUDE_BIN:-/home/trido/.local/bin/claude}"

id="${1:?usage: dispatch.sh <agent_id> \"prompt\" [--bg] [--timeout SEC] [--retries N]}"
prompt="${2:?usage: dispatch.sh <agent_id> \"prompt\" [--bg] [--timeout SEC] [--retries N]}"
shift 2

bg=""
TIMEOUT=600
RETRIES=1
while [ $# -gt 0 ]; do
  case "$1" in
    --bg) bg="--bg" ;;
    --timeout) TIMEOUT="${2:?--timeout needs a value}"; shift ;;
    --timeout=*) TIMEOUT="${1#*=}" ;;
    --retries) RETRIES="${2:?--retries needs a value}"; shift ;;
    --retries=*) RETRIES="${1#*=}" ;;
    *) echo "ERROR: unknown argument '$1'" >&2; exit 1 ;;
  esac
  shift
done

AGENT_DIR="$ROOT/agents/$id"
if [ ! -d "$AGENT_DIR" ]; then
  echo "ERROR: agent '$id' not found at $AGENT_DIR" >&2
  exit 1
fi

mkdir -p "$ROOT/logs"
ts="$(date -u +%Y%m%d_%H%M%S)"
logfile="$ROOT/logs/dispatch_${id}_${ts}.log"
job_id="${id}_${ts}"
JOBS_DIR="$ROOT/bus/jobs"

from="${DISPATCH_FROM:-Mike}"

# _job_watcher: runs in background alongside a dispatch job.
# Every WATCH_INTERVAL seconds, checks job status and sends heartbeat if still running.
# Stops automatically when job reaches a terminal state (done/failed/timeout/not-found).
_job_watcher() {
  local jid="$1" caller="$2" target="$3"
  local interval="${WATCH_INTERVAL:-300}"
  local elapsed=0
  # Capture Discord thread ID at dispatch time (set by ccdb-mike before starting Claude).
  local discord_thread_id
  discord_thread_id="${DISCORD_THREAD_ID:-$(cat "$ROOT/agents/Mike/state/ccdb_thread_id" 2>/dev/null || true)}"
  while true; do
    sleep "$interval" || break
    elapsed=$((elapsed + interval))
    set +e
    python3 "$ROOT/bin/mike_json.py" job-get "$JOBS_DIR" "$jid" >/dev/null 2>&1
    local jrc=$?
    set -e
    [ "$jrc" -eq 2 ] || break  # 0=done 1=failed/timeout 3=overdue 4=not-found → stop
    local elapsed_min=$((elapsed / 60))
    "$ROOT/bin/append_event.sh" "$target" heartbeat "$jid" \
      "{\"status\":\"still_running\",\"elapsed_min\":${elapsed_min},\"job_id\":\"$jid\",\"caller\":\"$caller\"}" 2>/dev/null || true
    # Post to the user's Discord thread if we know its ID.
    if [ -n "$discord_thread_id" ]; then
      "$ROOT/bin/notify_thread.sh" \
        "⏰ **$target** vẫn đang chạy (${elapsed_min}m) — job \`$jid\`. Sẽ notify khi xong." \
        "$discord_thread_id" 2>/dev/null || true
    else
      "$ROOT/bin/notify.sh" "[watcher] $target (job $jid) vẫn chạy sau ${elapsed_min}min — caller: $caller" 2>/dev/null || true
    fi
  done
}

# --- routing guards (added 2026-06-27) ---
# 1) No self-dispatch: an agent spawning a cold headless copy of itself would split its
#    context and double-write its bus/working-memory.
if [ "$from" = "$id" ]; then
  echo "ERROR: self-dispatch blocked ($from -> $id). You are already this agent; just do the work." >&2
  exit 2
fi
# 2) Target Mike only from the user. Mike is the up-escalation / user-facing point, NOT a
#    dispatch target — agents escalate UP via a 'question' event, they do not spawn a cold Mike
#    to orchestrate (that inverts the hierarchy + nests headless sessions). Human override:
#    DISPATCH_FROM=user bin/dispatch.sh Mike "...".
if [ "$id" = "Mike" ] && [ "$from" != "user" ]; then
  echo "ERROR: '$from' cannot dispatch Mike. To reach Mike, ESCALATE:" >&2
  echo "  $ROOT/bin/append_event.sh $from question \"<chủ đề>\" '{\"question\":\"...\",\"options\":[\"A\",\"B\"],\"urgency\":\"normal\"}'" >&2
  echo "  (Mike picks it up → user decides → Mike dispatches back. Human override: DISPATCH_FROM=user.)" >&2
  exit 2
fi

# JSET: merge fields into this job's record (all JSON handling stays in mike_json.py).
JSET() { python3 "$ROOT/bin/mike_json.py" job-set "$JOBS_DIR" "$job_id" "$@"; }
SUMMARY() { head -c 200 "$logfile" 2>/dev/null | tr '\n\t' '  '; }

dispatch_prompt="[DISPATCH từ $from | job=$job_id] $prompt

Khi hoàn thành, GHI KẾT QUẢ lên bus bằng:
  $ROOT/bin/append_event.sh $id finding \"<chủ đề>\" '<payload>'
(hoặc decision/answer tùy loại). Đây là phiên headless — kết quả PHẢI nằm trên bus để fleet thấy.

Heartbeat (bắt buộc): mỗi 4-5 tool call, ghi tiến độ để caller biết bạn còn sống:
  $ROOT/bin/append_event.sh $id heartbeat '$job_id' '{\"status\":\"in_progress\",\"note\":\"<đang làm gì>\"}'"

# Source wc_env.sh so google-cloud-sdk/bin is in PATH (needed by bq CLI + sync_bq_cache verify)
[ -f "$ROOT/../wc_env.sh" ] && source "$ROOT/../wc_env.sh" 2>/dev/null || true
export BQ_LOCAL_CACHE=data/bq_cache
if ! python3 "$ROOT/../preflight_bq_cache.py" --offline >/dev/null 2>&1; then
  echo "WARNING: BQ cache preflight failed — queries will fall back to BQ network" >&2
  unset BQ_LOCAL_CACHE
fi
cd "$AGENT_DIR"

echo "JOB $job_id (from=$from, timeout=${TIMEOUT}s) → $ROOT/bin/jobs.sh status $job_id" >&2

# Record the job in 'running' before the first attempt so it is visible immediately.
_start_ts="$(date +%s)"
JSET job_id="$job_id" from="$from" to="$id" status=running attempt=1 \
     max_attempts=$((RETRIES + 1)) started_at="$_start_ts" \
     deadline=$((_start_ts + TIMEOUT)) logfile="$logfile" \
     prompt_summary="$(printf '%s' "$prompt" | head -c 160 | tr '\n\t' '  ')"

if [ "$bg" = "--bg" ]; then
  # Background wrapper: run agent (with timeout + retry) → consolidate → notify
  _bg_wrapper() {
    local max_attempts=$((RETRIES + 1))
    local attempt=1 rc=0 astart
    JSET pid="$BASHPID"
    while [ "$attempt" -le "$max_attempts" ]; do
      astart="$(date +%s)"
      JSET status=running attempt="$attempt" started_at="$astart" deadline=$((astart + TIMEOUT))
      set +e
      timeout "${TIMEOUT}s" "$CLAUDE" -p "$dispatch_prompt" \
        --permission-mode auto --max-turns 50 > "$logfile" 2>&1
      rc=$?
      set -e
      if [ "$rc" -eq 0 ]; then
        JSET status=done ended_at="$(date +%s)" exit_code=0 result_summary="$(SUMMARY)"
        "$ROOT/bin/consolidate.sh" >> "$ROOT/logs/consolidator.log" 2>&1 || true
        "$ROOT/bin/notify.sh" "[dispatch] $id hoàn thành (job $job_id): $(SUMMARY)" 2>/dev/null || true
        # Auto-callback: notify the caller agent so it can pick up the result without manual prompt.
        # Only when caller is a real companion agent (not Mike/user — they have other channels).
        # GUARD (2026-06-28): a job that is ITSELF an auto-callback must NOT spawn another
        # auto-callback — otherwise two agents ping-pong callbacks forever (runaway loop seen
        # 2026-06-27, Taylor<->Winston). A callback is a terminal notification: process it, stop.
        if [ "$from" != "Mike" ] && [ "$from" != "user" ] && [ -d "$ROOT/agents/$from" ] \
           && [[ "$prompt" != "[AUTO-CALLBACK"* ]]; then
          local cb_summary
          cb_summary="$(head -c 400 "$logfile" 2>/dev/null | tr '\n\t' '  ')"
          DISPATCH_FROM="$id" "$ROOT/bin/dispatch.sh" "$from" \
            "[AUTO-CALLBACK job=$job_id] $id HOÀN THÀNH. Kết quả đầy đủ đã ghi trên bus (KB sẽ cập nhật trong vài giây). Tóm tắt output: $cb_summary" \
            --bg --timeout 300 \
            >> "$ROOT/logs/dispatch_${id}_${ts}.log" 2>&1 || true
        fi
        return 0
      fi
      if [ "$attempt" -lt "$max_attempts" ]; then
        JSET status=retrying exit_code="$rc"
        attempt=$((attempt + 1))
        continue
      fi
      break
    done
    # all attempts exhausted
    local fstatus=failed why="THẤT BẠI"
    if [ "$rc" -eq 124 ]; then fstatus=timeout; why="QUÁ HẠN (timeout ${TIMEOUT}s)"; fi
    JSET status="$fstatus" ended_at="$(date +%s)" exit_code="$rc" result_summary="$(SUMMARY)"
    "$ROOT/bin/consolidate.sh" >> "$ROOT/logs/consolidator.log" 2>&1 || true
    "$ROOT/bin/notify.sh" "[dispatch] $id $why sau $max_attempts lần (job $job_id) — xem $logfile" 2>/dev/null || true
  }
  # Detach the wrapper's std fds so it does NOT hold the caller's stdout pipe open —
  # otherwise `out=$(dispatch.sh ... --bg)` would block until the job finishes (it
  # inherits fd1). The wrapper writes nothing to stdout (claude→logfile, notify/
  # consolidate self-redirect), so /dev/null is safe.
  _bg_wrapper </dev/null >/dev/null 2>&1 &
  pid=$!
  # Watcher: every WATCH_INTERVAL seconds, notify if job is still running.
  _job_watcher "$job_id" "$from" "$id" </dev/null >/dev/null 2>&1 &
  echo "DISPATCHED $id (job=$job_id pid=$pid) → log: $logfile"
  echo "Theo dõi: $ROOT/bin/jobs.sh status $job_id | Khi xong: auto consolidate + Telegram notify."
  echo "$pid" > "$ROOT/logs/.dispatch_${id}_${ts}.pid"
else
  # Synchronous: caller gets stdout directly (bounded by --timeout, no auto-retry)
  # Watcher runs in background and notifies if job takes longer than WATCH_INTERVAL.
  _job_watcher "$job_id" "$from" "$id" </dev/null >/dev/null 2>&1 &
  _wpid=$!
  set +e
  timeout "${TIMEOUT}s" "$CLAUDE" -p "$dispatch_prompt" \
    --permission-mode auto --max-turns 50 \
    2>"$logfile.err" | tee "$logfile"
  rc=${PIPESTATUS[0]}
  set -e
  kill "$_wpid" 2>/dev/null || true  # watcher no longer needed
  # Push bus → KB immediately after agent finishes
  "$ROOT/bin/consolidate.sh" >> "$ROOT/logs/consolidator.log" 2>&1 || true
  if [ "$rc" -eq 0 ]; then
    JSET status=done ended_at="$(date +%s)" exit_code=0 result_summary="$(SUMMARY)"
  else
    fstatus=failed
    if [ "$rc" -eq 124 ]; then
      fstatus=timeout
      echo "WARNING: dispatch $id QUÁ HẠN sau ${TIMEOUT}s (job $job_id) — phiên headless bị kill." >&2
    else
      echo "WARNING: dispatch $id kết thúc bất thường (exit=$rc, job $job_id) — xem $logfile.err" >&2
    fi
    JSET status="$fstatus" ended_at="$(date +%s)" exit_code="$rc" result_summary="$(SUMMARY)"
    exit "$rc"
  fi
fi
