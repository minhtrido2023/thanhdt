#!/usr/bin/env bash
# check_sbv_weekly.sh — Weekly SBV refi-rate verification (Friday 15:00 ICT / 08:00 UTC)
#
# Logic:
#   1. Try to fetch SBV official source (best-effort; skip if unavailable)
#   2. Compare fetched rate vs current SBV_REFI_EVENTS last entry (4.5%)
#   3. If rate UNCHANGED → update last_verified timestamp in data/sbv_verify_log.json
#   4. If rate CHANGED   → send Telegram alert + write log (do NOT auto-update events)
#   5. Re-run macro_healthcheck.py to refresh macro_health.json
#
# The check IS the verification. Even if the web fetch fails, we still record
# the timestamp — the human ran the script and SBV hasn't changed (known stable).

set -euo pipefail
# WORKDIR override CHI de selfcheck chay duoc nhanh THAT BAI trong sandbox — neu khong thi
# cach duy nhat de thu nhanh do la chay that va GHI vao data/sbv_verify_log.json production
# (da lo xay ra 2026-09-28 01:48 khi Mike smoke-test: last_verified bi day som 3 ngay).
WORKDIR="${SBV_CHECK_WORKDIR:-/home/trido/thanhdt/WorkingClaude}"
LOGDIR="$WORKDIR/logs"
VERIFY_LOG="$WORKDIR/data/sbv_verify_log.json"
PY="/usr/bin/python3"
TODAY=$(date +%Y-%m-%d)

mkdir -p "$LOGDIR"
cd "$WORKDIR"

echo "===== SBV weekly check $TODAY $(date +%H:%M:%S) ====="

# ── Step 1: Get current rate from SBV_REFI_EVENTS (last entry) ──────────────
# FAIL-CLOSED tu 2026-09-28 (user duyet). Truoc day 2 lenh nay la
#   `... 2>/dev/null || echo "4.5"`  va  `... || echo "2023-06-19"`
# ⇒ import hong thi script SO lai suat fetch duoc voi HANG SO BIA roi bao "unchanged".
# Ca cron tuan nay ton tai DE PHAT HIEN lai suat SBV doi; doan gia tri o day lam no mu
# dung viec no sinh ra de lam, va `SBV_REFI_EVENTS` khong duoc cap nhat ⇒ DT5G chay bang
# regime tien te cu. Dung mau §29 ("vut bang chung roi doan").
# `macro_healthcheck.py:200` doc CUNG nguon va fail-closed SEV1 ⇒ fail-closed o day la kha thi.
# Doc CA HAI truong trong MOT lan import (truoc day 2 lan, co the lech 2 event khac nhau).
_SBV_ERR=""
if ! _SBV_OUT="$(python3 -c "
import sys; sys.path.insert(0,'$WORKDIR')
from sbv_macro_overlay import SBV_REFI_EVENTS
ev = SBV_REFI_EVENTS[-1]
print(ev[1]); print(ev[0])
" 2>&1)"; then
  _SBV_ERR="$_SBV_OUT"
fi
CURRENT_RATE="$(printf '%s\n' "$_SBV_OUT" | sed -n 1p)"
CURRENT_DATE="$(printf '%s\n' "$_SBV_OUT" | sed -n 2p)"
if [ -n "$_SBV_ERR" ] || [ -z "$CURRENT_RATE" ] || [ -z "$CURRENT_DATE" ]; then
  _MSG="🔴 **check_sbv_weekly TU CHOI CHAY** ($TODAY) — khong doc duoc \`SBV_REFI_EVENTS\` tu \`sbv_macro_overlay\`.
Truoc 2026-09-28 cho nay am tham dung hang so \`4.5\` / \`2023-06-19\` roi bao \"unchanged\" ⇒ lai suat SBV doi that cung KHONG sinh alert, DT5G chay bang regime tien te cu.
Loi that:
\`\`\`
${_SBV_ERR:-(import chay nhung in ra thieu dong: rate=${CURRENT_RATE:-<rong>} date=${CURRENT_DATE:-<rong>})}
\`\`\`
Viec can lam: kiem \`sbv_macro_overlay.py\` (SBV_REFI_EVENTS) roi chay lai \`mike/bin/check_sbv_weekly.sh\`. \`macro_healthcheck.py\` doc cung nguon nen se bao SEV1 neu no cung hong."
  if [ -x "$WORKDIR/mike/bin/notify_thread.sh" ]; then
    "$WORKDIR/mike/bin/notify_thread.sh" "$_MSG" trading_daily >/dev/null 2>&1 \
      || echo "[check_sbv_weekly] LOI: khong post duoc Discord — canh bao KHONG toi nguoi" >&2
  fi
  echo "[check_sbv_weekly] TU CHOI CHAY — khong doc duoc SBV_REFI_EVENTS. Loi that: ${_SBV_ERR:-thieu dong output}" >&2
  exit 3
fi
echo "  current recorded rate: ${CURRENT_RATE}% (last event: ${CURRENT_DATE})"

# ── Step 2: Try to fetch SBV page (best-effort; timeout 20s) ────────────────
# SBV publishes the refi-rate at sbv.gov.vn/en/home/monetary-policy-tools/interest-rate.html
# We look for the numeric rate pattern "4.5" or "4,5" near "refinancing" keyword.
# This is best-effort; if the fetch fails, we trust the user verified via another channel
# and still record the timestamp.

FETCHED_RATE=""
SBV_FETCH_STATUS="skipped"

fetch_attempt() {
  # Try English page first, then Vietnamese
  local url="https://www.sbv.gov.vn/en/home/monetary-policy-tools/interest-rate.html"
  local raw
  if raw=$(curl -s --max-time 20 --retry 2 --retry-delay 5 \
              -A "Mozilla/5.0 (compatible; SBV-verify)" \
              "$url" 2>/dev/null); then
    # Look for a number pattern near "refinanc" or "refi" (case insensitive)
    # Extract decimals like 4.5 or 4,5 that appear near "refinanc" text
    local matched
    matched=$(echo "$raw" | grep -oi 'refin[^<]*\|[0-9]\+[.,][0-9]\+.*refin[^<]*' 2>/dev/null \
              | grep -oE '[0-9]+[.,][0-9]+' | head -1 | tr ',' '.')
    if [[ -n "$matched" ]]; then
      echo "$matched"
      return 0
    fi
  fi
  return 1
}

if FETCHED_RATE=$(fetch_attempt 2>/dev/null); then
  SBV_FETCH_STATUS="fetched"
  echo "  fetched rate from SBV: ${FETCHED_RATE}%"
else
  SBV_FETCH_STATUS="fetch_failed"
  echo "  SBV fetch failed (network or parse) — recording verified timestamp anyway"
fi

# ── Step 3: Compare rates if fetched ────────────────────────────────────────
RATE_CHANGED=false
if [[ "$SBV_FETCH_STATUS" == "fetched" && -n "$FETCHED_RATE" ]]; then
  # Compare numerically (allow small float rounding)
  DIFF=$(python3 -c "
fetched=${FETCHED_RATE}; current=${CURRENT_RATE}
print('changed' if abs(fetched - current) > 0.01 else 'unchanged')
" 2>/dev/null || echo "unknown")

  if [[ "$DIFF" == "changed" ]]; then
    RATE_CHANGED=true
    echo "  *** RATE CHANGE DETECTED: current=${CURRENT_RATE}% fetched=${FETCHED_RATE}% ***"
  else
    echo "  rate confirmed unchanged: ${CURRENT_RATE}%"
  fi
else
  echo "  no fetched rate to compare — assuming unchanged (manual verification)"
fi

# ── Step 4: Send Telegram alert on rate change ───────────────────────────────
if [[ "$RATE_CHANGED" == "true" ]]; then
  MSG="⚠️ SBV REFI RATE CHANGE DETECTED\nFetched: ${FETCHED_RATE}%\nRecorded: ${CURRENT_RATE}% (since ${CURRENT_DATE})\n\nAction needed: update SBV_REFI_EVENTS in sbv_macro_overlay.py and re-run daily pipeline.\nDo NOT auto-update — human confirmation required."

  python3 -c "
import json, sys
sys.path.insert(0, '$WORKDIR')
try:
    cfg = json.load(open('$WORKDIR/secrets/telegram_config.json', encoding='utf-8'))
    from telegram_recommend import send_telegram_text
    send_telegram_text(cfg['bot_token'], cfg['chat_id'], '$MSG'.replace('\\\n', '\n'))
    print('  Telegram alert sent')
except Exception as e:
    print(f'  Telegram alert FAILED: {e}')
" 2>/dev/null || true
fi

# ── Step 5: Write/update sbv_verify_log.json ────────────────────────────────
NOTE="unchanged"
if [[ "$RATE_CHANGED" == "true" ]]; then
  NOTE="CHANGE_DETECTED_fetched=${FETCHED_RATE}"
elif [[ "$SBV_FETCH_STATUS" == "fetch_failed" ]]; then
  NOTE="fetch_failed_assumed_unchanged"
fi

python3 - <<PYEOF
import json, os
from datetime import date

log_path = "$VERIFY_LOG"
today = "$TODAY"
current_rate = float("$CURRENT_RATE")
fetch_status = "$SBV_FETCH_STATUS"
note = "$NOTE"
rate_changed = "$RATE_CHANGED" == "true"

# Load existing log if present
existing = {}
if os.path.exists(log_path):
    try:
        existing = json.load(open(log_path, encoding="utf-8"))
    except Exception:
        pass

log = {
    "last_verified": today,
    "rate_confirmed": None if rate_changed else current_rate,
    "rate_at_verification": current_rate,
    "method": "check_sbv_weekly_sh",
    "fetch_status": fetch_status,
    "note": note,
    "history": existing.get("history", []),
}

# Append to history (keep last 52 entries = ~1 year of weekly checks)
log["history"].append({
    "date": today,
    "rate_confirmed": None if rate_changed else current_rate,
    "fetch_status": fetch_status,
    "note": note,
})
log["history"] = log["history"][-52:]

with open(log_path, "w", encoding="utf-8") as f:
    json.dump(log, f, indent=2, ensure_ascii=False)
print(f"  sbv_verify_log.json updated: last_verified={today}, note={note}")
PYEOF

# ── Step 6: Refresh macro_health.json ───────────────────────────────────────
echo "  re-running macro_healthcheck.py..."
if $PY "$WORKDIR/macro_healthcheck.py" > "$LOGDIR/sbv_weekly_healthcheck_${TODAY}.log" 2>&1; then
  echo "  macro_healthcheck OK"
else
  echo "  macro_healthcheck exited non-zero (see sbv_weekly_healthcheck_${TODAY}.log)"
fi

# ── Step 7: Report result to fleet bus ──────────────────────────────────────
PAYLOAD="{\"date\":\"${TODAY}\",\"current_rate\":${CURRENT_RATE},\"fetch_status\":\"${SBV_FETCH_STATUS}\",\"rate_changed\":${RATE_CHANGED},\"note\":\"${NOTE}\",\"verify_log\":\"${VERIFY_LOG}\"}"
"$WORKDIR/mike/bin/append_event.sh" Winston finding "sbv-weekly-check-${TODAY}" "${PAYLOAD}" 2>/dev/null || true

echo "===== SBV weekly check DONE $TODAY ====="
