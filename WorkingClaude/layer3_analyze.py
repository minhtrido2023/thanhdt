"""Layer 3 backtest analysis:
- Match intraday features (eventsA/B) with forward returns from daily data
- Track A: verdict lift on real BA-system BUYs (forward 5/10/20-day return from D close)
- Track B: factor IC + verdict lift on top30 universe

Output: console + layer3_factor_ic.csv
"""
import os
import numpy as np
import pandas as pd
def spearmanr(x, y):
    """Manual Spearman correlation (avoid scipy dependency)."""
    import math
    x = pd.Series(x).rank()
    y = pd.Series(y).rank()
    n = len(x)
    if n < 3: return (float('nan'), float('nan'))
    rho = x.corr(y)
    # approximate two-sided p-value via t-stat
    if abs(rho) >= 0.9999:
        return (rho, 0.0)
    t = rho * math.sqrt((n-2)/max(1e-12, 1-rho*rho))
    # tail probability via normal approximation for large n
    from math import erf, sqrt
    z = abs(t)
    p = 2 * (1 - 0.5*(1+erf(z/sqrt(2))))
    return (rho, p)

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

def add_forward_returns(events_df, daily_df):
    """For each (ticker, session_date), join Close on D, D+1 open, D+5/10/20 closes."""
    daily_df = daily_df.copy()
    daily_df["time"] = pd.to_datetime(daily_df["time"]).dt.date
    daily_df = daily_df.sort_values(["ticker","time"]).reset_index(drop=True)
    # for each ticker compute forward closes
    daily_df["Open_T1"] = daily_df.groupby("ticker")["Open"].shift(-1)
    daily_df["Close_T5"]  = daily_df.groupby("ticker")["Close"].shift(-5)
    daily_df["Close_T10"] = daily_df.groupby("ticker")["Close"].shift(-10)
    daily_df["Close_T20"] = daily_df.groupby("ticker")["Close"].shift(-20)
    events_df = events_df.copy()
    events_df["session_date"] = pd.to_datetime(events_df["session_date"]).dt.date
    merged = events_df.merge(daily_df[["ticker","time","Close","Open_T1","Close_T5","Close_T10","Close_T20"]],
                              left_on=["ticker","session_date"], right_on=["ticker","time"], how="left")
    # use D close as entry baseline (we assume the system buys at T+1 open, but for fair fwd-comparison use D close)
    merged["entry"] = merged["Close"]
    merged["ret_5"]  = (merged["Close_T5"]  / merged["entry"] - 1) * 100
    merged["ret_10"] = (merged["Close_T10"] / merged["entry"] - 1) * 100
    merged["ret_20"] = (merged["Close_T20"] / merged["entry"] - 1) * 100
    # also a tighter T+1 metric: T+1 open vs D close
    merged["ret_overnight"] = (merged["Open_T1"] / merged["entry"] - 1) * 100
    return merged

def verdict_lift(df, ret_col):
    g = df.groupby("verdict")[ret_col].agg(['count','mean','median','std'])
    g["hit_rate"] = df.groupby("verdict")[ret_col].apply(lambda s: (s>0).mean()*100)
    return g.round(3)

def factor_ic(df, factors, ret_cols):
    rows = []
    for f in factors:
        for rc in ret_cols:
            sub = df[[f, rc]].dropna()
            if len(sub) < 30:
                continue
            rho, p = spearmanr(sub[f], sub[rc])
            rows.append({"factor": f, "ret": rc, "n": len(sub), "ic_spearman": round(rho,4), "pvalue": round(p,5)})
    return pd.DataFrame(rows)

def main():
    daily = pd.read_csv(os.path.join(WORKDIR, "daily_forward.csv"))

    # Track A
    a = pd.read_csv(os.path.join(WORKDIR, "layer3_backtest_eventsA.csv"))
    a = add_forward_returns(a, daily)
    print("="*90)
    print("TRACK A — 18 actual BA-system BUYs (intraday-available window)")
    print("="*90)
    print(f"Events with fwd_5  : {a['ret_5'].notna().sum()}")
    print(f"Events with fwd_20 : {a['ret_20'].notna().sum()}")
    for rc in ["ret_overnight","ret_5","ret_10","ret_20"]:
        sub = a.dropna(subset=[rc])
        if len(sub)==0: continue
        print(f"\nVerdict lift on {rc} (n={len(sub)})")
        print(verdict_lift(sub, rc).to_string())
    print("\nFull Track A table:")
    cols = ["ticker","session_date","verdict","score","play_type","ret_overnight","ret_5","ret_10","ret_20"]
    print(a[cols].to_string(index=False))
    a.to_csv(os.path.join(WORKDIR, "layer3_backtest_eventsA_with_returns.csv"), index=False)

    # Track B
    b = pd.read_csv(os.path.join(WORKDIR, "layer3_backtest_eventsB.csv"))
    b = add_forward_returns(b, daily)
    print("\n" + "="*90)
    print(f"TRACK B — top30 x sessions ({len(b)} events; with ret_20: {b['ret_20'].notna().sum()})")
    print("="*90)
    for rc in ["ret_overnight","ret_5","ret_10","ret_20"]:
        sub = b.dropna(subset=[rc])
        if len(sub)==0: continue
        print(f"\nVerdict lift on {rc} (n={len(sub)})")
        print(verdict_lift(sub, rc).to_string())

    factors = ["score","pct_above_vwap","trend_1h","vol_burst","last_bar_green",
               "last_vs_vwap","day_chg","pos_in_range","late_chg","rsi15m","macdh"]
    ic = factor_ic(b, factors, ["ret_overnight","ret_5","ret_10","ret_20"])
    ic.to_csv(os.path.join(WORKDIR, "layer3_factor_ic.csv"), index=False)
    print("\nFactor IC (Spearman, Track B):")
    print(ic.pivot(index="factor", columns="ret", values="ic_spearman").to_string())
    print("\np-values:")
    print(ic.pivot(index="factor", columns="ret", values="pvalue").to_string())
    print("\n-> saved layer3_factor_ic.csv")

    # additional: conditional analysis. Among Track B events, does score predict ret_5 controlling for market regime?
    # Quick: split by year-month and check IC stability
    b["month"] = pd.to_datetime(b["session_date"]).dt.to_period("M").astype(str)
    monthly_ic = []
    for m, sub in b.groupby("month"):
        s = sub.dropna(subset=["ret_5","score"])
        if len(s)<50: continue
        rho, p = spearmanr(s["score"], s["ret_5"])
        monthly_ic.append({"month": m, "n": len(s), "ic_score_vs_ret5": round(rho,4), "p": round(p,4)})
    print("\nMonthly IC of score vs ret_5 (stability check):")
    print(pd.DataFrame(monthly_ic).to_string(index=False))

if __name__=="__main__":
    main()
