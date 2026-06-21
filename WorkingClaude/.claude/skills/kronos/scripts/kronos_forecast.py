#!/usr/bin/env python3
"""
Kronos forecast runner for the WorkingClaude VN-stock workspace.

Pulls OHLCV from BigQuery (tav2_bq.ticker / ticker_1m / ticker_prune) or a local
CSV, runs the Kronos foundation model zero-shot, and writes a forecast CSV + PNG.

See .claude/skills/kronos/SKILL.md for usage. Run setup.sh once first.
"""
import argparse
import io
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SKILL_DIR = Path(__file__).resolve().parent.parent
KRONOS_DIR = SKILL_DIR / "vendor" / "Kronos"
BQ_PROJECT = "lithe-record-440915-m9"

# Make the vendored Kronos `model/` package importable.
sys.path.insert(0, str(KRONOS_DIR))


def _die(msg, code=1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------
OHLCV = ["open", "high", "low", "close", "volume", "amount"]


def load_from_bq(ticker, source, n):
    """Fetch the last `n` daily bars for `ticker` from BigQuery via the bq CLI."""
    # Price = unadjusted; fall back to adj Close if Price is null.
    sql = f"""
    SELECT time,
           Open  AS open, High AS high, Low AS low,
           COALESCE(Close, Price) AS close,
           Volume AS volume
    FROM tav2_bq.{source} AS t
    WHERE t.ticker = '{ticker}'
    ORDER BY time DESC
    LIMIT {n}
    """
    bq = shutil.which("bq")
    if not bq:
        for cand in [os.path.expanduser("~/google-cloud-sdk/bin/bq"),
                     "/usr/local/google-cloud-sdk/bin/bq", "/opt/google-cloud-sdk/bin/bq"]:
            if os.path.exists(cand):
                bq = cand
                break
    if not bq:
        _die("`bq` CLI not found (checked PATH and ~/google-cloud-sdk/bin). Use --csv instead.")
    cmd = [
        bq, "query", "--use_legacy_sql=false", f"--project_id={BQ_PROJECT}",
        "--format=csv", "-n", str(n + 10), sql,
    ]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    except FileNotFoundError:
        _die("`bq` CLI not runnable. Use --csv instead.")
    except subprocess.CalledProcessError as e:
        _die(f"bq query failed:\n{e.stderr}")
    df = pd.read_csv(io.StringIO(out))
    if df.empty:
        _die(f"No rows for ticker '{ticker}' in tav2_bq.{source}.")
    df = df.sort_values("time").reset_index(drop=True)
    df["timestamps"] = pd.to_datetime(df["time"])
    return df


def load_from_csv(path, n):
    df = pd.read_csv(path)
    # Normalize column names to lowercase, tolerant of case/aliases.
    lower = {c.lower(): c for c in df.columns}
    def pick(*names):
        for nm in names:
            if nm in lower:
                return lower[nm]
        return None
    cmap = {
        "open": pick("open"),
        "high": pick("high"),
        "low": pick("low"),
        "close": pick("close", "price", "vnindex", "value"),
        "volume": pick("volume", "vol"),
    }
    missing = [k for k in ("open", "high", "low", "close") if cmap[k] is None]
    if missing:
        _die(f"CSV missing required column(s): {missing}. Found: {list(df.columns)}")
    ts_col = pick("timestamps", "time", "date", "datetime")
    out = pd.DataFrame({k: df[v] for k, v in cmap.items() if v is not None})
    if ts_col:
        out["timestamps"] = pd.to_datetime(df[ts_col])
        out = out.sort_values("timestamps").reset_index(drop=True)
    else:
        out["timestamps"] = pd.date_range("2000-01-01", periods=len(out), freq="D")
    return out.tail(n).reset_index(drop=True)


def infer_freq(ts):
    """Best-effort pandas freq string from a timestamp series, for future bars."""
    if len(ts) < 3:
        return "D"
    diffs = ts.diff().dropna()
    med = diffs.median()
    minutes = med.total_seconds() / 60.0
    if minutes <= 1.5:   return "min"
    if minutes <= 6:     return "5min"
    if minutes <= 20:    return "15min"
    if minutes <= 75:    return "h"
    return "D"  # daily (skips weekends naturally because we extrapolate from real ts)


def make_future_timestamps(hist_ts, pred_len):
    freq = infer_freq(hist_ts)
    last = hist_ts.iloc[-1]
    if freq == "D":
        # Business-day forward fill (skip weekends) for daily VN data.
        fut = pd.bdate_range(start=last, periods=pred_len + 1, freq="C")[1:]
    else:
        fut = pd.date_range(start=last, periods=pred_len + 1, freq=freq)[1:]
    return pd.Series(fut[:pred_len])


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
MODELS = {
    "mini":  ("NeoQuasar/Kronos-mini",  "NeoQuasar/Kronos-Tokenizer-2k",   2048),
    "small": ("NeoQuasar/Kronos-small", "NeoQuasar/Kronos-Tokenizer-base", 512),
    "base":  ("NeoQuasar/Kronos-base",  "NeoQuasar/Kronos-Tokenizer-base", 512),
}

# Local VN-fine-tuned weights produced by finetune_vn.py.
VN_PRED = SKILL_DIR / "finetuned" / "vn" / "predictor" / "best_model"
VN_TOK = SKILL_DIR / "finetuned" / "vn" / "tokenizer" / "best_model"


def vn_available():
    return VN_PRED.exists() and VN_TOK.exists()


def resolve_model(name):
    """Return (predictor_id, tokenizer_id, max_ctx). 'vn' uses local fine-tuned weights."""
    if name == "vn":
        if not vn_available():
            _die("--model vn requested but no VN-fine-tuned weights found. "
                 "Run export_bq_to_pickle.py then finetune_vn.py first "
                 f"(expected {VN_PRED}).")
        # Fine-tuned from the 'small'/'base' base → 512 context.
        return str(VN_PRED), str(VN_TOK), 512
    return MODELS[name]


def main():
    ap = argparse.ArgumentParser(description="Kronos forecast runner")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--ticker", help="Ticker symbol to pull from BigQuery")
    src.add_argument("--csv", help="Local CSV of OHLCV instead of BigQuery")
    ap.add_argument("--source", default="ticker",
                    choices=["ticker", "ticker_1m", "ticker_prune"])
    ap.add_argument("--model", default=None, choices=list(MODELS) + ["vn"],
                    help="default: 'vn' if fine-tuned weights exist, else 'small'")
    ap.add_argument("--lookback", type=int, default=400)
    ap.add_argument("--pred-len", type=int, default=30)
    ap.add_argument("--T", type=float, default=1.0)
    ap.add_argument("--top-p", type=float, default=0.9)
    ap.add_argument("--sample-count", type=int, default=1)
    ap.add_argument("--device", default=None, help="cpu | cuda:0 (default auto)")
    ap.add_argument("--out", default="data/kronos")
    args = ap.parse_args()

    if not KRONOS_DIR.exists():
        _die(f"Kronos not vendored at {KRONOS_DIR}. Run: bash .claude/skills/kronos/scripts/setup.sh")

    try:
        import torch
        from model import Kronos, KronosTokenizer, KronosPredictor
    except Exception as e:  # noqa
        _die(f"Import failed ({e}). Run setup.sh first: bash .claude/skills/kronos/scripts/setup.sh")

    if args.model is None:
        args.model = "vn" if vn_available() else "small"
        if args.model == "vn":
            print(">> using VN-fine-tuned weights (finetuned/vn). Pass --model small to use the base.")
    model_id, tok_id, max_ctx = resolve_model(args.model)
    if args.lookback > max_ctx:
        print(f"WARNING: lookback {args.lookback} > model context {max_ctx}; clamping.")
        args.lookback = max_ctx

    device = args.device or ("cuda:0" if torch.cuda.is_available() else "cpu")
    label = args.ticker or Path(args.csv).stem

    # --- data ---
    n = args.lookback + 5
    if args.ticker:
        df = load_from_bq(args.ticker, args.source, n)
    else:
        df = load_from_csv(args.csv, n)
    if len(df) < args.lookback:
        print(f"WARNING: only {len(df)} bars available (< lookback {args.lookback}); using all.")
        args.lookback = min(args.lookback, len(df) - 1)

    df = df.tail(args.lookback).reset_index(drop=True)
    feat_cols = [c for c in ["open", "high", "low", "close", "volume", "amount"] if c in df.columns]
    x_df = df[feat_cols].astype(float)
    x_ts = df["timestamps"]
    y_ts = make_future_timestamps(x_ts, args.pred_len)

    # --- model ---
    print(f">> loading {model_id} ({args.model}) + {tok_id} on {device} ...")
    tokenizer = KronosTokenizer.from_pretrained(tok_id)
    model = Kronos.from_pretrained(model_id)
    predictor = KronosPredictor(model, tokenizer, device=device, max_context=max_ctx)

    print(f">> forecasting {label}: lookback={args.lookback}, pred_len={args.pred_len}, "
          f"samples={args.sample_count}, T={args.T}, top_p={args.top_p}")

    if args.sample_count > 1:
        # Average several sampled paths and capture the spread (vol proxy).
        paths = []
        for i in range(args.sample_count):
            p = predictor.predict(df=x_df, x_timestamp=x_ts, y_timestamp=y_ts,
                                  pred_len=args.pred_len, T=args.T, top_p=args.top_p,
                                  sample_count=1)
            paths.append(p["close"].values)
        arr = np.vstack(paths)
        pred_close = arr.mean(axis=0)
        pred_std = arr.std(axis=0)
        pred_df = predictor.predict(df=x_df, x_timestamp=x_ts, y_timestamp=y_ts,
                                    pred_len=args.pred_len, T=args.T, top_p=args.top_p,
                                    sample_count=1)
        pred_df["close"] = pred_close
    else:
        pred_df = predictor.predict(df=x_df, x_timestamp=x_ts, y_timestamp=y_ts,
                                    pred_len=args.pred_len, T=args.T, top_p=args.top_p,
                                    sample_count=1)
        pred_close = pred_df["close"].values
        pred_std = None

    pred_df.index = y_ts.values

    # --- report ---
    last_close = float(x_df["close"].iloc[-1])
    end_close = float(pred_close[-1])
    pct = (end_close / last_close - 1.0) * 100.0
    print("\n========== KRONOS FORECAST ==========")
    print(f"  symbol           : {label}")
    print(f"  last close       : {last_close:,.2f}  ({x_ts.iloc[-1].date()})")
    print(f"  forecast horizon : {args.pred_len} bars  -> {y_ts.iloc[-1].date()}")
    print(f"  predicted close  : {end_close:,.2f}")
    print(f"  expected change  : {pct:+.2f}%  ({'UP' if pct >= 0 else 'DOWN'})")
    if pred_std is not None:
        rel = pred_std[-1] / max(end_close, 1e-9) * 100
        print(f"  path dispersion  : ±{pred_std[-1]:,.2f} ({rel:.1f}%) at horizon  (vol proxy, {args.sample_count} paths)")
    print("=====================================\n")

    # --- save ---
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / f"{label}_forecast.csv"
    save_df = pred_df.copy()
    if pred_std is not None:
        save_df["close_std"] = pred_std
    save_df.to_csv(csv_path)
    print(f">> wrote {csv_path}")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(x_ts, x_df["close"], label="history", color="#1f77b4")
        ax.plot(y_ts, pred_close, label="kronos forecast", color="#d62728")
        if pred_std is not None:
            ax.fill_between(y_ts, pred_close - pred_std, pred_close + pred_std,
                            color="#d62728", alpha=0.15, label="±1σ path band")
        ax.axvline(x_ts.iloc[-1], ls="--", color="gray", lw=0.8)
        ax.set_title(f"Kronos ({args.model}) — {label}  |  {args.pred_len}-bar forecast  ({pct:+.1f}%)")
        ax.legend(); ax.grid(alpha=0.3)
        png_path = out_dir / f"{label}_forecast.png"
        fig.tight_layout(); fig.savefig(png_path, dpi=110)
        print(f">> wrote {png_path}")
    except Exception as e:  # noqa
        print(f"(plot skipped: {e})")


if __name__ == "__main__":
    main()
