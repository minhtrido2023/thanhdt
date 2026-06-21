#!/usr/bin/env python3
"""
Compare the VN-fine-tuned Kronos vs the base pretrained model on the HELD-OUT
test split (test_data.pkl, dates the model never trained on).

For many (ticker, cut-point) samples it forecasts `horizon` bars ahead from a
`lookback` context and scores both models against the realized closes:
  * MAE%   - mean abs pct error of predicted vs actual close over the horizon
  * DirAcc - % of samples where the predicted end-of-horizon direction (up/down
             vs last close) matches reality
A naive "flat = last close" baseline is included for reference.

Usage:
  python eval_compare.py --tickers 60 --lookback 250 --horizon 5 --samples 10
"""
import argparse
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "vendor" / "Kronos"))
from model import Kronos, KronosTokenizer, KronosPredictor  # noqa: E402

VN_PRED = SKILL_DIR / "finetuned" / "vn" / "predictor" / "best_model"
VN_TOK = SKILL_DIR / "finetuned" / "vn" / "tokenizer" / "best_model"
REN = {"vol": "volume", "amt": "amount"}


def load_predictors(device, max_ctx):
    base = KronosPredictor(Kronos.from_pretrained("NeoQuasar/Kronos-small"),
                           KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base"),
                           device=device, max_context=max_ctx)
    vn = KronosPredictor(Kronos.from_pretrained(str(VN_PRED)),
                         KronosTokenizer.from_pretrained(str(VN_TOK)),
                         device=device, max_context=max_ctx)
    return base, vn


def eval_one(pred, ctx, y_ts, horizon, T, top_p, samples, seed):
    x_df = ctx.rename(columns=REN)[["open", "high", "low", "close", "volume", "amount"]].reset_index(drop=True)
    torch.manual_seed(seed)
    out = pred.predict(df=x_df, x_timestamp=ctx["datetime"], y_timestamp=y_ts,
                       pred_len=horizon, T=T, top_p=top_p, sample_count=samples, verbose=False)
    return out["close"].values


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(SKILL_DIR / "data" / "vn" / "test_data.pkl"))
    ap.add_argument("--tickers", type=int, default=60)
    ap.add_argument("--cuts", type=int, default=3, help="eval points per ticker")
    ap.add_argument("--lookback", type=int, default=250)
    ap.add_argument("--horizon", type=int, default=5)
    ap.add_argument("--samples", type=int, default=10)
    ap.add_argument("--T", type=float, default=0.6)
    ap.add_argument("--top-p", type=float, default=0.9)
    ap.add_argument("--threads", type=int, default=16)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    if not torch.cuda.is_available():
        torch.set_num_threads(args.threads)
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    max_ctx = max(512, args.lookback)

    with open(args.data, "rb") as f:
        data = pickle.load(f)
    need = args.lookback + args.horizon + 5
    syms = [s for s, d in data.items() if len(d) >= need + (args.cuts - 1) * args.horizon]
    syms = sorted(syms)[: args.tickers]
    print(f">> evaluating {len(syms)} tickers x {args.cuts} cut-points, "
          f"lookback={args.lookback} horizon={args.horizon} samples={args.samples} on {device}")

    base, vn = load_predictors(device, max_ctx)

    rows = []
    rng = np.random.default_rng(args.seed)
    for i, s in enumerate(syms):
        df = data[s].reset_index()
        if "datetime" not in df.columns:
            df = df.rename(columns={df.columns[0]: "datetime"})
        n = len(df)
        # cut points spread across the usable tail
        latest = n - args.horizon
        earliest = args.lookback
        if latest <= earliest:
            continue
        cuts = sorted(set(int(c) for c in np.linspace(earliest, latest, args.cuts)))
        for cut in cuts:
            ctx = df.iloc[cut - args.lookback:cut].copy()
            fut = df.iloc[cut:cut + args.horizon]
            if len(fut) < args.horizon:
                continue
            last_close = float(ctx["close"].iloc[-1])
            actual = fut["close"].values.astype(float)
            y_ts = fut["datetime"]
            seed = int(rng.integers(1, 1_000_000))
            try:
                pv = eval_one(vn, ctx, y_ts, args.horizon, args.T, args.top_p, args.samples, seed)
                pb = eval_one(base, ctx, y_ts, args.horizon, args.T, args.top_p, args.samples, seed)
            except Exception as e:  # noqa
                print(f"   skip {s}@{cut}: {e}")
                continue
            mae_vn = np.mean(np.abs(pv / actual - 1.0)) * 100
            mae_bs = np.mean(np.abs(pb / actual - 1.0)) * 100
            mae_flat = np.mean(np.abs(last_close / actual - 1.0)) * 100
            dir_act = np.sign(actual[-1] - last_close)
            dir_vn = np.sign(pv[-1] - last_close)
            dir_bs = np.sign(pb[-1] - last_close)
            rows.append(dict(sym=s, cut=cut, mae_vn=mae_vn, mae_bs=mae_bs, mae_flat=mae_flat,
                             dvn=int(dir_vn == dir_act), dbs=int(dir_bs == dir_act),
                             moved=int(dir_act != 0)))
        if (i + 1) % 10 == 0:
            print(f"   ...{i+1}/{len(syms)} tickers done")

    r = pd.DataFrame(rows)
    if r.empty:
        print("No evaluations produced."); return
    out_csv = SKILL_DIR / "data" / "vn" / "eval_compare.csv"
    r.to_csv(out_csv, index=False)

    moved = r[r.moved == 1]
    print("\n================= KRONOS  VN-finetuned  vs  BASE  (held-out test) =================")
    print(f"  samples evaluated     : {len(r)}  ({r.sym.nunique()} tickers)")
    print(f"  horizon               : {args.horizon} bars")
    print(f"  --- MAE% of close over horizon (lower = better) ---")
    print(f"    VN-finetuned        : {r.mae_vn.mean():.3f}%")
    print(f"    base small          : {r.mae_bs.mean():.3f}%")
    print(f"    naive flat baseline : {r.mae_flat.mean():.3f}%")
    print(f"    VN improvement      : {(r.mae_bs.mean() - r.mae_vn.mean()):+.3f}pp vs base "
          f"({(1 - r.mae_vn.mean()/r.mae_bs.mean())*100:+.1f}% relative)")
    print(f"  --- Directional accuracy at horizon end (excl. flat days, n={len(moved)}) ---")
    print(f"    VN-finetuned        : {moved.dvn.mean()*100:.1f}%")
    print(f"    base small          : {moved.dbs.mean()*100:.1f}%")
    print(f"\n>> wrote {out_csv}")


if __name__ == "__main__":
    main()
