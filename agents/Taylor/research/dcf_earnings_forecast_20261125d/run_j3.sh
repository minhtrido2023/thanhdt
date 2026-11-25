#!/usr/bin/env bash
# J3: chạy lại C trên panel V3.1. Dùng: bash run_j3.sh <OC_dir> <ONLY models> [ROUTE_STATIC=1 ...env]
set -euo pipefail
D="$(cd "$(dirname "$0")" && pwd)"; PY=/home/trido/thanhdt/wc_venv/bin/python
export SNAP_DIR="$D/in_snapshot_v31" OUT_DIR="$D/out_J3"
OC="$D/$1"; mkdir -p "$OC"
cd "$D/calc"; OC_DIR="$OC" "$PY" "${DUPD:-d_update.py}" > "$OC/d.log" 2>&1
cd "$OC"; OUT_DIR="$OC" ONLY="$2" SFX=_C "$PY" "$D/in_snapshot_v31/d_metrics2.py" > "$OC/m.log" 2>&1
if [ -n "${VARIANTS:-}" ]; then cd "$D/calc"; OC_DIR="$OC" "$PY" e_cdiff.py > "$OC/e.log" 2>&1; fi
echo "done $1"
