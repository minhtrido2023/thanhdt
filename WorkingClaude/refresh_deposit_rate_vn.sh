#!/usr/bin/env bash
# refresh_deposit_rate_vn.sh — MONTHLY reminder to confirm the Big-4 12M deposit rate.
#
# Layer A of proposal_deposit_rate_monthly_refresh_20260713.md (§3, user-approved 2026-07-17):
#   - best-effort fetch (CafeF/VCB, short timeout, NO retry — known low success) as a HINT ONLY,
#   - NEVER auto-writes the live series,
#   - posts a Discord/fleet reminder so a human confirms the number and runs append_deposit_rate.py.
#
# deposit_rate_vn.current_deposit_rate() is a LIVE production input (rating_8l.py NEUTRAL tilt),
# so the actual value is only ever written by a human via append_deposit_rate.py.
#
# Schedule: day 3 of month, 08:10 ICT (before the DCF refresh-gate consumes it around day 11).
set -uo pipefail
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
PY="$DNA_PYEXE"; cd "$WORKDIR_8L"

MONTH="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m)"
TODAY="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)"
LOG="data/refresh_deposit_rate_vn_$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m).log"
echo "===== deposit-rate refresh reminder START $(date -u +%Y-%m-%dT%H:%M:%SZ) (ICT ${TODAY}) =====" >> "$LOG"

# current live value (frozen anchors + any CSV appends)
CUR="$($PY -c 'from deposit_rate_vn import current_deposit_rate; print(f"{current_deposit_rate():.2f}")' 2>>"$LOG")" || CUR="?"
echo "current_deposit_rate() = ${CUR}%" >> "$LOG"

# best-effort fetch (short timeout, no retry, failure EXPECTED — CafeF table is JS-rendered).
# Prints a plausible '12 thang' rate to stdout if it can scrape one; empty otherwise. Never fatal.
HINT="$($PY - <<'PYEOF' 2>>"$LOG"
import re, sys
try:
    import urllib.request
    req = urllib.request.Request(
        "https://cafef.vn/du-lieu/lai-suat-ngan-hang.chn",
        headers={"User-Agent": "Mozilla/5.0 (deposit-rate-refresh best-effort)"})
    html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "ignore")
    # loose: a number 3-10 near '12 thang'/'12 month'. Static HTML usually lacks it -> no output.
    m = re.search(r"12\s*th[aá]ng.{0,80}?(\d(?:[.,]\d)?)\s*%", html, re.I | re.S)
    if m:
        print(m.group(1).replace(",", "."))
except Exception as e:
    print(f"fetch failed: {e}", file=sys.stderr)
PYEOF
)"
HINT="$(printf '%s' "$HINT" | tr -d '[:space:]')"
echo "fetch hint = '${HINT:-<none>}'" >> "$LOG"

# --- compose reminder ---
MSG="📌 Đầu tháng ${MONTH} — xác nhận lãi suất tiết kiệm 12 tháng Big-4 (VCB/BIDV/CTG/Agribank).
Giá trị đang dùng (live, input rating_8l NEUTRAL tilt): ${CUR}%."
if [ -n "${HINT}" ]; then
  MSG="${MSG}
Gợi ý fetch tự động (CHƯA kiểm chứng, KHÔNG tự ghi): ~${HINT}%."
fi
MSG="${MSG}
Nếu lãi suất đã đổi, chạy (số phải xác nhận thật):
  python3 append_deposit_rate.py --rate <X> --effective ${TODAY} --source manual_verify"

# post via fleet notify (Discord #mikefleet) — never breaks caller, always exit 0
if [ -x "$WORKDIR_8L/mike/bin/notify.sh" ]; then
  "$WORKDIR_8L/mike/bin/notify.sh" "$MSG" >> "$LOG" 2>&1 || true
fi

# breadcrumb on the bus so the fleet sees the monthly reminder fired
if [ -x "$WORKDIR_8L/mike/bin/append_event.sh" ]; then
  "$WORKDIR_8L/mike/bin/append_event.sh" Winston status "deposit-rate-refresh-reminder" \
    "{\"month\":\"${MONTH}\",\"current\":\"${CUR}\",\"fetch_hint\":\"${HINT:-none}\"}" >> "$LOG" 2>&1 || true
fi

echo "===== deposit-rate refresh reminder DONE (posted reminder, current=${CUR}%) =====" >> "$LOG"
exit 0
