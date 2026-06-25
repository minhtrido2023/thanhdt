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
finding_topic=""; finding_json=""
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
print(json.dumps({"topic":pick.get("topic",""), "finding":finding}, ensure_ascii=False))
PY
)" || { echo "ERROR: no matching '$agent' finding (substr='$topic_substr')" >&2; exit 1; }
  finding_topic="$(printf '%s' "$sel" | python3 -c 'import json,sys; print(json.load(sys.stdin)["topic"])')"
  finding_json="$(printf '%s' "$sel" | python3 -c 'import json,sys; print(json.dumps(json.load(sys.stdin)["finding"], ensure_ascii=False))')"
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
log="$ROOT/logs/verify_${ts}.log"

run_and_record() {
  cd "$WORKDIR"
  "$CLAUDE" -p "$prompt" \
    --permission-mode auto \
    --allowedTools "Bash Read Grep Glob" \
    --max-turns 30 \
    > "$log" 2>"$log.err" || true

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
    print(json.dumps({"finding_topic":topic,"verdict":"INCONCLUSIVE","confidence":"low",
        "summary":"VERDICT_JSON present but unparseable: %s"%e,"checks":{}}))
    sys.exit(0)
obj.setdefault("finding_topic", topic)
print(json.dumps(obj, ensure_ascii=False))
PY
)"
  # write the verification event to the bus (deterministic, outside the agent)
  "$ROOT/bin/append_event.sh" "$REVIEWER_ID" verification "VERIFY: $finding_topic" "$verdict_json" >/dev/null
  "$ROOT/bin/consolidate.sh" >> "$ROOT/logs/consolidator.log" 2>&1 || true

  verdict="$(printf '%s' "$verdict_json" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("verdict","?"))')"
  echo "=== quant-skeptic verdict: $verdict ==="
  printf '%s\n' "$verdict_json" | python3 -m json.tool 2>/dev/null || printf '%s\n' "$verdict_json"
  echo "(full reviewer log: $log)"
  [ -n "$bg" ] && "$ROOT/bin/notify.sh" "[verify] $finding_topic → $verdict" 2>/dev/null || true
}

if [ -n "$bg" ]; then
  run_and_record &
  echo "VERIFYING (pid=$!) → log: $log ; verdict will land on bus as quant-skeptic/verification"
else
  run_and_record
fi
