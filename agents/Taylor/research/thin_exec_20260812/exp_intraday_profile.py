"""Profile thanh khoản TRONG PHIÊN + tích luỹ NHIỀU PHIÊN — rổ mã mỏng.

R&D only (§8). Trả lời 2 câu của dispatch:
  (1c) giờ nào trong phiên có "depth" tốt nhất cho nhóm mã này?
  (2a) chia lệnh ra nhiều phiên thì bao nhiêu phiên mới xong?
+ ca cụ thể TV1: trần 20.000đ so với KL thật đã khớp ở ≤20.000đ.

LƯU Ý ĐO LƯỜNG: "depth" ở đây = KL ĐÃ KHỚP theo phút (dữ liệu duy nhất có lịch sử),
KHÔNG phải KL chờ ở sổ lệnh. Với lệnh NẰM CHỜ cả phiên thì phân bố giờ gần như vô
nghĩa (nằm chờ không tốn gì); nó chỉ có ý nghĩa khi phải CHỦ ĐỘNG cắn giá (cross).
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


def sessions(path):
    """⚠ vnstock/VCI trả giá theo NGHÌN ĐỒNG — quy về VND ngay tại biên nạp."""
    df = pd.read_csv(path, parse_dates=["time"])
    for c in ("open", "high", "low", "close"):
        df[c] = df[c] * 1000.0
    df["date"] = df["time"].dt.date
    df["minute"] = df["time"].dt.hour * 60 + df["time"].dt.minute
    return df


def bucket(m):
    if m < 570:                 # < 09:30
        return "mở cửa <09:30"
    if m < 600:
        return "09:30-10:00"
    if m < 660:
        return "10:00-11:00"
    if m < 690:
        return "11:00-11:30"
    if m < 780:                 # 11:30-13:00
        return "nghỉ trưa"
    if m < 810:
        return "13:00-13:30"
    if m < 840:
        return "13:30-14:00"
    if m < 870:
        return "14:00-14:30"
    if m < 885:
        return "14:30-14:45"
    return "14:45+ (ATC)"


ORDER = ["mở cửa <09:30", "09:30-10:00", "10:00-11:00", "11:00-11:30", "nghỉ trưa",
         "13:00-13:30", "13:30-14:00", "14:00-14:30", "14:30-14:45", "14:45+ (ATC)"]


def profile():
    rows = []
    for p in sorted(glob.glob(os.path.join(BARS, "*.csv"))):
        tk = os.path.basename(p)[:-4]
        df = sessions(p)
        df = df[df.date >= sorted(df.date.unique())[-120]]
        df["b"] = df.minute.map(bucket)
        tot = df.volume.sum()
        if tot <= 0:
            continue
        g = df.groupby("b").volume.sum() / tot
        for b in ORDER:
            rows.append({"ticker": tk, "bucket": b, "share": float(g.get(b, 0.0))})
    pv = pd.DataFrame(rows).pivot(index="ticker", columns="bucket", values="share")[ORDER]
    pv.to_csv(os.path.join(OUTD, "intraday_profile.csv"))
    print("=== TỶ TRỌNG KL KHỚP THEO KHUNG GIỜ (120 phiên gần nhất, 23 mã mỏng) ===")
    print(f"{'khung giờ':<16}{'trung vị':>10}{'trung bình':>12}{'min-max mã':>18}")
    for b in ORDER:
        s = pv[b]
        print(f"{b:<16}{s.median()*100:9.1f}%{s.mean()*100:11.1f}%"
              f"{s.min()*100:8.1f}%-{s.max()*100:.1f}%")
    print(f"\nTV1 riêng: " +
          ", ".join(f"{b}={pv.loc['TV1', b]*100:.1f}%" for b in ORDER
                    if pv.loc['TV1', b] > 0.01))
    return pv


def multi_session(target_pct_adv=0.30, kappa=0.34, pacing_gain=0.0):
    """Bao nhiêu PHIÊN để gom xong lệnh = target_pct_adv × ADV20, nếu mỗi phiên chỉ
    lấy được tối đa `cap_per_session` (= 10% ADV20, trần ADV20-floor của executor)
    và thị trường phải có đủ hàng ở ≤ trần.

    Đây là câu hỏi CƠ HỌC (bao lâu), tách khỏi câu hỏi giá."""
    out = []
    for p in sorted(glob.glob(os.path.join(BARS, "*.csv"))):
        tk = os.path.basename(p)[:-4]
        df = sessions(p)
        dd = df.groupby("date").agg(vol=("volume", "sum"), close=("close", "last"))
        dd["turn"] = dd.vol * dd.close
        dd["adv20"] = dd.turn.rolling(20, min_periods=10).mean().shift(1)
        dd = dd.dropna().tail(80)
        if len(dd) < 40:
            continue
        # gom liên tiếp bắt đầu từ mỗi phiên trong 40 phiên đầu → phân bố số phiên cần
        idx = list(dd.index)
        for s0 in range(0, len(idx) - 30):
            adv0 = dd.iloc[s0]["adv20"]
            px0 = dd.iloc[s0]["close"]
            target = target_pct_adv * adv0 / px0
            got, k = 0.0, 0
            for j in range(s0, min(s0 + 30, len(idx))):
                k += 1
                cap = 0.10 * dd.iloc[j]["adv20"] / dd.iloc[j]["close"]
                got += min(cap, kappa * dd.iloc[j]["vol"])
                if got >= target:
                    break
            out.append({"ticker": tk, "sessions_needed": k if got >= target else np.nan})
    d = pd.DataFrame(out)
    ok = d.sessions_needed.dropna()
    print(f"\n=== SỐ PHIÊN CẦN ĐỂ GOM {target_pct_adv*100:.0f}% ADV "
          f"(trần 10%ADV/phiên, κ={kappa}; N={len(d)} lần thử) ===")
    print(f"  hoàn tất trong ≤30 phiên: {100*len(ok)/len(d):.1f}%")
    print(f"  trung vị {ok.median():.0f} phiên · p75 {ok.quantile(.75):.0f} · "
          f"p90 {ok.quantile(.90):.0f} · max {ok.max():.0f}")
    return d


def tv1_ceiling_case():
    """Ca thật: trần 20.000đ của chương trình TV1 (duyệt 2026-07-23)."""
    p = os.path.join(BARS, "TV1.csv")
    df = sessions(p)
    ds = sorted(df.date.unique())[-40:]
    rows = []
    for d in ds:
        b = df[df.date == d]
        if b.empty:
            continue
        v_le = float(sum(
            (r.volume if r.high <= 20000 else
             (0 if r.low > 20000 else r.volume * (20000 - r.low) / (r.high - r.low)))
            for r in b.itertuples()))
        rows.append({"date": d, "vol": int(b.volume.sum()), "lo": b.low.min(),
                     "hi": b.high.max(), "close": b.close.iloc[-1],
                     "vol_le_20000": int(v_le)})
    t = pd.DataFrame(rows)
    t.to_csv(os.path.join(OUTD, "tv1_ceiling_case.csv"), index=False)
    n0 = (t.vol_le_20000 < LOT).sum()
    print(f"\n=== TV1 vs TRẦN 20.000đ — {len(t)} phiên gần nhất ===")
    print(f"  Số phiên KHÔNG có nổi 1 lô khớp ở giá ≤20.000đ: {n0}/{len(t)} "
          f"({100*n0/len(t):.0f}%)")
    print(f"  KL trung vị khớp ở ≤20.000đ mỗi phiên: {t.vol_le_20000.median():.0f}cp "
          f"(tổng KL trung vị {t.vol.median():.0f}cp)")
    print("  10 phiên gần nhất:")
    print(t.tail(10).to_string(index=False))
    return t


if __name__ == "__main__":
    profile()
    for tp in (0.10, 0.30, 0.60):
        multi_session(target_pct_adv=tp)
    tv1_ceiling_case()
