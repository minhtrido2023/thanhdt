#!/usr/bin/env bash
# Selfcheck: _preempt_wakeup behaviour — no live ccdb, no live Claude
# Scenarios:
#   1. No CCDB_API_URL → no-op (no curl call)
#   2. CCDB_API_URL set but no task row → no PATCH
#   3. CCDB_API_URL set, row found → PATCH next_run_at=now
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0; FAIL=0

ok()  { echo "  PASS: $*"; PASS=$((PASS+1)); }
err() { echo "  FAIL: $*"; FAIL=$((FAIL+1)); }

# ── load the function ──────────────────────────────────────────────────────────
# dispatch.sh defines _preempt_wakeup inside `if [ "$bg" = "--bg" ]`.
# Source it by faking that condition so only the relevant block loads.
TMP_INIT=$(mktemp); trap 'rm -f "$TMP_INIT"' EXIT
# Extract the _preempt_wakeup block and source standalone
awk '/^  _preempt_wakeup\(\)/,/^  \}$/' "$ROOT/bin/dispatch.sh" \
  | sed 's/^  //' > "$TMP_INIT"   # strip 2-space indent used inside the if block
# shellcheck source=/dev/null
source "$TMP_INIT"

# ── mock curl ─────────────────────────────────────────────────────────────────
CURL_LOG=$(mktemp); CURL_CALLS=0
curl() {
  CURL_CALLS=$((CURL_CALLS+1))
  printf '%s\n' "$@" >> "$CURL_LOG"
  # Respond based on URL pattern
  local url=""
  for a in "$@"; do [[ "$a" == http* ]] && url="$a"; done
  if [[ "$url" == */api/tasks ]]; then
    printf '%s' "$_MOCK_TASKS_JSON"
  fi
  return 0
}
export -f curl

reset_curl() { CURL_CALLS=0; > "$CURL_LOG"; }

# ── Scenario 1: no CCDB_API_URL ───────────────────────────────────────────────
reset_curl
unset CCDB_API_URL 2>/dev/null || true
_preempt_wakeup "1234567890"
if [ "$CURL_CALLS" -eq 0 ]; then
  ok "Scenario 1: no CCDB_API_URL → 0 curl calls"
else
  err "Scenario 1: expected 0 curl calls, got $CURL_CALLS"
fi

# ── Scenario 2: no matching task row ──────────────────────────────────────────
reset_curl
export CCDB_API_URL="http://127.0.0.1:19999"  # not reachable, but curl is mocked
_MOCK_TASKS_JSON='{"tasks": [{"id": 99, "name": "wakeup-thread-9999999", "next_run_at": 1000}]}'
_preempt_wakeup "1234567890"
if grep -q "PATCH" "$CURL_LOG" 2>/dev/null; then
  err "Scenario 2: no matching row → should not PATCH, but did"
else
  ok "Scenario 2: no matching row → no PATCH"
fi

# ── Scenario 3: matching row found → PATCH ────────────────────────────────────
reset_curl
THREAD_ID="1234567890"
_MOCK_TASKS_JSON="{\"tasks\": [{\"id\": 42, \"name\": \"wakeup-thread-$THREAD_ID\", \"next_run_at\": 1000}]}"
_preempt_wakeup "$THREAD_ID"
if grep -q "PATCH" "$CURL_LOG" 2>/dev/null && grep -q "/api/tasks/42" "$CURL_LOG" 2>/dev/null; then
  ok "Scenario 3: matching row → PATCH /api/tasks/42"
else
  err "Scenario 3: expected PATCH /api/tasks/42, got: $(cat "$CURL_LOG")"
fi
# Verify next_run_at is approximately now
if grep -q "next_run_at" "$CURL_LOG" 2>/dev/null; then
  ok "Scenario 3: next_run_at present in PATCH body"
else
  err "Scenario 3: next_run_at missing from PATCH body"
fi

# ── Result ────────────────────────────────────────────────────────────────────
rm -f "$CURL_LOG"
echo ""
echo "preempt_wakeup_selfcheck: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
