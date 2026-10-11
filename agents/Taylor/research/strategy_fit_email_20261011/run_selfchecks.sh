#!/usr/bin/env bash
# Chạy lại selfcheck liên quan dưới 3 biến thể TZ. KHÔNG gồm nav_scripts_2account_selfcheck (gọi broker thật + ghi data/ thật).
cd "$1" || exit 1
OUT="$2"; : > "$OUT/summary.txt"
LIST="strategy_fit_email_attach_selfcheck.py strategy_fit_dashboard_selfcheck.py report_delivery_gate_selfcheck.py report_delivery_ledger_selfcheck.py check_report_cadence_selfcheck.py eod_delivery_wiring_selfcheck.py eod_trading_report_account_filter_selfcheck.py report_return_gate_selfcheck.py paper_report_render_selfcheck.py nav_flow_term_selfcheck.py portfolio_status_selfcheck.py production_manifest_selfcheck.sh"
for tz in unset America/New_York Asia/Ho_Chi_Minh; do
  for sc in $LIST; do
    [ -f "bin/$sc" ] || { echo "$tz $sc MISSING" >> "$OUT/summary.txt"; continue; }
    case "$sc" in *.py) run=(/home/trido/thanhdt/wc_venv/bin/python "bin/$sc");; *) run=(bash "bin/$sc");; esac
    log="$OUT/${sc%.*}__${tz//\//_}.log"
    if [ "$tz" = unset ]; then env -u TZ timeout 900 "${run[@]}" > "$log" 2>&1; else TZ="$tz" timeout 900 "${run[@]}" > "$log" 2>&1; fi
    echo "$tz $sc rc=$? | $(grep -v '^\s*$' "$log" | tail -n 1 | cut -c1-200)" >> "$OUT/summary.txt"
  done
done
