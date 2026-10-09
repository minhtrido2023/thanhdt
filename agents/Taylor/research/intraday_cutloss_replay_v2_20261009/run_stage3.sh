#!/bin/bash
# Stage 3: độ nhạy sổ lệnh trên universe v1 (có mã giá < 5.000đ), code mới, BROKEN, mọi ngày.
cd "$(dirname "$0")"
PY=/home/trido/thanhdt/wc_venv/bin/python
{ for cfg in "0.25 1" "0.25 3" "0.5 1" "1 1" "1 3"; do set -- $cfg
    for s in 0 1 2 3 4 5 6 7 8 9 live; do f=days/hist_$s.txt; [ $s = live ] && f=days/live.txt
      echo "new v1 BROKEN $1 $2 $f s$s"; done; done; } | xargs -P 14 -L 1 bash -c \
  '$0 replay_v2.py --code $1 --universe $2 --scenario $3 --depth-mult $4 --ticks $5 --days $6 --tail 3 --out runs/$2_$1_$3_d$4_t$5_$7 > logs/$2_$1_$3_d$4_t$5_$7.log 2>&1' $PY
echo STAGE3_DONE
