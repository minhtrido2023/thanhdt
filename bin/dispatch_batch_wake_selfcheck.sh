#!/usr/bin/env bash
# dispatch_batch_wake_selfcheck.sh — hồi quy cho BATCH-AWARE WAKE (2026-08-20, RCA
# agents/Mike/research/plan_pipeline_3loi_rca_20260820.md lỗi #1).
#
# Bất biến phải giữ:
#   (A) N job cùng --batch-id ⇒ ĐÚNG 1 lượt wake_thread.sh cho cả đợt, do job terminal
#       CUỐI CÙNG bắn, prompt gộp liệt kê MỌI job của đợt.
#   (B) Job KHÔNG có --batch-id ⇒ hành vi y hệt trước: mỗi job tự bắn wake của nó.
#   (C) FAIL-SAFE — không bao giờ nuốt mất wake: anh em TREO (record kẹt non-terminal, pid
#       chết, quá deadline) không được chặn; batch thiếu/hỏng ⇒ quay về wake đơn lẻ.
#   (D) Reconciler (lưới cuối) KHÔNG cứu job đang im lặng chờ anh em (batch còn bay), nhưng
#       cứu lại ngay khi batch hết bay.
#
# Hai tầng test, cố ý tách:
#   PHẦN 1 — dispatch THẬT trong sandbox (symlink bin/ thật, chỉ stub side-effect ra ngoài),
#            cùng khuôn với dispatch_wake_selfcheck.sh. Bắt được lỗi wiring (export biến,
#            đặt call site sai chỗ) mà test đơn vị không thấy.
#   PHẦN 2 — đua/treo ở mức nguyên thủy batch-claim-wake: dựng THẲNG job record ở trạng thái
#            cần (đang chạy / treo pid chết / quá deadline) vì không cách nào ép một job thật
#            treo đúng lúc mình muốn. Đây là chỗ duy nhất test được ca "1 job không bao giờ
#            terminal".
#
# Usage: bash mike/bin/dispatch_batch_wake_selfcheck.sh   (exit 0 = PASS)
set -uo pipefail

REAL="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SB="$(mktemp -d)"
trap 'rm -rf "$SB"' EXIT
MK="$SB/mike"

mkdir -p "$MK/bin" "$MK/kb" "$MK/bus/jobs" "$MK/bus/batches" "$MK/logs" "$MK/state/circuit" \
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
# Stub ghi MỖI LỜI GỌI trên ĐÚNG MỘT DÒNG: prompt wake của batch là NHIỀU DÒNG (nó liệt kê
# từng job), nên không ép xuống 1 dòng thì `wc -l` đếm 6 cho 1 lần gọi — đúng cái bẫy đã làm
# bản selfcheck đầu tiên báo FAIL giả (2026-08-20).
_stub wake_thread.sh "#!/usr/bin/env bash
printf 'thread_id=%s\tprompt=%s\tsuffix=%s\n' \"\$1\" \"\${2//\$'\n'/ | }\" \"\${3:-}\" >> \"$SB/wake_thread.calls\""
# Chốt an toàn y như dispatch_wake_selfcheck.sh: nếu _stub lỡ ghi vào bin/ THẬT thì dừng ngay.
for n in notify.sh notify_thread.sh append_event.sh consolidate.sh wake_thread.sh; do
  [ "$(wc -l < "$REAL/bin/$n")" -gt 5 ] || { echo "FATAL: $REAL/bin/$n bị ghi đè bởi stub — KHÔI PHỤC NGAY (git checkout -- bin/$n)"; exit 1; }
done
cat > "$SB/claude_stub.sh" <<EOF
#!/usr/bin/env bash
sleep \${CLAUDE_STUB_SLEEP:-0}
echo "[claude-stub] ok"
exit \${CLAUDE_STUB_RC:-0}
EOF
chmod +x "$SB/claude_stub.sh"

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
_nwake() { [ -f "$SB/wake_thread.calls" ] && wc -l < "$SB/wake_thread.calls" | tr -d ' ' || echo 0; }
_reset() { rm -f "$SB"/*.calls; rm -f "$MK/bus/jobs"/*.json "$MK/bus/jobs"/*.lock \
                 "$MK/bus/batches"/* "$MK/logs"/*.log "$MK/logs"/*.err 2>/dev/null; return 0; }

_dispatch_bg() {  # _dispatch_bg <agent> <prompt> [cờ thêm...]
  ( cd "$MK" && env CLAUDE_STUB_RC=0 CLAUDE_STUB_SLEEP="${STUB_SLEEP:-0}" \
      DISPATCH_CGROUP_DETACH=0 DISPATCH_CLAUDE_BIN="$SB/claude_stub.sh" DISPATCH_FROM=Mike \
      bash "$MK/bin/dispatch.sh" "$@" --thread architecture --bg --timeout 30 ) \
    > "$SB/out" 2>> "$SB/err"
}

_wait_all_terminal() {  # chờ mọi job record rời trạng thái đang chạy
  local i n_run
  for i in $(seq 1 120); do
    n_run="$(grep -l '"status": *"\(running\|retrying\)"' "$MK/bus/jobs"/*.json 2>/dev/null | wc -l)"
    [ "$n_run" = "0" ] && break
    sleep 0.5
  done
  sleep 1.5
}

echo "== CA 1: 2 job cùng --batch-id (dispatch THẬT) ⇒ ĐÚNG 1 lượt wake, prompt gộp cả 2 job"
_reset
BID="selfcheck.batch1"
_dispatch_bg Wags "batch job A" --batch-id "$BID" --batch-size 2
STUB_SLEEP=3 _dispatch_bg Taylor "batch job B" --batch-id "$BID" --batch-size 2
_wait_all_terminal
JOBS_ALL="$(ls "$MK/bus/jobs"/*.json | sed 's#.*/##;s/\.json$//' | sort)"
NJOB="$(printf '%s\n' "$JOBS_ALL" | grep -c .)"
assert "2 job record được tạo" "$NJOB" "2"
assert "wake_thread.sh được gọi ĐÚNG 1 lần cho cả batch" "$(_nwake)" "1"
WLINE="$(tail -1 "$SB/wake_thread.calls" 2>/dev/null || true)"
assert "prompt wake nêu batch_id" "$(echo "$WLINE" | grep -c "BATCH \`$BID\`")" "1"
NLISTED=0
for j in $JOBS_ALL; do
  echo "$WLINE" | grep -q "claim-reply <job_id>" && : # template chung
  echo "$WLINE" | grep -q "$j" && NLISTED=$((NLISTED + 1))
done
assert "prompt liệt kê ĐỦ cả 2 job của batch" "$NLISTED" "2"
assert "wake bắn vào đúng thread pinned" "$(echo "$WLINE" | grep -oP 'thread_id=\K[0-9]+')" "$ARCH_ID"
assert "batch record ghi người claim theo THREAD (wake_claimed[thread])" \
  "$(python3 -c "import json;print(1 if (json.load(open('$MK/bus/batches/$BID.json')).get('wake_claimed') or {}).get('$ARCH_ID') else 0)")" "1"

echo "== CA 1b: batch có job FAIL + job DONE ⇒ vẫn ĐÚNG 1 wake (call site nhánh thất bại)"
_reset
BID1B="selfcheck.batch1b"
( cd "$MK" && env CLAUDE_STUB_RC=1 CLAUDE_STUB_SLEEP=0 DISPATCH_CGROUP_DETACH=0 \
    DISPATCH_CLAUDE_BIN="$SB/claude_stub.sh" DISPATCH_FROM=Mike \
    bash "$MK/bin/dispatch.sh" Wags "batch job FAIL" --batch-id "$BID1B" --batch-size 2 \
      --thread architecture --bg --timeout 30 --retries 0 ) > "$SB/out" 2>> "$SB/err"
STUB_SLEEP=3 _dispatch_bg Taylor "batch job DONE" --batch-id "$BID1B" --batch-size 2
_wait_all_terminal
assert "1 job fail + 1 job done cùng batch ⇒ vẫn đúng 1 wake" "$(_nwake)" "1"
assert "prompt gộp nêu ĐỦ 2 trạng thái (failed + done)" \
  "$(tail -1 "$SB/wake_thread.calls" | grep -cE 'status=(failed|timeout).*status=done|status=done.*status=(failed|timeout)')" "1"

echo "== CA 2: KHÔNG --batch-id ⇒ hành vi cũ, mỗi job tự bắn wake (2 job = 2 wake)"
_reset
_dispatch_bg Wags "no-batch job A"
_dispatch_bg Taylor "no-batch job B"
_wait_all_terminal
assert "2 job không batch ⇒ 2 lượt wake (giữ nguyên hành vi cũ)" "$(_nwake)" "2"

echo "== CA 3: batch-id có nhưng batch record BỊ XOÁ giữa chừng ⇒ vẫn wake (đơn lẻ), không nuốt"
_reset
BID3="selfcheck.batch3"
STUB_SLEEP=2 _dispatch_bg Wags "batch job mất record" --batch-id "$BID3" --batch-size 1
sleep 0.8
rm -f "$MK/bus/batches/$BID3.json"
_wait_all_terminal
assert "batch record mất ⇒ vẫn có đúng 1 wake (fallback đơn lẻ)" "$(_nwake)" "1"
assert "prompt fallback là prompt ĐƠN LẺ (có status=done, không có chữ BATCH)" \
  "$(tail -1 "$SB/wake_thread.calls" | grep -c 'BATCH')" "0"

echo "== CA 4 (đơn vị): đua — 2 member cùng terminal, chỉ 1 người claim được"
_reset
JD="$MK/bus/jobs"; BD="$MK/bus/batches"
mk_job() {  # mk_job <job_id> <status> <pid> <deadline_offset> [from] [thread] [ended_at|-] [replied|-]
  python3 - "$JD" "$1" "$2" "$3" "$4" "${5-Mike}" "${6-1}" "${7-auto}" "${8--}" <<'PY'
import json, os, sys, time
jd, jid, st, pid, off, frm, tid, ended, replied = sys.argv[1:10]
now = int(time.time())
rec = {"job_id": jid, "to": "DollarBill", "from": frm, "status": st, "pid": pid,
       "started_at": now - 60, "deadline": now + int(off), "discord_thread_id": tid}
# ended_at: "auto" = theo lẽ thường (job đã xong thì có); "-" = KHÔNG có (job đang chạy thật);
# số = ép giá trị. Đây là trường phân biệt job ĐANG CHẠY với job ĐỖ XE (usage_limited…).
if ended == "auto":
    rec["ended_at"] = now - 30 if st not in ("running", "retrying") else None
elif ended != "-":
    rec["ended_at"] = int(ended)
if replied != "-":
    rec["replied_at"] = replied
rec = {k: v for k, v in rec.items() if v is not None}
json.dump(rec, open(os.path.join(jd, jid + ".json"), "w"))
PY
}
CLAIM() { python3 "$REAL/bin/mike_json.py" batch-claim-wake "$BD" "$1" "$2" "$JD" >/dev/null 2>&1; echo $?; }
mk_job jobA done "" 60; mk_job jobB done "" 60
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b4 jobA 2 >/dev/null
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b4 jobB 2 >/dev/null
R1="$(CLAIM b4 jobA)"; R2="$(CLAIM b4 jobB)"
assert "member #1 claim ⇒ exit 0 (được bắn)" "$R1" "0"
assert "member #2 claim ⇒ exit 1 (đã có người bắn)" "$R2" "1"

echo "== CA 5 (đơn vị): xong LỆCH NHAU — anh em còn CHẠY THẬT ⇒ im lặng; xong sau ⇒ bắn"
mk_job jobC done "" 60
mk_job jobD running "$$" 60 Mike 1 -   # pid=$$ (selfcheck) = còn sống thật, chưa có ended_at
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b5 jobC 2 >/dev/null
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b5 jobD 2 >/dev/null
assert "job xong TRƯỚC im lặng khi anh em còn chạy" "$(CLAIM b5 jobC)" "2"
assert "batch đang bay ⇒ reconciler phải bỏ qua (batch-in-flight exit 0)" \
  "$(python3 "$REAL/bin/mike_json.py" batch-in-flight "$BD" b5 "$JD" jobC >/dev/null 2>&1; echo $?)" "0"
mk_job jobD done "$$" 60
assert "job xong SAU bắn wake cho cả batch" "$(CLAIM b5 jobD)" "0"

echo "== CA 6 (đơn vị): FAIL-SAFE — 1 job TREO vĩnh viễn (pid chết, quá deadline) không được nuốt wake"
mk_job jobE done "" 60
mk_job jobF running 999999999 -400 Mike 1 -   # pid không tồn tại + quá deadline > BATCH_DEATH_GRACE_S
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b6 jobE 2 >/dev/null
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b6 jobF 2 >/dev/null
assert "anh em TREO không chặn ⇒ job terminal cuối VẪN bắn" "$(CLAIM b6 jobE)" "0"

echo "== CA 7 (đơn vị): job treo NHƯNG chưa quá deadline ⇒ còn nhường (chưa kết luận là chết)"
mk_job jobG done "" 60
mk_job jobH running 999999999 120 Mike 1 -    # pid chết ⇒ theo luật (c) là KHÔNG chặn nữa
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b7 jobG 2 >/dev/null
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b7 jobH 2 >/dev/null
assert "pid wrapper CHẾT (dù còn deadline) ⇒ không chặn: nó sẽ không bao giờ bắn nữa" "$(CLAIM b7 jobG)" "0"
IN_FLIGHT() { python3 "$REAL/bin/mike_json.py" batch-in-flight "$BD" "$1" "$JD" "${2:-}" >/dev/null 2>&1; echo $?; }
assert "đã có người claim ⇒ batch không còn 'đang bay'" "$(IN_FLIGHT b7 jobG)" "1"

echo "== CA 8 (đơn vị): expected=2 mà mới đăng ký 1 ⇒ chưa được bắn (anh em chưa kịp dispatch)"
mk_job jobI done "" 60
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b8 jobI 2 >/dev/null
assert "thiếu member chưa đăng ký ⇒ im lặng" "$(CLAIM b8 jobI)" "2"
python3 - "$BD/b8.json" <<'PY'
import json, sys, time
fp = sys.argv[1]; o = json.load(open(fp))
o["created_at"] = int(time.time()) - 3600      # quá BATCH_REG_GRACE_S
json.dump(o, open(fp, "w"))
PY
assert "quá hạn ân xá đăng ký ⇒ không kẹt vĩnh viễn, được bắn" "$(CLAIM b8 jobI)" "0"

echo "== CA 9 (đơn vị): batch record HỎNG / job không phải member ⇒ exit 3 = KHÔNG BIẾT"
mk_job jobJ done "" 60
printf 'x' > "$BD/b9.json"
assert "batch record hỏng ⇒ exit 3 (caller quay về wake đơn lẻ)" "$(CLAIM b9 jobJ)" "3"
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b9x jobJ 1 >/dev/null 2>&1
assert "job KHÔNG nằm trong batch ⇒ exit 3" "$(CLAIM b9x jobKhongCo)" "3"
assert "batch_id có ký tự lạ (traversal) ⇒ exit 3, không đụng file ngoài thư mục" \
  "$(CLAIM ../../etc/passwd jobJ)" "3"

echo "== CA 10 (đơn vị, arch-reviewer B1): member ĐỖ XE (usage_limited/maxturns_pending/"
echo "   provider_fallback — có ended_at, status chưa terminal) KHÔNG được chặn cả batch"
# Vì sao đây là BLOCKER chứ không phải góc khuất: 3 nhánh này `return 0` trong _bg_wrapper mà
# KHÔNG gọi wake, lượt resume là job KHÁC. Chặn tới deadline+300 = ~34' đo trên record thật
# 08-20 ⇒ kết quả account còn lại post SAU send_plan_report 19:30.
for ST in usage_limited maxturns_pending provider_fallback; do
  rm -f "$BD/b10_$ST.json"
  mk_job "jobPark_$ST" "$ST" "$$" 1700 Mike 1 "$(date +%s)"   # ended_at CÓ, pid còn sống
  mk_job "jobDone_$ST" done "" 1700
  python3 "$REAL/bin/mike_json.py" batch-register "$BD" "b10_$ST" "jobPark_$ST" 2 >/dev/null
  python3 "$REAL/bin/mike_json.py" batch-register "$BD" "b10_$ST" "jobDone_$ST" 2 >/dev/null
  assert "member $ST không chặn ⇒ anh em bắn ngay" "$(CLAIM "b10_$ST" "jobDone_$ST")" "0"
done

echo "== CA 11 (đơn vị, arch-reviewer N1): pid bị TÁI SỬ DỤNG (luôn 'còn sống') vẫn phải có TRẦN"
mk_job jobK done "" 1700
mk_job jobL running "$$" -400 Mike 1 -      # pid sống thật nhưng quá deadline + grace
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b11 jobK 2 >/dev/null
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b11 jobL 2 >/dev/null
assert "pid 'sống' + quá deadline+grace ⇒ hết chặn (không kẹt vĩnh viễn)" "$(CLAIM b11 jobK)" "0"

echo "== CA 12 (đơn vị, arch-reviewer B2): claim và batch-in-flight phải ĐỌC GIỐNG NHAU"
mk_job jobM done "" 1700
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b12 jobM 2 >/dev/null   # expected=2, mới có 1
assert "claim nói im lặng (còn job chưa đăng ký)" "$(CLAIM b12 jobM)" "2"
assert "batch-in-flight phải nói CÙNG điều đó (đang bay) — không thì reconciler cứu sớm" \
  "$(IN_FLIGHT b12 jobM)" "0"

echo "== CA 13 (đơn vị, arch-reviewer N3): member KHÁC THREAD là đợt RIÊNG, không gộp chéo topic"
mk_job jobT1 done "" 1700 Mike 111
mk_job jobT2 running "$$" 1700 Mike 222 -
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b13 jobT1 2 >/dev/null
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b13 jobT2 2 >/dev/null
python3 - "$BD/b13.json" <<'PY'
import json, sys, time
fp = sys.argv[1]; o = json.load(open(fp))
o["created_at"] = int(time.time()) - 3600   # bỏ yếu tố "chưa đăng ký xong" để cô lập yếu tố THREAD
json.dump(o, open(fp, "w"))
PY
assert "anh em ở THREAD KHÁC không chặn (đợt của topic này đã xong)" "$(CLAIM b13 jobT1)" "0"
assert "prompt gộp CHỈ liệt kê member cùng thread" \
  "$(python3 "$REAL/bin/mike_json.py" batch-claim-wake "$BD" b13 jobT2 "$JD" 2>/dev/null | grep -c jobT1)" "0"

echo "== CA 14 (đơn vị, arch-reviewer N5): member from != Mike không bao giờ bắn ⇒ không được chặn"
mk_job jobN done "" 1700
mk_job jobO running "$$" 1700 Taylor 1 -
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b14 jobN 2 >/dev/null
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b14 jobO 2 >/dev/null
assert "member from=Taylor (không push wake) không chặn" "$(CLAIM b14 jobN)" "0"

echo "== CA 15 (đơn vị, arch-reviewer N2): mọi member đã replied ⇒ không đánh thức thêm phiên nào"
mk_job jobP done "" 1700 Mike 1 auto "2026-08-20T12:00:00Z"
mk_job jobQ done "" 1700 Mike 1 auto "2026-08-20T12:01:00Z"
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b15 jobP 2 >/dev/null
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b15 jobQ 2 >/dev/null
assert "cả 2 đã được post (reconciler cứu trước) ⇒ im lặng" "$(CLAIM b15 jobQ)" "1"
mk_job jobQ done "" 1700 Mike 1 auto -      # còn 1 job chưa post
rm -f "$BD/b15.json"
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b15 jobP 2 >/dev/null
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b15 jobQ 2 >/dev/null
assert "…nhưng CÒN job chưa post thì VẪN bắn (không được nuốt wake của người xong sau)" \
  "$(CLAIM b15 jobQ)" "0"

echo "== CA 16 (đơn vị, arch-reviewer S1): LỖI LẠ phải ra 'KHÔNG BIẾT' (3), tuyệt đối không phải"
echo "   'đã có người claim' (1) — 1 nghĩa là IM LẶNG, tức nuốt mất wake vì một lỗi hạ tầng"
mk_job jobR done "" 1700
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b16 jobR 1 >/dev/null
chmod 500 "$BD"
RC_RO="$(CLAIM b16 jobR)"
chmod 700 "$BD"
assert "thư mục batches read-only ⇒ exit 3 (quay về wake đơn lẻ), KHÔNG phải 1" "$RC_RO" "3"
assert "…ghi lại được thì bắn bình thường" "$(CLAIM b16 jobR)" "0"

echo "== CA 17 (đơn vị, arch-reviewer S2): member PIN RỖNG được CHẶN nhưng KHÔNG được kéo vào"
echo "   prompt của topic khác (luật 'pin rỗng ⇒ im lặng phía Discord, không đoán topic')"
mk_job jobU done "" 1700 Mike 777
mk_job jobV running "$$" 1700 Mike "" -      # pin rỗng + đang chạy
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b17 jobU 2 >/dev/null
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b17 jobV 2 >/dev/null
assert "member pin rỗng đang chạy VẪN chặn (bảo thủ)" "$(CLAIM b17 jobU)" "2"
mk_job jobV done "" 1700 Mike "" auto
assert "…xong rồi thì anh em bắn được" "$(CLAIM b17 jobU)" "0"
rm -f "$BD/b17.json"; python3 "$REAL/bin/mike_json.py" batch-register "$BD" b17 jobU 2 >/dev/null
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b17 jobV 2 >/dev/null
assert "nhưng prompt của topic 777 KHÔNG liệt kê job pin rỗng" \
  "$(python3 "$REAL/bin/mike_json.py" batch-claim-wake "$BD" b17 jobU "$JD" 777 2>/dev/null | grep -c jobV)" "0"

echo "== CA 18 (arch-reviewer S3): --batch-id mà KHÔNG --bg ⇒ KHÔNG đăng ký (nó không bao giờ"
echo "   bắn được wake, đăng ký chỉ để chặn anh em tới deadline+300)"
_reset
BID18="selfcheck.batch18"
( cd "$MK" && env CLAUDE_STUB_RC=0 DISPATCH_CGROUP_DETACH=0 DISPATCH_CLAUDE_BIN="$SB/claude_stub.sh" \
    DISPATCH_FROM=Mike bash "$MK/bin/dispatch.sh" Wags "job đồng bộ trong batch" \
    --batch-id "$BID18" --batch-size 2 --thread architecture --timeout 30 ) >/dev/null 2>>"$SB/err"
assert "job đồng bộ KHÔNG tạo/đăng ký batch record" "$([ -f "$MK/bus/batches/$BID18.json" ] && echo 1 || echo 0)" "0"

echo "== CA 19 (arch-reviewer vòng 3, BLOCKER-1): mike_json.py KHÔNG CHẠY ĐƯỢC ⇒ batch_wake.sh"
echo "   phải bắn wake ĐƠN LẺ, tuyệt đối không im. Mã 1/2 cũng là mã thoát của chính python3"
echo "   khi nó chưa từng chạy tới cmd_batch_claim_wake — CA16 chỉ phủ lỗi BÊN TRONG hàm."
# Root RIÊNG: $MK/bin/mike_json.py là symlink tới file THẬT, ghi đè ở đó là hỏng repo.
BWR="$SB/bwroot"
mkdir -p "$BWR/bin" "$BWR/bus/jobs" "$BWR/bus/batches"
ln -s "$REAL/bin/batch_wake.sh" "$BWR/bin/batch_wake.sh"
cat > "$BWR/bin/wake_thread.sh" <<EOF
#!/usr/bin/env bash
echo "WAKE \$1" >> "$SB/bwroot.calls"
EOF
chmod +x "$BWR/bin/wake_thread.sh"
_bw_run() {  # _bw_run -> in "<rc> <số lượt wake>"
  : > "$SB/bwroot.calls"
  bash "$BWR/bin/batch_wake.sh" bw1 jobW 999 "prompt đơn lẻ" >/dev/null 2>&1
  echo "$? $(wc -l < "$SB/bwroot.calls" | tr -d ' ')"
}
printf 'def (\n' > "$BWR/bin/mike_json.py"                     # SyntaxError ⇒ python exit 1
assert "mike_json.py SyntaxError (exit 1) ⇒ rc=2 + ĐÚNG 1 wake đơn lẻ" "$(_bw_run)" "2 1"
rm -f "$BWR/bin/mike_json.py"                                   # file thiếu ⇒ python exit 2
assert "mike_json.py THIẾU (exit 2) ⇒ rc=2 + ĐÚNG 1 wake đơn lẻ" "$(_bw_run)" "2 1"
printf 'import sys\nsys.exit(2)\n' > "$BWR/bin/mike_json.py"    # subcommand đổi tên/rollback lệch pha
assert "subcommand đổi tên (main() sys.exit(2)) ⇒ rc=2 + ĐÚNG 1 wake đơn lẻ" "$(_bw_run)" "2 1"
# Chiều NGƯỢC LẠI — bản vá không được biến mọi thứ thành "cứ bắn": im lặng CÓ CHỦ Ý vẫn im.
rm -f "$BWR/bin/mike_json.py"; ln -s "$REAL/bin/mike_json.py" "$BWR/bin/mike_json.py"
cat > "$BWR/bus/jobs/jobW.json" <<EOF
{"job_id":"jobW","status":"done","from":"Mike","discord_thread_id":"999","deadline":$(( $(date +%s) + 600 )),"ended_at":$(date +%s),"replied_at":""}
EOF
python3 "$REAL/bin/mike_json.py" batch-register "$BWR/bus/batches" bw1 jobW 1 >/dev/null
python3 - "$BWR/bus/batches/bw1.json" <<'PY'
import json, sys
fp = sys.argv[1]; o = json.load(open(fp))
o["wake_claimed"] = {"999": "jobKhac"}     # đã có người claim thread này
json.dump(o, open(fp, "w"))
PY
assert "…nhưng mike_json LÀNH + đã có người claim ⇒ VẪN im lặng (rc=1, 0 wake)" "$(_bw_run)" "1 0"

echo "== CA 20 (arch-reviewer vòng 3, BLOCKER-2): mike_json.py hỏng KHÔNG được giết LƯỚI CUỐI."
echo "   wakeup_reconcile.py nạp nó ở top-level; chết ở import = không note_abort, không"
echo "   CRITICAL ABORT, không notify — im lặng tới cron_health_check 08:25 hôm sau."
RCR="$SB/rcroot"
mkdir -p "$RCR/bin" "$RCR/bus/jobs" "$RCR/bus/batches" "$RCR/logs" "$RCR/state/locks"
ln -s "$REAL/bin/wakeup_reconcile.py" "$RCR/bin/wakeup_reconcile.py"
printf 'def (\n' > "$RCR/bin/mike_json.py"
for n in wake_thread.sh notify_thread.sh; do
  printf '#!/usr/bin/env bash\nexit 0\n' > "$RCR/bin/$n"; chmod +x "$RCR/bin/$n"
done
env WAKEUP_RECONCILE_TASKS_DB="$RCR/none.db" WAKEUP_RECONCILE_SESSIONS_API="http://127.0.0.1:1/api" \
    WAKEUP_RECONCILE_LOG="$RCR/logs/r.log" WAKEUP_RECONCILE_STATE="$RCR/state/s.json" \
    WAKEUP_RECONCILE_LOCK="$RCR/state/locks/l" \
  python3 "$RCR/bin/wakeup_reconcile.py" >/dev/null 2>"$RCR/err" || true
assert "reconciler KHÔNG chết ở import (0 traceback exec_module/SyntaxError)" \
  "$(grep -cE 'exec_module|SyntaxError' "$RCR/err")" "0"
assert "…và chu kỳ CHẠY THẬT: log được ghi (không phải chết câm)" \
  "$([ -s "$RCR/logs/r.log" ] && echo 1 || echo 0)" "1"

echo "== CA 21 (arch-reviewer vòng 3, nit 5): ĐỒNG HỒ LÙI — created_at ở TƯƠNG LAI làm hiệu ÂM,"
echo "   vế '<= GRACE' đúng vĩnh viễn ⇒ chặn claim VÀ bịt miệng luôn reconciler suốt thời gian lệch"
# ended_at CŨ (quá BATCH_CLAIM_LAG_S) để cô lập đúng yếu tố ĐỒNG HỒ: nếu để ended_at=now thì
# mệnh đề TOCTOU (CA26) giữ batch "đang bay" 180s và ca này đo lẫn hai thứ. Khác biệt cốt lõi:
# cửa sổ TOCTOU tự hết sau 180s, còn `created_at` tương lai thì bịt miệng VÔ HẠN.
mk_job jobSkew done "" 1700 Mike 1 "$(( $(date +%s) - 400 ))"
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b21 jobSkew 2 >/dev/null   # expected=2, mới 1
python3 - "$BD/b21.json" <<'PY'
import json, sys, time
fp = sys.argv[1]; o = json.load(open(fp))
o["created_at"] = int(time.time()) + 7200      # NTP step / batch chép từ máy khác
json.dump(o, open(fp, "w"))
PY
assert "created_at tương lai ⇒ KHÔNG kẹt: vẫn được bắn" "$(CLAIM b21 jobSkew)" "0"
rm -f "$BD/b21.json"
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b21 jobSkew 2 >/dev/null
python3 - "$BD/b21.json" <<'PY'
import json, sys, time
fp = sys.argv[1]; o = json.load(open(fp))
o["created_at"] = int(time.time()) + 7200
json.dump(o, open(fp, "w"))
PY
assert "…và reconciler KHÔNG bị bịt miệng (in-flight = 1, tức KHÔNG đang bay)" \
  "$(IN_FLIGHT b21 jobSkew)" "1"

echo "== CA 22 (arch-reviewer vòng 3, nit 6 — N6 chưa có assertion nào): NHƯỜNG phải để lại"
echo "   dấu vết trong chính batch record, nếu không thì một wake biến mất là điều tra tay không"
mk_job jobY1 done "" 1700
mk_job jobY2 running "$$" 1700 Mike 1 -
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b22 jobY1 2 >/dev/null
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b22 jobY2 2 >/dev/null
assert "jobY1 nhường vì jobY2 còn chạy" "$(CLAIM b22 jobY1)" "2"
assert "…và ghi yielded[jobY1] kèm lý do (blockers) vào batch record" \
  "$(python3 -c "
import json
y = (json.load(open('$BD/b22.json')).get('yielded') or {}).get('jobY1') or {}
print(1 if y.get('at') and y.get('blockers') else 0)")" "1"

echo "== CA 23 (arch-reviewer vòng 3, nit 4): batch-register HỎNG ⇒ job KHÔNG được mang nhãn"
echo "   batch_id. Nhãn sai nói dối reconciler: batch_in_flight() trả True ⇒ lưới cuối bỏ qua"
echo "   job này, trong khi nó không phải member nên chẳng ai bắn thay."
_reset
BID23="selfcheck.batch23"
chmod 500 "$MK/bus/batches"
_dispatch_bg Wags "job có batch-register hỏng" --batch-id "$BID23" --batch-size 2
_wait_all_terminal
chmod 700 "$MK/bus/batches"
J23="$(ls "$MK/bus/jobs"/*.json 2>/dev/null | head -1)"
assert "job vẫn chạy tới terminal dù register hỏng" \
  "$(python3 -c "import json;print(json.load(open('$J23')).get('status'))")" "done"
assert "job record KHÔNG mang batch_id (không nói dối reconciler)" \
  "$(python3 -c "import json;print(json.load(open('$J23')).get('batch_id') or 'none')")" "none"
assert "…và vẫn bắn wake ĐƠN LẺ như trước khi có batch (không nuốt mất)" "$(_nwake)" "1"

echo "== CA 24 (arch-reviewer vòng 4, BLOCKER): marker phải NEO ĐẦU DÒNG. Traceback SyntaxError"
echo "   của Python in lại NGUYÊN VĂN dòng nguồn — mà dòng định nghĩa marker trong mike_json.py"
echo "   chính là chuỗi chứa marker ⇒ grep không neo sẽ coi một VỤ SẬP là 'im lặng hợp lệ'."
# Tái hiện đúng hình dạng traceback thật: dòng nguồn được echo, THỤT 4 DẤU CÁCH.
# rm TRƯỚC KHI ghi: CA19 để lại đây một SYMLINK tới bin/mike_json.py THẬT, `cat >` sẽ ghi
# XUYÊN symlink và huỷ file của repo (cùng lớp tai nạn mà _stub đã dựng chốt chặn ở đầu file).
_bw_mj() { rm -f "$BWR/bin/mike_json.py"; [ -L "$BWR/bin/mike_json.py" ] && { echo "FATAL: không gỡ được symlink mike_json trong sandbox — dừng để khỏi hỏng file thật"; exit 1; }; cat > "$BWR/bin/mike_json.py"; }
_bw_mj <<'PYEOF'
BATCH_SILENT_OK = "BATCH-SILENT-OK
PYEOF
assert "traceback echo dòng định nghĩa marker ⇒ VẪN phải wake đơn lẻ (không bị giả mạo)" \
  "$(_bw_run)" "2 1"
# Cùng chuỗi nhưng ở CỘT 0 trên stderr = marker thật ⇒ vẫn phải im. Neo không được chặt quá.
_bw_mj <<'PYEOF'
import sys
sys.stderr.write("BATCH-SILENT-OK: im lặng có chủ ý\n")
sys.exit(1)
PYEOF
assert "…nhưng marker THẬT ở cột 0 vẫn được tôn trọng (rc=1, 0 wake)" "$(_bw_run)" "1 0"
rm -f "$BWR/bin/mike_json.py"; ln -s "$REAL/bin/mike_json.py" "$BWR/bin/mike_json.py"

echo "== CA 25 (arch-reviewer vòng 4, nit 2): mktemp HỎNG ⇒ không kiểm được bằng chứng ⇒ rơi về"
echo "   wake đơn lẻ (N member = N push = bug gốc). Đúng chiều fail-safe nhưng PHẢI để lại dấu vết."
mkdir -p "$BWR/logs"; : > "$BWR/logs/wake_thread.log"
: > "$SB/bwroot.calls"
TMPDIR=/nonexistent-khong-ton-tai bash "$BWR/bin/batch_wake.sh" bw1 jobW 999 "prompt" >/dev/null 2>&1
assert "mktemp hỏng ⇒ vẫn bắn wake đơn lẻ (không nuốt)" \
  "$(wc -l < "$SB/bwroot.calls" | tr -d ' ')" "1"
assert "…và GHI LẠI vào logs/wake_thread.log (mất dedupe không được im lặng)" \
  "$(grep -c 'mktemp HỎNG' "$BWR/logs/wake_thread.log")" "1"

echo "== CA 26 (arch-reviewer vòng 4, nit 3): TOCTOU — member VỪA terminal mà CHƯA kịp claim."
echo "   status=done là hết chặn, nhưng _bg_wrapper còn consolidate+notify rồi mới gọi batch_wake"
echo "   ⇒ reconciler cứu job cũ ĐỒNG THỜI member cuối bắn wake gộp = 2 phiên Mike song song."
mk_job jobZ1 done "" 1700 Mike 1 "$(( $(date +%s) - 400 ))"   # xong lâu rồi
mk_job jobZ2 done "" 1700 Mike 1 "$(date +%s)"                # VỪA terminal, chưa claim
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b26 jobZ1 2 >/dev/null
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b26 jobZ2 2 >/dev/null
python3 - "$BD/b26.json" <<'PY'
import json, sys, time
fp = sys.argv[1]; o = json.load(open(fp))
o["created_at"] = int(time.time()) - 3600      # cô lập yếu tố TOCTOU khỏi ân hạn đăng ký
json.dump(o, open(fp, "w"))
PY
assert "reconciler phải TRÁNH ĐƯỜNG: batch còn 'đang bay' vì có member vừa terminal" \
  "$(IN_FLIGHT b26 jobZ1)" "0"
assert "…nhưng claim KHÔNG bị làm chậm (bất đối xứng CÓ CHỦ Ý: kiên nhẫn chỉ nghiêng về reconciler)" \
  "$(CLAIM b26 jobZ2)" "0"
# Hết cửa sổ trễ ⇒ reconciler làm việc lại bình thường (không kẹt vĩnh viễn).
rm -f "$BD/b26.json"
mk_job jobZ2 done "" 1700 Mike 1 "$(( $(date +%s) - 400 ))"
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b26 jobZ1 2 >/dev/null
python3 "$REAL/bin/mike_json.py" batch-register "$BD" b26 jobZ2 2 >/dev/null
python3 - "$BD/b26.json" <<'PY'
import json, sys, time
fp = sys.argv[1]; o = json.load(open(fp))
o["created_at"] = int(time.time()) - 3600
json.dump(o, open(fp, "w"))
PY
assert "…mọi member xong quá cửa sổ trễ ⇒ hết bay, reconciler được cứu (không kẹt)" \
  "$(IN_FLIGHT b26 jobZ1)" "1"

echo
if [ "$FAILS" -eq 0 ]; then
  echo "PASS — $CASES/$CASES assertion đúng (batch wake: 1 lượt/đợt, fail-safe khi treo/hỏng, không batch = hành vi cũ)"
  exit 0
else
  echo "FAIL — $FAILS/$CASES assertion sai"
  exit 1
fi
