#!/bin/bash
cd "C:/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude"
export PATH="$PATH:/c/Users/hotro/AppData/Local/Google/Cloud SDK/google-cloud-sdk/bin"
export CLOUDSDK_PYTHON="/c/Users/hotro/AppData/Local/Google/Cloud SDK/google-cloud-sdk/platform/bundledpython/python.exe"
for V in mode15_ms7 nomode_ms7 mode7_ms7 mode5_ms7; do
  echo "===== RUN $V ====="
  STATE_CSV_OVERRIDE="data/state_modevar_${V}.csv" TAG_SUFFIX="_MV_${V}" \
    python run_5systems_prodspec.py > "data/_mv_${V}.log" 2>&1
  echo "exit=$? for $V"
done
echo "ALL DONE"
