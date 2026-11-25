#!/usr/bin/env bash
# selfcheck sổ paper_cell_monthly_pit2.py: T1–T9 (append-only thật, idempotent, fail-closed đổi biến thể/sai file/sửa khối cũ/cache cũ).
# T10–T12 (B1): extract CA là DỮ LIỆU — đổi extract không đổi script_md5, không làm sổ fail-closed; md5 extract sai/thiếu ⇒ rc 3. Cần LVENS2_CA_MD5 (mặc định bên dưới = extract 202611).
# Dùng: bash calc/selfcheck_paper_cell_pit2.sh [OUT_DIR]   (cần out/final/lvens2_2026-0{7,8,9},10 _mcstepcar + _mcstepca). rc=0 nếu 9/9 đúng kỳ vọng.
set -u
export LVENS2_CA_MD5=${LVENS2_CA_MD5:-28418e9d4d91abfa8965ac756bb3d9c4}
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
# T10–T12 (B1): extract CA tháng mới (khác md5, cùng nội dung hiệu lực) + script GIỮ NGUYÊN ⇒ sổ vẫn ghi được; md5 extract sai/thiếu ⇒ rc 3
CA2=$O/ca_extract_new.csv; cp out/ca/ca_extract_202611.csv "$CA2"; echo >> "$CA2"; M2=$(md5sum < "$CA2" | cut -d' ' -f1)
lv() { "$PY" calc/lvens2_pit2.py --asof-ym 2026-07 --mc-pit stepcar --out-dir "$O/new" >"$O/last.txt" 2>&1; echo $?; }
chk "T10a dựng lvens2 với extract MỚI (md5 mới)" 0 "$(LVENS2_CA=$CA2 LVENS2_CA_MD5=$M2 lv)"
[ "$(md5sum < calc/lvens2_pit2.py)" = "$(python3 -c "import json;print(json.load(open('$O/new/lvens2_2026-07_mcstepcar.json'))['script_md5']+'  -')")" ] && echo "T10b script_md5 sidecar = md5 file script (không đổi theo extract) | PASS" || { echo "T10b | FAIL"; bad=$((bad+1)); }
chk "T10c sổ đã có khối ca_md5 cũ, ghi khối extract mới" 0 "$(run --asof-ym 2026-07 --lvens2-from $O/new/lvens2_2026-07_mcstepcar.parquet)"
[ "$(cut -d, -f"$(head -1 "$L" | tr , '\n' | grep -n '^ca_md5$' | cut -d: -f1)" "$L" | tail -n +2 | sort -u | wc -l)" = 2 ] && echo "T10d sổ chứa 2 ca_md5 khác nhau | PASS" || { echo "T10d | FAIL"; bad=$((bad+1)); }
chk "T11 extract md5 SAI" 3 "$(LVENS2_CA=$CA2 LVENS2_CA_MD5=0123456789abcdef0123456789abcdef lv)"
chk "T12 thiếu LVENS2_CA_MD5" 3 "$(env -u LVENS2_CA_MD5 LVENS2_CA=$CA2 bash -c 'cd . && '"$PY"' calc/lvens2_pit2.py --asof-ym 2026-07 --out-dir '"$O"'/new2 >'"$O"'/last.txt 2>&1; echo $?')"
echo "TZ=${TZ-<unset>} RESULT: $([ $bad = 0 ] && echo PASS || echo "FAIL $bad")"; exit $bad
