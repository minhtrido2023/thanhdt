#!/bin/bash
# job Taylor_20261021_012028 — F1/F2/F3 + control dau (dump F2) + control cuoi; TOI DA 2 engine song song (§32), tran RAM 8G/run.
O=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/survivorship_volzero_20261020
MC=/home/trido/thanhdt/WorkingClaude/mike/bin/memcap.sh
MULT="2014:1.000000,2015:1.308588,2016:1.088996,2017:1.042744,2018:1.110794,2019:1.075501,2020:1.057558,2021:1.085176,2022:1.088996,2023:1.028190,2024:1.055647,2025:1.019323,2026:1.062617"
cd "$O" || exit 9
source "$O/legs.sh"
V1D="ZVF_MODE=block LIQ_ZERO_BLOCK=lag V1D_SELL=1"
run_stage() {   # $1 = ten stage; mang jobs_list
  echo "STAGE $1 START $(date -Is) n=${#jobs_list[@]}"
  for ((k=0; k<${#jobs_list[@]}; k+=2)); do
    for j in "${jobs_list[@]:k:2}"; do
      tag="${j%%|*}"; envs="${j#*|}"
      # shellcheck disable=SC2086
      "$MC" 8 "$O/run_leg.sh" "$tag" $envs &
    done
    wait; echo "PAIR $1 $k $(date -Is)"
  done
}
add() { for leg in p30_pin0 p30_pin1M p0_pin0 p0_pin1M; do jobs_list+=("vz_$1_$leg|${LEG[$leg]} $2"); done; }
addl() { for leg in p30_pin0 p30_pin1M p0_pin0 p0_pin1M; do jobs_list+=("vz_$1_$leg|${LEG[$leg]} $2 $3=$O/f2_wl_$leg.json"); done; }
jobs_list=(); addl ctlD "" F2_DUMP; run_stage ctlD
jobs_list=()
add F1_N5H10  "$V1D F1_N=5 F1_H=0.10"
add F1_N5H30  "$V1D F1_N=5 F1_H=0.30"
add F1_N20H10 "$V1D F1_N=20 F1_H=0.10"
add F1_N20H30 "$V1D F1_N=20 F1_H=0.30"
addl F2  "$V1D" F2_WL
addl F2C "" F2_WL
add F3L "ZVF_MODE=block F3_MODE=lag F3_MULT=$MULT"
add F3B "ZVF_MODE=block F3_MODE=both F3_MULT=$MULT"
add ctlZ ""
run_stage main
echo "DONE $(date -Is)"
