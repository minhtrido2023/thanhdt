#!/usr/bin/env bash
# selfcheck vòng 3 (3 TZ) + đo rollfwd, tuần tự một luồng (dựng lại final/regress: xem r3_run.sh)
set -u
cd "$(dirname "$0")/.."
export LVENS2_FROZEN=/home/trido/thanhdt/WorkingClaude/data/research_frozen/dcf_v31_inputs/out LVENS2_CA=out/ca/ca_extract_202611.csv LVENS2_CA_MD5=28418e9d4d91abfa8965ac756bb3d9c4 PYTHONHASHSEED=0
PY=/home/trido/thanhdt/wc_venv/bin/python; D=out/r3_logs
for tz in unset America/New_York Asia/Ho_Chi_Minh; do
  tag=${tz//\//_}; if [ $tz = unset ]; then pre=(env -u TZ); else pre=(env TZ=$tz); fi
  "${pre[@]}" F=out/r3_final bash calc/selfcheck_paper_cell_pit2.sh out/sc_ledger_r3_$tag > $D/scl_$tag.txt 2>&1; echo "rc=$?" >> $D/scl_$tag.txt
  for ym in 2026-10 2026-05; do "${pre[@]}" $PY calc/selfcheck_pit2.py $ym stepcar out/sc_r3_${tag}_$ym > $D/scp_${ym}_$tag.txt 2>&1; echo "rc=$?" >> $D/scp_${ym}_$tag.txt; done
done
$PY calc/measure_ideas.py rollfwd > out/measure_rollfwd.txt 2>&1; echo "rc=$?" >> out/measure_rollfwd.txt
touch $D/DONE
