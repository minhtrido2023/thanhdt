#!/usr/bin/env bash
# 5-state market regime — daily refresh + classify + upload to BQ.
# Run BEFORE recommend_holistic.py.
#
# Schedule via cron after 15:00 ICT Mon-Fri:
#   0 8 * * 1-5 /home/USER/deploy_5state/run_daily.sh

set -e

# ─── CONFIG — sửa các path này cho server của bạn ─────────────────────────
WORKDIR="/home/USER/deploy_5state"
VENV_PYTHON="${WORKDIR}/.venv/bin/python"
LOG_DIR="${WORKDIR}/logs"

export BAVN_WORKDIR="${WORKDIR}"
export GOOGLE_APPLICATION_CREDENTIALS="${HOME}/.gcp/ba-sa-key.json"

# ─── RUN ─────────────────────────────────────────────────────────────────
mkdir -p "${LOG_DIR}"
DATE=$(date +%Y-%m-%d)
LOG="${LOG_DIR}/5state_${DATE}.log"

echo "=== $(date -Iseconds) — 5-state daily run ===" | tee -a "${LOG}"
cd "${WORKDIR}"

# Step 1: refresh VNINDEX.csv + breadth_data.csv from BQ
echo "" | tee -a "${LOG}"
echo "[STEP 1] refresh_data.py" | tee -a "${LOG}"
"${VENV_PYTHON}" refresh_data.py 2>&1 | tee -a "${LOG}"

# Step 2: classify states
echo "" | tee -a "${LOG}"
echo "[STEP 2] vnindex_5state_system.py" | tee -a "${LOG}"
"${VENV_PYTHON}" vnindex_5state_system.py 2>&1 | tee -a "${LOG}"

# Step 3: upload to BQ (tav2_bq.vnindex_5state)
echo "" | tee -a "${LOG}"
echo "[STEP 3] upload_to_bq.py" | tee -a "${LOG}"
"${VENV_PYTHON}" upload_to_bq.py 2>&1 | tee -a "${LOG}"

echo "" | tee -a "${LOG}"
echo "=== DONE $(date -Iseconds) ===" | tee -a "${LOG}"
