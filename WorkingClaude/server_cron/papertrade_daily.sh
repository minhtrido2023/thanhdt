#!/usr/bin/env bash
# Daily paper-trade orchestrator (server port of papertrade_daily.bat). Runs ~15:30 ICT.
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
TODAY=$(date +%F)
LOG="$WORKDIR_8L/data/papertrade_run_${TODAY}.log"
run(){ echo "[$(date +%T)] $*" >> "$LOG"; "$@" >> "$LOG" 2>&1; }

{ echo "===================================================="
  echo "Paper-trade daily run (server) — $(date)"
  echo "===================================================="; } > "$LOG"

run $VENV_PY pull_us_market.py
echo "[0a2] rebuild_state_from_ticker.sh" >> "$LOG"
bash "$WORKDIR_8L/server_cron/rebuild_state_from_ticker.sh" >> "$LOG" 2>&1
run $VENV_PY refresh_lagged_caches.py
run $VENV_PY snapshot_state_vintage.py
run $VENV_PY macro_healthcheck.py
run $VENV_PY deploy_golive_dt5g_v4/publish_gated_state.py
run $VENV_PY custom30_history.py
run $VENV_PY pt_v11_tq34b.py
run $VENV_PY pt_v12_macro.py
run $VENV_PY pt_v121_ensemble.py
run $VENV_PY pt_v121_ens_q2.py
run $VENV_PY pt_v4_dt5g.py
run $VENV_PY pt_v22_dt5g.py
run $VENV_PY deploy_golive_dt5g_v4/golive_recommend_v23.py
run $VENV_PY papertrade_compare.py
run $VENV_PY vol_spike_hedge_pt.py
run $VENV_PY f_sleeve_pt.py
run $VENV_PY orb_pt.py
run $VENV_PY pt_dt4_vs_tq34b_ab.py
run $VENV_PY crisis_alert_push.py
run $VENV_PY pt_capitulation_shadow.py
run $VENV_PY fetch_bdi_daily.py
run $VENV_PY edge_health_monitor.py --refresh
run $VENV_PY ecology_dashboard.py --refresh
run $VENV_PY amh_cockpit.py
run $VENV_PY pt_sleeve_allocator.py

# [15] phosphorus weekly — Fridays only (ICT)
if [ "$(date +%u)" = "5" ]; then
  run $VENV_PY phosphorus_dgc_weekly.py
else
  echo "  [15] phosphorus skipped — Fridays only (today=$(date +%A))" >> "$LOG"
fi

echo "Done $(date +%T)" >> "$LOG"
