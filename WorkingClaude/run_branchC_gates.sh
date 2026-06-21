#!/usr/bin/env bash
# Branch-C hard-gate walk-forward: baseline (C off) vs C-ungated vs C-gated, over FULL / IS / OOS.
# Reads the SYSTEM metric line from each run's stdout. Sequential (avoids CSV clobber). NAV=20B.
set -u
cd /home/trido/thanhdt/WorkingClaude
source ./wc_env.sh 2>/dev/null
PY="$DNA_PYEXE"
export NAV_TOTAL_B=20
LOG=/tmp/branchC_gates
mkdir -p $LOG

run () {  # $1=label $2=AUDIT_START $3=AUDIT_END ; C env vars passed via env before call
  local lbl="$1"; local s="$2"; local e="$3"
  AUDIT_START="$s" AUDIT_END="$e" $PY pt_v23_audit_2014.py v23a > "$LOG/$lbl.log" 2>&1
  local m=$(grep -E "Final NAV" "$LOG/$lbl.log" | tail -1)
  local v=$(grep -E "VNINDEX B&H" "$LOG/$lbl.log" | tail -1)
  local sc=$(grep -iE "self-check|mismatch|identity" "$LOG/$lbl.log" | tail -2 | tr '\n' ' ')
  printf "%-22s | %s\n" "$lbl" "$m"
  printf "%-22s | %s\n" "" "$v"
  printf "%-22s | check: %s\n\n" "" "$sc"
}

echo "=================== WINDOWS: FULL=2014-01-02..now  IS=2014..2019  OOS=2020..now ==================="

for W in FULL:2014-01-02:2026-12-31 IS:2014-01-02:2019-12-31 OOS:2020-01-01:2026-12-31; do
  win="${W%%:*}"; rest="${W#*:}"; s="${rest%%:*}"; e="${rest#*:}"
  echo "------------------------------------ $win ($s -> $e) ------------------------------------"
  ( unset CAPIT_BEAR_OVERFLOW CAPIT_DEPTH_SIZING; run "${win}_baseline"  "$s" "$e" )
  ( export CAPIT_BEAR_OVERFLOW=1 CAPIT_DEPTH_SIZING=1 CAPIT_OVERFLOW_MATURE=0 CAPIT_OVERFLOW_DD=0.0; run "${win}_C-ungated" "$s" "$e" )
  ( export CAPIT_BEAR_OVERFLOW=1 CAPIT_DEPTH_SIZING=1 CAPIT_OVERFLOW_MATURE=1 CAPIT_OVERFLOW_DD=-20.0; run "${win}_C-gated"   "$s" "$e" )
done
echo "=================== DONE ==================="
