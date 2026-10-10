#!/usr/bin/env bash
# Chạy lại sinh thử + cổng 02/10 (2 tài khoản) trên CÂY CUỐI (mọi file bin/ mtime ≤ 20:34:56) — lượt
# run_round2_real.sh bắt đầu 20:24 trong khi dar/rrg còn được sửa lúc 20:28:52 ⇒ hai lượt
# portfolio_status 02/10 + cổng ZaloPay 02/10 của nó chạy trên code CŨ HƠN cây commit. Chỉ ĐỌC dữ liệu.
set -uo pipefail
W=/home/trido/thanhdt/WorkingClaude/wt-dailyreturn-1010
R=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/daily_return_gate_20261010/round2
T=$R/final_tree
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
cd /home/trido/thanhdt/WorkingClaude
one() { # account date
  local A=$1 D=$2 MEMO F t0 rc
  MEMO="$(mktemp -d /tmp/taylor_k1_memo.XXXXXX)"
  F="$T/${A}_daily_report_${D}.md"; t0=$(date +%s)
  DAR_BQ_MEMO_DIR="$MEMO" python3 $W/bin/portfolio_status.py --account "$A" --date "$D" > "$T/ps_${A}_${D}.out" 2> "$T/ps_${A}_${D}.err"; rc=$?
  { printf '📊 **EOD Trading Report — %s (%s)**\n\n' "$A" "$D"; cat "$T/ps_${A}_${D}.out"; printf '\n(bản SINH THỬ — chỉ khối danh mục; phần lệnh/NAV không đổi trong nhánh này)\n'; } > "$F"
  echo "TRIAL $A $D portfolio_status rc=$rc $(( $(date +%s)-t0 ))s"
  t0=$(date +%s)
  DAR_BQ_MEMO_DIR="$MEMO" python3 $W/bin/report_return_gate.py --report "$F" > "$T/gate_${A}_${D}.txt" 2>&1; rc=$?
  echo "GATE $A $D rc=$rc $(( $(date +%s)-t0 ))s | $(grep -m1 'Đã kiểm' "$T/gate_${A}_${D}.txt" | cut -c1-110) | $(grep -m1 '^❌ CHẶN\|^✅ PASS' "$T/gate_${A}_${D}.txt" | cut -c1-12)"
  echo "DIFF vs round2/trial ps_${A}_${D}.out: $(diff -q "$T/ps_${A}_${D}.out" "$R/trial/ps_${A}_${D}.out" >/dev/null && echo IDENTICAL || echo DIFFERENT)"
  rm -rf "$MEMO"
}
one ZaloPay 2026-10-02 &
one SpaceX 2026-10-02 &
wait
echo ALLDONE
