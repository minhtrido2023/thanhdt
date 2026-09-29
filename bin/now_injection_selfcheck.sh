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
  # Loại transcript của phiên HEADLESS DISPATCH (2026-08-22, weekly ops audit): chúng nằm
  # CÙNG project dir agents-Mike, KB context của chúng nhắc cả 3 thread_id, và chúng KHÔNG đi
  # qua bridge Discord nên 30 dòng cuối (toàn tool result) không bao giờ có "[now:". Một phiên
  # dispatch đang chạy vì thế luôn là file MỚI NHẤT khớp mọi thread_id ⇒ cả 3 ca FAIL GIẢ.
  # Đây đúng lỗ hổng phần đầu file đã nêu ("headless fleet dispatch ... would self-match") —
  # scope agents-Mike chưa đủ vì chính Mike cũng nhận dispatch. Marker phân biệt: prompt
  # dispatch luôn mở đầu bằng "[DISPATCH từ user | job=..." (bin/dispatch.sh), phiên Discord
  # thật không có. Đo lúc vá: 3/5 transcript mới nhất là dispatch, file mới nhất là chính
  # phiên weekly-ops-audit này.
  file="$(grep -l "$tid" "$PROJECTS"/*.jsonl 2>/dev/null \
          | { grep -vFxf <(grep -l 'DISPATCH từ user | job=' "$PROJECTS"/*.jsonl 2>/dev/null) - || true; } \
          | xargs -r stat -c '%Y %n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)"
  if [ -z "$file" ]; then
    echo "FAIL $name — không tìm thấy transcript nào nhắc tới thread_id của $channel"
    overall_rc=1
    return
  fi
  # Neo vào LƯỢT PROMPT gần nhất, không phải "30 dòng JSONL cuối" (sửa 2026-08-22) — lý do
  # đầy đủ trong docstring bin/_now_injection_probe.py.
  local probe_out probe_rc
  probe_out="$(python3 "$ROOT/bin/_now_injection_probe.py" "$file" 2>&1)"; probe_rc=$?
  case "$probe_rc" in
    0) echo "PASS $name (file=$file)" ;;
    2) echo "FAIL $name — $file không có lượt prompt người dùng nào để kiểm (file=$file)"
       overall_rc=1 ;;
    *) echo "FAIL $name — lượt prompt GẦN NHẤT trong $file không có \"[now:\" [$probe_out] (file=$file)"
       overall_rc=1 ;;
  esac
}

_check_thread "Trading strategy" "taylor_research"
_check_thread "Trading Daily" "trading_daily"
_check_thread "Architecture" "architecture"

exit "$overall_rc"
