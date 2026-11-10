#!/bin/bash
# 4 chân R3 song song (-P 4, RAM ~1,3-3GB/chân theo bal-gate 2026-11-10; §32). Args giống pin "2026-10-08".
cd "$(dirname "$0")"; mkdir -p logs
xargs -P 4 -L 1 bash -c './run_leg.sh "$0" BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.0 "$@"' < "${1:-queue.txt}"
echo QUEUE_DONE > logs/QUEUE_DONE
