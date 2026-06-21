#!/usr/bin/env bash
set -e
export PATH="$HOME/.local/bin:/home/trido/google-cloud-sdk/bin:$PATH"
export OMP_NUM_THREADS=16 MKL_NUM_THREADS=16 OPENBLAS_NUM_THREADS=16
cd /home/trido/thanhdt/WorkingClaude
S=.claude/skills/kronos/scripts/finetune_vn.py
echo "=== HEAVY FINETUNE START $(date -u) ==="
echo "=== TOKENIZER phase $(date -u) ==="
python3 $S --phase tokenizer --base small --threads 16 --workers 6 \
  --epochs 2 --batch-size 64 --max-train-samples 60000 --max-val-samples 8000 --log-interval 100
echo "=== PREDICTOR phase $(date -u) ==="
python3 $S --phase predictor --base small --threads 16 --workers 6 \
  --epochs 6 --batch-size 64 --max-train-samples 70000 --max-val-samples 8000 --log-interval 100
echo "=== ALL DONE $(date -u) ==="
