#!/bin/bash
# runs queue.txt lines: <TAG> KEY=VAL... with -P 4 (RAM ~1.3-3GB/leg; §32 ceiling)
cd "$(dirname "$0")"
xargs -P 4 -L 1 bash -c './run_leg.sh "$0" BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.0 "$@"' < queue.txt
echo QUEUE_DONE > logs/QUEUE_DONE
