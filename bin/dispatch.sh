#!/usr/bin/env bash
# dispatch.sh <agent_id> "prompt" [--bg] [--timeout SEC] [--retries N] [--model NAME] [--effort LEVEL]
#
# Run a HEADLESS Claude session as the specified agent. The session inherits the
# agent's CLAUDE.md + hooks (KB context injection, bus writes, heartbeat).
#
# Every dispatch is tracked as a JOB in bus/jobs/<job_id>.json (running → done /
# failed / timeout). Poll it with bin/jobs.sh — a coordinator never has to block
# blindly. The claude run is wrapped in a HEARTBEAT-AWARE deadline (_hb_aware_timeout,
# 2026-07-09, thay `timeout` cứng): tới hạn TIMEOUT mà heartbeat bus CỦA AGENT còn tươi
# (<DISPATCH_HB_FRESH_S, mặc định 120s) → gia hạn thêm 1 chu kỳ TIMEOUT thay vì giết một
# job đang sống khỏe sắp xong (đã xảy ra 2 lần: Winston_20260707_072729,
# Wags_20260709_134401). Trần tuyệt đối: tối đa DISPATCH_HB_MAX_EXTENSIONS (mặc định 3)
# lần gia hạn = sống tối đa TIMEOUT×(N+1) mỗi attempt — hết trần thì giết thật dù
# heartbeat vẫn tươi (chống heartbeat lặp vô nghĩa che job treo vô hạn). Job không
# heartbeat (treo thật) vẫn chết đúng hạn gốc. Vẫn KHÔNG BAO GIỜ treo vô hạn.
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
#   --timeout SEC  deadline per attempt (default 600 = 10 min). NOT a hard kill: with a
#                  fresh agent heartbeat the deadline extends, up to
#                  DISPATCH_HB_MAX_EXTENSIONS more cycles (see _hb_aware_timeout).
#   --retries N    extra attempts after the first, --bg only (default 1)
#   --model NAME   model alias for this dispatch (sonnet|opus|haiku|fable). Omit to
#                  use the CLI's own default. Model choice is per-DISPATCH, not
#                  per-agent-identity — the same agent (e.g. Taylor) does both
#                  mechanical lookups and deep R&D, so the CALLER judges complexity
#                  per task and passes --model explicitly when it's warranted (see
#                  MIKE.md §Model routing for the 3-question heuristic).
#   --thread ID    pin this job's Discord topic explicitly (highest precedence). Omit and
#                  the topic is resolved by _ambient_thread: per-agent override → ambient
#                  session topic → global last-active pointer. Use when a job legitimately
#                  belongs to a topic other than the dispatching one.
#   --effort LEVEL reasoning effort (low|medium|high|xhigh|max). Omit → 'medium'
#                  (task thường lệ). Task phức tạp → --effort high. CHÍNH SÁCH user
#                  (2026-07-14): model 'fable' bị chặn tối đa 'high' — truyền xhigh/max
#                  cho fable sẽ tự clamp về high + cảnh báo stderr. Xem MIKE.md §Model routing.
# Context injection tier is fixed per AGENT IDENTITY, not per dispatch: each agent's
# own agents/<id>/CLAUDE.md statically imports its role-scoped default — see MIKE.md
# §"Context theo vai trò (role-scoped)" for the full table (Mike/Taylor -> full
# kb/context_pack.md ~35-45KB; DollarBill/Mafee -> context_safety_core + their planning/
# execution mini file + coding_guidelines.md (both own production code); Winston/Spyros
# -> context_safety_core + their mini file; Wendy -> context_mini.md only; Wags ->
# context_ops_mini.md only, ~5KB). This replaced an earlier binary split (cost-opt #1b,
# 2026-07-17: Wags=mini / everyone else=full) the same day it was introduced — the
# table above is the current source of truth, don't infer routing from this comment.
# A dispatch that genuinely needs MORE than an agent's default (e.g. a rare Wags task
# touching trading domain) doesn't need a flag here: every agent has Read tool access,
# so the prompt can just say "đọc kb/context_pack.md nếu cần" and the agent self-serves
# only when actually needed, instead of every dispatch unconditionally paying for it.
#
# Examples:
#   bin/dispatch.sh Taylor "Phân tích kỹ thuật VNM"
#   bin/dispatch.sh Winston "Kiểm tra corp-action hôm nay" --bg --timeout 1200
#   bin/dispatch.sh Taylor "Thiết kế backtest mới, nhiều giả thuyết" --model fable --effort high
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
# Shared usage-limit phrase list (single source of truth, also used by daily_retro.sh).
source "$ROOT/bin/usage_limit_phrases.sh"
# Override only for tests; production always uses the real CLI.
CLAUDE="${DISPATCH_CLAUDE_BIN:-/home/trido/.local/bin/claude}"

id="${1:?usage: dispatch.sh <agent_id> \"prompt\" [--bg] [--timeout SEC] [--retries N]}"
prompt="${2:?usage: dispatch.sh <agent_id> \"prompt\" [--bg] [--timeout SEC] [--retries N]}"
shift 2

bg=""
TIMEOUT=""
RETRIES=1
MODEL=""
EFFORT=""
FORCE_TID=""
while [ $# -gt 0 ]; do
  case "$1" in
    --bg) bg="--bg" ;;
    # --thread: pin this job's Discord topic EXPLICITLY — beats both the per-agent
    # override and the ambient session topic. This is the escape hatch that makes it
    # safe for _agent_thread_override to outrank ambient DISCORD_THREAD_ID
    # (fix 2026-07-22, see the _ambient_thread comment).
    --thread) FORCE_TID="${2:?--thread needs a value}"; shift ;;
    --thread=*) FORCE_TID="${1#*=}" ;;
    --timeout) TIMEOUT="${2:?--timeout needs a value}"; shift ;;
    --timeout=*) TIMEOUT="${1#*=}" ;;
    --retries) RETRIES="${2:?--retries needs a value}"; shift ;;
    --retries=*) RETRIES="${1#*=}" ;;
    --model) MODEL="${2:?--model needs a value}"; shift ;;
    --model=*) MODEL="${1#*=}" ;;
    --effort) EFFORT="${2:?--effort needs a value}"; shift ;;
    --effort=*) EFFORT="${1#*=}" ;;
    *) echo "ERROR: unknown argument '$1'" >&2; exit 1 ;;
  esac
  shift
done

# Per-agent BASE-timeout default — applies only when the caller passed no --timeout.
# DollarBill plan-T+1 jobs do 10-20+ min of real work and emit substantive heartbeats
# only every ~5 min, so the generic 600s base + HB_FRESH_S=120s extension window kills
# them mid-work (real HB is always >120s old at the 600s deadline → no extension).
# Measured 2026-07-13: SpaceX plan needed 725s (survived on a lucky extension), ZaloPay
# plan (job DollarBill_20260713_120124) was killed alive at 600s on BOTH attempts →
# plan_ZaloPay_2026-07-14.json never written, bot had no plan on 07-14. Same mechanism
# as the 07-06 "DollarBill treo" transition-plan timeouts.
if [ -z "$TIMEOUT" ]; then
  case "$id" in
    DollarBill) TIMEOUT="${DISPATCH_TIMEOUT_DOLLARBILL:-1800}" ;;
    *)          TIMEOUT=600 ;;
  esac
fi
case "$MODEL" in
  ""|sonnet|opus|haiku|fable) ;;
  *) echo "ERROR: --model '$MODEL' không hợp lệ — dùng sonnet|opus|haiku|fable." >&2; exit 1 ;;
esac
MODEL_FLAG=""
[ -n "$MODEL" ] && MODEL_FLAG="--model $MODEL"
# Soft nudge (2026-07-17, model-drift incident — see kb/INCIDENTS.md): fable should be
# rare per MIKE.md §Model routing ("dùng dè, không phải mặc định"), but measured
# 2026-07-17 showed 82/94 fable dispatches to Taylor/Winston in one week were Mike
# manually choosing it for routine audit/fix work that the ladder's own tie-break rule
# says belongs at Opus. This is a stderr reminder, not a block — fable is still valid
# when genuinely warranted; the point is to make the ladder's own question visible at
# the moment of choosing, not to prevent the choice.
if [ "$MODEL" = "fable" ]; then
  echo "NOTE: --model fable cho '$id' — xác nhận task này THẬT SỰ cực kỳ phức tạp (vượt tầm" >&2
  echo "  Opus), không phải audit/fix routine. Không chắc → dùng opus (MIKE.md §Model routing)." >&2
fi

# --- Effort policy (2026-07-14, user) ------------------------------------------
# Reasoning-effort per dispatch. Mặc định 'medium' (task thường lệ). Task phức tạp:
# truyền --effort high. Chính sách CỨNG của user: model 'fable' chỉ được tối đa 'high'
# — xhigh/max bị clamp về high (Fable dùng high cho phức tạp, medium cho phần còn lại).
case "$EFFORT" in
  ""|low|medium|high|xhigh|max) ;;
  *) echo "ERROR: --effort '$EFFORT' không hợp lệ — dùng low|medium|high|xhigh|max." >&2; exit 1 ;;
esac
[ -z "$EFFORT" ] && EFFORT="medium"
if [ "$MODEL" = "fable" ] && { [ "$EFFORT" = "xhigh" ] || [ "$EFFORT" = "max" ]; }; then
  echo "WARN: fable giới hạn effort tối đa 'high' (chính sách user) — hạ '$EFFORT'→'high'." >&2
  EFFORT="high"
fi
EFFORT_FLAG="--effort $EFFORT"

# Heartbeat-aware deadline knobs (see _hb_aware_timeout). MAX_EXT bounds the TOTAL
# lifetime of one attempt at TIMEOUT×(MAX_EXT+1) — every worst-case computation below
# (watcher zombie cap, wake-on-completion hint) must use that product, not bare TIMEOUT.
MAX_EXT="${DISPATCH_HB_MAX_EXTENSIONS:-3}"
HB_FRESH_S="${DISPATCH_HB_FRESH_S:-120}"

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
    local _cbtid; _cbtid="$(_job_thread_id "$job_id")"
    [ -n "$_cbtid" ] || _cbtid="$(_ambient_thread "$1")"
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
  # Anchored to the literal start of $prompt (2026-07-30, hardening after incident_lookup.py
  # started inlining kb/INCIDENTS.md excerpts into dispatch prompts): resume_pending.py always
  # places this marker at position 0 (bin/resume_pending.py:55) — an unanchored match could be
  # spoofed by incident text quoting the mechanism itself appearing later in the prompt body.
  if [[ "$prompt" =~ ^\[RESUME\ sau\ usage-limit\ \#([0-9]+) ]]; then
    echo "${BASH_REMATCH[1]}"
  else
    echo 0
  fi
}

_looks_like_usage_limit() {  # <logfile> [<err_logfile>] -> 0 if the failure looks usage-limit-shaped
  local lf="$1" ef="${2:-}" tail_text
  tail_text="$(tail -c 4000 "$lf" 2>/dev/null)"
  [ -n "$ef" ] && tail_text="$tail_text$(tail -c 4000 "$ef" 2>/dev/null)"
  if printf '%s' "$tail_text" | grep -qiE "$USAGE_LIMIT_PHRASE_RE"; then
    return 0
  fi
  # Corroborate with the account-wide estimate — catches wording changes in future CLI
  # versions that the phrase list above doesn't know about yet. NOTE: this only estimates
  # the rolling 5-HOUR window; it CANNOT catch a WEEKLY-cap exhaustion (different ceiling,
  # 5h pct reads low while weekly is blocked) — that case is caught by the phrase list
  # above ("weekly limit"), which is why the shared list is the primary signal.
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
  local _tid; _tid="$(_job_thread_id "$job_id")"
  [ -n "$_tid" ] || _tid="$(_ambient_thread "$id")"
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
    Wags) echo "1521475726329516122" ;;  # Architecture topic — Wags = fleet-ops/coordination
          # role, output luôn thuộc Architecture bất kể Mike dispatch từ topic nào (thêm
          # 2026-07-20 sau feedback user: dispatch Wags cho incident missed-wakeup mà không
          # set DISCORD_THREAD_ID đã khiến notify rơi vào topic Mike đang nói chuyện thay vì
          # Architecture — đúng lỗi §8 vừa sửa: chỉ nhắc trong prose không đủ, cần cơ chế)
  esac
}

# _job_thread_id <job_id> — the Discord topic THIS SPECIFIC job was dispatched from, persisted
# on the job record at dispatch time (added 2026-07-06, fixes cross-topic notification leak).
# Root cause: an agent like Taylor serves MULTIPLE topics (user's "8L research" vs "vĩ mô"
# topics both dispatch to Taylor) — _agent_thread_override only fits an agent whose output
# ALWAYS belongs to ONE fixed topic (DollarBill), and the old env-var/state-file fallback
# chain resolves to whatever topic Mike's LIVE session happens to be in at NOTIFICATION time,
# not the topic that actually asked for this job — so a job dispatched from "8L" while Mike
# later becomes active in "vĩ mô" would report its completion into "vĩ mô" instead. Reading
# the job's OWN persisted field removes this ambiguity regardless of the exact mechanism
# that made a live/global source unreliable (env staleness, restart, concurrent topics, ...).
_job_thread_id() {
  python3 "$ROOT/bin/mike_json.py" job-field "$JOBS_DIR" "$1" discord_thread_id 2>/dev/null
}

# _ambient_thread <agent> — fallback topic when the job record carries no discord_thread_id
# (old in-flight jobs, cron dispatches). Precedence, HIGHEST first:
#   1. _agent_thread_override  — agent whose output ALWAYS belongs to one fixed topic
#   2. $DISCORD_THREAD_ID      — ambient topic of the session that happens to be dispatching
#   3. state/ccdb_thread_id    — global "last topic Mike was active in" (last resort)
#
# The override MUST outrank the ambient env (fixed 2026-07-22). Before this, the chain was
# `${DISCORD_THREAD_ID:-$(_agent_thread_override ...)}` — env FIRST — which made the override
# dead code in practice, because Mike's live session ALWAYS has DISCORD_THREAD_ID set to
# whatever topic the user is currently chatting in. Measured evidence on the job board:
# Wags jobs were pinned across 6 different topics (only 9/27 to Architecture) and DollarBill
# across 5, despite both being declared single-topic agents. Net effect for the user: work
# discussed in topic A got reported into topic B simply because Mike happened to be dispatching
# from B. Explicit `--thread <id>` still beats the override when a caller really means it.
_ambient_thread() {
  local _t
  _t="$(_agent_thread_override "$1")"
  [ -n "$_t" ] || _t="${DISCORD_THREAD_ID:-}"
  [ -n "$_t" ] || _t="$(cat "$ROOT/agents/Mike/state/ccdb_thread_id" 2>/dev/null || true)"
  printf '%s' "$_t"
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
  discord_thread_id="$(_job_thread_id "$jid")"
  [ -n "$discord_thread_id" ] || discord_thread_id="$(_ambient_thread "$target")"
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

    # Hard lifetime cap (2026-07-09, cùng đợt fix cgroup-detach): watcher giờ được
    # detach khỏi cgroup caller nên KHÔNG còn bị dọn "nhờ" caller chết nữa — nếu record
    # kẹt 'running' vĩnh viễn (wrapper bị SIGKILL/OOM, không kịp finalize) thì watcher
    # sẽ bất tử + heartbeat 60s/lần giữ HB_AGE tươi giả tạo, che đúng tín hiệu triage
    # cần thấy. Quá deadline worst-case + 15' → bản thân đó LÀ anomaly: báo 1 lần rồi dừng.
    if [ "$elapsed" -gt $((TIMEOUT * (MAX_EXT + 1) * (RETRIES + 1) + 900)) ]; then
      _discord "🧟 **$target** job \`$jid\`: record vẫn 'running' quá deadline worst-case +15m — wrapper có thể bị kill cứng (SIGKILL/OOM), record kẹt. Kiểm tra: \`$ROOT/bin/jobs.sh status $jid\`"
      break
    fi

    local elapsed_min=$((elapsed / 60))

    # Bus heartbeat (internal always). source=watcher: this ping proves the WATCHER is
    # alive, not the agent — job-hb-age (heartbeat-aware deadline) filters it out so a
    # hung agent can't look alive by proxy. status=still_running doubles as the legacy
    # marker for the same filter.
    "$ROOT/bin/append_event.sh" "$target" heartbeat "$jid" \
      "{\"status\":\"still_running\",\"elapsed_min\":${elapsed_min},\"job_id\":\"$jid\",\"source\":\"watcher\"}" "$jid" 2>/dev/null || true

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

# _hb_aware_timeout <cmd...> — drop-in replacement for `timeout ${TIMEOUT}s <cmd...>`
# (added 2026-07-09, user-approved 'heartbeat-aware-deadline'; incidents
# Winston_20260707_072729 + Wags_20260709_134401: hard timeout killed jobs whose bus
# heartbeat was fresh to the minute — alive, working, nearly done).
#
# Behavior at each TIMEOUT deadline:
#   * Last AGENT bus event < HB_FRESH_S old → the job is demonstrably working: extend
#     the deadline one more TIMEOUT cycle instead of killing. Reads
#     `mike_json.py job-hb-age` which EXCLUDES _job_watcher liveness pings — the watcher
#     pings every 60s no matter what the agent does, so counting them would keep every
#     genuinely-hung job "fresh" forever (that filter is the whole safety of this design).
#   * Absolute cap: MAX_EXT extensions, then kill even with a fresh heartbeat — total
#     lifetime ≤ TIMEOUT×(MAX_EXT+1). A pathological agent that only emits heartbeats
#     while making no progress cannot live past the cap.
#   * No/stale heartbeat at the deadline → kill on schedule (no mercy for a real hang).
# Exit 124 on any deadline kill — same contract as timeout(1), so every rc==124 branch
# downstream (retry, status=timeout, notify wording) keeps working unchanged.
_hb_aware_timeout() {
  local grace="${DISPATCH_KILL_GRACE_S:-10}"
  local ext=0 pid now deadline hb waited
  # setsid: child gets its OWN process group (pgid=pid) so the deadline kill below can
  # take the WHOLE tree with `kill -- -pid`. Killing only the direct pid leaves orphaned
  # grandchildren alive — and in the sync path an orphan holding the inherited stdout
  # keeps the `| tee` pipe open, blocking dispatch.sh long past the kill (found in the
  # 2026-07-09 verification run: hung-job test blocked ~300s on exactly this).
  if command -v setsid >/dev/null 2>&1; then
    setsid "$@" &
  else
    "$@" &
  fi
  pid=$!
  deadline=$(( $(date +%s) + TIMEOUT ))
  while kill -0 "$pid" 2>/dev/null; do
    now="$(date +%s)"
    if [ "$now" -ge "$deadline" ]; then
      hb="$(python3 "$ROOT/bin/mike_json.py" job-hb-age "$JOBS_DIR" "$job_id" 2>/dev/null || echo '-')"
      if [ "$ext" -lt "$MAX_EXT" ] && [[ "$hb" =~ ^-?[0-9]+$ ]] && [ "$hb" -lt "$HB_FRESH_S" ]; then
        ext=$((ext + 1))
        deadline=$((now + TIMEOUT))
        JSET deadline="$deadline" hb_extensions="$ext" 2>/dev/null || true
        # Trace the extension on the bus. source=watcher: this event must NOT itself
        # count as agent liveness at the next deadline (job-hb-age filters it out).
        "$ROOT/bin/append_event.sh" "$id" status "$job_id" \
          "{\"status\":\"deadline_extended\",\"hb_age_s\":$hb,\"extension\":$ext,\"max_ext\":$MAX_EXT,\"source\":\"watcher\"}" \
          "$job_id" >/dev/null 2>&1 || true
        continue
      fi
      # Group kill first (whole tree), direct-pid kill as fallback when the child is
      # not a group leader (setsid missing).
      kill -TERM -- "-$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null || true
      waited=0
      while [ "$waited" -lt "$grace" ] && kill -0 "$pid" 2>/dev/null; do
        sleep 1; waited=$((waited + 1))
      done
      kill -KILL -- "-$pid" 2>/dev/null || kill -KILL "$pid" 2>/dev/null || true
      wait "$pid" 2>/dev/null
      return 124
    fi
    sleep 5
  done
  wait "$pid"
}

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
# discord_thread_id: capture the CALLING topic ONCE, here, at dispatch time — every
# notification for this job reads it back via _job_thread_id instead of re-deriving a
# "current" topic later (see _job_thread_id comment for why that was the actual bug).
_start_ts="$(date +%s)"
_dtid0="${FORCE_TID:-$(_ambient_thread "$id")}"
# …and hand that SAME pinned topic to the agent process itself (fix 2026-07-22b).
# Without this the child `claude` merely inherited the DISPATCHING session's ambient
# DISCORD_THREAD_ID, so the job record said topic A while the agent's own
# `notify_thread.sh` (no explicit thread arg) resolved topic B = whatever topic the user
# was chatting/reading in. That is the user-visible complaint ("phản hồi rơi vào topic
# đang đọc"): the parent's ✅/❌ notice landed correctly, the agent's own report did not.
# The gap WIDENED after commit b3e9fe8, which made _agent_thread_override and --thread
# outrank the ambient env for the job record only — record and agent env then disagreed
# by construction for Wags/DollarBill and for every `--thread` dispatch.
# Exporting here also makes any peer dispatch the agent issues inherit the job's topic
# (via _ambient_thread) instead of the caller's ambient one.
# ROUND 2 (arch-reviewer objection): this export ALSO armed three Mike-only branches in
# hooks/session_start.sh that used "DISCORD_THREAD_ID is set" as their proxy for "this is the
# user's LIVE Discord session". `dispatch.sh Mike` from cron (daily_retro.sh, kb_nightly.sh)
# would then clobber the global ccdb pointer, post "🟢 Đã resume xong" into whatever topic the
# user last opened, and lose the job-board fail-open that b3e9fe8 kept on purpose.
# Fixed at the CONSUMER — session_start.sh now derives INTERACTIVE_TID, gating those branches
# on the absence of $JOB_ID (exported above for dispatched runs only) — not by exempting
# id=Mike here: the stale proxy was the root cause, and an id-keyed exemption would leave the
# job record and the agent's env disagreeing for Mike alone, which is the exact class of bug
# this commit chain exists to remove.
if [ -n "$_dtid0" ]; then export DISCORD_THREAD_ID="$_dtid0"; fi
JSET job_id="$job_id" from="$from" to="$id" status=running attempt=1 \
     max_attempts=$((RETRIES + 1)) started_at="$_start_ts" \
     deadline=$((_start_ts + TIMEOUT)) logfile="$logfile" discord_thread_id="$_dtid0" \
     model="${MODEL:-default}" effort="$EFFORT" \
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
      _hb_aware_timeout "$CLAUDE" -p "$dispatch_prompt" \
        --permission-mode auto --max-turns 50 $MODEL_FLAG $EFFORT_FLAG > "$logfile" 2>&1
      rc=$?
      set -e
      if [ "$rc" -eq 0 ]; then
        JSET status=done ended_at="$(date +%s)" exit_code=0 result_summary="$(SUMMARY)"
        _circuit_record "$id" success
        "$ROOT/bin/consolidate.sh" >> "$ROOT/logs/consolidator.log" 2>&1 || true
        "$ROOT/bin/notify.sh" "[dispatch] $id hoàn thành (job $job_id): $(SUMMARY)" 2>/dev/null || true
        # Discord thread notification — always, regardless of who dispatched. Read the
        # topic THIS job was dispatched from (persisted at dispatch time), not whatever
        # topic Mike happens to be active in right now (see _job_thread_id comment).
        # tail -c 500: last bytes of log = agent's conclusion, not context-loading preamble.
        local _tid; _tid="$(_job_thread_id "$job_id")"
        [ -n "$_tid" ] || _tid="$(_ambient_thread "$id")"
        if [ -n "$_tid" ]; then
          # DollarBill's plan-generation jobs route straight into the user-facing plan
          # channel (_agent_thread_override) — a raw tail-c-500 preview strips newlines
          # and cuts mid-sentence, which only looks acceptable for a short HOLD summary
          # and reads as garbled/incomplete for longer multi-order reports (incident
          # 2026-07-08: ZaloPay's genuinely detailed summary got chopped mid-word by the
          # 500-char window while SpaceX's short HOLD summary happened to survive intact).
          # send_plan_report.sh already posts the authoritative structured render to this
          # same channel later the same day — this ping only needs to confirm completion.
          if [ "$id" = "DollarBill" ]; then
            # User feedback 2026-07-08: state the 19:30 ICT time explicitly so a short
            # completion ping is never mistaken for "nothing else is coming" — the full
            # structured report (targets/prices/reasons) always follows at that time.
            "$ROOT/bin/notify_thread.sh" "✅ **DollarBill** đã lập plan xong (job \`${job_id}\`) — report chi tiết (mục tiêu mua/bán, giá dự kiến, lý do) sẽ đăng vào kênh này lúc **19:30 ICT** hôm nay." "$_tid" 2>/dev/null || true
          else
            local _preview; _preview="$(tail -c 500 "$logfile" 2>/dev/null | tr '\n\t' '  ')"
            "$ROOT/bin/notify_thread.sh" "✅ **$id** xong (job \`${job_id}\`): $_preview" "$_tid" 2>/dev/null || true
          fi
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
    local _tid; _tid="$(_job_thread_id "$job_id")"
    [ -n "$_tid" ] || _tid="$(_ambient_thread "$id")"
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
  # LIFETIME DETACH — session is NOT enough, the job must leave the caller's CGROUP
  # (fix 2026-07-09, incident Taylor_20260708_170202 + 2 more in 3 days):
  #   * setsid detaches only the SESSION (controlling terminal / process group). The
  #     child still inherits the caller's systemd cgroup. Every service here runs with
  #     KillMode=control-group (the default), so when the caller's service restarts —
  #     e.g. ccdb-mike.service, the Discord bridge that spawns Mike's turns — systemd
  #     SIGTERM/SIGKILLs EVERY pid left in that cgroup, setsid or not. That is exactly
  #     how --bg jobs kept dying with the bridge and their job records stayed stuck at
  #     status=running forever (never finalized).
  #   * systemd-run --user --scope moves the child into its OWN transient run-*.scope
  #     cgroup under user@.service, fully outside the caller's unit. Verified
  #     empirically 2026-07-09: a scoped child SURVIVES `systemctl --user stop` of a
  #     fake parent service, while a setsid-only child is killed (see
  #     kb/INCIDENTS.md 2026-07-09). --scope forks/execs the command itself, so the
  #     exported functions and env below carry over exactly like a normal fork
  #     (verified: exported bash functions resolve inside the scope).
  #   * The systemd-run middleman stays in the caller's cgroup and may be killed with
  #     it — harmless: it does not forward SIGTERM to the scoped child (verified).
  #   * Fallback chain: no systemd-run / no reachable user manager (rare: cron without
  #     XDG_RUNTIME_DIR, non-systemd box) → setsid (old behavior) → plain &.
  #     DISPATCH_CGROUP_DETACH=0 forces the setsid path (escape hatch for debugging).
  #
  # Both spawn paths exec a COMMAND (execvp), not a shell function directly — so the
  # function and everything it closes over (JSET, SUMMARY, and the vars they use)
  # must be exported and re-entered via `bash -c`. Verified empirically: a plain
  # `setsid _bg_wrapper &` silently fails to find "_bg_wrapper" as a command.
  export -f _bg_wrapper _job_watcher JSET SUMMARY _agent_thread_override _ambient_thread _circuit_record \
            _maybe_schedule_usage_resume _looks_like_usage_limit _parse_reset_epoch \
            _current_resume_count _job_thread_id _hb_aware_timeout
  export ROOT JOBS_DIR job_id from id ts TIMEOUT RETRIES CLAUDE dispatch_prompt logfile prompt \
         CIRCUIT_DIR CIRCUIT_THRESHOLD CIRCUIT_COOLDOWN MODEL_FLAG EFFORT_FLAG MAX_EXT HB_FRESH_S
  # systemd-run --user needs the user manager socket; cron strips XDG_RUNTIME_DIR.
  export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
  _detach_ok=0
  if [ "${DISPATCH_CGROUP_DETACH:-1}" != "0" ] \
     && command -v systemd-run >/dev/null 2>&1 \
     && systemd-run --user --scope --quiet --collect /bin/true >/dev/null 2>&1; then
    _detach_ok=1
  fi
  _detached_spawn() {  # $1 = bash command string, $2 = human description
    if [ "$_detach_ok" = "1" ]; then
      systemd-run --user --scope --quiet --collect --description="$2" \
        bash -c "$1" </dev/null >/dev/null 2>&1 &
    elif command -v setsid >/dev/null 2>&1; then
      setsid bash -c "$1" </dev/null >/dev/null 2>&1 &
    else
      bash -c "$1" </dev/null >/dev/null 2>&1 &
    fi
  }
  _detached_spawn '_bg_wrapper' "mike-dispatch $job_id ($from → $id)"
  disown 2>/dev/null || true
  pid=$!
  # Watcher: milestone progress + anomaly detection (empty/stale log). Detached the
  # same way — if it stayed in the bridge cgroup it would die on bridge restart while
  # the job lives on, silencing the bus heartbeats that jobs.sh HB_AGE triage relies
  # on (job would look TREO while actually running).
  _detached_spawn '_job_watcher "$job_id" "$from" "$id" "$logfile"' "mike-dispatch-watcher $job_id"
  disown 2>/dev/null || true
  echo "DISPATCHED $id (job=$job_id pid=$pid) → log: $logfile"
  echo "Theo dõi: $ROOT/bin/jobs.sh status $job_id | Khi xong: auto consolidate + Telegram notify."
  # Fast wake-on-completion snippet (MIKE.md §Quy chuẩn 8; sửa 2026-07-07 incident
  # agent-wrapper-monitor-gap): cơ chế CHÍNH = ScheduleWakeup poll NGẮN lặp lại (~240-270s) —
  # không phụ thuộc schema Agent tool. Harness Fable-5 (Mike restart 2026-07-06) đã BỎ tham số
  # run_in_background khỏi Agent tool; isolation:worktree KHÔNG phải background (chỉ cách ly git
  # worktree, agent vẫn đồng bộ, tin nhắn cuối là kênh trả kết quả duy nhất — wrapper "sẽ báo
  # lại" không bao giờ báo lại được). Wrapper Agent nền CHỈ dùng nếu schema phiên hiện tại thật
  # sự có tham số nền. In sẵn để khỏi soạn lại từ trí nhớ — BẮT BUỘC ngay sau dispatch này.
  _ww=$((TIMEOUT * (MAX_EXT + 1) * (RETRIES + 1) + 60))
  echo "⚠️ BẮT BUỘC ngay sau dispatch này (MIKE.md §8, sửa 2026-07-07 — Agent tool KHÔNG còn run_in_background):" >&2
  echo "  1) CƠ CHẾ CHÍNH: ScheduleWakeup THÍCH ỨNG — 3 lần tỉnh ĐẦU ~240-270s (bắt job xong sớm); từ lần thứ 4 trở đi mà job vẫn running thì TĂNG DẦN (240→480→900→trần 1200s), không quay lại ngắn trừ khi có job MỚI phát sinh trong batch. Mỗi lần tỉnh chạy '$ROOT/bin/jobs.sh status $job_id'; chưa done → đặt lại wakeup theo bậc thang; done → xử lý ngay. KHÔNG đặt 1 lần chờ dài (worst-case chờ tối đa ~${_ww}s vẫn phủ qua nhiều lần poll)." >&2
  echo "  2) CHỈ nếu schema tool phiên này THẬT SỰ có tham số nền (run_in_background trên Agent/Bash) mới thêm wrapper bọc '$ROOT/bin/jobs.sh wait $job_id --timeout $_ww'. isolation:worktree KHÔNG phải background — cấm dùng thay thế." >&2
  echo "  3) SELF-CHECK: trước khi nói với user bất kỳ điều gì về trạng thái job này (đang chờ/xong/chết), chạy '$ROOT/bin/jobs.sh status $job_id' trong CÙNG turn — không nói từ trí nhớ." >&2
  echo "$pid" > "$ROOT/logs/.dispatch_${id}_${ts}.pid"
  # Immediate Discord notify so user sees task is in flight (don't wait for watcher heartbeat)
  { _dtid="$(_job_thread_id "$job_id")"
    [ -n "$_dtid" ] || _dtid="$(_ambient_thread "$id")"
    if [ -n "${_dtid:-}" ]; then
      _dp="$(printf '%s' "$prompt" | head -c 120 | tr '\n\t' '  ')"
      "$ROOT/bin/notify_thread.sh" "🚀 **$id** nhận việc (job \`$job_id\`): $_dp… Sẽ notify khi xong." "$_dtid" 2>/dev/null || true
    fi; } &
else
  # Synchronous: caller gets stdout directly (bounded by --timeout, no auto-retry)
  # Watcher runs in background: milestone progress + anomaly detection (empty/stale log).
  _job_watcher "$job_id" "$from" "$id" "$logfile" </dev/null >/dev/null 2>&1 &
  _wpid=$!
  # If dispatch.sh itself is killed mid-run (e.g. the caller's Bash tool 2-minute
  # timeout SIGTERMs the whole process group — incident 2026-07-09,
  # DollarBill_20260709_125326), finalize the job record instead of leaving it stuck
  # at status=running forever. Best-effort: a straight SIGKILL cannot be trapped.
  _sync_killed_guard() {
    trap - TERM INT HUP
    JSET status=failed ended_at="$(date +%s)" exit_code=143 \
         result_summary="KILLED: dispatch.sh sync bị kill giữa chừng (caller chết/Bash-tool timeout?) — job record finalize bởi trap, không phải agent tự kết thúc" \
         2>/dev/null || true
    kill "$_wpid" 2>/dev/null || true
    exit 143
  }
  trap _sync_killed_guard TERM INT HUP
  set +e
  _hb_aware_timeout "$CLAUDE" -p "$dispatch_prompt" \
    --permission-mode auto --max-turns 50 $MODEL_FLAG $EFFORT_FLAG \
    2>"$logfile.err" | tee "$logfile"
  rc=${PIPESTATUS[0]}
  set -e
  trap - TERM INT HUP  # claude finished — normal finalize below owns the record now
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
