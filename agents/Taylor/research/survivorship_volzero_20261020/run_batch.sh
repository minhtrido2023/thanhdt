#!/bin/bash
# job Taylor_20261020_153324 — chay lai V1B/V1C (chet luc reboot) + V3A/V3B; moi lo 8 run song song.
O=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/survivorship_volzero_20261020
cd "$O" || exit 9
source "$O/legs.sh"
run_var() { # $1=TAG-var $2=knob
  for leg in p30_pin0 p30_pin1M p0_pin0 p0_pin1M; do
    # shellcheck disable=SC2086
    "$O/run_leg.sh" "vz_$1_$leg" ${LEG[$leg]} $2 &
  done
}
echo "START $(date -Is)"
run_var V1B ZVF_MODE=block_advbuy; run_var V1C ZVF_MODE=block_advboth; wait; echo "LOT1 $(date -Is)"
run_var V3A V3_MODE=noentry_bear; run_var V3B V3_MODE=close_reopen; wait; echo "LOT2 $(date -Is)"
