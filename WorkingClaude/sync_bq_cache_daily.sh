#!/usr/bin/env bash
# Daily BQ cache sync — runs after BQ data ingest (~23:15 ICT / 16:15 UTC).
# Delta mode: appends today's new rows to existing parquet files.
# Full re-download of rolling tables (ticker_1m).
# Verifies against BQ, then runs preflight check.
set -euo pipefail
cd /home/trido/thanhdt/WorkingClaude
source wc_env.sh

python3 sync_bq_cache.py --delta 2>&1
python3 preflight_bq_cache.py 2>&1
