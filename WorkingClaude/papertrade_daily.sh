#!/usr/bin/env bash
# papertrade_daily.sh  — Linux port of papertrade_daily.bat
# Daily EOD: refresh feeds -> publish DT5G -> 4 sims + V2.3/V4 prod -> recommend
# -> dashboards/alerts. Continue-on-error per step (one bad step must not kill the
# rest), each step logged. Schedule via cron ~15:30 ICT trading days.
#
# NOTE: the Windows [0a2] rebuild_state_from_ticker.bat step is omitted — the
# v3.4b base + local state CSVs are refreshed nightly by daily_refresh_v34b_linux.sh.
set -uo pipefail
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
export STATE_WORKDIR="$WORKDIR_8L"
PY="$DNA_PYEXE"; cd "$WORKDIR_8L"
LOG="data/papertrade_run_$(date +%Y-%m-%d).log"
exec >>"$LOG" 2>&1
echo "===== papertrade_daily (linux) START $(date) acct=$(gcloud config get-value account 2>/dev/null) ====="

run() {  # run() "<label>" <script> [args...]   -- never aborts the pipeline
  echo; echo "--- $1 ---"
  shift
  if $PY "$@"; then echo "  [ok] $*"; else echo "  [FAIL exit $?] $*"; fi
}

# --- feeds + state ---
run "[1] pull_us_market"        pull_us_market.py
run "[2] refresh_lagged_caches" refresh_lagged_caches.py
run "[3] snapshot_state_vintage" snapshot_state_vintage.py
run "[4] macro_healthcheck"     macro_healthcheck.py
run "[5] publish_gated_state"   deploy_golive_dt5g_v4/publish_gated_state.py
run "[6] custom30_history"      custom30_history.py
# --- sims + production books ---
run "[7] pt_v11_tq34b"          pt_v11_tq34b.py
run "[8] pt_v12_macro"          pt_v12_macro.py
# [9] pt_v121_ensemble / [10] pt_v121_ens_q2 REMOVED 2026-06-16 — ensemble edge is a
# reduced-harness artifact (faithful audit 16.85% < V11/V2.3); dropped from daily comparison.
run "[11] pt_v4_dt5g"           pt_v4_dt5g.py
run "[12] pt_v22_dt5g (V2.3)"   pt_v22_dt5g.py
run "[13] golive_recommend_v23" deploy_golive_dt5g_v4/golive_recommend_v23.py
run "[14] papertrade_compare"   papertrade_compare.py
# --- sleeves / shadows / alerts ---
run "[15] vol_spike_hedge_pt"   vol_spike_hedge_pt.py
run "[16] f_sleeve_pt"          f_sleeve_pt.py
run "[17] orb_pt"               orb_pt.py
run "[18] pt_dt4_vs_tq34b_ab"   pt_dt4_vs_tq34b_ab.py
run "[19] crisis_alert_push"    crisis_alert_push.py
run "[20] pt_capitulation_shadow" pt_capitulation_shadow.py
run "[21] fetch_bdi_daily"      fetch_bdi_daily.py
run "[22] edge_health_monitor"  edge_health_monitor.py --refresh
run "[23] ecology_dashboard"    ecology_dashboard.py --refresh
run "[24] amh_cockpit"          amh_cockpit.py
run "[25] pt_sleeve_allocator"  pt_sleeve_allocator.py
# --- weekly: phosphorus (Friday only; ICT Friday = dow 5) ---
if [ "$(date +%u)" = "5" ]; then
  run "[26] phosphorus_dgc_weekly (Fri)" phosphorus_dgc_weekly.py
else
  echo; echo "--- [26] phosphorus_dgc_weekly skipped (not Friday) ---"
fi

# rolling 30-day log cleanup
find data -name 'papertrade_run_*.log' -mtime +30 -delete 2>/dev/null
echo; echo "===== papertrade_daily (linux) DONE $(date) ====="
