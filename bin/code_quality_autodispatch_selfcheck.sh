#!/usr/bin/env bash
# Selfcheck cho bin/code_quality_autodispatch.py (Tầng 3 auto-dispatch, code-quality-review-plan
# §CẬP NHẬT 2026-09-17, v3 sau arch-review round 2 NEEDS_CHANGES). Sandbox hoá: --root/--wc-root
# trỏ vào thư mục tạm có bin/{append_event,notify_thread}.sh giả (no-op, ghi log để assert) +
# --dispatch-bin giả — KHÔNG BAO GIỜ gọi script thật (sẽ ghi bus/Discord thật).
#
# Fixture dùng path "/x/..." và --wc-root "/x" — relpath("/x/trading_bot/brokers.py", "/x") =
# "trading_bot/brokers.py", đúng dạng repo-relative mà gate hot-core VÀ --write-scope đều cần
# (arch-review round 2: bản trước dùng path tuyệt đối làm vô hiệu job-write-scope-conflict +
# commit-collision-gate).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT="$ROOT/bin/code_quality_autodispatch.py"
WC_ROOT_FAKE="/x"

PASS=0; FAIL=0
ok() { PASS=$((PASS+1)); echo "PASS $1"; }
bad() { FAIL=$((FAIL+1)); echo "FAIL $1: $2"; }

SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT
mkdir -p "$SANDBOX/bin" "$SANDBOX/state"

cat > "$SANDBOX/bin/dispatch_ok.sh" <<'EOF'
#!/usr/bin/env bash
echo "$*" >> "$SANDBOX_DISPATCH_LOG"
echo "DISPATCHED $1 (pid=12345)"
echo "JOB fake_$(date +%s%N) (from=selfcheck)" >&2
exit 0
EOF
chmod +x "$SANDBOX/bin/dispatch_ok.sh"

cat > "$SANDBOX/bin/dispatch_fail.sh" <<'EOF'
#!/usr/bin/env bash
echo "$*" >> "$SANDBOX_DISPATCH_LOG"
echo "CIRCUIT TRIPPED for $1" >&2
exit 4
EOF
chmod +x "$SANDBOX/bin/dispatch_fail.sh"

cat > "$SANDBOX/bin/dispatch_wags_fails.sh" <<'EOF'
#!/usr/bin/env bash
echo "$*" >> "$SANDBOX_DISPATCH_LOG"
if [ "$1" = "Wags" ]; then
  echo "CIRCUIT TRIPPED for Wags" >&2
  exit 4
fi
echo "JOB fake_$1_$(date +%s%N) (from=selfcheck)" >&2
exit 0
EOF
chmod +x "$SANDBOX/bin/dispatch_wags_fails.sh"

cat > "$SANDBOX/bin/append_event_ok.sh" <<'EOF'
#!/usr/bin/env bash
echo "$*" >> "$SANDBOX_EVENT_LOG"
exit 0
EOF
chmod +x "$SANDBOX/bin/append_event_ok.sh"

cat > "$SANDBOX/bin/append_event_fail.sh" <<'EOF'
#!/usr/bin/env bash
echo "$*" >> "$SANDBOX_EVENT_LOG"
exit 1
EOF
chmod +x "$SANDBOX/bin/append_event_fail.sh"

cat > "$SANDBOX/bin/notify_thread.sh" <<'EOF'
#!/usr/bin/env bash
echo "$*" >> "$SANDBOX_NOTIFY_LOG"
exit 0
EOF
chmod +x "$SANDBOX/bin/notify_thread.sh"

export SANDBOX_DISPATCH_LOG="$SANDBOX/dispatch.log"
export SANDBOX_EVENT_LOG="$SANDBOX/event.log"
export SANDBOX_NOTIFY_LOG="$SANDBOX/notify.log"

use_append_event() { cp "$SANDBOX/bin/append_event_$1.sh" "$SANDBOX/bin/append_event.sh"; chmod +x "$SANDBOX/bin/append_event.sh"; }
use_append_event ok  # mặc định OK, T-fail tự đổi rồi đổi lại

reset_logs() { : > "$SANDBOX_DISPATCH_LOG"; : > "$SANDBOX_EVENT_LOG"; : > "$SANDBOX_NOTIFY_LOG"; }

# run()/run_keep_state() ghi kết quả vào 2 biến TOÀN CỤC (OUT/LAST_RC) thay vì echo qua command
# substitution — gọi qua $(run ...) sẽ chạy hàm trong SUBSHELL, khiến LAST_RC=$? bên trong không
# bao giờ thoát ra được biến cha (bài học tự bắt lúc viết selfcheck này: `set -u` báo "unbound").
run() {
  local fixture="$1" date_="$2" dispatch_bin="${3:-$SANDBOX/bin/dispatch_ok.sh}"
  reset_logs
  rm -f "$SANDBOX/state/code_quality_weekly_dispatch_${date_}.json"
  set +e
  OUT="$(python3 "$SCRIPT" --verified "$fixture" --date "$date_" --report-file "/tmp/r.md" \
    --root "$SANDBOX" --wc-root "$WC_ROOT_FAKE" --dispatch-bin "$dispatch_bin" 2>&1)"
  LAST_RC=$?
  set -e
}
run_keep_state() {
  local fixture="$1" date_="$2" dispatch_bin="${3:-$SANDBOX/bin/dispatch_ok.sh}"
  reset_logs
  set +e
  OUT="$(python3 "$SCRIPT" --verified "$fixture" --date "$date_" --report-file "/tmp/r.md" \
    --root "$SANDBOX" --wc-root "$WC_ROOT_FAKE" --dispatch-bin "$dispatch_bin" 2>&1)"
  LAST_RC=$?
  set -e
}

# --- T1: rỗng ---
echo '{"findings": []}' > "$SANDBOX/t1.json"
run "$SANDBOX/t1.json" 2099-01-01
[ "$LAST_RC" -eq 0 ] && echo "$OUT" | grep -q '"n_escalate": 0' && [ ! -s "$SANDBOX_DISPATCH_LOG" ] \
  && ok "T1 rỗng: không dispatch, không escalate, rc=0" || bad "T1" "rc=$LAST_RC out=$OUT"

# --- T2: mọi file dưới trading_bot/ (PREFIX, không phải tên cụ thể) -> escalate MỌI severity ---
cat > "$SANDBOX/t2.json" <<'EOF'
{"findings": [
  {"file": "/x/trading_bot/some_new_module_never_listed.py", "line": 1, "category": "correctness", "severity": "low", "summary": "s1", "evidence": "e1", "owner": "Taylor"}
]}
EOF
run "$SANDBOX/t2.json" 2099-01-02
if [ "$LAST_RC" -eq 0 ] && echo "$OUT" | grep -q '"n_escalate": 1' && [ ! -s "$SANDBOX_DISPATCH_LOG" ] \
   && grep -q "hard-boundary" "$SANDBOX_EVENT_LOG" && grep -q "triaged-needs-human" "$SANDBOX_EVENT_LOG"; then
  ok "T2 prefix trading_bot/ bắt được module CHƯA TỪNG liệt tên -> escalate + ack, severity=low vẫn escalate"
else
  bad "T2" "rc=$LAST_RC out=$OUT event=$(cat "$SANDBOX_EVENT_LOG")"
fi

# --- T3: file exact-match ngoài trading_bot/ (dnse_api.py, run_bot.sh) -> escalate MỌI severity ---
cat > "$SANDBOX/t3.json" <<'EOF'
{"findings": [
  {"file": "/x/dnse_api.py", "line": 1, "category": "correctness", "severity": "low", "summary": "s2", "evidence": "e2", "owner": "Taylor"},
  {"file": "/x/mike/bin/run_bot.sh", "line": 2, "category": "correctness", "severity": "low", "summary": "s3", "evidence": "e3", "owner": "Wags"}
]}
EOF
run "$SANDBOX/t3.json" 2099-01-03
if [ "$LAST_RC" -eq 0 ] && echo "$OUT" | grep -q '"n_escalate": 2' && [ ! -s "$SANDBOX_DISPATCH_LOG" ]; then
  ok "T3 exact-match dnse_api.py + mike/bin/run_bot.sh -> escalate dù severity=low"
else
  bad "T3" "rc=$LAST_RC out=$OUT"
fi

# --- T4: file NGOÀI mọi boundary (kể cả owner Wags, mike/bin nhưng không phải file nhạy cảm) -> dispatch bình thường ---
cat > "$SANDBOX/t4.json" <<'EOF'
{"findings": [{"file": "/x/mike/bin/some_random_tool.py", "line": 1, "category": "dead-code", "severity": "high", "summary": "s4", "evidence": "e4", "owner": "Wags"}]}
EOF
run "$SANDBOX/t4.json" 2099-01-04
job_id="$(echo "$OUT" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["results"]["Wags"]["job_id"])' 2>/dev/null || echo "PARSE_FAIL")"
if [ "$LAST_RC" -eq 0 ] && echo "$OUT" | grep -q '"n_escalate": 0' && [ -n "$job_id" ] && [ "$job_id" != "None" ] && [ "$job_id" != "PARSE_FAIL" ]; then
  ok "T4 file KHÔNG nhạy cảm (kể cả severity=high) -> dispatch bình thường, job_id parse ĐÚNG từ stderr"
else
  bad "T4" "rc=$LAST_RC out=$OUT job_id=$job_id"
fi

# --- T5: owner rỗng/lạ -> escalate (fail-safe) ---
cat > "$SANDBOX/t5.json" <<'EOF'
{"findings": [
  {"file": "/x/foo.py", "line": 1, "category": "dead-code", "severity": "low", "summary": "s5", "evidence": "e5", "owner": "someone-else"},
  {"file": "/x/bar.py", "line": 2, "category": "dead-code", "severity": "low", "summary": "s6", "evidence": "e6"}
]}
EOF
run "$SANDBOX/t5.json" 2099-01-05
[ "$LAST_RC" -eq 0 ] && echo "$OUT" | grep -q '"n_escalate": 2' && [ ! -s "$SANDBOX_DISPATCH_LOG" ] \
  && ok "T5 owner lạ/thiếu -> escalate cả 2" || bad "T5" "rc=$LAST_RC out=$OUT"

# --- T6: mix Taylor(hit_details.py, root R&D) + Wags(mike/bin/bar.sh) -> 2 dispatch, --write-scope RELATIVE ---
cat > "$SANDBOX/t6.json" <<'EOF'
{"findings": [
  {"file": "/x/hit_details.py", "line": 1, "category": "dead-code", "severity": "low", "summary": "s7", "evidence": "e7", "owner": "Taylor"},
  {"file": "/x/mike/bin/bar.sh", "line": 2, "category": "dead-code", "severity": "low", "summary": "s8", "evidence": "e8", "owner": "Wags"}
]}
EOF
run "$SANDBOX/t6.json" 2099-01-06
n_dispatch_calls="$(grep -cE '^(Taylor|Wags) Xử lý ' "$SANDBOX_DISPATCH_LOG" || true)"
# File dưới mike/ khai CẢ 2 dạng (mike/bin/bar.sh VÀ bin/bar.sh, write_scope_variants() — arch-review
# round 3): assert cả 2 dạng có mặt trong --write-scope của Wags, dạng ngoài mike/ (hit_details.py)
# chỉ có 1 dạng.
if [ "$LAST_RC" -eq 0 ] && echo "$OUT" | grep -q '"n_taylor": 1' && echo "$OUT" | grep -q '"n_wags": 1' && [ "$n_dispatch_calls" -eq 2 ] \
   && grep -qF -- "--write-scope hit_details.py" "$SANDBOX_DISPATCH_LOG" \
   && grep -qE -- "--write-scope [^ ]*mike/bin/bar\.sh" "$SANDBOX_DISPATCH_LOG" \
   && grep -qE -- "--write-scope [^ ]*bin/bar\.sh,mike/bin/bar\.sh" "$SANDBOX_DISPATCH_LOG" \
   && ! grep -qF -- "--write-scope /x/" "$SANDBOX_DISPATCH_LOG"; then
  ok "T6 mix Taylor+Wags -> --write-scope REPO-RELATIVE (không còn /x/...), file dưới mike/ khai CẢ 2 dạng"
else
  bad "T6" "out=$OUT dispatch_log=$(cat "$SANDBOX_DISPATCH_LOG")"
fi

# --- T7: idempotency — mọi nhóm đã có trong state -> skip sạch ---
cat > "$SANDBOX/t7.json" <<'EOF'
{"findings": [{"file": "/x/foo.py", "line": 1, "category": "dead-code", "severity": "low", "summary": "s", "evidence": "e", "owner": "Taylor"}]}
EOF
python3 -c "import json; json.dump({'taylor': {'job_id': 'fake_prev', 'n_findings': 1}}, open('$SANDBOX/state/code_quality_weekly_dispatch_2099-01-07.json','w'))"
run_keep_state "$SANDBOX/t7.json" 2099-01-07
[ "$LAST_RC" -eq 0 ] && echo "$OUT" | grep -q '"skipped": true' && [ ! -s "$SANDBOX_DISPATCH_LOG" ] \
  && ok "T7 idempotency: mọi nhóm đã có trong state -> skip sạch" || bad "T7" "rc=$LAST_RC out=$OUT"
rm -f "$SANDBOX/state/code_quality_weekly_dispatch_2099-01-07.json"

# --- T8: --dry-run không đụng gì thật ---
reset_logs
rm -f "$SANDBOX/state/code_quality_weekly_dispatch_2099-01-08.json"
set +e
OUT="$(python3 "$SCRIPT" --verified "$SANDBOX/t6.json" --date 2099-01-08 --report-file "/tmp/r.md" \
  --root "$SANDBOX" --wc-root "$WC_ROOT_FAKE" --dispatch-bin "$SANDBOX/bin/dispatch_ok.sh" --dry-run)"
LAST_RC=$?
set -e
if [ ! -s "$SANDBOX_DISPATCH_LOG" ] && [ ! -s "$SANDBOX_EVENT_LOG" ] && [ ! -s "$SANDBOX_NOTIFY_LOG" ] \
   && echo "$OUT" | grep -q '"dry_run": true' && echo "$OUT" | grep -q -- '--bg'; then
  ok "T8 --dry-run không đụng dispatch/event/notify thật, cmd_preview còn --bg (bug preview cũ đã vá)"
else
  bad "T8" "rc=$LAST_RC out=$OUT"
fi

# --- T9: finding thiếu 'file' -> escalate, KHÔNG crash ---
cat > "$SANDBOX/t9.json" <<'EOF'
{"findings": [
  {"line": 1, "category": "dead-code", "severity": "low", "summary": "thiếu file", "evidence": "e", "owner": "Taylor"},
  {"file": "/x/ok.py", "line": 2, "category": "dead-code", "severity": "low", "summary": "hợp lệ", "evidence": "e", "owner": "Taylor"}
]}
EOF
run "$SANDBOX/t9.json" 2099-01-09
if [ "$LAST_RC" -eq 0 ] && echo "$OUT" | grep -q '"n_escalate": 1' && echo "$OUT" | grep -q '"n_taylor": 1'; then
  ok "T9 finding thiếu 'file' -> escalate riêng, không crash"
else
  bad "T9" "rc=$LAST_RC out=$OUT"
fi

# --- T9b: severity không hợp lệ / có khoảng trắng thừa -> escalate hoặc chuẩn hoá đúng, không tự đoán ---
cat > "$SANDBOX/t9b.json" <<'EOF'
{"findings": [{"file": "/x/ok.py", "line": 1, "category": "dead-code", "severity": "Med", "summary": "s", "evidence": "e", "owner": "Taylor"}]}
EOF
run "$SANDBOX/t9b.json" 2099-01-09b
[ "$LAST_RC" -eq 0 ] && echo "$OUT" | grep -q '"n_escalate": 1' && [ ! -s "$SANDBOX_DISPATCH_LOG" ] \
  && ok "T9b severity không hợp lệ ('Med') -> escalate fail-safe" || bad "T9b" "rc=$LAST_RC out=$OUT"

# --- T9c: severity NAV-hard-boundary trước đây với khoảng trắng thừa " medium " trên file exact-match -> vẫn escalate đúng (bug chuẩn hoá vòng 2 đã vá) ---
cat > "$SANDBOX/t9c.json" <<'EOF'
{"findings": [{"file": "/x/dnse_api.py", "line": 1, "category": "correctness", "severity": " medium ", "summary": "s", "evidence": "e", "owner": "Taylor"}]}
EOF
run "$SANDBOX/t9c.json" 2099-01-09c
[ "$LAST_RC" -eq 0 ] && echo "$OUT" | grep -q '"n_escalate": 1' && [ ! -s "$SANDBOX_DISPATCH_LOG" ] \
  && ok "T9c severity ' medium ' (khoảng trắng thừa) chuẩn hoá đúng -> vẫn escalate" || bad "T9c" "rc=$LAST_RC out=$OUT"

# --- T10: dispatch rc≠0 -> KHÔNG ghi state, script trả rc≠0 (không còn báo 'Auto-dispatch xong' giả) ---
cat > "$SANDBOX/t10.json" <<'EOF'
{"findings": [{"file": "/x/foo.py", "line": 1, "category": "dead-code", "severity": "low", "summary": "s", "evidence": "e", "owner": "Taylor"}]}
EOF
run "$SANDBOX/t10.json" 2099-01-10 "$SANDBOX/bin/dispatch_fail.sh"
state_content="$(cat "$SANDBOX/state/code_quality_weekly_dispatch_2099-01-10.json" 2>/dev/null || echo '{}')"
if [ "$LAST_RC" -ne 0 ] && echo "$OUT" | grep -q '"n_taylor": 1' && ! echo "$state_content" | grep -q '"taylor"' \
   && grep -q "CẦN RERUN TAY" "$SANDBOX_NOTIFY_LOG"; then
  ok "T10 dispatch rc≠0 -> KHÔNG ghi state, script rc≠0, Discord có lệnh rerun tay (không hứa suông)"
else
  bad "T10" "rc=$LAST_RC out=$OUT state=$state_content"
fi

# --- T11: rerun sau khi 1 nhóm fail — chỉ retry nhóm CHƯA thành công ---
cat > "$SANDBOX/t11.json" <<'EOF'
{"findings": [
  {"file": "/x/foo.py", "line": 1, "category": "dead-code", "severity": "low", "summary": "s", "evidence": "e", "owner": "Taylor"},
  {"file": "/x/bar.sh", "line": 2, "category": "dead-code", "severity": "low", "summary": "s2", "evidence": "e2", "owner": "Wags"}
]}
EOF
run "$SANDBOX/t11.json" 2099-01-11 "$SANDBOX/bin/dispatch_wags_fails.sh"
state1="$(cat "$SANDBOX/state/code_quality_weekly_dispatch_2099-01-11.json" 2>/dev/null || echo '{}')"
run_keep_state "$SANDBOX/t11.json" 2099-01-11 "$SANDBOX/bin/dispatch_ok.sh"
if [ "$LAST_RC" -eq 0 ] && echo "$state1" | grep -q '"taylor"' && ! echo "$state1" | grep -q '"wags"' \
   && echo "$OUT" | grep -q '"skipped_already_done": true' \
   && ! grep -qE '^Taylor Xử lý ' "$SANDBOX_DISPATCH_LOG" && grep -qE '^Wags Xử lý ' "$SANDBOX_DISPATCH_LOG"; then
  ok "T11 rerun chỉ retry nhóm chưa xong (Wags), không dispatch lại Taylor, lần 2 rc=0"
else
  bad "T11" "state1=$state1 out2=$OUT rc=$LAST_RC dispatch_log_lan2=$(cat "$SANDBOX_DISPATCH_LOG")"
fi
rm -f "$SANDBOX/state/code_quality_weekly_dispatch_2099-01-11.json"

# --- T12: escalation FAIL (append_event.sh lỗi) -> notify_failure() được gọi, script trả rc≠0, KHÔNG ghi state["escalate"] ---
use_append_event fail
cat > "$SANDBOX/t12.json" <<'EOF'
{"findings": [{"file": "/x/dnse_api.py", "line": 1, "category": "correctness", "severity": "high", "summary": "s", "evidence": "e", "owner": "Taylor"}]}
EOF
run "$SANDBOX/t12.json" 2099-01-12
state_content="$(cat "$SANDBOX/state/code_quality_weekly_dispatch_2099-01-12.json" 2>/dev/null || echo '{}')"
use_append_event ok
if [ "$LAST_RC" -ne 0 ] && grep -q "CRASH\|THẤT BẠI" "$SANDBOX_NOTIFY_LOG" && ! echo "$state_content" | grep -q '"escalate"'; then
  ok "T12 escalation post FAIL -> notify_failure() gọi, rc≠0, KHÔNG ghi state (không im lặng như round 1)"
else
  bad "T12" "rc=$LAST_RC state=$state_content notify_log=$(cat "$SANDBOX_NOTIFY_LOG")"
fi

# --- T13: file KHÔNG nằm trong danh sách tay nhưng có tier=T0 trong kb/production_manifest.json
# giả -> escalate (arch-review round 3 killer objection: danh sách tay bỏ sót merge_park_orders.py
# vì nó không "nghe tên" nguy hiểm — nguồn manifest cơ học phải bắt được ca này) ---
mkdir -p "$SANDBOX/kb"
python3 -c "
import json
json.dump({'files': {'mike/bin/merge_park_orders_fake.py': {'tier': 'T0'}, 'some_harmless.py': {'tier': 'T1'}}},
          open('$SANDBOX/kb/production_manifest.json', 'w'))
"
cat > "$SANDBOX/t13.json" <<'EOF'
{"findings": [{"file": "/x/mike/bin/merge_park_orders_fake.py", "line": 1, "category": "correctness", "severity": "low", "summary": "s13", "evidence": "e13", "owner": "Wags"}]}
EOF
run "$SANDBOX/t13.json" 2099-01-13
if [ "$LAST_RC" -eq 0 ] && echo "$OUT" | grep -q '"n_escalate": 1' && [ ! -s "$SANDBOX_DISPATCH_LOG" ] \
   && grep -q "hard_boundary_manifest_t0" "$SANDBOX_EVENT_LOG"; then
  ok "T13 file KHÔNG trong danh sách tay nhưng tier=T0 trong production_manifest.json -> escalate (manifest union)"
else
  bad "T13" "out=$OUT event=$(cat "$SANDBOX_EVENT_LOG")"
fi
rm -f "$SANDBOX/kb/production_manifest.json"

# --- T14: cùng file vừa có finding escalate (owner lạ) vừa có finding dispatch (owner Taylor) ->
# prompt Taylor PHẢI chứa cảnh báo "CÙNG FILE ... ESCALATE" nêu đúng tên file (arch-review round 3:
# bản trước so _rel với path thô nên cảnh báo này là code chết, không bao giờ bắn) ---
cat > "$SANDBOX/t14.json" <<'EOF'
{"findings": [
  {"file": "/x/shared_file.py", "line": 1, "category": "dead-code", "severity": "low", "summary": "owner la", "evidence": "e", "owner": "unknown-owner"},
  {"file": "/x/shared_file.py", "line": 2, "category": "correctness", "severity": "low", "summary": "owner ro", "evidence": "e", "owner": "Taylor"}
]}
EOF
run "$SANDBOX/t14.json" 2099-01-14
if [ "$LAST_RC" -eq 0 ] && echo "$OUT" | grep -q '"n_escalate": 1' && echo "$OUT" | grep -q '"n_taylor": 1' \
   && grep -q "CÙNG FILE có finding khác đang ESCALATE" "$SANDBOX_DISPATCH_LOG" \
   && grep -qF "shared_file.py" "$SANDBOX_DISPATCH_LOG"; then
  ok "T14 cùng file escalate+dispatch -> cảnh báo THẬT SỰ xuất hiện trong prompt (regression round 3 đã vá)"
else
  bad "T14" "out=$OUT dispatch_log=$(cat "$SANDBOX_DISPATCH_LOG")"
fi

# --- T15: kb/production_manifest.json THIẾU (không tồn tại) -> cảnh báo THẤY ĐƯỢC trong summary
# JSON lẫn Discord, KHÔNG im lặng trả set rỗng (arch-review round 4 killer objection: bản trước
# nuốt exception, "gate đang bảo vệ" và "gate đã tắt" không phân biệt được từ output) ---
rm -f "$SANDBOX/kb/production_manifest.json"
cat > "$SANDBOX/t15.json" <<'EOF'
{"findings": [{"file": "/x/mike/bin/harmless_tool.py", "line": 1, "category": "dead-code", "severity": "low", "summary": "s15", "evidence": "e15", "owner": "Wags"}]}
EOF
run "$SANDBOX/t15.json" 2099-01-15
if [ "$LAST_RC" -eq 0 ] && echo "$OUT" | grep -q '"n_manifest_t0": 0' && echo "$OUT" | grep -qF '"manifest_warning": "không đọc được' \
   && grep -q "Không đọc được kb/production_manifest.json" "$SANDBOX_NOTIFY_LOG"; then
  ok "T15 manifest thiếu -> warning THẤY ĐƯỢC trong summary JSON + Discord (không im lặng như round 4 killer)"
else
  bad "T15" "out=$OUT notify_log=$(cat "$SANDBOX_NOTIFY_LOG")"
fi

echo "=== $PASS PASS / $FAIL FAIL ==="
[ "$FAIL" -eq 0 ]
