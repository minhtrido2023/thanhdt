#!/usr/bin/env bash
# selfcheck sổ paper_cell_monthly_pit2.py: T1–T9 (append-only thật, idempotent, fail-closed đổi biến thể/sai file/sửa khối cũ/cache cũ).
# Dùng: bash calc/selfcheck_paper_cell_pit2.sh [OUT_DIR]   (cần out/final/lvens2_2026-0{7,8,9},10 _mcstepcar + _mcstepca). rc=0 nếu 9/9 đúng kỳ vọng.
set -u
cd "$(dirname "$0")/.."
PY=${PY:-/home/trido/thanhdt/wc_venv/bin/python}; O=${1:-out/sc_ledger}; L=$O/led.csv; F=out/final; WC=/home/trido/thanhdt/WorkingClaude
rm -rf "$O"; mkdir -p "$O"; bad=0
run() { "$PY" calc/paper_cell_monthly_pit2.py --ledger "$L" "$@" >"$O/last.txt" 2>&1; echo $?; }
chk() { local name=$1 want=$2 got=$3; if [ "$got" = "$want" ]; then echo "$name | PASS | rc=$got"; else echo "$name | FAIL | rc=$got want=$want"; tail -3 "$O/last.txt"; bad=$((bad+1)); fi; }
chk "T1 ghi 2026-09" 0 "$(run --asof-ym 2026-09 --lvens2-from $F/lvens2_2026-09_mcstepcar.parquet)"
chk "T2 ghi 2026-10" 0 "$(run --asof-ym 2026-10 --lvens2-from $F/lvens2_2026-10_mcstepcar.parquet)"
chk "T3 chạy lại 2026-10 (SKIP idempotent)" 0 "$(run --asof-ym 2026-10 --lvens2-from $F/lvens2_2026-10_mcstepcar.parquet)"; grep -q SKIP "$O/last.txt" || { echo "T3 không SKIP"; bad=$((bad+1)); }
chk "T4 đổi biến thể giữa chừng (stepca)" 3 "$(run --asof-ym 2026-08 --lvens2-from $F/lvens2_2026-08_mcstepca.parquet --expect-mc stepca)"
chk "T5 file sai biến thể so với expect" 3 "$(run --asof-ym 2026-08 --lvens2-from $F/lvens2_2026-08_mcstepca.parquet)"
chk "T6 file sai tháng" 3 "$(run --asof-ym 2026-08 --lvens2-from $F/lvens2_2026-07_mcstepcar.parquet)"
cp "$L" "$O/led.bak"; pre=$(md5sum < "$L"); sz=$(stat -c %s "$L")
sed -i '2s/RE_DUOC_THUA_NHAN\|RE_CHUA_THUA_NHAN\|DAT_CON_NEO\|DAT_DANG_NGUOI/XX/' "$L"
chk "T7 sửa 1 dòng cũ rồi ghi" 3 "$(run --asof-ym 2026-08 --lvens2-from $F/lvens2_2026-08_mcstepcar.parquet)"
cp "$O/led.bak" "$L"
chk "T8 khôi phục rồi ghi 2026-08" 0 "$(run --asof-ym 2026-08 --lvens2-from $F/lvens2_2026-08_mcstepcar.parquet)"
[ "$(head -c "$sz" "$L" | md5sum)" = "$pre" ] && echo "T8b prefix byte cũ giữ nguyên | PASS" || { echo "T8b prefix đổi | FAIL"; bad=$((bad+1)); }
# T9: cây cache giả, manifest ticker_financial max_time lùi về 2026-10-01
FK=$O/fakewc/data/bq_cache; mkdir -p "$FK"; for d in "$WC"/data/bq_cache/*/; do ln -s "$d" "$FK/$(basename "$d")"; done
"$PY" -c "import json,sys;m=json.load(open('$WC/data/bq_cache/manifest.json'));m['tables']['ticker_financial']['max_time']='2026-10-01';json.dump(m,open('$FK/manifest.json','w'))"
chk "T9 cache ticker_financial cũ" 3 "$(WC_ROOT=$O/fakewc run --asof-ym 2026-10 --lvens2-from $F/lvens2_2026-10_mcstepcar.parquet --ledger $O/led9.csv)"
grep -q "max_time=2026-10-01" "$O/last.txt" || { echo "T9 lý do fail-closed sai"; cat "$O/last.txt"; bad=$((bad+1)); }
echo "TZ=${TZ-<unset>} RESULT: $([ $bad = 0 ] && echo PASS || echo "FAIL $bad")"; exit $bad
