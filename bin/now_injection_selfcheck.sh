#!/usr/bin/env bash
# now_injection_selfcheck.sh — §S2 selfcheck, discord_time_reasoning_by_construction_plan_20260821.md.
# E6 lesson from that incident: verification that only tested 2 paths (attachment + /api/notify)
# missed the text-only path where the real bug lived. This checks each of the 3 main topics'
# NEWEST transcript for the literal "[now:" marker in its last 30 rows — proof the injection
# actually reached the model, not just that the code looks right.
#
# There is no direct thread_id -> transcript mapping outside ccdb's own DB, so the transcript
# is found heuristically: newest agents-Mike/*.jsonl (Mike is the sole Discord-facing agent —
# all 3 topics are threads Mike replies in from the same working directory/project) that
# mentions the thread_id anywhere. Scoping to agents-Mike (not every project dir under
# ~/.claude/projects) matters: a headless fleet dispatch prompt (e.g. to Wags) routinely
# mentions these same thread ids in passing, which would otherwise self-match and mask a
# real FAIL. Even scoped to agents-Mike this can't perfectly disambiguate between the 3
# threads if Mike's own KB context mentions all of them in every session — treat FAIL as a
# strong signal, PASS as good-enough evidence (not a formal proof).
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECTS="${HOME}/.claude/projects/-home-trido-thanhdt-WorkingClaude-mike-agents-Mike"

overall_rc=0

_check_thread() {
  local name="$1" channel="$2" tid file
  tid="$("$ROOT/bin/discord_channel.sh" "$channel" 2>/dev/null)" || {
    echo "FAIL $name — không phân giải được channel '$channel' qua discord_channel.sh"
    overall_rc=1
    return
  }
  file="$(grep -l "$tid" "$PROJECTS"/*.jsonl 2>/dev/null | xargs -r stat -c '%Y %n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)"
  if [ -z "$file" ]; then
    echo "FAIL $name — không tìm thấy transcript nào nhắc tới thread_id của $channel"
    overall_rc=1
    return
  fi
  if tail -n 30 "$file" | grep -q '\[now:'; then
    echo "PASS $name (file=$file)"
  else
    echo "FAIL $name — 30 dòng cuối của $file không có \"[now:\" (file=$file)"
    overall_rc=1
  fi
}

_check_thread "Trading strategy" "taylor_research"
_check_thread "Trading Daily" "trading_daily"
_check_thread "Architecture" "architecture"

exit "$overall_rc"
