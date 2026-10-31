#!/bin/bash
# eod_report_v2_failopen_selfcheck.sh — kiểm nhánh báo cáo NGÀY v2 trong _deliver_eod (eod_trading_report.sh)
# bằng build.py + report_delivery_gate.py GIẢ trong thư mục tạm: không gửi gì, không chạm reports/ thật.
# Ca: v2 OK (SpaceX 3 dòng / ZaloPay + text cũ) · build lỗi ⇒ text cũ · cổng chặn v2 ⇒ gửi lại text cũ ·
# EOD_REPORT_V2=0 ⇒ text cũ · nhánh alert (not_applicable) không gọi builder.
# r3 (31/10): N7 — lỗi ở bước EMAIL sau khi Discord đã nhận (chuỗi BLOCK của script con) ⇒ KHÔNG fail-open;
# artifact-lint BLOCK mà sổ giao đã có kênh delivered cho sha này ⇒ KHÔNG fail-open. N6 — mọi lần rơi về
# text cũ (build lỗi / cổng chặn) phát đúng 1 bus event report_v2_fallback; đường v2 OK thì không phát.
set -u
S="$(cd "$(dirname "$0")" && pwd)/eod_trading_report.sh"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
mkdir -p "$T/bin/report_v2" "$T/reports"
cat > "$T/bin/report_v2/build.py" <<'EOF'
import os, sys
rc = int(os.environ.get("STUB_BUILD_RC", "0"))
a = sys.argv; acct = a[a.index("--account") + 1]; d = a[a.index("--period") + 1]; out = a[a.index("--out-dir") + 1]
if rc != 5:
  with open(f"{out}/{acct}_daily_report_{d}.md", "w") as fh:
    fh.write("# V2 SUMMARY\n" if rc == 0 else "# HALF WRITTEN\n")
if rc:
    print("Traceback boom", file=sys.stderr)
sys.exit(rc)
EOF
cat > "$T/bin/report_delivery_gate.py" <<'EOF'
import os, sys
body = open(sys.argv[1]).read()
open(os.environ["GATE_LOG"], "a").write("GATE:" + body.splitlines()[0] + "\n")
blk = os.environ.get("STUB_GATE_BLOCK")
if "V2 SUMMARY" in body and blk in ("1", "3"):
    if blk == "3":   # Discord đã nhận đúng sha này trước khi cổng chặn (ca giả định N7)
        import hashlib, json
        sha = hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest()
        json.dump({"reports": {os.path.basename(sys.argv[1]): {"discord": {"status": "delivered", "sha256": sha}}}},
                  open(os.environ["REPORT_DELIVERY_STATE"], "w"))
    print("report_delivery_gate: INCOMPLETE — artifact-lint BLOCK (stub)"); sys.exit(1)
if "V2 SUMMARY" in body and blk == "2":   # Discord xong, EMAIL lỗi; script con in chữ BLOCK/CHẶN
    print("send_report_email: artifact-lint BLOCK — CHẶN (stub email)")
    print("report_delivery_gate: INCOMPLETE — Command '[python3, send_report_email.py]' returned non-zero exit status 1"); sys.exit(1)
print("report_delivery_gate: COMPLETE"); sys.exit(0)
EOF
printf '#!/bin/bash\nexit 0\n' > "$T/bin/vendor_mismatch_alert.sh"
printf '#!/bin/bash\necho "EV:$2:$3" >> "$EV_LOG"\nexit 0\n' > "$T/bin/append_event.sh"
chmod +x "$T/bin/"*.sh
fn=""
for _f in _v2_fallback_event _v2_any_channel_delivered _deliver_eod; do
  _body="$(awk -v n="$_f" '$0 ~ "^"n"\\(\\) \\{"{f=1} f{print} f&&/^\}/{exit}' "$S")"
  [ -n "$_body" ] || { echo "FATAL: không trích được $_f từ $S"; exit 2; }
  fn="$fn
$_body"
done
fails=0
case_run() {  # acct build_rc gate_block mode v2flag want_first want_old want_gates [want_rc] [want_fallback_events]
  local got
  rm -f "$T/state.json"
  got="$(ROOT="$T" ACCOUNT="$1" PLAN_DATE=2026-10-30 TRADING_REPORT_THREAD=x GATE_LOG="$T/gate.log" EV_LOG="$T/ev.log" \
    REPORT_DELIVERY_STATE="$T/state.json" STUB_BUILD_RC="$2" STUB_GATE_BLOCK="$3" EOD_REPORT_V2="$5" bash -c '
      _strategy_fit_attach_args() { STRATEGY_FIT_ARGS=(); }
      f="$ROOT/reports/${ACCOUNT}_daily_report_2026-10-30.md"; rm -f "$f"
      [ -n "${PRE:-}" ] && printf "%s\n" "$PRE" > "$f"
      eval "$1"; : > "$GATE_LOG"; : > "$EV_LOG"; _deliver_eod "OLD TEXT BODY" "$2" >/dev/null 2>&1; rc=$?
      [ "$rc" -ne 0 ] && rc=1
      echo "$rc|$(head -1 "$f")|$(grep -c "OLD TEXT" "$f")|$(tr "\n" " " < "$GATE_LOG")|$(grep -c "^EV:error:report_v2_fallback$" "$EV_LOG")"' _ "$fn" "$4")"
  local want="${9:-0}|$6|$7|$8|${10:-0}"
  if [ "$got" = "$want" ]; then echo "  ok   $1 build=$2 block=$3 mode=$4 v2=$5"; else
    echo "  FAIL $1 build=$2 block=$3 mode=$4 v2=$5: got [$got] want [$want]"; fails=$((fails + 1)); fi
}
case_run SpaceX  0 0 full 1 "# V2 SUMMARY"  0 "GATE:# V2 SUMMARY "
case_run ZaloPay 0 0 full 1 "# V2 SUMMARY"  1 "GATE:# V2 SUMMARY "
case_run SpaceX  1 0 full 1 "OLD TEXT BODY" 1 "GATE:OLD TEXT BODY " 0 1
case_run SpaceX  0 1 full 1 "OLD TEXT BODY" 1 "GATE:# V2 SUMMARY GATE:OLD TEXT BODY " 0 1
case_run ZaloPay 0 1 full 1 "OLD TEXT BODY" 1 "GATE:# V2 SUMMARY GATE:OLD TEXT BODY " 0 1
# N7: email lỗi sau Discord ⇒ KHÔNG ghi đè, KHÔNG gọi cổng lần 2, không phát fallback
case_run SpaceX  0 2 full 1 "# V2 SUMMARY"  0 "GATE:# V2 SUMMARY " 1 0
case_run ZaloPay 0 2 full 1 "# V2 SUMMARY"  1 "GATE:# V2 SUMMARY " 1 0
# N7: artifact-lint BLOCK nhưng sổ giao đã có Discord delivered cho sha này ⇒ KHÔNG fail-open
case_run SpaceX  0 3 full 1 "# V2 SUMMARY"  0 "GATE:# V2 SUMMARY " 1 0
# r3 (arch-review): --promote rc=5 (bản chuẩn đã giao) ⇒ GIỮ NGUYÊN bản đã giao, KHÔNG ghi đè bằng text cũ,
# không phát fallback, cổng chạy trên đúng bản đã giao (chỉ thử lại kênh còn thiếu)
PRE="# V2 SUMMARY" case_run SpaceX  5 0 full 1 "# V2 SUMMARY"  0 "GATE:# V2 SUMMARY " 0 0
PRE="# V2 SUMMARY" case_run ZaloPay 5 0 full 1 "# V2 SUMMARY"  0 "GATE:# V2 SUMMARY " 0 0
case_run SpaceX  0 0 full 0 "OLD TEXT BODY" 1 "GATE:OLD TEXT BODY "
case_run SpaceX  0 0 not_applicable 1 "OLD TEXT BODY" 1 "GATE:OLD TEXT BODY "
[ "$fails" -eq 0 ] && echo "✅ PASS eod_report_v2_failopen_selfcheck (12/12)" || { echo "❌ FAIL $fails/12"; exit 1; }
