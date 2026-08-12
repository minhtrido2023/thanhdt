"""Mô phỏng THỰC THI trên bar 1 phút thật — rổ mã thanh khoản mỏng (case TV1).

R&D ONLY. Không import, không sửa, không chạy production code. Namespace exp_* (§8).

CÂU HỎI: cơ chế đặt lệnh hiện tại (trần giá tuyệt đối `hard_no_chase_ceiling_vnd` +
pacing `min(10%×ADV20, 30%×KL_luỹ_kế_trong_ngày)`) mất fill ở đâu, và sửa chỗ nào
thì được lại bao nhiêu?

PHÂN RÃ 3 TẦNG RÀNG BUỘC (mỗi tầng là 1 nguyên nhân khác nhau, KHÔNG gộp):
  L1 GIÁ    — KL thật đã khớp ở giá ≤ trần trong phiên. Trần dưới thị trường ⇒ L1=0,
              không thuật toán nào cứu được.
  L2 PACING — KL tối đa executor CHO PHÉP hiển thị, replay đúng công thức
              `_child_qty` theo từng phút (allowance = min(ADV20-floor, 30%×cum_vol)).
  L3 CAPTURE— phần của L1 mà một lệnh nằm chờ thực sự giành được (κ). KHÔNG quan sát
              được từ dữ liệu này ⇒ chạy 3 mức κ để xem kết luận có đổi dấu không.

Fill mỗi phút = min(hiển_thị_t , κ × KL_khớp_ở_giá≤limit_t).

GIỚI HẠN DỮ LIỆU (đo, không suy diễn — xem probe_pull_1m.py):
  • KHÔNG có sổ lệnh (order book) lịch sử. Mọi con số "depth" ở đây là KL ĐÃ KHỚP,
    không phải KL chờ. Chúng là CẬN DƯỚI của thanh khoản khả dụng.
  • Bar 1 phút chỉ có OHLCV ⇒ khi low_t < trần < high_t, KL ở ≤trần được nội suy
    tuyến tính theo vị trí trần trong biên độ bar (xem `_vol_at_or_below`). Với mã
    mỏng phần lớn bar là 1 giá (high==low) nên phần nội suy này nhỏ — có đo, in ra.
"""
import os
import sys
import glob
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
BARS = os.path.join(HERE, "data", "bars1m")
OUTD = os.path.join(HERE, "out")
os.makedirs(OUTD, exist_ok=True)

LOT = 100
# --- hằng số sao chép từ trading_bot/config.py (đọc 2026-08-12, KHÔNG import) ---
MAX_CHILD_VALUE = 200_000_000
MAX_PARTICIPATION = 0.10          # ADV20-floor
REALIZED_CEIL = 0.30              # capit_realized_participation_ceiling
SLICE_INTERVAL_MIN = 8


def load_bars(path):
    """⚠ vnstock/VCI trả giá theo NGHÌN ĐỒNG (19.8 = 19.800đ) — quy về VND ngay tại
    biên nạp, nếu không `max_child_value` (VND tuyệt đối) sẽ không bao giờ ràng buộc."""
    df = pd.read_csv(path, parse_dates=["time"])
    for c in ("open", "high", "low", "close"):
        df[c] = df[c] * 1000.0
    df["date"] = df["time"].dt.date
    df["minute"] = df["time"].dt.hour * 60 + df["time"].dt.minute
    return df.dropna(subset=["close"])


def _vol_at_or_below(bar_low, bar_high, vol, limit):
    """KL của bar khớp ở giá ≤ limit. Bar 1 giá (high==low) → all-or-nothing.
    Bar có biên độ → nội suy tuyến tính theo vị trí limit trong [low, high]."""
    if limit < bar_low:
        return 0.0
    if limit >= bar_high:
        return float(vol)
    return float(vol) * (limit - bar_low) / (bar_high - bar_low)


def daily_agg(df):
    g = df.groupby("date").agg(vol=("volume", "sum"), close=("close", "last"),
                               hi=("high", "max"), lo=("low", "min"),
                               first=("close", "first"))
    g["turnover"] = g.vol * g.close
    g["adv20_vnd"] = g.turnover.rolling(20, min_periods=10).mean().shift(1)
    return g


def simulate_session(bars, target_qty, ceiling, adv20_vnd, kappa, pacing="current",
                     window=None):
    """1 phiên. Trả dict các tầng ràng buộc + fill.

    pacing: 'current'  = min(ADV20-floor, 30%×cum_vol)   (production hôm nay)
            'adv_only' = chỉ ADV20-floor  (bỏ trần theo KL luỹ kế)
            'none'     = không pacing (chỉ trần giá trị lệnh con)
    window: (min_from, min_to) phút trong ngày để CHO PHÉP đặt lệnh; None = cả phiên.
    """
    bars = bars.sort_values("minute")
    px_ref = float(bars.close.iloc[0])
    limit = ceiling
    filled = 0
    cum_vol = 0
    l1 = 0.0                       # KL thật ở giá ≤ trần cả phiên
    displayed_track = []
    shown = 0
    last_refresh = -999
    for r in bars.itertuples():
        avail = _vol_at_or_below(r.low, r.high, r.volume, limit)
        l1 += avail
        if window and not (window[0] <= r.minute <= window[1]):
            cum_vol += r.volume
            continue
        # refresh lệnh con theo nhịp slice_interval_min (dùng cum_vol TRƯỚC phút này —
        # executor chỉ biết tape đã khớp, không nhìn trước)
        if r.minute - last_refresh >= SLICE_INTERVAL_MIN:
            remaining = target_qty - filled
            by_value = int(MAX_CHILD_VALUE / limit)
            q = min(remaining, by_value)
            if pacing == "current" and adv20_vnd:
                floor_allow = int(MAX_PARTICIPATION * adv20_vnd / limit) - filled
                ceil_allow = int(REALIZED_CEIL * cum_vol) - filled
                allow = min(floor_allow, ceil_allow)
                q = 0 if allow < LOT else min(q, allow)
            elif pacing == "adv_only" and adv20_vnd:
                allow = int(MAX_PARTICIPATION * adv20_vnd / limit) - filled
                q = 0 if allow < LOT else min(q, allow)
            shown = (q // LOT) * LOT
            last_refresh = r.minute
            displayed_track.append(shown)
        got = min(shown, int(kappa * avail))
        got = max(0, got)
        if got > 0:
            filled += got
            shown -= got
        cum_vol += r.volume
    return {"filled": filled, "l1_avail": l1, "day_vol": cum_vol,
            "max_shown": max(displayed_track) if displayed_track else 0,
            "px_ref": px_ref}


def run_ticker(tk, path, kappa, n_sessions=60, ceil_mode="atm", target_pct_adv=0.30):
    """Chạy mô phỏng trên `n_sessions` phiên gần nhất.

    ceil_mode: 'atm'  = trần đặt tại giá đóng cửa phiên TRƯỚC (kịch bản trung tính,
                        tách hẳn khỏi vấn đề "trần bị bỏ quên dưới thị trường");
               'stale'= trần đặt tại giá đóng cửa 5 phiên trước (mô phỏng đúng bệnh
                        TV1: trần cố định trong khi giá trôi lên).
    target_pct_adv: kích thước lệnh tính theo % ADV20 (TV1 thật ≈ 5%NAV ≈ 5-6% ADV;
                    lấy 30% để phản ánh nhu cầu gom nhiều phiên của chương trình).
    """
    df = load_bars(path)
    dd = daily_agg(df)
    dates = [d for d in dd.index if not np.isnan(dd.loc[d, "adv20_vnd"] or np.nan)]
    dates = dates[-n_sessions:]
    rows = []
    for i, d in enumerate(dates):
        adv20 = dd.loc[d, "adv20_vnd"]
        if not adv20 or adv20 <= 0:
            continue
        pos = list(dd.index).index(d)
        if ceil_mode == "atm":
            ceiling = dd.iloc[pos - 1]["close"]
        else:
            if pos < 5:
                continue
            ceiling = dd.iloc[pos - 5]["close"]
        ceiling = float(ceiling)
        if ceiling <= 0:
            continue
        target = int((target_pct_adv * adv20 / ceiling) // LOT * LOT)
        if target < LOT:
            continue
        b = df[df.date == d]
        if b.empty:
            continue
        base = dict(ticker=tk, date=d, adv20_vnd=adv20, ceiling=ceiling,
                    target=target)
        for name, kw in (("S0_current", dict(pacing="current")),
                         ("S1_adv_only", dict(pacing="adv_only")),
                         ("S2_no_pacing", dict(pacing="none"))):
            r = simulate_session(b, target, ceiling, adv20, kappa, **kw)
            base[f"{name}_filled"] = r["filled"]
            base[f"{name}_shown"] = r["max_shown"]
            base["l1_avail"] = r["l1_avail"]
            base["day_vol"] = r["day_vol"]
        rows.append(base)
    return pd.DataFrame(rows)


def main():
    kappa = float(os.environ.get("KAPPA", "0.34"))
    ceil_mode = os.environ.get("CEIL_MODE", "atm")
    n_sessions = int(os.environ.get("N_SESSIONS", "80"))
    tgt = float(os.environ.get("TARGET_PCT_ADV", "0.30"))
    frames = []
    for p in sorted(glob.glob(os.path.join(BARS, "*.csv"))):
        tk = os.path.basename(p)[:-4]
        try:
            f = run_ticker(tk, p, kappa, n_sessions=n_sessions, ceil_mode=ceil_mode,
                           target_pct_adv=tgt)
            if len(f):
                frames.append(f)
        except Exception as e:
            print(f"{tk} ERR {repr(e)[:150]}")
    all_df = pd.concat(frames, ignore_index=True)
    for s in ("S0_current", "S1_adv_only", "S2_no_pacing"):
        all_df[f"{s}_fr"] = all_df[f"{s}_filled"] / all_df.target
    tag = f"k{kappa}_{ceil_mode}_t{tgt}"
    all_df.to_csv(os.path.join(OUTD, f"sim_sessions_{tag}.csv"), index=False)

    print(f"\n=== κ={kappa} ceil_mode={ceil_mode} "
          f"N={len(all_df)} phiên-mã, {all_df.ticker.nunique()} mã ===")
    print("Fill-rate 1 PHIÊN (trung bình / trung vị / %phiên khớp đủ):")
    for s in ("S0_current", "S1_adv_only", "S2_no_pacing"):
        fr = all_df[f"{s}_fr"].clip(0, 1)
        print(f"  {s:14s} mean={fr.mean():.3f}  med={fr.median():.3f}  "
              f"full={100*(fr>=0.999).mean():5.1f}%  zero={100*(fr<=0.001).mean():5.1f}%")
    # tầng ràng buộc
    all_df["l1_ratio"] = all_df.l1_avail / all_df.target
    print("\nTẦNG RÀNG BUỘC (κ-free):")
    print(f"  L1: %phiên KL thật ở giá ≤trần = 0            : "
          f"{100*(all_df.l1_avail<=0).mean():.1f}%")
    print(f"  L1: %phiên KL thật ở ≤trần < KL cần (κ=1)     : "
          f"{100*(all_df.l1_ratio<1).mean():.1f}%")
    print(f"  L2: %phiên executor CHỈ cho hiện < KL cần     : "
          f"{100*(all_df.S0_current_shown<all_df.target).mean():.1f}%")
    print(f"  L2: %phiên executor cho hiện 0 (WAIT_QUOTA)   : "
          f"{100*(all_df.S0_current_shown<LOT).mean():.1f}%")
    binding = all_df[(all_df.l1_ratio >= 1)]
    print(f"  Trong {len(binding)} phiên THỊ TRƯỜNG ĐỦ HÀNG (L1≥target): "
          f"S0 fill={binding.S0_current_fr.clip(0,1).mean():.3f} vs "
          f"S1={binding.S1_adv_only_fr.clip(0,1).mean():.3f}")
    return all_df


if __name__ == "__main__":
    main()
