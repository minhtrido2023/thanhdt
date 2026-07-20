#!/usr/bin/env bash
# refresh_deposit_rate_vn.sh — MONTHLY reminder to update the Big-4 12M deposit rate.
#
# Layer A (CHỈ NHẮC) — reverted 2026-07-20 (user decision: stop auto-crosscheck after 6 rounds
# of adversarial review each finding new attack surface; cost > benefit for a 1×/month input;
# remove the attack surface entirely rather than continue patching it).
#
# Best-effort direct fetch (read-only, harmless) is kept as a cheap hint.
# Auto-dispatch of Winston to write is REMOVED — always sends the manual-reminder notify instead.
#
# deposit_rate_vn.current_deposit_rate() is a LIVE production input (rating_8l.py NEUTRAL tilt).
#
# Schedule: day 3 of month, 08:10 ICT (before the DCF refresh-gate consumes it around day 11).
set -uo pipefail
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
PY="$DNA_PYEXE"; cd "$WORKDIR_8L"

MONTH="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m)"
TODAY="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)"
LOG="data/refresh_deposit_rate_vn_$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m).log"
echo "===== deposit-rate refresh START $(date -u +%Y-%m-%dT%H:%M:%SZ) (ICT ${TODAY}) =====" >> "$LOG"

# current live value (frozen anchors + any CSV appends)
CUR="$($PY -c 'from deposit_rate_vn import current_deposit_rate; print(f"{current_deposit_rate():.2f}")' 2>>"$LOG")" || CUR="?"
echo "current_deposit_rate() = ${CUR}%" >> "$LOG"

# cheap best-effort direct fetch (CafeF table is JS-rendered, success expected to fail —
# kept only as a starting hint for the human who will manually confirm the rate)
HINT="$($PY - <<'PYEOF' 2>>"$LOG"
import re, sys
try:
    import urllib.request
    req = urllib.request.Request(
        "https://cafef.vn/du-lieu/lai-suat-ngan-hang.chn",
        headers={"User-Agent": "Mozilla/5.0 (deposit-rate-refresh best-effort)"})
    html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "ignore")
    m = re.search(r"12\s*th[aá]ng.{0,80}?(\d(?:[.,]\d)?)\s*%", html, re.I | re.S)
    if m:
        print(m.group(1).replace(",", "."))
except Exception as e:
    print(f"fetch failed: {e}", file=sys.stderr)
PYEOF
)"
HINT="$(printf '%s' "$HINT" | tr -d '[:space:]')"
echo "direct fetch hint = '${HINT:-<none>}'" >> "$LOG"

# Always send the manual reminder — no auto-dispatch, no agent writes.
MSG="📋 Nhắc tháng ${MONTH}: xác nhận lãi suất tiết kiệm 12 tháng Big-4 (Agribank/VCB/BIDV/VietinBank), kênh ONLINE.
Giá trị đang dùng (live, input rating_8l NEUTRAL tilt): ${CUR}%.
Gợi ý CafeF best-effort fetch: '${HINT:-không lấy được}'.
Nếu lãi suất đã đổi, chạy (xác nhận số thật trước):
  python3 append_deposit_rate.py --rate <X> --effective ${TODAY} --source manual_verify"
if [ -x "$WORKDIR_8L/mike/bin/notify.sh" ]; then
  "$WORKDIR_8L/mike/bin/notify.sh" "$MSG" >> "$LOG" 2>&1 || true
fi

echo "===== deposit-rate refresh DONE (manual-remind sent, current_before=${CUR}%) =====" >> "$LOG"
exit 0
