#!/usr/bin/env bash
# Sinh THỬ khối danh mục báo cáo ngày (không gửi gì, không gọi eod_trading_report.sh — tránh
# daily_nav_snapshot/notify/mismatch-file) rồi chạy cổng trên chính output đó. Đo thời gian.
set -uo pipefail
W=/home/trido/thanhdt/WorkingClaude/wt-dailyreturn-1010
M=/home/trido/thanhdt/WorkingClaude/mike
R=$M/agents/Taylor/research/daily_return_gate_20261010/trial
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
cd /home/trido/thanhdt/WorkingClaude
for D in 2026-10-02 2026-10-09; do
  MEMO="$(mktemp -d /tmp/taylor_k1_memo.XXXXXX)"
  for A in ZaloPay SpaceX; do
    F="$R/${A}_daily_report_${D}.md"
    t0=$(date +%s)
    DAR_BQ_MEMO_DIR="$MEMO" python3 $W/bin/portfolio_status.py --account "$A" --date "$D" > "$R/ps_${A}_${D}.out" 2> "$R/ps_${A}_${D}.err"; rc=$?
    t1=$(date +%s)
    { printf '📊 **EOD Trading Report — %s (%s)**\n\n' "$A" "$D"; cat "$R/ps_${A}_${D}.out"; printf '\n(bản SINH THỬ — chỉ khối danh mục; phần lệnh/NAV không đổi trong nhánh này)\n'; } > "$F"
    DAR_BQ_MEMO_DIR="$MEMO" python3 $W/bin/report_return_gate.py --report "$F" > "$R/gate_${A}_${D}.txt" 2>&1; grc=$?
    t2=$(date +%s)
    echo "TRIAL $A $D portfolio_status rc=$rc $((t1-t0))s | gate(memo ấm) rc=$grc $((t2-t1))s | memo files=$(ls "$MEMO" | wc -l)"
  done
  rm -rf "$MEMO"
done
# đối chứng thời gian: cổng KHÔNG sổ nhớ trên cùng file
for A in ZaloPay SpaceX; do
  F="$R/${A}_daily_report_2026-10-02.md"; t0=$(date +%s)
  python3 $W/bin/report_return_gate.py --report "$F" > "$R/gate_nomemo_${A}_2026-10-02.txt" 2>&1; grc=$?
  echo "TRIAL-NOMEMO $A 2026-10-02 gate rc=$grc $(( $(date +%s)-t0 ))s"
done
echo ALLDONE
