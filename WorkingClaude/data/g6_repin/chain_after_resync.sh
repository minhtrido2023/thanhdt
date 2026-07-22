#!/usr/bin/env bash
# G6 chain (job Taylor_20260722_112850): chờ resync 3 bảng lớn xong -> delta các bảng còn lại ->
# verify TOÀN BỘ -> chạy A/B trên cache ĐÓNG BĂNG.
#
# Vì sao có 2 chân control giống hệt nhau (control_c, control_c2):
#   Hai lần chạy control trên LIVE BQ hôm nay (16:59 / 17:15) cho 27,26% vs 27,63% — CÙNG config,
#   CÙNG 713.818 dòng signal, chỉ khác từ book BAL trở đi. Chưa phân biệt được 2 giả thuyết:
#     (H1) engine BAL không tất định (tie-break theo thứ tự dòng / iteration set), hoặc
#     (H2) BQ upstream ghi đè bảng GIỮA hai lần chạy (live BQ = mục tiêu di động).
#   Cache đóng băng loại bỏ H2. control_c == control_c2  => H2 (dữ liệu trôi).
#                                control_c != control_c2 => H1 (engine không tất định).
#   Không đo cái này thì KHÔNG kết luận được pit-vs-prune, vì chênh lệch pit (+0,49pp) NHỎ HƠN
#   chênh lệch giữa hai chân control (0,37pp).
set -u
cd /home/trido/thanhdt/WorkingClaude
OUT=data/g6_repin
PYEXE=/home/trido/thanhdt/wc_venv/bin/python

echo "[chain] $(date -u +%FT%TZ) waiting for resync pid ${RESYNC_PID:-none}..."
while [ -n "${RESYNC_PID:-}" ] && kill -0 "$RESYNC_PID" 2>/dev/null; do sleep 60; done
echo "[chain] $(date -u +%FT%TZ) resync of 3 big tables finished"

# 1) Delta các bảng còn lại (nhỏ, nhanh) — cần verified:true TOÀN CỤC mới dùng được cache.
$PYEXE sync_bq_cache.py --delta --skip-verify \
  --tables ticker_financial ticker_1m vnindex_5state_dt5g_live vnindex_5state \
           vnindex_5state_tam_quan_v34b_clean vnindex_5state_dt_4gate \
           fa_ratings fa_ratings_8l custom30v_8l custom30_8l risk_rating \
  > $OUT/delta_rest.log 2>&1
echo "[chain] delta_rest exit=$?"

# 2) Verify toàn bộ (KHÔNG nới lỏng — verify là lớp bảo vệ chính)
$PYEXE sync_bq_cache.py --verify > $OUT/verify_after_fix.log 2>&1
VERIFY_RC=$?
echo "[chain] verify exit=$VERIFY_RC"
if [ "$VERIFY_RC" -ne 0 ]; then
  echo "[chain] VERIFY FAILED — DỪNG, không chạy A/B trên cache chưa verify"
  touch $OUT/CHAIN_FAILED_VERIFY
  exit 1
fi

# 3) A/B trên cache đóng băng. Lệnh pin nguyên văn (results_registry dòng 2800) + $DNA_PYEXE.
source ./wc_env.sh
run_leg() {  # $1=UNIVERSE_SRC $2=EXP_TAG $3=logfile
  env BQ_LOCAL_CACHE=1 BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap \
      BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" AUDIT_END=2026-06-19 \
      UNIVERSE_SRC="$1" EXP_TAG="$2" \
      "$DNA_PYEXE" pt_v23_audit_2014.py v23a none postbull 0 edge > "$OUT/$3" 2>&1
  echo "EXIT=$? ($1/$2)" >> "$OUT/$3"
}
run_leg prune repinR3control_c  cache_control.log
run_leg prune repinR3control_c2 cache_control2.log   # chân đo NHIỄU (trùng config với trên)
run_leg pit   repinR3pit_c      cache_pit.log
touch $OUT/DONE_CACHE_AB
echo "[chain] $(date -u +%FT%TZ) DONE"
