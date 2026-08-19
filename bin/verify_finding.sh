#!/usr/bin/env bash
# verify_finding.sh — adversarial verification tier for quant findings.
#
# Runs the `quant-skeptic` reviewer (headless) against a Taylor (or any agent's)
# finding and writes a `verification` event back to the bus. The reviewer's ONLY
# job is to REFUTE; the verdict (CONFIRMED|REFUTED|INCONCLUSIVE) is auditable in KB.
#
# Design: the stateless reviewer RETURNS structured output; THIS script (deterministic)
# extracts the verdict JSON and writes the bus event — so the write never fails silently
# inside an ephemeral agent.
#
# Usage:
#   verify_finding.sh                       # verify the LATEST Taylor finding
#   verify_finding.sh --agent Taylor        # latest finding from <agent>
#   verify_finding.sh --topic "MGE1.5"      # latest finding whose topic matches substr
#   verify_finding.sh --claim "free-text claim to attack"   # ad-hoc, no bus finding
#   verify_finding.sh ... --dry-run         # print selected finding + prompt, DON'T call claude
#   verify_finding.sh ... --bg              # run in background, notify on done
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKDIR="/home/trido/thanhdt/WorkingClaude"
CLAUDE="/home/trido/.local/bin/claude"
AGENT_DEF="$HOME/.claude/agents/quant-skeptic.md"
REVIEWER_ID="quant-skeptic"

agent="Taylor"; topic_substr=""; claim=""; dry=""; bg=""
while [ $# -gt 0 ]; do
  case "$1" in
    --agent)  agent="${2:?}"; shift 2;;
    --topic)  topic_substr="${2:?}"; shift 2;;
    --claim)  claim="${2:?}"; shift 2;;
    --dry-run) dry=1; shift;;
    --bg)     bg=1; shift;;
    *) echo "unknown arg: $1" >&2; exit 2;;
  esac
done

[ -f "$AGENT_DEF" ] || { echo "ERROR: reviewer def missing: $AGENT_DEF" >&2; exit 1; }
# Canonical checklist = the reviewer agent def with YAML frontmatter stripped (single source of truth).
SKEPTIC_SYS="$(awk 'NR==1&&/^---$/{f=1;next} f&&/^---$/{f=0;next} !f' "$AGENT_DEF")"

# --- select the finding to attack ---
finding_topic=""; finding_json=""; finding_trace_id=""
if [ -n "$claim" ]; then
  finding_topic="ad-hoc claim"
  finding_json="$(printf '{"topic":"ad-hoc claim","payload":%s}' "$(printf '%s' "$claim" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')")"
else
  inbox="$ROOT/bus/inbox/$agent.jsonl"
  [ -f "$inbox" ] || { echo "ERROR: no inbox for agent '$agent' ($inbox)" >&2; exit 1; }
  # newest finding (optionally matching topic substr) → ONE JSON wrapper {topic, finding}
  sel="$(python3 - "$inbox" "$topic_substr" <<'PY'
import json,sys
inbox, sub = sys.argv[1], sys.argv[2]
pick=None
for ln in open(inbox, encoding="utf-8"):
    ln=ln.strip()
    if not ln: continue
    try: e=json.loads(ln)
    except Exception: continue
    if e.get("event_type")!="finding": continue
    if sub and sub.lower() not in e.get("topic","").lower(): continue
    pick=e  # keep scanning → last match wins (newest; file is append-order)
if not pick:
    sys.exit(3)
finding={"topic":pick.get("topic",""), "event_id":pick.get("event_id",""),
         "ts":pick.get("ts",""), "payload":pick.get("payload")}
print(json.dumps({"topic":pick.get("topic",""), "finding":finding,
                   "trace_id":pick.get("trace_id","")}, ensure_ascii=False))
PY
)" || { echo "ERROR: no matching '$agent' finding (substr='$topic_substr')" >&2; exit 1; }
  finding_topic="$(printf '%s' "$sel" | python3 -c 'import json,sys; print(json.load(sys.stdin)["topic"])')"
  finding_json="$(printf '%s' "$sel" | python3 -c 'import json,sys; print(json.dumps(json.load(sys.stdin)["finding"], ensure_ascii=False))')"
  # Propagate the source finding's trace_id so its verdict lands in the same job timeline.
  finding_trace_id="$(printf '%s' "$sel" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("trace_id") or "")')"
fi

# --- build the adversarial prompt ---
prompt="$SKEPTIC_SYS

--- FINDING UNDER REVIEW (attack this) ---
$finding_json

Work from the codebase at $WORKDIR. Open the artifacts the finding cites, run the 7 attacks,
recompute at least one headline number if cheap, then emit the VERDICT_JSON block exactly."

if [ -n "$dry" ]; then
  echo "=== SELECTED FINDING ==="; echo "topic: $finding_topic"
  echo "=== PROMPT (first 1200 chars) ==="; printf '%s\n' "${prompt:0:1200}"
  echo "..."; echo "[dry-run] not calling claude."
  exit 0
fi

mkdir -p "$ROOT/logs"
ts="$(date -u +%Y%m%d_%H%M%S)"
log="$ROOT/logs/verify_${ts}_$$.log"

# --- F3 (2026-08-19): --bg used to be a bare `&` + notify.sh, with NO bus/jobs/ record —
# jobs.sh could never see it, and nothing ever pushed a wake on completion (silent unless
# someone happened to grep the log). quant-skeptic has no agents/<id>/ home dir (it is a
# headless reviewer role invoked directly via `claude -p`, not a fleet agent identity), so
# `dispatch.sh quant-skeptic ... --bg` is not an option (dispatch.sh hard-requires
# agents/$id/ to exist). Mirror dispatch.sh's _bg_wrapper pattern by hand instead: a real job
# record (job_id follows the fleet's `<id>_<UTC-ts>` convention so it also satisfies the
# trace_id shape check below), pid stamped once the backgrounded run actually starts (so
# mike_json.py job-set's anti-lying guard recognizes this process as the record's own
# writer), status closed at the end, and — only when the SOURCE finding's own job carried a
# Discord topic — a real active-wake push via wake_thread.sh so a live Mike session resumes
# instead of waiting out a blind ladder.
job_id=""; _verify_src_tid=""
if [ -n "$bg" ]; then
  JOBS_DIR="$ROOT/bus/jobs"
  job_id="${REVIEWER_ID}_${ts}"
  if [ -n "$finding_trace_id" ]; then
    _verify_src_tid="$(python3 "$ROOT/bin/mike_json.py" job-field "$JOBS_DIR" "$finding_trace_id" discord_thread_id 2>/dev/null || true)"
  fi
  # dispatcher_pid="$$": recorded on the SAME initial call that creates the record (record
  # does not exist yet -> mike_json.py's anti-lying guard exempts this write unconditionally,
  # same as dispatch.sh:1182). Without it, the pid= stamp below is a SECOND, separate job-set
  # call on an already-"running" record with no dispatcher_pid to prove legitimacy against —
  # reproduced 2026-08-19: the guard refused it (exit 3), run_and_record died under `set -e`
  # before ever opening $log, and the record was stuck at status=running forever with no pid,
  # no log, no completion, no wake — silently defeating the entire point of this fix.
  # deadline: without one, bin/watcher (job-reap) can never close a record whose worker died
  # mid-run (crash, OOM, host restart) — it stays "running" forever, which (arch-review
  # coord-mechanism-08-19) also permanently locks its own result out of claim-reply (F1) and
  # permanently trips hooks/stop.sh's circuit breaker (F2) on every future Mike turn on the
  # same thread. 900s mirrors dispatch.sh's TIMEOUT default (600s) with headroom for
  # quant-skeptic's deeper multi-step review (7 attacks + recompute) vs a typical dispatch.
  _deadline_s="${VERIFY_FINDING_TIMEOUT_S:-900}"
  _started_epoch="$(date +%s)"
  python3 "$ROOT/bin/mike_json.py" job-set "$JOBS_DIR" "$job_id" \
    job_id="$job_id" from="${DISPATCH_FROM:-Mike}" to="$REVIEWER_ID" status=running \
    started_at="$_started_epoch" deadline=$((_started_epoch + _deadline_s)) \
    logfile="$log" discord_thread_id="$_verify_src_tid" \
    dispatcher_pid="$$" prompt_summary="VERIFY: $finding_topic" >/dev/null
fi

run_and_record() {
  cd "$WORKDIR"
  set +e
  "$CLAUDE" -p "$prompt" \
    --permission-mode auto \
    --allowedTools "Bash Read Grep Glob" \
    --max-turns 50 \
    > "$log" 2>"$log.err"
  _claude_rc=$?
  set -e

  # extract the VERDICT_JSON block → verdict_json
  verdict_json="$(python3 - "$log" "$finding_topic" <<'PY'
import json,sys,re
log, topic = sys.argv[1], sys.argv[2]
txt=open(log, encoding="utf-8", errors="replace").read()
m=re.search(r"<<<VERDICT_JSON>>>(.*?)<<<END_VERDICT>>>", txt, re.S)
if not m:
    print(json.dumps({"finding_topic":topic,"verdict":"INCONCLUSIVE","confidence":"low",
        "summary":"reviewer produced no parseable VERDICT_JSON block","checks":{},
        "killer_objection":None,"recommended_reruns":["re-run verify_finding.sh"]}))
    sys.exit(0)
raw=m.group(1).strip()
try:
    obj=json.loads(raw)
except Exception as e:
    # Reviewer models routinely leave a trailing comma before a closing `}`/`]`
    # (valid in JS/Python literals, invalid JSON) — strip it and retry once
    # before giving up. Recurred 3x same-day 2026-08-10, silently downgrading
    # real CONFIRMED/high verdicts to INCONCLUSIVE/low on the bus.
    repaired = re.sub(r",(\s*[}\]])", r"\1", raw)
    try:
        obj=json.loads(repaired)
    except Exception:
        print(json.dumps({"finding_topic":topic,"verdict":"INCONCLUSIVE","confidence":"low",
            "summary":"VERDICT_JSON present but unparseable: %s"%e,"checks":{}}))
        sys.exit(0)
obj.setdefault("finding_topic", topic)
print(json.dumps(obj, ensure_ascii=False))
PY
)"
  # write the verification event to the bus (deterministic, outside the agent) — carry the
  # source finding's trace_id (if any) so finding + verdict land in the same job timeline.
  #
  # SANITIZE the inherited trace_id first (arch-review coord-2026-08-13, killer objection):
  # it is read from an APPEND-ONLY bus whose historical records include poisoned values
  # (a 232-char string with spaces, `thêm`, …) that the same finding decided NOT to rewrite.
  # This line runs under `set -euo pipefail` with no guard, so a poisoned trace_id aborts
  # run_and_record AFTER a full headless reviewer pass has already been spent — the verdict
  # vanishes and consolidate never runs (under --bg, silently). This caller is clean and has
  # no way to re-quote immutable history, so the right move is: drop the trace_id, warn, and
  # STILL write the verdict. Never let a bad correlation id destroy a good verdict.
  if [ -n "$finding_trace_id" ] && ! printf '%s' "$finding_trace_id" \
       | grep -qE '^[A-Za-z0-9_.:-]+_[0-9]{8}_[0-9]{6}$'; then
    echo "verify_finding.sh: trace_id kế thừa SAI HÌNH DẠNG ($(printf '%q' "$finding_trace_id")) — BỎ trace_id, VẪN ghi verdict. Timeline job sẽ không gộp được event này." >&2
    finding_trace_id=""
  fi
  "$ROOT/bin/append_event.sh" "$REVIEWER_ID" verification "VERIFY: $finding_topic" "$verdict_json" "$finding_trace_id" >/dev/null
  "$ROOT/bin/consolidate.sh" >> "$ROOT/logs/consolidator.log" 2>&1 || true

  verdict="$(printf '%s' "$verdict_json" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("verdict","?"))')"
  echo "=== quant-skeptic verdict: $verdict ==="
  printf '%s\n' "$verdict_json" | python3 -m json.tool 2>/dev/null || printf '%s\n' "$verdict_json"
  echo "(full reviewer log: $log)"

  if [ -n "$job_id" ]; then
    _jstatus=done
    [ "$_claude_rc" -eq 0 ] || _jstatus=failed
    MIKE_JOB_OWNER="$job_id" python3 "$ROOT/bin/mike_json.py" job-set "$JOBS_DIR" "$job_id" \
      status="$_jstatus" ended_at="$(date +%s)" exit_code="$_claude_rc" \
      result_summary="verdict=$verdict" >/dev/null
    # Active wake (same claim-reply protocol as MIKE.md §8.4, in sync with the exit-3 gate
    # job-claim-reply now enforces): only fires when the source finding's OWN job named a
    # Discord topic — verify_finding.sh has none of its own to guess, and guessing is exactly
    # the bug class §8 exists to prevent.
    if [ -n "$_verify_src_tid" ]; then
      _wake_prompt="Đầu tiên: $ROOT/bin/jobs.sh claim-reply $job_id → exit 1 → ScheduleWakeup(noop:true,stop:true), DỪNG. exit 0 → [logic poll + post bình thường]. exit 2 → báo job record thiếu, đừng im lặng. exit 3 → job chưa xong, post progress bình thường (KHÔNG claim, KHÔNG coi là đã reply), tiếp tục poll. quant-skeptic đã xong verify \"$finding_topic\" (job \`${job_id}\`): verdict=$verdict."
      "$ROOT/bin/wake_thread.sh" "$_verify_src_tid" "$_wake_prompt" "$job_id" 2>/dev/null || true
    fi
  fi

  [ -n "$bg" ] && "$ROOT/bin/notify.sh" "[verify] $finding_topic → $verdict" 2>/dev/null || true
}

if [ -n "$bg" ]; then
  run_and_record &
  _bg_pid=$!
  # pid=$_bg_pid, stamped HERE (top-level script, still alive) rather than from inside
  # run_and_record: mike_json.py's anti-lying guard only accepts this first pid= write when
  # the CALLER's own /proc ancestry chain reaches `dispatcher_pid` (stamped above as "$$").
  # This top-level process IS that dispatcher_pid, so the write is trivially self-provable —
  # but by the time run_and_record's OWN body runs, this script has already reached its exit
  # (nothing left to do after backgrounding) and $_bg_pid has been reparented away from it,
  # breaking that exact ancestry chain. Reproduced 2026-08-19: stamping from inside
  # run_and_record got refused (exit 3) every time, silently killing the background worker
  # before it ever opened $log — the record was left at status=running forever with no pid,
  # no log, no completion, no wake. Stamping here, one line after backgrounding, is the fix.
  MIKE_JOB_OWNER="$job_id" python3 "$ROOT/bin/mike_json.py" job-set "$JOBS_DIR" "$job_id" pid="$_bg_pid" >/dev/null
  echo "VERIFYING (pid=$_bg_pid, job=$job_id) → log: $log ; bin/jobs.sh status $job_id ; verdict will land on bus as quant-skeptic/verification"
else
  run_and_record
fi
