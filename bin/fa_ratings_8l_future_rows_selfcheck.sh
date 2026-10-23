#!/usr/bin/env bash
# Selfcheck khoi canh bao "dong eff_date tuong lai" cua refresh_fa_ratings_8l.sh (extract-and-test trong tmpdir,
# stub bq/notify — KHONG cham BQ that, KHONG gui Discord). Ca: one/repeat/multi/null/err/stderr-warn/notify-fail/exit-code.
set -uo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)/refresh_fa_ratings_8l.sh"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
mkdir -p "$T/bin" "$T/state" "$T/stub"
# Trich DUNG khoi (tu comment mo dau toi `rm -f "$_fut_err"`): tu 057d22a25 dong ke tiep la "$EVENT" ... $NUM_ROWS
# (bien cua wrapper) — khong con chu append_event.sh de grep -v loc ra nua.
awk '/^# Dong eff_date TUONG LAI/{f=1} f{print} f&&/^rm -f "\$_fut_err"/{exit}' "$SRC" > "$T/block.sh"
[ -s "$T/block.sh" ] || { echo "FAIL: khong trich duoc khoi tu $SRC"; exit 1; }
NOTIFY_LOG="$T/notified"; : > "$NOTIFY_LOG"
cat > "$T/bin/notify_thread.sh" <<EOS
#!/bin/bash
[ "\${NOTIFY_RC:-0}" = 0 ] && echo "\$1" >> "$NOTIFY_LOG"
exit \${NOTIFY_RC:-0}
EOS
cat > "$T/stub/bq" <<'EOS'
#!/bin/bash
[ -n "${BQ_STDERR:-}" ] && echo "$BQ_STDERR" >&2
printf '%b' "$BQ_OUT"
exit "${BQ_RC:-0}"
EOS
chmod +x "$T/bin/notify_thread.sh" "$T/stub/bq"
fail=0
run() { # $1=BQ_OUT ; env: BQ_STDERR NOTIFY_RC
  # NOTIFY: khoi goi "$NOTIFY" tu 057d22a25 (truoc do goi thang $MIKE/bin/notify_thread.sh)
  PATH="$T/stub:$PATH" BQ_OUT="$1" MIKE="$T" PROJECT=p TABLE=t.t DISCORD_TRADING_DAILY=td NOTIFY="$T/bin/notify_thread.sh" \
    bash -c 'set -uo pipefail; source "$0"' "$T/block.sh" 2>&1
}
ok() { if [ "$1" = 0 ]; then echo "PASS $2"; else echo "FAIL $2"; fail=1; fi; }
notified() { wc -l < "$NOTIFY_LOG" | tr -d ' '; }
S="$T/state/fa_ratings_8l_future_rows.txt"

o="$(run 'fut\nPMT@2026-10-18\n')"; [ "$(notified)" = 1 ] && [ "$(cat "$S")" = "PMT@2026-10-18" ]; ok $? "one: bao 1 lan + ghi state"
o="$(run 'fut\nPMT@2026-10-18\n')"; [ "$(notified)" = 1 ]; ok $? "repeat cung tap: KHONG bao lai"
o="$(run 'fut\n"PMT@2026-10-18,XYZ@2026-10-20"\n')"; [ "$(notified)" = 2 ] && [ "$(cat "$S")" = "PMT@2026-10-18,XYZ@2026-10-20" ]; ok $? "multi (csv co ngoac kep): tap doi ⇒ bao lai"
o="$(run 'fut\n""\n')"; [ ! -e "$S" ] && ! echo "$o" | grep -q "WARN"; ok $? "null (\"\"): xoa state, khong WARN"
o="$(BQ_RC=1 run 'BigQuery error in query operation: boom\n')"; echo "$o" | grep -q "khong kiem duoc.*boom" && [ "$(notified)" = 2 ]; ok $? "loi bq (in ra stdout): in loi THAT, khong bao Discord"
o="$(BQ_STDERR='WARNING: deprecated flag' run 'fut\nPMT@2026-10-18\n')"; echo "$o" | grep -q "TUONG LAI: PMT" && ! echo "$o" | grep -q "khong kiem duoc"; ok $? "stderr canh bao KHONG lam lech header"
rm -f "$S"; : > "$NOTIFY_LOG"
o="$(NOTIFY_RC=1 run 'fut\nPMT@2026-10-18\n')"; [ ! -e "$S" ] && echo "$o" | grep -q "notify_thread.sh that bai"; ok $? "notify hong: KHONG ghi state"
o="$(run 'fut\nPMT@2026-10-18\n')"; [ "$(notified)" = 1 ] && [ -e "$S" ]; ok $? "lan sau notify OK: bao lai + ghi state (khong mat canh bao)"
PATH="$T/stub:$PATH" BQ_OUT='BigQuery error: x\n' BQ_RC=1 MIKE="$T" PROJECT=p TABLE=t.t DISCORD_TRADING_DAILY=td NOTIFY="$T/bin/notify_thread.sh" bash -c 'set -uo pipefail; source "$0"' "$T/block.sh" >/dev/null 2>&1
ok $? "bq loi: khoi van rc=0 (khong lam wrapper fail)"
echo "RESULT $([ "$fail" = 0 ] && echo PASS || echo FAIL)"; exit "$fail"
