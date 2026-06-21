"""Test using Layer 3 as a BUY filter for BA-system.

Three tests:
1. Match 18 BUYs in journal with their matched SELL → realized return per Layer 3 verdict
2. Filter sweep on Track B (6,742 events): apply rules, measure mean/hit/Sharpe lift
3. NAV simulation: top30 daily buy-and-hold N days, with vs without Layer 3 filter

Rules tested:
  R0  Baseline (no filter)
  R1  Skip when Layer 3 = AVOID
  R2  Skip when Layer 3 verdict <= WAIT (only take GO/GO_STRONG)
  R3  Skip Hard-Avoid combo: pct_above_vwap<40 AND day_chg<-1%
  R4  Skip when score < 0 (more aggressive than R3)
  R5  Take only Strong-Combo: pct_above_vwap>=60 AND day_chg in [-1,+2] AND vol_burst<1.5 AND macdh>0
"""
import os
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# ---------- Helpers ----------
def rule_keep_mask(df, rule):
    if rule == "R0": return pd.Series(True, index=df.index)
    if rule == "R1": return df["verdict"] != "AVOID"
    if rule == "R2": return df["verdict"].isin(["GO","GO_STRONG"])
    if rule == "R3": return ~((df["pct_above_vwap"]<40) & (df["day_chg"]<-1))
    if rule == "R4": return df["score"] >= 0
    if rule == "R5": return (df["pct_above_vwap"]>=60) & (df["day_chg"].between(-1,2)) & (df["vol_burst"]<1.5) & (df["macdh"]>0)
    raise ValueError(rule)

def perf_stats(rets):
    if len(rets)==0: return dict(n=0)
    rets = pd.Series(rets).dropna()
    return dict(
        n=len(rets),
        mean=round(rets.mean(),3),
        median=round(rets.median(),3),
        hit=round((rets>0).mean()*100,2),
        std=round(rets.std(),3),
        sharpe_like=round(rets.mean()/rets.std() if rets.std()>0 else 0, 3),
        sum_pct=round(rets.sum(),2),
    )

# ---------- Test 1: 18 BUYs in journal ----------
def test1():
    j = pd.read_csv(os.path.join(WORKDIR, "data/journal_v6_extended_events.csv"))
    j["date"] = pd.to_datetime(j["date"])
    a = pd.read_csv(os.path.join(WORKDIR, "data/layer3_backtest_eventsA_with_returns.csv"))
    a["session_date"] = pd.to_datetime(a["session_date"])

    # match BUY with subsequent SELL (FIFO by ticker)
    buys = j[j["action"]=="BUY"].sort_values("date").reset_index(drop=True)
    sells = j[j["action"]=="SELL"].sort_values("date").reset_index(drop=True)
    paired = []
    sell_used = set()
    for _, b in buys.iterrows():
        match = sells[(sells["ticker"]==b["ticker"]) & (sells["date"]>b["date"]) & (~sells.index.isin(sell_used))]
        if len(match)==0: continue
        s = match.iloc[0]
        sell_used.add(s.name)
        paired.append({"ticker": b["ticker"], "buy_date": b["date"], "sell_date": s["date"],
                       "play_type": b["play_type"], "exit_reason": s["exit_reason"],
                       "ret_net_pct": s["ret_net_pct"], "days_held": s["days_held"]})
    pairs = pd.DataFrame(paired)
    # join L3 verdict
    pairs = pairs.merge(a[["ticker","session_date","verdict","score","pct_above_vwap","day_chg","vol_burst","macdh"]],
                          left_on=["ticker","buy_date"], right_on=["ticker","session_date"], how="inner")
    print("="*90); print(f"TEST 1: 18 actual BA-system BUYs matched with realized SELL  (n={len(pairs)})")
    print("="*90)
    print(pairs[["ticker","buy_date","sell_date","days_held","verdict","score","play_type","exit_reason","ret_net_pct"]].to_string(index=False))
    print("\nRealized P&L per Layer 3 verdict:")
    g = pairs.groupby("verdict")["ret_net_pct"].agg(['count','mean','median','sum'])
    g["hit"] = pairs.groupby("verdict")["ret_net_pct"].apply(lambda s:(s>0).mean()*100)
    print(g.round(2).to_string())

    print("\nFilter rule impact on 18 BA-system BUYs:")
    rows = []
    for r in ["R0","R1","R2","R3","R4","R5"]:
        m = rule_keep_mask(pairs.rename(columns={}), r)
        kept = pairs[m]
        rows.append({"rule": r, **perf_stats(kept["ret_net_pct"])})
    print(pd.DataFrame(rows).to_string(index=False))
    return pairs

# ---------- Test 2: Filter sweep on Track B ----------
def test2():
    b = pd.read_csv(os.path.join(WORKDIR, "data/layer3_backtest_eventsB.csv"))
    daily = pd.read_csv(os.path.join(WORKDIR, "data/daily_forward.csv"))
    daily["time"] = pd.to_datetime(daily["time"]).dt.date
    daily = daily.sort_values(["ticker","time"]).reset_index(drop=True)
    for k in [1,5,10,20,45]:
        daily[f"Close_T{k}"] = daily.groupby("ticker")["Close"].shift(-k)
    b["session_date"] = pd.to_datetime(b["session_date"]).dt.date
    b = b.merge(daily[["ticker","time","Close"] + [f"Close_T{k}" for k in [1,5,10,20,45]]],
                left_on=["ticker","session_date"], right_on=["ticker","time"], how="left")
    for k in [1,5,10,20,45]:
        b[f"ret_{k}"] = (b[f"Close_T{k}"]/b["Close"] - 1)*100

    print("\n" + "="*90)
    print(f"TEST 2: Filter sweep on Track B (n={len(b)}; valid ret_20={b['ret_20'].notna().sum()}, ret_45={b['ret_45'].notna().sum()})")
    print("="*90)
    horizons = [1,5,10,20,45]
    for h in horizons:
        col = f"ret_{h}"
        print(f"\n--- Horizon {h}d ---")
        rows = []
        for r in ["R0","R1","R2","R3","R4","R5"]:
            m = rule_keep_mask(b, r) & b[col].notna()
            kept = b[m]
            skip = b[~m & b[col].notna()]
            stats = perf_stats(kept[col])
            stats["rule"] = r
            stats["skip_n"] = len(skip)
            stats["skip_mean"] = round(skip[col].mean(),3) if len(skip) else None
            rows.append(stats)
        df = pd.DataFrame(rows)[["rule","n","mean","median","hit","std","sharpe_like","skip_n","skip_mean"]]
        print(df.to_string(index=False))
    return b

# ---------- Test 3: NAV simulation ----------
def test3(b):
    """Daily buy-and-hold simulation:
       Each session_date, for top30 we either 'buy' (equal weight 1/N_kept) or skip.
       Hold for HOLD_DAYS, then sell.
       Track cumulative NAV.
    """
    print("\n" + "="*90); print("TEST 3: NAV simulation (top30, daily buy, hold 20d, equal-weight)")
    print("="*90)

    HOLD = 20
    b = b.dropna(subset=[f"ret_{HOLD}"]).copy()
    b["session_date"] = pd.to_datetime(b["session_date"]).dt.date

    out_rows = []
    for r in ["R0","R1","R2","R3","R4","R5"]:
        m = rule_keep_mask(b, r)
        kept = b[m].copy()
        # group by session_date: equal-weight buys → portfolio daily return
        daily_grp = kept.groupby("session_date")[f"ret_{HOLD}"].mean()
        n_trades = len(kept)
        n_days = len(daily_grp)
        cum = (1 + daily_grp/100).prod() - 1
        avg = daily_grp.mean()
        std = daily_grp.std()
        sharpe = avg/std*np.sqrt(252/HOLD) if std>0 else 0
        # drawdown of equity curve (using log-rets across event days)
        eq = (1 + daily_grp/100).cumprod()
        rolling_max = eq.cummax()
        dd = (eq/rolling_max - 1).min() * 100
        out_rows.append({
            "rule": r, "n_trades": n_trades, "n_event_days": n_days,
            "avg_trade_ret_%": round(avg,3),
            "trade_std_%": round(std,3),
            "ann_sharpe_proxy": round(sharpe,3),
            "max_dd_%": round(dd,2),
            "cum_total_%": round(cum*100,2),
        })
    df = pd.DataFrame(out_rows)
    print(df.to_string(index=False))

    # Test more conservative HOLD=5 (intraday signal natural horizon)
    print(f"\nSame simulation with HOLD=5 (Layer 3 natural horizon):")
    HOLD = 5
    b = b.dropna(subset=[f"ret_{HOLD}"]).copy()
    rows2 = []
    for r in ["R0","R1","R2","R3","R4","R5"]:
        m = rule_keep_mask(b, r)
        kept = b[m]
        daily_grp = kept.groupby("session_date")[f"ret_{HOLD}"].mean()
        n_trades = len(kept); n_days = len(daily_grp)
        cum = (1 + daily_grp/100).prod() - 1
        avg = daily_grp.mean(); std = daily_grp.std()
        sharpe = avg/std*np.sqrt(252/HOLD) if std>0 else 0
        eq = (1 + daily_grp/100).cumprod()
        rolling_max = eq.cummax()
        dd = (eq/rolling_max - 1).min() * 100
        rows2.append({"rule": r, "n_trades": n_trades, "n_event_days": n_days,
                       "avg_trade_ret_%": round(avg,3), "trade_std_%": round(std,3),
                       "ann_sharpe_proxy": round(sharpe,3), "max_dd_%": round(dd,2),
                       "cum_total_%": round(cum*100,2)})
    print(pd.DataFrame(rows2).to_string(index=False))

def main():
    pairs = test1()
    b_with_returns = test2()
    test3(b_with_returns)

if __name__=="__main__":
    main()
