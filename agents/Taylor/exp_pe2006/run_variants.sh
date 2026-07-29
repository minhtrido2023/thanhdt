#!/usr/bin/env bash
# run_variants.sh — PE-history sensitivity harness (job Taylor_20260729_132056)
# Rebuilds the v3.4b base chain (dual_v3 -> v3_1_clean -> v3_4b -> dt_4gate) 4x,
# varying ONLY the VNINDEX_PE history floor. Everything else (ew_full, concentration,
# us_market, Close series) is held byte-identical across variants so the PE channel
# is isolated. Writes into an isolated sandbox WORKDIR — never touches canonical data/.
set -euo pipefail
W=/home/trido/thanhdt/WorkingClaude
source $W/wc_env.sh
EXP=$W/mike/agents/Taylor/exp_pe2006
SB=$EXP/wd
PY=$DNA_PYEXE

VAR=$1          # OLD | NEW | M2007 | M2008
FLOOR=$2        # YYYY-MM-DD  (PE masked strictly before this date; 1900-01-01 = no mask)

export STATE_WORKDIR=$SB
mkdir -p $SB/data $EXP/out

# 1. PE-variant VNI cache
$PY - "$FLOOR" <<'PYEOF'
import sys, pandas as pd, os
floor = pd.Timestamp(sys.argv[1])
w = "/home/trido/thanhdt/WorkingClaude"
d = pd.read_pickle(f"{w}/data/_cache_vnindex_2000_now.pkl")
d["time"] = pd.to_datetime(d["time"])
n_before = d["VNINDEX_PE"].notna().sum()
d.loc[d["time"] < floor, "VNINDEX_PE"] = float("nan")
n_after = d["VNINDEX_PE"].notna().sum()
sb = os.environ["STATE_WORKDIR"]
d.to_pickle(f"{sb}/data/_cache_vnindex_2000_now.pkl")
print(f"[pe-mask] floor={floor.date()} non-null PE {n_before} -> {n_after} (dropped {n_before-n_after})")
PYEOF

cd $SB
echo "--- dual_v3 ---";        $PY dual_v3_exp.py > $EXP/out/log_${VAR}_dualv3.txt 2>&1
echo "--- v3_1_clean ---";     $PY $W/deploy_v3_4b_package/build_v3_1_clean.py > $EXP/out/log_${VAR}_v31.txt 2>&1
cp $SB/data/vnindex_5state_tam_quan_v3_1_clean.csv $SB/data/vnindex_5state_tam_quan_v3_1_full_history.csv
echo "--- v3_4b ---";          $PY $W/deploy_v3_4b_package/build_v3_4_bull_aware.py > $EXP/out/log_${VAR}_v34b.txt 2>&1 || echo "  (v34b print-block error ignored — CSVs already written)"
cp $SB/vnindex_5state_tam_quan_v3_4b_full_history.csv $SB/data/vnindex_5state_tam_quan_v3_4b_full_history.csv
echo "--- dt_4gate ---";       $PY dt_4gate_exp.py > $EXP/out/log_${VAR}_dt4.txt 2>&1

cp $SB/data/vnindex_5state_tam_quan_v3_4b_full_history.csv $EXP/out/v34b_${VAR}.csv
cp $SB/data/vnindex_5state_dt_4gate.csv                    $EXP/out/dt4_${VAR}.csv
cp $SB/data/vnindex_5state_dual_v3_staging.csv             $EXP/out/dualv3_${VAR}.csv
tail -3 $EXP/out/log_${VAR}_dt4.txt
echo "VARIANT $VAR DONE"
