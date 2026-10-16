#!/usr/bin/env bash
# Quét rộng §23 (job Taylor_20261013_125149). $1 = gốc WC cần quét (sandbox đã sed đường dẫn, hoặc canonical
# để lấy baseline), $2 = thư mục log, $3 = interpreter cho selfcheck .py của WC (DNA_PYEXE).
WC="$1"; OUT="$2"; PYX="${3:-python3}"; mkdir -p "$OUT"; : > "$OUT/summary.txt"
WC_LIST="lag_rating_filter_selfcheck.py lag_rating_order_gate_selfcheck.py lag_forensic_filter_selfcheck.py lag_live_schedule_selfcheck.py
 filter_lag_entry_window_selfcheck.py anomaly_gate_selfcheck.py anomaly_gate_prod_parity_selfcheck.py capit_lever_selfcheck.py
 cctg_tier2_series_selfcheck.py dot2_batch_selfcheck.py edge_wlag_gate_selfcheck.py failc_residual_selfcheck.py
 money_path_freshness_selfcheck.py navbasis_loud_selfcheck.py universe_pit_p3_selfcheck.py universe_pit_p4_selfcheck.py
 macro_healthcheck_sbv_reconfirm_selfcheck.py freshness_ops_selfcheck.py dt5g_chain_freshness_selfcheck.py
 account_overrides_broker_resolution_selfcheck.py"
MIKE_LIST="bin/bq_freshness_check_selfcheck.py bin/bq_price_freeze_gate_selfcheck.py bin/park_rail_consistency_selfcheck.py
 bin/strategy_fit_dashboard_selfcheck.py bin/tz_anchor_gate_selfcheck.py bin/code_quality_autodispatch_selfcheck.sh
 bin/dispatch_discord_topic_selfcheck.sh bin/dispatch_round_cap_selfcheck.py bin/dt5g_publisher_gate_selfcheck.sh
 bin/retro_escalate_selfcheck.py bin/wait_for_artifact_selfcheck.py agents/Winston/freshness_warn_selfcheck.py
 agents/Taylor/capit_dd_gate_selfcheck.py"
run1() { # $1=cwd $2=nhãn $3..=lệnh
  local cwd="$1" label="$2"; shift 2; local s; s=$(date +%s)
  ( cd "$cwd" && env -u TZ -u WC_ROOT -u MIKE_ROOT -u BQ_LOCAL_CACHE NO_GCE_CHECK=true PYTHONDONTWRITEBYTECODE=1 MIKE_BOT_TEST_MODE=1 \
      timeout 300 "$@" ) > "$OUT/$(echo "$label" | tr '/' '_').log" 2>&1
  echo "rc=$? $(( $(date +%s) - s ))s $label" >> "$OUT/summary.txt"
}
for f in $WC_LIST; do [ -f "$WC/$f" ] && run1 "$WC" "$f" "$PYX" "$f" || echo "rc=NA 0s $f (không có file)" >> "$OUT/summary.txt"; done
for f in $MIKE_LIST; do
  [ -f "$WC/mike/$f" ] || { echo "rc=NA 0s mike/$f (không có file)" >> "$OUT/summary.txt"; continue; }
  case "$f" in *.sh) run1 "$WC/mike" "mike/$f" bash "$f";; *) run1 "$WC/mike" "mike/$f" python3 "$f";; esac
done
