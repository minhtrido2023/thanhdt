#!/usr/bin/env bash
# Selfcheck cho phân loại nguyên nhân draft-fail của daily_retro.sh (3 lớp, thêm 2026-08-20).
# Bất biến kiểm tra: (1) log lỗi truyền tải THẬT của sự cố 08-19 phải khớp lớp transport và
# KHÔNG khớp usage-limit; (2) log usage-limit thật phải khớp usage-limit và KHÔNG khớp
# transport (nếu lẫn ⇒ mất auto-resume hoặc chờ backoff vô ích); (3) draft lạc đề bình thường
# không khớp cả hai. Chạy: bash mike/bin/daily_retro_failcause_selfcheck.sh
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/bin/usage_limit_phrases.sh"
API_TRANSPORT_ERROR_RE="$(grep -m1 '^API_TRANSPORT_ERROR_RE=' "$ROOT/bin/daily_retro.sh" | cut -d"'" -f2)"
[ -n "$API_TRANSPORT_ERROR_RE" ] || { echo "FAIL: khong doc duoc API_TRANSPORT_ERROR_RE tu daily_retro.sh"; exit 1; }

pass=0; fail=0
check() { # <ten> <text> <expect_transport 0/1> <expect_usage 0/1>
  local name="$1" text="$2" et="$3" eu="$4" gt=0 gu=0
  printf '%s' "$text" | grep -qiE "$API_TRANSPORT_ERROR_RE" && gt=1
  printf '%s' "$text" | grep -qiE "$USAGE_LIMIT_PHRASE_RE" && gu=1
  if [ "$gt" = "$et" ] && [ "$gu" = "$eu" ]; then pass=$((pass+1)); echo "PASS $name"
  else fail=$((fail+1)); echo "FAIL $name (transport got=$gt want=$et, usage got=$gu want=$eu)"; fi
}

# 1. Nguyên văn log sự cố 2026-08-19 (mike/logs/daily_retro_draft_20260819_173001_a1.log)
check "transport-selfsigned-real" \
  "API Error: Unable to connect to API: Self-signed certificate detected. Check your proxy or corporate SSL certificates" 1 0
check "transport-econnreset" "Error: read ECONNRESET" 1 0
check "transport-dns"        "getaddrinfo EAI_AGAIN api.anthropic.com" 1 0
# 2. Usage-limit thật — phải KHÔNG lẫn sang transport
check "usage-weekly"  "You've hit your weekly limit · resets Jul 26, 5pm" 0 1
check "usage-5h"      "usage limit reached · resets at 6am" 0 1
check "usage-429"     '{"type":"error","error":{"type":"rate_limit_error"},"status": 429}' 0 1
# 3. Draft lạc đề / lỗi thật khác — không khớp lớp nào
check "offtopic-plain" "Da xong viec truoc do, khong co gi de bao cao." 0 0
check "task-error"     "Traceback (most recent call last): KeyError: 'ticker'" 0 0

echo "---"; echo "PASS=$pass FAIL=$fail"
[ "$fail" -eq 0 ]
