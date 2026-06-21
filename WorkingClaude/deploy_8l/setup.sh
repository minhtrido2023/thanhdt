#!/usr/bin/env bash
# One-time server setup. Run from the app root (/opt/8l). Debian/Ubuntu.
set -e
cd "$(dirname "$0")/.."          # app root (parent of deploy_8l/)
echo "[1] system deps"
sudo apt-get update -y
sudo apt-get install -y python3 python3-venv python3-pip
echo "[2] python venv + libs"
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r deploy_8l/requirements.txt
echo "[3] Google Cloud SDK (bq CLI)"
if ! command -v bq >/dev/null 2>&1; then
  echo "  bq not found. Install Google Cloud SDK:"
  echo "  https://cloud.google.com/sdk/docs/install   (then re-run / ensure 'bq' on PATH)"
else
  echo "  bq present: $(command -v bq)"
fi
mkdir -p data data/pt_8l
echo "[done] Next:"
echo "  - place sa-key.json in app root"
echo "  - gcloud auth activate-service-account --key-file=sa-key.json && gcloud config set project lithe-record-440915-m9"
echo "  - edit env.sh paths, then: source env.sh && source venv/bin/activate"
echo "  - smoke test: python power_lens.py && python unified_screener.py && python rank_8l.py"
