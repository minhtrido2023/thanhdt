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
#
# Usage-limit-aware auto-resume (added 2026-07-03): a failure that looks like the ACCOUNT's
# shared 5-hour usage window (bin/usage_watch.py) is exhausted — not a real task failure —
# is NOT retried/failed normally. It's queued in bus/pending_resumes/ and automatically
# re-dispatched by bin/resume_pending.py (cron, every 10 min) once the window has rolled
# over, capped at DISPATCH_MAX_USAGE_RESUMES (default 3) consecutive resumes. Exit code 5
# (sync mode) or job status "usage_limited" (--bg) signals this — distinct from a real
# failure/timeout. Does not trip the circuit breaker (an account-wide constraint isn't the
# agent's fault). See the _maybe_schedule_usage_resume comment below for the full rationale.
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

# Circuit breaker: after CIRCUIT_THRESHOLD consecutive failed/timeout dispatches to the
# SAME agent, stop dispatching to it for CIRCUIT_COOLDOWN seconds instead of hammering a
# chronically-broken agent (Netflix Hystrix / Nygard "Release It!" pattern). Auto-resets
# on cooldown expiry (one trial allowed). Override for a deliberate manual retry:
# DISPATCH_FORCE=1 bin/dispatch.sh ...
CIRCUIT_DIR="$ROOT/state/circuit"
CIRCUIT_THRESHOLD="${DISPATCH_CIRCUIT_THRESHOLD:-3}"
CIRCUIT_COOLDOWN="${DISPATCH_CIRCUIT_COOLDOWN:-1800}"
if [ "${DISPATCH_FORCE:-}" != "1" ]; then
  set +e
  _cc_out="$(python3 "$ROOT/bin/mike_json.py" circuit-check "$CIRCUIT_DIR" "$id")"
  _cc_rc=$?
  set -e
  if [ "$_cc_rc" -ne 0 ]; then
    echo "ERROR: circuit breaker OPEN for '$id' ($_cc_out) — $CIRCUIT_THRESHOLD+ lỗi liên tiếp, đang cooldown." >&2
    echo "  Bỏ qua dispatch này. Ép chạy bất chấp: DISPATCH_FORCE=1 bin/dispatch.sh $id ..." >&2
    exit 4
  fi
fi

# _circuit_record <agent_id> <success|fail> — call after a dispatch reaches a terminal
# state. On the failure that trips the breaker, notify (Telegram + Discord thread).
_circuit_record() {
  local _cr_out _cr_rc
  set +e
  _cr_out="$(python3 "$ROOT/bin/mike_json.py" circuit-record "$CIRCUIT_DIR" "$1" "$2" "$CIRCUIT_THRESHOLD" "$CIRCUIT_COOLDOWN")"
  _cr_rc=$?
  set -e
  if [ "$2" = "fail" ] && [ "$_cr_rc" -eq 1 ]; then
    "$ROOT/bin/notify.sh" "[circuit-breaker] $1 TRIPPED ($_cr_out) — dispatch tạm dừng ${CIRCUIT_COOLDOWN}s." 2>/dev/null || true
    local _cbtid; _cbtid="${DISCORD_THREAD_ID:-$(_agent_thread_override "$1")}"
    [ -n "$_cbtid" ] || _cbtid="$(cat "$ROOT/agents/Mike/state/ccdb_thread_id" 2>/dev/null || true)"
    if [ -n "$_cbtid" ]; then
      "$ROOT/bin/notify_thread.sh" "🔴 **Circuit breaker OPEN** cho **$1** ($_cr_out) — $CIRCUIT_THRESHOLD+ lỗi liên tiếp, tạm dừng dispatch ${CIRCUIT_COOLDOWN}s. Ép chạy: \`DISPATCH_FORCE=1\`." "$_cbtid" 2>/dev/null || true
    fi
  fi
}

# --- usage-limit-aware auto-resume (added 2026-07-03) ---
# A headless dispatch can fail not because the TASK is broken but because the ACCOUNT's
# shared rolling 5-hour usage window (bin/usage_watch.py) is exhausted — every session on
# this login draws from the same ceiling. Treating that as a normal agent failure is wrong
# twice over: it would wrongly trip the circuit breaker (punishing an agent for an
# account-wide constraint, not its own behavior), and it leaves the task dead until a human
# comes back and re-prompts it manually — exactly the friction the user asked to remove
# (2026-07-03: "task tự động research bị limit token, chờ reset mới chạy tiếp"). Instead:
# detect the usage-limit shape, write a one-shot record to bus/pending_resumes/, and let
# bin/resume_pending.py (cron, every 10 min) re-dispatch automatically once the window
# has rolled over. Capped at DISPATCH_MAX_USAGE_RESUMES consecutive resumes so a GENUINE
# recurring bug can't hide behind "still waiting for reset" forever.
_current_resume_count() {  # parse "[RESUME sau usage-limit #<n> ..." prefix from $prompt, else 0
  if [[ "$prompt" =~ RESUME\ sau\ usage-limit\ \#([0-9]+) ]]; then
    echo "${BASH_REMATCH[1]}"
  else
    echo 0
  fi
}

_looks_like_usage_limit() {  # <logfile> [<err_logfile>] -> 0 if the failure looks usage-limit-shaped
  local lf="$1" ef="${2:-}" tail_text
  tail_text="$(tail -c 4000 "$lf" 2>/dev/null)"
  [ -n "$ef" ] && tail_text="$tail_text$(tail -c 4000 "$ef" 2>/dev/null)"
  if printf '%s' "$tail_text" | grep -qiE \
      'usage limit|rate.?limit|resets at|quota exceeded|limit reached|rate_limit_error|"status":[[:space:]]*429'; then
    return 0
  fi
  # Corroborate with the account-wide estimate — catches wording changes in future CLI
  # versions that the phrase list above doesn't know about yet.
  local pct
  pct="$(python3 "$ROOT/bin/usage_watch.py" --oneline 2>/dev/null | awk '{print $1}')"
  [ -n "$pct" ] && [ "${pct%%.*}" -ge "${DISPATCH_USAGE_LIMIT_PCT:-95}" ] 2>/dev/null
}

_parse_reset_epoch() {  # "HH:MMZ" -> epoch of the next future occurrence (today or tomorrow UTC)
  local hhmm="$1" hh mm today_epoch now_epoch
  [ -z "$hhmm" ] || [ "$hhmm" = "?" ] && return
  hh="${hhmm%%:*}"; mm="${hhmm#*:}"; mm="${mm%Z}"
  now_epoch="$(date +%s)"
  today_epoch="$(date -u -d "today ${hh}:${mm}" +%s 2>/dev/null)" || return
  if [ "$today_epoch" -le "$now_epoch" ]; then
    echo "$((today_epoch + 86400))"
  else
    echo "$today_epoch"
  fi
}

# _maybe_schedule_usage_resume <logfile> [<err_logfile>] -> 0 if a resume WAS scheduled
# (caller must treat this dispatch as "pending", NOT as a real failure/success — skip
# circuit-breaker bookkeeping and auto-callback), 1 if not usage-limit-shaped (or the
# resume cap was hit) -> caller proceeds with normal failure handling.
_maybe_schedule_usage_resume() {
  local lf="$1" ef="${2:-}"
  _looks_like_usage_limit "$lf" "$ef" || return 1
  local n; n="$(_current_resume_count)"
  local cap="${DISPATCH_MAX_USAGE_RESUMES:-3}"
  if [ "$n" -ge "$cap" ]; then
    "$ROOT/bin/notify.sh" "[dispatch] $id: usage-limit-like failure lặp lại $((n + 1)) lần liên tiếp (job $job_id) — DỪNG auto-resume (chạm trần $cap), có thể KHÔNG PHẢI usage limit thật. Cần người kiểm tra: $lf" 2>/dev/null || true
    return 1
  fi
  local reset_hhmm resume_at
  reset_hhmm="$(python3 "$ROOT/bin/usage_watch.py" --oneline 2>/dev/null | awk '{print $4}')"
  resume_at="$(_parse_reset_epoch "$reset_hhmm")"
  [ -n "$resume_at" ] || resume_at=$(( $(date +%s) + 5 * 3600 ))  # unknown reset -> assume full window
  resume_at=$((resume_at + ${DISPATCH_USAGE_RESUME_BUFFER:-600}))
  mkdir -p "$ROOT/bus/pending_resumes"
  printf '%s' "$prompt" | python3 "$ROOT/bin/mike_json.py" pending-resume-set \
    "$ROOT/bus/pending_resumes/${job_id}.json" "$id" "$from" "$job_id" "$resume_at" "$((n + 1))"
  JSET status=usage_limited ended_at="$(date +%s)" \
       result_summary="account usage limit — auto-resume scheduled at epoch $resume_at (attempt $((n + 1))/$cap)"
  local resume_ict; resume_ict="$(TZ=Asia/Ho_Chi_Minh date -d "@$resume_at" '+%H:%M %d/%m' 2>/dev/null || echo '?')"
  "$ROOT/bin/notify.sh" "[dispatch] $id: tài khoản hết usage limit (job $job_id) — KHÔNG PHẢI lỗi task. Tự động resume lúc ~${resume_ict} ICT (lần thử #$((n + 1))/$cap)." 2>/dev/null || true
  local _tid; _tid="${DISCORD_THREAD_ID:-$(_agent_thread_override "$id")}"
  [ -n "$_tid" ] || _tid="$(cat "$ROOT/agents/Mike/state/ccdb_thread_id" 2>/dev/null || true)"
  if [ -n "$_tid" ]; then
    "$ROOT/bin/notify_thread.sh" "⏳ **$id** hết usage limit tài khoản (job \`$job_id\`) — không phải lỗi task. TỰ ĐỘNG resume lúc ~${resume_ict} ICT. Không cần làm gì." "$_tid" 2>/dev/null || true
  fi
  return 0
}

mkdir -p "$ROOT/logs"
ts="$(date -u +%Y%m%d_%H%M%S)"
logfile="$ROOT/logs/dispatch_${id}_${ts}.log"
job_id="${id}_${ts}"
JOBS_DIR="$ROOT/bus/jobs"
export JOB_ID="$job_id"  # picked up by append_event.sh as the default trace_id (see there)

from="${DISPATCH_FROM:-Mike}"

# Per-agent Discord thread override — some agents' output belongs in a fixed topic
# regardless of which thread Mike's live session happens to be active in right now
# (root cause of thread-leak incidents 2026-07-01: dynamic ccdb_thread_id points at
# whatever thread last invoked Mike). Add entries here as the user requests them.
_agent_thread_override() {
  case "$1" in
    DollarBill) echo "1521183164364754974" ;;  # DollarBill trading-plan channel
  esac
}

# _job_watcher: runs in background alongside a dispatch job.
# Two distinct alert tracks:
#   ANOMALY track (fires immediately, no cap): empty log after 60s, stale log >120s with no update.
#   PROGRESS track (milestone only, max 2): 10m and 30m "still running" messages.
# Bus heartbeat fires every 60s poll regardless (internal, not sent to Discord).
_job_watcher() {
  local jid="$1" caller="$2" target="$3" logfile_path="$4"
  local poll=60
  local elapsed=0 discord_notified=0
  local log_stale_alerted=0 log_empty_alerted=0
  local discord_thread_id
  discord_thread_id="${DISCORD_THREAD_ID:-$(_agent_thread_override "$target")}"
  [ -n "$discord_thread_id" ] || discord_thread_id="$(cat "$ROOT/agents/Mike/state/ccdb_thread_id" 2>/dev/null || true)"
  local milestones="600 1800"  # 10 min, 30 min; max 2 Discord progress messages total

  _discord() {
    [ -n "$discord_thread_id" ] \
      && "$ROOT/bin/notify_thread.sh" "$1" "$discord_thread_id" 2>/dev/null || true
  }

  while true; do
    sleep "$poll" || break
    elapsed=$((elapsed + poll))
    set +e
    python3 "$ROOT/bin/mike_json.py" job-get "$JOBS_DIR" "$jid" >/dev/null 2>&1
    local jrc=$?
    set -e
    [ "$jrc" -eq 2 ] || break  # non-running terminal state → stop watching

    local elapsed_min=$((elapsed / 60))

    # Bus heartbeat (internal always)
    "$ROOT/bin/append_event.sh" "$target" heartbeat "$jid" \
      "{\"status\":\"still_running\",\"elapsed_min\":${elapsed_min},\"job_id\":\"$jid\"}" "$jid" 2>/dev/null || true

    # --- ANOMALY track: fast-fail detection ---
    # 1) Log empty at 60s → claude likely never started (auth/quota/crash on init)
    if [ "$elapsed" -eq 60 ] && [ "$log_empty_alerted" -eq 0 ]; then
      if [ ! -s "${logfile_path:-/dev/null}" ]; then
        log_empty_alerted=1
        _discord "⚠️ **$target** job \`$jid\`: log trống sau 60s — claude có thể không start được (auth/quota/crash). Kiểm tra: \`tail $logfile_path\`"
      fi
    fi
    # 2) Log no output after 120s — covers both: empty log (never got output) or stale log
    #    (got some output then froze). The -s check was wrong: empty file is the worst case.
    if [ "$log_stale_alerted" -eq 0 ] && [ "$elapsed" -ge 120 ] && [ -n "${logfile_path:-}" ]; then
      local log_mtime log_age_s
      log_mtime="$(stat -c '%Y' "$logfile_path" 2>/dev/null || echo 0)"
      log_age_s="$(( $(date +%s) - log_mtime ))"
      if [ "$log_age_s" -ge 120 ]; then
        log_stale_alerted=1
        local _why="log không cập nhật ${log_age_s}s"
        [ ! -s "${logfile_path}" ] && _why="log trống ${log_age_s}s (claude start được nhưng chưa ra output)"
        _discord "⚠️ **$target** job \`$jid\`: $_why — có thể bị stuck. Kiểm tra: \`tail $logfile_path\`"
      fi
    fi

    # --- PROGRESS track: milestone only, max 2 ---
    [ "$discord_notified" -lt 2 ] || continue
    local hit=0
    for ms in $milestones; do
      [ "$elapsed" -ge "$ms" ] && [ "$((elapsed - poll))" -lt "$ms" ] && { hit=1; break; }
    done
    [ "$hit" -eq 1 ] || continue
    discord_notified=$((discord_notified + 1))
    _discord "⏰ **$target** vẫn đang chạy (${elapsed_min}m) — job \`$jid\`. Sẽ notify khi xong."
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

Khi hoàn thành, GHI KẾT QUẢ lên bus bằng (tham số cuối '$job_id' là trace_id — LUÔN giữ
nguyên literal này, KHÔNG đổi tên biến — để mọi event của job này gộp lại được thành 1 timeline):
  $ROOT/bin/append_event.sh $id finding \"<chủ đề>\" '<payload>' '$job_id'
(hoặc decision/answer tùy loại). Đây là phiên headless — kết quả PHẢI nằm trên bus để fleet thấy.

Heartbeat (bắt buộc): mỗi 4-5 tool call, ghi tiến độ để caller biết bạn còn sống:
  $ROOT/bin/append_event.sh $id heartbeat '$job_id' '{\"status\":\"in_progress\",\"note\":\"<đang làm gì>\"}' '$job_id'"

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
        _circuit_record "$id" success
        "$ROOT/bin/consolidate.sh" >> "$ROOT/logs/consolidator.log" 2>&1 || true
        "$ROOT/bin/notify.sh" "[dispatch] $id hoàn thành (job $job_id): $(SUMMARY)" 2>/dev/null || true
        # Discord thread notification — always, regardless of who dispatched.
        # Use env var (set at dispatch time, inherited by bg subshell) then fall back to file.
        # tail -c 500: last bytes of log = agent's conclusion, not context-loading preamble.
        local _tid; _tid="${DISCORD_THREAD_ID:-$(_agent_thread_override "$id")}"
        [ -n "$_tid" ] || _tid="$(cat "$ROOT/agents/Mike/state/ccdb_thread_id" 2>/dev/null || true)"
        if [ -n "$_tid" ]; then
          local _preview; _preview="$(tail -c 500 "$logfile" 2>/dev/null | tr '\n\t' '  ')"
          "$ROOT/bin/notify_thread.sh" "✅ **$id** xong (job \`${job_id}\`): $_preview" "$_tid" 2>/dev/null || true
        fi
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
      # Check for a usage-limit-shaped failure on EVERY attempt, not just after retries are
      # exhausted — no point burning the remaining retries immediately against a still-full
      # account window.
      if _maybe_schedule_usage_resume "$logfile"; then
        "$ROOT/bin/consolidate.sh" >> "$ROOT/logs/consolidator.log" 2>&1 || true
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
    _circuit_record "$id" fail
    "$ROOT/bin/consolidate.sh" >> "$ROOT/logs/consolidator.log" 2>&1 || true
    "$ROOT/bin/notify.sh" "[dispatch] $id $why sau $max_attempts lần (job $job_id) — xem $logfile" 2>/dev/null || true
    local _tid; _tid="${DISCORD_THREAD_ID:-$(_agent_thread_override "$id")}"
    [ -n "$_tid" ] || _tid="$(cat "$ROOT/agents/Mike/state/ccdb_thread_id" 2>/dev/null || true)"
    if [ -n "$_tid" ]; then
      "$ROOT/bin/notify_thread.sh" "❌ **$id** $why (job \`${job_id}\`). Xem log: $logfile" "$_tid" 2>/dev/null || true
    fi
    # Also notify the caller agent on failure so it can decide to retry or escalate.
    # Same guard: no callback for auto-callback jobs (prevent loop on failure path too).
    if [ "$from" != "Mike" ] && [ "$from" != "user" ] && [ -d "$ROOT/agents/$from" ] \
       && [[ "$prompt" != "[AUTO-CALLBACK"* ]]; then
      DISPATCH_FROM="$id" "$ROOT/bin/dispatch.sh" "$from" \
        "[AUTO-CALLBACK-FAIL job=$job_id status=$fstatus] $id $why. Kết quả chưa ghi bus. Cần retry hoặc escalate." \
        --bg --timeout 300 \
        >> "$ROOT/logs/dispatch_${id}_${ts}.log" 2>&1 || true
    fi
  }
  # Detach the wrapper's std fds so it does NOT hold the caller's stdout pipe open —
  # otherwise `out=$(dispatch.sh ... --bg)` would block until the job finishes (it
  # inherits fd1). The wrapper writes nothing to stdout (claude→logfile, notify/
  # consolidate self-redirect), so /dev/null is safe.
  #
  # setsid: put the wrapper in its OWN session, detached from the caller's process
  # group/controlling terminal. Without this, a plain `&` background job is still a
  # child of the same session as whoever called dispatch.sh (e.g. Mike's own live
  # Claude Code turn) — if THAT session dies/restarts (context compaction, crash,
  # reconnect), the "background" job can die or become orphaned with it, leaving its
  # job-board entry stuck at status=running forever (incident 2026-07-02: job
  # Taylor_20260702_113418 died this way, 0-byte log, marked OVERDUE, required a
  # fresh re-dispatch). setsid is the standard Unix daemonization primitive for this
  # (see setsid(1); double-fork/detach pattern, Stevens "Advanced Programming in the
  # UNIX Environment").
  #
  # setsid execs a COMMAND (execvp), not a shell function directly — so the function
  # and every variable/function it closes over (JSET, SUMMARY, and the vars they use)
  # must be exported and re-entered via `bash -c`. Verified empirically: a plain
  # `setsid _bg_wrapper &` silently fails to find "_bg_wrapper" as a command.
  export -f _bg_wrapper JSET SUMMARY _agent_thread_override _circuit_record \
            _maybe_schedule_usage_resume _looks_like_usage_limit _parse_reset_epoch \
            _current_resume_count
  export ROOT JOBS_DIR job_id from id ts TIMEOUT RETRIES CLAUDE dispatch_prompt logfile prompt \
         CIRCUIT_DIR CIRCUIT_THRESHOLD CIRCUIT_COOLDOWN
  if command -v setsid >/dev/null 2>&1; then
    setsid bash -c '_bg_wrapper' </dev/null >/dev/null 2>&1 &
  else
    _bg_wrapper </dev/null >/dev/null 2>&1 &
  fi
  disown 2>/dev/null || true
  pid=$!
  # Watcher: milestone progress + anomaly detection (empty/stale log).
  _job_watcher "$job_id" "$from" "$id" "$logfile" </dev/null >/dev/null 2>&1 &
  echo "DISPATCHED $id (job=$job_id pid=$pid) → log: $logfile"
  echo "Theo dõi: $ROOT/bin/jobs.sh status $job_id | Khi xong: auto consolidate + Telegram notify."
  echo "$pid" > "$ROOT/logs/.dispatch_${id}_${ts}.pid"
  # Immediate Discord notify so user sees task is in flight (don't wait for watcher heartbeat)
  { _dtid="${DISCORD_THREAD_ID:-$(_agent_thread_override "$id")}"
    [ -n "$_dtid" ] || _dtid="$(cat "$ROOT/agents/Mike/state/ccdb_thread_id" 2>/dev/null || true)"
    if [ -n "${_dtid:-}" ]; then
      _dp="$(printf '%s' "$prompt" | head -c 120 | tr '\n\t' '  ')"
      "$ROOT/bin/notify_thread.sh" "🚀 **$id** nhận việc (job \`$job_id\`): $_dp… Sẽ notify khi xong." "$_dtid" 2>/dev/null || true
    fi; } &
else
  # Synchronous: caller gets stdout directly (bounded by --timeout, no auto-retry)
  # Watcher runs in background: milestone progress + anomaly detection (empty/stale log).
  _job_watcher "$job_id" "$from" "$id" "$logfile" </dev/null >/dev/null 2>&1 &
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
    _circuit_record "$id" success
  else
    if _maybe_schedule_usage_resume "$logfile" "$logfile.err"; then
      echo "NOTE: dispatch $id (job $job_id) hết usage limit tài khoản — KHÔNG PHẢI lỗi task." >&2
      echo "      Đã tự động lên lịch resume (bin/resume_pending.py sẽ tự chạy lại, không cần làm gì)." >&2
      exit 5
    fi
    fstatus=failed
    if [ "$rc" -eq 124 ]; then
      fstatus=timeout
      echo "WARNING: dispatch $id QUÁ HẠN sau ${TIMEOUT}s (job $job_id) — phiên headless bị kill." >&2
    else
      echo "WARNING: dispatch $id kết thúc bất thường (exit=$rc, job $job_id) — xem $logfile.err" >&2
    fi
    JSET status="$fstatus" ended_at="$(date +%s)" exit_code="$rc" result_summary="$(SUMMARY)"
    _circuit_record "$id" fail
    exit "$rc"
  fi
fi
