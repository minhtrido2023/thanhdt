#!/usr/bin/env bash
# Self-update v3.4b + DT4-gate market-state series from fresh BQ ticker (server port).
# LOCAL CSVs only — the risky BQ deploy step is deliberately skipped. On any step
# error: stop and return 1 (macro_state_live keeps last good CSV; healthcheck flags staleness).
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
export STATE_WORKDIR="$WORKDIR_8L"

# bug guard: stale pkl caches -> ew_v1 would reuse old pulls
rm -f "$WORKDIR_8L/_cache_vnindex_2000_now.pkl" "$WORKDIR_8L/_cache_universe_2013_now.pkl" 2>/dev/null

step(){ "$@" || { echo "rebuild_state_from_ticker: FAILED at: $*"; exit 1; }; }

step $VENV_PY vnindex_5state_ew_v1.py
step $VENV_PY build_concentration_history.py
step $VENV_PY vnindex_5state_dual_v3.py
step $VENV_PY deploy_v3_4b_package/build_v3_1_clean.py
cp -f "$WORKDIR_8L/vnindex_5state_tam_quan_v3_1_clean.csv" "$WORKDIR_8L/vnindex_5state_tam_quan_v3_1_full_history.csv"
step $VENV_PY deploy_v3_4b_package/build_v3_4_bull_aware.py
step $VENV_PY build_dt_4gate.py
echo "rebuild_state_from_ticker: OK"
