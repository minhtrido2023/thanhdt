#!/usr/bin/env bash
# restate_guard_selfcheck.sh — selfcheck cho restate_guard.sh.
#
# Mục tiêu chính: MÔ PHỎNG LẠI ĐÚNG SỰ KIỆN 2026-07-29 (101 phiên đổi ở
# vnindex_5state_dt5g_live) để chứng minh cơ chế mới SẼ BẮT được nó — hôm đó nó lọt qua
# hoàn toàn im lặng vì dt5g_live không hề có snapshot predeploy để so.
#
# Bảng "predeploy giả" được dựng bằng cách LẤY dt5g_live hiện tại rồi HOÀN NGUYÊN đúng 101
# phiên theo bảng old->new trong RCA (mục 3), tức tái tạo lại trạng thái bảng NGAY TRƯỚC
# lần refresh hôm nay. Nguồn: mike/agents/Winston/research/dt5g_history_restate_rca_20260729.md
# (state: 1=CRISIS 2=BEAR 3=NEUTRAL 4=BULL 5=EXBULL)
#
# Chạy read-mostly: chỉ tạo/xoá bảng tạm `_wg_selfcheck_*` trong tav2_bq, KHÔNG đụng bảng
# production nào. Guard luôn chạy ở RESTATE_GUARD_DRYRUN=1 nên không gửi alert thật.
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

PJ="lithe-record-440915-m9"
DS="tav2_bq"
SUF="$$"
T_OLD="_wg_selfcheck_old_$SUF"        # predeploy giả (đã hoàn nguyên 101 phiên)
T_SAME="_wg_selfcheck_same_$SUF"      # bản sao y hệt live (churn = 0)
T_RECENT="_wg_selfcheck_recent_$SUF"  # chỉ khác ở vùng < T-30 ngày (phải bị bỏ qua)
T_DROP="_wg_selfcheck_drop_$SUF"      # thiếu 1 dòng lịch sử (phải đếm là n_added)
HIST="/tmp/restate_guard_selfcheck_$SUF.jsonl"
LIVE="$PJ.$DS.vnindex_5state_dt5g_live"

pass=0; fail=0
cleanup() { for t in "$T_OLD" "$T_SAME" "$T_RECENT" "$T_DROP"; do bq rm -f -t "$PJ:$DS.$t" >/dev/null 2>&1; done; rm -f "$HIST"; }
trap cleanup EXIT

bqq() { bq query --use_legacy_sql=false --project_id="$PJ" --quiet "$1" >/dev/null 2>&1; }

# giá trị CŨ của 101 phiên bị viết lại hôm 2026-07-29 (RCA mục 3)
OLD_CASE="CASE
  WHEN time BETWEEN '2018-02-27' AND '2018-03-16' THEN 4   -- BULL  -> (mới) NEUTRAL, 14 phiên
  WHEN time BETWEEN '2018-03-19' AND '2018-03-21' THEN 1   -- CRISIS-> NEUTRAL, 3
  WHEN time BETWEEN '2018-03-22' AND '2018-05-08' THEN 1   -- CRISIS-> BULL,    31
  WHEN time = '2019-12-10'                        THEN 2   -- BEAR  -> NEUTRAL, 1
  WHEN time BETWEEN '2020-03-16' AND '2020-04-03' THEN 2   -- BEAR  -> CRISIS,  14
  WHEN time = '2020-05-26'                        THEN 3   -- NEUTRAL-> CRISIS, 1
  WHEN time = '2020-12-28'                        THEN 4   -- BULL  -> EXBULL,  1
  WHEN time IN ('2022-11-01','2022-12-14')        THEN 1   -- CRISIS-> BEAR,    2
  WHEN time BETWEEN '2023-02-07' AND '2023-03-16' THEN 3   -- NEUTRAL-> BEAR,   28
  WHEN time BETWEEN '2023-04-04' AND '2023-04-11' THEN 3   -- NEUTRAL-> BEAR,   6
  ELSE state END"

echo "=== dựng bảng tạm ==="
bqq "CREATE OR REPLACE TABLE \`$PJ.$DS.$T_OLD\` AS
     SELECT time, $OLD_CASE AS state, state_raw FROM \`$LIVE\`" || { echo "FATAL: không tạo được $T_OLD"; exit 1; }
bqq "CREATE OR REPLACE TABLE \`$PJ.$DS.$T_SAME\` AS SELECT * FROM \`$LIVE\`" || { echo "FATAL"; exit 1; }
bqq "CREATE OR REPLACE TABLE \`$PJ.$DS.$T_RECENT\` AS
     SELECT time, IF(time >= DATE_SUB(CURRENT_DATE('Asia/Ho_Chi_Minh'), INTERVAL 5 DAY), 9, state) AS state, state_raw
     FROM \`$LIVE\`" || { echo "FATAL"; exit 1; }
bqq "CREATE OR REPLACE TABLE \`$PJ.$DS.$T_DROP\` AS
     SELECT * FROM \`$LIVE\` WHERE time != '2018-04-02'" || { echo "FATAL"; exit 1; }

# run <old_table> <expect_exit> <expect_n_total> <name> [threshold]
run() {
  local old="$1" xrc="$2" xtot="$3" name="$4" thr="${5:-5}"
  : > "$HIST"
  RESTATE_GUARD_DRYRUN=1 RESTATE_GUARD_HISTORY="$HIST" RESTATE_ALERT_THRESHOLD="$thr" \
    ./restate_guard.sh "$LIVE" "$PJ.$DS.$old" "SELFCHECK $name" > "/tmp/rg_out_$SUF.txt" 2>&1
  local rc=$?
  local tot; tot="$(python3 -c "
import json,sys
try:
    print(json.loads(open('$HIST').read().strip().splitlines()[-1])['n_total'])
except Exception:
    print('ERR')
")"
  if [ "$rc" = "$xrc" ] && [ "$tot" = "$xtot" ]; then
    echo "  PASS  $name  (exit=$rc n_total=$tot)"; pass=$((pass+1))
  else
    echo "  FAIL  $name  (exit=$rc kỳ vọng $xrc · n_total=$tot kỳ vọng $xtot)"; fail=$((fail+1))
    sed 's/^/        /' "/tmp/rg_out_$SUF.txt"
  fi
  rm -f "/tmp/rg_out_$SUF.txt"
}

echo
echo "=== T1: MÔ PHỎNG SỰ KIỆN 2026-07-29 trên dt5g_live (kỳ vọng BẮT được, 101 phiên) ==="
run "$T_OLD" 2 101 "dt5g_live restate 101 phiên"

echo "=== T2: không có restate (bản sao y hệt) -> quiet, không alert ==="
run "$T_SAME" 0 0 "no-restate quiet path"

echo "=== T3: chỉ đổi trong 30 ngày gần đây -> phải BỎ QUA (đổi hợp lệ) ==="
run "$T_RECENT" 0 0 "recent-window ignored"

echo "=== T4: 1 dòng lịch sử biến mất/xuất hiện -> đếm là restate ==="
run "$T_DROP" 0 1 "row add/drop counted (1 <= ngưỡng 5, quiet)"

echo "=== T5: ngưỡng cao (200) trên đúng sự kiện 101 -> không alert ==="
run "$T_OLD" 0 101 "threshold honored" 200

echo "=== T6: bảng archive không tồn tại -> exit 1 (advisory, KHÔNG die) ==="
RESTATE_GUARD_DRYRUN=1 RESTATE_GUARD_HISTORY="$HIST" \
  ./restate_guard.sh "$LIVE" "$PJ.$DS._wg_no_such_table_$SUF" "SELFCHECK missing archive" >/dev/null 2>&1
rc=$?
if [ "$rc" = 1 ]; then echo "  PASS  missing-archive -> exit 1"; pass=$((pass+1));
else echo "  FAIL  missing-archive -> exit $rc (kỳ vọng 1)"; fail=$((fail+1)); fi

echo
echo "=== KẾT QUẢ: $pass PASS / $fail FAIL ==="
[ "$fail" = 0 ]
