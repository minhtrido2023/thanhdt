#!/usr/bin/env bash
# Decompose branch C into its two parts to find which one leaks IS:
#   overflow-only (gated)  : BEAR_OVERFLOW=1 DEPTH=0  -> gated custom30V augmentation only
#   depth-only             : BEAR_OVERFLOW=0 DEPTH=1  -> pb_z depth-sizing of ordinary golden events only
set -u
cd /home/trido/thanhdt/WorkingClaude
source ./wc_env.sh 2>/dev/null
PY="$DNA_PYEXE"
export NAV_TOTAL_B=20
LOG=/tmp/branchC_decomp; mkdir -p $LOG

run () {
  local lbl="$1"; local s="$2"; local e="$3"
  AUDIT_START="$s" AUDIT_END="$e" $PY pt_v23_audit_2014.py v23a > "$LOG/$lbl.log" 2>&1
  printf "%-26s | %s\n" "$lbl" "$(grep -E 'Final NAV' "$LOG/$lbl.log" | tail -1)"
}

for W in FULL:2014-01-02:2026-12-31 IS:2014-01-02:2019-12-31 OOS:2020-01-01:2026-12-31; do
  win="${W%%:*}"; rest="${W#*:}"; s="${rest%%:*}"; e="${rest#*:}"
  echo "------------------------------------ $win ($s -> $e) ------------------------------------"
  ( export CAPIT_BEAR_OVERFLOW=1 CAPIT_DEPTH_SIZING=0 CAPIT_OVERFLOW_MATURE=1 CAPIT_OVERFLOW_DD=-20.0; run "${win}_overflowGATED-only" "$s" "$e" )
  ( export CAPIT_BEAR_OVERFLOW=0 CAPIT_DEPTH_SIZING=1; run "${win}_depth-only" "$s" "$e" )
done
echo "=== DONE ==="
