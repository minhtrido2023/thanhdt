---
name: kronos
description: Forecast financial candlesticks (K-lines) with Kronos — the open-source foundation model pre-trained on 12B+ K-line records from 45 exchanges (arXiv 2508.02739, AAAI 2026). Use when the user wants a model-based price/volatility forecast or "market language" read on a ticker, an index, or a CSV of OHLCV data. Pulls data from BigQuery (ticker / ticker_1m) or a local CSV, runs Kronos zero-shot, and outputs a forecast table + chart.
---

# Kronos — Financial Market Foundation Model

Kronos is a decoder-only foundation model that treats a sequence of candlesticks as a
*language*. A specialized tokenizer discretizes OHLCV(+amount) bars into tokens; the model
was autoregressively pre-trained on **12B+ K-lines from 45 global exchanges**, so it
forecasts price-series, volatility, and can generate synthetic paths **zero-shot** (no
fine-tuning needed to get a useful forecast).

- Paper: https://arxiv.org/abs/2508.02739 · Repo: https://github.com/shiyu-coder/Kronos
- Weights on HuggingFace under `NeoQuasar/*` (downloaded automatically on first run).

## Model variants (pick with `--model`)

| name (`--model`) | model id | tokenizer | context | params | when to use |
|---|---|---|---|---|---|
| `vn`    | local `finetuned/vn/*`   | local fine-tuned | 512 | (from base) | **auto-default once fine-tuned** — VN market |
| `mini`  | `NeoQuasar/Kronos-mini`  | `Kronos-Tokenizer-2k`   | 2048 | 4.1M   | long lookback, CPU, quick |
| `small` | `NeoQuasar/Kronos-small` | `Kronos-Tokenizer-base` | 512  | 24.7M  | base default if no VN weights |
| `base`  | `NeoQuasar/Kronos-base`  | `Kronos-Tokenizer-base` | 512  | 102.3M | best quality, prefer GPU |

`small`/`base`/`vn` see at most **512** bars of history; `mini` up to 2048.

**Auto-selection:** the forecast runner defaults to `--model vn` whenever fine-tuned
weights exist at `.claude/skills/kronos/finetuned/vn/{tokenizer,predictor}/best_model`;
otherwise it falls back to `small`. Pass `--model small` to force the un-tuned base for
comparison. So **once you've fine-tuned, every `/kronos` forecast is VN-tuned by default.**

## First-time setup (run once)

Installs torch/transformers/huggingface_hub/pandas and vendors the Kronos `model/`
package into this skill. Safe to re-run (idempotent).

```bash
bash .claude/skills/kronos/scripts/setup.sh
```

If `pip` here is sandboxed, tell the user to run it themselves with `! bash .claude/skills/kronos/scripts/setup.sh`.

## Running a forecast

The runner handles BigQuery → Kronos column mapping (BQ `Open/High/Low/Close/Volume` →
kronos `open/high/low/close/volume`) and timestamp construction for you.

```bash
# Forecast a Vietnamese ticker from BigQuery (daily bars from tav2_bq.ticker)
python .claude/skills/kronos/scripts/kronos_forecast.py \
    --ticker VNM --lookback 400 --pred-len 30 --model small

# Forecast the index from the local VNINDEX.csv (no BigQuery needed)
python .claude/skills/kronos/scripts/kronos_forecast.py \
    --csv VNINDEX.csv --lookback 400 --pred-len 30

# Probabilistic read: average 30 sampled paths + show the spread (vol forecast)
python .claude/skills/kronos/scripts/kronos_forecast.py \
    --ticker FPT --lookback 480 --pred-len 20 --sample-count 30 --T 1.0
```

### Key arguments

- `--ticker SYM` — pull daily OHLCV from `tav2_bq.ticker` (uses unadjusted `Price` if present, else `Close`). Mutually exclusive with `--csv`.
- `--source ticker_1m|ticker|ticker_prune` — BigQuery table (default `ticker`).
- `--csv PATH` — read OHLCV from a local CSV instead (auto-detects column case; needs at least open/high/low/close).
- `--lookback N` — history bars fed to the model (≤512 for small/base, ≤2048 for mini). Default 400.
- `--pred-len N` — bars to forecast forward. Default 30.
- `--T` — sampling temperature (higher = more diverse paths). Default 1.0.
- `--top-p` — nucleus sampling prob. Default 0.9.
- `--sample-count N` — number of forecast paths; >1 averages them and reports a confidence band (use for volatility / uncertainty). Default 1.
- `--device cpu|cuda:0` — default auto.
- `--out DIR` — output dir (default `data/kronos/`). Writes `<sym>_forecast.csv` and `<sym>_forecast.png`.

## Fine-tuning on the Vietnamese market (BigQuery)

Goal: produce local weights so `/kronos` is VN-tuned by default. Three steps —
**export → train → (auto-use)**. Steps 1–2 are heavy; run them on the box with the
`bq` CLI + ideally a GPU. Once `finetuned/vn/` exists, the runner picks it up
automatically with no extra flags.

```bash
# 0. one-time deps + vendored model code
bash .claude/skills/kronos/scripts/setup.sh

# 1. Export VN OHLCV from BigQuery into the Kronos pickle format.
#    Default universe = tav2_bq.ticker_prune (449 quality tickers, history from 2014),
#    split train 2014-2022 / val 2023-H1'24 / test H2'24-now. Per-ticker windows
#    (no cross-ticker leakage); liquidity floor via --min-avg-amt.
python .claude/skills/kronos/scripts/export_bq_to_pickle.py --source ticker_prune
#  -> .claude/skills/kronos/data/vn/{train,val,test}_data.pkl + meta.json

# 2. Two-phase fine-tune (tokenizer -> predictor). GPU strongly recommended.
python .claude/skills/kronos/scripts/finetune_vn.py --base small --epochs 10
#  -> .claude/skills/kronos/finetuned/vn/{tokenizer,predictor}/best_model

# 3. Nothing to do — forecasts now default to the VN model:
python .claude/skills/kronos/scripts/kronos_forecast.py --ticker FPT --pred-len 30
#  ">> using VN-fine-tuned weights (finetuned/vn)."
```

**What the fine-tune does (faithful to the official repo):** reuses Kronos's exact
two-stage objective — (1) tokenizer: reconstruction MSE + BSQ quantizer loss; (2)
predictor: dual-stream cross-entropy via `head.compute_loss` over tokens from the
fine-tuned tokenizer. Per-ticker windows, lookback-only normalization (no leakage),
same as `finetune/dataset.py`. The driver is single-process and runs on **CPU or GPU**
(the official `torchrun` scripts are CUDA+DDP+comet only — this one strips that so it
runs anywhere).

**Compute reality:** a real fine-tune (≈449 tickers, 10 epochs) wants a GPU
(Colab/cloud/local CUDA) — minutes-to-hours. On CPU it's only practical as a smoke
test: `--max-train-samples 2000 --epochs 1`. Key knobs: `--base {mini,small,base}`,
`--epochs`, `--batch-size`, `--lookback/--predict`, `--max-train-samples`, `--device`.

**Re-fresh:** re-run steps 1–2 periodically (e.g. quarterly) to fold in new data;
output overwrites `finetuned/vn/` and the runner keeps auto-using it.

**Validate it helped:** forecast the same ticker over a held-out window with
`--model vn` vs `--model small` and compare against realized closes — don't assume the
fine-tune helps without checking on the test split.

## Interpreting output

The runner prints: last close, forecast horizon, predicted close path, % change to
horizon end, and (with `--sample-count>1`) the cross-path std as a volatility proxy.
It saves a CSV of the predicted OHLCV and a PNG overlaying history + forecast (+ band).

**Caveats to relay to the user every time:**
- Kronos is a *statistical pattern* forecaster, **not** a guarantee — treat it as one more lens, alongside the workspace's own DT5G / 8L / V2.3 signals, never as a standalone trade trigger.
- It has no knowledge of news, fundamentals, or the forward-looking `profit_*` targets.
- Zero-shot on VN tickers is out-of-distribution relative to its training exchanges; longer lookback + `sample-count>1` gives a more honest (wider) read. Fine-tune (see repo `finetune/`) for serious use.

## How it maps to this workspace

This is an **orthogonal, model-based** forecaster — complementary to the rule/quant
systems documented in CLAUDE.md (DT5G regime, 8L ratings, V2.3 book). Good uses: a quick
"what does the candlestick language say next" sanity read on a name you're already
screening, volatility estimation, or generating synthetic continuations for stress tests.
Do not wire it into production allocation without a proper VN fine-tune + walk-forward.
