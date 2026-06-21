"""Backfill simulation: apply new paper-trade rules (E1/E_S2 entry + intraday stop)
to ALL historical BA-system journal events, compare vs journal-recorded returns.

For each (BUY, SELL) pair where intraday data is available:
  1. Re-simulate entry on buy_date using new rule
  2. Walk forward day-by-day; check if intraday stop (low <= entry × 0.80) hits any day
  3. If stop hits, exit at stop level that day. Else exit on journal sell_date with X1_T0945_LIM
  4. Compare new ret_net vs journal's recorded ret_net

This gives realistic backfill of how the new system would have performed historically,
avoiding the 1-month wait for live data.
"""
import os, sys, pickle, time
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

sys.path.insert(0, r"/home/trido/thanhdt/WorkingClaude/stockquery")
from stockquery_agent import StockQuery

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
CACHE = os.path.join(WORKDIR, "data/intraday_full.pkl")

PLAY_RULE = {
    "COMPOUNDER_BUY":      "E1_T1115_LIM",
    "MOMENTUM_N":          "E1_T1115_LIM",
    "MOMENTUM_S":          "E1_T1115_LIM",
    "MOMENTUM_QUALITY":    "E1_T1115_LIM",
    "MOMENTUM":            "E1_T1115_LIM",
    "S_PRO":               "E1_T1115_LIM",
    "MEGA":                "E1_T1115_LIM",
    "DEEP_VALUE_RECOVERY": "E_S2_ANTICIPATE",
    "COMPOUNDER_HOLD":     "E1_T1115_LIM",  # treat as buy candidate for backfill
    "DEEP_VALUE_NS":       "E_S2_ANTICIPATE",
}
STOP_PCT = -0.20
S2_DAYCHG_THR = -3.0
S2_BOUNCE_MIN_PCT = 0.0
TC_PCT = 0.1

def prep_session(sub):
    sub = sub.copy()
    sub["time"] = pd.to_datetime(sub["time"])
    sub = sub.sort_values("time").reset_index(drop=True)
    sub["hhmm"] = sub["time"].dt.strftime("%H:%M")
    return sub

def simulate_buy(bars, rule):
    open_px = float(bars.iloc[0]["open"])
    atc_px = float(bars.iloc[-1]["close"])
    if rule == "E1_T1115_LIM":
        times = bars["hhmm"].values
        idx_arr = np.where(times >= "11:15")[0]
        if len(idx_arr)==0 or idx_arr[0] >= len(bars)-1:
            return atc_px, True, "FALLBACK_ATC", open_px
        i = idx_arr[0]
        limit = float(bars.iloc[i]["close"])
        for j in range(i+1, len(bars)):
            if bars.iloc[j]["low"] <= limit:
                return limit, False, "T1115_LIM", open_px
        return atc_px, True, "FALLBACK_ATC", open_px
    if rule == "E_S2_ANTICIPATE":
        b = bars.reset_index(drop=True)
        sopen = float(b["open"].iloc[0])
        for k in range(3, len(b)):
            row = b.iloc[k]
            day_chg = (row["close"]/sopen - 1)*100
            if k >= 2:
                bounce = (row["close"]/b.iloc[k-2]["close"] - 1)*100
            else:
                bounce = 0
            if day_chg <= S2_DAYCHG_THR and bounce > S2_BOUNCE_MIN_PCT:
                return float(row["close"]), False, "S2_TRIGGERED", open_px
        return atc_px, True, "FALLBACK_ATC_NO_S2", open_px
    if rule == "E0_OPEN_MKT":
        return open_px, False, "OPEN_MKT", open_px
    return open_px, False, "DEFAULT_OPEN", open_px

def simulate_sell_x1(bars):
    """Limit sell at 09:45 close. If miss, fallback ATC."""
    times = bars["hhmm"].values
    idx_arr = np.where(times >= "09:45")[0]
    if len(idx_arr)==0 or idx_arr[0] >= len(bars)-1:
        return float(bars.iloc[-1]["close"]), True
    i = idx_arr[0]
    limit = float(bars.iloc[i]["close"])
    for j in range(i+1, len(bars)):
        if bars.iloc[j]["high"] >= limit:
            return limit, False
    return float(bars.iloc[-1]["close"]), True

def get_session(intraday_full, ticker, target_date):
    """Return prepared bars for one session, or None."""
    df = intraday_full.get(ticker)
    if df is None: return None
    df = df.copy()
    df["time"] = pd.to_datetime(df["time"])
    df["date"] = df["time"].dt.date
    sub = df[df["date"]==target_date]
    if len(sub) < 5: return None
    return prep_session(sub)

def fetch_missing(tickers, intraday):
    """Fetch intraday for tickers not in cache. Save to cache."""
    sq = StockQuery()
    fetched = 0
    for tk in tickers:
        if tk in intraday: continue
        try:
            sq.start_date = "2025-08-12"
            sq.end_date = "2026-05-12"
            df = sq.get_historical_symbol(tk, interval="15m")
            if df is not None and len(df) > 50:
                df["time"] = pd.to_datetime(df["time"])
                intraday[tk] = df
                fetched += 1
                print(f"  fetched {tk}: {len(df)} bars")
            else:
                print(f"  {tk}: NO DATA")
            time.sleep(0.05)
        except Exception as ex:
            print(f"  {tk}: ERROR {str(ex)[:60]}")
    if fetched:
        with open(CACHE,"wb") as f:
            pickle.dump(intraday, f)
        print(f"Cache updated with {fetched} new tickers")

def match_pairs(j):
    j = j.sort_values("date").reset_index(drop=True)
    buys = j[j["action"]=="BUY"].reset_index(drop=True)
    sells = j[j["action"]=="SELL"].reset_index(drop=True)
    pairs = []
    used = set()
    for _, b in buys.iterrows():
        m = sells[(sells["ticker"]==b["ticker"]) & (sells["date"]>b["date"]) & (~sells.index.isin(used))]
        if not len(m): continue
        s = m.iloc[0]
        used.add(s.name)
        pairs.append({
            "ticker": b["ticker"], "buy_date": b["date"].date(),
            "sell_date": s["date"].date(), "play_type": b["play_type"],
            "exit_reason_journal": s["exit_reason"],
            "buy_price_journal_vnd": b["price"],
            "sell_price_journal_vnd": b["price"]*(1 + s["ret_net_pct"]/100),
            "journal_ret_net_pct": s["ret_net_pct"],
            "days_held_journal": s["days_held"],
        })
    return pd.DataFrame(pairs)

def simulate_pair(p, intraday):
    """Apply new rules: E1/E_S2 entry + intraday stop monitoring + X1 exit at sell_date."""
    tk = p["ticker"]
    buy_d = p["buy_date"]
    sell_d = p["sell_date"]
    play_type = p["play_type"]
    rule = PLAY_RULE.get(play_type, "E1_T1115_LIM")

    buy_bars = get_session(intraday, tk, buy_d)
    if buy_bars is None:
        return {"ticker": tk, "buy_date": buy_d, "skipped":"NO_BUY_INTRADAY"}

    fill_price_k, missed, fill_detail, baseline_open = simulate_buy(buy_bars, rule)
    # fill is in thousand VND; convert to VND for comparison with journal price
    fill_price_vnd = fill_price_k * 1000
    stop_lvl_k = fill_price_k * (1 + STOP_PCT)

    # Walk through every trading day from buy_date+1 to sell_date
    current = buy_d + timedelta(days=1)
    exit_type = None; exit_price_k = None; exit_date = None
    # iterate via dates present in this ticker's intraday
    df_tk = intraday.get(tk).copy()
    df_tk["time"] = pd.to_datetime(df_tk["time"])
    df_tk["date"] = df_tk["time"].dt.date
    all_dates = sorted(df_tk["date"].unique())
    intermediate = [d for d in all_dates if buy_d < d <= sell_d]
    for d in intermediate:
        sub = df_tk[df_tk["date"]==d]
        if len(sub)<5: continue
        if sub["low"].min() <= stop_lvl_k:
            exit_type = "STOP_INTRADAY"
            exit_price_k = stop_lvl_k
            exit_date = d
            break

    if exit_type is None:
        sell_bars = get_session(intraday, tk, sell_d)
        if sell_bars is None:
            return {"ticker": tk, "buy_date": buy_d, "skipped":"NO_SELL_INTRADAY"}
        exit_price_k, sell_missed = simulate_sell_x1(sell_bars)
        exit_type = "TIME_X1"
        exit_date = sell_d

    new_gross = (exit_price_k/fill_price_k - 1)*100
    new_net = new_gross - 2*TC_PCT
    return {
        "ticker": tk, "play_type": play_type, "rule": rule,
        "buy_date": buy_d, "exit_date": exit_date, "exit_type": exit_type,
        "journal_buy_vnd": p["buy_price_journal_vnd"],
        "new_buy_vnd": round(fill_price_vnd,0),
        "fill_detail": fill_detail, "missed_entry": missed,
        "stop_lvl_k": round(stop_lvl_k,3),
        "exit_price_k": round(exit_price_k,3),
        "new_ret_net_pct": round(new_net,3),
        "journal_ret_net_pct": round(p["journal_ret_net_pct"],3),
        "lift_pp": round(new_net - p["journal_ret_net_pct"],3),
        "days_held_new": (exit_date - buy_d).days,
        "days_held_journal": p["days_held_journal"],
        "exit_reason_journal": p["exit_reason_journal"],
    }

def main():
    print("Loading journal + intraday cache...")
    j = pd.read_csv(os.path.join(WORKDIR, "data/journal_v6_extended_events.csv"))
    j["date"] = pd.to_datetime(j["date"])
    with open(CACHE,"rb") as f: intraday = pickle.load(f)
    print(f"  {len(intraday)} tickers in cache")

    pairs = match_pairs(j)
    pairs = pairs[pairs["buy_date"] >= datetime(2025,8,12).date()]
    print(f"  {len(pairs)} BUY-SELL pairs with buy_date >= 2025-08-12")
    print(f"  unique tickers: {pairs['ticker'].nunique()}")

    missing = sorted(set(pairs["ticker"]) - set(intraday.keys()))
    if missing:
        print(f"\nFetching {len(missing)} missing tickers: {missing}")
        fetch_missing(missing, intraday)
    else:
        print("  all tickers already cached")

    print("\nRunning simulation...")
    results = []
    for _, p in pairs.iterrows():
        r = simulate_pair(p, intraday)
        results.append(r)
        if "skipped" in r:
            print(f"  {r['ticker']} {p['buy_date']} SKIPPED: {r['skipped']}")
        else:
            print(f"  {r['ticker']:>5} {r['buy_date']} {r['play_type']:>20} {r['exit_type']:>14}  new={r['new_ret_net_pct']:>7.2f}%  journal={r['journal_ret_net_pct']:>7.2f}%  lift={r['lift_pp']:+.2f}pp")

    df = pd.DataFrame([r for r in results if "skipped" not in r])
    skipped = [r for r in results if "skipped" in r]
    print(f"\n{len(df)} simulated, {len(skipped)} skipped")
    df.to_csv(os.path.join(WORKDIR, "data/layer3_backfill_results.csv"), index=False)

    print("\n" + "="*100)
    print("SUMMARY")
    print("="*100)
    print(f"Mean lift_pp:    {df['lift_pp'].mean():+.3f}pp")
    print(f"Median lift_pp:  {df['lift_pp'].median():+.3f}pp")
    print(f"Total sum lift:  {df['lift_pp'].sum():+.2f}pp")
    print(f"Hit rate (lift>0): {(df['lift_pp']>0).mean()*100:.1f}%")
    print(f"\nJournal sum:  {df['journal_ret_net_pct'].sum():+.2f}%")
    print(f"New rule sum: {df['new_ret_net_pct'].sum():+.2f}%")
    print(f"Improvement:  {df['new_ret_net_pct'].sum() - df['journal_ret_net_pct'].sum():+.2f}pp total over {len(df)} trades")

    print("\nBreakdown by exit_type:")
    print(df.groupby("exit_type").agg(
        n=("lift_pp","count"),
        new_mean=("new_ret_net_pct","mean"),
        journal_mean=("journal_ret_net_pct","mean"),
        lift_mean=("lift_pp","mean"),
        lift_sum=("lift_pp","sum"),
    ).round(3).to_string())

    print("\nBreakdown by play_type:")
    print(df.groupby("play_type").agg(
        n=("lift_pp","count"),
        new_mean=("new_ret_net_pct","mean"),
        journal_mean=("journal_ret_net_pct","mean"),
        lift_mean=("lift_pp","mean"),
    ).round(3).to_string())

    print("\nBreakdown by exit_reason_journal vs new exit_type:")
    print(pd.crosstab(df["exit_reason_journal"].fillna("?"), df["exit_type"]).to_string())

    # cases where stop saved (journal said STOP, new caught earlier)
    journal_stops = df[df["exit_reason_journal"]=="STOP"]
    if len(journal_stops):
        new_stop_save = journal_stops[journal_stops["exit_type"]=="STOP_INTRADAY"]
        print(f"\nJournal STOPs: {len(journal_stops)}; of which new rule fired intraday stop: {len(new_stop_save)}")
        if len(new_stop_save):
            print(f"  mean lift on these: {new_stop_save['lift_pp'].mean():+.2f}pp")

if __name__=="__main__":
    main()
