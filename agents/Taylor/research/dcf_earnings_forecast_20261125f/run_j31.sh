#!/usr/bin/env bash
# J3.1: chạy lại C của J2/J3 (D0,C1,C2,C3,EP) và C' của J3 (D0,C2,C4,C5,EP × ALL/CYC/REST) trên panel V3.2 (in/vp2.parquet = ..e/out_panel/vp2.parquet).
# Code đo d_metrics2.py V3.1 nguyên văn (..d/in_snapshot_v31). events + đặc trưng chu kỳ tái dùng từ J3 (..d/out_J3, ..d/out_CY: không phụ thuộc mc).
set -euo pipefail
D="$(cd "$(dirname "$0")" && pwd)"; J3="$D/../dcf_earnings_forecast_20261125d"; PY=/home/trido/thanhdt/wc_venv/bin/python; S="$J3/in_snapshot_v31/d_metrics2.py"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
OC="$D/out_J3C"; mkdir -p "$OC"
( cd "$D/calc" && SNAP_DIR="$D/in" OUT_DIR="$J3/out_J3" OC_DIR="$OC" "$PY" d_update.py > "$OC/d.log" 2>&1 )
( cd "$OC" && OUT_DIR="$OC" ONLY=D0,C1,C2,C3,EP SFX=_C "$PY" "$S" > "$OC/m.log" 2>&1 )
( cd "$D/calc" && OC_DIR="$OC" VARIANTS=C1,C2,C3 "$PY" e_cdiff.py > "$OC/e.log" 2>&1 )
( cd "$D/calc" && "$PY" g_cycle_update.py > "$D/g.log" 2>&1 )
for t in ALL CYC REST; do
  ( cd "$D/out_CYC_$t" && OUT_DIR="$PWD" ONLY=D0,C2,C4,C5,EP SFX=_C "$PY" "$S" > m.log 2>&1 && cd "$D/calc" && OC_DIR="$D/out_CYC_$t" VARIANTS=C2,C4,C5 "$PY" e_cdiff.py > "$D/out_CYC_$t/e.log" 2>&1 && echo "done $t" ) &
done; wait
( cd "$D/calc" && "$PY" h_dsr.py > "$D/out_CYC_ALL/h.log" 2>&1 )
echo done
