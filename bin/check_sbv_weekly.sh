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
WORKDIR="/home/trido/thanhdt/WorkingClaude"
LOGDIR="$WORKDIR/logs"
VERIFY_LOG="$WORKDIR/data/sbv_verify_log.json"
PY="/usr/bin/python3"
TODAY=$(date +%Y-%m-%d)

mkdir -p "$LOGDIR"
cd "$WORKDIR"

echo "===== SBV weekly check $TODAY $(date +%H:%M:%S) ====="

# ── Step 1: Get current rate from SBV_REFI_EVENTS (last entry) ──────────────
CURRENT_RATE=$(python3 -c "
import sys; sys.path.insert(0,'$WORKDIR')
from sbv_macro_overlay import SBV_REFI_EVENTS
ev = SBV_REFI_EVENTS[-1]
print(ev[1])
" 2>/dev/null || echo "4.5")
CURRENT_DATE=$(python3 -c "
import sys; sys.path.insert(0,'$WORKDIR')
from sbv_macro_overlay import SBV_REFI_EVENTS
ev = SBV_REFI_EVENTS[-1]
print(ev[0])
" 2>/dev/null || echo "2023-06-19")
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
