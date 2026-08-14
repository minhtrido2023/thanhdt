"""Đường đổi chác GIÁ ↔ FILL của trần no-chase, trên rổ mã mỏng.

R&D only (§8). KHÔNG phá trần (§24) — chỉ đo: nếu trần là một LUẬT
`trần = anchor × (1+τ)` thay vì một SỐ đông cứng, thì τ mua được bao nhiêu fill và
phải trả bao nhiêu giá?

anchor = giá đóng cửa L phiên trước (mô phỏng "trần chốt lúc duyệt chương trình,
không xem lại" — đúng bệnh TV1: trần 20.000đ duyệt 2026-07-23, dùng tới 2026-08-12).

Hai đại lượng đối lập, phải đọc CÙNG NHAU:
  fill  — %KL gom được (cao hơn = tốt)
  slip  — giá bình quân trả / anchor − 1 (cao hơn = xấu)
"""
import os
import glob
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
BARS = os.path.join(HERE, "data", "bars1m")
OUTD = os.path.join(HERE, "out")
os.makedirs(OUTD, exist_ok=True)
LOT = 100
MAX_CHILD_VALUE = 200_000_000
MAX_PARTICIPATION = 0.10
REALIZED_CEIL = 0.30
SLICE_INTERVAL_MIN = 8


def load(path):
    df = pd.read_csv(path, parse_dates=["time"])
    for c in ("open", "high", "low", "close"):
        df[c] = df[c] * 1000.0
    df["date"] = df["time"].dt.date
    df["minute"] = df["time"].dt.hour * 60 + df["time"].dt.minute
    return df.dropna(subset=["close"])


def vol_le(lo, hi, v, lim):
    if lim < lo:
        return 0.0, 0.0
    if lim >= hi:
        return float(v), (lo + hi) / 2.0
    frac = (lim - lo) / (hi - lo)
    return float(v) * frac, (lo + lim) / 2.0     # giá bq của phần ≤ lim


def run_session(bars, target, ceiling, adv20, kappa, pacing):
    filled, cum_vol, cost = 0, 0, 0.0
    shown, last = 0, -999
    for r in bars.sort_values("minute").itertuples():
        avail, px_avg = vol_le(r.low, r.high, r.volume, ceiling)
        if r.minute - last >= SLICE_INTERVAL_MIN:
            rem = target - filled
            q = min(rem, int(MAX_CHILD_VALUE / ceiling))
            if adv20:
                floor_allow = int(MAX_PARTICIPATION * adv20 / ceiling) - filled
                if pacing == "current" and cum_vol >= 0:
                    allow = min(floor_allow, int(REALIZED_CEIL * cum_vol) - filled)
                else:
                    allow = floor_allow
                q = 0 if allow < LOT else min(q, allow)
            shown = (q // LOT) * LOT
            last = r.minute
        got = min(shown, int(kappa * avail))
        if got > 0:
            filled += got
            cost += got * px_avg
            shown -= got
        cum_vol += r.volume
    return filled, cost


def main():
    kappa = float(os.environ.get("KAPPA", "0.34"))
    tgt_pct = float(os.environ.get("TARGET_PCT_ADV", "0.10"))
    n_sess = int(os.environ.get("N_SESSIONS", "80"))
    rows = []
    for p in sorted(glob.glob(os.path.join(BARS, "*.csv"))):
        tk = os.path.basename(p)[:-4]
        df = load(p)
        dd = df.groupby("date").agg(vol=("volume", "sum"), close=("close", "last"))
        dd["turn"] = dd.vol * dd.close
        dd["adv20"] = dd.turn.rolling(20, min_periods=10).mean().shift(1)
        dd = dd.dropna()
        idx = list(dd.index)
        for pos in range(max(20, len(idx) - n_sess), len(idx)):
            d = idx[pos]
            adv20 = float(dd.iloc[pos]["adv20"])
            b = df[df.date == d]
            if b.empty or adv20 <= 0:
                continue
            for lag in (5, 10, 20):
                anchor = float(dd.iloc[pos - lag]["close"])
                target = int((tgt_pct * adv20 / anchor) // LOT * LOT)
                if target < LOT:
                    continue
                for tau in (0.0, 0.01, 0.02, 0.03, 0.05):
                    ceil = anchor * (1 + tau)
                    for pac in ("current", "adv_only"):
                        f, c = run_session(b, target, ceil, adv20, kappa, pac)
                        rows.append({"ticker": tk, "date": d, "lag": lag, "tau": tau,
                                     "pacing": pac, "target": target, "filled": f,
                                     "cost": c, "anchor": anchor})
    d = pd.DataFrame(rows)
    d.to_csv(os.path.join(OUTD, f"tolerance_k{kappa}_t{tgt_pct}.csv"), index=False)
    d["fr"] = (d.filled / d.target).clip(0, 1)
    d["slip"] = np.where(d.filled > 0, d.cost / d.filled.replace(0, np.nan) / d.anchor - 1,
                         np.nan)
    print(f"=== κ={kappa}, lệnh = {tgt_pct*100:.0f}% ADV20, N={d.date.nunique()} ngày "
          f"× {d.ticker.nunique()} mã ===")
    print(f"{'anchor cũ':>10}{'τ trần':>8}{'pacing':>11}{'fill TB':>10}"
          f"{'%phiên fill=0':>15}{'slippage TB':>13}")
    for lag in (5, 10, 20):
        for pac in ("current", "adv_only"):
            for tau in (0.0, 0.01, 0.02, 0.03, 0.05):
                s = d[(d.lag == lag) & (d.tau == tau) & (d.pacing == pac)]
                if not len(s):
                    continue
                print(f"{lag:>8}p{tau*100:>7.0f}%{pac:>11}{s.fr.mean():>10.3f}"
                      f"{100*(s.filled<LOT).mean():>14.1f}%"
                      f"{100*s.slip.mean():>12.2f}%")
        print()
    return d


if __name__ == "__main__":
    main()
