#!/bin/bash
# usage: run_stage.sh <out_dir> [steps...]  (b c d e f)  — PY=wc_venv
S=$1; shift; PY=/home/trido/thanhdt/wc_venv/bin/python; cd "$(dirname "$0")/${CALC:-calc}"; export OUT_DIR=$(cd ..; pwd)/$S PYTHONHASHSEED=${PYTHONHASHSEED:-0}
for k in "$@"; do case $k in b) f=b_panel.py;; c) f=c_models2.py;; d) f=d_metrics2.py;; e) f=e_bt2.py;; f) f=f_proxy_diag.py;; n) f=h_null_ep.py;; esac
 echo "== $k $f $(date +%T)"; /usr/bin/time -f "%es" $PY $f > $OUT_DIR/log_$k.txt 2>&1 || echo "FAIL $k"; tail -2 $OUT_DIR/log_$k.txt | cut -c1-200; done
