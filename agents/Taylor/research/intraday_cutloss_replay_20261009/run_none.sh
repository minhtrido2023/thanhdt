#!/bin/bash
cd "$(dirname "$0")"
PY=/home/trido/thanhdt/wc_venv/bin/python
nohup $PY replay.py --scenario NONE --days live_days.txt --out runs/live_NONE_d0.5 > live_none.log 2>&1 &
for i in 0 1 2 3; do nohup $PY replay.py --scenario NONE --days ledger_days_$i.txt --out runs/ledger${i}_NONE_d0.5 > ledger_none_$i.log 2>&1 & done
