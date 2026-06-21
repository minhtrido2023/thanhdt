#!/usr/bin/env bash
set -u
cd /home/trido/thanhdt/WorkingClaude
source ./wc_env.sh 2>/dev/null
PY="$DNA_PYEXE"; export NAV_TOTAL_B=20
L=/tmp/panic_matrix; mkdir -p $L
run(){ local lbl="$1"; shift
  env "$@" $PY pt_panic_yield_sleeve.py > "$L/$lbl.log" 2>&1
  echo "########## $lbl ##########"
  grep -E "signals across|distinct|SELF-CHECK|FULL |IS 2014|OOS 2020" "$L/$lbl.log"
  echo
}
run "rsiOFF_prune"  RSI_GATE=0 QUAL=prune
run "rsiOFF_mild"   RSI_GATE=0 QUAL=mild
run "rsiOFF_strict" RSI_GATE=0 QUAL=strict
run "rsiON_prune"   RSI_GATE=1 QUAL=prune
echo "=== DONE ==="
