#!/bin/bash
# job Taylor_20261021_012028 — HAU KY, KHONG PREREG (gan nhan trong REPORT): F2 + F1 o 2 dau luoi F1 (nhe nhat N20H10, nang nhat N5H30)
# de tach phan hoan-ban-vo-han khoi phan du cua F2. Cho batch chinh xong truoc (§32: toi da 2 engine).
O=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/survivorship_volzero_20261020
MC=/home/trido/thanhdt/WorkingClaude/mike/bin/memcap.sh
cd "$O" || exit 9
# (vong cho pgrep bo: tu khop cmdline shell boc; batch chinh DONE 10:55:40 truoc khi chay)
source "$O/legs.sh"
V1D="ZVF_MODE=block LIQ_ZERO_BLOCK=lag V1D_SELL=1"
jobs_list=()
for v in "F2F1_N20H10|F1_N=20 F1_H=0.10" "F2F1_N5H30|F1_N=5 F1_H=0.30"; do
  for leg in p30_pin0 p30_pin1M p0_pin0 p0_pin1M; do jobs_list+=("vz_${v%%|*}_$leg|${LEG[$leg]} $V1D ${v#*|} F2_WL=$O/f2_wl_$leg.json"); done
done
echo "START $(date -Is) n=${#jobs_list[@]}"
for ((k=0; k<${#jobs_list[@]}; k+=2)); do
  for j in "${jobs_list[@]:k:2}"; do
    tag="${j%%|*}"; envs="${j#*|}"
    # shellcheck disable=SC2086
    "$MC" 8 "$O/run_leg.sh" "$tag" $envs &
  done
  wait; echo "PAIR $k $(date -Is)"
done
echo "DONE $(date -Is)"
