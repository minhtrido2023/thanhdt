#!/bin/bash
# Stage 1: BROKEN cấu hình gốc (sổ 0,5× KL/phút, 3 bước giá), universe v2, code MỚI và CŨ, mọi ngày.
cd "$(dirname "$0")"
PY=/home/trido/thanhdt/wc_venv/bin/python
{ for c in new old; do for s in 0 1 2 3 4 5 6 7 8 9 live; do f=days/hist_$s.txt; [ $s = live ] && f=days/live.txt
    echo "$c $s $f"; done; done; } | xargs -P 14 -L 1 bash -c \
  'mkdir -p logs; $0 replay_v2.py --code $1 --universe v2 --scenario BROKEN --depth-mult 0.5 --ticks 3 --days $3 --out runs/v2_$1_BROKEN_d0.5_t3_s$2 > logs/v2_$1_BROKEN_d0.5_t3_s$2.log 2>&1' $PY
echo STAGE1_DONE
