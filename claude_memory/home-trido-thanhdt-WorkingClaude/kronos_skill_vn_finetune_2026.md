---
name: kronos-skill-vn-finetune-2026
description: "Kronos candlestick foundation-model skill + VN fine-tune pipeline, weights, and the honest eval verdict (calibration win, no directional alpha)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 4bbb8993-5568-4087-83dc-fd2d77a0486e
---

Skill `kronos` (in `.claude/skills/kronos/`) wraps the Kronos candlestick foundation model (shiyu-coder/Kronos, arXiv 2508.02739) for this VN workspace. Runs fully on **this Linux box (CPU, no GPU)** — torch 2.12+cpu installed via user pip (bootstrapped get-pip; ensurepip blocked). `bq` lives at `~/google-cloud-sdk/bin` (scripts auto-find it).

**Pipeline (all CPU-capable, single-process, no DDP/comet):**
- `scripts/export_bq_to_pickle.py` — BQ `ticker_prune` → `{ticker: df}` pickle (cols open/high/low/close/vol/amt, index datetime), per-ticker windows (no leak), split train 2014-2022 / val 2023-H1'24 / test H2'24+. Liquidity floor → 385 train tickers / 475k rows.
- `scripts/vn_dataset.py` — multi-ticker dataset, mirrors official `finetune/dataset.py` normalization.
- `scripts/finetune_vn.py` — 2-phase (tokenizer recon+bsq, predictor dual-stream CE via `head.compute_loss`), EXACT repo loss formulas. **Key: `--threads 8-16` (NOT 34 — 34 threads = ~4 samples/s, 8-16 = ~18-20; small model, op-launch overhead). batch 64.**
- `scripts/kronos_forecast.py` — forecast runner, **auto-uses VN weights** (`finetuned/vn/{tokenizer,predictor}/best_model`) when present, else base `small`. `--model vn|small|base|mini`.
- `scripts/eval_compare.py` — VN vs base on held-out test (MAE% + dir-acc).

**Done [REDACTED]:** heavy fine-tune (base small, tok 2ep×60k, pred 6ep×70k≈1 full pass of 436k windows), ~6h CPU. Predictor val 3.2195→3.1995, no overfit. Weights live in `finetuned/vn/`.

**HONEST EVAL VERDICT (60 tickers×3 cuts, horizon 5d):** fine-tune is a **calibration win, NOT a directional edge.** MAE% close: VN **2.56%** vs base **3.93%** (−35% rel — base badly over-moves for VN, fine-tune fixed the OOD scale) BUT naive flat = **2.25%** still beats both, and dir-acc ~48% (coin-flip) for both. → Daily VN close at 1-week horizon is ~random-walk; Kronos (even VN-tuned at CPU budget) shows no point-direction alpha. **Use as a calibrated scenario/vol lens, never a trade trigger** — consistent with DT5G/8L no-overfit philosophy. Untested upside: longer horizon, vol-forecasting, `--base` 102M, or many-epoch GPU run. See [[oil_gas_chain_8l_2026]] for the kind of orthogonal lens this complements.
