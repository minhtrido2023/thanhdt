"""Layer 3 intraday backtest:
- Track A: 18 actual BA-system BUY events with intraday available (validate verdict)
- Track B: 30 most-liquid tickers x ~184 sessions (factor-IC mining)

For each (ticker, session_date):
  compute Layer 3 features at session close
  match with forward returns from BigQuery daily data

Output: layer3_backtest_eventsA.csv, layer3_backtest_eventsB.csv
"""
import os, sys, subprocess, json
from datetime import datetime
import numpy as np
import pandas as pd

sys.path.insert(0, r"/home/trido/thanhdt/WorkingClaude/stockquery")
from stockquery_agent import StockQuery

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

TOP30 = ["VIC","VHM","HPG","SHB","SSI","FPT","VIX","STB","MWG","MSN",
         "VCB","BSR","MBB","VPB","TCB","HDB","HCM","CTG","NVL","BID",
         "CII","PVS","VNM","GEX","VCI","SHS","DXG","VRE","VJC","DCM"]

# ---- indicators (same as layer3_intraday_timing.py) ----
def rsi_wilder(close, period=14):
    delta = close.diff()
    up = delta.clip(lower=0); dn = (-delta).clip(lower=0)
    ru = up.ewm(alpha=1/period, adjust=False).mean()
    rd = dn.ewm(alpha=1/period, adjust=False).mean()
    rs = ru / rd.replace(0, np.nan)
    return 100 - (100/(1+rs))

def session_vwap(df):
    tp = (df["high"]+df["low"]+df["close"])/3.0
    pv = tp * df["volume"]
    g = df["time"].dt.date
    return pv.groupby(g).cumsum() / df["volume"].groupby(g).cumsum().replace(0, np.nan)

def compute_features_for_session(full_df, session_date):
    """Given full 15m DataFrame and a session_date, return feature dict for that session."""
    full_df = full_df.copy()
    full_df["time"] = pd.to_datetime(full_df["time"])
    full_df = full_df.sort_values("time").reset_index(drop=True)
    full_df["RSI14"] = rsi_wilder(full_df["close"], 14)
    full_df["EMA12"] = full_df["close"].ewm(span=12, adjust=False).mean()
    full_df["EMA26"] = full_df["close"].ewm(span=26, adjust=False).mean()
    full_df["MACD"]  = full_df["EMA12"] - full_df["EMA26"]
    full_df["MACDsig"] = full_df["MACD"].ewm(span=9, adjust=False).mean()
    full_df["MACDh"] = full_df["MACD"] - full_df["MACDsig"]
    full_df["VolMA20"] = full_df["volume"].rolling(20).mean()

    today_idx = full_df[full_df["time"].dt.date == session_date].index
    if len(today_idx) < 3:
        return None
    today_df = full_df.loc[today_idx].copy()
    today_df["VWAP"] = session_vwap(today_df)
    last = today_df.iloc[-1]
    n_bars = len(today_df)

    pct_above_vwap = (today_df["close"] > today_df["VWAP"]).sum() / n_bars * 100
    last_4 = today_df.tail(4)
    trend_1h = (last_4["close"].iloc[-1]/last_4["close"].iloc[0] - 1)*100 if len(last_4)>=2 else 0
    last_hour_vol = today_df.tail(4)["volume"].sum() if n_bars>=4 else today_df["volume"].sum()
    avg_vol_4 = full_df["VolMA20"].iloc[-1]*4 if not pd.isna(full_df["VolMA20"].iloc[-1]) else 1
    vol_burst = last_hour_vol/avg_vol_4 if avg_vol_4>0 else 1
    last_bar_green = int(last["close"] >= last["open"])
    last_vs_vwap = (last["close"]-last["VWAP"])/last["VWAP"]*100 if not pd.isna(last["VWAP"]) else 0
    day_open = today_df["open"].iloc[0]
    day_high = today_df["high"].max(); day_low = today_df["low"].min()
    day_close = last["close"]
    day_chg = (day_close/day_open - 1)*100
    pos_in_range = (day_close-day_low)/max(day_high-day_low,0.01)*100
    last_30 = today_df.tail(2)
    late_chg = (last_30["close"].iloc[-1]/last_30["close"].iloc[0]-1)*100 if len(last_30)>=2 else 0
    rsi_now = last["RSI14"]
    macdh_now = last["MACDh"]

    # Layer 3 score (replicate)
    score = 0
    if pct_above_vwap >= 60: score += 30
    elif pct_above_vwap >= 40: score += 10
    if last_bar_green and last_vs_vwap>0: score += 20
    elif (not last_bar_green) and last_vs_vwap<0: score -= 10
    if trend_1h > 0.5: score += 15
    elif trend_1h < -0.5: score -= 10
    if rsi_now is not None and not pd.isna(rsi_now):
        if 50 < rsi_now < 75: score += 15
        elif rsi_now < 40: score -= 5
    if macdh_now > 0: score += 15
    if pos_in_range >= 60: score += 10
    elif pos_in_range < 30: score -= 10
    if len(last_30)>=2 and late_chg < -0.5: score -= 15
    if vol_burst >= 1.5 and trend_1h > 0: score += 10

    if score >= 60: verdict = "GO_STRONG"
    elif score >= 40: verdict = "GO"
    elif score >= 20: verdict = "WAIT"
    else: verdict = "AVOID"

    return dict(
        session_date=str(session_date),
        n_bars=n_bars,
        verdict=verdict, score=score,
        pct_above_vwap=round(pct_above_vwap,2),
        trend_1h=round(trend_1h,3),
        vol_burst=round(vol_burst,3),
        last_bar_green=last_bar_green,
        last_vs_vwap=round(last_vs_vwap,3),
        day_chg=round(day_chg,3),
        pos_in_range=round(pos_in_range,2),
        late_chg=round(late_chg,3),
        rsi15m=round(rsi_now,2) if not pd.isna(rsi_now) else None,
        macdh=round(macdh_now,5) if not pd.isna(macdh_now) else None,
        day_close=round(day_close,3),
    )

# ---- main ----
def fetch_intraday_bulk(tickers, start="2025-08-12", end="2026-05-12"):
    """Fetch 15m bars per ticker. Returns dict ticker -> DataFrame."""
    sq = StockQuery()
    out = {}
    for i, tk in enumerate(tickers):
        try:
            sq.start_date = start; sq.end_date = end
            df = sq.get_historical_symbol(tk, interval="15m")
            if df is not None and len(df) > 50:
                out[tk] = df
                print(f"  [{i+1}/{len(tickers)}] {tk}: {len(df)} bars, {df['time'].dt.date.nunique() if pd.api.types.is_datetime64_any_dtype(df['time']) else 'NA'} sessions")
            else:
                print(f"  [{i+1}/{len(tickers)}] {tk}: NO DATA")
        except Exception as e:
            print(f"  [{i+1}/{len(tickers)}] {tk}: ERROR {str(e)[:80]}")
    return out

def build_track_a(intraday_data):
    """For each BUY event in journal, compute features on the event date's session."""
    j = pd.read_csv(os.path.join(WORKDIR, "journal_v6_extended_events.csv"))
    j = j[j["action"]=="BUY"].copy()
    j["date"] = pd.to_datetime(j["date"])
    j = j[j["date"]>=pd.Timestamp("2025-08-12")].copy()
    rows = []
    for _, r in j.iterrows():
        tk = r["ticker"]; d = r["date"].date()
        if tk not in intraday_data:
            continue
        df = intraday_data[tk]
        feats = compute_features_for_session(df, d)
        if feats is None:
            continue
        feats["ticker"] = tk
        feats["entry_price"] = r["price"]
        feats["play_type"] = r["play_type"]
        rows.append(feats)
    return pd.DataFrame(rows)

def build_track_b(intraday_data):
    """For each (top30 ticker, every session) compute features."""
    rows = []
    for tk, df in intraday_data.items():
        df["time"] = pd.to_datetime(df["time"])
        sessions = sorted(df["time"].dt.date.unique())
        for d in sessions:
            feats = compute_features_for_session(df, d)
            if feats is None:
                continue
            feats["ticker"] = tk
            rows.append(feats)
    return pd.DataFrame(rows)

def main():
    # tickers we need: top30 + unique BUY tickers
    j = pd.read_csv(os.path.join(WORKDIR, "journal_v6_extended_events.csv"))
    j = j[j["action"]=="BUY"]; j["date"]=pd.to_datetime(j["date"])
    buy_tickers = j[j["date"]>=pd.Timestamp("2025-08-12")]["ticker"].unique().tolist()
    all_tickers = sorted(set(TOP30) | set(buy_tickers))
    print(f"Fetching 15m intraday for {len(all_tickers)} tickers (Aug 2025 - May 2026)...")
    intraday = fetch_intraday_bulk(all_tickers)
    print(f"\nGot data for {len(intraday)} tickers\n")

    # Track A
    print("Building Track A (actual BA-system BUYs)...")
    a = build_track_a(intraday)
    a.to_csv(os.path.join(WORKDIR, "layer3_backtest_eventsA.csv"), index=False)
    print(f"  Track A: {len(a)} events  -> layer3_backtest_eventsA.csv")
    if len(a):
        print(f"  Verdicts: {a['verdict'].value_counts().to_dict()}")

    # Track B
    print("\nBuilding Track B (top30 x all sessions)...")
    b = build_track_b({tk: intraday[tk] for tk in TOP30 if tk in intraday})
    b.to_csv(os.path.join(WORKDIR, "layer3_backtest_eventsB.csv"), index=False)
    print(f"  Track B: {len(b)} events  -> layer3_backtest_eventsB.csv")
    if len(b):
        print(f"  Verdicts: {b['verdict'].value_counts().to_dict()}")

if __name__=="__main__":
    main()
