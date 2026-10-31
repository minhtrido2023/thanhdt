#!/bin/bash
# chạy 3 biến thể TZ của report_v2_selfcheck song song, log riêng từng biến thể
cd /home/trido/wt-report-v2-r3-20261031 || exit 1
export WC_ROOT=/home/trido/thanhdt/WorkingClaude
L=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/report_v2_r3_20261031/selfcheck
python3 bin/report_v2_selfcheck.py > "$L/default.log" 2>&1 & p1=$!
env -u TZ python3 bin/report_v2_selfcheck.py > "$L/unsetTZ.log" 2>&1 & p2=$!
TZ=America/New_York python3 bin/report_v2_selfcheck.py > "$L/newyork.log" 2>&1 & p3=$!
wait $p1; echo "default rc=$?" >> "$L/rc.txt"
wait $p2; echo "unsetTZ rc=$?" >> "$L/rc.txt"
wait $p3; echo "newyork rc=$?" >> "$L/rc.txt"
echo DONE >> "$L/rc.txt"
