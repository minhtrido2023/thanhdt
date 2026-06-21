"""Deep-dive analysis:
1. Decile lift of key factors on ret_5
2. Test alternative scoring (invert vol_burst, downweight rsi15m)
3. Conditional: factor IC by ticker liquidity / market regime
"""
import os
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

def decile_lift(df, factor, ret_col, q=10):
    sub = df[[factor, ret_col]].dropna()
    if len(sub) < 100: return None
    sub = sub.copy()
    sub["dec"] = pd.qcut(sub[factor].rank(method="first"), q, labels=False)
    g = sub.groupby("dec")[ret_col].agg(['count','mean','median'])
    g["hit"] = sub.groupby("dec")[ret_col].apply(lambda s:(s>0).mean()*100)
    return g.round(3)

def alt_score(df):
    """Recompute Layer 3 score with hypothesis-driven tweaks:
       - invert vol_burst contribution (high burst = contrarian)
       - reduce RSI-50-75 reward (RSI predicts mean reversion at horizon)
       - keep VWAP-related factors
    """
    s = pd.Series(0.0, index=df.index)
    # pct_above_vwap (keep)
    s += np.where(df["pct_above_vwap"] >= 60, 30, np.where(df["pct_above_vwap"] >= 40, 10, 0))
    # last bar
    cond_green = (df["last_bar_green"]==1) & (df["last_vs_vwap"]>0)
    cond_red = (df["last_bar_green"]==0) & (df["last_vs_vwap"]<0)
    s += np.where(cond_green, 20, np.where(cond_red, -10, 0))
    # trend_1h
    s += np.where(df["trend_1h"]>0.5, 15, np.where(df["trend_1h"]<-0.5, -10, 0))
    # RSI — REMOVE (no longer reward)
    # MACDh
    s += np.where(df["macdh"]>0, 15, 0)
    # pos_in_range
    s += np.where(df["pos_in_range"]>=60, 10, np.where(df["pos_in_range"]<30, -10, 0))
    # late_chg — invert at long horizon? Use mild penalty only
    s += np.where(df["late_chg"]<-0.5, -10, 0)
    # vol_burst INVERTED — high burst with no trend = exhaustion. Only reward when burst MODERATE
    s += np.where((df["vol_burst"]>=1.0) & (df["vol_burst"]<1.5) & (df["trend_1h"]>0), 10, 0)
    s += np.where(df["vol_burst"]>=2.0, -10, 0)  # extreme burst = penalty
    return s

def main():
    a = pd.read_csv(os.path.join(WORKDIR, "layer3_backtest_eventsA_with_returns.csv"))
    b = pd.read_csv(os.path.join(WORKDIR, "layer3_backtest_eventsB.csv"))
    daily = pd.read_csv(os.path.join(WORKDIR, "daily_forward.csv"))
    # Recompute fwd returns for B
    daily["time"] = pd.to_datetime(daily["time"]).dt.date
    daily = daily.sort_values(["ticker","time"]).reset_index(drop=True)
    daily["Close_T5"] = daily.groupby("ticker")["Close"].shift(-5)
    daily["Open_T1"] = daily.groupby("ticker")["Open"].shift(-1)
    daily["Close_T1"] = daily.groupby("ticker")["Close"].shift(-1)
    b["session_date"] = pd.to_datetime(b["session_date"]).dt.date
    b = b.merge(daily[["ticker","time","Close","Open_T1","Close_T1","Close_T5"]],
                 left_on=["ticker","session_date"], right_on=["ticker","time"], how="left")
    b["entry"] = b["Close"]
    b["ret_5"] = (b["Close_T5"]/b["entry"]-1)*100
    b["ret_overnight"] = (b["Open_T1"]/b["entry"]-1)*100
    b["ret_t1c"] = (b["Close_T1"]/b["entry"]-1)*100

    print("="*90)
    print("DECILE LIFT — key factors on ret_5 (Track B)")
    print("="*90)
    for f in ["score","pct_above_vwap","day_chg","vol_burst","rsi15m","late_chg","macdh"]:
        d = decile_lift(b, f, "ret_5")
        if d is None: continue
        print(f"\n[{f}] vs ret_5 (deciles, 1=low, 10=high):")
        print(d.to_string())

    print("\n" + "="*90)
    print("DECILE LIFT — same factors on ret_overnight (Track B)")
    print("="*90)
    for f in ["score","pct_above_vwap","day_chg","vol_burst","rsi15m"]:
        d = decile_lift(b, f, "ret_overnight")
        if d is None: continue
        print(f"\n[{f}] vs ret_overnight:")
        print(d.to_string())

    print("\n" + "="*90)
    print("ALTERNATIVE SCORE TEST")
    print("="*90)
    b["score_alt"] = alt_score(b)
    print("Original score IC vs ret_5:    ", b[["score","ret_5"]].dropna().corr(method="spearman").iloc[0,1].round(4))
    print("Alt-score IC vs ret_5:         ", b[["score_alt","ret_5"]].dropna().corr(method="spearman").iloc[0,1].round(4))
    print("Original score IC vs overnight:", b[["score","ret_overnight"]].dropna().corr(method="spearman").iloc[0,1].round(4))
    print("Alt-score IC vs overnight:     ", b[["score_alt","ret_overnight"]].dropna().corr(method="spearman").iloc[0,1].round(4))
    # quintile lift on alt_score
    sub = b.dropna(subset=["score_alt","ret_5"]).copy()
    sub["q"] = pd.qcut(sub["score_alt"].rank(method="first"), 5, labels=["Q1","Q2","Q3","Q4","Q5"])
    print("\nAlt-score quintiles on ret_5:")
    g = sub.groupby("q",observed=True)["ret_5"].agg(['count','mean','median'])
    g["hit_rate"] = sub.groupby("q",observed=True)["ret_5"].apply(lambda s:(s>0).mean()*100)
    print(g.round(3).to_string())
    sub2 = b.dropna(subset=["score","ret_5"]).copy()
    sub2["q"] = pd.qcut(sub2["score"].rank(method="first"), 5, labels=["Q1","Q2","Q3","Q4","Q5"])
    print("\nOriginal-score quintiles on ret_5 (for comparison):")
    g2 = sub2.groupby("q",observed=True)["ret_5"].agg(['count','mean','median'])
    g2["hit_rate"] = sub2.groupby("q",observed=True)["ret_5"].apply(lambda s:(s>0).mean()*100)
    print(g2.round(3).to_string())

    print("\n" + "="*90)
    print("COMBO SIGNAL TEST — VWAP+ AND day_chg moderate AND vol_burst < 1.5")
    print("="*90)
    cond_strong = (b["pct_above_vwap"]>=60) & (b["day_chg"].between(-1,2)) & (b["vol_burst"]<1.5) & (b["macdh"]>0)
    sub = b.dropna(subset=["ret_5"])
    in_sig = sub[cond_strong.reindex(sub.index, fill_value=False)]
    out_sig = sub[~cond_strong.reindex(sub.index, fill_value=False)]
    print(f"  In signal:  n={len(in_sig)}  mean_ret5={in_sig['ret_5'].mean():.3f}%  hit={(in_sig['ret_5']>0).mean()*100:.1f}%")
    print(f"  Out signal: n={len(out_sig)} mean_ret5={out_sig['ret_5'].mean():.3f}%  hit={(out_sig['ret_5']>0).mean()*100:.1f}%")
    cond_avoid = (b["pct_above_vwap"]<40) & (b["day_chg"]<-1)
    in_av = sub[cond_avoid.reindex(sub.index, fill_value=False)]
    print(f"  Avoid signal (VWAP<40% & day<-1%): n={len(in_av)} mean_ret5={in_av['ret_5'].mean():.3f}%  hit={(in_av['ret_5']>0).mean()*100:.1f}%")

if __name__=="__main__":
    main()
