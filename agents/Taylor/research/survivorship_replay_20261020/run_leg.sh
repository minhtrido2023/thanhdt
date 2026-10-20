#!/bin/bash
# survivorship-sensitivity control leg runner — job Taylor_20261020_094204 (replay). Ban sao run_leg.sh / run_leg_main.sh cua
# repin_park0_dep1m_20261008 (pin 2026-10-08), CHI doi: SRC (tham so 1), CACHE (tham so 2), OUT. Moi env khac nguyen van.
# Usage: run_leg.sh <SRC_WC_DIR> <CACHE_DIR_rel> <TAG> KEY=VAL...
SRC="$1"; CACHE="$2"; TAG="$3"; shift 3
WC=/home/trido/thanhdt/WorkingClaude
OUT=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/survivorship_replay_20261020/logs
cd "$WC" || exit 9
export WORKDIR_8L="$WC"
export PATH="$PATH:/home/trido/google-cloud-sdk/bin"
export CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
export DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python
export TZ=Asia/Ho_Chi_Minh
env "$@" \
BASKET_CA_SNAPSHOT=/home/trido/thanhdt/WorkingClaude/data/snapshots/corp_action_share_20260927.parquet \
BQ_LOCAL_CACHE="$CACHE" BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
$DNA_PYEXE "$SRC/pt_v23_audit_2014.py" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG $SRC $CACHE $*)" >> "$OUT/$TAG.log"
