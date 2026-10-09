#!/bin/bash
# Stage 2: độ nhạy sổ lệnh (code mới, universe v2, BROKEN) + UNCLEAR + universe v1 (code mới & cũ, mọi ngày).
cd "$(dirname "$0")"
PY=/home/trido/thanhdt/wc_venv/bin/python
$PY casedays.py 10
{ for cfg in "0.25 1" "0.25 3" "0.5 1" "1 1" "1 3"; do set -- $cfg
    for s in 0 1 2 3 4 5 6 7 8 9; do echo "new v2 BROKEN $1 $2 days/case_$s.txt c$s"; done; done
  for s in 0 1 2 3 4 5 6 7 8 9; do echo "new v2 UNCLEAR 0.5 3 days/case_$s.txt c$s"; done
  for c in new old; do for s in 0 1 2 3 4 5 6 7 8 9 live; do f=days/hist_$s.txt; [ $s = live ] && f=days/live.txt
    echo "$c v1 BROKEN 0.5 3 $f s$s"; done; done; } | xargs -P 14 -L 1 bash -c \
  '$0 replay_v2.py --code $1 --universe $2 --scenario $3 --depth-mult $4 --ticks $5 --days $6 --tail 3 --out runs/$2_$1_$3_d$4_t$5_$7 > logs/$2_$1_$3_d$4_t$5_$7.log 2>&1' $PY
echo STAGE2_DONE
