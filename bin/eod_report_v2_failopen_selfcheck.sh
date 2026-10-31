#!/bin/bash
# eod_report_v2_failopen_selfcheck.sh — kiểm nhánh báo cáo NGÀY v2 trong _deliver_eod (eod_trading_report.sh)
# bằng build.py + report_delivery_gate.py GIẢ trong thư mục tạm: không gửi gì, không chạm reports/ thật.
# Ca: v2 OK (SpaceX 3 dòng / ZaloPay + text cũ) · build lỗi ⇒ text cũ · cổng chặn v2 ⇒ gửi lại text cũ ·
# EOD_REPORT_V2=0 ⇒ text cũ · nhánh alert (not_applicable) không gọi builder.
set -u
S="$(cd "$(dirname "$0")" && pwd)/eod_trading_report.sh"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
mkdir -p "$T/bin/report_v2" "$T/reports"
cat > "$T/bin/report_v2/build.py" <<'EOF'
import os, sys
rc = int(os.environ.get("STUB_BUILD_RC", "0"))
a = sys.argv; acct = a[a.index("--account") + 1]; d = a[a.index("--period") + 1]; out = a[a.index("--out-dir") + 1]
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
if "V2 SUMMARY" in body and os.environ.get("STUB_GATE_BLOCK") == "1":
    print("report_delivery_gate: INCOMPLETE — artifact-lint BLOCK (stub)"); sys.exit(1)
print("report_delivery_gate: COMPLETE"); sys.exit(0)
EOF
printf '#!/bin/bash\nexit 0\n' > "$T/bin/vendor_mismatch_alert.sh"
printf '#!/bin/bash\nexit 0\n' > "$T/bin/append_event.sh"
chmod +x "$T/bin/"*.sh
fn="$(awk '/^_deliver_eod\(\) \{/{f=1} f{print} f&&/^\}/{exit}' "$S")"
[ -n "$fn" ] || { echo "FATAL: không trích được _deliver_eod từ $S"; exit 2; }
fails=0
case_run() {  # acct build_rc gate_block mode v2flag want_first want_old want_gates
  local got
  got="$(ROOT="$T" ACCOUNT="$1" PLAN_DATE=2026-10-30 TRADING_REPORT_THREAD=x GATE_LOG="$T/gate.log" \
    STUB_BUILD_RC="$2" STUB_GATE_BLOCK="$3" EOD_REPORT_V2="$5" bash -c '
      _strategy_fit_attach_args() { STRATEGY_FIT_ARGS=(); }
      eval "$1"; : > "$GATE_LOG"; _deliver_eod "OLD TEXT BODY" "$2" >/dev/null 2>&1; rc=$?
      f="$ROOT/reports/${ACCOUNT}_daily_report_2026-10-30.md"
      echo "$rc|$(head -1 "$f")|$(grep -c "OLD TEXT" "$f")|$(tr "\n" " " < "$GATE_LOG")"' _ "$fn" "$4")"
  local want="0|$6|$7|$8"
  if [ "$got" = "$want" ]; then echo "  ok   $1 build=$2 block=$3 mode=$4 v2=$5"; else
    echo "  FAIL $1 build=$2 block=$3 mode=$4 v2=$5: got [$got] want [$want]"; fails=$((fails + 1)); fi
}
case_run SpaceX  0 0 full 1 "# V2 SUMMARY"  0 "GATE:# V2 SUMMARY "
case_run ZaloPay 0 0 full 1 "# V2 SUMMARY"  1 "GATE:# V2 SUMMARY "
case_run SpaceX  1 0 full 1 "OLD TEXT BODY" 1 "GATE:OLD TEXT BODY "
case_run SpaceX  0 1 full 1 "OLD TEXT BODY" 1 "GATE:# V2 SUMMARY GATE:OLD TEXT BODY "
case_run ZaloPay 0 1 full 1 "OLD TEXT BODY" 1 "GATE:# V2 SUMMARY GATE:OLD TEXT BODY "
case_run SpaceX  0 0 full 0 "OLD TEXT BODY" 1 "GATE:OLD TEXT BODY "
case_run SpaceX  0 0 not_applicable 1 "OLD TEXT BODY" 1 "GATE:OLD TEXT BODY "
[ "$fails" -eq 0 ] && echo "✅ PASS eod_report_v2_failopen_selfcheck (7/7)" || { echo "❌ FAIL $fails/7"; exit 1; }
