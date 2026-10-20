#!/usr/bin/env bash
# fa_ratings_ticker_gate_selfcheck.sh — selfcheck cổng ticker-gate (job Taylor_20261020_082306).
# Không chạm BQ/Discord/bus thật: số đo giả qua GATE_FAKE_MEASURE, notify/event là stub ghi file.
# Chạy: bash bin/fa_ratings_ticker_gate_selfcheck.sh   (tự chạy lại dưới env -u TZ và TZ lạ)
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GATE_SRC="$HERE/fa_ratings_ticker_gate.sh"; WRAP_SRC="$HERE/refresh_fa_ratings_8l.sh"
FA_SRC="$HERE/refresh_fa_ratings.sh"; WIN_SRC="$HERE/fa_ratings_earnings_window_daily.sh"
if [ -z "${_GATE_SC_INNER:-}" ]; then
  rc=0
  for mode in "env -u TZ" "env TZ=Pacific/Kiritimati" "env TZ=America/Los_Angeles"; do
    echo "### $mode"; _GATE_SC_INNER=1 $mode bash "${BASH_SOURCE[0]}" || rc=1
  done
  [ "$rc" -eq 0 ] && echo "ALL ENVIRONMENTS OK" || echo "FAILED in some environment"
  exit "$rc"
fi
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
PASS=0; FAIL=0
ok(){ PASS=$((PASS+1)); }
bad(){ FAIL=$((FAIL+1)); echo "  FAIL: $*"; }
cat > "$TMP/notify.sh" <<'S'
#!/usr/bin/env bash
echo "$1" >> "$NOTIFY_LOG"; exit "${NOTIFY_RC:-0}"
S
cat > "$TMP/event.sh" <<'S'
#!/usr/bin/env bash
echo "$*" >> "$EVENT_LOG"
S
chmod +x "$TMP/notify.sh" "$TMP/event.sh"

# run_gate <gate_script> <fake_measure> [extra env...] → đặt G_OUT, G_RC; state/log mới mỗi lần trừ khi KEEP=1
run_gate(){
  local script="$1" fake="$2"; shift 2
  [ -z "${KEEP:-}" ] && { rm -rf "$TMP/state"; : > "$TMP/n.log"; : > "$TMP/e.log"; }
  mkdir -p "$TMP/state"
  G_OUT="$(env GATE_FAKE_MEASURE="$fake" GATE_FAKE_LM="2026-10-20 14:29 ICT" GATE_STATE_DIR="$TMP/state" \
     FA8L_NOTIFY="$TMP/notify.sh" FA8L_EVENT="$TMP/event.sh" NOTIFY_LOG="$TMP/n.log" EVENT_LOG="$TMP/e.log" "$@" bash "$script" 2>&1)"
  G_RC=$?
}
expect(){  # name script fake want_rc [want_substr]
  local name="$1" script="$2" fake="$3" wrc="$4" sub="${5:-}"
  run_gate "$script" "$fake"
  if [ "$G_RC" -ne "$wrc" ]; then bad "$name: rc=$G_RC want $wrc | $G_OUT"; return; fi
  if [ -n "$sub" ] && ! grep -qF -- "$sub" <<<"$G_OUT"; then bad "$name: thiếu '$sub' | $G_OUT"; return; fi
  if [ "$wrc" -eq 3 ] && [ "${G_OUT:0:1}" != "❌" ]; then bad "$name: dòng fail không bắt đầu bằng ❌"; return; fi
  ok
}
suite(){  # $1 = gate script; trả về số fail thêm
  local g="$1"
  expect normal         "$g" "1294,343,343,2026-10-20,2026-10-19" 0 "PASS"
  expect real-today     "$g" "1066,343,310,2026-10-20,2026-10-19" 3 "n_mã 1066 < 1250"
  expect real-cov-shown "$g" "1066,343,310,2026-10-20,2026-10-19" 3 "0.904"
  expect n-at-thresh    "$g" "1250,343,343,2026-10-20,2026-10-19" 0
  expect n-below-thresh "$g" "1249,343,343,2026-10-20,2026-10-19" 3
  expect univ-250       "$g" "1294,250,250,2026-10-20,2026-10-19" 3 "n_universe 250 < 300"
  expect univ-300       "$g" "1294,300,300,2026-10-20,2026-10-19" 0
  expect univ-0         "$g" "1294,0,0,2026-10-20,2026-10-19" 3
  expect cov-0979       "$g" "1294,343,336,2026-10-20,2026-10-19" 3 "phủ"
  expect cov-0982       "$g" "1294,343,337,2026-10-20,2026-10-19" 0
  expect query-error    "$g" "ERROR:bq rc=1: boom-xyz" 3 "truy vấn đo số mã LỖI"
  expect query-error-ev "$g" "ERROR:bq rc=1: boom-xyz" 3 "boom-xyz"
  expect garbage        "$g" "abc" 3 "không parse"
  expect weekend-stale  "$g" "1294,343,343,2026-10-11,2026-10-09" 0   # max(time) cũ KHÔNG chặn
  # dedupe: fail,fail → 1 notify + 1 event; pass xoá state; fail lại → lần 2
  KEEP=1 run_gate "$g" "1066,343,310,x,y"; KEEP=1 run_gate "$g" "1066,343,310,x,y"
  [ "$(wc -l < "$TMP/n.log")" -eq 1 ] && [ "$(wc -l < "$TMP/e.log")" -eq 1 ] && ok || bad "dedupe: n=$(wc -l < "$TMP/n.log") e=$(wc -l < "$TMP/e.log") want 1/1"
  KEEP=1 run_gate "$g" "1294,343,343,x,y"; KEEP=1 run_gate "$g" "1066,343,310,x,y"
  [ "$(wc -l < "$TMP/n.log")" -eq 2 ] && ok || bad "re-alert sau PASS: n=$(wc -l < "$TMP/n.log") want 2"
  # notify hỏng ⇒ không ghi state ⇒ lần sau thử lại
  rm -rf "$TMP/state"; : > "$TMP/n.log"
  KEEP=1 run_gate "$g" "1066,343,310,x,y" NOTIFY_RC=1; KEEP=1 run_gate "$g" "1066,343,310,x,y" NOTIFY_RC=1
  [ "$(wc -l < "$TMP/n.log")" -eq 2 ] && ok || bad "notify-fail retry: n=$(wc -l < "$TMP/n.log") want 2"
}
echo "== suite chính"; suite "$GATE_SRC"
echo "== wiring wrapper: fail không gọi rating_8l_history.py"
cat > "$TMP/hist_stub.sh" <<S
#!/usr/bin/env bash
echo called >> "$TMP/hist_called"
exit 0
S
chmod +x "$TMP/hist_stub.sh"
wrap(){  # <wrapper> <fake> ; đặt W_RC; hist_called tạo nếu stub chạy
  local w="$1" fake="$2"; rm -f "$TMP/hist_called"; rm -rf "$TMP/state"; : > "$TMP/n.log"; : > "$TMP/e.log"
  env GATE_FAKE_MEASURE="$fake" GATE_FAKE_LM=x GATE_STATE_DIR="$TMP/state" FA8L_NOTIFY="$TMP/notify.sh" FA8L_EVENT="$TMP/event.sh" \
    NOTIFY_LOG="$TMP/n.log" EVENT_LOG="$TMP/e.log" FA8L_GATE_CMD="$TMP/gate_under_test.sh" FA8L_HISTORY_CMD="$TMP/hist_stub.sh" \
    bash "$w" >/dev/null 2>&1; W_RC=$?
}
wiring(){  # <wrapper> <gate> tag
  cp "$2" "$TMP/gate_under_test.sh"; chmod +x "$TMP/gate_under_test.sh"
  wrap "$1" "1066,343,310,x,y"
  [ "$W_RC" -eq 3 ] && [ ! -e "$TMP/hist_called" ] && ok || bad "$3: fail ⇒ want rc3 & stub KHÔNG gọi (rc=$W_RC called=$([ -e "$TMP/hist_called" ] && echo yes || echo no))"
  wrap "$1" "1294,343,343,x,y"
  [ -e "$TMP/hist_called" ] && ok || bad "$3: pass ⇒ stub phải được gọi"
}
wiring "$WRAP_SRC" "$GATE_SRC" real


echo "== đường BQ thật (stub bq): rc/header/stderr/NULL/âm/float/timeout"
cat > "$TMP/bq_stub.sh" <<'S'
#!/usr/bin/env bash
[ "$1" = show ] && { echo '{}'; exit 0; }
H="n_distinct,n_universe,n_cov,max_t,univ_date"; G="1294,343,343,2026-10-20,2026-10-19"
case "$BQ_MODE" in
  good)    printf '%s\n%s\n' "$H" "$G" ;;
  rc1good) printf '%s\n%s\n' "$H" "$G"; echo "boom-rc1" >&2; exit 1 ;;
  empty)   : ;;
  header)  printf '%s\n' "$H" ;;
  warn)    echo "WARNING: gcloud deprecated thing" >&2; printf '%s\n%s\n' "$H" "$G" ;;
  null)    printf '%s\n%s\n' "$H" "1294,343,,2026-10-20,2026-10-19" ;;
  neg)     printf '%s\n%s\n' "$H" "-5,343,343,2026-10-20,2026-10-19" ;;
  float)   printf '%s\n%s\n' "$H" "1294.5,343,343,2026-10-20,2026-10-19" ;;
  cols)    printf '%s\n%s\n' "$H" "1294,343,343" ;;
  slow)    sleep 5; printf '%s\n%s\n' "$H" "$G" ;;
esac
S
chmod +x "$TMP/bq_stub.sh"
bqrun(){  # <gate> <mode> → G_OUT/G_RC (KHÔNG đặt GATE_FAKE_MEASURE ⇒ đi đường bq thật)
  rm -rf "$TMP/state"; : > "$TMP/n.log"; : > "$TMP/e.log"
  G_OUT="$(env -u GATE_FAKE_MEASURE BQ_MODE="$2" FA8L_BQ_CMD="$TMP/bq_stub.sh" GATE_BQ_TIMEOUT=1 GATE_STATE_DIR="$TMP/state" \
     FA8L_NOTIFY="$TMP/notify.sh" FA8L_EVENT="$TMP/event.sh" NOTIFY_LOG="$TMP/n.log" EVENT_LOG="$TMP/e.log" bash "$1" 2>&1)"; G_RC=$?
}
bqexpect(){  # <gate> <mode> <want_rc> [substr]
  bqrun "$1" "$2"
  [ "$G_RC" -eq "$3" ] || { bad "bq[$2]: rc=$G_RC want $3 | $G_OUT"; return; }
  [ -z "${4:-}" ] || grep -qF -- "$4" <<<"$G_OUT" || { bad "bq[$2]: thiếu '$4' | $G_OUT"; return; }
  ok
}
bqsuite(){
  local g="$1"
  bqexpect "$g" good    0 "PASS"
  bqexpect "$g" warn    0 "PASS"          # stderr có warning + dữ liệu hợp lệ ⇒ PASS
  bqexpect "$g" rc1good 3 "bq rc=1"       # rc≠0 kèm stdout tốt ⇒ FAIL
  bqexpect "$g" empty   3 "LỖI"
  bqexpect "$g" header  3 "không parse"
  bqexpect "$g" null    3 "không parse"
  bqexpect "$g" neg     3 "n_mã -5 < 1250"
  bqexpect "$g" float   3 "không parse"
  bqexpect "$g" cols    3 "không parse"
  bqexpect "$g" slow    3 "bq rc=124"     # timeout
}
bqsuite "$GATE_SRC"
echo "== NB2: bước đánh giá crash ⇒ vẫn chặn, nói rõ 'không đo được'"
mkdir -p "$TMP/badpy"; printf '#!/bin/sh\nexit 1\n' > "$TMP/badpy/python3"; chmod +x "$TMP/badpy/python3"
nb2(){ rm -rf "$TMP/state"; : > "$TMP/n.log"; : > "$TMP/e.log"
  G_OUT="$(env PATH="$TMP/badpy:$PATH" GATE_FAKE_MEASURE="1294,343,343,x,y" GATE_FAKE_LM=x GATE_STATE_DIR="$TMP/state" FA8L_NOTIFY="$TMP/notify.sh" FA8L_EVENT="$TMP/event.sh" NOTIFY_LOG="$TMP/n.log" EVENT_LOG="$TMP/e.log" bash "$1" 2>&1)"; G_RC=$?
  [ "$G_RC" -eq 3 ] && grep -qF "KHÔNG ĐO ĐƯỢC" <<<"$G_OUT" && grep -qF "KHÔNG ĐO ĐƯỢC" "$TMP/n.log" && ok || bad "NB2: rc=$G_RC out=$G_OUT"; }
nb2 "$GATE_SRC"

echo "== wiring refresh_fa_ratings.sh (cron T7 09:15): gate FAIL ⇒ rc3 & KHÔNG gọi python"
cat > "$TMP/fa_stub.sh" <<S
#!/usr/bin/env bash
echo called >> "$TMP/fa_called"
exit 0
S
chmod +x "$TMP/fa_stub.sh"
fawrap(){  # <wrapper> <fake>
  rm -f "$TMP/fa_called"; rm -rf "$TMP/state"; : > "$TMP/n.log"; : > "$TMP/e.log"
  env GATE_FAKE_MEASURE="$2" GATE_FAKE_LM=x GATE_STATE_DIR="$TMP/state" FA8L_NOTIFY="$TMP/notify.sh" FA8L_EVENT="$TMP/event.sh" \
    NOTIFY_LOG="$TMP/n.log" EVENT_LOG="$TMP/e.log" FA8L_GATE_CMD="$TMP/gate_under_test.sh" FA_REFRESH_CMD="$TMP/fa_stub.sh" \
    timeout 120 bash "$1" >/dev/null 2>&1; W_RC=$?
}
fawiring(){  # <wrapper> tag
  cp "$GATE_SRC" "$TMP/gate_under_test.sh"; chmod +x "$TMP/gate_under_test.sh"
  fawrap "$1" "1066,343,310,x,y"
  [ "$W_RC" -eq 3 ] && [ ! -e "$TMP/fa_called" ] && ok || bad "$2: fail ⇒ want rc3 & python KHÔNG gọi (rc=$W_RC called=$([ -e "$TMP/fa_called" ] && echo yes || echo no))"
  fawrap "$1" "1294,343,343,x,y"
  [ -e "$TMP/fa_called" ] && ok || bad "$2: pass ⇒ python phải được gọi"
}
fawiring "$FA_SRC" fa

echo "== R2: fa_ratings_earnings_window_daily.sh — child 8l rc=3 ⇒ bỏ child fa_ratings"
for r in 0 1 3; do printf '#!/usr/bin/env bash\necho c8 >> "%s/c8_called"; exit %s\n' "$TMP" "$r" > "$TMP/c8_$r.sh"; chmod +x "$TMP/c8_$r.sh"; done
printf '#!/usr/bin/env bash\necho cfa >> "%s/cfa_called"; exit 0\n' "$TMP" > "$TMP/cfa.sh"; chmod +x "$TMP/cfa.sh"
winrun(){  # <script> <rc8l> → W_RC; c8_called/cfa_called
  rm -f "$TMP/c8_called" "$TMP/cfa_called"
  env FA8L_WINDOW_RUN_DATE=2026-10-20 FA8L_WINDOW_SPACING_S=0 FA8L_WINDOW_LOG_8L="$TMP/l8.log" FA8L_WINDOW_LOG_FA="$TMP/lfa.log" \
    FA8L_WINDOW_CHILD_8L="$TMP/c8_$2.sh" FA8L_WINDOW_CHILD_FA="$TMP/cfa.sh" timeout 60 bash "$1" >/dev/null 2>&1; W_RC=$?
}
winsuite(){
  local w="$1" n="$2"
  winrun "$w" 3; [ "$W_RC" -eq 3 ] && [ -e "$TMP/c8_called" ] && [ ! -e "$TMP/cfa_called" ] && ok || bad "$n: 8l=3 ⇒ rc3 & fa KHÔNG chạy (rc=$W_RC fa=$([ -e "$TMP/cfa_called" ] && echo yes || echo no))"
  winrun "$w" 0; [ "$W_RC" -eq 0 ] && [ -e "$TMP/cfa_called" ] && ok || bad "$n: 8l=0 ⇒ rc0 & fa chạy (rc=$W_RC)"
  winrun "$w" 1; [ "$W_RC" -eq 1 ] && [ -e "$TMP/cfa_called" ] && ok || bad "$n: 8l=1 ⇒ rc1 & fa vẫn chạy (rc=$W_RC)"
}
winsuite "$WIN_SRC" real

echo "== mutants (mỗi mutant PHẢI bị bắt)"
CAUGHT=0; TOTAL=0
mut(){  # name which(gate|bq|nb2|wrap|fa|win) sed_expr
  local name="$1" which="$2" expr="$3" src dst
  case "$which" in gate|bq|nb2) src="$GATE_SRC";; wrap) src="$WRAP_SRC";; fa) src="$FA_SRC";; win) src="$WIN_SRC";; esac
  dst="$TMP/mut_$name.sh"; sed -E "$expr" "$src" > "$dst"; chmod +x "$dst"
  if cmp -s "$src" "$dst"; then bad "mutant $name: sed không đổi gì (mutant vô hiệu)"; return; fi
  TOTAL=$((TOTAL+1)); local before=$FAIL caught=0 out
  case "$which" in
    gate) out="$(suite "$dst" 2>&1)"; grep -q '  FAIL:' <<<"$out" && caught=1 ;;
    bq)   out="$(bqsuite "$dst" 2>&1)"; grep -q '  FAIL:' <<<"$out" && caught=1 ;;
    nb2)  out="$(nb2 "$dst" 2>&1)"; grep -q '  FAIL:' <<<"$out" && caught=1 ;;
    wrap) cp "$GATE_SRC" "$TMP/gate_under_test.sh"; wrap "$dst" "1066,343,310,x,y"; { [ -e "$TMP/hist_called" ] || [ "$W_RC" -ne 3 ]; } && caught=1 ;;
    fa)   cp "$GATE_SRC" "$TMP/gate_under_test.sh"; fawrap "$dst" "1066,343,310,x,y"; { [ -e "$TMP/fa_called" ] || [ "$W_RC" -ne 3 ]; } && caught=1 ;;
    win)  out="$(winsuite "$dst" m 2>&1)"; grep -q '  FAIL:' <<<"$out" && caught=1 ;;
  esac
  FAIL=$before
  [ "$caught" -eq 1 ] && { CAUGHT=$((CAUGHT+1)); echo "  caught $name"; } || bad "mutant $name SỐNG"
}
mut M1-n-cmp-flipped       gate 's/if nd < min_d/if nd > min_d/'
mut M2-cov-cmp-flipped     gate 's/if cov < min_c/if cov > min_c/'
mut M3-univ-cmp-flipped    gate 's/if nu < min_u/if nu > min_u/'
mut M4-no-error-branch     gate 's/raw\.startswith\("ERROR:"\)/False/'
mut M5-fail-exit0          gate 's/^exit 3$/exit 0/'
mut M6-no-state-clear      gate 's/^  rm -f "\$STATE"$/  :/'
mut M7-dedupe-inverted     gate 's/!= "\$TODAY"/== "$TODAY"/'
mut M8-thresh-1251         gate 's/GATE_MIN_DISTINCT:-1250/GATE_MIN_DISTINCT:-1251/'
mut M9-thresh-1000         gate 's/GATE_MIN_DISTINCT:-1250/GATE_MIN_DISTINCT:-1000/'
mut M10-cov-thresh-090     gate 's/GATE_MIN_COV:-0\.98/GATE_MIN_COV:-0.90/'
mut M11-univ-thresh-200    gate 's/GATE_MIN_UNIVERSE:-300/GATE_MIN_UNIVERSE:-200/'
mut M12-univ-cond-removed  gate 's/if nu < min_u: bad/if False: bad/'
mut M13-state-before-notify gate 's/then$/then :/;s/^  if "\$NOTIFY"/  if true || "$NOTIFY"/'
mut W1-gate-bypassed       wrap 's/\|\| exit 3$/|| true/'
mut W2-gate-removed        wrap 's/^"\$\{FA8L_GATE_CMD:-.*$/true/'
mut B1-rc-cond-dropped     bq   's/\[ "\$_rc" -eq 0 \] && //'
mut B2-header-check-dropped bq  's/ && \[ "\$\(printf .%s\\n. "\$_out" \| head -n1\)" = "n_distinct[^]]*\]//'
mut B3-stderr-merged       bq   's/2>"\$_errf"\)"/2>\&1)"/'
mut B4-timeout-removed     bq   's/timeout "\$\{GATE_BQ_TIMEOUT:-180\}" //'
mut N1-empty-verdict-unchecked nb2 's/^if \[ -z "\$VERDICT" \]; then/if false; then/'
mut F1-fa-gate-bypassed    fa   's/\|\| exit 3$/|| true/'
mut F2-fa-gate-removed     fa   's/^"\$\{FA8L_GATE_CMD:-.*$/true/'
mut R2a-rc3-cmp-changed    win  's/-eq 3 \]/-eq 4 ]/'
mut R2b-rc3-skip-removed   win  's/^  exit 3$/  :/'
echo "mutants caught: $CAUGHT/$TOTAL"
[ "$CAUGHT" -eq "$TOTAL" ] || FAIL=$((FAIL+1))
echo "assertions ok=$PASS fail=$FAIL"
[ "$FAIL" -eq 0 ]
