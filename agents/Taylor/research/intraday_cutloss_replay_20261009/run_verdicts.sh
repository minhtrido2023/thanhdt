#!/bin/bash
cd "$(dirname "$0")"
PY=/home/trido/thanhdt/wc_venv/bin/python
for S in BROKEN UNCLEAR; do for i in 0 1 2 3; do
  nohup $PY replay.py --scenario $S --days ledger_case_days_$i.txt --out runs/ledger${i}_${S}_d0.5 > ledger_${S}_$i.log 2>&1 &
done; done
