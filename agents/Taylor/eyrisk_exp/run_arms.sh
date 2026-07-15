#!/usr/bin/env bash
# eyrisk anchored ablation, job Taylor_20260715_025346. Anchor A2 (eyonly) RERUN in this session
# (same-session anchor rule, job 152605 precedent). Each R-arm differs from A2 by exactly ONE axis:
#   R1 = eyrisk scope=all  (continuous ROE_Min5Y penalty on every name's ey)
#   R2 = eyrisk scope=fin  (penalty only on BANK/INSURANCE/SECURITIES — the user's NPL thesis)
# N-budget pre-declared: 2 arms, penalty knobs (0.5, 0.10) FIXED, no sweep. EXP_TAG on every arm
# (incl. anchor) -> §8-safe, nothing can land on a registry-pinned path.
set -u
cd /home/trido/thanhdt/WorkingClaude
source wc_env.sh 2>/dev/null
export BQ_CACHE_THREADS=1
L=mike/agents/Taylor/eyrisk_exp/logs
COMMON='NAV_TOTAL_B=50 ETF_LIQ=custompitg PARK_STATES=3:0.7 AUDIT_END=2026-06-19'

run () {  # run <tag> <extra env...>
  tag=$1; shift
  echo "=== [$tag] start $(date +%H:%M:%S) ==="
  env $COMMON EXP_TAG="$tag" "$@" $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge \
      > "$L/$tag.log" 2>&1
  echo "=== [$tag] exit=$? $(date +%H:%M:%S) ==="
  grep -E "self-check|CAGR|Sharpe|MaxDD|Calmar" "$L/$tag.log" | tail -6
}

run eyr_A2_anchor BASKET_WT=namecap BASKET_SELECT=eyonly
run eyr_R1_all    BASKET_WT=namecap BASKET_SELECT=eyrisk BASKET_RISK_SCOPE=all
run eyr_R2_fin    BASKET_WT=namecap BASKET_SELECT=eyrisk BASKET_RISK_SCOPE=fin
echo "ALL ARMS DONE $(date +%H:%M:%S)"
