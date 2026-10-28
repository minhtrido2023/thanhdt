#!/bin/bash
# bal_concentration_cap leg runner — job Taylor_20261022_095008. Env copied VERBATIM from repin_park0_dep1m_20261008/run_leg.sh
# (= pin command in PINS.jsonl for 4707bcbe / bcd0469f). CODE = worktree wt-balcap-20261022 (f66dab18 + BAL_WMAX_NAV knob).
SRC=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-balcap-20261022/WorkingClaude
WC=/home/trido/thanhdt/WorkingClaude
OUT=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/bal_concentration_cap_20261022/logs
TAG="$1"; shift
cd "$WC" || exit 9
export WORKDIR_8L="$WC"
export PATH="$PATH:/home/trido/google-cloud-sdk/bin"
export CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
export DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python
export TZ=Asia/Ho_Chi_Minh
env "$@" \
BASKET_CA_SNAPSHOT=/home/trido/thanhdt/WorkingClaude/data/snapshots/corp_action_share_20260927.parquet \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3 \
/usr/bin/time -v $DNA_PYEXE "$SRC/pt_v23_audit_2014.py" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG $*)" >> "$OUT/$TAG.log"
