#!/usr/bin/env bash
# Job Taylor_20260714_152605. Two INDEPENDENT questions, deliberately not mixed in one arm:
#   Viec 1 — A4: DY tie-break in the marginal band, on the A2 (eyonly) base, NO cap.
#   Viec 2 — peak-targeted financial cap sweep, on the A2 base, NO DY.
# Anchored-ablation discipline (§12.2): every arm differs from A2 by EXACTLY ONE axis, so each
# delta is attributable. A2 is re-run here rather than quoted from job 140127 — same vintage, same
# session, same cache: a cross-job number is not a controlled neighbour.
#
# Viec 2 note — the mechanism needed is the one already in the tree: `fincap` caps the financial
# group at BASKET_FIN_CAP, and a cap at X by construction does nothing on any day the group is
# already under X. "Cap only when the peak exceeds X" and "flat cap at X" are the SAME rule; the
# only thing that separates the risk-auditor's proposal from the NO-GO'd A3 is the LEVEL (0.30 ->
# 0.45-0.60). So this is a level sweep, not a new mechanism — no new code, nothing new to trust.
#
# EXP_TAG on every arm (incl. the A2 baseline) -> no run can land on the registry-pinned R3 path (§8).
# Usage: run_arms_a4.sh viec2   (A2 baseline + cap sweep — independent of the A4 mechanism)
#        run_arms_a4.sh viec1   (A4 — run ONLY after a4_dy_selfcheck.py passes)
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
  grep -E "self-check|CAGR|Sharpe|MaxDD|Calmar|fincap|DY tie-break" "$L/$tag.log" | tail -8
}

case "${1:-all}" in
  viec2)
    # baseline (the anchored neighbour for BOTH questions) + peak-cap level sweep
    run v4f_A2_eyonly_rerun BASKET_WT=namecap BASKET_SELECT=eyonly
    for X in 0.45 0.50 0.55 0.60; do
      run "v4f_C${X/0./}_fincap" BASKET_WT=fincap BASKET_FIN_CAP=$X BASKET_SELECT=eyonly
    done
    ;;
  viec1)
    # A4 = A2 + DY tie-break in the pre-registered marginal band. Gated on the selfcheck.
    run v4f_A4_dy2045 BASKET_WT=namecap BASKET_SELECT=eyonly BASKET_DY_TIEBREAK=20:45
    ;;
  *)
    echo "usage: $0 viec1|viec2"; exit 2;;
esac
echo "ALL ARMS DONE $(date +%H:%M:%S)"
