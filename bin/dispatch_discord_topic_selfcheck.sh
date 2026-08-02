#!/usr/bin/env bash
# dispatch_discord_topic_selfcheck.sh — self-check HÀNH VI ĐỊNH TUYẾN TOPIC của bin/dispatch.sh
# + bin/notify_thread.sh (bản vá 2026-08-02, arch-reviewer S1/S2).
#
# VÌ SAO cần: 4 sự cố rò rỉ chéo topic (2026-07-01, 07-06, 07-22, 07-22b) đều CÙNG một cơ chế —
# một tầng nào đó "đoán lại" topic khi giá trị đã ghim rỗng, và vì mọi caller bọc `2>/dev/null
# || true` nên đoán sai KHÔNG BAO GIỜ fail, chỉ biểu hiện thành "tin nhắn rơi nhầm topic". Bản
# vá 2026-08-02 chốt 2 nguyên tắc; script này là thứ duy nhất giữ chúng không mục:
#   S1 — KHÔNG ĐOÁN: mọi consumer sau lúc dispatch chỉ ĐỌC LẠI ID đã ghim trên job record.
#        Ghim rỗng ⇒ IM LẶNG phía Discord (không rơi về ambient / con trỏ toàn cục).
#   S2 — Phân biệt "agent KHÔNG có override" (hợp lệ, đi tiếp) với "CÓ override nhưng registry
#        hỏng" (ABORT). Gộp 2 cái này thành chuỗi rỗng = override cố định của Wags/DollarBill
#        âm thầm biến thành topic ambient — chính là lỗi 07-22 "override thành dead-code".
#
# CÁCH TEST (điểm mấu chốt — KHÔNG copy logic): dựng một ROOT mike GIẢ trong tmpdir, bin/ là
# SYMLINK tới file THẬT (dispatch.sh, discord_channel.sh, mike_json.py…) nên test luôn chạy
# trên đúng code production; chỉ notify.sh / notify_thread.sh / append_event.sh / consolidate.sh
# là stub ghi log ⇒ KHÔNG ping Discord/Telegram/git thật. `claude` được thay bằng stub qua
# DISPATCH_CLAUDE_BIN (hook có sẵn trong dispatch.sh) — stub dump env của tiến trình con, nhờ
# đó kiểm được ID GHIM trên job record và ID mà AGENT THẬT SỰ nhận có khớp nhau không (đúng
# cặp lệch nhau đã gây sự cố 07-22b).
#
# Usage: bash mike/bin/dispatch_discord_topic_selfcheck.sh   (exit 0 = tất cả ca PASS)
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

# Stub: ghi lại lời gọi thay vì gửi thật. `$2` của notify_thread.sh = topic ⇒ đó chính là thứ
# ta cần quan sát (gửi vào topic nào, hay không gửi gì cả).
#
# ⚠️ PHẢI `rm -f` symlink TRƯỚC khi ghi stub. `cat > <symlink>` ĐI THEO symlink và cắt cụt FILE
# THẬT trong bin/ — đã xảy ra thật khi viết script này (2026-08-02): 4 script sống của fleet bị
# thay bằng stub 2 dòng, may mà git khôi phục được. Hàm _stub bên dưới là hàng rào duy nhất.
_stub() {  # _stub <tên file trong bin> <nội dung>
  rm -f "$MK/bin/$1"                                  # gỡ symlink, KHÔNG ghi xuyên qua nó
  [ -e "$MK/bin/$1" ] && { echo "FATAL: không gỡ được $MK/bin/$1"; exit 1; }
  printf '%s\n' "$2" > "$MK/bin/$1"
  chmod +x "$MK/bin/$1"
  [ -L "$MK/bin/$1" ] && { echo "FATAL: $MK/bin/$1 vẫn là symlink — dừng để khỏi hỏng file thật"; exit 1; }
  return 0
}
_stub notify_thread.sh "#!/usr/bin/env bash
printf '%s\n' \"\${2:-<NO_TOPIC>}\" >> \"$SB/notify_thread.calls\""
_stub notify.sh "#!/usr/bin/env bash
printf '%s\n' \"\$1\" >> \"$SB/notify.calls\""
_stub append_event.sh "#!/usr/bin/env bash
exit 0"
_stub consolidate.sh "#!/usr/bin/env bash
exit 0"
# claude stub: dump env con (⇒ kiểm được ID agent THẬT SỰ nhận) + báo đã chạy.
cat > "$SB/claude_stub.sh" <<EOF
#!/usr/bin/env bash
{ echo "DISCORD_THREAD_ID=\${DISCORD_THREAD_ID-<UNSET>}"; echo "JOB_ID=\${JOB_ID-<UNSET>}"; } > "$SB/claude.env"
echo "[claude-stub] ok"
exit \${CLAUDE_STUB_RC:-0}
EOF
chmod +x "$SB/claude_stub.sh"
# Hàng rào cuối: file THẬT trong bin/ phải nguyên vẹn sau khi dựng sandbox.
for n in notify.sh notify_thread.sh append_event.sh consolidate.sh; do
  [ "$(wc -l < "$REAL/bin/$n")" -gt 5 ] || { echo "FATAL: $REAL/bin/$n bị ghi đè bởi stub — KHÔI PHỤC NGAY (git checkout -- bin/$n)"; exit 1; }
done

ARCH_ID="$(bash "$REAL/bin/discord_channel.sh" architecture)"
[ -n "$ARCH_ID" ] || { echo "FATAL: không phân giải được topic 'architecture' từ registry thật"; exit 1; }

FAILS=0; CASES=0
# assert <mô tả> <giá trị thực> <giá trị mong đợi>
assert() {
  CASES=$((CASES + 1))
  if [ "$2" = "$3" ]; then
    printf '    ok   %s = %q\n' "$1" "$2"
  else
    printf '    FAIL %s: thực=%q ≠ mong đợi=%q\n' "$1" "$2" "$3"; FAILS=$((FAILS + 1))
  fi
}

RC=0; PINNED=""; CHILD_TID=""; NCALLS=0; NJOBS=0
# run_dispatch <env_assignments...> -- <dispatch args...>
run_dispatch() {
  rm -f "$SB"/*.calls "$SB/claude.env"
  rm -f "$MK/bus/jobs"/*.json "$MK/logs"/*.log "$MK/logs"/*.err
  local envs=() ; while [ "$1" != "--" ]; do envs+=("$1"); shift; done; shift
  ( cd "$MK" && env "${envs[@]}" \
      DISPATCH_CGROUP_DETACH=0 DISPATCH_CLAUDE_BIN="$SB/claude_stub.sh" DISPATCH_FROM=Mike \
      DISPATCH_TIMEOUT_DOLLARBILL=60 \
      bash "$MK/bin/dispatch.sh" "$@" ) > "$SB/out" 2> "$SB/err"
  RC=$?
  NJOBS="$(find "$MK/bus/jobs" -name '*.json' | wc -l | tr -d ' ')"
  local jf; jf="$(find "$MK/bus/jobs" -name '*.json' | head -1)"
  PINNED=""
  [ -n "$jf" ] && PINNED="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("discord_thread_id",""))' "$jf")"
  CHILD_TID="$(sed -n 's/^DISCORD_THREAD_ID=//p' "$SB/claude.env" 2>/dev/null || true)"
  [ -f "$SB/claude.env" ] || CHILD_TID="<CLAUDE-KHONG-CHAY>"
  NCALLS=0
  [ -f "$SB/notify_thread.calls" ] && NCALLS="$(wc -l < "$SB/notify_thread.calls" | tr -d ' ')"
}

echo "== CA 1: dispatch bình thường (Wags, không --thread) — override ghim + agent nhận ĐÚNG ID"
printf '%s\n' "$ARCH_ID" > "$MK/agents/Mike/state/ccdb_thread_id"   # ambient có sẵn, override phải THẮNG
run_dispatch -u DISCORD_THREAD_ID -- Wags "selfcheck ca1" --timeout 60
assert "exit code" "$RC" "0"
assert "ID ghim trên job record" "$PINNED" "$ARCH_ID"
assert "ID agent con thật sự nhận" "$CHILD_TID" "$ARCH_ID"

echo "== CA 2: --thread TÊN SAI ⇒ ABORT (không dispatch, không đoán topic khác)"
run_dispatch -u DISCORD_THREAD_ID -- Wags "selfcheck ca2" --thread trading_dialy --timeout 60
assert "exit code khác 0" "$([ "$RC" -ne 0 ] && echo yes || echo no)" "yes"
assert "claude KHÔNG được chạy" "$CHILD_TID" "<CLAUDE-KHONG-CHAY>"
assert "không tạo job record" "$NJOBS" "0"
assert "stderr báo HUỶ" "$(grep -c 'HUỶ' "$SB/err")" "1"

echo "== CA 3: agent không override + không ambient nào ⇒ VẪN dispatch, Discord IM LẶNG"
rm -f "$MK/agents/Mike/state/ccdb_thread_id"
run_dispatch -u DISCORD_THREAD_ID -- Taylor "selfcheck ca3" --timeout 60
assert "exit code" "$RC" "0"
assert "ID ghim rỗng (không đoán)" "$PINNED" ""
assert "agent con KHÔNG có DISCORD_THREAD_ID" "$CHILD_TID" "<UNSET>"
assert "số tin nhắn Discord" "$NCALLS" "0"

echo "== CA 4: registry HỎNG + agent CÓ override ⇒ ABORT rõ ràng (S2)"
run_dispatch -u DISCORD_THREAD_ID DISCORD_CHANNELS_REGISTRY=/nonexistent/registry.json -- \
  Wags "selfcheck ca4" --timeout 60
assert "exit code khác 0" "$([ "$RC" -ne 0 ] && echo yes || echo no)" "yes"
assert "claude KHÔNG được chạy" "$CHILD_TID" "<CLAUDE-KHONG-CHAY>"
assert "không tạo job record" "$NJOBS" "0"
assert "cảnh báo registry hỏng (Telegram)" "$(grep -c 'registry' "$SB/notify.calls" 2>/dev/null || echo 0)" "1"

echo "== CA 5: registry hỏng + agent KHÔNG override + có ID trần ⇒ VẪN chạy (abort phải ĐÚNG chỗ)"
run_dispatch DISCORD_THREAD_ID="$ARCH_ID" DISCORD_CHANNELS_REGISTRY=/nonexistent/registry.json -- \
  Taylor "selfcheck ca5" --timeout 60
assert "exit code" "$RC" "0"
assert "ID ghim = ID trần truyền vào" "$PINNED" "$ARCH_ID"
assert "agent con nhận đúng ID" "$CHILD_TID" "$ARCH_ID"

echo "== CA 6: notify_thread.sh không có topic nào ⇒ THOÁT LỖI, không rơi về con trỏ toàn cục (R1)"
printf '%s\n' "$ARCH_ID" > "$MK/agents/Mike/state/ccdb_thread_id"   # con trỏ toàn cục CÓ tồn tại
rm -f "$MK/logs/notify_thread_errors.log"
rm -f "$MK/bin/notify_thread.sh" && ln -s "$REAL/bin/notify_thread.sh" "$MK/bin/notify_thread.sh"
out6="$(env -u DISCORD_THREAD_ID bash "$MK/bin/notify_thread.sh" "selfcheck ca6 — KHONG DUOC GUI" 2>&1)"; rc6=$?
assert "exit code khác 0" "$([ "$rc6" -ne 0 ] && echo yes || echo no)" "yes"
assert "báo không đoán topic" "$(printf '%s' "$out6" | grep -c 'không đoán topic')" "1"
assert "ghi vào notify_thread_errors.log" \
  "$(grep -c 'KHONG CO topic' "$MK/logs/notify_thread_errors.log" 2>/dev/null || echo 0)" "1"

echo
if [ "$FAILS" -eq 0 ]; then
  echo "PASS — $CASES/$CASES assertion đúng (S1 không-đoán + S2 abort-đúng-chỗ + R1 notify_thread)"
  exit 0
fi
echo "FAIL — $FAILS/$CASES assertion sai"
exit 1
