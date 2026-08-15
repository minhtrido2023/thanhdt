#!/usr/bin/env bash
# dispatch_wake_selfcheck.sh — self-check cho ACTIVE WAKE (2026-08-15, MIKE.md §8 rev):
# _bg_wrapper trong bin/dispatch.sh gọi bin/wake_thread.sh khi job Mike TỰ dispatch xong
# (thành công hoặc thất bại), thay vì để Mike tự đoán delay qua ScheduleWakeup ladder mù.
#
# VÌ SAO cần: đây là 2 call site MỚI, gated bởi `[ "$from" = "Mike" ]` và lồng trong
# `if [ -n "$_tid" ]; then`. Cả 2 điều kiện đều là chỗ dễ lẫn (agent khác không có thread
# sống để đánh thức; pin rỗng thì notify_thread.sh cũng im lặng, wake phải im theo, không
# được rơi vào nhánh nào gây lỗi/gọi mù). Test bằng SANDBOX y hệt dispatch_discord_topic_
# selfcheck.sh (symlink bin/ THẬT, chỉ stub các side-effect ra ngoài) — chạy đúng code
# production, không copy logic.
#
# Usage: bash mike/bin/dispatch_wake_selfcheck.sh   (exit 0 = tất cả ca PASS)
set -uo pipefail

REAL="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SB="$(mktemp -d)"
trap 'rm -rf "$SB"' EXIT
MK="$SB/mike"

mkdir -p "$MK/bin" "$MK/kb" "$MK/bus/jobs" "$MK/logs" "$MK/state/circuit" \
         "$MK/agents/Wags" "$MK/agents/Taylor" "$MK/agents/Mike/state"
for f in "$REAL/bin"/*; do
  [ -f "$f" ] && ln -s "$f" "$MK/bin/$(basename "$f")"
done
cp "$REAL/kb/discord_channels.json" "$MK/kb/discord_channels.json"
cp "$REAL/kb/cli_providers.json" "$MK/kb/cli_providers.json"

_stub() {  # _stub <tên file trong bin> <nội dung>
  rm -f "$MK/bin/$1"
  [ -e "$MK/bin/$1" ] && { echo "FATAL: không gỡ được $MK/bin/$1"; exit 1; }
  printf '%s\n' "$2" > "$MK/bin/$1"
  chmod +x "$MK/bin/$1"
  [ -L "$MK/bin/$1" ] && { echo "FATAL: $MK/bin/$1 vẫn là symlink — dừng để khỏi hỏng file thật"; exit 1; }
  return 0
}
_stub notify_thread.sh "#!/usr/bin/env bash
exit 0"
_stub notify.sh "#!/usr/bin/env bash
exit 0"
_stub append_event.sh "#!/usr/bin/env bash
exit 0"
_stub consolidate.sh "#!/usr/bin/env bash
exit 0"
# wake_thread.sh stub: ghi lại ĐÚNG những gì _bg_wrapper truyền vào (thread_id, prompt,
# name_suffix) — đây là thứ selfcheck này thật sự cần quan sát.
_stub wake_thread.sh "#!/usr/bin/env bash
printf 'thread_id=%s\tprompt=%s\tsuffix=%s\n' \"\$1\" \"\$2\" \"\${3:-}\" >> \"$SB/wake_thread.calls\""
cat > "$SB/claude_stub.sh" <<EOF
#!/usr/bin/env bash
echo "[claude-stub] ok"
exit \${CLAUDE_STUB_RC:-0}
EOF
chmod +x "$SB/claude_stub.sh"
for n in notify.sh notify_thread.sh append_event.sh consolidate.sh wake_thread.sh; do
  [ "$(wc -l < "$REAL/bin/$n")" -gt 5 ] || { echo "FATAL: $REAL/bin/$n bị ghi đè bởi stub — KHÔI PHỤC NGAY (git checkout -- bin/$n)"; exit 1; }
done

ARCH_ID="$(bash "$REAL/bin/discord_channel.sh" architecture)"
[ -n "$ARCH_ID" ] || { echo "FATAL: không phân giải được topic 'architecture' từ registry thật"; exit 1; }

FAILS=0; CASES=0
assert() {
  CASES=$((CASES + 1))
  if [ "$2" = "$3" ]; then
    printf '    ok   %s = %q\n' "$1" "$2"
  else
    printf '    FAIL %s: thực=%q ≠ mong đợi=%q\n' "$1" "$2" "$3"; FAILS=$((FAILS + 1))
  fi
}

RC=0; NWAKE=0; WAKE_LINE=""
_collect() {
  NWAKE=0
  [ -f "$SB/wake_thread.calls" ] && NWAKE="$(wc -l < "$SB/wake_thread.calls" | tr -d ' ')"
  WAKE_LINE="$([ -f "$SB/wake_thread.calls" ] && tail -1 "$SB/wake_thread.calls" || true)"
}

run_dispatch() {
  rm -f "$SB"/*.calls
  rm -f "$MK/bus/jobs"/*.json "$MK/logs"/*.log "$MK/logs"/*.err
  local envs=() ; while [ "$1" != "--" ]; do envs+=("$1"); shift; done; shift
  ( cd "$MK" && env "${envs[@]}" \
      DISPATCH_CGROUP_DETACH=0 DISPATCH_CLAUDE_BIN="$SB/claude_stub.sh" \
      DISPATCH_FROM="${FROM_AGENT:-Mike}" \
      bash "$MK/bin/dispatch.sh" "$@" ) > "$SB/out" 2> "$SB/err"
  RC=$?
  _collect
}

_wait_bg() {
  local i jf st
  for i in $(seq 1 80); do
    jf="$(find "$MK/bus/jobs" -name '*.json' | sort | head -1)"
    if [ -n "$jf" ]; then
      st="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("status",""))' "$jf" 2>/dev/null || true)"
      [ "$st" != "running" ] && [ "$st" != "retrying" ] && [ "$st" != "" ] && break
    fi
    sleep 0.5
  done
  sleep 1
  _collect
}

echo "== CA 1: from=Mike, job THÀNH CÔNG, có thread pinned ⇒ wake_thread.sh ĐƯỢC gọi"
FROM_AGENT=Mike CLAUDE_STUB_RC=0
run_dispatch -u DISCORD_THREAD_ID CLAUDE_STUB_RC=0 -- Wags "selfcheck wake ca1" --thread architecture --bg --timeout 30
_wait_bg
assert "exit code (--bg trả ngay)" "$RC" "0"
assert "wake_thread.sh được gọi đúng 1 lần" "$NWAKE" "1"
assert "wake gọi đúng thread pinned" "$(echo "$WAKE_LINE" | grep -oP 'thread_id=\K[0-9]+')" "$ARCH_ID"
assert "prompt wake nêu status=done" "$(echo "$WAKE_LINE" | grep -c 'status=done')" "1"

echo "== CA 2: from=Taylor (agent khác, không phải Mike) ⇒ wake_thread.sh KHÔNG được gọi dù thành công"
FROM_AGENT=Taylor
run_dispatch -u DISCORD_THREAD_ID CLAUDE_STUB_RC=0 -- Wags "[AUTO-CALLBACK job=x] selfcheck wake ca2" --thread architecture --bg --timeout 30
_wait_bg
assert "wake_thread.sh KHÔNG được gọi (from != Mike)" "$NWAKE" "0"

echo "== CA 3: from=Mike, job THẤT BẠI (hết retry) ⇒ wake_thread.sh vẫn được gọi ở nhánh fail"
FROM_AGENT=Mike
run_dispatch -u DISCORD_THREAD_ID CLAUDE_STUB_RC=1 -- Wags "selfcheck wake ca3" --thread architecture --bg --timeout 30 --retries 0
_wait_bg
assert "wake_thread.sh được gọi đúng 1 lần (nhánh fail)" "$NWAKE" "1"
assert "prompt wake nêu lý do fail (THẤT BẠI/timeout)" "$(echo "$WAKE_LINE" | grep -cE 'THẤT BẠI|timeout')" "1"

echo "== CA 4: from=Mike, KHÔNG có thread nào pinned (không --thread, không ambient) ⇒ wake_thread.sh KHÔNG được gọi"
FROM_AGENT=Mike
run_dispatch -u DISCORD_THREAD_ID CLAUDE_STUB_RC=0 -- Taylor "selfcheck wake ca4" --bg --timeout 30
_wait_bg
assert "wake_thread.sh KHÔNG được gọi (không có _tid để đánh thức)" "$NWAKE" "0"

echo
if [ "$FAILS" -eq 0 ]; then
  echo "PASS — $CASES/$CASES assertion đúng (active wake gated đúng: from=Mike + có _tid, cả 2 nhánh done/fail)"
  exit 0
else
  echo "FAIL — $FAILS/$CASES assertion sai"
  exit 1
fi
