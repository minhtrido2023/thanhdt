#!/usr/bin/env bash
# Selfcheck morning-mode của bq_freshness_check.sh (phần NGOÀI gate publisher — gate nằm trong
# dt5g_publisher_gate_selfcheck.sh ca M1-M9). Trích ĐÚNG các khối bằng marker CÓ GIỚI HẠN (start<end,
# bounded) rồi chạy trong harness: (a) header TODAY/MORNING_NEXT + rào giờ, (b) khối NEXT_TRADING_DAY
# (override), (c) khối MORNING-SKIP (không ghi đè plan). KHÔNG chạy pipeline thật / notify / BQ.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; SRC="${SRC_OVERRIDE:-$HERE/bq_freshness_check.sh}"
WC="${WC_ROOT:-/home/trido/thanhdt/WorkingClaude}"
fail=0; chk() { if [ "$2" = "$3" ]; then echo "OK   $1"; else echo "FAIL $1: got '$2' want '$3'"; fail=1; fi; }
extract() { # $1=start regex $2=end regex (dòng kết thúc ĐƯỢC gồm); trả rỗng nếu không bounded
  local s e; s=$(grep -nE "$1" "$SRC" | head -1 | cut -d: -f1); e=$(awk -v s="${s:-0}" -v re="$2" 'NR>s && $0 ~ re {print NR; exit}' "$SRC")
  [ -n "$s" ] && [ -n "$e" ] && [ "$e" -gt "$s" ] && [ $((e-s)) -lt 40 ] && sed -n "${s},${e}p" "$SRC"; }
HDR="$(extract '^MORNING="\$\{MIKE_MORNING_RUN' '^fi$')"
HDR="$(printf '%s\n' "$HDR" | sed "s#\$(dirname \"\${BASH_SOURCE\\[0\\]}\")#$HERE#")"
NEXTB="$(extract '^NEXT_TRADING_DAY=' '^fi$')"
SKIP="$(extract 'MORNING-SKIP-BEGIN' 'MORNING-SKIP-END')"
for n in HDR NEXTB SKIP; do [ -n "${!n}" ] || { echo "FAIL không trích được khối $n (marker đổi/không bounded)"; exit 1; }; done
grep -q 'echo "MORNING MODE' <<<"$HDR" || { echo "FAIL HDR không chứa dòng MORNING MODE — trích sai"; exit 1; }

hdr() { env -u TZ MIKE_NOW_ICT="$1" MIKE_MORNING_RUN="$2" WORKDIR_8L="$WC" bash -c "TODAY=CAL; $HDR
echo \"rc=0 \$TODAY \${MORNING_NEXT:-}\"" 2>&1 | tail -1; }
chk "header: 07:30 T5 -> phiên 10-14, plan 10-15" "$(hdr 2026-10-15T07:30:00 1)" "rc=0 2026-10-14 2026-10-15"
chk "header: 18:30 T4 -> phiên 10-14, plan 10-15 (như cron)" "$(hdr 2026-10-14T18:30:00 1)" "rc=0 2026-10-14 2026-10-15"
chk "header: 10:00 T5 -> TỪ CHỐI (rào giờ)" "$(hdr 2026-10-15T10:00:00 1 | grep -c 'TỪ CHỐI')" "1"
chk "header: mode tắt -> TODAY giữ nguyên" "$(hdr 2026-10-15T10:00:00 0)" "rc=0 CAL "

nxt() { # $1=MORNING $2=MORNING_NEXT
  local sb; sb="$(mktemp -d)"; ln -s "$WC/trading_bot" "$sb/trading_bot"
  env -u TZ bash -c "WORKDIR=$sb; MORNING=$1; MORNING_NEXT=$2; $NEXTB
echo \"NEXT=\$NEXT_TRADING_DAY\"" 2>&1 | tail -1; rm -rf "$sb"; }
chk "NEXT: morning=1 -> lấy MORNING_NEXT (không phải next_trading_day(hôm nay))" "$(nxt 1 2026-10-15)" "NEXT=2026-10-15"
EXP="$(env -u TZ python3 -c "
import sys; sys.path.insert(0,'$WC')
from trading_bot.vn_market import next_trading_day; import datetime as dt; print('NEXT='+str(next_trading_day(dt.date.today())))")"
chk "NEXT: morning=0 -> next_trading_day(hôm nay) như cũ" "$(nxt 0 2026-10-15)" "$EXP"

skip() { # $1=MORNING $2=file-exists(1/0) $3=FORCE
  local sb; sb="$(mktemp -d)"; mkdir -p "$sb/data/trade_plans"; [ "$2" = 1 ] && : > "$sb/data/trade_plans/plan_X_2026-10-15.json"
  env -u TZ bash -c "WORKDIR=$sb; MORNING=$1; ACCT=X; NEXT_TRADING_DAY=2026-10-15; MIKE_MORNING_FORCE=$3
for ACCT in X; do
$SKIP
echo DISPATCHED
done" 2>&1 | tail -1; rm -rf "$sb"; }
r="$(skip 1 1 0)"; [ "$r" = "DISPATCHED" ] && { echo "FAIL SKIP: morning + plan tồn tại vẫn dispatch"; fail=1; } || echo "OK   SKIP: morning + plan tồn tại -> không dispatch"
chk "SKIP: morning + plan CHƯA có -> dispatch" "$(skip 1 0 0)" "DISPATCHED"
chk "SKIP: morning + plan có + FORCE=1 -> dispatch" "$(skip 1 1 1)" "DISPATCHED"
chk "SKIP: mode tắt + plan có -> dispatch (cron cũ)" "$(skip 0 1 0)" "DISPATCHED"
[ "$fail" = 0 ] && echo "selfcheck: PASS" || { echo "selfcheck: FAIL"; exit 1; }
