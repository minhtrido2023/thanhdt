#!/usr/bin/env bash
# vendor_mismatch_alert_selfcheck.sh — bộ hồi quy cho `bin/vendor_mismatch_alert.sh`.
#
# VÌ SAO cần (arch-review vòng 1, W3): 88 dòng bash MỚI đứng giữa cổng và USER — nó parse marker,
# ghi state de-dup, và bắn HAI side-effect ra NGOÀI (bus + Discord). Hỏng ở đây không biểu hiện
# thành lỗi: nó biểu hiện thành IM LẶNG, đúng thứ script này sinh ra để chặn.
#
# CÁCH TEST (mấu chốt — KHÔNG copy logic): dựng sandbox `$TMP/mike/bin/` rồi SYMLINK chính
# script thật vào đó. `ROOT=dirname($BASH_SOURCE)/..` ⇒ ROOT = sandbox ⇒ state/ và 2 lời gọi
# `$ROOT/bin/{append_event,notify_thread}.sh` đều rơi vào STUB trong sandbox. Chạy đúng code
# production, KHÔNG monkeypatch, KHÔNG post thật. Sửa script mà quên sửa test ⇒ test chạy trên
# code mới, không có chuyện test và production trôi khỏi nhau.
#
# Stub điều khiển bằng env: SC_NOTIFY_RC / SC_APPEND_RC (mặc định 0), ghi lại lời gọi vào
# $SC_CALLLOG để assert "có gọi / không gọi".
#
#   bash mike/bin/vendor_mismatch_alert_selfcheck.sh                 # đủ bộ (ca + mutation), ~3s
#   bash mike/bin/vendor_mismatch_alert_selfcheck.sh --no-mutations  # chỉ bộ ca
set -uo pipefail

REAL_BIN="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# SC_TARGET_SRC: chạy TRỌN bộ ca lên một bản MUTANT thay vì bản thật. Đây là cách mutation test
# ở cuối file chứng minh "mutant bị giết bằng ASSERTION CÓ TÊN" — nó tái chạy chính file này.
SRC="${SC_TARGET_SRC:-$REAL_BIN/vendor_mismatch_alert.sh}"
[ -f "$SRC" ] || { echo "FATAL: không thấy $SRC"; exit 1; }

# Mutation BẬT MẶC ĐỊNH: `run_selfchecks.sh` tự dò `*selfcheck*.sh` và chạy KHÔNG THAM SỐ —
# để mutation sau một cờ opt-in là nó không bao giờ chạy trong lượt tuần. Cả bộ ~3s nên không
# có lý do đánh đổi. Lượt CON (chạy bộ ca lên mutant) tự tắt nhờ SC_TARGET_SRC — chống đệ quy.
RUN_MUTATIONS=1
[ -n "${SC_TARGET_SRC:-}" ] && RUN_MUTATIONS=0
[ "${1:-}" = "--no-mutations" ] && RUN_MUTATIONS=0

PASS=0; FAIL=0
ok()   { PASS=$((PASS+1)); printf '  ✓ %s\n' "$1"; }
bad()  { FAIL=$((FAIL+1)); printf '  ✗ %s\n     mong: %s\n     thật: %s\n' "$1" "$2" "$3"; }
check() { # check <tên> <mong> <thật>
  if [ "$2" = "$3" ]; then ok "$1"; else bad "$1" "$2" "$3"; fi
}

MARKER_PUB='VENDOR_MISMATCH_ALERT|SpaceX|VCB|2026-09-11|1600|1450|1'
MARKER_NOPUB='VENDOR_MISMATCH_ALERT|ZaloPay|MBB|2026-09-11|900|820|0'

# make_sandbox <script_path_to_link_or_copy>  → in ra đường dẫn sandbox
make_sandbox() {
  local target="$1" sb
  sb="$(mktemp -d)"
  mkdir -p "$sb/mike/bin" "$sb/mike/state"
  ln -s "$target" "$sb/mike/bin/vendor_mismatch_alert.sh"
  for n in append_event.sh notify_thread.sh; do
    cat > "$sb/mike/bin/$n" <<STUB
#!/usr/bin/env bash
echo "$n \$*" >> "\$SC_CALLLOG"
if [ "$n" = "notify_thread.sh" ]; then
  rc="\${SC_NOTIFY_RC:-0}"
  [ "\$rc" != "0" ] && echo "ccdb /api/notify: HTTP 502 Bad Gateway (stub)" >&2
else
  rc="\${SC_APPEND_RC:-0}"
  [ "\$rc" != "0" ] && echo "append_event: bus/events.jsonl read-only (stub)" >&2
fi
[ "\$rc" = "0" ] && echo "[stub $n ok]"
exit "\$rc"
STUB
    chmod +x "$sb/mike/bin/$n"
  done
  # Shim `python3` trên PATH: khi SC_KILL_MIDWRITE=1, GIẾT tiến trình ĐÚNG lúc đã ghi dở nội dung
  # nhưng CHƯA `os.replace` — mô phỏng kill thật, không monkeypatch code sản xuất. Chỉ bắt đúng
  # khối GHI STATE (nhận diện bằng `json.dump` + `TODAY`; khối PAYLOAD dùng json.dumpS và không
  # có TODAY nên không dính).
  mkdir -p "$sb/shim"
  cat > "$sb/shim/python3" <<'SHIM'
#!/usr/bin/env bash
REAL_PY="$(PATH="${SC_REAL_PATH}" command -v python3)"
if [ "${SC_KILL_MIDWRITE:-0}" = "1" ] && [ "${1:-}" = "-c" ] \
   && [[ "${2:-}" == *"json.dump"* ]] && [[ "${2:-}" == *"TODAY"* ]]; then
  exec "$REAL_PY" -c "import json, os
_dumps = json.dumps
def _kill_mid(obj, fp, **kw):
    fp.write(_dumps(obj, indent=2, ensure_ascii=False)[:9])
    fp.flush()
    os._exit(137)
json.dump = _kill_mid
$2"
fi
exec "$REAL_PY" "$@"
SHIM
  chmod +x "$sb/shim/python3"
  # Shim `date`: chỉ bật khi SC_FAKE_DATE=1 (R2, arch-review vòng 3b) — trả ngày CỐ ĐỊNH theo $TZ
  # nhận được thay vì đồng hồ thật, để test mốc ICT không lệ thuộc giờ chạy thật (chạy lúc nào
  # trong ngày cũng ra cùng kết quả — không phụ thuộc khoảng lệch múi giờ trùng ngày lịch tình cờ).
  # Script sản xuất gọi `TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d` (dòng neo TZ tường minh) — override
  # đó thắng TZ môi trường ngoài nên shim thấy đúng "Asia/Ho_Chi_Minh"; ai lỡ bỏ tiền tố TZ= đi thì
  # shim thấy TZ AMBIENT (test set = Pacific/Kiritimati) và trả ngày KHÁC — đó là cách
  # MUTATION-GUARD vendor_alert_ict_anchor bắt được hồi quy.
  cat > "$sb/shim/date" <<'SHIM'
#!/usr/bin/env bash
REAL_DATE="$(PATH="${SC_REAL_PATH}" command -v date)"
if [ "${SC_FAKE_DATE:-0}" = "1" ]; then
  if [ "${TZ:-}" = "Asia/Ho_Chi_Minh" ]; then
    echo "2026-09-24"
  else
    echo "2026-09-25"
  fi
  exit 0
fi
exec "$REAL_DATE" "$@"
SHIM
  chmod +x "$sb/shim/date"
  printf '%s' "$sb"
}

# run_case in ra: "<rc>|<state_json_1_dòng>|<có_gọi_notify>|<stderr>"
# run_case <sandbox> <markers> [env assignments...]
STATE_REL="mike/state/vendor_mismatch_alerted.json"

# ---------------------------------------------------------------- ca chính
section() { printf '\n%s\n' "$1"; }

run_one() { # run_one <sb> <markers> ; đặt biến RC/STATE_TXT/CALLS/ERRTXT
  local sb="$1" markers="$2"
  local errf="$sb/stderr.txt"
  export SC_CALLLOG="$sb/calls.log"
  : > "$SC_CALLLOG"
  export SC_REAL_PATH="${SC_REAL_PATH:-$PATH}"
  local _oldpath="$PATH"
  export PATH="$sb/shim:$SC_REAL_PATH"     # shim phải phủ CẢ script lẫn python3 nó gọi
  printf '%s\n' "$markers" | "$sb/mike/bin/vendor_mismatch_alert.sh" \
      "spacex_daily_report_2026-09-11.md" "trading_report" >"$sb/stdout.txt" 2>"$errf"
  RC=$?
  export PATH="$_oldpath"
  ERRTXT="$(cat "$errf")"
  CALLS="$(cat "$SC_CALLLOG")"
  if [ -f "$sb/$STATE_REL" ]; then STATE_TXT="$(tr -d '\n ' < "$sb/$STATE_REL")"; else STATE_TXT="<no-file>"; fi
}

section "CA 1 — notify THÀNH CÔNG ⇒ state CÓ ghi, exit 10"
SB1="$(make_sandbox "$SRC")"
( export SC_NOTIFY_RC=0 SC_APPEND_RC=0; run_one "$SB1" "$MARKER_PUB"
  check "exit 10" "10" "$RC"
  case "$CALLS" in *notify_thread.sh*) ok "có gọi notify_thread.sh" ;; *) bad "có gọi notify_thread.sh" "gọi" "$CALLS" ;; esac
  case "$CALLS" in *append_event.sh*) ok "có ghi bus" ;; *) bad "có ghi bus" "gọi" "$CALLS" ;; esac
  case "$STATE_TXT" in *spacex_daily_report_2026-09-11.md*) ok "state CÓ ghi de-dup cho file" ;; *) bad "state CÓ ghi de-dup cho file" "có key" "$STATE_TXT" ;; esac
  # ghi nguyên tử: không để lại rác .tmp
  n_tmp=$(find "$SB1/mike/state" -name '.vendor_mismatch_alerted.*.tmp' | wc -l)
  check "không sót file .tmp (ghi nguyên tử)" "0" "$n_tmp"
  # lượt 2 cùng ngày ⇒ de-dup, KHÔNG gọi notify lần nữa
  run_one "$SB1" "$MARKER_PUB"
  check "lượt 2 cùng ngày vẫn exit 10 (de-dup)" "10" "$RC"
  case "$CALLS" in *notify_thread.sh*) bad "lượt 2 KHÔNG gọi lại notify" "không gọi" "$CALLS" ;; *) ok "lượt 2 KHÔNG gọi lại notify (de-dup thật)" ;; esac
  echo "$PASS|$FAIL" > "$SB1/tally" )
read -r PASS FAIL < <(tr '|' ' ' < "$SB1/tally")

section "CA 2 — notify THẤT BẠI ⇒ state KHÔNG ghi + IN LỖI THẬT"
SB2="$(make_sandbox "$SRC")"
( export SC_NOTIFY_RC=7 SC_APPEND_RC=0; run_one "$SB2" "$MARKER_PUB"
  check "vẫn exit 10 (lệch nguồn CÓ thật, caller dựa vào để quy nguyên nhân)" "10" "$RC"
  # ĐÂY là assertion mutation phải giết: ghi state khi gửi hỏng = mất cảnh báo vĩnh viễn.
  # MUTATION-GUARD vendor_alert_no_state_on_notify_fail
  case "$STATE_TXT" in
    *spacex_daily_report_2026-09-11.md*) bad "MUTATION-GUARD vendor_alert_no_state_on_notify_fail: state KHÔNG được ghi khi notify hỏng" "không có key (lượt sau còn thử lại)" "$STATE_TXT" ;;
    *) ok "MUTATION-GUARD vendor_alert_no_state_on_notify_fail: state KHÔNG ghi ⇒ lượt sau thử lại" ;;
  esac
  # §29: phải in LỖI THẬT của kênh, không phải một câu đoán
  case "$ERRTXT" in *"HTTP 502 Bad Gateway"*) ok "stderr mang LỖI THẬT của notify (§29)" ;; *) bad "stderr mang LỖI THẬT của notify (§29)" "chứa 'HTTP 502 Bad Gateway'" "$ERRTXT" ;; esac
  case "$ERRTXT" in *"notify_thread.sh THAT BAI"*) ok "stderr nói rõ kênh nào hỏng" ;; *) bad "stderr nói rõ kênh nào hỏng" "chứa 'notify_thread.sh THAT BAI'" "$ERRTXT" ;; esac
  # lượt kế tiếp PHẢI thử lại (chính là điều state-không-ghi mua được)
  export SC_NOTIFY_RC=0; run_one "$SB2" "$MARKER_PUB"
  case "$CALLS" in *notify_thread.sh*) ok "lượt sau THỬ LẠI notify (không bị de-dup khoá)" ;; *) bad "lượt sau THỬ LẠI notify" "gọi" "$CALLS" ;; esac
  case "$STATE_TXT" in *spacex_daily_report_2026-09-11.md*) ok "lượt sau gửi được thì mới ghi state" ;; *) bad "lượt sau gửi được thì mới ghi state" "có key" "$STATE_TXT" ;; esac
  echo "$PASS|$FAIL" > "$SB2/tally" )
read -r PASS FAIL < <(tr '|' ' ' < "$SB2/tally")

section "CA 2b — bus hỏng nhưng Discord SỐNG ⇒ vẫn cảnh báo được (bus là kênh phụ)"
SB2B="$(make_sandbox "$SRC")"
( export SC_NOTIFY_RC=0 SC_APPEND_RC=3; run_one "$SB2B" "$MARKER_PUB"
  check "exit 10" "10" "$RC"
  case "$CALLS" in *notify_thread.sh*) ok "bus hỏng KHÔNG chặn đường tới user" ;; *) bad "bus hỏng KHÔNG chặn đường tới user" "vẫn gọi notify" "$CALLS" ;; esac
  case "$STATE_TXT" in *spacex_daily_report*) ok "state vẫn ghi (Discord mới là điều kiện)" ;; *) bad "state vẫn ghi" "có key" "$STATE_TXT" ;; esac
  case "$ERRTXT" in *"read-only (stub)"*) ok "stderr mang LỖI THẬT của bus (§29)" ;; *) bad "stderr mang LỖI THẬT của bus (§29)" "chứa lỗi stub" "$ERRTXT" ;; esac
  echo "$PASS|$FAIL" > "$SB2B/tally" )
read -r PASS FAIL < <(tr '|' ' ' < "$SB2B/tally")

section "CA 3 — state file CỤT/hỏng ⇒ VẪN cảnh báo được, không chết im lặng"
SB3="$(make_sandbox "$SRC")"
printf '{"spacex_daily_report_2026-09-11.md": "2026-0' > "$SB3/$STATE_REL"   # JSON cụt đúng kiểu kill giữa lúc ghi
( export SC_NOTIFY_RC=0 SC_APPEND_RC=0; run_one "$SB3" "$MARKER_PUB"
  check "exit 10" "10" "$RC"
  case "$CALLS" in *notify_thread.sh*) ok "state hỏng KHÔNG làm câm cảnh báo" ;; *) bad "state hỏng KHÔNG làm câm cảnh báo" "vẫn gọi notify" "$CALLS" ;; esac
  case "$ERRTXT" in *"KHONG doc duoc state de-dup"*) ok "nêu rõ state hỏng (không im lặng)" ;; *) bad "nêu rõ state hỏng" "chứa 'KHONG doc duoc state de-dup'" "$ERRTXT" ;; esac
  # §29: phải trích lỗi parser THẬT, không đoán
  case "$ERRTXT" in *JSONDecodeError*|*"Expecting"*) ok "trích lỗi parser THẬT (§29), không đoán nguyên nhân" ;; *) bad "trích lỗi parser THẬT (§29)" "tên exception/thông điệp json" "$ERRTXT" ;; esac
  # và tự chữa lành: file sau lượt chạy phải là JSON hợp lệ
  if python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$SB3/$STATE_REL" 2>/dev/null; then
    ok "state được dựng lại thành JSON hợp lệ"
  else bad "state được dựng lại thành JSON hợp lệ" "json hợp lệ" "$(cat "$SB3/$STATE_REL")"; fi
  echo "$PASS|$FAIL" > "$SB3/tally" )
read -r PASS FAIL < <(tr '|' ' ' < "$SB3/tally")

section "CA 4 — KHÔNG có marker ⇒ không post gì, không ghi state, exit 0"
SB4="$(make_sandbox "$SRC")"
( export SC_NOTIFY_RC=0 SC_APPEND_RC=0
  run_one "$SB4" "Delivery COMPLETE — khong co lech nguon nao
report_return_gate: PASS"
  check "exit 0" "0" "$RC"
  check "KHÔNG gọi side-effect nào" "" "$CALLS"
  check "KHÔNG tạo state" "<no-file>" "$STATE_TXT"
  echo "$PASS|$FAIL" > "$SB4/tally" )
read -r PASS FAIL < <(tr '|' ' ' < "$SB4/tally")

section "CA 5 — marker KHÔNG công bố (published=0) ⇒ vẫn cảnh báo (ca cổng rc=0, không kênh nào khác kêu)"
SB5="$(make_sandbox "$SRC")"
( export SC_NOTIFY_RC=0 SC_APPEND_RC=0; run_one "$SB5" "$MARKER_NOPUB"
  check "exit 10" "10" "$RC"
  case "$CALLS" in *notify_thread.sh*) ok "vẫn gửi Discord dù báo cáo KHÔNG bị chặn" ;; *) bad "vẫn gửi Discord" "gọi notify" "$CALLS" ;; esac
  case "$CALLS" in *'"blocked_report":0'*) ok "payload bus ghi blocked_report=0" ;; *) bad "payload bus ghi blocked_report=0" "blocked_report:0" "$CALLS" ;; esac
  echo "$PASS|$FAIL" > "$SB5/tally" )
read -r PASS FAIL < <(tr '|' ' ' < "$SB5/tally")

section "CA 6 — --dry-run ⇒ exit 10, KHÔNG side-effect, KHÔNG state"
SB6="$(make_sandbox "$SRC")"
export SC_CALLLOG="$SB6/calls.log"; : > "$SC_CALLLOG"
DRY_OUT="$(printf '%s\n' "$MARKER_PUB" | SC_NOTIFY_RC=0 "$SB6/mike/bin/vendor_mismatch_alert.sh" \
  "spacex_daily_report_2026-09-11.md" "trading_report" --dry-run 2>&1)"; DRY_RC=$?
check "exit 10" "10" "$DRY_RC"
check "KHÔNG side-effect" "" "$(cat "$SC_CALLLOG")"
if [ -f "$SB6/$STATE_REL" ]; then bad "KHÔNG tạo state" "không có file" "có file"; else ok "KHÔNG tạo state"; fi
case "$DRY_OUT" in *"[dry-run]"*VCB*) ok "dry-run in chi tiết mã" ;; *) bad "dry-run in chi tiết mã" "chứa VCB" "$DRY_OUT" ;; esac

section "CA 7 — KILL giữa lúc ghi state ⇒ state CŨ còn NGUYÊN VẸN (ghi nguyên tử, §5)"
SB7="$(make_sandbox "$SRC")"
printf '{\n  "old_report_2026-09-01.md": "2026-09-01"\n}\n' > "$SB7/$STATE_REL"
( export SC_NOTIFY_RC=0 SC_APPEND_RC=0 SC_KILL_MIDWRITE=1
  run_one "$SB7" "$MARKER_PUB"
  case "$CALLS" in *notify_thread.sh*) ok "đã gửi cảnh báo trước khi bị kill" ;; *) bad "đã gửi cảnh báo trước khi bị kill" "gọi notify" "$CALLS" ;; esac
  # MUTATION-GUARD vendor_alert_atomic_state_write — ghi thẳng `open(path,'w')` sẽ CẮT CỤT
  # chính file state này, lượt sau `json.load` vấp; ghi tmp+os.replace thì bản cũ còn nguyên.
  if python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$SB7/$STATE_REL" 2>/dev/null; then
    ok "MUTATION-GUARD vendor_alert_atomic_state_write: state vẫn là JSON HỢP LỆ sau kill"
  else
    bad "MUTATION-GUARD vendor_alert_atomic_state_write: state vẫn là JSON HỢP LỆ sau kill" \
        "json hợp lệ" "$(cat "$SB7/$STATE_REL")"
  fi
  if grep -q 'old_report_2026-09-01.md' "$SB7/$STATE_REL"; then
    ok "MUTATION-GUARD vendor_alert_atomic_state_write: nội dung CŨ không mất"
  else
    bad "MUTATION-GUARD vendor_alert_atomic_state_write: nội dung CŨ không mất" \
        "còn key old_report_2026-09-01.md" "$(cat "$SB7/$STATE_REL")"
  fi
  echo "$PASS|$FAIL" > "$SB7/tally" )
read -r PASS FAIL < <(tr '|' ' ' < "$SB7/tally")

section "CA 8 — sai số đối số (0/1) ⇒ rc=2 + usage ra stderr, KHÔNG post gì (dòng 18/31-34)"
SB8="$(make_sandbox "$SRC")"
( for nargs in 0 1; do
    export SC_CALLLOG="$SB8/calls_$nargs.log"; : > "$SC_CALLLOG"
    case "$nargs" in
      0) OUT_ERR="$("$SB8/mike/bin/vendor_mismatch_alert.sh" 2>&1 >/dev/null </dev/null)"; RC8=$? ;;
      1) OUT_ERR="$("$SB8/mike/bin/vendor_mismatch_alert.sh" "only_one_arg" 2>&1 >/dev/null </dev/null)"; RC8=$? ;;
    esac
    check "rc=2 khi gọi với $nargs đối số" "2" "$RC8"
    case "$OUT_ERR" in *"Usage:"*) ok "in usage ra stderr ($nargs đối số)" ;; *) bad "in usage ra stderr ($nargs đối số)" "chứa 'Usage:'" "$OUT_ERR" ;; esac
    check "KHÔNG gọi side-effect nào ($nargs đối số)" "" "$(cat "$SC_CALLLOG")"
  done
  echo "$PASS|$FAIL" > "$SB8/tally" )
read -r PASS FAIL < <(tr '|' ' ' < "$SB8/tally")

section "CA 9 — mốc ICT neo CỨNG bất kể TZ môi trường gọi script (MUTATION-GUARD vendor_alert_ict_anchor)"
SB9="$(make_sandbox "$SRC")"
( export SC_NOTIFY_RC=0 SC_APPEND_RC=0 SC_FAKE_DATE=1 TZ='Pacific/Kiritimati'
  run_one "$SB9" "$MARKER_PUB"
  check "exit 10" "10" "$RC"
  case "$STATE_TXT" in
    *'"spacex_daily_report_2026-09-11.md":"2026-09-24"'*)
      ok "MUTATION-GUARD vendor_alert_ict_anchor: key = ngày ICT (2026-09-24), không phải ngày theo TZ môi trường (2026-09-25)" ;;
    *)
      bad "MUTATION-GUARD vendor_alert_ict_anchor: key = ngày ICT (2026-09-24), không phải ngày theo TZ môi trường (2026-09-25)" \
          '"...":"2026-09-24"' "$STATE_TXT" ;;
  esac
  echo "$PASS|$FAIL" > "$SB9/tally" )
read -r PASS FAIL < <(tr '|' ' ' < "$SB9/tally")

section "CA 10 — RẼ theo mã lý do (VENDOR_MISMATCH_REASON, arch-review D1b R1): câu Discord + Việc cần làm PHẢI khác nhau theo reason, không phát một câu cố định"
# Ba mã lý do trong CÙNG một lượt gọi (đúng dạng report_return_gate.py thật in ra: ALERT rồi
# REASON nối liền cho mỗi mã) — STK=stock_leg_ignored, CSH=cash_mismatch, UNK=REASON marker vắng
# mặt hẳn (mô phỏng caller cũ/hỏng, giống hệt ca fail-closed "unknown" phía report_return_gate.py).
MARKER_REASONS='VENDOR_MISMATCH_ALERT|SpaceX|STK|2026-09-24|1000|0|1
VENDOR_MISMATCH_REASON|SpaceX|STK|2026-09-24|stock_leg_ignored|0.2604
VENDOR_MISMATCH_ALERT|SpaceX|CSH|2026-09-11|1600|1450|1
VENDOR_MISMATCH_REASON|SpaceX|CSH|2026-09-11|cash_mismatch|0.0000
VENDOR_MISMATCH_ALERT|SpaceX|UNK|2026-09-12|900|820|1'
SB10="$(make_sandbox "$SRC")"
( export SC_NOTIFY_RC=0 SC_APPEND_RC=0; run_one "$SB10" "$MARKER_REASONS"
  check "exit 10" "10" "$RC"
  case "$CALLS" in
    *"THUẦN CỔ PHIẾU"*) ok "STK (stock_leg_ignored): câu nói ĐÚNG 'THUẦN CỔ PHIẾU', không phải 'hai nguồn bất đồng'" ;;
    *) bad "STK (stock_leg_ignored): câu nói ĐÚNG 'THUẦN CỔ PHIẾU'" "chứa 'THUẦN CỔ PHIẾU'" "$CALLS" ;;
  esac
  case "$CALLS" in
    *"Nghi giá rơi chia tách"*) ok "STK: Việc cần làm có mục 'Nghi giá rơi chia tách' (không phải 'đối soát cho khớp lại')" ;;
    *) bad "STK: Việc cần làm có mục 'Nghi giá rơi chia tách'" "chứa 'Nghi giá rơi chia tách'" "$CALLS" ;;
  esac
  case "$CALLS" in
    *"CSH"*"hai nguồn bất đồng số cổ tức"*) ok "CSH (cash_mismatch): câu nói ĐÚNG 'hai nguồn bất đồng số cổ tức'" ;;
    *) bad "CSH (cash_mismatch): câu nói ĐÚNG 'hai nguồn bất đồng số cổ tức'" "chứa 'hai nguồn bất đồng số cổ tức'" "$CALLS" ;;
  esac
  case "$CALLS" in
    *"Bất đồng số cổ tức"*) ok "CSH: Việc cần làm có mục 'Bất đồng số cổ tức' (đối soát Winston)" ;;
    *) bad "CSH: Việc cần làm có mục 'Bất đồng số cổ tức'" "chứa 'Bất đồng số cổ tức'" "$CALLS" ;;
  esac
  case "$CALLS" in
    *"UNK"*"KHÔNG xác định được mã lý do"*) ok "UNK (REASON vắng mặt): câu nói THẲNG không xác định được, không đoán" ;;
    *) bad "UNK (REASON vắng mặt): câu nói THẲNG không xác định được" "chứa 'KHÔNG xác định được mã lý do'" "$CALLS" ;;
  esac
  case "$CALLS" in
    *"Không xác định được mã lý do"*"kiểm thủ công"*) ok "UNK: Việc cần làm nói 'kiểm thủ công', KHÔNG suy đoán nguyên nhân" ;;
    *) bad "UNK: Việc cần làm nói 'kiểm thủ công'" "chứa 'Không xác định được mã lý do' + 'kiểm thủ công'" "$CALLS" ;;
  esac
  # MUTATION-GUARD chính: xoá dòng đọc REASON (hoặc gộp cả 3 mã vào MỘT câu cố định) sẽ làm CẢ BA
  # assertion trên rơi vào cùng 1 nhánh — bắt bằng việc BA câu-đặc-trưng phải XUẤT HIỆN ĐỒNG THỜI.
  if printf '%s' "$CALLS" | grep -qF "THUẦN CỔ PHIẾU" && printf '%s' "$CALLS" | grep -qF "hai nguồn bất đồng số cổ tức" && printf '%s' "$CALLS" | grep -qF "KHÔNG xác định được mã lý do"; then
    ok "MUTATION-GUARD vendor_alert_reason_routing: CẢ BA câu đặc trưng cùng có mặt — 3 mã lý do KHÔNG bị gộp thành 1 câu chung"
  else
    bad "MUTATION-GUARD vendor_alert_reason_routing: CẢ BA câu đặc trưng cùng có mặt — 3 mã lý do KHÔNG bị gộp thành 1 câu chung" \
        "cả 3 cụm từ" "$CALLS"
  fi
  echo "$PASS|$FAIL" > "$SB10/tally" )
read -r PASS FAIL < <(tr '|' ' ' < "$SB10/tally")

section "CA 11 — VENDOR_LOOKUP_FAILED, had_broker_cash=1 published=1 (arch-review vòng 4 R1(e) + vòng 5 R1-A/R1-B): sự kiện TỪNG là CASH_CONFIRMED, đang công bố ⇒ CHẶN thật"
# Ca THUẦN lookup_failed (không có mismatch nào khác trong lượt gọi) — trước bản vá R1(e) script
# chỉ grep VENDOR_MISMATCH_ALERT nên MARKERS rỗng ⇒ exit 0 câm lặng đúng lúc báo cáo đang bị CHẶN.
# had_broker_cash=1: per_share LÀ tiền broker thật (đúng ca sự kiện từng CASH_CONFIRMED).
MARKER_LOOKUP_ONLY='VENDOR_LOOKUP_FAILED|SpaceX|VPB|2026-09-23|1200|1|1'
SB11="$(make_sandbox "$SRC")"
( export SC_NOTIFY_RC=0 SC_APPEND_RC=0; run_one "$SB11" "$MARKER_LOOKUP_ONLY"
  check "exit 10 (thuần lookup_failed vẫn phải bắn cảnh báo)" "10" "$RC"
  case "$CALLS" in
    *"KHÔNG TRA ĐƯỢC nguồn vendor"*) ok "câu Discord nói ĐÚNG 'KHÔNG TRA ĐƯỢC nguồn vendor', không phải 'hai nguồn bất đồng'" ;;
    *) bad "câu Discord nói ĐÚNG 'KHÔNG TRA ĐƯỢC nguồn vendor'" "chứa 'KHÔNG TRA ĐƯỢC nguồn vendor'" "$CALLS" ;;
  esac
  case "$CALLS" in
    *"VENDOR LOOKUP THẤT BẠI"*) ok "tiêu đề riêng cho ca THUẦN lookup_failed (không phải 'LỆCH NGUỒN CỔ TỨC')" ;;
    *) bad "tiêu đề riêng cho ca THUẦN lookup_failed" "chứa 'VENDOR LOOKUP THẤT BẠI'" "$CALLS" ;;
  esac
  case "$CALLS" in
    *"chạy lại"*"report_return_gate.py"*) ok "Việc cần làm nói 'chạy lại report_return_gate.py' (rerun), không giao Winston đối soát số" ;;
    *) bad "Việc cần làm nói 'chạy lại report_return_gate.py'" "chứa 'chạy lại' + 'report_return_gate.py'" "$CALLS" ;;
  esac
  case "$CALLS" in
    *"hai nguồn bất đồng số cổ tức"*) bad "KHÔNG được phát câu 'hai nguồn bất đồng số cổ tức' cho ca lookup_failed" "không chứa" "$CALLS" ;;
    *) ok "KHÔNG phát nhầm câu 'hai nguồn bất đồng số cổ tức' của mismatch" ;;
  esac
  # R1-A: had_broker_cash=1 ⇒ câu phải khẳng định "broker đã giải" (per_share LÀ tiền thật).
  case "$CALLS" in
    *"broker đã giải 1,200đ/cp nhưng chưa đối soát chéo được"*)
      ok "R1-A: had_broker_cash=1 ⇒ câu 'broker đã giải Xđ/cp' (per_share là tiền broker thật)" ;;
    *) bad "R1-A: had_broker_cash=1 ⇒ câu 'broker đã giải Xđ/cp' (per_share là tiền broker thật)" \
        "chứa 'broker đã giải 1,200đ/cp nhưng chưa đối soát chéo được'" "$CALLS" ;;
  esac
  # R1-B: had_broker_cash=1 AND published=1 ⇒ BLOCKED thật, câu phải nói "báo cáo bị CHẶN".
  case "$CALLS" in
    *"mã này ĐANG công bố tỉ suất ⇒ báo cáo bị CHẶN"*)
      ok "R1-B: had_broker_cash=1 + published=1 ⇒ câu nói ĐÚNG 'báo cáo bị CHẶN'" ;;
    *) bad "R1-B: had_broker_cash=1 + published=1 ⇒ câu nói ĐÚNG 'báo cáo bị CHẶN'" \
        "chứa 'mã này ĐANG công bố tỉ suất ⇒ báo cáo bị CHẶN'" "$CALLS" ;;
  esac
  case "$CALLS" in
    *'"blocked_report":1'*) ok "R1-D: payload bus ghi blocked_report=1 đúng lúc report bị CHẶN" ;;
    *) bad "R1-D: payload bus ghi blocked_report=1" "chứa '\"blocked_report\":1'" "$CALLS" ;;
  esac
  echo "$PASS|$FAIL" > "$SB11/tally" )
read -r PASS FAIL < <(tr '|' ' ' < "$SB11/tally")

section "CA 11b — VENDOR_LOOKUP_FAILED, had_broker_cash=0 (arch-review vòng 5 R1-A/R1-B): per_share chỉ là ƯỚC LƯỢNG, KHÔNG mất số công bố ⇒ KHÔNG chặn dù published=1"
# Ca MBS thật (K1, dựng lại từ exp_vendor_mismatch/k1_v2_rerun.log): STOCK_CONFIRMED/unresolved,
# broker=4828.8 chỉ là ước lượng từ giá rơi (_scan_jumps) — CHƯA từng là CASH_CONFIRMED. published=1
# (mã ĐANG công bố tỉ suất) nhưng KHÔNG mất số nào ⇒ BLOCKED phải là 0, câu KHÔNG được nói "chặn".
MARKER_LOOKUP_NOCASH='VENDOR_LOOKUP_FAILED|SpaceX|MBS|2026-04-02|4829|0|1'
SB11B="$(make_sandbox "$SRC")"
( export SC_NOTIFY_RC=0 SC_APPEND_RC=0; run_one "$SB11B" "$MARKER_LOOKUP_NOCASH"
  check "exit 10 (vẫn phải bắn cảnh báo, kể cả không chặn)" "10" "$RC"
  case "$CALLS" in
    *"broker CHƯA giải được số nào (ước lượng từ giá rơi 4,829đ/cp, KHÔNG phải tiền broker thật)"*)
      ok "R1-A: had_broker_cash=0 ⇒ câu ĐÚNG 'broker CHƯA giải được số nào (ước lượng...)'" ;;
    *) bad "R1-A: had_broker_cash=0 ⇒ câu ĐÚNG 'broker CHƯA giải được số nào (ước lượng...)'" \
        "chứa 'broker CHƯA giải được số nào (ước lượng từ giá rơi 4,829đ/cp, KHÔNG phải tiền broker thật)'" "$CALLS" ;;
  esac
  case "$CALLS" in
    *"broker đã giải"*) bad "R1-A: KHÔNG được khẳng định 'broker đã giải' khi had_broker_cash=0" "không chứa 'broker đã giải'" "$CALLS" ;;
    *) ok "R1-A: KHÔNG khẳng định sai 'broker đã giải' cho số ước lượng" ;;
  esac
  case "$CALLS" in
    *"không mất số đã công bố (chưa từng là CASH_CONFIRMED), báo cáo vẫn gửi bình thường"*)
      ok "R1-B: had_broker_cash=0 ⇒ câu ĐÚNG 'không mất số đã công bố ... vẫn gửi bình thường'" ;;
    *) bad "R1-B: had_broker_cash=0 ⇒ câu ĐÚNG 'không mất số đã công bố ... vẫn gửi bình thường'" \
        "chứa 'không mất số đã công bố (chưa từng là CASH_CONFIRMED), báo cáo vẫn gửi bình thường'" "$CALLS" ;;
  esac
  case "$CALLS" in
    *"⇒ báo cáo bị CHẶN"*) bad "R1-B: KHÔNG được chặn khi had_broker_cash=0 (không mất số công bố)" "không chứa '⇒ báo cáo bị CHẶN'" "$CALLS" ;;
    *) ok "R1-B: KHÔNG chặn oan — per_share ước lượng chưa từng là tiền broker" ;;
  esac
  case "$CALLS" in
    *'"blocked_report":0'*) ok "payload bus ghi blocked_report=0 (published=1 nhưng had_broker_cash=0 ⇒ không chặn)" ;;
    *) bad "payload bus ghi blocked_report=0" "chứa '\"blocked_report\":0'" "$CALLS" ;;
  esac
  echo "$PASS|$FAIL" > "$SB11B/tally" )
read -r PASS FAIL < <(tr '|' ' ' < "$SB11B/tally")

section "CA 12 — MIX: mismatch (VCB) + lookup_failed (VPB) trong CÙNG lượt ⇒ CẢ HAI câu cùng có mặt, không đè lẫn nhau"
MARKER_MIX="VENDOR_MISMATCH_ALERT|SpaceX|VCB|2026-09-11|1600|1450|1
VENDOR_MISMATCH_REASON|SpaceX|VCB|2026-09-11|cash_mismatch|0.0000
VENDOR_LOOKUP_FAILED|SpaceX|VPB|2026-09-23|1200|1|0"
SB12="$(make_sandbox "$SRC")"
( export SC_NOTIFY_RC=0 SC_APPEND_RC=0; run_one "$SB12" "$MARKER_MIX"
  check "exit 10" "10" "$RC"
  case "$CALLS" in
    *"VCB"*"hai nguồn bất đồng số cổ tức"*) ok "VCB (mismatch) vẫn ra ĐÚNG câu cash_mismatch" ;;
    *) bad "VCB (mismatch) vẫn ra ĐÚNG câu cash_mismatch" "chứa 'VCB' + 'hai nguồn bất đồng số cổ tức'" "$CALLS" ;;
  esac
  case "$CALLS" in
    *"VPB"*"KHÔNG TRA ĐƯỢC nguồn vendor"*) ok "VPB (lookup_failed) vẫn ra ĐÚNG câu riêng, không bị VCB đè" ;;
    *) bad "VPB (lookup_failed) vẫn ra ĐÚNG câu riêng" "chứa 'VPB' + 'KHÔNG TRA ĐƯỢC nguồn vendor'" "$CALLS" ;;
  esac
  case "$CALLS" in
    *"Bất đồng số cổ tức"*"BQ lỗi hạ tầng"*) ok "Việc cần làm có CẢ HAI mục (đối soát Winston + rerun BQ), không mất mục nào" ;;
    *) bad "Việc cần làm có CẢ HAI mục" "chứa cả 'Bất đồng số cổ tức' và 'BQ lỗi hạ tầng'" "$CALLS" ;;
  esac
  # tiêu đề ca MIX phải là tiêu đề LỆCH NGUỒN chung (không phải tiêu đề riêng của ca THUẦN lookup_failed)
  case "$CALLS" in
    *"VENDOR LOOKUP THẤT BẠI"*) bad "ca MIX KHÔNG dùng tiêu đề riêng của ca THUẦN lookup_failed" "không chứa 'VENDOR LOOKUP THẤT BẠI'" "$CALLS" ;;
    *) ok "ca MIX dùng tiêu đề chung 'LỆCH NGUỒN CỔ TỨC' (đúng vì có cả 2 loại)" ;;
  esac
  echo "$PASS|$FAIL" > "$SB12/tally" )
read -r PASS FAIL < <(tr '|' ' ' < "$SB12/tally")

# ---------------------------------------------------------------- mutation
if [ "$RUN_MUTATIONS" -eq 1 ]; then
  # Mutation THẬT: dựng bản hỏng rồi chạy TRỌN bộ ca trên nó (SC_TARGET_SRC). Mutant "bị giết"
  # chỉ khi bộ ca trả FAIL Ở ĐÚNG assertion CÓ TÊN mong đợi — không nhận rc≠0 trơn (crash,
  # syntax error, hay ca khác fail đều KHÔNG tính là giết đúng chỗ).
  MUTDIR="$(mktemp -d)"
  trap 'rm -rf "$MUTDIR"' EXIT

  mutate() { # mutate <tên_mutant> <old_python_literal_file> ...; dùng python để thay chuỗi
    local name="$1" needle="$2" repl="$3"
    NEEDLE="$needle" REPL="$repl" python3 - "$SRC" "$MUTDIR/$name.sh" <<'PYM'
import io, os, sys
src = io.open(sys.argv[1], encoding="utf-8").read()
needle, repl = os.environ["NEEDLE"], os.environ["REPL"]
if needle not in src:
    sys.stderr.write("MUTATION khong ap duoc (nguon da doi) — sua selfcheck truoc:\n%s\n" % needle)
    sys.exit(3)
io.open(sys.argv[2], "w", encoding="utf-8").write(src.replace(needle, repl, 1))
PYM
    chmod +x "$MUTDIR/$name.sh" 2>/dev/null
  }

  kill_check() { # kill_check <tên> <mô tả> <assertion phải FAIL>
    local name="$1" desc="$2" guard="$3" out rc
    if [ ! -f "$MUTDIR/$name.sh" ]; then bad "MUTANT $name: dựng được bản hỏng" "có file" "không áp được needle"; return; fi
    out="$(SC_TARGET_SRC="$MUTDIR/$name.sh" bash "${BASH_SOURCE[0]}" 2>&1)"; rc=$?
    if [ "$rc" -eq 0 ]; then
      bad "MUTANT $name ($desc) phải BỊ GIẾT" "bộ ca FAIL" "bộ ca vẫn PASS — mutant SỐNG SÓT"
      return
    fi
    if printf '%s' "$out" | grep -qF "✗ $guard"; then
      ok "MUTANT $name ($desc) chết bằng ASSERTION: $guard"
    else
      bad "MUTANT $name ($desc) chết ĐÚNG chỗ" "✗ $guard" "$(printf '%s' "$out" | grep '✗' | head -3)"
    fi
  }

  section "MUTATION 1 — W1(a) quay xe: ghi state VÔ ĐIỀU KIỆN dù notify hỏng"
  mutate m1 'luot sau se thu lai. Loi that: ${NOTIFY_ERR}" >&2
  exit 10
fi' 'luot sau se thu lai. Loi that: ${NOTIFY_ERR}" >&2
fi'
  kill_check m1 "mất cảnh báo vĩnh viễn" \
    "MUTATION-GUARD vendor_alert_no_state_on_notify_fail: state KHÔNG được ghi khi notify hỏng"

  section "MUTATION 2 — W1(b) quay xe: nuốt stderr của notify (2>/dev/null)"
  mutate m2 'NOTIFY_ERR="$("$ROOT/bin/notify_thread.sh" "$MSG" "$TOPIC" 2>&1 >/dev/null)"' \
            'NOTIFY_ERR="$("$ROOT/bin/notify_thread.sh" "$MSG" "$TOPIC" 2>/dev/null >/dev/null)"'
  kill_check m2 "chẩn đoán mất bằng chứng (§29)" \
    "stderr mang LỖI THẬT của notify (§29)"

  section "MUTATION 3 — W2 quay xe: ghi state KHÔNG nguyên tử (open(path,'w') thẳng)"
  mutate m3 "fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix='.vendor_mismatch_alerted.', suffix='.tmp')
try:
    with os.fdopen(fd, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
except BaseException:
    try:
        os.unlink(tmp)
    except OSError:
        pass
    raise" "with open(path, 'w') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)"
  kill_check m3 "kill giữa lúc ghi ⇒ state cụt" \
    "MUTATION-GUARD vendor_alert_atomic_state_write: state vẫn là JSON HỢP LỆ sau kill"

  section "MUTATION 4 — W1(c) quay xe: bus hỏng chặn luôn đường Discord"
  mutate m4 'if ! BUS_ERR="$("$ROOT/bin/append_event.sh" Mike error "vendor-mismatch-${FNAME}" "$PAYLOAD" 2>&1 >/dev/null)"; then
  echo "vendor_mismatch_alert: append_event.sh THAT BAI (bus la kenh phu, van gui Discord). Loi that: ${BUS_ERR}" >&2
fi' 'if ! BUS_ERR="$("$ROOT/bin/append_event.sh" Mike error "vendor-mismatch-${FNAME}" "$PAYLOAD" 2>&1 >/dev/null)"; then
  echo "vendor_mismatch_alert: append_event.sh THAT BAI. Loi that: ${BUS_ERR}" >&2
  exit 10
fi'
  kill_check m4 "kênh phụ chặn kênh chính" \
    "bus hỏng KHÔNG chặn đường tới user"

  section "MUTATION 5 — mốc ICT quay xe: bỏ TZ='Asia/Ho_Chi_Minh' khi tính TODAY (R2)"
  mutate m5 "TODAY=\"\$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)\"" 'TODAY="$(date +%Y-%m-%d)"'
  kill_check m5 "mốc ngày lệ thuộc TZ môi trường gọi (cron/host có thể không phải ICT)" \
    "MUTATION-GUARD vendor_alert_ict_anchor: key = ngày ICT (2026-09-24), không phải ngày theo TZ môi trường (2026-09-25)"

  section "MUTATION 6 — R1 quay xe: xoá dòng đọc VENDOR_MISMATCH_REASON (mọi mã lý do rơi về UNKNOWN)"
  # Hậu quả THẬT nếu mutant này sống: 3 mã lý do khác nhau (bất đồng số tiền / thuần cổ phiếu bị
  # bỏ qua / không xác định) đều nhận CÙNG một câu "KHÔNG xác định được mã lý do — kiểm thủ công"
  # — bản thân câu đó không SAI (fail-safe), nhưng làm mất TOÀN BỘ giá trị của việc rẽ nhánh mà
  # R1 dựng ra: Winston lại phải tự tra log để biết mã nào cần đối soát tiền, mã nào cần tra chân
  # cổ phiếu — đúng việc alert này sinh ra để làm hộ.
  mutate m6 "REASON_LINES=\"\$(printf '%s\n' \"\$GATE_OUT\" | grep -E '^VENDOR_MISMATCH_REASON\\|' || true)\"" \
            'REASON_LINES=""'
  kill_check m6 "3 mã lý do khác nhau gộp về cùng 1 câu, mất định tuyến Winston" \
    "MUTATION-GUARD vendor_alert_reason_routing: CẢ BA câu đặc trưng cùng có mặt — 3 mã lý do KHÔNG bị gộp thành 1 câu chung"

  section "MUTATION 7 — R1(e) quay xe: bỏ điều kiện LOOKUP_MARKERS ở cổng thoát sớm (ca THUẦN lookup_failed lại exit 0 câm lặng)"
  # Hậu quả THẬT nếu mutant này sống: một báo cáo bị CHẶN THUẦN vì lookup_failed (không có mismatch
  # nào khác) làm MARKERS rỗng ⇒ script exit 0 ngay dòng 1, không post gì — đúng lúc report đang bị
  # CHẶN thật, quay lại nguyên hành vi mà toàn bộ script này sinh ra để chặn (§29).
  mutate m7 '[ -z "$MARKERS" ] && [ -z "$LOOKUP_MARKERS" ] && exit 0' \
            '[ -z "$MARKERS" ] && exit 0'
  kill_check m7 "ca THUẦN lookup_failed exit 0 câm lặng đúng lúc bị CHẶN" \
    "exit 10 (thuần lookup_failed vẫn phải bắn cảnh báo)"

  section "MUTATION 8 — R1-D quay xe: đảo điều kiện published trong vòng lặp VENDOR_LOOKUP_FAILED (BLOCKED không còn bật đúng lúc CHẶN thật)"
  # Hậu quả THẬT nếu mutant này sống: ca CA11 (had_broker_cash=1, published=1 — sự kiện TỪNG là
  # CASH_CONFIRMED, mã ĐANG công bố, per_share bị mất khỏi báo cáo) không còn bật BLOCKED/nói
  # "báo cáo bị CHẶN" nữa — báo cáo vẫn công bố Discord "gửi bình thường" đúng lúc report_return_gate
  # đã CHẶN THẬT (rc=1) — đúng lớp lỗi "trường thứ 8" đã trả giá một lần trước đây.
  mutate m8 'if [ "${hadcash:-0}" = "1" ] && [ "${published:-0}" = "1" ]; then' \
            'if [ "${hadcash:-0}" = "1" ] && [ "${published:-0}" = "9" ]; then'
  kill_check m8 "BLOCKED không bật đúng lúc CHẶN thật — lớp lỗi 'trường thứ 8' tái diễn" \
    "R1-B: had_broker_cash=1 + published=1 ⇒ câu nói ĐÚNG 'báo cáo bị CHẶN'"
fi

printf '\n===== vendor_mismatch_alert_selfcheck: %d PASS / %d FAIL =====\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
