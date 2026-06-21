#!/usr/bin/env python3
"""
Fine-tune Kronos on the Vietnamese market (BigQuery-exported pickles).

Self-contained single-process driver — runs on GPU (cuda) OR CPU. It removes the
official pipeline's hard dependency on CUDA+DDP+comet_ml, but reuses the EXACT
loss formulas from the Kronos repo:
  * Tokenizer: recon_loss(z_pre)+recon_loss(z) + bsq_loss, averaged   (finetune_csv/finetune_tokenizer.py)
  * Predictor: head.compute_loss over the two token streams           (finetune_csv/finetune_base_model.py)

Two phases, run in order by default:
  1. Fine-tune the tokenizer  -> finetuned/vn/tokenizer/best_model
  2. Fine-tune the predictor  -> finetuned/vn/predictor/best_model
The forecast runner auto-loads these once present. See SKILL.md.

GPU strongly recommended. CPU works for a small smoke run (use --max-train-samples
small, --epochs 1) but a full VN fine-tune on CPU is impractically slow.
"""
import argparse
import sys
import time
from pathlib import Path

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader

SKILL_DIR = Path(__file__).resolve().parent.parent
KRONOS_DIR = SKILL_DIR / "vendor" / "Kronos"
sys.path.insert(0, str(KRONOS_DIR))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # vn_dataset

from vn_dataset import VNMultiTickerDataset  # noqa: E402

# Pretrained HF ids per base size (predictor + matching tokenizer).
BASES = {
    "mini":  ("NeoQuasar/Kronos-mini",  "NeoQuasar/Kronos-Tokenizer-2k"),
    "small": ("NeoQuasar/Kronos-small", "NeoQuasar/Kronos-Tokenizer-base"),
    "base":  ("NeoQuasar/Kronos-base",  "NeoQuasar/Kronos-Tokenizer-base"),
}


def make_loader(pkl, lb, pw, clip, bs, workers, max_samples, seed):
    ds = VNMultiTickerDataset(pkl, lookback_window=lb, predict_window=pw, clip=clip,
                              seed=seed, max_samples=max_samples)
    dl = DataLoader(ds, batch_size=bs, shuffle=True, num_workers=workers,
                    drop_last=True, pin_memory=torch.cuda.is_available())
    return ds, dl


# ---------------------------------------------------------------------------
# Phase 1: tokenizer
# ---------------------------------------------------------------------------
def finetune_tokenizer(args, device, data_dir, out_dir):
    from model import KronosTokenizer
    _, tok_id = BASES[args.base]
    print(f"\n===== PHASE 1: tokenizer ({tok_id}) =====")
    tok = KronosTokenizer.from_pretrained(tok_id).to(device)

    tr_ds, tr = make_loader(data_dir / "train_data.pkl", args.lookback, args.predict,
                            args.clip, args.batch_size, args.workers,
                            args.max_train_samples, args.seed)
    va_ds, va = make_loader(data_dir / "val_data.pkl", args.lookback, args.predict,
                            args.clip, args.batch_size, args.workers,
                            args.max_val_samples, args.seed + 1)

    opt = torch.optim.AdamW(tok.parameters(), lr=args.tok_lr, weight_decay=args.wd)
    sched = torch.optim.lr_scheduler.OneCycleLR(
        opt, max_lr=args.tok_lr, steps_per_epoch=len(tr), epochs=args.epochs,
        pct_start=0.03, div_factor=10)

    best = float("inf")
    save_path = out_dir / "tokenizer" / "best_model"
    for epoch in range(args.epochs):
        tok.train(); tr_ds.set_epoch_seed(epoch * 10000); t0 = time.time(); run = 0.0
        for bi, (x, _) in enumerate(tr):
            x = x.to(device)
            zs, bsq_loss, _, _ = tok(x)
            z_pre, z = zs
            recon = F.mse_loss(z_pre, x) + F.mse_loss(z, x)
            loss = (recon + bsq_loss) / 2
            opt.zero_grad(); loss.backward()
            torch.nn.utils.clip_grad_norm_(tok.parameters(), 2.0)
            opt.step(); sched.step(); run += loss.item()
            if (bi + 1) % args.log_interval == 0:
                print(f"  [tok e{epoch+1} {bi+1}/{len(tr)}] loss={run/(bi+1):.4f} "
                      f"lr={opt.param_groups[0]['lr']:.2e}")
        # validation
        tok.eval(); va_ds.set_epoch_seed(0); vs = 0.0; nb = 0
        with torch.no_grad():
            for x, _ in va:
                x = x.to(device)
                zs, bsq_loss, _, _ = tok(x)
                z_pre, z = zs
                vloss = (F.mse_loss(z_pre, x) + F.mse_loss(z, x) + bsq_loss) / 2
                vs += vloss.item(); nb += 1
        vmean = vs / max(nb, 1)
        print(f">> tok epoch {epoch+1}/{args.epochs}  val={vmean:.4f}  ({time.time()-t0:.0f}s)")
        if vmean < best:
            best = vmean
            save_path.parent.mkdir(parents=True, exist_ok=True)
            tok.save_pretrained(str(save_path))
            print(f"   saved best tokenizer -> {save_path} (val {best:.4f})")
    return save_path


# ---------------------------------------------------------------------------
# Phase 2: predictor
# ---------------------------------------------------------------------------
def finetune_predictor(args, device, data_dir, out_dir, tok_path):
    from model import Kronos, KronosTokenizer
    pred_id, _ = BASES[args.base]
    print(f"\n===== PHASE 2: predictor ({pred_id}) =====")
    tok = KronosTokenizer.from_pretrained(str(tok_path)).eval().to(device)
    model = Kronos.from_pretrained(pred_id).to(device)

    tr_ds, tr = make_loader(data_dir / "train_data.pkl", args.lookback, args.predict,
                            args.clip, args.batch_size, args.workers,
                            args.max_train_samples, args.seed)
    va_ds, va = make_loader(data_dir / "val_data.pkl", args.lookback, args.predict,
                            args.clip, args.batch_size, args.workers,
                            args.max_val_samples, args.seed + 1)

    opt = torch.optim.AdamW(model.parameters(), lr=args.pred_lr,
                            betas=(0.9, 0.95), weight_decay=args.wd)
    sched = torch.optim.lr_scheduler.OneCycleLR(
        opt, max_lr=args.pred_lr, steps_per_epoch=len(tr), epochs=args.epochs,
        pct_start=0.03, div_factor=10)

    best = float("inf")
    save_path = out_dir / "predictor" / "best_model"
    for epoch in range(args.epochs):
        model.train(); tr_ds.set_epoch_seed(epoch * 10000); t0 = time.time()
        for bi, (x, stamp) in enumerate(tr):
            x = x.to(device); stamp = stamp.to(device)
            with torch.no_grad():
                s0, s1 = tok.encode(x, half=True)
            logits = model(s0[:, :-1], s1[:, :-1], stamp[:, :-1, :])
            loss, _, _ = model.head.compute_loss(logits[0], logits[1], s0[:, 1:], s1[:, 1:])
            opt.zero_grad(); loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 3.0)
            opt.step(); sched.step()
            if (bi + 1) % args.log_interval == 0:
                print(f"  [pred e{epoch+1} {bi+1}/{len(tr)}] loss={loss.item():.4f} "
                      f"lr={opt.param_groups[0]['lr']:.2e}")
        # validation
        model.eval(); va_ds.set_epoch_seed(0); vs = 0.0; nb = 0
        with torch.no_grad():
            for x, stamp in va:
                x = x.to(device); stamp = stamp.to(device)
                s0, s1 = tok.encode(x, half=True)
                logits = model(s0[:, :-1], s1[:, :-1], stamp[:, :-1, :])
                vloss, _, _ = model.head.compute_loss(logits[0], logits[1], s0[:, 1:], s1[:, 1:])
                vs += vloss.item(); nb += 1
        vmean = vs / max(nb, 1)
        print(f">> pred epoch {epoch+1}/{args.epochs}  val={vmean:.4f}  ({time.time()-t0:.0f}s)")
        if vmean < best:
            best = vmean
            save_path.parent.mkdir(parents=True, exist_ok=True)
            model.save_pretrained(str(save_path))
            print(f"   saved best predictor -> {save_path} (val {best:.4f})")
    return save_path


def main():
    ap = argparse.ArgumentParser(description="Fine-tune Kronos on VN market data")
    ap.add_argument("--data", default=str(SKILL_DIR / "data" / "vn"),
                    help="dir with train_data.pkl / val_data.pkl from export_bq_to_pickle.py")
    ap.add_argument("--out", default=str(SKILL_DIR / "finetuned" / "vn"),
                    help="output dir (skill auto-loads tokenizer/ & predictor/ from here)")
    ap.add_argument("--base", default="small", choices=list(BASES))
    ap.add_argument("--phase", default="all", choices=["all", "tokenizer", "predictor"])
    ap.add_argument("--lookback", type=int, default=90)
    ap.add_argument("--predict", type=int, default=10)
    ap.add_argument("--clip", type=float, default=5.0)
    ap.add_argument("--epochs", type=int, default=10)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--tok-lr", type=float, default=2e-4)
    ap.add_argument("--pred-lr", type=float, default=4e-5)
    ap.add_argument("--wd", type=float, default=0.1)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--log-interval", type=int, default=50)
    ap.add_argument("--seed", type=int, default=100)
    ap.add_argument("--max-train-samples", type=int, default=100_000,
                    help="cap windows/epoch (lower for CPU smoke runs)")
    ap.add_argument("--max-val-samples", type=int, default=20_000)
    ap.add_argument("--device", default=None, help="cpu | cuda:0 (default auto)")
    ap.add_argument("--threads", type=int, default=8,
                    help="CPU intra-op threads. For this small model ~8 is the sweet "
                         "spot; more threads SLOW it down (op-launch overhead). Ignored on GPU.")
    args = ap.parse_args()

    if not (args.device or "").startswith("cuda") and not torch.cuda.is_available():
        torch.set_num_threads(max(1, args.threads))
        print(f">> torch CPU threads set to {torch.get_num_threads()}")

    if not KRONOS_DIR.exists():
        sys.exit(f"Kronos not vendored at {KRONOS_DIR}. Run setup.sh first.")
    data_dir = Path(args.data)
    if not (data_dir / "train_data.pkl").exists():
        sys.exit(f"No train_data.pkl in {data_dir}. Run export_bq_to_pickle.py first.")

    device = torch.device(args.device or ("cuda:0" if torch.cuda.is_available() else "cpu"))
    print(f">> device: {device}  base={args.base}  epochs={args.epochs}")
    if device.type == "cpu":
        print("!! WARNING: training on CPU is slow. For a real fine-tune use a GPU "
              "(Colab/cloud). For a smoke test pass small --max-train-samples --epochs 1.")

    out_dir = Path(args.out)
    tok_path = out_dir / "tokenizer" / "best_model"
    if args.phase in ("all", "tokenizer"):
        tok_path = finetune_tokenizer(args, device, data_dir, out_dir)
    if args.phase in ("all", "predictor"):
        if not tok_path.exists():
            sys.exit(f"Tokenizer not found at {tok_path}. Run --phase tokenizer first.")
        finetune_predictor(args, device, data_dir, out_dir, tok_path)

    print("\n>> DONE. The forecast runner will now auto-use the VN-fine-tuned weights:")
    print(f"   {out_dir/'tokenizer'/'best_model'}")
    print(f"   {out_dir/'predictor'/'best_model'}")


if __name__ == "__main__":
    main()
