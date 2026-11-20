#!/usr/bin/env bash
# Selfcheck dd_zone_candidates_daily.sh — stub watch + stub notify, KHÔNG chạm production/mạng/Discord.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TD="$(mktemp -d)"; trap 'rm -rf "$TD"' EXIT
export DDZ_CANDIDATES="$TD/cand.json" DDZ_DAILY_NOTIFY_CMD="$TD/notify.sh" MIKE_BOT_TEST_MODE=1
printf '#!/usr/bin/env bash\necho "$1 |$2" >> %s/notified.txt\n' "$TD" > "$TD/notify.sh"; chmod +x "$TD/notify.sh"
EXP="$(cd "$ROOT/bin" && python3 -c "import datetime as dt,dd_price_zone_watch as W;print(W.default_asof(dt.datetime.now(W._ICT))[0].isoformat())")"
fail=0; chk(){ if [ "$2" = "1" ]; then echo "PASS $1"; else echo "FAIL $1"; fail=1; fi; }
mkstub(){ printf '#!/usr/bin/env bash\n%s\n' "$1" > "$TD/watch.sh"; chmod +x "$TD/watch.sh"; }
run(){ DDZ_WATCH_CMD="$TD/watch.sh" DNA_PYEXE=python3 bash "$ROOT/bin/dd_zone_candidates_daily.sh" >/dev/null 2>&1; echo $?; }

# 1) watch OK + file tươi ⇒ rc0, không báo
rm -f "$TD/notified.txt"; mkstub "echo '{\"schema\":\"dd_zone_candidates/v1\",\"asof\":\"$EXP\"}' > \"$DDZ_CANDIDATES\""
r="$(run)"; chk "watch OK + file tươi ⇒ rc=0, không báo" "$([ "$r" = 0 ] && [ ! -f "$TD/notified.txt" ] && echo 1 || echo 0)"
# 2) watch lỗi (TypeError giả) + file cũ ⇒ rc1, báo kèm lỗi thật
echo '{"schema":"dd_zone_candidates/v1","asof":"2000-01-03"}' > "$DDZ_CANDIDATES"
mkstub "echo 'LỖI: TypeError: fromisoformat: argument must be str' >&2; exit 1"
r="$(run)"; chk "watch lỗi ⇒ rc=1" "$([ "$r" = 1 ] && echo 1 || echo 0)"
chk "tin báo mang lỗi thật + STALE + gửi trading_daily" "$(grep -q 'TypeError' "$TD/notified.txt" && grep -q 'STALE' "$TD/notified.txt" && grep -q '|trading_daily' "$TD/notified.txt" && echo 1 || echo 0)"
# 3) watch rc0 nhưng KHÔNG ghi file mới (file cũ) ⇒ vẫn báo (không tin rc một mình)
rm -f "$TD/notified.txt"; mkstub "exit 0"
r="$(run)"; chk "rc=0 nhưng file cũ ⇒ vẫn báo + rc=1" "$([ "$r" = 1 ] && [ -f "$TD/notified.txt" ] && echo 1 || echo 0)"
# 4) thiếu file ⇒ báo MISSING
rm -f "$TD/notified.txt" "$DDZ_CANDIDATES"
r="$(run)"; chk "thiếu file ⇒ báo MISSING" "$(grep -q MISSING "$TD/notified.txt" && echo 1 || echo 0)"
exit $fail
