#!/bin/bash
# chạy hàng đợi chân: mỗi dòng "<sb|sbv> <TAG> KEY=VAL..."; song song P (mặc định 4) — trần RAM §32
cd "$(dirname "$0")"; P=${P:-4}
xargs -P "$P" -L 1 bash -c 'SB=$0 ./run_leg.sh "$@"' < "$1"; echo "QUEUE_DONE $1"
