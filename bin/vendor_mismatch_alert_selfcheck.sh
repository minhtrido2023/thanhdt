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
fi

printf '\n===== vendor_mismatch_alert_selfcheck: %d PASS / %d FAIL =====\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
