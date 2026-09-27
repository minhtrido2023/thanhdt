#!/bin/bash
# Moi truong PIN y nguyen lenh pin R3 (research/final_pin_20260927/run_pin.sh) — chi doi
# entrypoint sang dump_basket.py. Khong doi mot tham so nao anh huong so.
WC=/home/trido/thanhdt/WorkingClaude
OUT=$WC/mike/agents/Taylor/research/c30v_position_replay_20260927
cd "$WC" || exit 9
export WORKDIR_8L="$WC"
export PATH="$PATH:/home/trido/google-cloud-sdk/bin"
export CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
export DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python
export TZ=Asia/Ho_Chi_Minh
env \
BASKET_CA_SNAPSHOT=$WC/data/snapshots/corp_action_share_20260927.parquet \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
BASKET_WT=namecap BASKET_SELECT=yieldcombo \
$DNA_PYEXE "$OUT/dump_basket.py" > "$OUT/dump.log" 2>&1
echo "EXIT=$?" >> "$OUT/dump.log"
tail -25 "$OUT/dump.log"
