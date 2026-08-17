"""Tái lập ĐỘC LẬP: trần giá Rule A (close[t-1]×1.03) vs Rule B (mean5(close)×1.03),
+ chiến lược participation-rate cho mã thanh khoản mỏng.

Job Taylor_20260814_170351 · R&D ONLY (§8: namespace exp_*, không đụng production).
Chạy: /home/trido/thanhdt/wc_venv/bin/python exp_ceiling_ab.py

VIẾT LẠI TỪ ĐẦU — cố ý KHÔNG import/copy exp_ceiling_tolerance.py hay exp_fill_sim.py của
job Taylor_20260812_091343; chỉ dùng chung DỮ LIỆU thô (bar 1 phút cache) để hai bản mô
phỏng độc lập nhau về code. Mọi tham số cơ chế đọc thẳng từ trading_bot/config.py
(giá trị chép vào CONST dưới đây kèm ngày đọc, không import trading_bot).

GIỚI HẠN (mang theo mọi con số): KHÔNG có order-book lịch sử ⇒ "hàng dưới trần" = KL ĐÃ
KHỚP ở giá ≤ trần = CẬN DƯỚI. κ (capture) không quan sát được ⇒ chạy nhiều mức.
"""
import os
import glob
import json
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
BARS_THIN = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/thin_exec_20260812/data/bars1m"
BARS_LIQ = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/thin_exec_20260812/data/bars1m_liquid"

# --- tham số cơ chế, đọc từ trading_bot/config.py ngày 2026-08-14 -------------------
LOT = 100
MAX_CHILD_VALUE = 200_000_000          # VND
MAX_PARTICIPATION = float(os.environ.get("MAXPART", "0.10"))  # floor_allow = 10% × ADV20_vnd / px
REALIZED_CEIL = 0.30                   # ceil_allow  = 30% × KL đã khớp
SLICE_INTERVAL_MIN = 8
TAPE_CLAMP = 0.50
EXPVOL_CURVE = [[555, 0.045], [570, 0.082], [585, 0.145], [600, 0.198],
                [615, 0.246], [630, 0.318], [645, 0.351], [660, 0.411],
                [675, 0.444], [690, 0.488], [780, 0.499], [795, 0.568],
                [810, 0.637], [825, 0.721], [840, 0.784], [855, 0.853],
                [870, 0.958], [885, 1.000]]
TAU = 0.03                             # +3% — cả Rule A và Rule B dùng chung, câu hỏi là ANCHOR
CAMPAIGN_LEN = int(os.environ.get("CAMPAIGN_LEN", "5"))
WARMUP = 20                            # phiên để tính ADV20 causal


def round_lot(x):
    return int(x // LOT) * LOT


_CX = np.array([p[0] for p in EXPVOL_CURVE], dtype=float)
_CY = np.array([p[1] for p in EXPVOL_CURVE], dtype=float)


def fcurve(minute_of_day):
    """f(t) = tỷ trọng KL luỹ kế kỳ vọng tới phút t. Trước mốc đầu = 0 (P2 không ăn)."""
    return np.interp(minute_of_day, _CX, _CY, left=0.0, right=1.0)


def load_bars(path):
    d = pd.read_csv(path, parse_dates=["time"])
    d = d[d.volume > 0].copy()
    d["sess"] = d.time.dt.normalize()
    d["mod"] = d.time.dt.hour * 60 + d.time.dt.minute
    return d.sort_values("time").reset_index(drop=True)


def session_frames(d):
    """-> list phiên: dict(date, mod[], close[], high[], low[], vol[]) + bảng ngày."""
    sess = []
    for dt, g in d.groupby("sess", sort=True):
        sess.append({
            "date": dt,
            "mod": g["mod"].to_numpy(dtype=np.int32),
            "close": g["close"].to_numpy(dtype=np.float64),
            "high": g["high"].to_numpy(dtype=np.float64),
            "low": g["low"].to_numpy(dtype=np.float64),
            "vol": g["volume"].to_numpy(dtype=np.float64),
        })
    daily = pd.DataFrame({
        "date": [s["date"] for s in sess],
        "close": [s["close"][-1] for s in sess],
        "vol": [s["vol"].sum() for s in sess],
        "vwap": [float((s["close"] * s["vol"]).sum() / s["vol"].sum()) for s in sess],
    })
    return sess, daily


def eligible_frac(high, low, cap):
    """Phần KL của bar khớp ở giá ≤ cap. Xấp xỉ tuyến tính trong [low, high]."""
    if cap >= high:
        return 1.0
    if cap < low:
        return 0.0
    rng = high - low
    if rng <= 0:
        return 1.0
    return (cap - low) / rng


def parse_mech(m):
    """'pr50' -> ('pr', 0.50); 'prod'/'p2'/'nocap' -> (m, mặc định)."""
    if m.startswith("pr") and m[2:].isdigit():
        return "pr", int(m[2:]) / 100.0
    return m, REALIZED_CEIL


def run_session(s, cap, adv20_vnd, adv20_cp, remaining, kappa, mech, pr_p=REALIZED_CEIL):
    """Mô phỏng 1 phiên. Trả (filled, value, tape_vol, avail_below_cap).

    mech: 'prod' = cơ chế LIVE hôm nay (trần phụ 30% × KL ĐÃ khớp)
          'p2'   = mẫu số max(KL đã khớp, ADV20_cp×f(t)) + clamp đuôi 50% tape (đã wire PAPER)
          'pr'   = participation-rate thuần: allowance = p × ADV20_cp×f(t) − đã khớp, + clamp
          'nocap'= bỏ hẳn trần phụ (chỉ còn ADV20-floor) — cận trên tham chiếu
    """
    mod, close, high, low, vol = s["mod"], s["close"], s["high"], s["low"], s["vol"]
    n = len(vol)
    cum_vol = 0.0
    day_filled = 0
    filled = 0
    value = 0.0
    display = 0
    avail = 0.0
    last_refresh = -10**6
    for i in range(n):
        px = close[i]
        frac = eligible_frac(high[i], low[i], cap)
        elig = vol[i] * frac
        avail += elig
        if (remaining - filled >= LOT
                and (mod[i] - last_refresh >= SLICE_INTERVAL_MIN or display < LOT)):
            last_refresh = mod[i]
            # px theo NGHÌN đồng (VCI) ⇒ quy về VND trước khi chia giá trị
            floor_allow = int(MAX_PARTICIPATION * adv20_vnd / (px * 1000.0)) - day_filled
            if mech == "prod":
                allow = min(floor_allow, int(REALIZED_CEIL * cum_vol) - day_filled)
            elif mech == "p2":
                basis = max(cum_vol, adv20_cp * fcurve(mod[i]))
                allow = min(floor_allow, int(REALIZED_CEIL * basis) - day_filled)
                clamp = int((TAPE_CLAMP * cum_vol - day_filled) / (1.0 - TAPE_CLAMP))
                allow = min(allow, clamp)
            elif mech == "pr":
                basis = adv20_cp * fcurve(mod[i])
                allow = int(pr_p * basis) - day_filled
                allow = min(allow, floor_allow)
                clamp = int((TAPE_CLAMP * cum_vol - day_filled) / (1.0 - TAPE_CLAMP))
                allow = min(allow, clamp)
            else:                       # nocap
                allow = floor_allow
            by_value = int(MAX_CHILD_VALUE / (px * 1000.0))   # giá VCI theo NGHÌN đồng
            display = round_lot(max(0, min(remaining - filled, allow, by_value)))
        cum_vol += vol[i]
        if display >= LOT and elig > 0:
            take = round_lot(min(display, kappa * elig))
            if take >= LOT:
                px_fill = min(px, cap)
                filled += take
                value += take * px_fill
                day_filled += take
                display -= take
    return filled, value, avail


def build_campaigns(daily):
    """Khối 5 phiên KHÔNG chồng lấn sau warm-up. N = số campaign độc lập."""
    n = len(daily)
    out = []
    i = WARMUP
    while i + CAMPAIGN_LEN <= n:
        out.append(i)
        i += CAMPAIGN_LEN
    return out


def main():
    files = sorted(glob.glob(os.path.join(BARS_THIN, "*.csv")))
    files += sorted(glob.glob(os.path.join(BARS_LIQ, "*.csv")))
    kappas = [float(x) for x in os.environ.get("KAPPAS", "0.20,0.34,0.50").split(",")]
    size_pcts = [float(x) for x in os.environ.get("SIZES", "0.10").split(",")]
    mechs = os.environ.get("MECHS", "prod").split(",")
    rows = []
    for f in files:
        tk = os.path.basename(f)[:-4]
        d = load_bars(f)
        sess, daily = session_frames(d)
        if len(daily) < WARMUP + CAMPAIGN_LEN:
            print(f"skip {tk}: {len(daily)} phiên"); continue
        c = daily["close"].to_numpy()
        v = daily["vol"].to_numpy()
        # ADV20 CAUSAL: trung bình 20 phiên TRƯỚC phiên hiện tại
        adv_cp = pd.Series(v).rolling(20).mean().shift(1).to_numpy()
        adv_vnd = pd.Series(v * c * 1000.0).rolling(20).mean().shift(1).to_numpy()
        mean5 = pd.Series(c).rolling(5).mean().shift(1).to_numpy()
        prev = pd.Series(c).shift(1).to_numpy()
        for start in build_campaigns(daily):
            a20cp, a20vnd = adv_cp[start], adv_vnd[start]
            if not np.isfinite(a20cp) or a20cp <= 0:
                continue
            for spct in size_pcts:
                Q = round_lot(spct * a20cp)
                if Q < LOT:
                    continue
                bench_num = bench_den = 0.0
                for k in range(CAMPAIGN_LEN):
                    j = start + k
                    bench_num += daily["vwap"].iloc[j] * v[j]
                    bench_den += v[j]
                bench = bench_num / bench_den if bench_den else np.nan
                for mech_raw in mechs:
                    mech, pr_p = parse_mech(mech_raw)
                    for kappa in kappas:
                        for rule in os.environ.get("RULES", "A,B").split(","):
                            filled = 0
                            value = 0.0
                            avail = 0.0
                            tape = 0.0
                            for k in range(CAMPAIGN_LEN):
                                j = start + k
                                if rule == "A":
                                    anchor = prev[j]          # close phiên trước, rolling
                                elif rule == "B":
                                    anchor = mean5[j]         # mean-5 close, rolling
                                else:                          # "C" = ĐÓNG BĂNG lúc lập plan
                                    anchor = prev[start]       # (tái lập đúng bệnh TV1 20.000đ)
                                if not np.isfinite(anchor):
                                    continue
                                cap = anchor * (1.0 + TAU)
                                fq, val, av = run_session(
                                    sess[j], cap, adv_vnd[j], adv_cp[j],
                                    Q - filled, kappa, mech, pr_p)
                                filled += fq
                                value += val
                                avail += av
                                tape += v[j]
                                if filled >= Q:
                                    break
                            rows.append({
                                "ticker": tk, "start": str(daily["date"].iloc[start].date()),
                                "rule": rule, "mech": mech_raw, "kappa": kappa, "size_pct": spct,
                                "Q": Q, "filled": filled,
                                "fill_frac": filled / Q,
                                "complete": int(filled >= Q),
                                "avg_px": (value / filled) if filled else np.nan,
                                "bench_vwap": bench,
                                "adv20_vnd_mn": a20vnd / 1e6,
                                "avail_below_cap": avail, "tape": tape,
                            })
        print(f"{tk}: {len(daily)} phiên, campaigns={len(build_campaigns(daily))}", flush=True)
    df = pd.DataFrame(rows)
    tag = os.environ.get("TAG", "main")
    p = os.path.join(OUT, f"campaigns_{tag}.csv")
    df.to_csv(p, index=False)
    print(f"\nwrote {p}  rows={len(df)}")
    return df


if __name__ == "__main__":
    main()
