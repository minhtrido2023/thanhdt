#!/bin/bash
# chạy selfcheck liên quan trên WT (qua run_wt.py) và PROD (đối chứng), 2 TZ
LOG=/home/trido/wt-oshares-r11-ops-20261031/agents/Taylor/research/oshares_live_r11_20261031; WT=/home/trido/wt-oshares-r11-20261031/WorkingClaude; PROD=/home/trido/thanhdt/WorkingClaude
export MIKE_BOT_TEST_MODE=1
L="dcf_rate_frame_selfcheck.py dcf_check_selfcheck.py dcf_selector_selfcheck.py dcf_refresh_gate_selfcheck.py dcf_earning_power_test.py tz_asof_ict_dd_dcf_selfcheck.py due_diligence_selfcheck.py custom_basket_forensic_failclosed_selfcheck.py basket_oshares_step_exdate_selfcheck.py basket_price_basis_audit_selfcheck.py basket_price_basis_selfcheck.py basket_return_leg_oshares_selfcheck.py test_trading_bot.py test_multi_strategy.py"
run() { tag=$1; root=$2; tzmode=$3; out=$LOG/sc_${tag}_${tzmode}.txt; : > $out
  for f in $L; do
    if [ "$tzmode" = UTC ]; then pre="env TZ=UTC"; else pre="env -u TZ"; fi
    if [ "$tag" = wt ]; then cmd="/home/trido/thanhdt/wc_venv/bin/python $LOG/run_wt.py $root $root/$f"; else cmd="/home/trido/thanhdt/wc_venv/bin/python $root/$f"; fi
    ( cd $root && timeout 1500 $pre $cmd > $LOG/sc_${tag}_${tzmode}_$f.log 2>&1 ); rc=$?
    echo "== $f rc=$rc :: $(grep -v 'CPI COVERAGE' $LOG/sc_${tag}_${tzmode}_$f.log | grep -E 'run_wt|PASS|FAIL|OK|ALL' | tail -n 2 | tr '\n' ' ' | cut -c1-260)" >> $out
  done; }
run wt $WT UTC & run wt $WT noTZ & run prod $PROD UTC & wait
