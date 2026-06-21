#!/usr/bin/env python3
"""
Export Vietnamese OHLCV from BigQuery into the pickle format Kronos fine-tuning
expects: a dict {symbol -> DataFrame}, each frame indexed by a DatetimeIndex
named 'datetime' with columns ['open','high','low','close','vol','amt'].

Splits by date into train/val/test pickles (no cross-ticker window leakage —
each ticker is a separate series). Default universe = tav2_bq.ticker_prune
(449 quality tickers, full history from 2014).

Usage (run on a machine with the `bq` CLI authenticated, e.g. the Windows box):
  python export_bq_to_pickle.py --source ticker_prune \
      --train 2014-01-01:2022-12-31 --val 2023-01-01:2024-06-30 \
      --test 2024-07-01:2026-12-31 --out .claude/skills/kronos/data/vn

Output: <out>/train_data.pkl, val_data.pkl, test_data.pkl  (+ meta.json)
"""
import argparse
import io
import json
import os
import pickle
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd

BQ_PROJECT = "lithe-record-440915-m9"


def find_bq():
    """Locate the bq CLI even if the SDK bin isn't on PATH for non-interactive shells."""
    exe = shutil.which("bq")
    if exe:
        return exe
    for cand in [Path.home() / "google-cloud-sdk" / "bin" / "bq",
                 Path("/usr/local/google-cloud-sdk/bin/bq"),
                 Path("/opt/google-cloud-sdk/bin/bq")]:
        if cand.exists():
            os.environ["PATH"] = f"{cand.parent}:{os.environ.get('PATH', '')}"
            return str(cand)
    return None
FEATURES = ["open", "high", "low", "close", "vol", "amt"]


def parse_range(s):
    a, b = s.split(":")
    return a, b


def fetch(source, start, end, min_value, max_rows):
    """Pull daily OHLCV for the whole universe over [start, end] via bq CLI."""
    # amt (turnover) = unadjusted Price * Volume when Price present, else Close*Volume.
    # Liquidity floor via Trading_Value-like proxy keeps illiquid junk out of training.
    sql = f"""
    SELECT t.time, t.ticker,
           t.Open  AS open, t.High AS high, t.Low AS low, t.Close AS close,
           t.Volume AS vol,
           COALESCE(t.Price, t.Close) * t.Volume AS amt
    FROM tav2_bq.{source} AS t
    WHERE t.time BETWEEN '{start}' AND '{end}'
      AND t.Volume > 0 AND t.Close IS NOT NULL
    ORDER BY t.ticker, t.time
    """
    bq = find_bq()
    if not bq:
        sys.exit("ERROR: `bq` CLI not found (checked PATH and ~/google-cloud-sdk/bin).")
    cmd = [bq, "query", "--use_legacy_sql=false", f"--project_id={BQ_PROJECT}",
           "--format=csv", "-n", str(max_rows), sql]
    print(f">> querying tav2_bq.{source}  {start}..{end} ...", file=sys.stderr)
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    except FileNotFoundError:
        sys.exit("ERROR: `bq` CLI not runnable.")
    except subprocess.CalledProcessError as e:
        sys.exit(f"ERROR: bq query failed:\n{e.stderr}")
    df = pd.read_csv(io.StringIO(out))
    if df.empty:
        sys.exit(f"No rows for {source} in {start}..{end}.")
    df["datetime"] = pd.to_datetime(df["time"])
    return df


def to_symbol_dict(df, min_len, min_avg_amt):
    """Group the long frame into {ticker -> per-ticker DataFrame} (QlibDataset format)."""
    out = {}
    for sym, g in df.groupby("ticker"):
        g = g.sort_values("datetime")
        if len(g) < min_len:
            continue
        if g["amt"].mean() < min_avg_amt:
            continue
        frame = g[["datetime"] + FEATURES].copy()
        frame = frame.set_index("datetime")
        frame = frame[~frame.index.duplicated(keep="last")]
        out[sym] = frame.astype("float64")
    return out


def main():
    ap = argparse.ArgumentParser(description="BigQuery -> Kronos fine-tune pickle exporter")
    ap.add_argument("--source", default="ticker_prune",
                    choices=["ticker_prune", "ticker", "ticker_1m"])
    ap.add_argument("--train", default="2014-01-01:2022-12-31")
    ap.add_argument("--val", default="2023-01-01:2024-06-30")
    ap.add_argument("--test", default="2024-07-01:2026-12-31")
    ap.add_argument("--min-len", type=int, default=250,
                    help="min bars a ticker needs in the TRAIN window to be included")
    ap.add_argument("--min-avg-amt", type=float, default=1e9,
                    help="min average daily turnover (VND) to keep a ticker (liquidity floor)")
    ap.add_argument("--max-rows", type=int, default=2_000_000)
    ap.add_argument("--out", default=".claude/skills/kronos/data/vn")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    meta = {"source": args.source, "splits": {}, "features": FEATURES}
    for name, rng in [("train", args.train), ("val", args.val), ("test", args.test)]:
        start, end = parse_range(rng)
        df = fetch(args.source, start, end, args.min_avg_amt, args.max_rows)
        # liquidity/length filter is anchored on the train split; val/test inherit the
        # same tickers that survived training so the universe is consistent.
        if name == "train":
            sym_dict = to_symbol_dict(df, args.min_len, args.min_avg_amt)
            keep = set(sym_dict)
            meta["universe"] = sorted(keep)
        else:
            sym_dict = to_symbol_dict(df, 1, 0.0)
            sym_dict = {k: v for k, v in sym_dict.items() if k in keep}

        path = out_dir / f"{name}_data.pkl"
        with open(path, "wb") as f:
            pickle.dump(sym_dict, f, protocol=4)
        n_rows = sum(len(v) for v in sym_dict.values())
        meta["splits"][name] = {"range": [start, end], "tickers": len(sym_dict), "rows": n_rows}
        print(f">> {name}: {len(sym_dict)} tickers, {n_rows:,} rows -> {path}")

    with open(out_dir / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)
    print(f">> wrote {out_dir/'meta.json'}")
    print(">> done. Next: python .claude/skills/kronos/scripts/finetune_vn.py")


if __name__ == "__main__":
    main()
