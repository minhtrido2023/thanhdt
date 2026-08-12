"""P2 — thay "30% × KL ĐÃ khớp" bằng "30% × KL KỲ VỌNG tới giờ này", có clamp đuôi.

R&D only (§8). KHÔNG sửa production.

BỆNH đang chữa (đọc từ executor.py:583-596): `ceil_allow = 0.30 × cum_vol − filled`
lấy KL ĐÃ khớp trong ngày làm mẫu số. Đầu phiên cum_vol≈0 ⇒ allowance≈0 ⇒ ta chỉ được
hiện vài lô. Nhưng KL đã khớp là KL xảy ra KHÔNG CÓ TA — cơ chế bắt ta luôn đi sau tape.
Trên mã mỏng, người bán duy nhất của phiên xuất hiện lúc 09:40 chỉ nhìn thấy 100cp của ta.

P2: mẫu số = max(KL đã khớp, KL KỲ VỌNG tới giờ này) với
    KL kỳ vọng = ADV20_cp × f(t),  f(t) = tỷ trọng KL luỹ kế trung vị tới phút t
                                          (đo trên chính rổ mã mỏng, 120 phiên).
BẢO VỆ ĐUÔI vẫn giữ: fill luỹ kế KHÔNG BAO GIỜ vượt `TAIL_CLAMP × KL thật đã khớp`.
Đó mới là bất biến "không thành đa số một phiên mỏng" — nó phải neo vào tape THẬT,
còn allowance HIỂN THỊ thì không cần (hiện lệnh không tiêu thụ tape của ai).
"""
import os
import glob
import numpy as np
import pandas as pd
import exp_ceiling_tolerance as T

OUTD = T.OUTD
LOT = T.LOT
TAIL_CLAMP = float(os.environ.get("TAIL_CLAMP", "0.50"))


def build_profile():
    """f(t): tỷ trọng KL luỹ kế trung vị tới từng phút, gộp rổ mã mỏng, 120 phiên."""
    acc = {}
    for p in sorted(glob.glob(os.path.join(T.BARS, "*.csv"))):
        df = T.load(p)
        ds = sorted(df.date.unique())[-120:]
        df = df[df.date.isin(ds)]
        for d, b in df.groupby("date"):
            tot = b.volume.sum()
            if tot <= 0:
                continue
            b = b.sort_values("minute")
            cum = b.volume.cumsum() / tot
            for m, c in zip(b.minute, cum):
                acc.setdefault(int(m), []).append(float(c))
    mins = sorted(acc)
    prof = pd.Series({m: float(np.median(acc[m])) for m in mins}).sort_index()
    # ép đơn điệu không giảm (trung vị theo phút có thể lồi lõm nhẹ)
    prof = prof.cummax()
    prof.to_csv(os.path.join(OUTD, "cum_volume_profile.csv"))
    return prof


def frac_at(prof, m):
    idx = prof.index[prof.index <= m]
    return float(prof.loc[idx[-1]]) if len(idx) else 0.0


def run_session(bars, target, ceiling, adv20, kappa, mode, prof):
    """mode: 'current' | 'adv_only' | 'expected_floor'"""
    filled, cum_vol, cost = 0, 0, 0.0
    shown, last = 0, -999
    adv_shares = adv20 / ceiling if ceiling else 0
    for r in bars.sort_values("minute").itertuples():
        avail, px_avg = T.vol_le(r.low, r.high, r.volume, ceiling)
        if r.minute - last >= T.SLICE_INTERVAL_MIN:
            rem = target - filled
            q = min(rem, int(T.MAX_CHILD_VALUE / ceiling))
            floor_allow = int(T.MAX_PARTICIPATION * adv_shares) - filled
            if mode == "current":
                allow = min(floor_allow, int(T.REALIZED_CEIL * cum_vol) - filled)
            elif mode == "expected_floor":
                expected = adv_shares * frac_at(prof, r.minute)
                allow = min(floor_allow,
                            int(T.REALIZED_CEIL * max(cum_vol, expected)) - filled)
            else:
                allow = floor_allow
            q = 0 if allow < LOT else min(q, allow)
            shown = (q // LOT) * LOT
            last = r.minute
        got = min(shown, int(kappa * avail))
        if mode == "expected_floor":          # clamp đuôi trên TAPE THẬT
            headroom = int(TAIL_CLAMP * (cum_vol + avail)) - filled
            got = max(0, min(got, headroom))
        if got > 0:
            filled += got
            cost += got * px_avg
            shown -= got
        cum_vol += r.volume
    return filled, cost, (filled / cum_vol if cum_vol else 0.0)


def main():
    kappa = float(os.environ.get("KAPPA", "0.34"))
    tgt = float(os.environ.get("TARGET_PCT_ADV", "0.10"))
    tau = float(os.environ.get("TAU", "0.03"))
    lag = int(os.environ.get("ANCHOR_LAG", "5"))
    prof = build_profile()
    print(f"profile f(t): 09:15={frac_at(prof,555):.1%} 10:00={frac_at(prof,600):.1%} "
          f"11:00={frac_at(prof,660):.1%} 13:30={frac_at(prof,810):.1%} "
          f"14:30={frac_at(prof,870):.1%}")
    rows = []
    for p in sorted(glob.glob(os.path.join(T.BARS, "*.csv"))):
        tk = os.path.basename(p)[:-4]
        df = T.load(p)
        dd = df.groupby("date").agg(vol=("volume", "sum"), close=("close", "last"))
        dd["turn"] = dd.vol * dd.close
        dd["adv20"] = dd.turn.rolling(20, min_periods=10).mean().shift(1)
        dd = dd.dropna()
        idx = list(dd.index)
        for pos in range(max(lag, len(idx) - 80), len(idx)):
            d = idx[pos]
            adv20 = float(dd.iloc[pos]["adv20"])
            b = df[df.date == d]
            if b.empty or adv20 <= 0:
                continue
            anchor = float(dd.iloc[pos - lag]["close"])
            ceil = anchor * (1 + tau)
            target = int((tgt * adv20 / anchor) // LOT * LOT)
            if target < LOT:
                continue
            row = {"ticker": tk, "date": d, "target": target, "anchor": anchor}
            for mode in ("current", "expected_floor", "adv_only"):
                f, c, sh = run_session(b, target, ceil, adv20, kappa, mode, prof)
                row[f"{mode}_fill"] = f
                row[f"{mode}_cost"] = c
                row[f"{mode}_share"] = sh
            rows.append(row)
    d = pd.DataFrame(rows)
    d.to_csv(os.path.join(OUTD, f"expected_floor_k{kappa}_tau{tau}.csv"), index=False)
    print(f"\n=== P2 vs hiện tại (κ={kappa}, lệnh {tgt*100:.0f}%ADV, τ={tau*100:.0f}%, "
          f"anchor cũ {lag} phiên, clamp đuôi {TAIL_CLAMP:.0%}) N={len(d)} ===")
    print(f"{'cơ chế':>16}{'fill TB':>10}{'%fill=0':>10}{'giá/anchor':>12}"
          f"{'%tape TB':>10}{'p95':>8}{'%phiên>50%tape':>16}")
    for m, lab in (("current", "hiện tại"), ("expected_floor", "P2 kỳ vọng"),
                   ("adv_only", "bỏ hẳn trần")):
        fr = (d[f"{m}_fill"] / d.target).clip(0, 1)
        slip = np.where(d[f"{m}_fill"] > 0,
                        d[f"{m}_cost"] / d[f"{m}_fill"].replace(0, np.nan) / d.anchor - 1,
                        np.nan)
        sh = d[f"{m}_share"]
        print(f"{lab:>16}{fr.mean():>10.3f}{100*(d[f'{m}_fill']<LOT).mean():>9.1f}%"
              f"{100*np.nanmean(slip):>11.2f}%{100*sh.mean():>9.1f}%"
              f"{100*sh.quantile(.95):>7.1f}%{100*(sh > 0.50).mean():>15.1f}%")
    return d


if __name__ == "__main__":
    main()
