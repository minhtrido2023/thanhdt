#!/bin/bash
# Publish leg cho TICKET 1 (vòng review 2, job Taylor_20260927_052432): chạy `custom30_history.py`
# — ĐƯỜNG PUBLISH THẬT — với `custom_basket.py` CỦA WORKTREE, `bq load` bị chặn bằng stub PATH.
# Khác vòng 1 ở ĐÚNG MỘT điểm: BASKET_CA_SNAPSHOT được TRUYỀN VÀO, nên claim "0/30 tên đổi ở rebal
# 2026-08-05" đứng trên vintage corp-action ĐÃ GHIM chứ không trên một lần đọc live BQ (bảng đó bị
# UPSERT in-place — vòng 1 in "corp-action LIVE BQ: 4466 dòng", không tái lập được sau này).
# $1 = quarter | exdate
set -u
MODE="$1"
WT=/home/trido/thanhdt/wt-c30v-wexdate/WorkingClaude
OUT=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/oshares_weight_exdate_20260927
export PATH="/tmp/nobq:$PATH:/home/trido/google-cloud-sdk/bin"
export CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
export DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python
export TZ=Asia/Ho_Chi_Minh
cd "$WT" || exit 9
env BASKET_OSHARES_STEP="$MODE" \
    BASKET_CA_SNAPSHOT=/home/trido/thanhdt/WorkingClaude/data/snapshots/corp_action_share_20260927.parquet \
    BASKET_SELECT=yieldcombo \
    CUSTOM30_TABLE=lithe-record-440915-m9:tav2_bq.custom30v_8l \
    CUSTOM30_CSV="custom30v_8l_publish_expwexdate2_${MODE}.csv" \
    BQ_LOCAL_CACHE=data/bq_cache BQ_CACHE_THREADS=1 \
    "$DNA_PYEXE" "$OUT/../c30v_retleg_repin_20260927/run_with_wt_basket.py" \
        "$WT" "$WT/custom30_history.py" > "$OUT/publish2_${MODE}.log" 2>&1
echo "EXIT=$? (publish $MODE)" >> "$OUT/publish2_${MODE}.log"
