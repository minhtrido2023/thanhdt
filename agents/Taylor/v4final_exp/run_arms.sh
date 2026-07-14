#!/usr/bin/env bash
# Anchored ablation chain, job Taylor_20260714_140127. Each arm differs from its NEIGHBOUR by ONE axis.
# EXP_TAG on every arm (incl. the baseline) -> no run can land on the registry-pinned R3 path (§8).
set -u
cd /home/trido/thanhdt/WorkingClaude
source wc_env.sh 2>/dev/null
export BQ_CACHE_THREADS=1
L=mike/agents/Taylor/v4final_exp/logs
COMMON='NAV_TOTAL_B=50 ETF_LIQ=custompitg PARK_STATES=3:0.7 AUDIT_END=2026-06-19'

run () {  # run <tag> <extra env...>
  tag=$1; shift
  echo "=== [$tag] start $(date +%H:%M:%S) ==="
  env $COMMON EXP_TAG="$tag" "$@" $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge \
      > "$L/$tag.log" 2>&1
  echo "=== [$tag] exit=$? $(date +%H:%M:%S) ==="
  grep -E "self-check|CAGR|Sharpe|MaxDD|Calmar" "$L/$tag.log" | tail -6
}

run v4f_A0_base   BASKET_WT=namecap BASKET_SELECT=yieldcombo
run v4f_A1_eyfin  BASKET_WT=namecap BASKET_SELECT=eyfin
run v4f_A2_eyonly BASKET_WT=namecap BASKET_SELECT=eyonly
run v4f_A3_fincap BASKET_WT=fincap  BASKET_FIN_CAP=0.30 BASKET_SELECT=eyonly
echo "ALL ARMS DONE $(date +%H:%M:%S)"
