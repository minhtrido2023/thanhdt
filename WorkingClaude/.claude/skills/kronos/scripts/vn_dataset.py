"""
Multi-ticker dataset for Kronos VN fine-tuning.

Mirrors the official finetune/dataset.py QlibDataset exactly (windows are built
*within* each ticker — no cross-ticker leakage; normalization stats come from the
lookback portion only), but loads our BigQuery-exported pickle instead of qlib.
"""
import pickle
import random

import numpy as np
import torch
from torch.utils.data import Dataset

FEATURES = ["open", "high", "low", "close", "vol", "amt"]
TIME_FEATURES = ["minute", "hour", "weekday", "day", "month"]


class VNMultiTickerDataset(Dataset):
    def __init__(self, pkl_path, lookback_window=90, predict_window=10, clip=5.0,
                 seed=100, max_samples=None):
        self.lookback_window = lookback_window
        self.predict_window = predict_window
        self.window = lookback_window + predict_window + 1
        self.clip = clip
        self.seed = seed
        self.py_rng = random.Random(seed)

        with open(pkl_path, "rb") as f:
            data = pickle.load(f)

        self.data = {}
        self.indices = []
        for symbol, df in data.items():
            df = df.reset_index()
            dt = df["datetime"]
            df["minute"] = dt.dt.minute
            df["hour"] = dt.dt.hour
            df["weekday"] = dt.dt.weekday
            df["day"] = dt.dt.day
            df["month"] = dt.dt.month
            cols = [c for c in FEATURES if c in df.columns]
            if len(cols) < len(FEATURES):
                raise ValueError(f"{symbol}: missing feature columns {set(FEATURES) - set(cols)}")
            frame = df[FEATURES + TIME_FEATURES].copy()
            if frame.isnull().any().any():
                frame = frame.ffill().bfill()
            n = len(frame) - self.window + 1
            if n <= 0:
                continue
            self.data[symbol] = frame
            for i in range(n):
                self.indices.append((symbol, i))

        if not self.indices:
            raise ValueError(f"No usable windows in {pkl_path} "
                             f"(need >= {self.window} bars per ticker).")
        total = len(self.indices)
        self.n_samples = min(max_samples, total) if max_samples else total
        print(f">> {pkl_path}: {len(self.data)} tickers, {total:,} windows, "
              f"using {self.n_samples:,}/epoch")

    def set_epoch_seed(self, epoch):
        self.py_rng.seed(self.seed + epoch)

    def __len__(self):
        return self.n_samples

    def __getitem__(self, idx):
        symbol, start = self.indices[self.py_rng.randint(0, len(self.indices) - 1)]
        df = self.data[symbol]
        win = df.iloc[start:start + self.window]
        x = win[FEATURES].values.astype(np.float32)
        x_stamp = win[TIME_FEATURES].values.astype(np.float32)

        past = x[:self.lookback_window]
        mean, std = past.mean(axis=0), past.std(axis=0)
        x = (x - mean) / (std + 1e-5)
        x = np.clip(x, -self.clip, self.clip)
        return torch.from_numpy(x), torch.from_numpy(x_stamp)
