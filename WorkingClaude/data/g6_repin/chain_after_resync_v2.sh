#!/usr/bin/env bash
# G6 A/B — BẢN V2 (job Taylor_20260722_151919). Chạy lại 3 chân trên cache ĐÓNG BĂNG cho ĐÚNG.
#
# Vì sao phải chạy lại: bản v1 (chain_after_resync.sh + run_cache_ab.sh) đặt `BQ_LOCAL_CACHE=1`,
# copy nguyên văn từ lệnh pin ở results_registry.md L2800 — nhưng biến này là ĐƯỜNG DẪN
# (bq_local_cache.py dòng 3), nên "1" ⇒ không có manifest tại ./1/manifest.json ⇒ ÂM THẦM rơi về
# live BQ. Toàn bộ 3 chân chạy 21:23–21:51 hôm nay do đó KHÔNG đo trên cache đóng băng ⇒ hỏng
# mục đích A/B (không tách được H1 engine không tất định vs H2 dữ liệu BQ trôi).
# Lệnh pin đã được sửa trong registry (commit c592a74).
#
# 3 chân giữ nguyên thiết kế v1:
#   control_c, control_c2 = CÙNG config (chân đo NHIỄU). Cache đóng băng loại bỏ H2.
#     control_c == control_c2 ⇒ H2 (dữ liệu trôi giữa 2 lần chạy live).
#     control_c != control_c2 ⇒ H1 (engine không tất định) — và khi đó delta pit (+0,49pp)
#     nhỏ hơn nhiễu (0,37pp) nên KHÔNG kết luận được pit-vs-prune.
#   pit_c = chân đo thật (UNIVERSE_SRC=pit).
#
# Bỏ bước chờ resync + delta: 3 bảng lớn đã resync xong, manifest verified:true (14:22:24Z,
# 14/14 bảng) — kiểm tra lại ngay dưới đây thay vì tin giả định.
set -u
cd /home/trido/thanhdt/WorkingClaude
OUT=data/g6_repin
source ./wc_env.sh

# Cổng: cache PHẢI verified:true, nếu không thì dừng (không lặp lại lỗi chạy trên cache bẩn).
/home/trido/thanhdt/wc_venv/bin/python - <<'PY' || { echo "[v2] CACHE NOT VERIFIED — DUNG"; touch $OUT/CHAIN_V2_FAILED_VERIFY; exit 1; }
import json, sys
m = json.load(open("data/bq_cache/manifest.json"))
print(f"[v2] manifest verified={m.get('verified')} at {m.get('verified_at')} tables={len(m.get('tables',{}))}")
sys.exit(0 if m.get("verified") else 1)
PY

run_leg() {  # $1=UNIVERSE_SRC $2=EXP_TAG $3=logfile
  echo "[v2] $(date -u +%FT%TZ) START $1/$2 -> $3"
  env BQ_LOCAL_CACHE=data/bq_cache BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg \
      BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" AUDIT_END=2026-06-19 \
      UNIVERSE_SRC="$1" EXP_TAG="$2" \
      "$DNA_PYEXE" pt_v23_audit_2014.py v23a none postbull 0 edge > "$OUT/$3" 2>&1
  echo "EXIT=$? ($1/$2)" >> "$OUT/$3"
  echo "[v2] $(date -u +%FT%TZ) END   $1/$2"
}

run_leg prune repinR3control_v2c  cache_v2_control.log
run_leg prune repinR3control_v2c2 cache_v2_control2.log
run_leg pit   repinR3pit_v2c      cache_v2_pit.log
touch $OUT/DONE_CACHE_AB_V2
echo "[v2] $(date -u +%FT%TZ) DONE"
