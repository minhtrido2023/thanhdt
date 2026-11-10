#!/bin/bash
# Env y lệnh pin R3 (registry "2026-10-08"), chỉ khác: cwd/WORKDIR = sandbox chọn bởi knob LAG_CACHE_BASIS
# (canonical ⇒ sandbox_ctrl = data/ canonical nguyên trạng; adjusted ⇒ sandbox_adj = 4 file LAG dẫn xuất từ pkl
# adjusted, xem make_sandbox.sh). Usage: run_leg.sh <TAG> LAG_CACHE_BASIS=canonical|adjusted KEY=VAL...
R="$(cd "$(dirname "$0")" && pwd)"; TAG="$1"; shift
BASIS=""; for a in "$@"; do case "$a" in LAG_CACHE_BASIS=*) BASIS="${a#LAG_CACHE_BASIS=}";; esac; done
case "$BASIS" in canonical) SB=ctrl;; adjusted) SB=adj;; *) echo "thiếu LAG_CACHE_BASIS=canonical|adjusted" >&2; exit 8;; esac
S="$R/sandbox_$SB"; OUT="$R/logs"; mkdir -p "$OUT"
cd "$S" || exit 9
export WORKDIR_8L=/home/trido/thanhdt/WorkingClaude
export PATH="$PATH:/home/trido/google-cloud-sdk/bin"
export CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
export DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python
export TZ=Asia/Ho_Chi_Minh
env "$@" \
BASKET_CA_SNAPSHOT=/home/trido/thanhdt/WorkingClaude/data/snapshots/corp_action_share_20260927.parquet \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
$DNA_PYEXE "$S/pt_v23_audit_2014.py" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($SB $TAG $*)" >> "$OUT/$TAG.log"
