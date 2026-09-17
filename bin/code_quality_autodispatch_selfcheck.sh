#!/usr/bin/env bash
# Selfcheck cho bin/code_quality_autodispatch.py (Tầng 3 auto-dispatch, code-quality-review-plan
# §CẬP NHẬT 2026-09-17). Sandbox hoá: --root trỏ vào thư mục tạm có bin/{append_event,notify_thread}.sh
# giả (no-op, chỉ ghi log để assert) + --dispatch-bin giả (echo "JOB fake_<n> ..." rồi exit 0) —
# KHÔNG BAO GIỜ gọi dispatch.sh/append_event.sh/notify_thread.sh thật (sẽ ghi bus/Discord thật).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT="$ROOT/bin/code_quality_autodispatch.py"

PASS=0; FAIL=0
ok() { PASS=$((PASS+1)); echo "PASS $1"; }
bad() { FAIL=$((FAIL+1)); echo "FAIL $1: $2"; }

SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT
mkdir -p "$SANDBOX/bin" "$SANDBOX/state"

cat > "$SANDBOX/bin/dispatch.sh" <<'EOF'
#!/usr/bin/env bash
# fake dispatch.sh: ghi lại argv để selfcheck assert, in JOB id giả, KHÔNG chạy gì thật
echo "$*" >> "$SANDBOX_DISPATCH_LOG"
echo "JOB fake_$(date +%s%N) (from=selfcheck)"
exit 0
EOF
chmod +x "$SANDBOX/bin/dispatch.sh"

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
: > "$SANDBOX_DISPATCH_LOG"; : > "$SANDBOX_EVENT_LOG"; : > "$SANDBOX_NOTIFY_LOG"

run() {
  local fixture="$1" date_="$2"
  : > "$SANDBOX_DISPATCH_LOG"; : > "$SANDBOX_EVENT_LOG"; : > "$SANDBOX_NOTIFY_LOG"
  rm -f "$SANDBOX/state/code_quality_weekly_dispatch_${date_}.json"
  python3 "$SCRIPT" --verified "$fixture" --date "$date_" --report-file "/tmp/r.md" \
    --root "$SANDBOX" --dispatch-bin "$SANDBOX/bin/dispatch.sh"
}

# --- T1: rỗng — không dispatch, không escalate ---
echo '{"findings": []}' > "$SANDBOX/t1.json"
out="$(run "$SANDBOX/t1.json" 2099-01-01)"
if echo "$out" | grep -q '"n_escalate": 0' && [ ! -s "$SANDBOX_DISPATCH_LOG" ] && [ ! -s "$SANDBOX_EVENT_LOG" ]; then
  ok "T1 rỗng: không dispatch, không escalate"
else
  bad "T1" "out=$out dispatch_log=$(cat "$SANDBOX_DISPATCH_LOG")"
fi

# --- T2: hard-boundary (brokers.py, medium) -> escalate, KHÔNG dispatch cho finding đó ---
cat > "$SANDBOX/t2.json" <<'EOF'
{"findings": [
  {"file": "/x/trading_bot/brokers.py", "line": 518, "category": "correctness", "severity": "medium", "summary": "s1", "evidence": "e1", "owner": "Taylor"}
]}
EOF
out="$(run "$SANDBOX/t2.json" 2099-01-02)"
if echo "$out" | grep -q '"n_escalate": 1' && [ ! -s "$SANDBOX_DISPATCH_LOG" ] && grep -q "hard-boundary" "$SANDBOX_EVENT_LOG"; then
  ok "T2 hard-boundary medium -> escalate, không dispatch"
else
  bad "T2" "out=$out event_log=$(cat "$SANDBOX_EVENT_LOG") dispatch_log=$(cat "$SANDBOX_DISPATCH_LOG")"
fi

# --- T3: CÙNG file brokers.py nhưng severity=low -> KHÔNG escalate, ĐƯỢC dispatch cho Taylor ---
cat > "$SANDBOX/t3.json" <<'EOF'
{"findings": [
  {"file": "/x/trading_bot/brokers.py", "line": 1474, "category": "correctness", "severity": "low", "summary": "s2", "evidence": "e2", "owner": "Taylor"}
]}
EOF
out="$(run "$SANDBOX/t3.json" 2099-01-03)"
if echo "$out" | grep -q '"n_escalate": 0' && echo "$out" | grep -q '"n_taylor": 1' && grep -q "Taylor" "$SANDBOX_DISPATCH_LOG"; then
  ok "T3 hard-core file nhưng severity=low -> dispatch bình thường (không escalate)"
else
  bad "T3" "out=$out dispatch_log=$(cat "$SANDBOX_DISPATCH_LOG")"
fi

# --- T4: owner rỗng/lạ -> escalate (fail-safe) ---
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

# --- T5: mix Taylor + Wags -> 2 dispatch riêng, đúng owner ---
cat > "$SANDBOX/t5.json" <<'EOF'
{"findings": [
  {"file": "/x/trading_bot/foo.py", "line": 1, "category": "dead-code", "severity": "low", "summary": "s5", "evidence": "e5", "owner": "Taylor"},
  {"file": "/x/mike/bin/bar.sh", "line": 2, "category": "dead-code", "severity": "low", "summary": "s6", "evidence": "e6", "owner": "Wags"}
]}
EOF
out="$(run "$SANDBOX/t5.json" 2099-01-05)"
# Mỗi lời gọi dispatch.sh giả ghi "$*" (prompt nhiều dòng) trên 1 lần echo — đếm SỐ LỜI GỌI bằng
# số dòng KHỚP "<agent> Xử lý " (dòng đầu của mỗi prompt), không phải tổng số dòng trong log.
n_dispatch_calls="$(grep -cE '^(Taylor|Wags) Xử lý ' "$SANDBOX_DISPATCH_LOG" || true)"
if echo "$out" | grep -q '"n_taylor": 1' && echo "$out" | grep -q '"n_wags": 1' && [ "$n_dispatch_calls" -eq 2 ] \
   && grep -q "^Taylor " "$SANDBOX_DISPATCH_LOG" && grep -q "^Wags " "$SANDBOX_DISPATCH_LOG"; then
  ok "T5 mix Taylor+Wags -> 2 dispatch call riêng biệt đúng owner"
else
  bad "T5" "out=$out dispatch_log=$(cat "$SANDBOX_DISPATCH_LOG")"
fi

# --- T6: idempotency guard — state file đã tồn tại -> skip, KHÔNG dispatch lại ---
: > "$SANDBOX_DISPATCH_LOG"; : > "$SANDBOX_EVENT_LOG"
echo '{"date":"2099-01-06","n_escalate":0}' > "$SANDBOX/state/code_quality_weekly_dispatch_2099-01-06.json"
out="$(python3 "$SCRIPT" --verified "$SANDBOX/t5.json" --date 2099-01-06 --report-file "/tmp/r.md" \
  --root "$SANDBOX" --dispatch-bin "$SANDBOX/bin/dispatch.sh")"
if echo "$out" | grep -q '"skipped": true' && [ ! -s "$SANDBOX_DISPATCH_LOG" ]; then
  ok "T6 idempotency guard: state file có sẵn -> skip, không dispatch lại"
else
  bad "T6" "out=$out dispatch_log=$(cat "$SANDBOX_DISPATCH_LOG")"
fi
rm -f "$SANDBOX/state/code_quality_weekly_dispatch_2099-01-06.json"

# --- T7: --dry-run KHÔNG gọi dispatch.sh/append_event.sh/notify_thread.sh thật (chỉ in dự kiến) ---
: > "$SANDBOX_DISPATCH_LOG"; : > "$SANDBOX_EVENT_LOG"; : > "$SANDBOX_NOTIFY_LOG"
out="$(python3 "$SCRIPT" --verified "$SANDBOX/t5.json" --date 2099-01-07 --report-file "/tmp/r.md" \
  --root "$SANDBOX" --dispatch-bin "$SANDBOX/bin/dispatch.sh" --dry-run)"
if [ ! -s "$SANDBOX_DISPATCH_LOG" ] && [ ! -s "$SANDBOX_EVENT_LOG" ] && [ ! -s "$SANDBOX_NOTIFY_LOG" ] \
   && echo "$out" | grep -q '"dry_run": true'; then
  ok "T7 --dry-run không đụng dispatch/event/notify thật"
else
  bad "T7" "out=$out dispatch_log=$(cat "$SANDBOX_DISPATCH_LOG")"
fi

# --- T8: finding cùng file brokers.py vừa có escalate (medium) vừa có dispatch (low) -> prompt
# Taylor phải chứa cảnh báo "ĐỪNG động vào vùng" của finding escalate ---
cat > "$SANDBOX/t8.json" <<'EOF'
{"findings": [
  {"file": "/x/trading_bot/brokers.py", "line": 518, "category": "correctness", "severity": "medium", "summary": "hard one", "evidence": "e1", "owner": "Taylor"},
  {"file": "/x/trading_bot/brokers.py", "line": 1474, "category": "correctness", "severity": "low", "summary": "safe one", "evidence": "e2", "owner": "Taylor"}
]}
EOF
out="$(run "$SANDBOX/t8.json" 2099-01-08)"
if grep -q "ĐỪNG động vào vùng" "$SANDBOX_DISPATCH_LOG"; then
  ok "T8 cùng file có escalate+dispatch -> prompt cảnh báo tránh xung đột"
else
  bad "T8" "dispatch_log=$(cat "$SANDBOX_DISPATCH_LOG")"
fi

echo "=== $PASS PASS / $FAIL FAIL ==="
[ "$FAIL" -eq 0 ]
