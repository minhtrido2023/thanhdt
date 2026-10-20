#!/bin/bash
# job Taylor_20261020_162558 — V1D/V1D0/V1E20/V1E60/V3Ap + control cuoi; TOI DA 2 engine song song (§32), moi run tran RAM 8G.
O=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/survivorship_volzero_20261020
MC=/home/trido/thanhdt/WorkingClaude/mike/bin/memcap.sh
cd "$O" || exit 9
source "$O/legs.sh"
jobs_list=()
add() { for leg in p30_pin0 p30_pin1M p0_pin0 p0_pin1M; do jobs_list+=("vz_$1_$leg|${LEG[$leg]} $2"); done; }
add V1D  "ZVF_MODE=block LIQ_ZERO_BLOCK=lag V1D_SELL=1"
add V1D0 "LIQ_ZERO_BLOCK=lag V1D_SELL=1"
add V1E20 "ZVF_MODE=block_trail ZVF_TRAIL_N=20"
add V1E60 "ZVF_MODE=block_trail ZVF_TRAIL_N=60"
add V3Ap "V3_MODE=noentry_bear_t1"
add ctlG ""
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
