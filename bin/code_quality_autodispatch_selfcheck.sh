#!/usr/bin/env bash
# Selfcheck cho bin/code_quality_autodispatch.py (Tầng 3 auto-dispatch, code-quality-review-plan
# §CẬP NHẬT 2026-09-17, v2 sau arch-review round 1 NEEDS_CHANGES). Sandbox hoá: --root trỏ vào
# thư mục tạm có bin/{append_event,notify_thread}.sh giả (no-op, chỉ ghi log để assert) +
# --dispatch-bin giả — KHÔNG BAO GIỜ gọi dispatch.sh/append_event.sh/notify_thread.sh thật.
#
# Fake dispatch.sh in "JOB <id>" ra STDERR (khớp CONTRACT THẬT của bin/dispatch.sh:1154) — bản
# v1 in ra stdout, che mất bug job_id luôn None (arch-review round 1 killer objection).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT="$ROOT/bin/code_quality_autodispatch.py"

PASS=0; FAIL=0
ok() { PASS=$((PASS+1)); echo "PASS $1"; }
bad() { FAIL=$((FAIL+1)); echo "FAIL $1: $2"; }

SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT
mkdir -p "$SANDBOX/bin" "$SANDBOX/state"

# Fake dispatch.sh THÀNH CÔNG: JOB id ra STDERR (đúng contract thật), 1 dòng vô hại ra stdout.
cat > "$SANDBOX/bin/dispatch_ok.sh" <<'EOF'
#!/usr/bin/env bash
echo "$*" >> "$SANDBOX_DISPATCH_LOG"
echo "DISPATCHED $1 (pid=12345)"
echo "JOB fake_$(date +%s%N) (from=selfcheck)" >&2
exit 0
EOF
chmod +x "$SANDBOX/bin/dispatch_ok.sh"

# Fake dispatch.sh THẤT BẠI (vd circuit breaker exit 4): không có dòng JOB nào.
cat > "$SANDBOX/bin/dispatch_fail.sh" <<'EOF'
#!/usr/bin/env bash
echo "$*" >> "$SANDBOX_DISPATCH_LOG"
echo "CIRCUIT TRIPPED for $1" >&2
exit 4
EOF
chmod +x "$SANDBOX/bin/dispatch_fail.sh"

# Fake dispatch.sh CÓ ĐIỀU KIỆN theo tên agent (T-retry-partial): Wags fail, Taylor ok.
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

cat > "$SANDBOX/bin/append_event.sh" <<'EOF'
#!/usr/bin/env bash
echo "$*" >> "$SANDBOX_EVENT_LOG"
exit 0
EOF
chmod +x "$SANDBOX/bin/append_event.sh"

cat > "$SANDBOX/bin/notify_thread.sh" <<'EOF'
#!/usr/bin/env bash
echo "$*" >> "$SANDBOX_NOTIFY_LOG"
exit 0
EOF
chmod +x "$SANDBOX/bin/notify_thread.sh"

export SANDBOX_DISPATCH_LOG="$SANDBOX/dispatch.log"
export SANDBOX_EVENT_LOG="$SANDBOX/event.log"
export SANDBOX_NOTIFY_LOG="$SANDBOX/notify.log"

reset_logs() { : > "$SANDBOX_DISPATCH_LOG"; : > "$SANDBOX_EVENT_LOG"; : > "$SANDBOX_NOTIFY_LOG"; }

run() {
  local fixture="$1" date_="$2" dispatch_bin="${3:-$SANDBOX/bin/dispatch_ok.sh}"
  reset_logs
  python3 "$SCRIPT" --verified "$fixture" --date "$date_" --report-file "/tmp/r.md" \
    --root "$SANDBOX" --dispatch-bin "$dispatch_bin"
}
run_keep_state() {
  # Như run() nhưng KHÔNG xoá state trước — dùng cho test rerun/idempotency.
  local fixture="$1" date_="$2" dispatch_bin="${3:-$SANDBOX/bin/dispatch_ok.sh}"
  reset_logs
  python3 "$SCRIPT" --verified "$fixture" --date "$date_" --report-file "/tmp/r.md" \
    --root "$SANDBOX" --dispatch-bin "$dispatch_bin"
}

# --- T1: rỗng — không dispatch, không escalate ---
echo '{"findings": []}' > "$SANDBOX/t1.json"
rm -f "$SANDBOX/state/code_quality_weekly_dispatch_2099-01-01.json"
out="$(run "$SANDBOX/t1.json" 2099-01-01)"
if echo "$out" | grep -q '"n_escalate": 0' && [ ! -s "$SANDBOX_DISPATCH_LOG" ] && [ ! -s "$SANDBOX_EVENT_LOG" ]; then
  ok "T1 rỗng: không dispatch, không escalate"
else
  bad "T1" "out=$out"
fi

# --- T2: EXEC hard-boundary (brokers.py, MỌI severity kể cả low) -> escalate, KHÔNG dispatch ---
rm -f "$SANDBOX/state/code_quality_weekly_dispatch_2099-01-02.json"
cat > "$SANDBOX/t2.json" <<'EOF'
{"findings": [
  {"file": "/x/trading_bot/brokers.py", "line": 1474, "category": "correctness", "severity": "low", "summary": "s1", "evidence": "e1", "owner": "Taylor"}
]}
EOF
out="$(run "$SANDBOX/t2.json" 2099-01-02)"
if echo "$out" | grep -q '"n_escalate": 1' && [ ! -s "$SANDBOX_DISPATCH_LOG" ] && grep -q "hard-boundary" "$SANDBOX_EVENT_LOG" \
   && grep -q "triaged-needs-human" "$SANDBOX_EVENT_LOG"; then
  ok "T2 EXEC hard-boundary (kể cả severity=low) -> escalate + ack triaged-needs-human, không dispatch"
else
  bad "T2" "out=$out event_log=$(cat "$SANDBOX_EVENT_LOG")"
fi

# --- T3: NAV-scale file (compute_active_nav.py) severity=low -> KHÔNG escalate, dispatch bình thường ---
rm -f "$SANDBOX/state/code_quality_weekly_dispatch_2099-01-03.json"
cat > "$SANDBOX/t3.json" <<'EOF'
{"findings": [
  {"file": "/x/mike/bin/compute_active_nav.py", "line": 269, "category": "correctness", "severity": "low", "summary": "s2", "evidence": "e2", "owner": "Wags"}
]}
EOF
out="$(run "$SANDBOX/t3.json" 2099-01-03)"
job_id="$(echo "$out" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["results"]["Wags"]["job_id"])')"
if echo "$out" | grep -q '"n_escalate": 0' && echo "$out" | grep -q '"n_wags": 1' && [ -n "$job_id" ] && [ "$job_id" != "None" ]; then
  ok "T3 NAV-scale file severity=low -> dispatch bình thường, job_id parse ĐÚNG (từ stderr)"
else
  bad "T3" "out=$out job_id=$job_id"
fi

# --- T3b: NAV-scale file severity=medium -> escalate ---
rm -f "$SANDBOX/state/code_quality_weekly_dispatch_2099-01-03b.json"
cat > "$SANDBOX/t3b.json" <<'EOF'
{"findings": [
  {"file": "/x/trading_bot/strategies.py", "line": 391, "category": "duplicate-formula", "severity": "medium", "summary": "s2b", "evidence": "e2b", "owner": "Taylor"}
]}
EOF
out="$(run "$SANDBOX/t3b.json" 2099-01-03b)"
if echo "$out" | grep -q '"n_escalate": 1' && [ ! -s "$SANDBOX_DISPATCH_LOG" ]; then
  ok "T3b NAV-scale file severity=medium -> escalate"
else
  bad "T3b" "out=$out"
fi

# --- T4: owner rỗng/lạ -> escalate (fail-safe) ---
rm -f "$SANDBOX/state/code_quality_weekly_dispatch_2099-01-04.json"
cat > "$SANDBOX/t4.json" <<'EOF'
{"findings": [
  {"file": "/x/foo.py", "line": 1, "category": "dead-code", "severity": "low", "summary": "s3", "evidence": "e3", "owner": "someone-else"},
  {"file": "/x/bar.py", "line": 2, "category": "dead-code", "severity": "low", "summary": "s4", "evidence": "e4"}
]}
EOF
out="$(run "$SANDBOX/t4.json" 2099-01-04)"
if echo "$out" | grep -q '"n_escalate": 2' && [ ! -s "$SANDBOX_DISPATCH_LOG" ]; then
  ok "T4 owner lạ/thiếu -> escalate cả 2, không dispatch"
else
  bad "T4" "out=$out"
fi

# --- T5: mix Taylor + Wags -> 2 dispatch riêng, đúng owner, --write-scope có trong argv ---
rm -f "$SANDBOX/state/code_quality_weekly_dispatch_2099-01-05.json"
cat > "$SANDBOX/t5.json" <<'EOF'
{"findings": [
  {"file": "/x/trading_bot/foo.py", "line": 1, "category": "dead-code", "severity": "low", "summary": "s5", "evidence": "e5", "owner": "Taylor"},
  {"file": "/x/mike/bin/bar.sh", "line": 2, "category": "dead-code", "severity": "low", "summary": "s6", "evidence": "e6", "owner": "Wags"}
]}
EOF
out="$(run "$SANDBOX/t5.json" 2099-01-05)"
n_dispatch_calls="$(grep -cE '^(Taylor|Wags) Xử lý ' "$SANDBOX_DISPATCH_LOG" || true)"
if echo "$out" | grep -q '"n_taylor": 1' && echo "$out" | grep -q '"n_wags": 1' && [ "$n_dispatch_calls" -eq 2 ] \
   && grep -q "^Taylor " "$SANDBOX_DISPATCH_LOG" && grep -q "^Wags " "$SANDBOX_DISPATCH_LOG" \
   && grep -q -- "--write-scope /x/trading_bot/foo.py" "$SANDBOX_DISPATCH_LOG" \
   && grep -q -- "--write-scope /x/mike/bin/bar.sh" "$SANDBOX_DISPATCH_LOG"; then
  ok "T5 mix Taylor+Wags -> 2 dispatch call riêng biệt, --write-scope đúng file"
else
  bad "T5" "out=$out dispatch_log=$(cat "$SANDBOX_DISPATCH_LOG")"
fi

# --- T6: idempotency guard — MỌI nhóm đã có trong state -> skip sạch ---
rm -f "$SANDBOX/state/code_quality_weekly_dispatch_2099-01-06.json"
cat > "$SANDBOX/t6.json" <<'EOF'
{"findings": [{"file": "/x/foo.py", "line": 1, "category": "dead-code", "severity": "low", "summary": "s", "evidence": "e", "owner": "Taylor"}]}
EOF
python3 -c "
import json
json.dump({'taylor': {'job_id': 'fake_prev', 'n_findings': 1}}, open('$SANDBOX/state/code_quality_weekly_dispatch_2099-01-06.json', 'w'))
"
out="$(run_keep_state "$SANDBOX/t6.json" 2099-01-06)"
if echo "$out" | grep -q '"skipped": true' && [ ! -s "$SANDBOX_DISPATCH_LOG" ]; then
  ok "T6 idempotency: mọi nhóm đã có trong state -> skip sạch, không dispatch lại"
else
  bad "T6" "out=$out"
fi
rm -f "$SANDBOX/state/code_quality_weekly_dispatch_2099-01-06.json"

# --- T7: --dry-run KHÔNG gọi dispatch.sh/append_event.sh/notify_thread.sh thật ---
rm -f "$SANDBOX/state/code_quality_weekly_dispatch_2099-01-07.json"
reset_logs
out="$(python3 "$SCRIPT" --verified "$SANDBOX/t5.json" --date 2099-01-07 --report-file "/tmp/r.md" \
  --root "$SANDBOX" --dispatch-bin "$SANDBOX/bin/dispatch_ok.sh" --dry-run)"
if [ ! -s "$SANDBOX_DISPATCH_LOG" ] && [ ! -s "$SANDBOX_EVENT_LOG" ] && [ ! -s "$SANDBOX_NOTIFY_LOG" ] \
   && echo "$out" | grep -q '"dry_run": true'; then
  ok "T7 --dry-run không đụng dispatch/event/notify thật"
else
  bad "T7" "out=$out"
fi

# --- T8: cùng file vừa có escalate (medium) vừa có dispatch (low) -> prompt cảnh báo ---
rm -f "$SANDBOX/state/code_quality_weekly_dispatch_2099-01-08.json"
cat > "$SANDBOX/t8.json" <<'EOF'
{"findings": [
  {"file": "/x/trading_bot/brokers.py", "line": 518, "category": "correctness", "severity": "medium", "summary": "hard one", "evidence": "e1", "owner": "Taylor"}
]}
EOF
out="$(run "$SANDBOX/t8.json" 2099-01-08)"
if echo "$out" | grep -q '"n_escalate": 1'; then
  ok "T8 EXEC hard-boundary medium -> escalate (đường cũ vẫn đúng)"
else
  bad "T8" "out=$out"
fi

# --- T9: finding thiếu field 'file' -> escalate, KHÔNG crash ---
rm -f "$SANDBOX/state/code_quality_weekly_dispatch_2099-01-09.json"
cat > "$SANDBOX/t9.json" <<'EOF'
{"findings": [
  {"line": 1, "category": "dead-code", "severity": "low", "summary": "thiếu file", "evidence": "e", "owner": "Taylor"},
  {"file": "/x/ok.py", "line": 2, "category": "dead-code", "severity": "low", "summary": "hợp lệ", "evidence": "e", "owner": "Taylor"}
]}
EOF
if out="$(run "$SANDBOX/t9.json" 2099-01-09)"; then
  if echo "$out" | grep -q '"n_escalate": 1' && echo "$out" | grep -q '"n_taylor": 1'; then
    ok "T9 finding thiếu 'file' -> escalate riêng, không crash, finding hợp lệ khác vẫn dispatch"
  else
    bad "T9" "out=$out"
  fi
else
  bad "T9" "script CRASH (rc≠0) thay vì fail-safe escalate — out=$out"
fi

# --- T9b: severity không hợp lệ (typo "Med") -> escalate, không tự đoán ---
rm -f "$SANDBOX/state/code_quality_weekly_dispatch_2099-01-09b.json"
cat > "$SANDBOX/t9b.json" <<'EOF'
{"findings": [{"file": "/x/ok.py", "line": 1, "category": "dead-code", "severity": "Med", "summary": "s", "evidence": "e", "owner": "Taylor"}]}
EOF
out="$(run "$SANDBOX/t9b.json" 2099-01-09b)"
if echo "$out" | grep -q '"n_escalate": 1' && [ ! -s "$SANDBOX_DISPATCH_LOG" ]; then
  ok "T9b severity không hợp lệ -> escalate (fail-safe), không tự đoán medium/low"
else
  bad "T9b" "out=$out"
fi

# --- T10: dispatch rc≠0 (circuit breaker) -> KHÔNG ghi state cho nhóm đó (rerun sẽ thử lại) ---
rm -f "$SANDBOX/state/code_quality_weekly_dispatch_2099-01-10.json"
cat > "$SANDBOX/t10.json" <<'EOF'
{"findings": [{"file": "/x/foo.py", "line": 1, "category": "dead-code", "severity": "low", "summary": "s", "evidence": "e", "owner": "Taylor"}]}
EOF
out="$(run "$SANDBOX/t10.json" 2099-01-10 "$SANDBOX/bin/dispatch_fail.sh")"
state_content="$(cat "$SANDBOX/state/code_quality_weekly_dispatch_2099-01-10.json" 2>/dev/null || echo '{}')"
if echo "$out" | grep -q '"n_taylor": 1' && ! echo "$state_content" | grep -q '"taylor"'; then
  ok "T10 dispatch rc≠0 -> KHÔNG ghi state cho nhóm đó (retryable)"
else
  bad "T10" "out=$out state=$state_content"
fi

# --- T11: rerun sau khi 1 nhóm fail — chỉ retry nhóm CHƯA thành công, không dispatch lại nhóm đã xong ---
rm -f "$SANDBOX/state/code_quality_weekly_dispatch_2099-01-11.json"
cat > "$SANDBOX/t11.json" <<'EOF'
{"findings": [
  {"file": "/x/foo.py", "line": 1, "category": "dead-code", "severity": "low", "summary": "s", "evidence": "e", "owner": "Taylor"},
  {"file": "/x/bar.sh", "line": 2, "category": "dead-code", "severity": "low", "summary": "s2", "evidence": "e2", "owner": "Wags"}
]}
EOF
# Lượt 1: Wags fail, Taylor ok.
out1="$(run "$SANDBOX/t11.json" 2099-01-11 "$SANDBOX/bin/dispatch_wags_fails.sh")"
state1="$(cat "$SANDBOX/state/code_quality_weekly_dispatch_2099-01-11.json" 2>/dev/null || echo '{}')"
# Lượt 2 (rerun cùng ngày, KHÔNG xoá state) — đổi sang dispatch_ok để Wags giờ thành công.
out2="$(run_keep_state "$SANDBOX/t11.json" 2099-01-11 "$SANDBOX/bin/dispatch_ok.sh")"
n_taylor_calls_total="$(grep -cE '^Taylor Xử lý ' "$SANDBOX_DISPATCH_LOG" || true)"  # log bị reset đầu lượt 2, chỉ đếm lượt 2
if echo "$state1" | grep -q '"taylor"' && ! echo "$state1" | grep -q '"wags"' \
   && echo "$out2" | grep -q '"skipped_already_done": true' \
   && [ "$n_taylor_calls_total" -eq 0 ] && grep -qE '^Wags Xử lý ' "$SANDBOX_DISPATCH_LOG"; then
  ok "T11 rerun chỉ retry nhóm chưa xong (Wags), KHÔNG dispatch lại Taylor đã thành công"
else
  bad "T11" "state1=$state1 out2=$out2 dispatch_log_lan2=$(cat "$SANDBOX_DISPATCH_LOG")"
fi
rm -f "$SANDBOX/state/code_quality_weekly_dispatch_2099-01-11.json"

echo "=== $PASS PASS / $FAIL FAIL ==="
[ "$FAIL" -eq 0 ]
