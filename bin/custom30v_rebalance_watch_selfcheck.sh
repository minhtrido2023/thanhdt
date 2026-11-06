#!/usr/bin/env bash
# Selfcheck custom30v_rebalance_watch.sh: không WARN giả khi hôm nay <= phiên đầu >= ngày 5 (D).
# Stub bq/date/notify trong sandbox tạm; chạy dưới TZ lạ để chắc không phụ thuộc TZ máy.
set -uo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/bin/custom30v_rebalance_watch.sh"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
mkdir -p "$T/root/bin" "$T/stub"
cp "$SRC" "$T/root/bin/"
cat > "$T/root/bin/notify_thread.sh" <<'EOS'
#!/usr/bin/env bash
echo "$1" >> "$NOTIFY_LOG"
EOS
cat > "$T/stub/date" <<'EOS'
#!/usr/bin/env bash
echo "$FAKE_TODAY"
EOS
cat > "$T/stub/bq" <<'EOS'
#!/usr/bin/env bash
q="${*: -1}"
case "$q" in
  *"MAX(rebal_date)"*) printf 'f0_\n%s\n' "$FAKE_MAX_REBAL" ;;
  *"MIN(t.time)"*)     printf 'f0_\n%s\n' "$FAKE_FIRST_TDAY" ;;
esac
EOS
chmod +x "$T"/root/bin/*.sh "$T"/stub/*
FAIL=0
run() { # name today max_rebal first_tday expect_notify(0/1) expect_rc [pre_streak]
  local name="$1" today="$2" maxr="$3" ftd="$4" want_n="$5" want_rc="$6" pre="${7:-0}"
  rm -rf "$T/root/state"; mkdir -p "$T/root/state"
  echo "{\"streak\": $pre, \"last_bad_date\": \"2026-11-04\", \"last_expected_trigger\": \"2026-11-05\"}" > "$T/root/state/custom30v_rebalance_streak.json"
  : > "$T/notify.log"
  env TZ=Pacific/Kiritimati MIKE_C30V_WATCH_BQ="$T/stub/bq" PATH="$T/stub:$PATH" NOTIFY_LOG="$T/notify.log" FAKE_TODAY="$today" \
      FAKE_MAX_REBAL="$maxr" FAKE_FIRST_TDAY="$ftd" bash "$T/root/bin/custom30v_rebalance_watch.sh" >/dev/null 2>"$T/err.log"
  local rc=$? n; n=$(wc -l < "$T/notify.log")
  local ok=0; [ "$rc" = "$want_rc" ] || ok=1
  if [ "$want_n" = 0 ]; then [ "$n" = 0 ] || ok=1; else [ "$n" -ge 1 ] || ok=1; fi
  if [ "$ok" = 0 ]; then
    echo "PASS $name"; else echo "FAIL $name (rc=$rc want=$want_rc notify=$n want=$want_n)"; FAIL=$((FAIL+1)); fi
}
run "ngày D (05/11), bảng cũ -> im lặng (ca gốc)"        2026-11-05 2026-08-05 2026-11-05 0 0
run "D chưa có trong lịch BQ -> im lặng"                 2026-11-05 2026-08-05 ""         0 0
run "phiên kế sau D, đã nhích -> khoẻ"                    2026-11-06 2026-11-05 2026-11-05 0 0
run "phiên kế sau D, bảng vẫn cũ -> WARN (bắt lỗi thật)"  2026-11-06 2026-08-05 2026-11-05 1 1
run "2 ngày liền cũ -> RED"                               2026-11-09 2026-08-05 2026-11-05 1 1 1
run "5th rơi T7: D=T2 09/11; hôm nay T2, cũ -> im lặng"   2026-11-09 2026-08-05 2026-11-09 0 0
run "5th rơi T7: D=T2; hôm nay T3, cũ -> WARN"            2026-11-10 2026-08-05 2026-11-09 1 1
[ "${DEBUG:-0}" = 1 ] && { cat "$T/notify.log" "$T/err.log"; }
echo "fails=$FAIL"; exit $((FAIL>0))
