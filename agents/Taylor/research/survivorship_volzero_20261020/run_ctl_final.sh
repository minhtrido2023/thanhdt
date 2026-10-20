#!/bin/bash
# job Taylor_20261020_153324 — control cuoi 4 chan (ZVF_MODE=off, V3_MODE=off) tren ban sao engine.
O=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/survivorship_volzero_20261020
cd "$O" || exit 9
source "$O/legs.sh"
echo "START $(date -Is)"
for leg in p30_pin0 p30_pin1M p0_pin0 p0_pin1M; do
  # shellcheck disable=SC2086
  "$O/run_leg.sh" "vz_ctlF_$leg" ${LEG[$leg]} &
done
wait; echo "DONE $(date -Is)"
