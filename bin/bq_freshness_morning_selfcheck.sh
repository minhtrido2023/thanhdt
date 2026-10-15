#!/usr/bin/env bash
# Selfcheck morning-mode của bq_freshness_check.sh: trích ĐÚNG 2 khối đã sửa (header TODAY/NEXT và gate
# publisher-evidence) bằng marker rồi chạy trong harness — KHÔNG chạy pipeline thật, KHÔNG notify/BQ.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; SRC="$HERE/bq_freshness_check.sh"
fail=0; chk() { if [ "$2" = "$3" ]; then echo "OK   $1"; else echo "FAIL $1: got '$2' want '$3'"; fail=1; fi; }
HDR="$(sed -n '/^TODAY="\$(date +%Y-%m-%d)"$/,/^  echo "MORNING MODE/p' "$SRC" | sed "s#\$(dirname \"\${BASH_SOURCE\[0\]}\")#$HERE#"; echo fi)"
GATE="$(sed -n '/^dt5g_pub_reason=""$/,/^if \[ -n "\$dt5g_pub_reason" \]/p' "$SRC" | sed '$d')"
[ -n "$HDR" ] && [ -n "$GATE" ] || { echo "FAIL không trích được khối từ $SRC"; exit 1; }
hdr() { # $1 = MIKE_NOW_ICT, $2 = MIKE_MORNING_RUN
  env -u TZ MIKE_NOW_ICT="$1" MIKE_MORNING_RUN="$2" bash -c "$HDR
echo \"\$TODAY \${MORNING_NEXT:-}\"" 2>/dev/null | tail -1; }
chk "morning sáng T5 -> phiên T4" "$(hdr 2026-10-15T07:30:00 1)" "2026-10-14 2026-10-15"
chk "morning tối T4 -> phiên T4"  "$(hdr 2026-10-14T18:30:00 1)" "2026-10-14 2026-10-15"
DAYNOW="$(env -u TZ date +%Y-%m-%d)"; chk "mode tắt -> TODAY=ngày lịch, không MORNING_NEXT" "$(hdr 2026-10-15T07:30:00 0)" "$DAYNOW "
# gate: dựng state json + mtime
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
gate() { # $1 as_of $2 ok(true/false) $3 mtime-date $4 MORNING $5 TODAY $6 LAST $7 IS_TRADING
  printf '{"as_of":"%s","bq_publish_ok":%s}' "$1" "$2" > "$T/s.json"; touch -d "$3 12:00" "$T/s.json"; : > "$T/c.csv"
  bash -c "STATE_JSON_F=$T/s.json; DT5G_CSV_F=$T/c.csv; MORNING=$4; TODAY=$5; LAST_TRADING_DAY=$6; IS_TRADING_TODAY=$7
$GATE
echo \"[\$dt5g_pub_reason]\"" 2>/dev/null | tail -1; }
NOWD="$(date +%Y-%m-%d)"
chk "morning: as_of=phiên, mtime=hôm nay -> PASS"  "$(gate 2026-10-14 true $NOWD 1 2026-10-14 2026-10-14 1)" "[]"
chk "morning: mtime=phiên (publish tối) -> PASS"   "$(gate 2026-10-14 true 2026-10-14 1 2026-10-14 2026-10-14 1)" "[]"
chk "morning: mtime TRƯỚC phiên -> FAIL"           "$(gate 2026-10-14 true 2026-10-13 1 2026-10-14 2026-10-14 1 | grep -c 'KHÔNG chạy sau phiên')" "1"
chk "morning: as_of cũ -> FAIL"                    "$(gate 2026-10-13 true $NOWD 1 2026-10-14 2026-10-14 1 | grep -c '≠ phiên gần nhất')" "1"
chk "morning: publish_ok=false -> FAIL"            "$(gate 2026-10-14 false $NOWD 1 2026-10-14 2026-10-14 1 | grep -c 'bq_publish_ok=false')" "1"
chk "morning: mtime tương lai -> FAIL"             "$(gate 2026-10-14 true 2999-01-01 1 2026-10-14 2026-10-14 1 | grep -c 'KHÔNG chạy sau phiên')" "1"
chk "cron cũ: mtime != hôm nay -> vẫn FAIL"        "$(gate 2026-10-14 true 2026-10-13 0 $NOWD 2026-10-14 1 | grep -c 'KHÔNG chạy hôm nay')" "1"
[ "$fail" = 0 ] && echo "selfcheck: PASS" || { echo "selfcheck: FAIL"; exit 1; }
