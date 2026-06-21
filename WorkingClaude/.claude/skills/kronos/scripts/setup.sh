#!/usr/bin/env bash
# One-time setup for the Kronos skill. Idempotent — safe to re-run.
# Installs Python deps and vendors the Kronos `model/` package (which the HF
# weights need in order to load) into the skill directory.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENDOR="$SKILL_DIR/vendor"
KRONOS_DIR="$VENDOR/Kronos"

echo ">> Kronos skill setup"
echo ">> skill dir: $SKILL_DIR"

# 1. Python dependencies ------------------------------------------------------
# torch is the big one; CPU wheel is fine for mini/small. Users on GPU can
# pre-install a CUDA torch before running this and pip will keep it.
echo ">> installing python deps (torch, transformers, huggingface_hub, pandas, numpy, matplotlib, einops, safetensors) ..."
python3 -m pip install --quiet --upgrade \
    "torch" "transformers>=4.40" "huggingface_hub>=0.23" \
    "pandas" "numpy" "matplotlib" "einops" "safetensors" "tqdm" || {
    echo "!! pip install failed. If this env is sandboxed, run this script yourself:"
    echo "   ! bash .claude/skills/kronos/scripts/setup.sh"
    exit 1
}

# 2. Vendor the Kronos model code --------------------------------------------
mkdir -p "$VENDOR"
if [ -d "$KRONOS_DIR/.git" ]; then
    echo ">> updating existing Kronos checkout ..."
    git -C "$KRONOS_DIR" pull --ff-only || echo "   (pull skipped/failed; using existing checkout)"
else
    echo ">> cloning Kronos repo (for the model/ package) ..."
    git clone --depth 1 https://github.com/shiyu-coder/Kronos.git "$KRONOS_DIR"
fi

# Sanity: the importable package we need
if [ -d "$KRONOS_DIR/model" ]; then
    echo ">> OK: model package present at $KRONOS_DIR/model"
else
    echo "!! WARNING: $KRONOS_DIR/model not found — repo layout may have changed."
fi

echo ">> setup complete. Weights download automatically on first forecast."
