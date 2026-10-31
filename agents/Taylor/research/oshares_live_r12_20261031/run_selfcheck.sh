#!/bin/bash
# R12: oshares_dcf_selfcheck trên WT ở 3 TZ (TUẦN TỰ: 3 bq CLI song song từng treo 16:45), log run_selfcheck_{UTC,noTZ,ICT}.txt
cd /home/trido/wt-oshares-r12-20261031/WorkingClaude
export PYTHONUNBUFFERED=1 MIKE_BOT_TEST_MODE=1 DCF_OS_OPS_HEALTH=/home/trido/wt-oshares-r12-ops-20261031/bin/ops_health_check.sh DCF_OS_LAG_DD_PACK=/home/trido/wt-oshares-r12-ops-20261031/bin/lag_dd_pack.py
for z in UTC noTZ ICT; do
  case $z in UTC) pre="env TZ=UTC";; noTZ) pre="env -u TZ";; ICT) pre="env TZ=Asia/Ho_Chi_Minh";; esac
  $pre timeout 3000 /home/trido/thanhdt/wc_venv/bin/python /home/trido/wt-oshares-r12-ops-20261031/agents/Taylor/research/oshares_live_r12_20261031/run_wt.py /home/trido/wt-oshares-r12-20261031/WorkingClaude /home/trido/wt-oshares-r12-20261031/WorkingClaude/oshares_dcf_selfcheck.py > /home/trido/wt-oshares-r12-ops-20261031/agents/Taylor/research/oshares_live_r12_20261031/run_selfcheck_$z.txt 2>&1; echo "rc=$?" >> /home/trido/wt-oshares-r12-ops-20261031/agents/Taylor/research/oshares_live_r12_20261031/run_selfcheck_$z.txt
done
wait
