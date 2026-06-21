"""Layer 3 — Intraday entry timing for Holistic watchlist tickers.

Workflow:
  1. Load latest holistic watchlist (top picks from recommend_holistic.py)
  2. For each ticker, fetch 15m intraday bars via vnstock API
  3. Compute intraday signals: session VWAP, 15m RSI, MACD, volume profile,
     volume burst direction, microstructure
  4. Output GO/WAIT/AVOID per ticker with reasoning
  5. Recommend specific entry price/zone

Use after holistic engine runs (post-14:50 close, plan T+1 entry).
"""
import os
import sys
from datetime import datetime, time as dtime, timedelta

import numpy as np
import pandas as pd

sys.path.insert(0, r"/home/trido/thanhdt/WorkingClaude/stockquery")
from stockquery_agent import StockQuery

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"


def rsi_wilder(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    up = delta.clip(lower=0)
    dn = (-delta).clip(lower=0)
    ru = up.ewm(alpha=1/period, adjust=False).mean()
    rd = dn.ewm(alpha=1/period, adjust=False).mean()
    rs = ru / rd.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def session_vwap(df: pd.DataFrame) -> pd.Series:
    tp = (df["high"] + df["low"] + df["close"]) / 3.0
    pv = tp * df["volume"]
    g = df["time"].dt.date
    return pv.groupby(g).cumsum() / df["volume"].groupby(g).cumsum().replace(0, np.nan)


def analyze_ticker_intraday(sq: StockQuery, ticker: str, target_date: str = None):
    """Analyze 15m intraday for ticker, return GO/WAIT/AVOID signal."""
    try:
        # Fetch ~10 days of 15m for context (for MA/RSI warm-up)
        from datetime import date, timedelta
        if target_date:
            end = pd.Timestamp(target_date)
        else:
            end = pd.Timestamp.today()
        start = (end - pd.Timedelta(days=15)).strftime("%Y-%m-%d")
        sq.start_date = start
        sq.end_date = end.strftime("%Y-%m-%d")
        df = sq.get_historical_symbol(ticker, interval="15m")
    except Exception as e:
        return {"ticker": ticker, "verdict": "ERROR", "reason": str(e)[:80]}

    if df is None or len(df) < 20:
        return {"ticker": ticker, "verdict": "NO_DATA", "reason": "insufficient bars"}

    df = df.copy()
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)

    # Filter to today's session if possible
    if target_date:
        target_d = pd.Timestamp(target_date).date()
    else:
        target_d = df["time"].dt.date.max()
    today_df = df[df["time"].dt.date == target_d].copy()
    full_df = df.copy()

    if len(today_df) < 3:
        # Try last available session
        last_d = full_df["time"].dt.date.max()
        today_df = full_df[full_df["time"].dt.date == last_d].copy()
        target_d = last_d

    if len(today_df) < 3:
        return {"ticker": ticker, "verdict": "NO_DATA", "reason": "no session bars"}

    # Indicators on full series
    full_df["RSI14"] = rsi_wilder(full_df["close"], 14)
    full_df["EMA12"] = full_df["close"].ewm(span=12, adjust=False).mean()
    full_df["EMA26"] = full_df["close"].ewm(span=26, adjust=False).mean()
    full_df["MACD"] = full_df["EMA12"] - full_df["EMA26"]
    full_df["MACDsig"] = full_df["MACD"].ewm(span=9, adjust=False).mean()
    full_df["MACDhist"] = full_df["MACD"] - full_df["MACDsig"]
    full_df["VolMA20"] = full_df["volume"].rolling(20).mean()

    today_idx = full_df[full_df["time"].dt.date == target_d].index
    today_df = full_df.loc[today_idx].copy()
    today_df["VWAP"] = session_vwap(today_df)

    # Compute signal features
    last = today_df.iloc[-1]
    n_bars = len(today_df)
    bars_above_vwap = (today_df["close"] > today_df["VWAP"]).sum()
    pct_above_vwap = bars_above_vwap / n_bars * 100

    # Last 4-bar trend (1 hour)
    last_4 = today_df.tail(4)
    trend_1h = (last_4["close"].iloc[-1] / last_4["close"].iloc[0] - 1) * 100 if len(last_4) >= 2 else 0

    # Volume burst in last hour
    last_hour_vol = today_df.tail(4)["volume"].sum() if n_bars >= 4 else today_df["volume"].sum()
    avg_vol_per_4bars = full_df["VolMA20"].iloc[-1] * 4 if not pd.isna(full_df["VolMA20"].iloc[-1]) else 1
    vol_burst_ratio = last_hour_vol / avg_vol_per_4bars if avg_vol_per_4bars > 0 else 1

    # Last bar specifics
    last_bar_green = last["close"] >= last["open"]
    last_close_vs_vwap = (last["close"] - last["VWAP"]) / last["VWAP"] * 100 if not pd.isna(last["VWAP"]) else 0

    # Day OHLC
    day_open = today_df["open"].iloc[0]
    day_high = today_df["high"].max()
    day_low = today_df["low"].min()
    day_close_now = last["close"]
    day_chg_pct = (day_close_now / day_open - 1) * 100
    pos_in_range = (day_close_now - day_low) / max(day_high - day_low, 0.01) * 100  # 0=low, 100=high

    # Score
    score = 0
    reasons = []

    # +30 above VWAP majority of session
    if pct_above_vwap >= 60:
        score += 30
        reasons.append(f"VWAP+ ({pct_above_vwap:.0f}% bars)")
    elif pct_above_vwap >= 40:
        score += 10
        reasons.append(f"VWAP mixed ({pct_above_vwap:.0f}% bars)")
    else:
        reasons.append(f"VWAP- ({pct_above_vwap:.0f}% below)")

    # +20 last bar green + above VWAP
    if last_bar_green and last_close_vs_vwap > 0:
        score += 20
        reasons.append("last bar green & >VWAP")
    elif not last_bar_green and last_close_vs_vwap < 0:
        score -= 10
        reasons.append("last bar red & <VWAP")

    # +15 trend up in last hour
    if trend_1h > 0.5:
        score += 15
        reasons.append(f"+{trend_1h:.1f}% last hour")
    elif trend_1h < -0.5:
        score -= 10
        reasons.append(f"{trend_1h:.1f}% last hour")

    # +15 RSI > 50, momentum
    rsi_now = last["RSI14"]
    if rsi_now is not None and not pd.isna(rsi_now):
        if 50 < rsi_now < 75:
            score += 15
            reasons.append(f"RSI {rsi_now:.0f} healthy")
        elif rsi_now >= 75:
            reasons.append(f"RSI {rsi_now:.0f} overbought")
        elif rsi_now < 40:
            score -= 5
            reasons.append(f"RSI {rsi_now:.0f} weak")

    # +15 MACD histogram positive
    if last["MACDhist"] > 0:
        score += 15
        reasons.append("MACDh+")

    # +10 position in upper half of day range
    if pos_in_range >= 60:
        score += 10
        reasons.append(f"upper {pos_in_range:.0f}% range")
    elif pos_in_range < 30:
        score -= 10
        reasons.append(f"lower {pos_in_range:.0f}% range — weak")

    # -5 if late-day weakness (last 30 min red)
    last_30min = today_df.tail(2)
    if len(last_30min) >= 2:
        last_30min_chg = (last_30min["close"].iloc[-1] / last_30min["close"].iloc[0] - 1) * 100
        if last_30min_chg < -0.5:
            score -= 15
            reasons.append(f"late weakness {last_30min_chg:.1f}%")

    # Volume burst up
    if vol_burst_ratio >= 1.5 and trend_1h > 0:
        score += 10
        reasons.append(f"vol burst {vol_burst_ratio:.1f}x ↑")

    # Verdict
    if score >= 60:
        verdict = "GO_STRONG"
    elif score >= 40:
        verdict = "GO"
    elif score >= 20:
        verdict = "WAIT"
    else:
        verdict = "AVOID"

    return {
        "ticker": ticker,
        "session_date": str(target_d),
        "verdict": verdict,
        "score": score,
        "reason": ", ".join(reasons[:4]),
        "open": round(day_open, 2),
        "high": round(day_high, 2),
        "low": round(day_low, 2),
        "close": round(day_close_now, 2),
        "day_chg_pct": round(day_chg_pct, 2),
        "vwap": round(last["VWAP"], 2) if not pd.isna(last["VWAP"]) else None,
        "vs_vwap_pct": round(last_close_vs_vwap, 2),
        "rsi15m": round(rsi_now, 1) if not pd.isna(rsi_now) else None,
        "macd_hist": round(last["MACDhist"], 4),
        "pos_in_range": round(pos_in_range, 0),
        "trend_1h_pct": round(trend_1h, 2),
        "vol_burst_x": round(vol_burst_ratio, 2),
        "n_bars": n_bars,
    }


def main():
    if len(sys.argv) > 1 and sys.argv[1] not in ("--", "-"):
        # Read tickers from arg list (comma-separated)
        tickers = [t.strip().upper() for t in sys.argv[1].split(",") if t.strip()]
        target_date = sys.argv[2] if len(sys.argv) > 2 else None
    else:
        # Default: read top picks from latest holistic CSV
        import glob
        files = sorted(glob.glob(os.path.join(WORKDIR, "holistic_*.csv")))
        if not files:
            print("No holistic_*.csv found. Run recommend_holistic.py first.")
            print("Or pass tickers: python layer3_intraday_timing.py FPT,VNM,HPG")
            return
        latest = files[-1]
        df = pd.read_csv(latest)
        # Top 10 picks: high conviction tiers
        priority_tiers = ["MEGA", "S_PRO", "MOMENTUM", "MOMENTUM_QUALITY", "MOMENTUM_N",
                          "DEEP_VALUE_RECOVERY", "MOMENTUM_S"]
        df_picks = df[df["play_type"].isin(priority_tiers)].sort_values(
            ["conviction", "ta_score"], ascending=False).head(10)
        tickers = df_picks["ticker"].tolist()
        target_date = None
        print(f"Loaded {len(tickers)} picks from {os.path.basename(latest)}")

    print(f"\nAnalyzing intraday for {len(tickers)} tickers...")
    print("=" * 95)

    sq = StockQuery()
    results = []
    for tk in tickers:
        print(f"\n  {tk}...", end="", flush=True)
        try:
            r = analyze_ticker_intraday(sq, tk, target_date)
            results.append(r)
            print(f"  {r.get('verdict', 'ERR'):10}  score={r.get('score', 0):3d}  "
                  f"close={r.get('close', '?')}  vs_VWAP={r.get('vs_vwap_pct', 0):+.2f}%  "
                  f"RSI={r.get('rsi15m', '?')}")
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({"ticker": tk, "verdict": "ERROR", "reason": str(e)[:80]})

    # Save results
    df_out = pd.DataFrame(results)
    out_path = os.path.join(WORKDIR, "data/layer3_intraday_signals.csv")
    df_out.to_csv(out_path, index=False)

    # Summary by verdict
    print("\n" + "=" * 95)
    print("  SUMMARY")
    print("=" * 95)
    if "verdict" in df_out.columns:
        for v in ["GO_STRONG", "GO", "WAIT", "AVOID", "NO_DATA", "ERROR"]:
            sub = df_out[df_out["verdict"] == v]
            if len(sub):
                tickers_str = ", ".join(sub["ticker"])
                print(f"  {v:11} ({len(sub)}): {tickers_str}")

    # Print full table
    print("\n" + "=" * 95)
    print("  FULL DETAIL")
    print("=" * 95)
    cols = ["ticker", "verdict", "score", "close", "day_chg_pct", "vs_vwap_pct",
            "rsi15m", "pos_in_range", "trend_1h_pct", "vol_burst_x", "reason"]
    cols = [c for c in cols if c in df_out.columns]
    print(df_out[cols].to_string(index=False))

    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
