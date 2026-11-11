#!/usr/bin/env bash
# fa_ratings_conditional_rerate_selfcheck.sh — test nhánh re-rate CÓ ĐIỀU KIỆN NGOÀI cửa sổ của
# fa_ratings_earnings_window_daily.sh (2026-11-11, P2). Stub toàn bộ: không chạm BQ/refresh thật.
# Exit 0 = PASS hết; 1 = có ca lệch.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="${GATE_SCRIPT:-$HERE/fa_ratings_earnings_window_daily.sh}"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
fail=0; n=0
printf '#!/usr/bin/env bash\necho x >> "%s/ran8l"; exit "${STUB_RC8:-0}"\n' "$T" > "$T/c8"
printf '#!/usr/bin/env bash\necho x >> "%s/ranfa"; exit 0\n' "$T" > "$T/cfa"
printf '#!/usr/bin/env bash\nif [ "${STUB_TF:-}" = FAIL ]; then exit 1; fi; echo "$STUB_TF"\n' > "$T/ctf"
chmod +x "$T"/c8 "$T"/cfa "$T"/ctf

run() {  # $1=ngày giả lập  → in output; đặt biến RAN8 (0/1)
  rm -f "$T/ran8l" "$T/ranfa"
  OUT="$(FA8L_WINDOW_RUN_DATE="$1" FA8L_WINDOW_STATE_TF="$T/state" FA8L_WINDOW_TF_CMD="$T/ctf" \
    FA8L_WINDOW_CHILD_8L="$T/c8" FA8L_WINDOW_CHILD_FA="$T/cfa" FA8L_WINDOW_SPACING_S=0 \
    FA8L_WINDOW_LOG_8L="$T/l8" FA8L_WINDOW_LOG_FA="$T/lfa" "$SCRIPT" 2>&1)"
  [ -f "$T/ran8l" ] && RAN8=1 || RAN8=0
}
check() {  # $1=nhãn $2=kỳ vọng ran8 $3=kỳ vọng state ('-' = không có file) $4=từ khoá trong OUT
  n=$((n+1)); local st="-"; [ -f "$T/state" ] && st="$(cat "$T/state")"
  if [ "$RAN8" != "$2" ] || [ "$st" != "$3" ] || ! grep -q -- "$4" <<<"$OUT"; then
    echo "FAIL [$1]: ran8=$RAN8 (want $2) state=$st (want $3) kw='$4' out=$OUT"; fail=$((fail+1))
  fi
}
OUTW=2026-11-20   # ngoài cửa sổ (tháng 11, ngày>10)
INW=2026-11-05    # trong cửa sổ

rm -f "$T/state"; STUB_TF=1000 STUB_RC8=0; export STUB_TF STUB_RC8
run $OUTW; check "ngoai-cua-so, chua co state => RUN-COND + ghi baseline" 1 1000 "RUN-COND"
STUB_TF=1000; run $OUTW; check "numRows khong doi => SKIP, state giu nguyen" 0 1000 "khong doi"
STUB_TF=1075; run $OUTW; check "numRows tang => RUN-COND, state cap nhat" 1 1075 "1000 -> 1075"
STUB_TF=FAIL; run $OUTW;  check "BQ loi => SKIP khong chay mu" 0 1075 "khong doc duoc"
STUB_TF=1200; STUB_RC8=1; export STUB_RC8; run $OUTW; check "8l that bai => state KHONG cap nhat (lan sau thu lai)" 1 1075 "RUN-COND"
STUB_RC8=3; export STUB_RC8; run $OUTW; check "ticker-gate rc=3 => state KHONG cap nhat" 1 1075 "RUN-COND"
STUB_RC8=0; export STUB_RC8; run $OUTW; check "thu lai sau that bai => chay + ghi" 1 1200 "1075 -> 1200"
STUB_TF=1200; run $INW;   check "TRONG cua so: chay du numRows khong doi" 1 1200 "trong cua so"
STUB_TF=1300; run $INW;   check "TRONG cua so: ghi state moi" 1 1300 "trong cua so"
STUB_TF=FAIL; run $INW;   check "TRONG cua so + BQ loi: van chay, state giu" 1 1300 "trong cua so"
STUB_TF=1300; run 2026-11-21; check "ngoai cua so, khong doi lai => SKIP" 0 1300 "SKIP"

echo "fa_ratings conditional re-rate selfcheck: $((n-fail))/$n PASS"
[ "$fail" -eq 0 ]
