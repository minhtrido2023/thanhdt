#!/usr/bin/env bash
# VIEC 1 — sinh lai 16 *_screen.py sau merge ec9750f2 (chieu sort 8L top-25).
# Backup MOI artifact se bi ghi de sang <path>.bak_20260927_prescreenfix TRUOC khi chay.
set -uo pipefail
cd /home/trido/thanhdt/WorkingClaude
SUF=".bak_20260927_prescreenfix"
LOGD="mike/agents/Taylor/research/screen_regen_20260927/logs"
mkdir -p "$LOGD"
PY="${DNA_PYEXE:-/home/trido/thanhdt/wc_venv/bin/python}"

# --- backup pha 1 (khong chay gi truoc khi backup xong) ---
python3 - <<'PYEOF'
import json, shutil, os
outs = json.load(open("mike/agents/Taylor/research/screen_regen_20260927/outputs.json"))
SUF = ".bak_20260927_prescreenfix"
n_ok = n_missing = 0
for f, paths in outs.items():
    for p in paths:
        if os.path.exists(p):
            shutil.copy2(p, p + SUF); n_ok += 1
        else:
            print(f"  (chua ton tai, khong can backup) {p}"); n_missing += 1
print(f"BACKUP: {n_ok} file da sao luu, {n_missing} file chua ton tai")
PYEOF

# --- pha 2: chay 16 screen ---
for f in aviation bank_compounder compounder construction energy fertchem_rubber fnb \
         livestock logistics_port pharma re_compounder retail_compounder securities \
         steel_buildmat tech textile; do
  s="${f}_screen.py"
  echo "=== RUN $s  $(TZ='Asia/Ho_Chi_Minh' date '+%H:%M:%S') ==="
  "$PY" "$s" > "$LOGD/${f}.log" 2> "$LOGD/${f}.err"
  rc=$?
  echo "    rc=$rc  ($(wc -l < "$LOGD/${f}.log") dong stdout)"
  [ $rc -ne 0 ] && { echo "    --- stderr cuoi ---"; tail -5 "$LOGD/${f}.err"; }
done
echo "DONE $(TZ='Asia/Ho_Chi_Minh' date '+%H:%M:%S')"
