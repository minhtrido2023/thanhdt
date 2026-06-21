"""Deep intraday analysis of FPT on 2026-05-08 (5m bars)."""
import datetime as dt

import numpy as np
import pandas as pd

from stockquery_agent import StockQuery

TARGET_DATE = dt.date(2026, 5, 8)


def rsi_wilder(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    up = delta.clip(lower=0)
    dn = (-delta).clip(lower=0)
    ru = up.ewm(alpha=1 / period, adjust=False).mean()
    rd = dn.ewm(alpha=1 / period, adjust=False).mean()
    rs = ru / rd.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def macd(close, fast=12, slow=26, sig=9):
    f = close.ewm(span=fast, adjust=False).mean()
    s = close.ewm(span=slow, adjust=False).mean()
    line = f - s
    signal = line.ewm(span=sig, adjust=False).mean()
    return line, signal, line - signal


def cmf(df, period=14):
    hl = (df["high"] - df["low"])
    mfm = np.where(hl > 0, ((df["close"] - df["low"]) - (df["high"] - df["close"])) / hl, 0.0)
    mfv = pd.Series(mfm, index=df.index) * df["volume"]
    return mfv.rolling(period).sum() / df["volume"].rolling(period).sum().replace(0, np.nan)


def main():
    print("=" * 76)
    print("  FPT intraday — 2026-05-08 (5m bars)")
    print("=" * 76)

    sq = StockQuery(start_date="2026-04-15")
    df = sq.get_historical_symbol("FPT", interval="5m")
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)

    # context: include preceding sessions so RSI/MACD warm up
    pre_cutoff = pd.Timestamp(TARGET_DATE) - dt.timedelta(days=10)
    df = df[df["time"] >= pre_cutoff].reset_index(drop=True)

    df["MA20"] = df["close"].rolling(20).mean()
    df["RSI14"] = rsi_wilder(df["close"], 14)
    line, sig, hist = macd(df["close"])
    df["MACD"], df["MACDsig"], df["MACDhist"] = line, sig, hist
    df["CMF14"] = cmf(df, 14)
    df["VolMA20"] = df["volume"].rolling(20).mean()
    df["VolSpike"] = df["volume"] / df["VolMA20"]

    day = df[df["time"].dt.date == TARGET_DATE].copy().reset_index(drop=True)
    if day.empty:
        print(f"No 5m bars found for {TARGET_DATE}")
        return

    # Session VWAP (within the day)
    tp = (day["high"] + day["low"] + day["close"]) / 3.0
    cum_pv = (tp * day["volume"]).cumsum()
    cum_v = day["volume"].cumsum().replace(0, np.nan)
    day["VWAP"] = cum_pv / cum_v

    print(f"Bars: {len(day)} | {day['time'].min().time()} → {day['time'].max().time()}")
    open_p = day["open"].iloc[0]
    high_p = day["high"].max()
    low_p = day["low"].min()
    close_p = day["close"].iloc[-1]
    vol_total = day["volume"].sum()
    chg = (close_p / open_p - 1) * 100
    print(f"O={open_p:.2f}  H={high_p:.2f}  L={low_p:.2f}  C={close_p:.2f}  ({chg:+.2f}%)")
    print(f"Volume tổng: {vol_total:,.0f}  |  range biên độ: {(high_p-low_p):.2f} đ ({(high_p-low_p)/open_p*100:.2f}%)")

    # ── Bar-by-bar table ──────────────────────────────────────────────────
    print("\n--- Bảng diễn biến 5m bar ---")
    show = day[["time", "open", "high", "low", "close", "volume",
                "VWAP", "RSI14", "MACDhist", "VolSpike"]].copy()
    show["ret%"] = day["close"].pct_change() * 100
    show["vsVWAP"] = day["close"] - day["VWAP"]
    show["time"] = show["time"].dt.strftime("%H:%M")
    print(show.to_string(index=False, float_format=lambda x: f"{x:.2f}"))

    # ── Key moments ───────────────────────────────────────────────────────
    print("\n--- Key moments ---")
    idx_high = day["high"].idxmax()
    idx_low = day["low"].idxmin()
    print(f"  Đỉnh ngày  : {day.loc[idx_high, 'time'].strftime('%H:%M')}  high={day.loc[idx_high,'high']:.2f}  vol={day.loc[idx_high,'volume']:,}")
    print(f"  Đáy  ngày  : {day.loc[idx_low,  'time'].strftime('%H:%M')}  low ={day.loc[idx_low, 'low']:.2f}  vol={day.loc[idx_low, 'volume']:,}")

    bursts = day[day["VolSpike"] >= 2.0]
    if len(bursts):
        print(f"\n  Volume burst (≥2× MA20) — {len(bursts)} bar:")
        for _, r in bursts.iterrows():
            direction = "↑" if r["close"] >= r["open"] else "↓"
            print(f"    {r['time'].strftime('%H:%M')} {direction}  C={r['close']:.2f}  vol={r['volume']:,.0f}  ({r['VolSpike']:.2f}× MA20)")

    rsi_min_idx = day["RSI14"].idxmin()
    rsi_max_idx = day["RSI14"].idxmax()
    print(f"\n  RSI thấp nhất: {day.loc[rsi_min_idx,'RSI14']:.1f} @ {day.loc[rsi_min_idx,'time'].strftime('%H:%M')}  (close {day.loc[rsi_min_idx,'close']:.2f})")
    print(f"  RSI cao nhất : {day.loc[rsi_max_idx,'RSI14']:.1f} @ {day.loc[rsi_max_idx,'time'].strftime('%H:%M')}  (close {day.loc[rsi_max_idx,'close']:.2f})")

    # MACD hist crosses
    cross_up = day[(day["MACDhist"] > 0) & (day["MACDhist"].shift(1) <= 0)]
    cross_dn = day[(day["MACDhist"] < 0) & (day["MACDhist"].shift(1) >= 0)]
    print(f"\n  MACD hist cross up: {len(cross_up)} lần " + (", ".join(t.strftime('%H:%M') for t in cross_up['time']) if len(cross_up) else "—"))
    print(f"  MACD hist cross dn: {len(cross_dn)} lần " + (", ".join(t.strftime('%H:%M') for t in cross_dn['time']) if len(cross_dn) else "—"))

    # ── VWAP & price action ───────────────────────────────────────────────
    above_vwap = (day["close"] > day["VWAP"]).sum()
    print(f"\n--- VWAP & flow ---")
    print(f"  VWAP cuối ngày     : {day['VWAP'].iloc[-1]:.2f}")
    print(f"  Bar trên VWAP      : {above_vwap}/{len(day)} ({above_vwap/len(day)*100:.0f}%)")
    print(f"  Close vs VWAP cuối : {(close_p - day['VWAP'].iloc[-1]):+.2f}")

    # ── Volume @ price ────────────────────────────────────────────────────
    print("\n--- Volume profile (theo mức giá close, làm tròn 0.1) ---")
    vp = day.groupby((day["close"] * 10).round() / 10)["volume"].sum().sort_index()
    vp_pct = vp / vp.sum() * 100
    poc = vp.idxmax()
    print(f"  POC (point of control): {poc:.2f}  ({vp_pct.max():.1f}% volume)")
    for price, v in vp.items():
        bar = "█" * int(vp_pct[price] / 2)
        print(f"   {price:.2f}  {v:>10,.0f}  {vp_pct[price]:5.1f}%  {bar}")

    # ── 4 phases ──────────────────────────────────────────────────────────
    print("\n--- 4 giai đoạn trong phiên ---")
    phases = [
        ("Mở cửa  09:15-10:00",  dt.time(9, 15),  dt.time(10, 0)),
        ("Sáng    10:00-11:30", dt.time(10, 0),  dt.time(11, 30)),
        ("Đầu chiều 13:00-14:00", dt.time(13, 0), dt.time(14, 0)),
        ("ATC/cuối 14:00-14:45", dt.time(14, 0),  dt.time(14, 45)),
    ]
    for name, t0, t1 in phases:
        seg = day[(day["time"].dt.time >= t0) & (day["time"].dt.time <= t1)]
        if seg.empty:
            continue
        s_open = seg["open"].iloc[0]
        s_close = seg["close"].iloc[-1]
        s_vol = seg["volume"].sum()
        s_chg = (s_close / s_open - 1) * 100
        print(f"  {name}: O={s_open:.2f} C={s_close:.2f} ({s_chg:+.2f}%) vol={s_vol:,.0f}")


if __name__ == "__main__":
    main()
