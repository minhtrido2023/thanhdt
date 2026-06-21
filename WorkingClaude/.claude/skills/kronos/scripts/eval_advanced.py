#!/usr/bin/env python3
"""
Advanced held-out evaluation of the VN-fine-tuned Kronos, three lenses:

  A. VOLATILITY / CALIBRATION  - is the model's predicted uncertainty trustworthy?
     * coverage: do actual closes land inside the sampled +/-1sigma (68%) and
       5-95% (90%) bands at the right frequency?
     * vol-skill: does predicted terminal-return std correlate with the actual
       size of the move, and does it beat a naive trailing-vol baseline?
  B. CROSS-SECTIONAL RANKING (the decisive test) - on common dates, rank ALL
     tickers by Kronos predicted H-return; measure rank-IC (Spearman) and the
     realized long/short decile spread. Absolute direction can be coin-flip yet
     the cross-section still tradeable.
  C. LONG HORIZON - MAE% and directional accuracy at H=20/40/60 (1M/2M/3M),
     VN vs base, where trend/mean-reversion may carry more signal than 5d.

All on test_data.pkl (dates never trained on). CPU-friendly. See SKILL.md.
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
PRICE6 = ["open", "high", "low", "close", "volume", "amount"]


def spearman(a, b):
    a = pd.Series(a).rank().values
    b = pd.Series(b).rank().values
    if np.std(a) == 0 or np.std(b) == 0:
        return np.nan
    return float(np.corrcoef(a, b)[0, 1])


def predict_paths(pred, ctx, y_ts, H, T, top_p, samples, seed):
    """Return the array of sampled terminal close paths: shape (samples, H)."""
    x_df = ctx.rename(columns=REN)[PRICE6].reset_index(drop=True)
    paths = np.empty((samples, H), dtype=float)
    for k in range(samples):
        torch.manual_seed(seed + k)
        out = pred.predict(df=x_df, x_timestamp=ctx["datetime"], y_timestamp=y_ts,
                           pred_len=H, T=T, top_p=top_p, sample_count=1, verbose=False)
        paths[k] = out["close"].values
    return paths


def get_frames(data):
    out = {}
    for s, df in data.items():
        df = df.reset_index()
        if "datetime" not in df.columns:
            df = df.rename(columns={df.columns[0]: "datetime"})
        out[s] = df
    return out


# ----------------------------------------------------------------------------- A
def run_A(vn, frames, syms, lookback, H, samples, T, top_p, cuts, seed):
    print(f"\n[A] volatility/calibration: {len(syms)} tickers x {cuts} cuts, "
          f"H={H}, samples={samples}")
    cov68 = cov90 = n = 0
    pk, pn, am = [], [], []  # pred-vol kronos, pred-vol naive, |actual ret|
    for i, s in enumerate(syms):
        df = frames[s]
        latest = len(df) - H
        if latest <= lookback:
            continue
        for cut in sorted(set(int(c) for c in np.linspace(lookback, latest, cuts))):
            ctx = df.iloc[cut - lookback:cut]
            fut = df.iloc[cut:cut + H]
            if len(fut) < H:
                continue
            last = float(ctx["close"].iloc[-1])
            paths = predict_paths(vn, ctx, fut["datetime"], H, T, top_p, samples, seed)
            term = paths[:, -1]
            act = float(fut["close"].iloc[-1])
            lo16, hi84 = np.percentile(term, 16), np.percentile(term, 84)
            lo05, hi95 = np.percentile(term, 5), np.percentile(term, 95)
            cov68 += int(lo16 <= act <= hi84)
            cov90 += int(lo05 <= act <= hi95)
            n += 1
            pk.append(np.std(term / last - 1.0))
            rets = ctx["close"].pct_change().dropna().values
            pn.append(np.std(rets) * np.sqrt(H))
            am.append(abs(act / last - 1.0))
        if (i + 1) % 20 == 0:
            print(f"   A ...{i+1}/{len(syms)}")
    return dict(n=n, cov68=cov68 / max(n, 1), cov90=cov90 / max(n, 1),
                ic_kronos=spearman(pk, am), ic_naive=spearman(pn, am))


# ----------------------------------------------------------------------------- B
def run_B(models, frames, syms, lookback, H, samples, T, top_p, n_dates, seed):
    print(f"\n[B] cross-sectional ranking: H={H}, {n_dates} dates, "
          f"{len(syms)} tickers, samples={samples}")
    # reference date grid from the longest ticker
    ref = max(syms, key=lambda s: len(frames[s]))
    rdf = frames[ref]
    valid = rdf["datetime"].iloc[lookback: len(rdf) - H].reset_index(drop=True)
    targets = [valid.iloc[int(c)] for c in np.linspace(0, len(valid) - 1, n_dates)]
    res = {m: {"ic": [], "spread": []} for m in models}
    for di, D in enumerate(targets):
        rows = {m: [] for m in models}
        for s in syms:
            df = frames[s]
            pos = df.index[df["datetime"] <= D]
            if len(pos) < lookback:
                continue
            cut = int(pos[-1]) + 1
            if cut + H > len(df) or cut < lookback:
                continue
            ctx = df.iloc[cut - lookback:cut]
            fut = df.iloc[cut:cut + H]
            if len(fut) < H:
                continue
            last = float(ctx["close"].iloc[-1])
            act_ret = float(fut["close"].iloc[-1]) / last - 1.0
            for m, pred in models.items():
                paths = predict_paths(pred, ctx, fut["datetime"], H, T, top_p, samples, seed)
                pred_ret = float(np.mean(paths[:, -1]) / last - 1.0)
                rows[m].append((s, pred_ret, act_ret))
        for m in models:
            r = rows[m]
            if len(r) < 10:
                continue
            pr = np.array([x[1] for x in r]); ar = np.array([x[2] for x in r])
            res[m]["ic"].append(spearman(pr, ar))
            k = max(1, len(r) // 10)
            order = np.argsort(pr)
            bot = ar[order[:k]].mean(); top = ar[order[-k:]].mean()
            res[m]["spread"].append(top - bot)
        print(f"   B date {di+1}/{n_dates} ({pd.Timestamp(D).date()}): "
              + " ".join(f"{m} IC={np.mean(res[m]['ic'][-1:]) if res[m]['ic'] else float('nan'):+.3f}"
                         for m in models))
    return {m: dict(ic=float(np.nanmean(res[m]["ic"])) if res[m]["ic"] else float("nan"),
                    spread=float(np.nanmean(res[m]["spread"])) * 100 if res[m]["spread"] else float("nan"),
                    n_dates=len(res[m]["ic"])) for m in models}


# ----------------------------------------------------------------------------- C
def run_C(models, frames, syms, lookback, horizons, samples, T, top_p, cuts, seed):
    print(f"\n[C] long horizon: H={horizons}, {len(syms)} tickers x {cuts} cuts")
    out = {}
    for H in horizons:
        agg = {m: {"mae": [], "dir": [], "moved": []} for m in models}
        for s in syms:
            df = frames[s]
            latest = len(df) - H
            if latest <= lookback:
                continue
            for cut in sorted(set(int(c) for c in np.linspace(lookback, latest, cuts))):
                ctx = df.iloc[cut - lookback:cut]
                fut = df.iloc[cut:cut + H]
                if len(fut) < H:
                    continue
                last = float(ctx["close"].iloc[-1])
                act = fut["close"].values.astype(float)
                dir_act = np.sign(act[-1] - last)
                for m, pred in models.items():
                    paths = predict_paths(pred, ctx, fut["datetime"], H, T, top_p, samples, seed)
                    pc = paths.mean(axis=0)
                    agg[m]["mae"].append(np.mean(np.abs(pc / act - 1.0)) * 100)
                    agg[m]["dir"].append(int(np.sign(pc[-1] - last) == dir_act))
                    agg[m]["moved"].append(int(dir_act != 0))
        row = {}
        for m in models:
            mv = np.array(agg[m]["moved"], dtype=bool)
            d = np.array(agg[m]["dir"])
            row[m] = dict(mae=float(np.mean(agg[m]["mae"])),
                          dir=float(d[mv].mean() * 100) if mv.any() else float("nan"),
                          n=len(agg[m]["mae"]))
        # naive flat MAE for reference (model-independent)
        out[H] = row
        print(f"   C H={H}: " + " ".join(f"{m} MAE={row[m]['mae']:.2f}% dir={row[m]['dir']:.0f}%" for m in models))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(SKILL_DIR / "data" / "vn" / "test_data.pkl"))
    ap.add_argument("--lookback", type=int, default=120)
    ap.add_argument("--threads", type=int, default=16)
    ap.add_argument("--seed", type=int, default=11)
    # A
    ap.add_argument("--a-tickers", type=int, default=60)
    ap.add_argument("--a-cuts", type=int, default=2)
    ap.add_argument("--a-h", type=int, default=10)
    ap.add_argument("--a-samples", type=int, default=30)
    # B
    ap.add_argument("--b-tickers", type=int, default=150)
    ap.add_argument("--b-dates", type=int, default=4)
    ap.add_argument("--b-h", type=int, default=20)
    ap.add_argument("--b-samples", type=int, default=5)
    # C
    ap.add_argument("--c-tickers", type=int, default=40)
    ap.add_argument("--c-cuts", type=int, default=2)
    ap.add_argument("--c-horizons", default="20,40,60")
    ap.add_argument("--c-samples", type=int, default=8)
    ap.add_argument("--T", type=float, default=0.7)
    ap.add_argument("--top-p", type=float, default=0.9)
    ap.add_argument("--quick", action="store_true", help="tiny smoke run")
    ap.add_argument("--skip", default="", help="comma list of A,B,C to skip")
    args = ap.parse_args()

    if args.quick:
        args.a_tickers = args.b_tickers = args.c_tickers = 8
        args.a_cuts = args.c_cuts = 1
        args.b_dates = 1
        args.a_samples = 6; args.b_samples = 3; args.c_samples = 4
        args.c_horizons = "20"

    if not torch.cuda.is_available():
        torch.set_num_threads(args.threads)
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    max_ctx = max(512, args.lookback)

    with open(args.data, "rb") as f:
        data = pickle.load(f)
    frames = get_frames(data)
    allsyms = sorted(frames)
    print(f">> test universe: {len(allsyms)} tickers, device={device}, lookback={args.lookback}")

    base = KronosPredictor(Kronos.from_pretrained("NeoQuasar/Kronos-small"),
                           KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base"),
                           device=device, max_context=max_ctx)
    vn = KronosPredictor(Kronos.from_pretrained(str(VN_PRED)),
                         KronosTokenizer.from_pretrained(str(VN_TOK)),
                         device=device, max_context=max_ctx)
    models = {"VN": vn, "base": base}
    skip = set(x.strip().upper() for x in args.skip.split(",") if x.strip())

    report = {}
    if "A" not in skip:
        report["A"] = run_A(vn, frames, allsyms[:args.a_tickers], args.lookback,
                            args.a_h, args.a_samples, args.T, args.top_p, args.a_cuts, args.seed)
    if "B" not in skip:
        report["B"] = run_B(models, frames, allsyms[:args.b_tickers], args.lookback,
                            args.b_h, args.b_samples, args.T, args.top_p, args.b_dates, args.seed)
    if "C" not in skip:
        hs = [int(x) for x in args.c_horizons.split(",")]
        report["C"] = run_C(models, frames, allsyms[:args.c_tickers], args.lookback,
                            hs, args.c_samples, args.T, args.top_p, args.c_cuts, args.seed)

    print("\n" + "=" * 78)
    print("KRONOS VN — ADVANCED EVAL (held-out test)")
    print("=" * 78)
    if "A" in report:
        a = report["A"]
        print(f"[A] CALIBRATION/VOL (VN, n={a['n']}):")
        print(f"    coverage  +/-1sigma : {a['cov68']*100:.1f}%  (ideal 68%)")
        print(f"    coverage  5-95%    : {a['cov90']*100:.1f}%  (ideal 90%)")
        print(f"    vol-skill IC (pred-vol vs |actual move|): Kronos {a['ic_kronos']:+.3f}  "
              f"naive {a['ic_naive']:+.3f}  -> {'KRONOS better' if a['ic_kronos']>a['ic_naive'] else 'naive better/equal'}")
    if "B" in report:
        print(f"[B] CROSS-SECTIONAL RANKING (H={args.b_h}, {report['B']['VN']['n_dates']} dates):")
        for m in ("VN", "base"):
            b = report["B"][m]
            print(f"    {m:4s}: rank-IC {b['ic']:+.3f}   long-short decile spread {b['spread']:+.2f}%")
    if "C" in report:
        print(f"[C] LONG HORIZON (VN vs base):")
        for H, row in report["C"].items():
            print(f"    H={H:>2}d: VN MAE {row['VN']['mae']:.2f}% dir {row['VN']['dir']:.0f}% | "
                  f"base MAE {row['base']['mae']:.2f}% dir {row['base']['dir']:.0f}%  (n={row['VN']['n']})")
    print("=" * 78)
    import json
    outp = SKILL_DIR / "data" / "vn" / "eval_advanced.json"
    with open(outp, "w") as f:
        json.dump(report, f, indent=2, default=float)
    print(f">> wrote {outp}")


if __name__ == "__main__":
    main()
