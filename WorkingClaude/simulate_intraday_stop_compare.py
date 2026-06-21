"""A/B compare close-based vs intraday-low stop across full BA-system history.

Run same strategies with stop_mode=CLOSE (baseline) and stop_mode=INTRADAY_LOW.
Compare CAGR, Sharpe, MaxDD, win-rate, stop-fire counts.

Daily Low is the actual market data — no synthetic intraday. This is the standard
daily-resolution proxy for "did price touch stop intraday?".

This test scales the 18-event backfill finding (intraday stop loses on real BA flow)
to full 12-year history.
"""
import os, sys, subprocess
from io import StringIO
import numpy as np
import pandas as pd

sys.path.insert(0, r"/home/trido/thanhdt/WorkingClaude")
from simulate_holistic_nav import (
    simulate, metrics, bq, SIGNAL_QUERY, VNI_QUERY,
    START_DATE, END_DATE, INIT_NAV, STOP_LOSS,
)

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
LOWS_CACHE = os.path.join(WORKDIR, "intraday_stop_lows.csv")

LOWS_QUERY = """
SELECT t.ticker, t.time, t.Low
FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{start}' AND DATE '{end}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  AND t.Low IS NOT NULL
"""

def load_lows(start, end):
    if os.path.exists(LOWS_CACHE):
        print(f"Loading cached Low data: {LOWS_CACHE}")
        df = pd.read_csv(LOWS_CACHE)
        df["time"] = pd.to_datetime(df["time"])
        return df
    print(f"Querying BigQuery for daily Low (this may take a minute)...")
    df = bq(LOWS_QUERY.format(start=start, end=end))
    df["time"] = pd.to_datetime(df["time"])
    df.to_csv(LOWS_CACHE, index=False)
    print(f"  cached to {LOWS_CACHE} ({len(df):,} rows)")
    return df

def build_lows_dict(df):
    out = {}
    for tk, g in df.groupby("ticker"):
        out[tk] = dict(zip(g["time"], g["Low"]))
    return out

def main():
    print(f"Loading signals + prices ({START_DATE} -> {END_DATE})...")
    sig = bq(SIGNAL_QUERY.format(start=START_DATE, end=END_DATE))
    sig["time"] = pd.to_datetime(sig["time"])
    print(f"  {len(sig):,} signal rows")

    vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
    vni["time"] = pd.to_datetime(vni["time"])
    vni_dates = sorted(vni["time"].unique())
    print(f"  {len(vni_dates):,} trading days")

    prices = {}
    for tk, g in sig.groupby("ticker"):
        prices[tk] = dict(zip(g["time"], g["Close"]))

    lows_df = load_lows(START_DATE, END_DATE)
    lows = build_lows_dict(lows_df)
    print(f"  Low data for {len(lows):,} tickers")

    # Strategies to test — use BAL (BA-system production strategy)
    strategies = {
        "BAL_8pos": {
            "tiers": ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"],
            "max_pos": 8,
        },
        "MEGA_3pos": {
            "tiers": ["MEGA"],
            "max_pos": 3,
        },
    }

    rows = []
    for sname, cfg in strategies.items():
        for mode in ["CLOSE", "INTRADAY_LOW"]:
            label = f"{sname}_stop_{mode}"
            print(f"\n--- {label} ---")
            nav_df, trades_df = simulate(
                sig, prices, vni_dates,
                allowed_tiers=cfg["tiers"], max_positions=cfg["max_pos"],
                hold_days=45, stop_loss=-0.20, min_hold=2,
                lows=lows, stop_mode=mode,
                name=label)
            m = metrics(nav_df, trades_df, label)
            n_stop = (trades_df["reason"].astype(str).str.startswith("STOP")).sum()
            n_intra = (trades_df["reason"] == "STOP_INTRADAY").sum()
            n_close = (trades_df["reason"] == "STOP").sum()
            n_time = (trades_df["reason"] == "TIME").sum()
            print(f"  CAGR={m['cagr_pct']:.2f}%, Sharpe={m['sharpe']:.3f}, "
                  f"MaxDD={m['max_dd_pct']:.2f}%, WinRate={m['win_rate_pct']:.1f}%, "
                  f"trades={m['n_trades']}")
            print(f"  Exits: TIME={n_time}, STOP_close={n_close}, STOP_INTRADAY={n_intra}")
            rows.append({
                "strategy": sname, "stop_mode": mode,
                "cagr_pct": m["cagr_pct"], "sharpe": m["sharpe"],
                "max_dd_pct": m["max_dd_pct"], "win_rate_pct": m["win_rate_pct"],
                "n_trades": m["n_trades"],
                "n_stop_total": n_stop, "n_stop_intraday": n_intra, "n_stop_close": n_close, "n_time": n_time,
                "avg_ret": trades_df["ret_net"].mean()*100 if len(trades_df) else 0,
                "avg_hold": trades_df["days_held"].mean() if len(trades_df) else 0,
            })
            # save per-strategy results
            nav_df.to_csv(os.path.join(WORKDIR, f"intraday_stop_nav_{label}.csv"), index=False)
            trades_df.to_csv(os.path.join(WORKDIR, f"intraday_stop_trades_{label}.csv"), index=False)

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(WORKDIR, "intraday_stop_compare.csv"), index=False)

    print("\n" + "="*100)
    print("A/B COMPARISON")
    print("="*100)
    print(df.to_string(index=False))

    print("\n" + "="*100)
    print("DELTA: INTRADAY_LOW vs CLOSE")
    print("="*100)
    for sname in strategies:
        sub = df[df["strategy"]==sname]
        if len(sub)!=2: continue
        close = sub[sub["stop_mode"]=="CLOSE"].iloc[0]
        intra = sub[sub["stop_mode"]=="INTRADAY_LOW"].iloc[0]
        print(f"\n[{sname}]")
        print(f"  CAGR:     {close['cagr_pct']:.2f}% -> {intra['cagr_pct']:.2f}%  delta {intra['cagr_pct']-close['cagr_pct']:+.2f}pp")
        print(f"  Sharpe:   {close['sharpe']:.3f} -> {intra['sharpe']:.3f}  delta {intra['sharpe']-close['sharpe']:+.3f}")
        print(f"  MaxDD:    {close['max_dd_pct']:.2f}% -> {intra['max_dd_pct']:.2f}%  delta {intra['max_dd_pct']-close['max_dd_pct']:+.2f}pp")
        print(f"  Stops:    close={int(close['n_stop_close'])} -> intraday={int(intra['n_stop_intraday'])} ({int(intra['n_stop_intraday'])-int(close['n_stop_close']):+d})")
        print(f"  TIME ex:  {int(close['n_time'])} -> {int(intra['n_time'])} ({int(intra['n_time'])-int(close['n_time']):+d})")
        print(f"  Trades:   {int(close['n_trades'])} -> {int(intra['n_trades'])}")
    print("\nSaved: intraday_stop_compare.csv + per-strategy nav/trades CSVs")

if __name__=="__main__":
    main()
