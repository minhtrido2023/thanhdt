#!/bin/bash
# BAL shadow (KHÔNG cổng) = engine pinned R3 knob live (namecap/yieldcombo/park 3:0.0), data bq_cache local (0 BQ).
# Usage: run_shadow.sh <AUDIT_END YYYY-MM-DD> <TAG>
WC=/home/trido/thanhdt/WorkingClaude
SRC=${SRC:-/home/trido/thanhdt/WorkingClaude/wt-bal-edge-gate-20261110/WorkingClaude}
OUT=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/bal_edge_gate_20261110/logs
END="$1"; TAG="$2"
cd "$WC" || exit 9
export WORKDIR_8L="$WC" PATH="$PATH:/home/trido/google-cloud-sdk/bin" CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
export DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python TZ=Asia/Ho_Chi_Minh
env BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.0 \
  BASKET_CA_SNAPSHOT=$WC/data/snapshots/corp_action_share_20260927.parquet \
  BQ_LOCAL_CACHE=data/bq_cache BQ_CACHE_THREADS=1 OMP_NUM_THREADS=1 \
  NAV_TOTAL_B=50 ETF_LIQ=custompitg AUDIT_END="$END" EXP_TAG="$TAG" \
  /usr/bin/time -v $DNA_PYEXE "$SRC/pt_v23_audit_2014.py" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG END=$END)" >> "$OUT/$TAG.log"
