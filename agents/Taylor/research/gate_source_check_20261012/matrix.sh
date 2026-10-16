#!/usr/bin/env bash
# 13 selfcheck (mọi file selfcheck có nhắc bq_freshness_check / send_plan_report.sh / gate_source_check
# + ops_health_check_selfcheck vì check 13 đọc cùng golive_state_today.json) × 4 môi trường TZ.
cd "$1" || exit 1
S="bq_freshness_check_selfcheck.py send_plan_report_state_gate_selfcheck.py send_plan_report_aei_notes_selfcheck.py send_plan_report_park_jit_selfcheck.py dt5g_publisher_gate_selfcheck.sh bq_price_freeze_gate_selfcheck.py plan_position_drift_check_selfcheck.py wait_for_artifact_selfcheck.py retro_escalate_selfcheck.py dispatch_round_cap_selfcheck.py dispatch_discord_topic_selfcheck.sh code_quality_autodispatch_selfcheck.sh ops_health_check_selfcheck.py"
printf '%-46s %-10s %-10s %-22s %-20s\n' selfcheck mặc-định "env -u TZ" America/Los_Angeles Pacific/Kiritimati
tot=0; bad=0
for s in $S; do
  case "$s" in *.py) run="python3 bin/$s";; *) run="bash bin/$s";; esac
  row=""
  for mode in default unset LA KI; do
    case $mode in
      default) out=$($run 2>&1); rc=$?;;
      unset)   out=$(env -u TZ $run 2>&1); rc=$?;;
      LA)      out=$(TZ=America/Los_Angeles $run 2>&1); rc=$?;;
      KI)      out=$(TZ=Pacific/Kiritimati $run 2>&1); rc=$?;;
    esac
    tot=$((tot+1)); [ $rc -ne 0 ] && { bad=$((bad+1)); echo "--- FAIL $s [$mode] rc=$rc ---"; echo "$out" | tail -15; }
    row="$row rc=$rc      "
  done
  printf '%-46s %s\n' "$s" "$row"
done
echo "TỔNG: $tot lượt chạy, $bad lượt rc≠0"
