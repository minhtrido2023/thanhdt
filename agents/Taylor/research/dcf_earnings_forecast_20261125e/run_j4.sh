#!/usr/bin/env bash
# J4: đo D0/EP/P1/M1..M5 bằng d_metrics2.py V3.1 (nguyên văn, J3 in_snapshot_v31) trên ALL/CYC/REST
set -euo pipefail
D="$(cd "$(dirname "$0")" && pwd)"; PY=/home/trido/thanhdt/wc_venv/bin/python; S="$D/../dcf_earnings_forecast_20261125d/in_snapshot_v31/d_metrics2.py"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
for t in ALL CYC REST; do ( cd "$D/out_$t" && OUT_DIR="$PWD" ONLY=D0,EP,P1,M1,M2,M3,M4,M5 SFX=_J4 "$PY" "$S" > m.log 2>&1 && echo "done $t" ) & done; wait
