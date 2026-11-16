#!/usr/bin/env bash
# Selfcheck bin/ai_momentum_cron.sh — stub python + notify gia (khong BQ, khong M1, khong Discord) + 6 mutant tren chinh wrapper.
# Chay: env -u TZ bash bin/ai_momentum_cron_selfcheck.sh ; TZ=UTC ... ; TZ=America/New_York ...
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; WRAP_SRC="$HERE/ai_momentum_cron.sh"
SB="$(mktemp -d /tmp/am_cron_sc.XXXXXX)"; trap 'rm -rf "$SB"' EXIT
fail=0; n=0
chk() { n=$((n+1)); if [ "$2" = "$3" ]; then echo "  ok   $1 = $2"; else echo "  FAIL $1: got '$2' want '$3'"; fail=$((fail+1)); fi; }
cat > "$SB/stub.py" <<'PY'
import os, sys, time, json
open(os.environ["STUB_MARK"], "a").write(" ".join(sys.argv[1:]) + "\n")
if os.environ.get("STUB_SLEEP"): time.sleep(float(os.environ["STUB_SLEEP"]))
if os.environ.get("STUB_JSON"): print(os.environ["STUB_JSON"])
sys.exit(int(os.environ.get("STUB_RC", "0")))
PY
cat > "$SB/notify.sh" <<'SH'
#!/usr/bin/env bash
printf '%s\t%s\n' "$2" "$1" >> "$STUB_ALERTS"
SH
chmod +x "$SB/notify.sh"
# run <wrapper> [ENV=VAL ...] -> rc ; reset marks
run() {
  local w="$1"; shift; : > "$SB/mark"; : > "$SB/alerts"; [ -n "${KEEP_STATE:-}" ] || rm -f "$SB/log/m2_alert.state"
  env AI_MOMENTUM_SCRIPT="$SB/stub.py" AI_MOMENTUM_LEDGER_DIR="$SB/ledger" AI_MOMENTUM_LOCK="$SB/lock" AI_MOMENTUM_LOGDIR="$SB/log" AI_MOMENTUM_NOTIFY="$SB/notify.sh" \
      AI_MOMENTUM_TODAY=2026-11-16 AI_MOMENTUM_HOUR=20 AI_MOMENTUM_TOTAL_TIMEOUT=60 STUB_MARK="$SB/mark" STUB_ALERTS="$SB/alerts" "$@" bash "$w"
}
alerts() { wc -l < "$SB/alerts" | tr -d ' '; }
cases() {   # $1 = wrapper path ; in ket qua tung ca
  local W="$1"
  run "$W" STUB_RC=0 STUB_JSON='{"m1_fail":0,"m2_fail":0,"m2_fail_streak":0,"written":[]}'; chk "rc0 sach: exit" "$?" 0; chk "rc0 sach: alert" "$(alerts)" 0
  chk "doi so truyen: --date + --ledger-dir" "$(cat "$SB/mark")" "--date 2026-11-16 --ledger-dir $SB/ledger"
  for r in 3 4 6; do run "$W" STUB_RC=$r; chk "rc=$r: exit 0, im lang" "$?/$(alerts)" "0/0"; done
  # C (R3): rc=4 o moc cuoi 23:00 ICT => alert 1 (topic momentum_lab) + exit 0; 22h = im lang; 00h (qua nua dem) khong tinh
  run "$W" STUB_RC=4 AI_MOMENTUM_HOUR=23; _rc=$?; chk "rc=4 moc cuoi 23h: exit 0 + alert 1" "$_rc/$(alerts)" "0/1"; grep -q "^momentum_lab.*MOC CUOI" "$SB/alerts" && chk "alert moc cuoi dung topic+noi dung" yes yes || chk "alert moc cuoi dung topic+noi dung" no yes
  run "$W" STUB_RC=4 AI_MOMENTUM_HOUR=22; chk "rc=4 luot 22h: im lang" "$?/$(alerts)" "0/0"
  run "$W" STUB_RC=4 AI_MOMENTUM_HOUR=08; chk "rc=4 08h (so sanh so hoc, khong bat 08 la bat phan): im lang" "$?/$(alerts)" "0/0"
  run "$W" STUB_RC=3 AI_MOMENTUM_HOUR=23; chk "rc=3 o 23h: im lang" "$?/$(alerts)" "0/0"
  for r in 5 1 7; do run "$W" STUB_RC=$r; _rc=$?; chk "rc=$r: alert 1 + exit $r" "$_rc/$(alerts)" "$r/1"; grep -q "rc=$r" "$SB/alerts" || { echo "  FAIL alert thieu rc=$r"; fail=$((fail+1)); }; done
  grep -q "^momentum_lab" "$SB/alerts" && chk "alert dung topic Momentum Lab" yes yes || chk "alert dung topic Momentum Lab" no yes
  run "$W" STUB_RC=0 STUB_JSON='{"m1_fail":2,"m2_fail_streak":0,"written":["A_1","B_1"]}'; chk "M1 FAIL>0: alert" "$(alerts)" 1
  run "$W" STUB_RC=0 STUB_JSON='{"m1_fail":0,"m2_fail_streak":3,"written":[]}'; chk "M2 FAIL streak 3: alert" "$(alerts)" 1
  run "$W" STUB_RC=0 STUB_JSON='{"m1_fail":0,"m2_fail_streak":2,"written":[]}'; chk "M2 FAIL streak 2: im lang" "$(alerts)" 0
  # R3-D(b): alert M2 chi khi DOI trang thai
  J3='{"m1_fail":0,"m2_fail_streak":3,"written":[]}'; J0='{"m1_fail":0,"m2_fail_streak":0,"written":[]}'
  run "$W" STUB_RC=0 STUB_JSON="$J3"; a1="$(alerts)"
  KEEP_STATE=1 run "$W" STUB_RC=0 STUB_JSON='{"m1_fail":0,"m2_fail_streak":4,"written":[]}'; a2="$(alerts)"
  KEEP_STATE=1 run "$W" STUB_RC=0 STUB_JSON="$J0"; a3="$(alerts)"
  KEEP_STATE=1 run "$W" STUB_RC=0 STUB_JSON="$J3"; a4="$(alerts)"
  chk "M2 FAIL: bao lan dau / khong lap / hoi phuc im lang / hong lai bao" "$a1/$a2/$a3/$a4" "1/0/0/1"
  run "$W" STUB_RC=0 STUB_JSON='khong phai json'; chk "stdout rac: alert" "$(alerts)" 1
  local t0=$SECONDS; run "$W" STUB_RC=0 STUB_SLEEP=30 AI_MOMENTUM_TOTAL_TIMEOUT=2; _rc=$?; local dt=$((SECONDS-t0))
  chk "timeout tong: exit 124, alert, <15s" "$_rc/$(alerts)/$([ $dt -lt 15 ] && echo fast || echo slow)" "124/1/fast"
  # flock: giu khoa o ngoai => wrapper KHONG goi python, KHONG alert, exit 0
  : > "$SB/mark"; ( exec 8>"$SB/lock"; flock -n 8 && sleep 4 ) & sleep 0.5
  run "$W" STUB_RC=0; chk "dang co luot khac: exit 0, python khong chay, im lang" "$?/$(wc -c < "$SB/mark" | tr -d ' ')/$(alerts)" "0/0/0"; wait
  run "$W" STUB_RC=0 STUB_JSON='{"m1_fail":0,"m2_fail_streak":0}'; chk "sau khi nha khoa: chay lai duoc" "$(wc -l < "$SB/mark" | tr -d ' ')" 1
}
echo "TZ env=${TZ:-<unset>}"; echo "== wrapper that"; cases "$WRAP_SRC"
real_fail=$fail; n_real=$n
echo "== mutant (moi mutant PHAI lam it nhat 1 ca FAIL; target phai ton tai)"
mkdir -p "$SB/m/bin"; mut=0; killed=0
mutate() {   # name old new
  local name="$1" old="$2" new="$3"; mut=$((mut+1))
  grep -qF -- "$old" "$WRAP_SRC" || { echo "  HARNESS-FAIL mutant[$name]: target khong ton tai"; fail=$((fail+1)); return; }
  python3 - "$WRAP_SRC" "$SB/m/bin/ai_momentum_cron.sh" "$old" "$new" <<'PY'
import sys; s = open(sys.argv[1]).read(); open(sys.argv[2], "w").write(s.replace(sys.argv[3], sys.argv[4], 1))
PY
  local before=$fail; fail=0; cases "$SB/m/bin/ai_momentum_cron.sh" > "$SB/mut.out" 2>&1; local mf=$fail; fail=$before
  if [ "$mf" -gt 0 ]; then killed=$((killed+1)); echo "  KILLED mutant[$name] ($mf ca fail)"; else echo "  SURVIVED mutant[$name]"; fail=$((fail+1)); fi
}
mutate "bo flock -n" 'if ! flock -n 9; then' 'if false; then'
mutate "alert ca rc=3" '3|6) exit 0 ;;' '6) exit 0 ;;'
mutate "khong alert rc ha tang" '*) alert "ai_momentum T=$TODAY: rc=$rc' '*) : "ai_momentum T=$TODAY: rc=$rc'
mutate "bo timeout tong" 'timeout --kill-after=30 "$TOTAL_TIMEOUT" "$PY"' '"$PY"'
mutate "bo canh bao M1 FAIL" 'if o.get("m1_fail", 0) > 0 else ""' 'if False else ""'
mutate "streak 3 -> 99" '[ "$streak" -ge 3 ]' '[ "$streak" -ge 99 ]'
mutate "M2 alert lap moi luot" '!= "FAIL" ]; then alert' '!= "ZZZ" ]; then alert'
mutate "M2 hoi phuc khong xoa trang thai" 'echo OK > "$M2_STATE"' ':'
mutate "C rc=4 moc cuoi khong alert" '-ge "$((10#$FINAL_HOUR))"' '-ge 99'
mutate "C rc=4 luon alert" '-ge "$((10#$FINAL_HOUR))"' '-ge 0'
mutate "C bo 10# (08 -> bat phan)" '"$((10#$START_HOUR))"' '"$((START_HOUR))"'
mutate "doi topic" 'TOPIC=momentum_lab' 'TOPIC=trading_daily'
echo "== $n_real ca x (1+$mut) lan, $mut mutant ($killed killed) -> $([ $fail -eq 0 ] && echo 'ALL PASS' || echo "$fail LOI")"
exit $([ $fail -eq 0 ] && echo 0 || echo 1)
