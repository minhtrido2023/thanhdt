#!/usr/bin/env bash
# BA-system V11 daily runner — Linux / macOS.
# Schedule via cron after 15:00 ICT Mon-Fri:
#   5 8 * * 1-5 /home/USER/deploy_v11/run_daily.sh

set -e

# ─── CONFIG — sửa các path này cho server của bạn ─────────────────────────
WORKDIR="/home/USER/deploy_v11"
VENV_PYTHON="${WORKDIR}/.venv/bin/python"
LOG_DIR="${WORKDIR}/logs"

# Service account key (Cách A trong DEPLOY.md). Nếu dùng `gcloud auth login`
# cá nhân thì bỏ comment dòng GOOGLE_APPLICATION_CREDENTIALS.
export GOOGLE_APPLICATION_CREDENTIALS="${HOME}/.gcp/ba-sa-key.json"

# ─── RUN ─────────────────────────────────────────────────────────────────
mkdir -p "${LOG_DIR}"
DATE=$(date +%Y-%m-%d)
LOG="${LOG_DIR}/run_${DATE}.log"

echo "=== $(date -Iseconds) — BA-system daily run ===" | tee -a "${LOG}"
cd "${WORKDIR}"

# Run; truyền date nếu user pass argument để rerun ngày cũ
if [[ -n "$1" ]]; then
    "${VENV_PYTHON}" recommend_holistic.py "$1" 2>&1 | tee -a "${LOG}"
else
    "${VENV_PYTHON}" recommend_holistic.py 2>&1 | tee -a "${LOG}"
fi

EXIT=${PIPESTATUS[0]}
echo "=== exit ${EXIT} ===" | tee -a "${LOG}"
exit "${EXIT}"
