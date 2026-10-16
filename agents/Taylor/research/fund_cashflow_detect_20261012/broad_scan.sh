#!/usr/bin/env bash
# Quét rộng §23 TRONG SANDBOX (không secrets ⇒ không broker; data/ là bản sao). BỎ nav_scripts_2account_selfcheck.py
# (vòng 2 nó gọi broker thật + ghi data/ thật). Dùng: broad_scan.sh <sandbox WC> <thư mục log>
SB="$1"; OUT="$2"; mkdir -p "$OUT"; : > "$OUT/summary.txt"; cd "$SB/mike" || exit 9
for f in auto_exit_inject_selfcheck.py bus_question_housekeeping_selfcheck.py check_report_cadence_selfcheck.py \
  corp_action_broker_detect_selfcheck.py daily_nav_snapshot_corpaction_error_selfcheck.py daily_nav_snapshot_from_raw_selfcheck.py \
  discretionary_margin_gate_selfcheck.py eod_delivery_wiring_selfcheck.py eod_trading_report_account_filter_selfcheck.py \
  exdate_frame_selfcheck.py exrights_price_basis_selfcheck.py failopen_batch1_selfcheck.py nav_corpaction_gate_e2e_selfcheck.py \
  nav_cum_dividend_selfcheck.py nav_exdate_forecast_selfcheck.py nav_flow_term_selfcheck.py nav_jump_flow_gate_selfcheck.py \
  nav_snapshot_daily_selfcheck.sh nav_sync_retry_rc_selfcheck.sh nav_unit_ledger_selfcheck.py paper_report_render_selfcheck.py \
  portfolio_status_selfcheck.py report_delivery_gate_selfcheck.py report_delivery_ledger_selfcheck.py \
  report_return_gate_selfcheck.py worktree_stale_check_selfcheck.py cash_identity_selfcheck.py; do
  case "$f" in *.sh) run=(bash "bin/$f");; *) run=(python3 "bin/$f");; esac
  s=$(date +%s)
  env -u TZ -u WC_ROOT -u MIKE_ROOT NO_GCE_CHECK=true PYTHONDONTWRITEBYTECODE=1 MIKE_BOT_TEST_MODE=1 timeout 300 "${run[@]}" > "$OUT/$f.log" 2>&1
  echo "rc=$? $(( $(date +%s) - s ))s $f" >> "$OUT/summary.txt"
done
echo "BỎ (ràng buộc vòng 3): nav_scripts_2account_selfcheck.py" >> "$OUT/summary.txt"
