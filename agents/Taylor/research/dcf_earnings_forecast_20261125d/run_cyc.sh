#!/usr/bin/env bash
# J3 C': đo D0/C2/C4/C5/EP bằng d_metrics2.py V3.1 trên 3 phạm vi (sau calc/g_cycle_update.py)
set -euo pipefail
D="$(cd "$(dirname "$0")" && pwd)"; PY=/home/trido/thanhdt/wc_venv/bin/python
for t in ALL CYC REST; do
  ( cd "$D/out_CYC_$t" && OUT_DIR="$PWD" ONLY=D0,C2,C4,C5,EP SFX=_C "$PY" "$D/in_snapshot_v31/d_metrics2.py" > m.log 2>&1 && cd "$D/calc" && OC_DIR="$D/out_CYC_$t" VARIANTS=C2,C4,C5 "$PY" e_cdiff.py > "$D/out_CYC_$t/e.log" 2>&1 && echo "done $t" ) &
done; wait
