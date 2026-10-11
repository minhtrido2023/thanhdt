#!/usr/bin/env bash
# Chạy các selfcheck lõi trong sandbox dưới 1 TZ. Dùng: run_core.sh <unset|TZ-name> [sandbox]
tz="$1"; SB="${2:-/tmp/ar3/WC}"; cd "$SB/mike" || exit 9
if [ "$tz" = unset ]; then E=(env -u TZ -u WC_ROOT); else E=(env -u WC_ROOT TZ="$tz"); fi
rc=0
for c in "bin/nav_unit_ledger_selfcheck.py" "bin/nav_flow_term_selfcheck.py" "bin/nav_jump_flow_gate_selfcheck.py" "bin/nav_period_returns.py --selfcheck" "bin/daily_nav_snapshot_from_raw_selfcheck.py" "bin/nav_corpaction_gate_e2e_selfcheck.py" "bin/daily_nav_snapshot_corpaction_error_selfcheck.py" "bin/portfolio_status_selfcheck.py"; do
  out=$("${E[@]}" NO_GCE_CHECK=true PYTHONDONTWRITEBYTECODE=1 MIKE_BOT_TEST_MODE=1 python3 $c 2>&1); r=$?
  echo "[$tz] rc=$r $c :: $(echo "$out" | grep -v '^\s*$' | tail -1 | cut -c1-200)"
  [ $r -ne 0 ] && { rc=1; echo "$out" | tail -15; }
done
exit $rc
