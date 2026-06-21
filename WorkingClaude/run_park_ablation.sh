#!/usr/bin/env bash
# Isolate the LIVE custom30V PARKING contribution + per-year stability.
# Live parking vehicle = custompitg + namecap + yieldcombo (custom30V). @50B. V2.3A.
#   OFF      = no parking (idle cash @0%)
#   NEUTRAL  = park 70% idle in NEUTRAL  (current live <150B)
#   NEU+BULL = park 70% NEUTRAL + 70% BULL (live >=150B)
set -u
cd /home/trido/thanhdt/WorkingClaude
source ./wc_env.sh 2>/dev/null
PY="$DNA_PYEXE"
export NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_SELECT=yieldcombo BASKET_WT=namecap
L=/tmp/park_abl; mkdir -p $L
run(){ local lbl="$1"; local spec="$2"
  PARK_STATES="$spec" $PY pt_v23_audit_2014.py v23a > "$L/$lbl.log" 2>&1
  local newest=$(ls -t data/v23_golive_audit_2014_now*.csv 2>/dev/null | head -1)
  echo "########## $lbl  (PARK_STATES='$spec') ##########"
  grep -E "Final NAV|selfcheck BAL" "$L/$lbl.log" | head -2
  $PY extract_peryear.py "$newest"
  echo
}
run "OFF"      ""
run "NEUTRAL"  "3:0.7"
run "NEU_BULL" "3:0.7,4:0.7"
echo "=== DONE ==="
