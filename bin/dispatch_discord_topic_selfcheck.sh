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
#        hỏng" (trường hợp bất thường: pin RỖNG + ghi logs/notify_thread_errors.log, KHÔNG tụt
#        về ambient — KHÔNG phải "alert Telegram", xem vòng 5/6 ở CA 4). Gộp 2
#        cái này thành chuỗi rỗng = override cố định của Wags/DollarBill âm thầm biến thành topic
#        ambient — chính là lỗi 07-22 "override thành dead-code".
#   ABORT chỉ dành cho `--thread` TƯỜNG MINH không phân giải được: caller đã nêu đích danh 1 topic
#        thì phải dừng. Registry hỏng KHÔNG được chặn việc (F4, vòng 3): cron sinh plan T+1 dispatch
#        DollarBill không kèm `--thread`, chặn nó = "không có plan sáng mai" đổi lấy 1 tin nhắn.
#
# KỶ LUẬT (vòng 3 — bộ ca đầu tiên PASS Y HỆT trên code TRƯỚC bản vá, tức không test gì cả):
# mỗi ca phải được MUTATION TEST — revert đúng dòng nó canh rồi chạy lại, ca đó PHẢI FAIL.
# Đã đo 2026-08-02: bỏ `|| true` trong _job_thread_id ⇒ CA 9 fail; khôi phục fallback ambient ở
# done-notify ⇒ CA 8 fail; khôi phục `cat ccdb_thread_id` trong watchdog.sh ⇒ CA 10 fail.
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
# SELFCHECK_MIDRUN_POINTER: dựng con trỏ toàn cục XUẤT HIỆN GIỮA CHỪNG (user mở 1 topic khác
# trong lúc job đang chạy) — mô phỏng đúng cửa sổ mà tầng "đoán lại topic" từng rò rỉ qua.
cat > "$SB/claude_stub.sh" <<EOF
#!/usr/bin/env bash
{ echo "DISCORD_THREAD_ID=\${DISCORD_THREAD_ID-<UNSET>}"; echo "JOB_ID=\${JOB_ID-<UNSET>}"; } > "$SB/claude.env"
[ -n "\${SELFCHECK_MIDRUN_POINTER:-}" ] && printf '%s\n' "\$SELFCHECK_MIDRUN_POINTER" > "$MK/agents/Mike/state/ccdb_thread_id"
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

RC=0; PINNED=""; CHILD_TID=""; NCALLS=0; NJOBS=0; FROM_AGENT=Mike
# _collect — đọc lại trạng thái quan sát được sau một lần dispatch (dùng chung sync/bg).
_collect() {
  NJOBS="$(find "$MK/bus/jobs" -name '*.json' | wc -l | tr -d ' ')"
  local jf; jf="$(find "$MK/bus/jobs" -name '*.json' | sort | head -1)"
  PINNED=""
  [ -n "$jf" ] && PINNED="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("discord_thread_id",""))' "$jf")"
  CHILD_TID="$(sed -n 's/^DISCORD_THREAD_ID=//p' "$SB/claude.env" 2>/dev/null || true)"
  [ -f "$SB/claude.env" ] || CHILD_TID="<CLAUDE-KHONG-CHAY>"
  NCALLS=0
  [ -f "$SB/notify_thread.calls" ] && NCALLS="$(wc -l < "$SB/notify_thread.calls" | tr -d ' ')"
}
# run_dispatch <env_assignments...> -- <dispatch args...>
# ⚠️ "${envs[@]}" PHẢI đứng đầu: `env` chỉ nhận cờ (`-u VAR`) TRƯỚC NAME=VALUE đầu tiên, đặt sau
# thì `-u` bị hiểu là tên lệnh ⇒ exit 127 (đã dẫm phải khi viết ca 9).
# Người gọi (DISPATCH_FROM) đổi qua biến $FROM_AGENT, không qua envs — ca AUTO-CALLBACK cần nó
# là agent thật, vì Mike/user bị guard chặn callback.
run_dispatch() {
  rm -f "$SB"/*.calls "$SB/claude.env"
  rm -f "$MK/bus/jobs"/*.json "$MK/logs"/*.log "$MK/logs"/*.err
  local envs=() ; while [ "$1" != "--" ]; do envs+=("$1"); shift; done; shift
  ( cd "$MK" && env "${envs[@]}" \
      DISPATCH_CGROUP_DETACH=0 DISPATCH_CLAUDE_BIN="$SB/claude_stub.sh" \
      DISPATCH_FROM="${FROM_AGENT:-Mike}" \
      DISPATCH_TIMEOUT_DOLLARBILL=60 \
      bash "$MK/bin/dispatch.sh" "$@" ) > "$SB/out" 2> "$SB/err"
  RC=$?
  _collect
}
# _wait_bg <số job record mong đợi> — job `--bg` chạy tách tiến trình, phải CHỜ rồi mới đo.
# Chờ tới khi đủ số record VÀ record đầu đã chốt trạng thái (hoặc hết 40s), + 2s cho các
# tác dụng phụ đuôi (notify/auto-callback) kịp xảy ra ⇒ "0 tin nhắn" là kết luận thật.
_wait_bg() {
  local want="$1" i jf st
  for i in $(seq 1 80); do
    jf="$(find "$MK/bus/jobs" -name '*.json' | sort | head -1)"
    if [ -n "$jf" ]; then
      st="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("status",""))' "$jf" 2>/dev/null || true)"
      if [ "$st" != "running" ] && [ "$st" != "" ] \
         && [ "$(find "$MK/bus/jobs" -name '*.json' | wc -l | tr -d ' ')" -ge "$want" ]; then
        break
      fi
    fi
    sleep 0.5
  done
  sleep 2
  _collect
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
# Mong đợi RỖNG chứ không phải <UNSET> (đổi 2026-08-02, vòng 4 M2): dispatch.sh nay LUÔN
# `export DISCORD_THREAD_ID` — bằng pin, hoặc bằng chuỗi rỗng tường minh khi pin rỗng. Với
# consumer thì rỗng ≡ không có (`${DISCORD_THREAD_ID:-}` ở khắp nơi), nhưng export tường minh
# chặn được việc agent con THỪA KẾ biến của tiến trình cha — xem CA 4b.
assert "agent con KHÔNG có topic (biến rỗng tường minh)" "$CHILD_TID" ""
assert "số tin nhắn Discord" "$NCALLS" "0"

echo "== CA 4: registry HỎNG + agent CÓ override ⇒ VẪN chạy, pin RỖNG, Discord im lặng (S2/F4)"
# ĐÁNH ĐỔI chốt 2026-08-02 (arch-reviewer vòng 3, F4): bản trước ABORT ở đây. Sai — cron
# `bq_freshness_check.sh` dispatch DollarBill (có override) KHÔNG kèm `--thread`, nên registry
# hỏng sẽ chặn luôn job SINH PLAN T+1 ⇒ sáng hôm sau bot chạy không có plan. Đổi "user không
# thấy 1 tin nhắn" lấy "không có việc" là sai hướng cho một sự cố THUẦN ĐỊNH TUYẾN THÔNG BÁO.
# Nay: pin RỖNG + ghi logs/notify_thread_errors.log + VẪN CHẠY. Vẫn KHÔNG tụt về ambient (đó mới
# là rò rỉ). (Bản trước ghi "alert Telegram" ở đây — SAI, xem ghi chú vòng 5/6 dưới.)
rm -f "$MK/logs/notify_thread_errors.log"
run_dispatch -u DISCORD_THREAD_ID DISCORD_CHANNELS_REGISTRY=/nonexistent/registry.json -- \
  Wags "selfcheck ca4" --timeout 60
assert "exit code" "$RC" "0"
assert "job VẪN chạy (có job record)" "$NJOBS" "1"
assert "ID ghim RỖNG (không đoán topic thay thế)" "$PINNED" ""
assert "agent con KHÔNG có topic (biến rỗng tường minh)" "$CHILD_TID" ""
assert "số tin nhắn Discord" "$NCALLS" "0"
assert "cảnh báo registry hỏng (notify.sh → #mikefleet)" "$(grep -c 'registry' "$SB/notify.calls" 2>/dev/null || echo 0)" "1"
# Vòng 5: đường báo TRÊN không đáng tin trong ĐÚNG ca này — `notify_discord.sh:22` cũng phân
# giải tên `mikefleet` qua CHÍNH registry đang hỏng (`set -e` ⇒ chết trước curl; đo thật:
# `DISCORD_CHANNELS_REGISTRY=/nonexistent notify.sh "..."` → "send failed (rc=1)"). Ở đây
# notify.sh là STUB nên nó "thành công" — đúng lớp PASS-GIẢ. Vậy nên bất biến thật phải là khâu
# GHI không chết cùng registry: ghi logs/notify_thread_errors.log (ops_health_check check #10
# đọc file này 08:20/12:45). Đó là thứ bảo đảm sự cố registry không im lặng Ở KHÂU GHI.
# Vòng 6 (arch-reviewer) — PHẠM VI: chỉ khâu GHI mới độc lập với Discord. Khâu GIAO TỚI NGƯỜI
# của check #10 là `ops_health_check.sh:587` → notify_thread.sh TÊN 'trading_daily' → CHÍNH
# registry này ⇒ registry hỏng kéo dài thì báo cáo health-check cũng câm. Vá: ops_health_check
# rơi sang Telegram khi notify_thread.sh trả khác 0 (canh bởi ops_health_check_selfcheck.py,
# khối DELIVER — không thuộc phạm vi file này).
assert "ghi logs/notify_thread_errors.log (khâu GHI không chết cùng registry)" \
  "$(grep -c 'registry Discord HONG' "$MK/logs/notify_thread_errors.log" 2>/dev/null || echo 0)" "1"

echo "== CA 4b: pin RỖNG trong khi tiến trình cha CÓ ambient ⇒ agent con KHÔNG được thừa kế (M2)"
# Ca DUY NHẤT phủ được lỗi 07-22b ở dạng mới: job record nói "không có topic" nhưng agent con
# lại thấy topic của phiên cha ⇒ mọi `notify_thread.sh "<msg>"` (không đối số 2) do CHÍNH agent
# gọi rơi vào topic Mike đang chat, dù wrapper im lặng đúng thiết kế. Record và env phải đồng ý.
# Dựng cửa sổ đó: registry hỏng + agent CÓ override ⇒ pin bị xoá rỗng, NHƯNG $DISCORD_THREAD_ID
# của cha VẪN còn giá trị. Thiếu nhánh `else export DISCORD_THREAD_ID=""` là ca này FAIL ngay.
run_dispatch DISCORD_THREAD_ID="$ARCH_ID" DISCORD_CHANNELS_REGISTRY=/nonexistent/registry.json -- \
  Wags "selfcheck ca4b" --timeout 60
assert "exit code" "$RC" "0"
assert "ID ghim RỖNG" "$PINNED" ""
assert "agent con KHÔNG thừa kế ambient của cha" "$CHILD_TID" ""
assert "số tin nhắn Discord" "$NCALLS" "0"

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
# ⚠️ TRẢ LẠI STUB NGAY: CA 6 vừa thay symlink notify_thread.sh THẬT vào sandbox. Ca nào chạy sau
# mà quên bước này sẽ (a) gọi API Discord THẬT, và (b) đếm "0 tin nhắn" từ file .calls không bao
# giờ được ghi ⇒ PASS GIẢ. Đúng lớp lỗi mà chính script này sinh ra để chặn.
_stub notify_thread.sh "#!/usr/bin/env bash
printf '%s\n' \"\${2:-<NO_TOPIC>}\" >> \"$SB/notify_thread.calls\""

echo "== CA 7: --thread= RỖNG (biến chưa set) ⇒ ABORT, không âm thầm tụt về ambient (F6)"
printf '%s\n' "$ARCH_ID" > "$MK/agents/Mike/state/ccdb_thread_id"   # ambient CÓ, phải KHÔNG được dùng
run_dispatch -u DISCORD_THREAD_ID -- Wags "selfcheck ca7" --thread= --timeout 60
assert "exit code khác 0" "$([ "$RC" -ne 0 ] && echo yes || echo no)" "yes"
assert "claude KHÔNG được chạy" "$CHILD_TID" "<CLAUDE-KHONG-CHAY>"
assert "không tạo job record" "$NJOBS" "0"

echo "== CA 8: pin RỖNG + con trỏ toàn cục xuất hiện GIỮA CHỪNG ⇒ 0 tin nhắn (S1, --bg)"
# Ca này là ca DUY NHẤT bắt được đúng cửa sổ rò rỉ thật: lúc dispatch không có topic nào (pin
# rỗng), rồi user mở một topic khác trong lúc job chạy ⇒ con trỏ toàn cục đổi. Mọi tầng "đoán
# lại" sau đó sẽ gửi vào topic user vừa mở. Bộ ca cũ KHÔNG bắt được vì con trỏ luôn tĩnh.
rm -f "$MK/agents/Mike/state/ccdb_thread_id"
run_dispatch -u DISCORD_THREAD_ID SELFCHECK_MIDRUN_POINTER="$ARCH_ID" -- \
  Taylor "selfcheck ca8" --bg --timeout 60
_wait_bg 1
assert "exit code" "$RC" "0"
assert "ID ghim rỗng" "$PINNED" ""
assert "con trỏ toàn cục ĐÃ xuất hiện giữa chừng" \
  "$(cat "$MK/agents/Mike/state/ccdb_thread_id" 2>/dev/null || echo '<KHONG-CO>')" "$ARCH_ID"
assert "số tin nhắn Discord" "$NCALLS" "0"

echo "== CA 9: pin RỖNG ⇒ AUTO-CALLBACK vẫn chạy (pin rỗng không được GIẾT _bg_wrapper, F2)"
# `mike_json.py job-field` EXIT 1 khi field rỗng; `_bg_wrapper` bật lại `set -e` giữa chừng ⇒
# thiếu `|| true` trong _job_thread_id là cả wrapper chết ngay tại dòng đọc pin, mất luôn
# AUTO-CALLBACK báo kết quả về agent đã gọi việc. Đo bằng SỐ JOB RECORD: 1 = wrapper chết,
# 2 = wrapper sống và đã đẻ job callback.
rm -f "$MK/agents/Mike/state/ccdb_thread_id"
FROM_AGENT=Wags run_dispatch -u DISCORD_THREAD_ID -- Taylor "selfcheck ca9" --bg --timeout 60
FROM_AGENT=Mike
_wait_bg 2
assert "exit code" "$RC" "0"
assert "ID ghim rỗng" "$PINNED" ""
assert "có job AUTO-CALLBACK (wrapper sống qua chỗ đọc pin rỗng)" "$NJOBS" "2"
assert "job callback đúng là gửi về người gọi (Wags)" \
  "$(find "$MK/bus/jobs" -name 'Wags_*.json' | wc -l | tr -d ' ')" "1"

echo "== CA 10: KHÔNG còn nơi nào ĐỌC con trỏ toàn cục (F1 + vòng 4: tầng đoán bỏ HẲN)"
# Ca hành vi không phủ được `watchdog.sh`: nó tự `cat` con trỏ rồi truyền ID TƯỜNG MINH, nên
# việc gỡ tầng đoán khỏi notify_thread.sh KHÔNG chặn được nó (đúng lỗi F1). Bài học của sự cố
# là "sửa nơi TIÊU THỤ chưa đủ, phải grep mọi nơi tự đọc NGUỒN" ⇒ mã hoá thành bất biến tĩnh.
# Chạy trên cây nguồn THẬT ($REAL), không phải sandbox. (watchdog.sh không test hành vi được:
# nó quét systemd unit thật của user, chạy trong test là đụng dịch vụ sống.)
#
# NGƯỠNG ĐỔI 1 → 0 (2026-08-02, vòng 4): vòng 3 chấp nhận ĐÚNG 1 nơi đọc (`_ambient_thread`
# tầng 3 trong dispatch.sh) vì lúc đó tầng đoán vẫn còn. Vòng 4 xác định chính tầng đó là điều
# kiện tồn tại của cả 4 sự cố và đã XOÁ HẲN ⇒ bất biến đúng bây giờ là KHÔNG AI ĐỌC. Con trỏ
# chỉ còn được GHI (hooks/session_start.sh) và không còn người tiêu thụ — xem chú thích "code
# chết" tại chính chỗ ghi đó.
_mentions="$(grep -rn 'ccdb_thread_id' "$REAL/bin" "$REAL/hooks" 2>/dev/null \
            | grep -v 'dispatch_discord_topic_selfcheck.sh' \
            | grep -v ':[0-9]*: *#' || true)"
# GHI = có dấu chuyển hướng `>` trước tên file; mọi dạng khác (cat/$(<)/read) tính là ĐỌC.
# Không khớp theo tên file để một hàm đọc mới thêm vào session_start.sh vẫn bị bắt.
_writes="$(printf '%s' "$_mentions" | grep '>[^>]*ccdb_thread_id' || true)"
_readers="$(printf '%s' "$_mentions" | grep -v '>[^>]*ccdb_thread_id' || true)"
assert "số nơi ĐỌC con trỏ toàn cục (tầng đoán đã bỏ hẳn ⇒ phải là 0)" \
  "$(printf '%s' "$_readers" | grep -c . )" "0"
assert "số nơi GHI con trỏ toàn cục" "$(printf '%s' "$_writes" | grep -c . )" "1"
assert "nơi GHI duy nhất là hooks/session_start.sh" \
  "$(printf '%s' "$_writes" | grep -c '/hooks/session_start\.sh:')" "1"

echo
if [ "$FAILS" -eq 0 ]; then
  echo "PASS — $CASES/$CASES assertion đúng (S1 không-đoán + S2 abort-đúng-chỗ + R1 notify_thread)"
  exit 0
fi
echo "FAIL — $FAILS/$CASES assertion sai"
exit 1
