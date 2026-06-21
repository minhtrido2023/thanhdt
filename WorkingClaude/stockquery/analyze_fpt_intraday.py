"""Fetch FPT intraday (15m) for the past ~1 week and compute technical signals."""
import datetime as dt

import numpy as np
import pandas as pd

from stockquery_agent import StockQuery


def rsi_wilder(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    up = delta.clip(lower=0)
    dn = (-delta).clip(lower=0)
    roll_up = up.ewm(alpha=1 / period, adjust=False).mean()
    roll_dn = dn.ewm(alpha=1 / period, adjust=False).mean()
    rs = roll_up / roll_dn.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def macd(close: pd.Series, fast=12, slow=26, sig=9):
    ema_f = close.ewm(span=fast, adjust=False).mean()
    ema_s = close.ewm(span=slow, adjust=False).mean()
    line = ema_f - ema_s
    signal = line.ewm(span=sig, adjust=False).mean()
    hist = line - signal
    return line, signal, hist


def cmf(df: pd.DataFrame, period: int = 14) -> pd.Series:
    hl = (df["high"] - df["low"]).replace(0, np.nan)
    mfm = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / hl
    mfv = mfm * df["volume"]
    return mfv.rolling(period).sum() / df["volume"].rolling(period).sum()


def vwap(df: pd.DataFrame) -> pd.Series:
    tp = (df["high"] + df["low"] + df["close"]) / 3.0
    pv = (tp * df["volume"]).cumsum()
    vv = df["volume"].cumsum().replace(0, np.nan)
    return pv / vv


def session_vwap(df: pd.DataFrame) -> pd.Series:
    """VWAP reset per trading day."""
    tp = (df["high"] + df["low"] + df["close"]) / 3.0
    pv = tp * df["volume"]
    g = df["time"].dt.date
    return pv.groupby(g).cumsum() / df["volume"].groupby(g).cumsum().replace(0, np.nan)


def main():
    print("=" * 72)
    print("  FPT intraday signal scan — past ~1 week")
    print("=" * 72)

    today = dt.date.today()
    start = today - dt.timedelta(days=10)
    sq = StockQuery(start_date=start.strftime("%Y-%m-%d"))

    df = sq.get_historical_symbol("FPT", interval="15m")
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)

    cutoff = pd.Timestamp(today - dt.timedelta(days=7))
    df = df[df["time"] >= cutoff].reset_index(drop=True)

    if df.empty:
        print("No data returned for FPT in the requested window.")
        return

    print(f"\nRows: {len(df)} | from {df['time'].min()} to {df['time'].max()}")
    print(f"Distinct sessions: {df['time'].dt.date.nunique()}")

    # ── Indicators ────────────────────────────────────────────────────────
    df["MA20"] = df["close"].rolling(20).mean()
    df["MA50"] = df["close"].rolling(50).mean()
    df["RSI14"] = rsi_wilder(df["close"], 14)
    macd_line, macd_sig, macd_hist = macd(df["close"])
    df["MACD"] = macd_line
    df["MACDsig"] = macd_sig
    df["MACDhist"] = macd_hist
    df["CMF14"] = cmf(df, 14)
    df["VWAPses"] = session_vwap(df)
    df["RetPct"] = df["close"].pct_change() * 100
    df["VolMA20"] = df["volume"].rolling(20).mean()
    df["VolSpike"] = df["volume"] / df["VolMA20"]

    # ── Daily summary ─────────────────────────────────────────────────────
    print("\n--- Daily OHLCV summary (15m bars rolled up) ---")
    g = df.groupby(df["time"].dt.date)
    daily = pd.DataFrame({
        "open": g["open"].first(),
        "high": g["high"].max(),
        "low": g["low"].min(),
        "close": g["close"].last(),
        "volume": g["volume"].sum(),
        "bars": g.size(),
    })
    daily["chg_pct"] = daily["close"].pct_change() * 100
    print(daily.to_string(float_format=lambda x: f"{x:.2f}"))

    # ── Latest snapshot ────────────────────────────────────────────────────
    last = df.iloc[-1]
    print("\n--- Latest 15m bar ---")
    print(f"  time     : {last['time']}")
    print(f"  close    : {last['close']:.2f}  (ret_15m: {last['RetPct']:+.2f}%)")
    print(f"  MA20/MA50: {last['MA20']:.2f} / {last['MA50']:.2f}")
    print(f"  RSI14    : {last['RSI14']:.1f}")
    print(f"  MACDhist : {last['MACDhist']:+.3f}  (line {last['MACD']:+.3f}, sig {last['MACDsig']:+.3f})")
    print(f"  CMF14    : {last['CMF14']:+.3f}")
    print(f"  VWAPses  : {last['VWAPses']:.2f}  (close vs VWAP: {(last['close']-last['VWAPses']):+.2f})")
    print(f"  Vol      : {last['volume']:,.0f}  (vs MA20: {last['VolSpike']:.2f}x)")

    # ── Signal flags ──────────────────────────────────────────────────────
    print("\n--- Recent signal flags (last 20 bars) ---")
    sub = df.tail(20).copy()

    sub["RSI_OB"] = sub["RSI14"] >= 70
    sub["RSI_OS"] = sub["RSI14"] <= 30
    sub["MACD_X_up"] = (sub["MACDhist"] > 0) & (sub["MACDhist"].shift(1) <= 0)
    sub["MACD_X_dn"] = (sub["MACDhist"] < 0) & (sub["MACDhist"].shift(1) >= 0)
    sub["MA_X_up"] = (sub["close"] > sub["MA20"]) & (sub["close"].shift(1) <= sub["MA20"].shift(1))
    sub["MA_X_dn"] = (sub["close"] < sub["MA20"]) & (sub["close"].shift(1) >= sub["MA20"].shift(1))
    sub["VolBurst"] = sub["VolSpike"] >= 2.0

    flags = sub[["time", "close", "RSI14", "MACDhist", "CMF14", "VolSpike",
                 "RSI_OB", "RSI_OS", "MACD_X_up", "MACD_X_dn",
                 "MA_X_up", "MA_X_dn", "VolBurst"]]
    print(flags.to_string(index=False, float_format=lambda x: f"{x:.2f}"))

    # ── Aggregate event count over the week ───────────────────────────────
    print("\n--- Event counts over the window ---")
    events = {
        "RSI overbought (>=70)": int((df["RSI14"] >= 70).sum()),
        "RSI oversold (<=30)":   int((df["RSI14"] <= 30).sum()),
        "MACD hist cross up":    int(((df["MACDhist"] > 0) & (df["MACDhist"].shift(1) <= 0)).sum()),
        "MACD hist cross dn":    int(((df["MACDhist"] < 0) & (df["MACDhist"].shift(1) >= 0)).sum()),
        "Close above VWAPses":   int((df["close"] > df["VWAPses"]).sum()),
        "Close below VWAPses":   int((df["close"] < df["VWAPses"]).sum()),
        "Volume burst >=2x MA20":int((df["VolSpike"] >= 2.0).sum()),
        "CMF positive (>0)":     int((df["CMF14"] > 0).sum()),
        "CMF negative (<0)":     int((df["CMF14"] < 0).sum()),
    }
    for k, v in events.items():
        print(f"  {k:30} {v}")

    # ── Read of the week ──────────────────────────────────────────────────
    print("\n--- Read of the week ---")
    first_close = daily["close"].iloc[0]
    last_close = daily["close"].iloc[-1]
    week_ret = (last_close / first_close - 1) * 100
    avg_vol = daily["volume"].mean()
    rsi_mean = df["RSI14"].mean()
    cmf_mean = df["CMF14"].mean()
    vwap_share = (df["close"] > df["VWAPses"]).mean() * 100
    macd_pos = (df["MACDhist"] > 0).mean() * 100
    print(f"  Week return         : {week_ret:+.2f}%")
    print(f"  Avg daily volume    : {avg_vol:,.0f}")
    print(f"  Avg RSI(14)         : {rsi_mean:.1f}")
    print(f"  Avg CMF(14)         : {cmf_mean:+.3f}")
    print(f"  Bars above VWAPses  : {vwap_share:.1f}%")
    print(f"  Bars MACDhist > 0   : {macd_pos:.1f}%")


if __name__ == "__main__":
    main()
