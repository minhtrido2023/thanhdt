#!/bin/bash
cd "C:/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude"
export PATH="$PATH:/c/Users/hotro/AppData/Local/Google/Cloud SDK/google-cloud-sdk/bin"
export CLOUDSDK_PYTHON="/c/Users/hotro/AppData/Local/Google/Cloud SDK/google-cloud-sdk/platform/bundledpython/python.exe"
declare -A CSV=(
  [v34b_base]="vnindex_5state_tam_quan_v3_4b_full_history.csv"
  [dt_5_15_15]="vnindex_5state_dt_5_15_15.csv"
  [dt_7_20_20]="vnindex_5state_dt_7_20_20.csv"
  [dt_10_25_25]="vnindex_5state_dt_10_25_25.csv"
  [dt_15_30_25]="vnindex_5state_dt_15_30_25.csv"
)
for V in v34b_base dt_5_15_15 dt_7_20_20 dt_10_25_25 dt_15_30_25; do
  echo "===== RUN $V (${CSV[$V]}) ====="
  STATE_CSV_OVERRIDE="${CSV[$V]}" TAG_SUFFIX="_DTS_${V}" \
    python run_5systems_prodspec.py > "data/_dts_${V}.log" 2>&1
  echo "exit=$? for $V"
done
echo "ALL DONE"
