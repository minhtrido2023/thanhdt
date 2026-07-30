#!/usr/bin/env bash
# daily_refresh_v3_4b.sh
# Daily refresh pipeline for Tam Quan v3.4b "Định Tâm" state series.
#
# Run this once per day AFTER market close (e.g. 18:00 ICT).
#
# Pipeline:
#   1. Pull latest US market data (SPX + VIX)
#   2. Regenerate v3 staging (raw + EW + concentration) — assumed already
#      in upstream pipeline; this script does NOT regenerate it
#   3. Build v3.1 = v3 staging + US overlay
#   4. Build v3.4b = v3.1 + BTC bull-aware US bypass + RSI gate + conc filter
#   5. Upload to BQ tav2_bq.vnindex_5state (replace LIVE)
#
# UPSTREAM PREREQUISITES (must exist before this script runs):
#   $STATE_WORKDIR/data/vnindex_5state_dual_v3_staging.csv  (from raw factor pipeline)
#   $STATE_WORKDIR/data/vnindex_5state_dual_v3_full.csv     (from raw factor pipeline)
#
# These are the SAME files used by the previous LIVE Tinh Tế (v2g_pe3c_s3)
# pipeline — re-use existing infrastructure.

set -e

cd "$(dirname "$0")"
export STATE_WORKDIR="${STATE_WORKDIR:-$(pwd)}"

echo "============================================================"
echo "Daily v3.4b refresh pipeline · $(date)"
echo "WORKDIR: $STATE_WORKDIR"
echo "============================================================"

# Step 1: Pull US data
echo ""
echo "[1/4] Pulling US market data (SPX + VIX)..."
python pull_us_market.py

# Step 2-3: Build v3.1 from v3 staging + US overlay
echo ""
echo "[2/4] Building v3.1 (v3 staging + US override)..."
python build_v3_1_clean.py

# v3.1 output is vnindex_5state_tam_quan_v3_1_clean.csv
# build_v3_4 expects _full_history.csv — copy
cp vnindex_5state_tam_quan_v3_1_clean.csv vnindex_5state_tam_quan_v3_1_full_history.csv

# Step 3: Build v3.4b from v3.1 + BTC overlay
echo ""
echo "[3/4] Building v3.4b (BTC bull-aware US bypass + RSI gate + conc filter)..."
python build_v3_4_bull_aware.py

# Step 4: Deploy to LIVE BQ table
echo ""
echo "[4/4] Deploying v3.4b → LIVE BQ table..."
python deploy_v3_4b_to_live.py

echo ""
echo "============================================================"
echo "✅ Daily v3.4b refresh complete · $(date)"
echo "============================================================"
