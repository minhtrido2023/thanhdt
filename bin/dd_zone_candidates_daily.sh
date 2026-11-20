#!/usr/bin/env bash
# dd_zone_candidates_daily.sh — làm mới data/dd_zone_candidates_latest.json MỖI phiên (T2-T6, 19:45 ICT),
# ĐỘC LẬP với việc gửi plan. User duyệt 2026-11-20 (đề xuất 1+3). Nguồn mục E của bản tin 08:00 và phễu
# discretionary — trước đây chỉ được làm mới như khối phụ của send_plan_report.sh (ZaloPay, 21:00), nên
# khối phụ hỏng/plan không gửi ⇒ danh sách đứng yên (sự cố 16–19/11/2026: expires_on null ⇒ TypeError).
#
# CHỈ ĐỌC (DNSE ohlc 1D + sổ kb/dd_price_zones.json); KHÔNG đặt lệnh, KHÔNG ghi plan.
# Sau khi chạy, so asof trong file với phiên đã đóng gần nhất; lỗi hoặc file CŨ ⇒ 1 tin vào Trading Daily
# kèm dòng lỗi THẬT (coding_guidelines §29), không im lặng.
# Chạy lại cùng asof là idempotent (state/ngày ghi đè đúng khoá asof).
#
# Test: DDZ_WATCH_CMD=<stub> DDZ_DAILY_NOTIFY_CMD=<stub> DDZ_CANDIDATES=<file> bin/dd_zone_candidates_daily.sh
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"
# shellcheck source=/dev/null
[ -f "$WC_ROOT/wc_env.sh" ] && source "$WC_ROOT/wc_env.sh" 2>/dev/null || true
PY="${DNA_PYEXE:-python3}"
WATCH="${DDZ_WATCH_CMD:-$ROOT/bin/dd_price_zone_watch.py}"
NOTIFY="${DDZ_DAILY_NOTIFY_CMD:-$ROOT/bin/notify_thread.sh}"
ERR="$(mktemp)"; OUT="$(mktemp)"
trap 'rm -f "$ERR" "$OUT"' EXIT

case "$WATCH" in *.py) RUNNER=("$PY" "$WATCH") ;; *) RUNNER=("$WATCH") ;; esac   # stub selfcheck là .sh
timeout -k 5 "${DDZ_DAILY_TIMEOUT:-300}" "${RUNNER[@]}" run >"$OUT" 2>"$ERR"
RC=$?

# Phiên đã đóng gần nhất (cùng hàm watch dùng) vs asof trong file ứng viên.
VERDICT="$(cd "$ROOT/bin" && "$PY" - <<'PYEOF' 2>&1
import datetime as dt, json, os, sys
import dd_price_zone_watch as W
exp, _ = W.default_asof(dt.datetime.now(W._ICT))
try:
    got = json.load(open(W.CAND_JSON, encoding="utf-8")).get("asof")
except Exception as e:  # noqa: BLE001 — §29: in lỗi thật
    print(f"MISSING {type(e).__name__}: {e}"); sys.exit(0)
print(("OK " if str(got) >= exp.isoformat() else "STALE ") + f"file={got} expected={exp.isoformat()}")
PYEOF
)"

if [ "$RC" -eq 0 ] && [ "${VERDICT%% *}" = "OK" ]; then
  echo "[ddz-daily] $(TZ='Asia/Ho_Chi_Minh' date +'%F %H:%M ICT') OK — $VERDICT"
  exit 0
fi

REAL_ERR="$(grep -v -i -E 'warn|^\s*$' "$ERR" | tail -2 | cut -c1-220 | tr '\n' ' ')"
MSG="⚠️ Danh sách ứng viên sleeve từ sổ DD KHÔNG được làm mới (dd_zone_candidates_daily rc=$RC; $VERDICT). Mục E bản tin 08:00 sẽ hiển thị KẾT QUẢ CŨ. Lỗi thật: ${REAL_ERR:-không có dòng lỗi (kiểm logs/dd_zone_candidates_daily.log)}"
echo "[ddz-daily] $MSG" >&2
"$NOTIFY" "$MSG" trading_daily >/dev/null 2>&1 || echo "[ddz-daily] notify_thread thất bại" >&2
exit 1
