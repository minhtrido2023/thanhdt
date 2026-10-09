#!/bin/bash
cd "$(dirname "$0")"
PY=/home/trido/thanhdt/wc_venv/bin/python
for i in 0 1 2 3; do nohup $PY replay.py --scenario NONE --days ledger_days_$i.txt --out runs/ledger${i}_NONE_d0.5 --resume > ledger_none_${i}_r.log 2>&1 & done
