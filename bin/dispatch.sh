#!/usr/bin/env bash
# dispatch.sh <agent_id> "prompt" [--bg] [--timeout SEC] [--retries N] [--model NAME] [--effort LEVEL] [--max-turns N]
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
# notification via notify.sh (Discord #mikefleet — CÙNG bridge với notify_thread.sh, không
# phải kênh độc lập).
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
#   --thread NAME|ID  pin this job's Discord topic explicitly (highest precedence). NHẬN TÊN
#                  trong kb/discord_channels.json (vd `--thread architecture`) hoặc ID trần.
#                  TÊN SAI / không phân giải được ⇒ **HUỶ CẢ DISPATCH** (exit 1), không âm
#                  thầm rơi về topic khác — caller đã nêu đích danh 1 topic thì không đoán
#                  (2026-08-02). Bỏ cờ này ⇒ _ambient_thread: override theo agent → topic
#                  phiên gọi → con trỏ toàn cục. Registry hỏng khi agent CÓ override ⇒ pin
#                  RỖNG + job VẪN CHẠY (không chặn việc vì lỗi định tuyến thông báo) + ghi
#                  logs/notify_thread_errors.log để ops_health_check báo lên. Pin rỗng ⇒ im
#                  lặng phía Discord, không bao giờ đoán topic.
#   --effort LEVEL reasoning effort (low|medium|high|xhigh|max). Omit → 'medium'
#                  (task thường lệ). Task phức tạp → --effort high. CHÍNH SÁCH user
#                  (2026-07-14): model 'fable' bị chặn tối đa 'high' — truyền xhigh/max
#                  cho fable sẽ tự clamp về high + cảnh báo stderr. Xem MIKE.md §Model routing.
#   --max-turns N  override trần lượt tool-call. Mặc định SCALE theo --effort khi omit
#                  (high->80, xhigh/max->120, còn lại 50 — thêm 2026-08-02). Task ước
#                  lượng chạm/vượt trần → cân nhắc TĂNG THÊM THỦ CÔNG THAY VÌ chia task nếu
#                  các phần phụ thuộc lẫn nhau (không chia được sạch); ngược lại, ưu tiên
#                  chia thành nhiều dispatch độc lập theo ranh giới tự nhiên (mỗi phần tự
#                  commit+report) — chia rẻ hơn nâng trần vô hạn vì mỗi dispatch giữ được
#                  toàn bộ lượt cho ĐÚNG 1 việc. Nếu vẫn hết lượt giữa chừng: dispatch.sh TỰ
#                  ĐỘNG nâng trần + retry (trong-vòng-lặp, rồi qua bus/pending_resumes/ nếu
#                  hết attempt — xem _maybe_schedule_maxturns_resume), không cần làm gì thêm;
#                  chỉ cân nhắc tự tăng --max-turns thủ công khi ĐÃ THẤY job đó tự-resume mà
#                  vẫn không đủ (DISPATCH_MAX_TURNS_RESUMES mặc định 2 lần rồi dừng).
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
MAX_TURNS=""
PROVIDER=""
while [ $# -gt 0 ]; do
  case "$1" in
    --bg) bg="--bg" ;;
    # --provider: CLI nao chay job nay (claude|opencode|codex...). Bo qua => default_provider
    # trong kb/cli_providers.json (= claude) ⇒ MOI lenh dispatch cu chay y nguyen.
    # Ten sai / provider dang tat / agent khong duoc phep ⇒ HUY dispatch (exit 1), KHONG bao
    # gio am tham roi ve claude — cung ky luat voi --thread (2026-08-02).
    --provider) PROVIDER="${2:?--provider needs a value}"; shift ;;
    --provider=*) PROVIDER="${1#*=}"
                  [ -n "$PROVIDER" ] || { echo "ERROR: --provider= rong (bien chua set?)" >&2; exit 1; } ;;
    --max-turns) MAX_TURNS="${2:?--max-turns needs a value}"; shift ;;
    --max-turns=*) MAX_TURNS="${1#*=}" ;;
    # --thread: pin this job's Discord topic EXPLICITLY — beats both the per-agent
    # override and the ambient session topic. This is the escape hatch that makes it
    # safe for _agent_thread_override to outrank ambient DISCORD_THREAD_ID
    # (fix 2026-07-22, see the _ambient_thread comment).
    --thread) FORCE_TID="${2:?--thread needs a value}"; shift ;;
    # `--thread=` (rỗng) phải BÁO LỖI y như `--thread ""`, đừng âm thầm tụt về ambient —
    # caller gõ `--thread=$MISSING_VAR` là đang NÊU ĐÍCH DANH 1 topic, không phải bỏ trống
    # (arch-reviewer vòng cuối F6, 2026-08-02).
    --thread=*) FORCE_TID="${1#*=}"
                [ -n "$FORCE_TID" ] || { echo "ERROR: --thread= rỗng (biến chưa set?) — nêu tên topic hoặc bỏ hẳn cờ này." >&2; exit 1; } ;;
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
# --- Provider resolution (2026-08-03, multi-CLI) --------------------------------
# Danh sach model/effort hop le KHONG con hardcode o day — moi provider tu khai trong
# kb/cli_providers.json. `validate` kiem: enabled + allow_agents + model thuoc provider +
# effort hop le, va tra ve effort DA CLAMP (effort_caps, vd fable<=high).
# KHONG tu dich tier giua provider (--model opus KHONG tu thanh gpt-5.1-codex) — do dung la
# lop su co model-drift 07-17. Sai model cho provider ⇒ exit 1.
if [ -z "$PROVIDER" ]; then
  PROVIDER="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['default_provider'])" \
              "$ROOT/kb/cli_providers.json" 2>/dev/null || echo claude)"
fi
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
[ -z "$EFFORT" ] && EFFORT="medium"
# Cong provider DUY NHAT: enabled + allow_agents + model hop le cho provider + effort hop le,
# tra ve effort DA CLAMP (fable<=high van duoc giu, nay khai trong registry `effort_caps`
# thay vi hardcode o day). Fail => HUY dispatch, khong am tham roi ve claude.
if ! _eff_clamped="$("$ROOT/bin/cli_provider.sh" validate "$PROVIDER" "$id" "$MODEL" "$EFFORT")"; then
  echo "ERROR: HUY dispatch — provider '$PROVIDER' khong nhan job nay (ly do o tren)." >&2
  exit 1
fi
[ -n "$_eff_clamped" ] && EFFORT="$_eff_clamped"
EFFORT_FLAG="--effort $EFFORT"
# Binary + env cua provider. `bin` da ap dung bin_env_override (DISPATCH_CLAUDE_BIN...) nen
# bin/dispatch_discord_topic_selfcheck.sh van lai duoc dispatch qua stub (F11 arch-reviewer).
CLI_BIN="$("$ROOT/bin/cli_provider.sh" bin "$PROVIDER")" || { echo "ERROR: khong phan giai duoc binary cua provider '$PROVIDER'." >&2; exit 1; }
# default_model: provider khai model mac dinh rieng (vd opencode -> deepseek free tier).
# Chi ap khi caller KHONG truyen --model. claude de null => giu nguyen hanh vi cu (omit co
# => khong truyen --model => CLI lay tu agents/<id>/.claude/settings.json).
if [ -z "$MODEL" ]; then
  _defmodel="$("$ROOT/bin/cli_provider.sh" field "$PROVIDER" default_model 2>/dev/null || true)"
  [ -n "$_defmodel" ] && MODEL="$_defmodel"
fi
CLI_PROFILE="$("$ROOT/bin/cli_provider.sh" field "$PROVIDER" profile 2>/dev/null || echo claude-native)"
CLI_SUPPORTS_TURNS="$("$ROOT/bin/cli_provider.sh" field "$PROVIDER" supports_turns 2>/dev/null || echo true)"
CLI_USAGE_PROBE="$("$ROOT/bin/cli_provider.sh" field "$PROVIDER" usage_probe 2>/dev/null || true)"
CLI_MAXTURNS_PAT="$("$ROOT/bin/cli_provider.sh" field "$PROVIDER" max_turns_pattern 2>/dev/null || true)"
# env bo sung (pin interpreter cho CLI dang shim node — xem registry _README).
while IFS= read -r _envline; do
  [ -n "$_envline" ] && export "${_envline?}"
done < <("$ROOT/bin/cli_provider.sh" env-exports "$PROVIDER" 2>/dev/null)
# Giu ten bien cu: mot so nhanh/ban ghi van tham chieu $CLAUDE.
CLAUDE="$CLI_BIN"

# --- Max-turns override (2026-07-31, sau sự cố Winston_20260731_062642 fail "Reached
# max turns (50)" 2 lần liên tiếp cho 1 task gộp 3 deliverable độc lập — 50 là hằng số
# cứng không có lối thoát, dù nội dung thật đã gần xong khi kiểm tay). Caller vẫn có thể
# nâng thủ công khi biết trước task cần nhiều lượt hơn (cost-opt #3 ở MIKE.md).
#
# Mặc định SCALE theo effort khi omit (thêm 2026-08-02, sau 5 job fail max-turns cùng
# 1 ngày — tất cả đều effort=high/opus, cả 2 attempt trong loop retry DÙNG CHUNG 1 trần
# 50 nên attempt 2 tạch giống hệt attempt 1, đúng kiểu "chạy tới chạy lui" vô ích user
# nêu). effort=high đã tự khai "việc phức tạp" qua ladder MIKE.md §Model routing — tận
# dụng tín hiệu có sẵn thay vì bắt Mike nhớ ước lượng + truyền --max-turns tay mỗi lần
# (thực tế đã KHÔNG xảy ra đủ, bằng chứng là 5 job fail hôm nay không job nào override).
case "$MAX_TURNS" in
  "")
    case "$EFFORT" in
      high) MAX_TURNS=80 ;;
      xhigh|max) MAX_TURNS=120 ;;
      *) MAX_TURNS=50 ;;
    esac
    ;;
  *[!0-9]*) echo "ERROR: --max-turns '$MAX_TURNS' phải là số nguyên dương." >&2; exit 1 ;;
  *) ;;
esac

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
# Khoa breaker theo AGENT+PROVIDER, khong phai agent khong (sua 2026-08-03, arch-reviewer F10).
# Neu chi theo agent: opencode hong 3 lan lien tiep se KHOA LUON Taylor tren claude — tuc mot
# provider phu lam dung viec production tren provider chinh. claude giu nguyen ten khoa cu
# ("Taylor") de khong mat trang thai breaker lich su dang co trong state/circuit/.
if [ "$PROVIDER" = "claude" ]; then CIRCUIT_KEY="$id"; else CIRCUIT_KEY="${id}@${PROVIDER}"; fi
if [ "${DISPATCH_FORCE:-}" != "1" ]; then
  set +e
  _cc_out="$(python3 "$ROOT/bin/mike_json.py" circuit-check "$CIRCUIT_DIR" "$CIRCUIT_KEY")"
  _cc_rc=$?
  set -e
  if [ "$_cc_rc" -ne 0 ]; then
    echo "ERROR: circuit breaker OPEN for '$CIRCUIT_KEY' ($_cc_out) — $CIRCUIT_THRESHOLD+ lỗi liên tiếp, đang cooldown." >&2
    echo "  Bỏ qua dispatch này. Ép chạy bất chấp: DISPATCH_FORCE=1 bin/dispatch.sh $id ..." >&2
    exit 4
  fi
fi

# _circuit_record <agent_id> <success|fail> — call after a dispatch reaches a terminal
# state. On the failure that trips the breaker, notify (#mikefleet qua notify.sh + Discord thread).
_circuit_record() {
  local _cr_out _cr_rc
  set +e
  _cr_out="$(python3 "$ROOT/bin/mike_json.py" circuit-record "$CIRCUIT_DIR" "$1" "$2" "$CIRCUIT_THRESHOLD" "$CIRCUIT_COOLDOWN")"
  _cr_rc=$?
  set -e
  if [ "$2" = "fail" ] && [ "$_cr_rc" -eq 1 ]; then
    "$ROOT/bin/notify.sh" "[circuit-breaker] $1 TRIPPED ($_cr_out) — dispatch tạm dừng ${CIRCUIT_COOLDOWN}s." 2>/dev/null || true
    local _cbtid; _cbtid="$(_job_thread_id "$job_id")"
    # Không suy lại topic (2026-08-02, arch-reviewer S1) — chỉ đọc pin. Xem chú thích ở
    # điểm ghim: pin rỗng ⇒ im lặng phía Discord, KHÔNG đoán topic. notify.sh ở trên vẫn bắn vào
    # #mikefleet — cùng bridge Discord, nên nó KHÔNG cứu được ca bridge chết.
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
  #
  # ⚠️ PROBE THEO PROVIDER (sua 2026-08-03, arch-reviewer): bin/usage_watch.py doc
  # ~/.claude/projects = usage cua CLAUDE. Dung no lam doi chung cho provider KHAC la doc
  # NHAM TAI KHOAN: 1 job opencode/codex fail vi ly do bat ky, dung luc quota claude >=95%,
  # se bi phan loai nham "usage-limited" -> day vao bus/pending_resumes/ -> hen resume theo
  # GIO RESET CUA CLAUDE, va co y KHONG trip circuit breaker => job hong that lang le retry
  # roi im. usage_probe=null (opencode/codex) => CHI dung phrase-match o tren.
  [ -n "${CLI_USAGE_PROBE:-}" ] || return 1
  local pct
  pct="$(python3 "$ROOT/$CLI_USAGE_PROBE" --oneline 2>/dev/null | awk '{print $1}')"
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
  # Gio reset cung phai lay tu probe CUA PROVIDER — khong co probe thi KHONG DOAN gio reset,
  # roi ve buffer 5h mac dinh o dong duoi (cung ly do §5.4 o _looks_like_usage_limit).
  reset_hhmm=""
  [ -n "${CLI_USAGE_PROBE:-}" ] && \
    reset_hhmm="$(python3 "$ROOT/$CLI_USAGE_PROBE" --oneline 2>/dev/null | awk '{print $4}')"
  resume_at="$(_parse_reset_epoch "$reset_hhmm")"
  [ -n "$resume_at" ] || resume_at=$(( $(date +%s) + 5 * 3600 ))  # unknown reset -> assume full window
  resume_at=$((resume_at + ${DISPATCH_USAGE_RESUME_BUFFER:-600}))
  mkdir -p "$ROOT/bus/pending_resumes"
  # Truyen day du kind/model/effort/provider (sua 2026-08-03): nhanh usage_limit truoc day
  # chi truyen 6 tham so nen MODEL/EFFORT bi mat khi resume — trai voi chinh docstring cua
  # resume_pending.py. Thieu `provider` thi job opencode se resume bang CLAUDE kem --model
  # cua opencode => cong provider tu choi (exit 1) => task mat im (arch-reviewer F9).
  printf '%s' "$prompt" | python3 "$ROOT/bin/mike_json.py" pending-resume-set \
    "$ROOT/bus/pending_resumes/${job_id}.json" "$id" "$from" "$job_id" "$resume_at" "$((n + 1))" \
    "usage_limit" "${MODEL:-}" "$EFFORT" "" "$PROVIDER"
  JSET status=usage_limited ended_at="$(date +%s)" \
       result_summary="account usage limit — auto-resume scheduled at epoch $resume_at (attempt $((n + 1))/$cap)"
  local resume_ict; resume_ict="$(TZ=Asia/Ho_Chi_Minh date -d "@$resume_at" '+%H:%M %d/%m' 2>/dev/null || echo '?')"
  "$ROOT/bin/notify.sh" "[dispatch] $id: tài khoản hết usage limit (job $job_id) — KHÔNG PHẢI lỗi task. Tự động resume lúc ~${resume_ict} ICT (lần thử #$((n + 1))/$cap)." 2>/dev/null || true
  local _tid; _tid="$(_job_thread_id "$job_id")"
  # KHÔNG suy lại topic ở đây (sửa 2026-08-02, arch-reviewer S1): chỉ đọc field đã GHIM lúc
  # dispatch. Trước đây `[ -n "$X" ] || X="$(_ambient_thread ...)"` khiến pin rỗng rơi về topic
  # ambient của dispatcher — đúng cơ chế rò rỉ. Pin rỗng ⇒ IM LẶNG phía Discord, không bao giờ
  # đoán topic. (KHÔNG có kênh dự phòng độc lập nào ở đây: `notify.sh` cũng đi qua CÙNG bridge
  # Discord 127.0.0.1:8199 — xem chú thích tại nhánh "registry hỏng" bên dưới.)
  if [ -n "$_tid" ]; then
    "$ROOT/bin/notify_thread.sh" "⏳ **$id** hết usage limit tài khoản (job \`$job_id\`) — không phải lỗi task. TỰ ĐỘNG resume lúc ~${resume_ict} ICT. Không cần làm gì." "$_tid" 2>/dev/null || true
  fi
  return 0
}

# _maybe_fallback_provider_on_usage_limit <logfile> [<err_logfile>] -> 0 nếu ĐÃ fallback
# sang claude (caller coi job này là "handled", không phải fail thật); 1 nếu không áp dụng
# (không phải usage-limit-shaped, hoặc dispatch này vốn đã là claude — không có gì để
# fallback TỪ).
#
# User mandate 2026-08-03: task dùng provider phụ (opencode/deepseek...) hết usage/rate
# limit → CHUYỂN NGAY sang claude, KHÔNG xếp hàng chờ cùng provider như
# _maybe_schedule_usage_resume làm cho claude. Lý do khác nhau về BẢN CHẤT, không phải
# cùng 1 cơ chế đổi tên: claude có cửa sổ 5h/tuần với giờ reset DỰ ĐOÁN ĐƯỢC (usage_watch.py
# đọc trực tiếp), nên "chờ rồi thử lại đúng provider đó" là hợp lý. Provider phụ có
# usage_probe=null (kb/cli_providers.json) — KHÔNG có cách nào biết khi nào quota thật sự
# hồi, nên "chờ 5h rồi thử lại" chỉ là đoán mù, dễ tạch lại y hệt cho tới khi chạm trần
# DISPATCH_MAX_USAGE_RESUMES rồi bó tay — trong khi claude là quota ĐỘC LẬP, luôn sẵn sàng
# ngay lập tức. PHẢI gọi hàm này TRƯỚC _maybe_schedule_usage_resume ở mọi call site (thứ
# tự if/elif quyết định provider phụ đi fallback-ngay, claude thật đi chờ-resume).
_maybe_fallback_provider_on_usage_limit() {
  local lf="$1" ef="${2:-}"
  [ -n "${PROVIDER:-}" ] && [ "$PROVIDER" != "claude" ] || return 1
  _looks_like_usage_limit "$lf" "$ef" || return 1
  JSET status=provider_fallback ended_at="$(date +%s)" \
       result_summary="provider '$PROVIDER' hết usage/rate limit — fallback NGAY sang claude (quota độc lập, không chờ)"
  local _fb_argv=("$ROOT/bin/dispatch.sh" "$id" "[FALLBACK provider->claude sau usage-limit, job gốc=$job_id] $prompt" --bg --timeout "$TIMEOUT")
  [ -n "${EFFORT:-}" ] && _fb_argv+=(--effort "$EFFORT")
  DISPATCH_FROM="$from" "${_fb_argv[@]}" >> "$ROOT/logs/dispatch_${id}_${ts}.log" 2>&1 || true
  "$ROOT/bin/notify.sh" "[dispatch] $id: provider '$PROVIDER' hết usage/rate limit (job $job_id) — đã fallback NGAY sang claude (không chờ, quota độc lập)." 2>/dev/null || true
  local _tid; _tid="$(_job_thread_id "$job_id")"
  if [ -n "$_tid" ]; then
    "$ROOT/bin/notify_thread.sh" "🔀 **$id** provider '$PROVIDER' hết usage/rate limit (job \`$job_id\`) — đã tự chuyển sang claude ngay, không chờ reset." "$_tid" 2>/dev/null || true
  fi
  return 0
}

# --- Max-turns auto-continuation (2026-08-02, user mandate: 5 job fail "Reached max
# turns (50)" trong 1 ngày, tất cả effort=high, cả 2 attempt trong retry loop dùng
# CHUNG 1 trần nên attempt 2 tạch giống hệt attempt 1 — retry vô ích, đúng "chạy tới
# chạy lui" user mô tả). Mirrors _maybe_schedule_usage_resume's shape/contract (0 =
# resume scheduled, treat as pending not failed; 1 = not this failure type or cap hit)
# nhưng khác 2 điểm: (a) resume NGAY, không có "giờ reset" nào phải chờ; (b) mỗi lần
# resume NÂNG --max-turns thay vì giữ nguyên — hết lượt là tín hiệu NGÂN SÁCH xác định,
# không phải lỗi thoáng qua đáng thử lại y hệt.
_looks_like_max_turns() {
  local lf="$1"
  # "Reached max turns" la wording RIENG cua Claude CLI. Moi provider khai pattern cua no
  # trong kb/cli_providers.json (max_turns_pattern); null/rong = provider KHONG co khai niem
  # turn-cap (vd opencode, codex) => khong bao gio khop, ca nhanh auto-resume nang tran bi
  # BO HAN thay vi bia ra mot luoi an toan khong ton tai.
  [ -n "${CLI_MAXTURNS_PAT:-}" ] || return 1
  [ -f "$lf" ] && grep -qi "$CLI_MAXTURNS_PAT" "$lf" 2>/dev/null
}

MAXTURNS_CEILING="${DISPATCH_MAX_TURNS_CEILING:-200}"

_bumped_max_turns() {  # next ceiling for a max-turns-triggered retry/resume — doubles, capped
  local next=$((MAX_TURNS * 2))
  [ "$next" -gt "$MAXTURNS_CEILING" ] && next=$MAXTURNS_CEILING
  echo "$next"
}

_current_maxturns_resume_count() {  # same anchoring discipline as _current_resume_count
  if [[ "$prompt" =~ ^\[RESUME\ sau\ max-turns\ \#([0-9]+) ]]; then
    echo "${BASH_REMATCH[1]}"
  else
    echo 0
  fi
}

_maybe_schedule_maxturns_resume() {
  local lf="$1" ef="${2:-}"
  _looks_like_max_turns "$lf" || { [ -n "$ef" ] && _looks_like_max_turns "$ef"; } || return 1
  local n; n="$(_current_maxturns_resume_count)"
  local cap="${DISPATCH_MAX_TURNS_RESUMES:-2}"
  if [ "$n" -ge "$cap" ]; then
    "$ROOT/bin/notify.sh" "[dispatch] $id: hết turn-budget lặp lại $((n + 1)) lần liên tiếp (job $job_id, trần đã tới $MAX_TURNS) — DỪNG auto-resume (chạm trần $cap lần). Task có thể quá lớn để tự chia — cần người xem lại, cân nhắc chia thủ công thành nhiều dispatch độc lập (rẻ hơn nâng trần vô hạn). Log: $lf" 2>/dev/null || true
    return 1
  fi
  local bumped; bumped="$(_bumped_max_turns)"
  local resume_at=$(( $(date +%s) + 30 ))
  mkdir -p "$ROOT/bus/pending_resumes"
  printf '%s' "$prompt" | python3 "$ROOT/bin/mike_json.py" pending-resume-set \
    "$ROOT/bus/pending_resumes/${job_id}.json" "$id" "$from" "$job_id" "$resume_at" "$((n + 1))" \
    "max_turns" "${MODEL:-}" "$EFFORT" "$bumped" "$PROVIDER"
  JSET status=maxturns_pending ended_at="$(date +%s)" \
       result_summary="hết turn budget (--max-turns=$MAX_TURNS) — auto-resume ngay với --max-turns=$bumped (lần thử #$((n + 1))/$cap)"
  "$ROOT/bin/notify.sh" "[dispatch] $id: hết turn budget (job $job_id, --max-turns=$MAX_TURNS) — KHÔNG PHẢI lỗi nội dung. Tự động resume NGAY với trần cao hơn (--max-turns=$bumped, lần thử #$((n + 1))/$cap)." 2>/dev/null || true
  local _tid; _tid="$(_job_thread_id "$job_id")"
  if [ -n "$_tid" ]; then
    "$ROOT/bin/notify_thread.sh" "⏳ **$id** hết turn budget (job \`$job_id\`) — không phải lỗi nội dung, chỉ hết lượt tool-call (--max-turns=$MAX_TURNS). TỰ ĐỘNG resume NGAY với trần cao hơn (--max-turns=$bumped)." "$_tid" 2>/dev/null || true
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
# Tên topic tra qua kb/discord_channels.json (registry duy nhất) — không viết ID trần.
# PHÂN BIỆT 2 TRƯỜNG HỢP (arch-reviewer S2, 2026-08-02): "agent này KHÔNG có override" (return 0,
# rỗng — hợp lệ, đi tiếp xuống ambient) vs "CÓ override nhưng registry hỏng/mất" (return 1 —
# TUYỆT ĐỐI không được tụt xuống ambient). Bản trước gộp cả hai thành chuỗi rỗng, nên registry
# hỏng sẽ âm thầm biến override cố định của Wags/DollarBill thành topic ambient — chính là lỗi
# 2026-07-22 "override thành dead-code" tái sinh dưới trigger mới.
_agent_thread_override() {
  local _name=""
  case "$1" in
    DollarBill) _name=plan_approval ;;  # DollarBill trading-plan channel
    Wags) _name=architecture ;;  # Architecture topic — Wags = fleet-ops/coordination
          # role, output luôn thuộc Architecture bất kể Mike dispatch từ topic nào (thêm
          # 2026-07-20 sau feedback user: dispatch Wags cho incident missed-wakeup mà không
          # set DISCORD_THREAD_ID đã khiến notify rơi vào topic Mike đang nói chuyện thay vì
          # Architecture — đúng lỗi §8 vừa sửa: chỉ nhắc trong prose không đủ, cần cơ chế)
    *) return 0 ;;                      # không có override cho agent này — hợp lệ
  esac
  local _id
  if ! _id="$("$ROOT/bin/discord_channel.sh" "$_name" 2>&1)"; then
    echo "dispatch: registry HỎNG — không phân giải được override '$_name' cho $1: $_id" >&2
    # Câu "dispatch bị CHẶN" ở đây SAI từ vòng 3 (F4 đã đổi sang VẪN CHẠY) — sửa 2026-08-02
    # vòng 5. Và bản thân lời gọi này gần như chắc chắn KHÔNG tới nơi: notify.sh →
    # notify_discord.sh cũng phân giải `mikefleet` qua CHÍNH registry đang hỏng (`set -e` ⇒
    # chết trước curl). Vẫn gọi (rẻ, cứu được ca registry hỏng CỤC BỘ cho 1 tên), nhưng đường
    # báo THẬT cho ca này là dòng ghi logs/notify_thread_errors.log ở chỗ gọi (xem F4).
    "$ROOT/bin/notify.sh" "[dispatch] registry Discord HỎNG: không phân giải được '$_name' cho $1 — job VẪN CHẠY nhưng KHÔNG có topic (không đoán); mọi thông báo Discord của job này bị mất." 2>/dev/null || true
    return 1
  fi
  printf '%s' "$_id"
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
# `|| true` KHÔNG PHẢI trang trí (sửa 2026-08-02, arch-reviewer vòng cuối, F2): mike_json.py
# `job-field` EXIT 1 khi field RỖNG, mà `_bg_wrapper` bật lại `set -e` tường minh giữa chừng ⇒
# mọi call site dạng `local _tid; _tid="$(_job_thread_id ...)"` GIẾT CẢ WRAPPER khi pin rỗng,
# làm mất AUTO-CALLBACK báo kết quả/thất bại về agent đã gọi việc (đo được: pin rỗng ⇒ 1 job
# record, pin có ⇒ 2). "Pin rỗng ⇒ im lặng phía Discord" chỉ đúng khi pin rỗng là GIÁ TRỊ hợp
# lệ (chuỗi rỗng), không phải một lỗi làm sập luồng điều phối.
_job_thread_id() {
  python3 "$ROOT/bin/mike_json.py" job-field "$JOBS_DIR" "$1" discord_thread_id 2>/dev/null || true
}

# _ambient_thread <agent> — fallback topic when the job record carries no discord_thread_id
# (old in-flight jobs, cron dispatches). Precedence, HIGHEST first:
#   1. _agent_thread_override  — agent whose output ALWAYS belongs to one fixed topic
#   2. $DISCORD_THREAD_ID      — ambient topic of the session that happens to be dispatching
# Hết. KHÔNG có tầng 3.
#
# TẦNG 3 `state/ccdb_thread_id` ("topic Mike mở phiên gần nhất") BỎ HẲN 2026-08-02, vòng 4
# (arch-reviewer, B1) — đây mới là ĐIỀU KIỆN TỒN TẠI của cả 4 sự cố rò rỉ, không phải các
# consumer. Ba vòng trước đều gỡ tầng đoán ở nơi TIÊU THỤ, nhưng chính NƠI SINH RA pin vẫn
# đoán: tầng 3 chỉ kích hoạt khi $DISCORD_THREAD_ID rỗng = đúng ngữ cảnh CRON, nơi "topic Mike
# mở gần nhất" không có quan hệ nhân quả nào với job. Tệ hơn bản gốc ở chỗ cú đoán được GHIM
# thành pin, trông như sự thật đã chốt, nên không consumer nào phát hiện được nữa.
# Bằng chứng đo trên job board: cùng một dòng cron daily_retro `30 17 * * *` ghim HAI topic KHÁC
# nhau trong 2 ngày liên tiếp (job Mike_20260801_173001 vs Mike_20260802_173001), cả hai đều
# NGOÀI registry. (ID cụ thể xem kb/incidents/2026-08/2026-08-02-discord-channel-registry.md —
# không chép ID trần vào code, đó chính là thứ discord_id_gate chặn.)
# Nay: cron không nêu topic ⇒ pin RỖNG ⇒ im lặng phía Discord cho job đó. (Fleet CÓ Telegram
# thật, nhưng đó là đường RIÊNG của pipeline trading — bot_execute/crisis_alert_push — không đi
# qua dispatch, nên KHÔNG được viện dẫn nó để biện minh cho im lặng ở đây.) Cron nào
# THẬT SỰ cần báo vào 1 topic thì nêu ĐÍCH DANH `--thread <tên>` (đã thêm cho daily_retro.sh,
# weekly_ops_audit.sh, check_report_cadence.sh) — nêu đích danh là hợp lệ, đoán thì không.
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
  # return 1 = registry hỏng (KHÔNG phải "không có override") ⇒ lan lỗi lên caller để ABORT,
  # tuyệt đối không rơi xuống ambient (arch-reviewer S2, 2026-08-02).
  _t="$(_agent_thread_override "$1")" || return 1
  [ -n "$_t" ] || _t="${DISCORD_THREAD_ID:-}"
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
  # KHÔNG suy lại topic ở đây (sửa 2026-08-02, arch-reviewer S1): chỉ đọc field đã GHIM lúc
  # dispatch. Trước đây `[ -n "$X" ] || X="$(_ambient_thread ...)"` khiến pin rỗng rơi về topic
  # ambient của dispatcher — đúng cơ chế rò rỉ. Pin rỗng ⇒ IM LẶNG phía Discord, không bao giờ
  # đoán topic. (KHÔNG có kênh dự phòng độc lập nào ở đây: `notify.sh` cũng đi qua CÙNG bridge
  # Discord 127.0.0.1:8199 — xem chú thích tại nhánh "registry hỏng" bên dưới.)
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
# MIKE_JOB_OWNER: "lệnh ghi này là dispatch.sh đang finalize ĐÚNG job của mình", không phải
# một lệnh ứng biến gõ tay từ bên ngoài. Đây là chỗ DUY NHẤT cần đánh dấu vì mọi ghi hợp lệ
# của dispatch.sh đều đi qua JSET.
# ⚠️ Biến môi trường KHÔNG phải bằng chứng — ai cũng export được, tin nó là xoá sổ guard. Nó
# chỉ là VẾ HẸP: bằng chứng thật là `dispatcher_pid` trên record (xem chỗ tạo record bên
# dưới), và mike_json._writer_is_job_dispatcher đối chiếu nó với /proc — người ghi phải thật
# sự nằm trong cây tiến trình của dispatch.sh đó. Ứng biến kiểu 08-09 (Bash tool call KHÁC)
# không phải hậu duệ của cây đó nên vẫn bị TỪ CHỐI dù có set biến này.
JSET() { MIKE_JOB_OWNER="$job_id" python3 "$ROOT/bin/mike_json.py" job-set "$JOBS_DIR" "$job_id" "$@"; }
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
  # Publish the child through a FILE, not a variable. In the sync path this function is the
  # left side of a pipeline (`... | tee "$logfile"`), so bash runs it in a SUBSHELL and any
  # variable set here dies with it — _sync_killed_guard, which runs in the main shell, would
  # never see it. The pid matters because the child is a setsid'd session leader: once this
  # subshell is gone it is reparented to init and a PPid walk can no longer find it.
  printf '%s' "$pid" > "$logfile.workerpid" 2>/dev/null || true
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
      rm -f "$logfile.workerpid" 2>/dev/null || true
      return 124
    fi
    sleep 5
  done
  wait "$pid"
  local _rc=$?
  rm -f "$logfile.workerpid" 2>/dev/null || true
  return "$_rc"
}

# _build_argv <prompt_text> — dung mang CLI_ARGV cho $PROVIDER hien tai.
#
# ⚠️ PHAI goi BEN TRONG _bg_wrapper (hoac nhanh sync), KHONG BAO GIO dung san roi van chuyen
# mang nay qua ranh gioi tien trinh. Ly do da do thuc nghiem (arch-reviewer 2026-08-03):
#   - array bash khong export duoc: `arr=(a "b c"); export arr; bash -c 'declare -p arr'`
#     -> "bash: declare: arr: not found". Ma _bg_wrapper duoc re-enter bang `bash -c`.
#   - NUL khong song qua $( ): `x="$(printf 'a\0b\0c')"` -> len=3 "abc".
#   - moi duong di qua `eval` chuoi tai sinh lop loi quoting §15 (4 su co 07-17 -> 08-01),
#     ma prompt fleet la tieng Viet day dau " va backtick.
# => registry CHI tra FIELD; argv dung tai cho, bang bash thuan, khong quote thu cong.
_build_argv() {
  local _p="$1"
  case "$PROVIDER" in
    claude)
      # Phai BYTE-FOR-BYTE bang chuoi cu:
      #   "$CLAUDE" -p "$P" --permission-mode auto --max-turns $MAX_TURNS $MODEL_FLAG $EFFORT_FLAG
      # ($MODEL_FLAG/$EFFORT_FLAG KHONG quote nen word-split thanh 2 word, hoac 0 word khi rong.)
      CLI_ARGV=( "$CLI_BIN" -p "$_p" --permission-mode auto --max-turns "$MAX_TURNS" )
      if [ -n "$MODEL" ]; then CLI_ARGV+=( --model "$MODEL" ); fi
      CLI_ARGV+=( --effort "$EFFORT" )
      ;;
    opencode)
      # prompt la POSITIONAL (`opencode run [message..]`) => de CUOI CUNG.
      # --auto: auto-approve nhung KHONG de len rule `deny` (da kiem chung 2026-08-03:
      # bash deny-by-default van chan, tra loi sach ~7s, khong treo).
      CLI_ARGV=( "$CLI_BIN" run --dir "$AGENT_DIR" --auto )
      if [ -n "$MODEL" ]; then CLI_ARGV+=( -m "$MODEL" ); fi
      if [ -n "$EFFORT" ]; then CLI_ARGV+=( --variant "$EFFORT" ); fi
      CLI_ARGV+=( "$_p" )
      ;;
    codex)
      # -s workspace-write (KHONG dung --dangerously-bypass-approvals-and-sandbox —
      # arch-reviewer required_change #6c). Chua wire that: enabled=false toi khi user login.
      CLI_ARGV=( "$CLI_BIN" exec --skip-git-repo-check -C "$AGENT_DIR" -s workspace-write )
      if [ -n "$MODEL" ]; then CLI_ARGV+=( -m "$MODEL" ); fi
      if [ -n "$EFFORT" ]; then CLI_ARGV+=( -c "model_reasoning_effort=\"$EFFORT\"" ); fi
      CLI_ARGV+=( "$_p" )
      ;;
    antigravity)
      # `agy -p` = headless print mode (giong `claude -p`). Contract lay tu src/adapter.rs
      # :611-634 cua agy-acp.zip — nguon co tham quyen, khong doan.
      # KHONG di qua agy-acp (ACP adapter): xem notes trong kb/cli_providers.json.
      CLI_ARGV=( "$CLI_BIN" --add-dir "$AGENT_DIR" )
      if [ -n "$MODEL" ]; then CLI_ARGV+=( --model "$MODEL" ); fi
      CLI_ARGV+=( -p "$_p" )
      ;;
    *)
      echo "dispatch: provider '$PROVIDER' chua co bo dung argv trong _build_argv()." >&2
      return 1
      ;;
  esac
  return 0
}

dispatch_prompt="[DISPATCH từ $from | job=$job_id] $prompt

Khi hoàn thành, GHI KẾT QUẢ lên bus bằng (tham số cuối '$job_id' là trace_id — LUÔN giữ
nguyên literal này, KHÔNG đổi tên biến — để mọi event của job này gộp lại được thành 1 timeline):
  $ROOT/bin/append_event.sh $id finding \"<chủ đề>\" '<payload>' '$job_id'
(hoặc decision/answer tùy loại). Đây là phiên headless — kết quả PHẢI nằm trên bus để fleet thấy.

Heartbeat (bắt buộc): mỗi 4-5 tool call, ghi tiến độ để caller biết bạn còn sống:
  $ROOT/bin/append_event.sh $id heartbeat '$job_id' '{\"status\":\"in_progress\",\"note\":\"<đang làm gì>\"}' '$job_id'"

# --- profile = prompt-inline (2026-08-03) ---------------------------------------
# Provider KHONG doc duoc file profile nao cua fleet (codex doc AGENTS.md chu khong doc
# CLAUDE.md; agy khong doc file nao) => identity + context phai di VAO PROMPT, neu khong
# agent chay nhu mot model trang tron, khong biet minh la Taylor hay Wendy.
# claude-native / opencode-json KHONG di qua day (claude tu nap CLAUDE.md + @import;
# opencode doc CLAUDE.md tu --dir + `instructions` trong agents/<id>/opencode.json).
if [ "$CLI_PROFILE" = "prompt-inline" ]; then
  _profile_txt="$("$ROOT/bin/render_profile_prompt.sh" "$id" 2>/dev/null)"
  if [ -z "$_profile_txt" ]; then
    # Fail LOUD: chay tiep voi prompt khong co identity la ca te nhat — agent se lam sai
    # ma trong nhu that. Tha huy dispatch.
    echo "ERROR: HUY dispatch — provider '$PROVIDER' can profile prompt-inline nhung" >&2
    echo "  render_profile_prompt.sh '$id' khong tra ve gi. Khong chay agent thieu identity." >&2
    exit 1
  fi
  dispatch_prompt="$_profile_txt
$dispatch_prompt"
fi

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
# _ambient_thread trả 1 KHI VÀ CHỈ KHI registry hỏng cho một agent CÓ override cố định.
#
# ĐÁNH ĐỔI, sửa 2026-08-02 sau arch-reviewer vòng cuối (F4) — bản trước ABORT ở đây, SAI:
# `bq_freshness_check.sh` dispatch DollarBill (có override) KHÔNG kèm `--thread`, nên một
# registry Discord hỏng sẽ chặn luôn job SINH PLAN T+1 ⇒ sáng hôm sau bot chạy không có plan.
# Đó là đổi "user không thấy 1 tin nhắn" lấy "không có việc" — sai hướng với một sự cố thuần
# định tuyến thông báo. Nay: pin RỖNG + VẪN CHẠY + ghi log lỗi có người đọc. Vẫn KHÔNG tụt về ambient
# (đó mới là cơ chế rò rỉ mà S2 sinh ra để diệt) — pin rỗng ⇒ im lặng phía Discord, an toàn
# vì F2 đã được sửa (pin rỗng không còn giết _bg_wrapper).
# ABORT chỉ còn giữ cho `--thread` tường minh ở ngay dưới: caller đã nêu đích danh 1 topic thì
# không phân giải được phải dừng, không đoán.
#
# ⚠️ ĐO ĐƯỢC 2026-08-02 (vòng 5, arch-reviewer MINOR-1 + tự kiểm chứng): "đã cảnh báo qua
# Telegram" — câu ghi ở đây trước kia — LÀ SAI HAI LẦN. (a) `mike/bin/notify.sh` KHÔNG phải
# Telegram: `notify.sh` → `notify_discord.sh` → CÙNG bridge `127.0.0.1:8199` với
# `notify_thread.sh`, tức nó chết vì CÙNG registry. (Fleet CÓ Telegram thật —
# `secrets/telegram_config.json` + `telegram_recommend.send_telegram_text`, ~15 script production
# dùng: bot_execute.py, macro_healthcheck.py, crisis_alert_push.py… — nhưng `notify.sh` không
# phải nó, nên "Telegram vẫn chạy" KHÔNG bao che được cho đường báo của dispatch.)
# (b) Tệ hơn: trong ĐÚNG ca này (registry hỏng) `notify_discord.sh:22` cũng phân giải tên
# `mikefleet` QUA CHÍNH REGISTRY ĐÓ, `set -e` ⇒ nó chết trước khi curl. Đo thật:
# `DISCORD_CHANNELS_REGISTRY=/nonexistent notify.sh "..."` → "send failed (rc=1)", KHÔNG có
# tin nào đi. Nghĩa là lập luận đánh đổi F4 ("vẫn chạy vì dù sao cũng có alert") dựa trên một
# cảnh báo KHÔNG BAO GIỜ TỚI. Giữ nguyên quyết định VẪN CHẠY (đúng: không chặn việc vì lỗi
# định tuyến), nhưng cảnh báo phải đi bằng đường không chết cùng registry: ghi
# `logs/notify_thread_errors.log` — file mà `ops_health_check.sh` check #10 ĐỌC mỗi 08:20/12:45.
# PHẠM VI CHÍNH XÁC (vòng 6, arch-reviewer): chỉ khâu **GHI** là độc lập với Discord. Khâu
# **GIAO TỚI NGƯỜI** của check #10 vẫn là `ops_health_check.sh:587` → `notify_thread.sh` với TÊN
# `trading_daily` → `discord_channel.sh` → CHÍNH registry đang hỏng ⇒ registry hỏng KÉO DÀI thì
# báo cáo health-check CŨNG câm theo, không ai được báo gì. Vá ở vòng 6: `ops_health_check.sh`
# rơi sang Telegram (đường thật, không qua registry) khi `notify_thread.sh` trả về khác 0.
if ! _dtid0="${FORCE_TID:-$(_ambient_thread "$id")}"; then
  echo "dispatch: registry Discord hỏng cho override của '$id' — job VẪN CHẠY nhưng KHÔNG có topic Discord (không đoán). Đã ghi logs/notify_thread_errors.log (ops_health_check sẽ báo)." >&2
  mkdir -p "$ROOT/logs"
  printf '%s dispatch: registry Discord HONG cho override cua %q (job cho %s) — job VAN CHAY nhung KHONG co topic, moi thong bao Discord cua job nay bi MAT.\n' \
    "$(date -Iseconds)" "$id" "${job_id:-<chua-tao>}" >> "$ROOT/logs/notify_thread_errors.log" 2>/dev/null || true
  _dtid0=""
fi
# `--thread` chấp nhận TÊN trong kb/discord_channels.json (vd `--thread architecture`) ngoài
# ID trần. Phân giải NGAY TẠI ĐÂY để job record + $DISCORD_THREAD_ID của tiến trình con luôn
# giữ ID THẬT — mọi tầng sau chỉ đọc lại ID đã ghim, không bao giờ phải phân giải tên lần nữa.
#
# TÊN SAI ⇒ **ABORT cả dispatch** (sửa 2026-08-02 sau arch-reviewer S1). Bản đầu để _dtid0=""
# rồi chạy tiếp, TƯỞNG là fail-safe — thực tế KHÔNG: pin rỗng khiến mọi consumer bên dưới tự
# suy lại topic qua _ambient_thread/ccdb_thread_id, tức tin nhắn rơi đúng vào topic ambient của
# dispatcher — CHÍNH cơ chế rò rỉ R3 mà bản vá này sinh ra để diệt. Caller đã nêu đích danh 1
# topic; không phân giải được thì dừng lại, không đoán.
if [ -n "$_dtid0" ]; then
  if _dtid0_resolved="$("$ROOT/bin/discord_channel.sh" "$_dtid0" 2>&1)"; then
    _dtid0="$_dtid0_resolved"
  else
    echo "dispatch: HUỶ — không phân giải được topic '$_dtid0'. $_dtid0_resolved" >&2
    "$ROOT/bin/notify.sh" "[dispatch] HUỶ job cho $id: topic '$_dtid0' không có trong registry Discord." 2>/dev/null || true
    exit 1
  fi
fi
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
# Nhánh `else` là BẮT BUỘC (thêm 2026-08-02, arch-reviewer vòng 4 M2): thiếu nó thì pin RỖNG
# vẫn để agent con THỪA KẾ $DISCORD_THREAD_ID của tiến trình cha ⇒ job record nói "không có
# topic" (wrapper im lặng đúng như thiết kế) trong khi BÁO CÁO DO CHÍNH AGENT gửi
# (`notify_thread.sh "<msg>"` không đối số 2) lại rơi vào topic Mike đang chat — đúng lớp lỗi
# 07-22b (record và env của agent bất đồng). Pin rỗng phải rỗng ở CẢ HAI phía.
if [ -n "$_dtid0" ]; then export DISCORD_THREAD_ID="$_dtid0"; else export DISCORD_THREAD_ID=""; fi
_psum="$(printf '%s' "$prompt" | head -c 160 | tr '\n\t' '  ')"

# Cảnh báo TRÙNG DISPATCH (2026-08-10) — CHỈ cảnh báo, KHÔNG chặn.
# Dấu hiệu quan sát được của pattern "2 dispatch cùng sửa 1 file": 2/3 lần va chạm
# (08-09 sáng filter_lag_entry_window.py, 08-09 chiều executor.py) là cùng agent + prompt
# NGUYÊN VĂN, cách nhau 77s/59s. job-find-dup chỉ khớp khi job cũ còn status=running VÀ pid
# CÒN SỐNG THẬT — không phải chỉ đọc cờ trạng thái, vì chính cái cờ đó mới là thứ nói dối
# hôm 08-09. Không chặn: chạy lại có chủ đích là hợp lệ; khoá cứng theo file bất khả thi ở
# đây (đường dẫn agent sẽ sửa chưa tồn tại lúc dispatch). Tuyệt đối non-fatal.
_dup="$(python3 "$ROOT/bin/mike_json.py" job-find-dup "$JOBS_DIR" "$id" "$_psum" 2>/dev/null || true)"
if [ -n "${_dup:-}" ]; then
  echo "⚠️ TRÙNG DISPATCH? $id đang chạy THẬT (pid còn sống) một job có prompt y hệt:" >&2
  printf '     %s\n' "$_dup" >&2
  echo "   Kiểm tra trước: $ROOT/bin/jobs.sh status <job_id> (cột HB_AGE = tín hiệu sống đúng)." >&2
  echo "   Muốn THAY job cũ: $ROOT/bin/jobs.sh cancel <job_id> — đừng dispatch chồng lên nó." >&2
fi

# dispatcher_pid: pid CỦA CHÍNH dispatch.sh này (bash giữ nguyên `$$` trong mọi subshell, kể
# cả nhánh trái của pipeline `... | tee`). Ghi NGAY lúc tạo record, trước khi có người ghi nào
# khác tồn tại. job-set dùng nó để nhận ra "người ghi đang nằm TRONG cây tiến trình của
# dispatcher job này" — bằng chứng sống DUY NHẤT cho nhánh ĐỒNG BỘ, vốn không ghi `pid` nào
# (JSET pid=$BASHPID chỉ có trong _bg_wrapper) và có worker là ANH EM chứ không phải con của
# tiến trình job-set (arch-reviewer round 3, N2). Ghi đè field này trên job còn sống bị CHẶN
# y như ghi đè `pid` — nếu không thì lại thành đường vòng 2 lệnh.
JSET job_id="$job_id" from="$from" to="$id" status=running attempt=1 dispatcher_pid="$$" \
     max_attempts=$((RETRIES + 1)) started_at="$_start_ts" \
     deadline=$((_start_ts + TIMEOUT)) logfile="$logfile" discord_thread_id="$_dtid0" \
     model="${MODEL:-default}" effort="$EFFORT" \
     provider="$PROVIDER" turn_cap="$([ "$CLI_SUPPORTS_TURNS" = "true" ] && echo "$MAX_TURNS" || echo unsupported)" \
     prompt_summary="$_psum"

if [ "$bg" = "--bg" ]; then
  # Background wrapper: run agent (with timeout + retry) → consolidate → notify
  _bg_wrapper() {
    local max_attempts=$((RETRIES + 1))
    local attempt=1 rc=0 astart
    JSET pid="$BASHPID"
    while [ "$attempt" -le "$max_attempts" ]; do
      astart="$(date +%s)"
      JSET status=running attempt="$attempt" started_at="$astart" deadline=$((astart + TIMEOUT))
      # Salvage-trước-retry (2026-07-31, sau sự cố Winston_20260731_062642): AUTO-CALLBACK-FAIL
      # KHÔNG chạy được cho job from=Mike/user (guard "$from" != "Mike"/"user" ở dưới chặn
      # chính case phổ biến nhất) — chỗ đúng để mã hoá "kiểm việc đã làm tới đâu trước khi
      # làm lại" là NGAY TRONG prompt của lần thử tiếp theo, chạy bất kể từ đâu dispatch.
      # Bằng chứng cơ chế có tác dụng thật: job Winston_20260731_014953 tự làm đúng việc này
      # ở attempt=2 (đọc thấy code cũ dở dang, hoàn tất phần thiếu thay vì viết lại) — nhưng
      # đó là agent TỰ NGHĨ RA, không phải luôn xảy ra. Mã hoá thành chỉ dẫn tường minh.
      run_prompt="$dispatch_prompt"
      if [ "$attempt" -gt 1 ]; then
        run_prompt="$dispatch_prompt

⚠️ ĐÂY LÀ LẦN THỬ LẠI (attempt $attempt/$max_attempts) sau khi lần trước fail/timeout/hết
lượt. TRƯỚC KHI làm lại từ đầu: chạy 'git status' + 'git diff' ở MỌI repo bạn có thể đã sửa
(kể cả nested repo, vd mike/ bên trong WorkingClaude/) để xem việc đã làm tới đâu. Nếu code/
nội dung đã gần xong (chỉ thiếu verify/commit/report bus) → HOÀN TẤT phần còn thiếu thay vì
viết lại từ đầu (tốn gấp đôi vô ích). Nếu phần dở dang sai/không dùng được → nói rõ lý do rồi
làm lại có chủ đích, đừng âm thầm ghi đè mất công sức cũ mà không giải thích."
      fi
      set +e
      # argv dung TAI DAY (trong tien trinh con), khong phai o tien trinh cha — xem _build_argv.
      CLI_ARGV=()
      _build_argv "$run_prompt" && _hb_aware_timeout "${CLI_ARGV[@]}" > "$logfile" 2>&1
      rc=$?
      set -e
      if [ "$rc" -eq 0 ]; then
        JSET status=done ended_at="$(date +%s)" exit_code=0 result_summary="$(SUMMARY)"
        _circuit_record "$CIRCUIT_KEY" success
        "$ROOT/bin/consolidate.sh" >> "$ROOT/logs/consolidator.log" 2>&1 || true
        "$ROOT/bin/notify.sh" "[dispatch] $id hoàn thành (job $job_id): $(SUMMARY)" 2>/dev/null || true
        # Discord thread notification — always, regardless of who dispatched. Read the
        # topic THIS job was dispatched from (persisted at dispatch time), not whatever
        # topic Mike happens to be active in right now (see _job_thread_id comment).
        # tail -c 500: last bytes of log = agent's conclusion, not context-loading preamble.
        local _tid; _tid="$(_job_thread_id "$job_id")"
  # KHÔNG suy lại topic ở đây (sửa 2026-08-02, arch-reviewer S1): chỉ đọc field đã GHIM lúc
  # dispatch. Trước đây `[ -n "$X" ] || X="$(_ambient_thread ...)"` khiến pin rỗng rơi về topic
  # ambient của dispatcher — đúng cơ chế rò rỉ. Pin rỗng ⇒ IM LẶNG phía Discord, không bao giờ
  # đoán topic. (KHÔNG có kênh dự phòng độc lập nào ở đây: `notify.sh` cũng đi qua CÙNG bridge
  # Discord 127.0.0.1:8199 — xem chú thích tại nhánh "registry hỏng" bên dưới.)
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
      # account window. Non-claude provider → fallback to claude NOW (checked first: a
      # provider fallback is always preferred over queuing a same-provider blind-wait resume).
      if _maybe_fallback_provider_on_usage_limit "$logfile"; then
        "$ROOT/bin/consolidate.sh" >> "$ROOT/logs/consolidator.log" 2>&1 || true
        return 0
      fi
      if _maybe_schedule_usage_resume "$logfile"; then
        "$ROOT/bin/consolidate.sh" >> "$ROOT/logs/consolidator.log" 2>&1 || true
        return 0
      fi
      # Max-turns: if an in-loop attempt remains, bump the ceiling and retry immediately
      # (cheaper than a full async pending-resume cycle) — otherwise the next attempt
      # would use the SAME $MAX_TURNS and fail identically (the exact "chạy tới chạy lui"
      # pattern observed 2026-08-02: 5/5 jobs failed on attempt 2/2 with an unchanged cap).
      # Only escalate to the cross-dispatch pending-resume once in-loop attempts are spent.
      if _looks_like_max_turns "$logfile"; then
        if [ "$attempt" -lt "$max_attempts" ]; then
          MAX_TURNS="$(_bumped_max_turns)"
          JSET status=retrying exit_code="$rc" result_summary="hết turn budget, retry attempt $((attempt + 1)) với --max-turns=$MAX_TURNS"
          attempt=$((attempt + 1))
          continue
        elif _maybe_schedule_maxturns_resume "$logfile"; then
          "$ROOT/bin/consolidate.sh" >> "$ROOT/logs/consolidator.log" 2>&1 || true
          return 0
        fi
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
    _circuit_record "$CIRCUIT_KEY" fail
    "$ROOT/bin/consolidate.sh" >> "$ROOT/logs/consolidator.log" 2>&1 || true
    "$ROOT/bin/notify.sh" "[dispatch] $id $why sau $max_attempts lần (job $job_id) — xem $logfile" 2>/dev/null || true
    local _tid; _tid="$(_job_thread_id "$job_id")"
    # Không suy lại topic (2026-08-02, arch-reviewer S1) — chỉ đọc pin đã ghim lúc dispatch.
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
            _current_resume_count _job_thread_id _hb_aware_timeout \
            _maybe_schedule_maxturns_resume _looks_like_max_turns _bumped_max_turns \
            _current_maxturns_resume_count _build_argv
  # Chi export SCALAR (bash khong export duoc array — do la ly do _build_argv chay trong con).
  export ROOT JOBS_DIR job_id from id ts TIMEOUT RETRIES CLAUDE dispatch_prompt logfile prompt \
         CIRCUIT_DIR CIRCUIT_THRESHOLD CIRCUIT_COOLDOWN MODEL_FLAG EFFORT_FLAG MAX_EXT HB_FRESH_S \
         MAX_TURNS MAXTURNS_CEILING MODEL EFFORT \
         PROVIDER CLI_BIN AGENT_DIR CLI_SUPPORTS_TURNS CLI_USAGE_PROBE CLI_MAXTURNS_PAT CIRCUIT_KEY CLI_PROFILE
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
  echo "Theo dõi: $ROOT/bin/jobs.sh status $job_id | Khi xong: auto consolidate + notify #mikefleet."
  # Fast wake-on-completion snippet (MIKE.md §Quy chuẩn 8; sửa 2026-07-07 incident
  # agent-wrapper-monitor-gap): cơ chế CHÍNH = ScheduleWakeup poll NGẮN lặp lại (~240-270s) —
  # không phụ thuộc schema Agent tool. Harness Fable-5 (Mike restart 2026-07-06) đã BỎ tham số
  # run_in_background khỏi Agent tool; isolation:worktree KHÔNG phải background (chỉ cách ly git
  # worktree, agent vẫn đồng bộ, tin nhắn cuối là kênh trả kết quả duy nhất — wrapper "sẽ báo
  # lại" không bao giờ báo lại được). Wrapper Agent nền CHỈ dùng nếu schema phiên hiện tại thật
  # sự có tham số nền. In sẵn để khỏi soạn lại từ trí nhớ — BẮT BUỘC ngay sau dispatch này.
  _ww=$((TIMEOUT * (MAX_EXT + 1) * (RETRIES + 1) + 60))
  # Gợi ý độ trễ tỉnh ĐẦU tiên từ state/wakeup_profile.json (Wags 2026-08-01, wired live
  # 2026-08-03 — trước đây script này chỉ SINH file, dispatch.sh vẫn in ladder cứng cũ ở đây
  # khiến hint thực tế mâu thuẫn với MIKE.md §8 đã tài liệu hoá). Bucket đúng field sẽ ghi
  # cho CHÍNH job này (model mặc định "default", effort rỗng -> "?", khớp bucket_key() của
  # wakeup_profile.py). File thiếu/hỏng/không có bucket khớp -> _wsugg rỗng, in ladder cũ
  # 240-270s như trước — KHÔNG BAO GIỜ chặn dispatch dù lỗi gì.
  # Provider KHONG doi dinh dang key cho claude (giu nguyen bucket lich su trong
  # state/wakeup_profile.json — doi dinh dang la moi hint cu tro thanh khong khop, hint rong
  # im lang). Provider khac lay namespace RIENG: chua co mau do tre nao nen se roi ve ladder
  # mac dinh — dung, vi do tre opencode/codex khong duoc phep lam nhieu hint cua claude (F10).
  if [ "$PROVIDER" = "claude" ]; then
    _wkey="${id}|${MODEL:-default}|${EFFORT:-?}"
  else
    _wkey="${id}|${PROVIDER}:${MODEL:-default}|${EFFORT:-?}"
  fi
  _wsugg="$(python3 -c "
import json, sys
key = sys.argv[1]
try:
    with open(sys.argv[2], encoding='utf-8') as f:
        prof = json.load(f)
    b = prof.get('buckets', {}).get(key) or prof.get('global_fallback', {})
    m = b.get('median_s')
    print(max(90, min(1200, int(m))) if m else '')
except Exception:
    print('')
" "$_wkey" "$ROOT/state/wakeup_profile.json" 2>/dev/null)"
  echo "⚠️ BẮT BUỘC ngay sau dispatch này (MIKE.md §8, sửa 2026-07-07 — Agent tool KHÔNG còn run_in_background):" >&2
  if [ -n "$_wsugg" ]; then
    echo "  1) CƠ CHẾ CHÍNH: ScheduleWakeup THÍCH ỨNG — lần tỉnh ĐẦU dùng gợi ý wakeup_profile.json cho bucket '$_wkey': ~${_wsugg}s (kẹp [90,1200]); từ lần thứ 2 trở đi mà job vẫn running thì TĂNG DẦN (nhân ~1.6-2x, trần 1200s), không quay lại ngắn trừ khi có job MỚI phát sinh trong batch. Mỗi lần tỉnh chạy '$ROOT/bin/jobs.sh status $job_id'; chưa done → đặt lại wakeup theo bậc thang; done → xử lý ngay. KHÔNG đặt 1 lần chờ dài (worst-case chờ tối đa ~${_ww}s vẫn phủ qua nhiều lần poll)." >&2
  else
    echo "  1) CƠ CHẾ CHÍNH: ScheduleWakeup THÍCH ỨNG — không có gợi ý wakeup_profile.json cho bucket '$_wkey' (file thiếu/hỏng/mẫu quá ít) → dùng ladder mặc định: 3 lần tỉnh ĐẦU ~240-270s; từ lần thứ 4 trở đi mà job vẫn running thì TĂNG DẦN (240→480→900→trần 1200s), không quay lại ngắn trừ khi có job MỚI phát sinh trong batch. Mỗi lần tỉnh chạy '$ROOT/bin/jobs.sh status $job_id'; chưa done → đặt lại wakeup theo bậc thang; done → xử lý ngay. KHÔNG đặt 1 lần chờ dài (worst-case chờ tối đa ~${_ww}s vẫn phủ qua nhiều lần poll)." >&2
  fi
  echo "  2) CHỈ nếu schema tool phiên này THẬT SỰ có tham số nền (run_in_background trên Agent/Bash) mới thêm wrapper bọc '$ROOT/bin/jobs.sh wait $job_id --timeout $_ww'. isolation:worktree KHÔNG phải background — cấm dùng thay thế." >&2
  echo "  3) SELF-CHECK: trước khi nói với user bất kỳ điều gì về trạng thái job này (đang chờ/xong/chết), chạy '$ROOT/bin/jobs.sh status $job_id' trong CÙNG turn — không nói từ trí nhớ." >&2
  echo "$pid" > "$ROOT/logs/.dispatch_${id}_${ts}.pid"
  # Immediate Discord notify so user sees task is in flight (don't wait for watcher heartbeat)
  { _dtid="$(_job_thread_id "$job_id")"
  # KHÔNG suy lại topic ở đây (sửa 2026-08-02, arch-reviewer S1): chỉ đọc field đã GHIM lúc
  # dispatch. Trước đây `[ -n "$X" ] || X="$(_ambient_thread ...)"` khiến pin rỗng rơi về topic
  # ambient của dispatcher — đúng cơ chế rò rỉ. Pin rỗng ⇒ IM LẶNG phía Discord, không bao giờ
  # đoán topic. (KHÔNG có kênh dự phòng độc lập nào ở đây: `notify.sh` cũng đi qua CÙNG bridge
  # Discord 127.0.0.1:8199 — xem chú thích tại nhánh "registry hỏng" bên dưới.)
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
    # STOP THE WORKER FIRST, then close the record — never the other way round. The caller's
    # SIGTERM hits this shell's process group, but the worker was put in its OWN session by
    # _hb_aware_timeout, so it SURVIVES and keeps editing the repo with nobody left to report
    # its outcome. Writing status=failed while it runs is the exact record that made the
    # board lie on 2026-08-09 (Mike read "failed", re-dispatched, two runs collided on
    # executor.py). Same order as `jobs.sh cancel`: kill the tree, give it a grace period,
    # SIGKILL the remainder, and only then stamp.
    _wp="$(cat "$logfile.workerpid" 2>/dev/null || true)"
    if [ -n "$_wp" ]; then
      kill -TERM -- "-$_wp" 2>/dev/null || kill -TERM "$_wp" 2>/dev/null || true
      _w=0
      while [ "$_w" -lt "${DISPATCH_KILL_GRACE_S:-10}" ] && kill -0 "$_wp" 2>/dev/null; do
        sleep 1; _w=$((_w + 1))
      done
      kill -KILL -- "-$_wp" 2>/dev/null || kill -KILL "$_wp" 2>/dev/null || true
      sleep 1
      rm -f "$logfile.workerpid" 2>/dev/null || true
    fi
    # VERIFY, đừng chỉ giết rồi tin. Cùng hợp đồng với `jobs.sh cancel` (exit 5): còn tiến
    # trình nào của job sống sót thì KHÔNG ghi trạng thái kết thúc — để record ở running và
    # nói ra sự thật. Giết-mà-không-kiểm chính là nửa đầu của sự cố 08-09; nửa sau là đóng
    # dấu dựa trên niềm tin đó. Ví dụ có thật: worker spawn một tiến trình con detached
    # (đúng thứ _detached_spawn làm cho dispatch --bg lồng nhau) — nó sống qua cú giết group.
    if _alive="$(python3 "$ROOT/bin/mike_json.py" job-live-pids "$JOBS_DIR" "$job_id" 2>/dev/null)" \
       && [ -n "$_alive" ]; then
      echo "WARNING: dispatch.sh sync bị kill, đã giết worker nhưng CÒN tiến trình sống của job $job_id: $_alive" >&2
      echo "         => record GIỮ NGUYÊN status=running (không bao giờ báo 'đã dừng' cho một writer còn sống)." >&2
      echo "         Đóng nốt bằng: $ROOT/bin/jobs.sh cancel $job_id" >&2
    else
      # KHÔNG nuốt rc: nếu guard từ chối lệnh ghi này thì đó là tín hiệu cần thấy, không
      # phải thứ để `2>/dev/null || true` giấu đi.
      JSET status=failed ended_at="$(date +%s)" exit_code=143 \
           result_summary="KILLED: dispatch.sh sync bị kill giữa chừng (caller chết/Bash-tool timeout?) — trap đã DỪNG worker, XÁC MINH đã chết, rồi mới finalize record" \
        || echo "WARNING: không finalize được record $job_id (job-set rc=$?) — xem $ROOT/bin/jobs.sh status $job_id" >&2
    fi
    kill "$_wpid" 2>/dev/null || true
    exit 143
  }
  trap _sync_killed_guard TERM INT HUP
  set +e
  CLI_ARGV=()
  if _build_argv "$dispatch_prompt"; then
    _hb_aware_timeout "${CLI_ARGV[@]}" 2>"$logfile.err" | tee "$logfile"
    rc=${PIPESTATUS[0]}
  else
    rc=78   # loi CAU HINH provider, khong phai loi agent
  fi
  set -e
  trap - TERM INT HUP  # claude finished — normal finalize below owns the record now
  kill "$_wpid" 2>/dev/null || true  # watcher no longer needed
  # Push bus → KB immediately after agent finishes
  "$ROOT/bin/consolidate.sh" >> "$ROOT/logs/consolidator.log" 2>&1 || true
  if [ "$rc" -eq 0 ]; then
    JSET status=done ended_at="$(date +%s)" exit_code=0 result_summary="$(SUMMARY)"
    _circuit_record "$CIRCUIT_KEY" success
  else
    if _maybe_fallback_provider_on_usage_limit "$logfile" "$logfile.err"; then
      echo "NOTE: dispatch $id (job $job_id) provider '$PROVIDER' hết usage/rate limit — đã fallback NGAY sang claude (job mới chạy nền, không chờ reset)." >&2
      exit 5
    fi
    if _maybe_schedule_usage_resume "$logfile" "$logfile.err"; then
      echo "NOTE: dispatch $id (job $job_id) hết usage limit tài khoản — KHÔNG PHẢI lỗi task." >&2
      echo "      Đã tự động lên lịch resume (bin/resume_pending.py sẽ tự chạy lại, không cần làm gì)." >&2
      exit 5
    fi
    if _maybe_schedule_maxturns_resume "$logfile" "$logfile.err"; then
      echo "NOTE: dispatch $id (job $job_id) hết turn budget (--max-turns=$MAX_TURNS) — KHÔNG PHẢI lỗi task." >&2
      echo "      Đã tự động lên lịch resume NGAY với trần cao hơn (bin/resume_pending.py sẽ tự chạy lại)." >&2
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
    _circuit_record "$CIRCUIT_KEY" fail
    exit "$rc"
  fi
fi
